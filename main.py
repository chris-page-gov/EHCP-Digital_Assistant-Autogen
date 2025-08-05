import os
import sys
import logging
import time
import autogen
import litellm
from datetime import datetime
from dotenv import load_dotenv

from writer import create_writer_team, create_final_writer_team
from validator import create_validator_team, create_final_validator_team
from utils import (
    read_markdown_file,
    parse_feedback_and_count_issues,
    preprocess_all_pdfs,
    merge_output_files,
    DOCS_DIR,
    PROCESSED_DOCS_DIR,
    OUTPUTS_DIR,
    INSTRUCTIONS_DIR,
    LOGS_DIR,
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
    os.makedirs(LOGS_DIR, exist_ok=True)

    # ---- Full Output Logger (mirrors console) ----
    # Construct the log filename with the timestamp
    full_log_filename = f"full_run_{run_timestamp}.log"
    full_log_path = os.path.join(LOGS_DIR, full_log_filename)

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
    azure_model_name2 = os.getenv("AZURE_OPENAI_MODEL_NAME2")
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
            #"price": [0.00146, 0.00583]
        }
    ]
    llm_config = {
        "config_list": config_list, 
        "timeout": 120,
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
        "timeout": 240,
        }
    
    #all_agents_created = []

    total_sections = 5
    process_completed_successfully = True
    for section_number in range(1, total_sections + 1):
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
            writer_manager = create_writer_team(llm_config=llm_config, llm_config_fast=llm_config_fast)

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
                    f"The prompt_writer must generate a single, clean [REVISION_REQUEST] prompt for the Document_Writer. "
                    f"Save your refined summary to '{output_filepath}'."
                )

            writer_manager.initiate_chat(recipient=writer_manager, message=writer_task)
            loop_logger.info(f"Section {section_number}, Iteration {iteration}: Writer team completed.")

            # --- VALIDATOR TEAM ---
            logging.info("\n--- Kicking off Validator Team ---")
            validator_manager = create_validator_team(llm_config=llm_config, llm_config_fast=llm_config_fast)
            validator_task = (
                f"Your task is to validate the file '{output_filepath}'.\n"
                f"1. Read your validation rules from '{validation_guidance_file}'.\n"
                f"2. Generate a feedback report based on these rules.\n"
                f"3. Save your feedback report to '{feedback_filepath}'."
            )
            validator_manager.initiate_chat(recipient=validator_manager, message=validator_task)
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

            if iteration >= 2 and issue_counts['critical'] == 0:
                logging.info(f"\n✅ Success! Section {section_number} passed validation.")
                loop_logger.info(f"===== Section {section_number} PASSED =====")
                section_passed = True
                break # Exit inner loop and proceed to the next section
            elif iteration == 1:
                logging.info(f"\n🔄 First iteration complete. Proceeding to mandatory refinement iteration.")
                loop_logger.info(f"Section {section_number}, Iteration 1 complete. Feedback will be used in Iteration 2.")
            else:
                logging.warning(f"\n❌ Critical issues found for Section {section_number}. Retrying...")
                loop_logger.warning(f"Section {section_number}, Iteration {iteration} FAILED. Retrying.")

        # --- After inner loop, check if the section ultimately failed ---
        if not section_passed:
            logging.error(f"\n🚫 FAILED: Section {section_number} could not be completed after {max_iterations} iterations.")
            loop_logger.error(f"===== Section {section_number} FAILED TO PASS. Aborting entire run. =====")
            process_completed_successfully = False
            break # Exit the main section loop


    # Final valiadation phase
    if not process_completed_successfully:
        logging.error("Process stopped before finalization due to failures in sectional generation.")
        loop_logger.error("Aborting. Finalization phase skipped.")
    else:
        logging.info(f"\n{'#'*25} STARTING FINALIZATION PHASE {'#'*25}")
        loop_logger.info("===== Starting Finalization Phase: Merging and Holistic Review =====")

        final_doc_filename = "final_document.md"
        merge_success = merge_output_files(total_sections, OUTPUTS_DIR, final_doc_filename)

        if not merge_success:
            logging.error("Failed to merge sectional documents. Aborting finalization.")
            loop_logger.error("Process stopped: Merge step failed.")
        else:
            final_output_filepath = os.path.join(OUTPUTS_DIR, final_doc_filename)
            final_feedback_filepath = os.path.join(OUTPUTS_DIR, "final_feedback.md")
            final_writer_guidance = os.path.join(INSTRUCTIONS_DIR, "writer_guidance_final.md")
            final_validation_guidance = os.path.join(INSTRUCTIONS_DIR, "validation_guidance_final.md")
            max_final_iterations = 5
            
            final_feedback_content = "No feedback yet. This is the first validation run on the merged document."
            final_document_passed = False

            for i in range(max_final_iterations):
                iteration = i + 1
                logging.info(f"\n{'='*20} FINALIZATION - ITERATION {iteration} {'='*20}")
                loop_logger.info(f"--- Finalization Iteration {iteration} START ---")

                validator_manager = create_final_validator_team(llm_config)
                #all_agents_created.extend(validator_manager.groupchat.agents)
                validator_task = (f"Your task is a holistic review of the document at '{final_output_filepath}'. Read your validation rules from '{final_validation_guidance}'. Generate a feedback report and save it to '{final_feedback_filepath}'.")
                validator_manager.initiate_chat(recipient=validator_manager, message=validator_task)

                final_feedback_content = read_markdown_file(final_feedback_filepath)
                issue_counts = parse_feedback_and_count_issues(final_feedback_content)
                logging.info(f"Final Doc Issues Found: Critical={issue_counts['critical']}, Major={issue_counts['major']}, Minor={issue_counts['minor']}")

                if issue_counts['critical'] == 0:
                    logging.info("\n✅ Success! Final document has passed holistic validation.")
                    loop_logger.info("===== Final Document PASSED =====")
                    final_document_passed = True
                    break
                else:
                    logging.warning(f"\n❌ Critical issues found in final document. Starting correction...")
                    writer_manager = create_final_writer_team(llm_config)
                    #all_agents_created.extend(writer_manager.groupchat.agents)
                    writer_task = (f"The merged document has critical consistency/duplication errors. Your task is to correct the document at '{final_output_filepath}'. Read the correction guidance from '{final_writer_guidance}'. Carefully review the feedback provided below. Load, correct, and re-save the final document.\n\n--- FEEDBACK TO ADDRESS ---\n{final_feedback_content}\n--- END FEEDBACK ---")
                    writer_manager.initiate_chat(recipient=writer_manager, message=writer_task)

            if not final_document_passed:
                logging.error(f"\n🚫 FAILED: Final document could not be corrected after {max_final_iterations} iterations.")
                loop_logger.error("===== Final Document FAILED TO PASS. =====")
                process_completed_successfully = False

    
    
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