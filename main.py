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
from writer import create_writer_team, create_final_writer_team
from validator import create_final_validator_team
from specialist_agents import create_prompt_writer_agent, create_final_prompt_writer_agent
from tasks import get_correction_task, get_creation_task, get_final_validation_task, get_final_writer_task, run_validation_async
from utils import (
    read_markdown_file_async,
    parse_feedback_and_count_issues,
    preprocess_all_pdfs,
    merge_output_files,
    TokenTracker,
    clear_directory
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

async def process_section(section_number: str, semaphore: asyncio.Semaphore, llm_config: Dict, llm_config_fast: Dict, prompt_writer: ConversableAgent):
    """Asynchronously processes a single section, including retries, under a semaphore."""
    async with semaphore:
        logging.info(f"Semaphore acquired for section {section_number}. Starting processing.")
        
        output_filepath = os.path.join(config.OUTPUTS_DIR, f"output_s{section_number}.md")
        feedback_filepath = os.path.join(config.OUTPUTS_DIR, f"feedback_s{section_number}.md")
        
        max_iterations = config.MAX_SECTION_ITERATIONS
        loop_logger = logging.getLogger('LoopTracer')

        try: # <--- START OF THE ISOLATION BLOCK
            for i in range(1, max_iterations + 1):
                logging.info(f"\n{'='*20} SECTION {section_number} - ITERATION {i} {'='*20}")
                
                # --- WRITER TEAM ---
                writer_manager = create_writer_team(llm_config, llm_config_fast)
                writer_proxy_agent = writer_manager.groupchat.agent_by_name("Writer_User_Proxy")
                
                if i == 1:
                    writer_task = get_creation_task(section_number)
                else:
                    logging.info(f"--- Preparing clean revision request for s{section_number} with Prompt_Writer ---")
                    previous_draft = await read_markdown_file_async(output_filepath)
                    feedback_report = await read_markdown_file_async(feedback_filepath)
                    
                    prompt_writer_task = f"""
    Here is a document that failed validation and the feedback report. Create a clean [REVISION_REQUEST] for the Document_Writer.

    **Document to Revise:**
    {previous_draft}

    **Feedback Report:**
    {feedback_report}
    """
                    # Use the async version of generate_reply
                    clean_request = await prompt_writer.a_generate_reply(messages=[{"role": "user", "content": prompt_writer_task}])
                    
                    writer_task = get_correction_task(section_number, clean_request)

                await writer_proxy_agent.a_initiate_chat(
                    recipient=writer_manager, message=writer_task, clear_history=True
                )
                loop_logger.info(f"Section {section_number}, Iteration {i}: Writer team completed.")

                # --- VALIDATOR TEAM ---
                await run_validation_async(section_number, llm_config, llm_config_fast)
                loop_logger.info(f"Section {section_number}, Iteration {i}: Validator team completed.")
            
                # Assessment
                feedback_content = await read_markdown_file_async(feedback_filepath)
                issue_counts = parse_feedback_and_count_issues(feedback_content)
                logging.info(f"Section {section_number} Issues Found: Critical={issue_counts['critical']}, Major={issue_counts['major']}, Minor={issue_counts['minor']}")

                if issue_counts['critical'] == 0 and i >= 2:
                    logging.info(f"\n✅ Success! Section {section_number} passed validation on iteration {i}.")
                    loop_logger.info(f"===== Section {section_number} PASSED =====")
                    return True
                elif issue_counts['critical'] == 0 and i == 1:
                    logging.info(f"\n⚠️ Section {section_number} passed on first attempt. Forcing a second loop for robustness.")
                    loop_logger.info(f"Section {section_number}, Iteration 1: Passed, but continuing to mandatory second loop.")
            
            logging.error(f"\n🚫 FAILED: Section {section_number} could not pass after {max_iterations} iterations.")
            return False # Failure for this section
            
        except Exception as e:
            # If anything inside the loop crashes
            # (e.g., an unexpected agent error, a file not found, a sudden API outage),
            # this block will catch it.
            logging.critical(f"FATAL ERROR in process_section '{section_number}': {e}", exc_info=True)
            loop_logger.critical(f"===== Section {section_number} FAILED with a critical exception: {e} =====")
            return False # Return False to signal failure, but DO NOT re-raise the exception.    


async def main_async():
    """Main function to run the writer-validator loop."""
    start_time = time.monotonic()
    run_timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    setup_logging(run_timestamp)

    litellm.max_retries = 5

    loop_logger = logging.getLogger('LoopTracer')
    loop_logger.info("Main process started.")

    is_preprocessing_successful = preprocess_all_pdfs()
    if not is_preprocessing_successful:
        logging.critical("Pre-processing failed. Aborting main process.")
        loop_logger.critical("Process aborted due to pre-processing failure.")
        return # Stop execution if pre-processing fails
        
    loop_logger.info("Pre-processing complete. Starting agent workflow.")
    setup_environment()

    # --- Load Azure OpenAI credentials ---
    azure_api_key = os.getenv("AZURE_OPENAI_API_KEY")
    azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
    azure_model_name = os.getenv("AZURE_OPENAI_MODEL_NAME")
    azure_model_name2 = os.getenv("AZURE_OPENAI_MODEL_NAME2")
    azure_api_version = os.getenv("AZURE_OPENAI_API_VERSION")

    if not all([azure_api_key, azure_endpoint, azure_model_name, azure_model_name2, azure_api_version]):
        logging.error("Error: One or more Azure OpenAI environment variables are not set.")
        logging.error("Please check your .env file for: AZURE_OPENAI_API_KEY, AZURE_OPENAI_ENDPOINT, AZURE_OPENAI_MODEL_NAME, AZURE_OPENAI_MODEL_NAME2, AZURE_OPENAI_API_VERSION")
        loop_logger.error("Process stopped: Missing Azure credentials.")
        return

    config_list = [
        {
            "model": azure_model_name,
            "api_key": azure_api_key,
            "base_url": azure_endpoint,
            "api_type": "azure",
            "api_version": azure_api_version,
        }
    ]
    llm_config = {
        "config_list": config_list, 
        "timeout": 300,
        }
    
    config_list_fast = [
        {
            "model": azure_model_name2,
            "api_key": azure_api_key,
            "base_url": azure_endpoint,
            "api_type": "azure",
            "api_version": azure_api_version,
        }
    ]

    llm_config_fast = {
        "config_list": config_list_fast, 
        "timeout": 300,
        }
      
    prompt_writer = create_prompt_writer_agent(llm_config_fast)
    final_prompt_writer = create_final_prompt_writer_agent(llm_config_fast)
    
    total_sections = 5
    
    semaphore = asyncio.Semaphore(config.CONCURRENT_SECTIONS)
    
    logging.info(f"Starting concurrent processing for {total_sections} sections with a limit of {config.CONCURRENT_SECTIONS}.")
    
    sections_to_process = [i for i in range(1, total_sections + 1)]
    
    # --- CONCURRENT SECTIONAL PROCESSING ---
    processing_tasks = [
        process_section(sec_id, semaphore, llm_config, llm_config_fast, prompt_writer)
        for sec_id in sections_to_process
    ]
    
    section_results = await asyncio.gather(*processing_tasks)
    process_completed_successfully = all(section_results)


    # Final valiadation phase
    if not process_completed_successfully:
        logging.error("Process stopped before finalization due to failures in sectional generation.")
        loop_logger.error("Aborting. Finalization phase skipped.")
    else:
        logging.info(f"\n{'#'*25} STARTING FINALIZATION PHASE {'#'*25}")
        loop_logger.info("===== Starting Finalization Phase: Merging and Holistic Review =====")

        final_doc_filename = "final_document.md"
        merge_success = merge_output_files(total_sections, config.OUTPUTS_DIR, final_doc_filename)

        if not merge_success:
            logging.error("Failed to merge sectional documents. Aborting finalization.")
            loop_logger.error("Process stopped: Merge step failed.")
        else:
            final_output_filepath = os.path.join(config.OUTPUTS_DIR, final_doc_filename)
            final_feedback_filepath = os.path.join(config.OUTPUTS_DIR, "final_feedback.md")
            final_writer_guidance = os.path.join(config.INSTRUCTIONS_DIR, "writer_guidance_final.md")
            final_validation_guidance = os.path.join(config.INSTRUCTIONS_DIR, "validation_guidance_final.md")
            max_final_iterations = config.MAX_FINAL_ITERATIONS
            final_feedback_content = "No feedback yet. This is the first validation run on the merged document."
            final_document_passed = False

            for i in range(max_final_iterations):
                iteration = i + 1
                logging.info(f"\n{'='*20} FINALIZATION - ITERATION {iteration} {'='*20}")
                loop_logger.info(f"--- Finalization Iteration {iteration} START ---")

                final_validator_manager = create_final_validator_team(llm_config=llm_config, llm_config_fast=llm_config_fast)
                final_validator_proxy = final_validator_manager.groupchat.agent_by_name("Final_Validator_Proxy")
                final_validation_task = get_final_validation_task()
                await final_validator_proxy.a_initiate_chat(recipient=final_validator_manager, message=final_validation_task, clear_history=True)
                loop_logger.info(f"Finalization Iteration {iteration}: Validator team completed.")          

                final_feedback_content = await read_markdown_file_async(final_feedback_filepath)
                issue_counts = parse_feedback_and_count_issues(final_feedback_content)
                logging.info(f"Final Doc Issues Found: Critical={issue_counts['critical']}, Major={issue_counts['major']}, Minor={issue_counts['minor']}")

                if issue_counts['critical'] == 0:
                    logging.info("\n✅ Success! Final document has passed holistic validation.")
                    loop_logger.info("===== Final Document PASSED =====")
                    final_document_passed = True
                    break
                else:
                    logging.warning(f"\n❌ Critical issues found in final document. Starting correction...")
                    # --- PROMPT WRITER SANITIZES FEEDBACK ---
                    logging.info("--- Preparing clean revision request with Prompt_Writer ---")
                    previous_draft = await read_markdown_file_async(final_output_filepath)
                    final_feedback_content = await read_markdown_file_async(final_feedback_filepath)
                    prompt_writer_task = f"""
                    Here is a final document that failed validation and the feedback report. Create a clean [REVISION_REQUEST] for the Document_Polisher.

                    **Document to Revise:**
                    {previous_draft}

                    **Feedback Report:**
                    {final_feedback_content}
                    """
                    clean_final_request = await final_prompt_writer.a_generate_reply(messages=[{"role": "user", "content": prompt_writer_task}])

                    # --- FINAL WRITER TEAM ---
                    logging.info("--- Kicking off Final Writer Team for correction ---")
                    final_writer_manager = create_final_writer_team(llm_config=llm_config, llm_config_fast=llm_config_fast)
                    final_writer_proxy = final_writer_manager.groupchat.agent_by_name("Final_Writer_Proxy")
                    final_writer_task = get_final_writer_task(clean_final_request)
                    
                    await final_writer_proxy.a_initiate_chat(recipient=final_writer_manager, message=final_writer_task, clear_history=True)
                    loop_logger.info(f"Finalization Iteration {iteration}: Writer team completed correction.")

            if not final_document_passed:
                logging.error(f"\n🚫 FAILED: Final document could not be corrected after {max_final_iterations} iterations.")
                loop_logger.error("===== Final Document FAILED TO PASS. =====")
                process_completed_successfully = False
    
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