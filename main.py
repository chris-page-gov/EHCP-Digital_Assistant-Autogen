import os
import logging
import time
import autogen
import litellm
from datetime import datetime
from dotenv import load_dotenv

from writer import create_writer_team
from validator import create_validator_team
from utils import (
    read_markdown_file,
    parse_feedback_and_count_issues,
    preprocess_all_pdfs,
    DOCS_DIR,
    PROCESSED_DOCS_DIR,
    OUTPUTS_DIR,
    INSTRUCTIONS_DIR,
    LOGS_DIR,
)

# Load environment variables from .env file
load_dotenv()

def setup_logging(run_timestamp: str):
    """
    Configures two loggers with timestamped filenames: one for full output, one for loop tracing.
    Args:
        run_timestamp (str): A string timestamp (e.g., 'YYYY-MM-DD_HH-MM-SS') to use in log filenames.
    """
    # Create logs directory if it doesn't exist
    os.makedirs(LOGS_DIR, exist_ok=True)

    # ---- Full Output Logger (mirrors console) ----
    # Construct the log filename with the timestamp
    full_log_filename = f"full_run_{run_timestamp}.log"
    full_log_path = os.path.join(LOGS_DIR, full_log_filename)
    
    # Get the root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    root_logger.handlers.clear()
    
    # Create a file handler for the full log. Mode is 'w' (write), so no need to change it.
    file_handler = logging.FileHandler(full_log_path, mode='w')
    file_formatter = logging.Formatter('%(asctime)s - %(message)s')
    file_handler.setFormatter(file_formatter)
    
    # Create a stream handler for console output
    stream_handler = logging.StreamHandler()
    stream_formatter = logging.Formatter('%(message)s')
    stream_handler.setFormatter(stream_formatter)
    
    root_logger.addHandler(file_handler)
    root_logger.addHandler(stream_handler)

    # ---- Loop Trace Logger (only for specific milestones) ----
    # Construct the log filename with the timestamp
    loop_log_filename = f"loop_trace_{run_timestamp}.log"
    loop_log_path = os.path.join(LOGS_DIR, loop_log_filename)

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
    os.makedirs(DOCS_DIR, exist_ok=True)
    os.makedirs(PROCESSED_DOCS_DIR, exist_ok=True)
    os.makedirs(OUTPUTS_DIR, exist_ok=True)
    os.makedirs(INSTRUCTIONS_DIR, exist_ok=True)
    print("Environment setup complete.")

def main():
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
    azure_api_version = os.getenv("AZURE_OPENAI_API_VERSION")

    if not all([azure_api_key, azure_endpoint, azure_model_name, azure_api_version]):
        logging.error("Error: One or more Azure OpenAI environment variables are not set.")
        logging.error("Please check your .env file for: AZURE_OPENAI_API_KEY, AZURE_OPENAI_ENDPOINT, AZURE_OPENAI_MODEL_NAME, AZURE_OPENAI_API_VERSION")
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
        "timeout": 120,
        }
    
    #all_agents_created = []

    total_sections = 5
    process_completed_successfully = True
    for section_number in range(4, total_sections + 1):
        logging.info(f"\n{'#'*25} STARTING SECTION {section_number} {'#'*25}")
        loop_logger.info(f"===== Processing Section {section_number} START =====")

    # --- Dynamically generate file paths for the current section ---
        writer_guidance_file = os.path.join(INSTRUCTIONS_DIR, f"writer_guidance_s{section_number}.md")
        validation_guidance_file = os.path.join(INSTRUCTIONS_DIR, f"validation_guidance_s{section_number}.md")
        output_filepath = os.path.join(OUTPUTS_DIR, f"output_s{section_number}.md")
        feedback_filepath = os.path.join(OUTPUTS_DIR, f"feedback_s{section_number}.md")

        # --- Guardrail: Check if guidance files exist before starting ---
        if not os.path.exists(writer_guidance_file) or not os.path.exists(validation_guidance_file):
            logging.error(f"Guidance files for Section {section_number} not found. Searched for:")
            logging.error(f"- {writer_guidance_file}")
            logging.error(f"- {validation_guidance_file}")
            logging.error("Stopping process.")
            loop_logger.error(f"Process stopped: Missing guidance files for Section {section_number}.")
            process_completed_successfully = False
            break # Exit the main section loop


        max_iterations = 10
        feedback_content = "No feedback yet. This is the first attempt."
        section_passed = False

        for i in range(max_iterations):
            iteration = i + 1
            logging.info(f"\n{'='*20} SECTION {section_number} - ITERATION {iteration} {'='*20}")
            loop_logger.info(f"--- Section {section_number}, Iteration {iteration} START ---")

            # --- WRITER TEAM ---
            logging.info("\n--- Kicking off Writer Team ---")
            writer_manager = create_writer_team(llm_config)

            if iteration == 1:
                writer_task = (
                    f"You are the writer team. Your task is to generate a summary document. "
                    f"First, read the guidance document at '{writer_guidance_file}'. "
                    f"Then, read all source documents in the '{PROCESSED_DOCS_DIR}' folder. "
                    f"Generate a summary based on the guidance and the content of the source documents. "
                    f"Finally, save your summary to '{output_filepath}'."
                )

            else:
                writer_task = (
                    f"You are the writer team. Your task is to refine the existing document based on feedback. "
                    f"First, read the guidance document at '{writer_guidance_file}'. "
                    f"Then, read all source documents in the '{PROCESSED_DOCS_DIR}' folder. "
                    f"Next, read the previous output file at '{output_filepath}'. "
                    f"Finally, read the feedback report at '{feedback_filepath}' and incorporate the feedback into your new summary. "
                    f"Save your refined summary to '{output_filepath}'."
                )

            writer_manager.initiate_chat(recipient=writer_manager, message=writer_task)
            #all_agents_created.extend(writer_manager.groupchat.agents)
            loop_logger.info(f"Section {section_number}, Iteration {iteration}: Writer team completed.")

            # --- VALIDATOR TEAM ---
            logging.info("\n--- Kicking off Validator Team ---")
            validator_manager = create_validator_team(llm_config)
            validator_task = (
                f"Your task is to validate the file '{output_filepath}'.\n"
                f"1. Read your validation rules from '{validation_guidance_file}'.\n"
                f"2. Generate a feedback report based on these rules.\n"
                f"3. Save your feedback report to '{feedback_filepath}'."
            )
            validator_manager.initiate_chat(recipient=validator_manager, message=validator_task)
            #all_agents_created.extend(validator_manager.groupchat.agents)
            loop_logger.info(f"Section {section_number}, Iteration {iteration}: Validator team completed.")

            # --- ASSESSMENT ---
            logging.info("\n--- Assessing Feedback ---")
            feedback_content = read_markdown_file(feedback_filepath)
            if "Error:" in feedback_content:
                logging.error(f"Could not read feedback file: {feedback_content}")
                loop_logger.error(f"Section {section_number}: FAILED to read feedback file. Aborting section.")
                break # Exit the inner iteration loop for this section

            issue_counts = parse_feedback_and_count_issues(feedback_content)
            logging.info(f"Section {section_number} Issues Found: Critical={issue_counts['critical']}, Major={issue_counts['major']}, Minor={issue_counts['minor']}")
            loop_logger.info(f"Section {section_number}, Iteration {iteration} Result: Critical={issue_counts['critical']}.")

            if issue_counts['critical'] == 0:
                logging.info(f"\n✅ Success! Section {section_number} passed validation.")
                loop_logger.info(f"===== Section {section_number} PASSED =====")
                section_passed = True
                break # Exit inner loop and proceed to the next section
            else:
                logging.warning(f"\n❌ Critical issues found for Section {section_number}. Retrying...")
                loop_logger.warning(f"Section {section_number}, Iteration {iteration} FAILED. Retrying.")

        # --- After inner loop, check if the section ultimately failed ---
        if not section_passed:
            logging.error(f"\n🚫 FAILED: Section {section_number} could not be completed after {max_iterations} iterations.")
            loop_logger.error(f"===== Section {section_number} FAILED TO PASS. Aborting entire run. =====")
            process_completed_successfully = False
            break # Exit the main section loop

    logging.info(f"\n{'#'*25} PROCESS COMPLETE {'#'*25}")
    loop_logger.info("Main process finished.")

    end_time = time.monotonic()
    total_duration_seconds = end_time - start_time
    total_duration_minutes = total_duration_seconds / 60

    # unique_agents = list({agent.name: agent for agent in all_agents_created}.values())
    # usage_summary = calculate_total_cost_and_tokens(unique_agents)

    loop_logger.info("=" * 40)
    loop_logger.info("            RUN SUMMARY")
    loop_logger.info("=" * 40)
    if process_completed_successfully:
        loop_logger.info("Overall Status: SUCCESS")
    else:
        loop_logger.info("Overall Status: FAILED / STOPPED EARLY")
    
    loop_logger.info(f"Total Execution Time: {total_duration_seconds:.2f} seconds ({total_duration_minutes:.2f} minutes)")
    # loop_logger.info(f"Total API Cost: ${usage_summary['total_cost']:.4f}")
    # loop_logger.info(f"Total Tokens: {usage_summary['total_tokens']}")
    # loop_logger.info(f"  - Prompt Tokens: {usage_summary['prompt_tokens']}")
    # loop_logger.info(f"  - Completion Tokens: {usage_summary['completion_tokens']}")
    loop_logger.info("=" * 40)

if __name__ == "__main__":
    main()