import os
import sys
import logging
import time
import autogen
from autogen import ConversableAgent
import litellm
from datetime import datetime
from dotenv import load_dotenv
from typing import List, Dict
import asyncio

import config
from config import llm_config, llm_config_fast
from orchestrator import process_section, correct_section_async
from writer import create_writer_team
from validator import create_final_validator_team
from specialist_agents import create_prompt_writer_agent, create_final_prompt_writer_agent
from tasks import get_correction_task, get_creation_task, get_final_validation_task, get_final_writer_task, run_validation_async
from utils import (
    read_markdown_file_async,
    parse_feedback_and_count_issues,
    preprocess_all_pdfs,
    merge_output_files,
    TokenTracker,
    clear_directory,
    parse_holistic_feedback
)

# Load environment variables from .env file
load_dotenv()

token_tracker = TokenTracker()
litellm.success_callback = [token_tracker.log_success]
class Tee:
    """A helper class to redirect stdout to both console and a file."""
    def __init__(self, original_stream, log_file):
        self.original_stream = original_stream
        self.log_file = log_file

    def write(self, text):
        self.original_stream.write(text)
        self.log_file.write(text)

    def flush(self):
        self.original_stream.flush()
        self.log_file.flush()

def setup_logging(run_timestamp: str):
    """
    Configures logging to capture full terminal output and a separate loop trace.
    """
    # Create logs directory if it doesn't exist
    os.makedirs(config.LOGS_DIR, exist_ok=True)

    # ---- Full Output Logger (mirrors console) ----
    # Construct the log filename with the timestamp
    full_log_filename = f"full_run_{run_timestamp}.log"
    full_log_path = os.path.join(config.LOGS_DIR, full_log_filename)

    # Open the log file in write mode
    log_file_handle = open(full_log_path, 'w', encoding='utf-8')

    # Redirect stdout and stderr
    original_stdout = sys.stdout
    original_stderr = sys.stderr
    sys.stdout = Tee(original_stdout, log_file_handle)
    sys.stderr = Tee(original_stderr, log_file_handle)
    
    # Get the root logger
    root_logger = logging.getLogger()
    root_logger.handlers.clear()
    root_logger.setLevel(logging.INFO)

    stream_handler = logging.StreamHandler(sys.stdout) # Use the redirected stdout
    # Use a more detailed formatter for the logs now
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    stream_handler.setFormatter(formatter)

    root_logger.addHandler(stream_handler)
    
    # ---- Loop Trace Logger (only for specific milestones) ----
    # Construct the log filename with the timestamp
    loop_log_filename = f"loop_trace_{run_timestamp}.log"
    loop_log_path = os.path.join(config.LOGS_DIR, loop_log_filename)

    loop_logger = logging.getLogger('LoopTracer')
    loop_logger.setLevel(logging.INFO)
    loop_logger.handlers.clear() # Clear handlers in case of re-runs in the same session
    
    # Create a file handler for the loop trace log
    loop_file_handler = logging.FileHandler(loop_log_path, mode='w')
    loop_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    loop_file_handler.setFormatter(loop_formatter)
    
    loop_logger.addHandler(loop_file_handler)
    loop_logger.propagate = False
    
    logging.info(f"Logging initialized. Full log: {full_log_filename}, Loop trace: {loop_log_filename}")

def setup_environment():
    """Create necessary directories if they don't exist."""
    os.makedirs(config.DOCS_DIR, exist_ok=True)
    os.makedirs(config.PROCESSED_DOCS_DIR, exist_ok=True)
    os.makedirs(config.OUTPUTS_DIR, exist_ok=True)
    os.makedirs(config.INSTRUCTIONS_DIR, exist_ok=True)
    print("Environment setup complete.")

async def main_async():
    """Main function to run the writer-validator loop."""
    start_time = time.monotonic()
    run_timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    setup_logging(run_timestamp)

    litellm.max_retries = 5

    loop_logger = logging.getLogger('LoopTracer')
    loop_logger.info("Main process started.")

    process_completed_successfully = True # Delete this line after testing
    is_preprocessing_successful = True # Delete this line after testing
    # is_preprocessing_successful = preprocess_all_pdfs()
    # if not is_preprocessing_successful:
    #     logging.critical("Pre-processing failed. Aborting main process.")
    #     loop_logger.critical("Process aborted due to pre-processing failure.")
    #     return # Stop execution if pre-processing fails
        
    # loop_logger.info("Pre-processing complete. Starting agent workflow.")
    # setup_environment()    
    
    # prompt_writer = create_prompt_writer_agent(llm_config_fast)
    # final_prompt_writer = create_final_prompt_writer_agent(llm_config_fast)
    
    total_sections = 5
    
    # semaphore = asyncio.Semaphore(config.CONCURRENT_SECTIONS)
    
    # logging.info(f"Starting concurrent processing for {total_sections} sections with a limit of {config.CONCURRENT_SECTIONS}.")
    
    # sections_to_process = [i for i in range(1, total_sections + 1)]
    
    # # --- CONCURRENT SECTIONAL PROCESSING ---
    # processing_tasks = [
    #     process_section(sec_id, semaphore, llm_config, llm_config_fast, prompt_writer)
    #     for sec_id in sections_to_process
    # ]
    
    # section_results = await asyncio.gather(*processing_tasks)
    # process_completed_successfully = all(section_results)
    process_completed_successfully = True # Delete this line after testing

    # Final valiadation phase
    if not process_completed_successfully:
        logging.error("Process stopped before finalization due to failures in sectional generation.")
        loop_logger.error("Aborting. Finalization phase skipped.")
    else:
        logging.info(f"\n{'#'*25} STARTING FINALIZATION PHASE {'#'*25}")
        loop_logger.info("===== Starting Finalization Phase: Holistic Review and Correction Loop =====")
        
        final_document_passed = False
        for i in range(config.MAX_FINAL_ITERATIONS):
            iteration = i + 1
            logging.info(f"\n{'='*20} FINALIZATION LOOP - ITERATION {iteration} {'='*20}")
            loop_logger.info(f"--- Finalization Iteration {iteration} START ---")

            # 1. RUN THE HOLISTIC VALIDATION
            final_validator_manager = create_final_validator_team(llm_config, llm_config_fast)
            final_validator_proxy = final_validator_manager.groupchat.agent_by_name("Final_Validator_Proxy")
            final_validation_task = get_final_validation_task()
            await final_validator_proxy.a_initiate_chat(recipient=final_validator_manager, message=final_validation_task, clear_history=True)
            loop_logger.info(f"Finalization Iteration {iteration}: Holistic Validator team completed.")

            # 2. PARSE FEEDBACK AND CHECK FOR PASS CONDITION
            final_feedback_content = await read_markdown_file_async(config.FINAL_FEEDBACK_PATH)
            issue_counts = parse_feedback_and_count_issues(final_feedback_content)
            logging.info(f"Final Holistic Issues Found: Critical={issue_counts['critical']}, Major={issue_counts['major']}, Minor={issue_counts['minor']}")

            if issue_counts['critical'] == 0:
                logging.info("\n✅ Success! No critical issues found in holistic review. Exiting correction loop.")
                loop_logger.info("===== Final Document Sections PASSED Holistic Review =====")
                final_document_passed = True
                break # Exit the loop
            
            # 3. IF NOT PASSED, RUN PARALLEL CORRECTIONS
            logging.warning("\n❌ Critical issues found. Starting parallel correction phase...")
            loop_logger.info(f"--- Initiating parallel corrections for final sections. ---")
            
            # Use our new parser to get feedback for each section
            feedback_per_section = parse_holistic_feedback(final_feedback_content)
            
            correction_tasks = []
            for sec_number, feedback_text in feedback_per_section.items():
                task = asyncio.create_task(correct_section_async(
                    sec_number, feedback_text, llm_config, llm_config_fast
                ))
                correction_tasks.append(task)
            
            if correction_tasks:
                try:
                    await asyncio.gather(*correction_tasks)
                except Exception as e:
                    logging.error(f"A correction task failed! Reason: {e}", exc_info=True)
            # if correction_tasks:
            #     await asyncio.gather(*correction_tasks)
            
            logging.info(f"--- All parallel corrections for iteration {iteration} are complete. ---")
            
        if not final_document_passed:
            logging.error(f"\n🚫 FAILED: Final sections could not be corrected after {config.MAX_FINAL_ITERATIONS} iterations.")
            loop_logger.error("===== Final Sections FAILED TO PASS. Aborting before merge. =====")
            process_completed_successfully = False
        else:
            # 4. FINAL MERGE (only happens if the loop was successful)
            logging.info("--- Merging corrected section files into final document. ---")
            merge_success = merge_output_files(total_sections, config.OUTPUTS_DIR, config.FINAL_DOCUMENT_FILENAME)

            if not merge_success:
                logging.error("Failed to merge sectional documents. Finalization failed.")
                loop_logger.error("Process stopped: Final merge step failed.")
                process_completed_successfully = False
            else:
                logging.info(f"✅ Final document successfully created at {config.FINAL_DOCUMENT_PATH}")
    
    logging.info(f"\n{'#'*25} PROCESS COMPLETE {'#'*25}")
    loop_logger.info("Main process finished.")

    end_time = time.monotonic()
    total_duration_seconds = end_time - start_time
    total_duration_minutes = total_duration_seconds / 60

    loop_logger.info("=" * 40)
    loop_logger.info("            RUN SUMMARY")
    loop_logger.info("=" * 40)
    if process_completed_successfully:
        loop_logger.info("Overall Status: SUCCESS")
    else:
        loop_logger.info("Overall Status: FAILED / STOPPED EARLY")
    
    loop_logger.info(f"Total Execution Time: {total_duration_seconds:.2f} seconds ({total_duration_minutes:.2f} minutes)")
    loop_logger.info("=" * 40)

if __name__ == "__main__":
    try:
        # The main asynchronous event loop runs here.
        asyncio.run(main_async())

    except KeyboardInterrupt:
        print("\nProcess interrupted by user. Shutting down.")
        logging.getLogger('LoopTracer').warning("===== PROCESS TERMINATED BY USER =====")

    except Exception as e:
        # This is a catch-all for any other unexpected errors.
        logging.getLogger('LoopTracer').critical(f"===== A FATAL ERROR OCCURRED: {e} =====", exc_info=True)

    finally:
        print("\n--- Displaying final token usage summary. ---")
        token_tracker.display_summary()
        print("\n--- Running final cleanup process. ---")
        clear_directory(config.PROCESSED_DOCS_DIR)