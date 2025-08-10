import os
import sys
import logging
import time
import litellm
import autogen
from datetime import datetime
from dotenv import load_dotenv
import asyncio


import config
from config import llm_config, llm_config_fast
from orchestrator import process_section
from specialist_agents import create_prompt_writer_agent
from utils import (
    preprocess_all_pdfs,
    merge_output_files,
    clear_directory,
)

# Load environment variables from .env file
load_dotenv()

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

    is_preprocessing_successful = preprocess_all_pdfs()
    if not is_preprocessing_successful:
        logging.critical("Pre-processing failed. Aborting main process.")
        loop_logger.critical("Process aborted due to pre-processing failure.")
        return # Stop execution if pre-processing fails
        
    loop_logger.info("Pre-processing complete. Starting agent workflow.")
    setup_environment()    
    
    prompt_writer = create_prompt_writer_agent(llm_config_fast)
        
    semaphore = asyncio.Semaphore(config.CONCURRENT_SECTIONS)
    
    logging.info(f"Starting concurrent processing for {config.TOTAL_SECTIONS} sections with a limit of {config.CONCURRENT_SECTIONS}.")
    
    sections_to_process = [i for i in range(1, config.TOTAL_SECTIONS + 1)]
    
    # --- CONCURRENT SECTIONAL PROCESSING ---
    processing_tasks = [
        process_section(sec_id, semaphore, llm_config, llm_config_fast, prompt_writer)
        for sec_id in sections_to_process
    ]
    
    section_results = await asyncio.gather(*processing_tasks)
    process_completed_successfully = all(section_results)

    if not process_completed_successfully:
        logging.error("Process stopped before final merge due to failures in sectional generation.")
        loop_logger.error("Aborting. Final merge skipped.")
    else:
        # 4. FINAL MERGE
        logging.info(f"\n{'#'*25} MERGING FINAL DOCUMENT {'#'*25}")
        logging.info("--- Merging all successful section files into the final document. ---")
        merge_success = merge_output_files(config.TOTAL_SECTIONS, config.OUTPUTS_DIR, config.FINAL_DOCUMENT_FILENAME)

        if not merge_success:
            logging.error("Failed to merge sectional documents.")
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
            asyncio.run(main_async())

        except KeyboardInterrupt:
            print("\nProcess interrupted by user. Shutting down.")
            logging.getLogger('LoopTracer').warning("===== PROCESS TERMINATED BY USER =====")

        except Exception as e:
            # This is a catch-all for any other unexpected errors.
            logging.getLogger('LoopTracer').critical(f"===== A FATAL ERROR OCCURRED: {e} =====", exc_info=True)

        finally:        
            print("\n--- Running final cleanup process. ---")
            clear_directory(config.PROCESSED_DOCS_DIR)
