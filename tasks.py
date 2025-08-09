import os
import logging
from validator import create_validator_team
import config
import re


def get_creation_task(section_number: str) -> str:
    """
    Generates the initial creation task prompt for a given section.
    This is used for the very first attempt (Iteration 1).
    """
    paths = config.get_path_config(section_number)
    writer_guidance_files = paths["writer_guidance"]
    output_filepath = paths["output"]
    
    return f"""
    Your task is to generate the summary document for section '{section_number}'.
    The combined guidance files are at the following paths: {writer_guidance_files}. 
    The 'Writer_User_Proxy' must read ALL of these files using the `read_multiple_markdown_files_async` tool.

    The source document folder is: '{config.PROCESSED_DOCS_DIR}'
    The final output file must be saved to: '{output_filepath}'

    The Planner must now create a step-by-step plan to achieve this.
    """

def get_correction_task(section_number: str, clean_request: str) -> str:
    """
    Generates the correction task using a pre-cleaned revision request.
    """
    paths = config.get_path_config(section_number)
    writer_guidance_files = paths["writer_guidance"]
    output_filepath = paths["output"]
    
    
    return f"""
Planner, your task is to oversee the revision of the document for section '{section_number}'.

Your first and only action is to direct the `Document_Writer` to execute the revision based *only* on the information provided below inside the [REVISION_REQUEST] block.

After the `Document_Writer` provides the full revised text, your existing plan to save the output to '{output_filepath}' and then terminate will proceed.

{clean_request}
"""

async def run_validation_async(section_number: str, llm_config: dict, llm_config_fast: dict):
    """Asynchronously initializes and runs the full validator team for a specific section."""
    logging.info(f"\n--- Kicking off Validator Team for Section {section_number} ---")

    paths = config.get_path_config(section_number)
    output_filepath = paths["output"]
    feedback_filepath = paths["feedback"]
    validation_guidance_files = paths["validation_guidance"]

    validator_manager = create_validator_team(llm_config, llm_config_fast)
    validator_proxy_agent = validator_manager.groupchat.agent_by_name("Validator_User_Proxy")

    validator_task = f"""
    Please perform a full validation of the document at '{output_filepath}'.

    **Workflow:**
    1.  **Read Initial Files:** `Validator_User_Proxy` will read the validation guidance at '{validation_guidance_files}' and the target document at '{output_filepath}'.
    2.  **Quality Check:** `Quality_Assessor` will review the document for structural and rule-based issues based on the files just read.
    3.  **Read Source Files for Fact-Checking:** `Validator_User_Proxy` must now list all files in the '{config.PROCESSED_DOCS_DIR}' directory and use the `read_markdown_file` tool to read the content of **each one**, providing this content to the chat for the next step.
    4.  **Fact Check:** Now that the source content is available, the `Fact_Checker` will review the document for factual accuracy.
    5.  **Consolidate and Report:** `Quality_Assessor` will create the final, consolidated feedback report, including findings from both agents.
    6.  **Save Report:** `Validator_User_Proxy` will save this final report to '{feedback_filepath}'.
    7.  **Terminate:** `Validator_User_Proxy` will then terminate by replying with 'VALIDATION_COMPLETE'.

    Begin.
    """

    await validator_proxy_agent.a_initiate_chat(
        recipient=validator_manager,
        message=validator_task,
        clear_history=True
    )
    
def get_final_validation_task() -> str:
    """Generates the structured task for the final holistic validation team."""
    
    # Create a list of all sectional output files to be reviewed
    files_to_review = [config.get_path_config(str(i))["output"] for i in range(1, 6)]
    
    return f"""
    Your task is a holistic review of the 5 complete document sections.

    **Workflow:**
    1.  **Read All Files:** The `Final_Validator_Proxy` will:
        a. Read the combined validation rules from the file paths at '{config.FINAL_VALIDATION_GUIDANCE}' using `read_multiple_markdown_files_async`.
        b. Read the content of ALL 5 sectional documents located at: `{files_to_review}` using `read_multiple_markdown_files_async`.
        c. Read all source documents from the '{config.PROCESSED_DOCS_DIR}' folder.
    2.  **Holistic Review:** The `Holistic_Assessor` will perform a full review based on all the provided content.
    3.  **Save Report:** The `Final_Validator_Proxy` will save the consolidated feedback to '{config.FINAL_FEEDBACK_PATH}'.
    4.  **Terminate:** The `Final_Validator_Proxy` will then terminate.

    Begin the process.
    """

def get_final_writer_task(clean_request: str) -> str:
    """Generates the final correction task using a pre-cleaned revision request."""
    return f"""
    The merged document requires polishing. The full document text and a set of explicit instructions are provided below inside the `[REVISION_REQUEST]` block. Your task is to execute these instructions and save the result.

    {clean_request}

    **Your Plan:**
    1. **Execute Revisions:** The `Planner` must instruct the `Document_Polisher` to execute the revision request contained in this prompt. The `Document_Polisher` will then return the complete, modified document text.
    2. **Save Output:** The `Planner` must then instruct the `Final_Writer_Proxy` to save the corrected document text to the final output path: '{config.FINAL_DOCUMENT_PATH}'.
    3. **Terminate:** After the `Final_Writer_Proxy` confirms the save is complete, the `Planner` must reply with the single word "TERMINATE".
    """

