import config
import logging
import asyncio
from typing import Dict
from autogen import ConversableAgent
from tasks import get_creation_task, get_correction_task, run_validation_async
from writer import create_writer_team
from utils import download_blob_as_text_async, parse_feedback_and_count_issues

async def process_section(section_number: str, semaphore: asyncio.Semaphore, llm_config: Dict, llm_config_fast: Dict, prompt_writer: ConversableAgent):
    """Asynchronously processes a single section, including retries, under a semaphore."""
    async with semaphore:
        logging.info(f"Semaphore acquired for section {section_number}. Starting processing.")
        
        paths = config.get_section_config(section_number) 
        output_blob_name = paths["output_blob_name"] 
        feedback_blob_name = paths["feedback_blob_name"] 
        
        max_iterations = config.MAX_SECTION_ITERATIONS
        loop_logger = logging.getLogger('LoopTracer')

        try: # <--- START OF THE ISOLATION BLOCK
            for i in range(1, max_iterations + 1):
                logging.info(f"\n{'='*20} SECTION {section_number} - ITERATION {i} {'='*20}")
                
                # --- WRITER TEAM ---
                writer_manager = create_writer_team(llm_config, llm_config_fast)
                writer_proxy_agent = writer_manager.groupchat.agent_by_name("Writer_User_Proxy")
                
                if i == 1:
                    writer_task = await get_creation_task(section_number)
                else:
                    logging.info(f"--- Preparing clean revision request for s{section_number} with Prompt_Writer ---")
                    previous_draft = await download_blob_as_text_async(config.OUTPUT_BLOB_CONTAINER, output_blob_name)
                    feedback_report = await download_blob_as_text_async(config.OUTPUT_BLOB_CONTAINER, feedback_blob_name)
                    
                    prompt_writer_task = f"""
                    Here is a document that failed validation and the feedback report. Create a clean [REVISION_REQUEST] for the Document_Writer.

                    **Document to Revise:**
                    {previous_draft}

                    **Feedback Report:**
                    {feedback_report}
                    """

                    clean_request_message = await prompt_writer.a_generate_reply(messages=[{"role": "user", "content": prompt_writer_task}])
                    
                    # The Prompt_Writer might return a raw string or a dict. Handle both cases.
                    if isinstance(clean_request_message, dict):
                        clean_request = clean_request_message.get("content", "")
                    else:
                        clean_request = str(clean_request_message) # Ensure it's a string
                    
                    writer_task = await get_correction_task(section_number, clean_request)
                    
                await writer_proxy_agent.a_initiate_chat(
                    recipient=writer_manager, message=writer_task, clear_history=True
                )
                loop_logger.info(f"Section {section_number}, Iteration {i}: Writer team completed.")

                # --- VALIDATOR TEAM ---
                await run_validation_async(section_number, llm_config, llm_config_fast)
                loop_logger.info(f"Section {section_number}, Iteration {i}: Validator team completed.")
            
                # Assessment
                feedback_content = await download_blob_as_text_async(config.OUTPUT_BLOB_CONTAINER, feedback_blob_name)
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


    