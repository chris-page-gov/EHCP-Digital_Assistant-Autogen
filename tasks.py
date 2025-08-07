import os
from utils import PROCESSED_DOCS_DIR, OUTPUTS_DIR, INSTRUCTIONS_DIR
from validator_heavy import create_validator_team

def get_creation_task(section_number: str) -> str:
    """
    Generates the initial creation task prompt for a given section.
    This is used for the very first attempt (Iteration 1).
    """
    writer_guidance_file = os.path.join(INSTRUCTIONS_DIR, f"writer_guidance_s{section_number}.md")
    output_filepath = os.path.join(OUTPUTS_DIR, f"output_s{section_number}.md")
    
    return f"""
You are the writer team. Your task is to generate the summary document for section '{section_number}'.

**Your Plan:**
1.  **Read Files:** The `Writer_User_Proxy` must read the writer's guidance at '{writer_guidance_file}' and all source documents from the '{PROCESSED_DOCS_DIR}' folder.
2.  **Draft Content:** The `Document_Writer` must synthesize this information into a complete draft.
3.  **Save Output:** The `Writer_User_Proxy` must save the final draft to '{output_filepath}'.
4.  **Terminate:** The `Planner` will then confirm the save and terminate the task.
"""

def get_correction_task(section_number: str, clean_request: str) -> str:
    """
    Generates the correction task using a pre-cleaned revision request.
    """
    writer_guidance_file = os.path.join(INSTRUCTIONS_DIR, f"writer_guidance_s{section_number}.md")
    output_filepath = os.path.join(OUTPUTS_DIR, f"output_s{section_number}.md")
    feedback_filepath = os.path.join(OUTPUTS_DIR, f"feedback_s{section_number}.md")
    
    
    return f"""
You are the writer team. Your task is to revise the document for section '{section_number}' based on a clean set of instructions.

{clean_request}

**Your Plan:**
1. **Read Files: ** The 'Writer_User_proxy' must read the writer's guidance at '{writer_guidance_file}' and all source documents from the '{PROCESSED_DOCS_DIR}' folder.
1. **Revise Content:** The `Document_Writer` must execute the revision request.
2. **Save Output:** The `Writer_User_Proxy` must save the new draft to '{output_filepath}'.
3. **Terminate:** The `Planner` will then confirm the save and terminate the task.
"""
    
def get_final_validation_task(final_output_filepath: str, final_validation_guidance: str, final_feedback_filepath: str) -> str:
    """Generates the structured task for the final holistic validation team."""
    return f"""
Your task is a holistic review of the complete document at '{final_output_filepath}'.

**Workflow:**
1.  **Read Files:** The `Final_Validator_Proxy` will read the validation rules from '{final_validation_guidance}', the full document at '{final_output_filepath}', and the source documents from the {PROCESSED_DOCS_DIR}' folder.
2.  **Holistic Review:** The `Holistic_Assessor` will perform a full review, focusing on consistency, duplication, and flow.
3.  **Save Report:** The `Final_Validator_Proxy` will save the consolidated feedback to '{final_feedback_filepath}'.
4.  **Terminate:** The `Final_Validator_Proxy` will then terminate by replying with 'VALIDATION_COMPLETE'.

Begin the process.
"""

def get_final_writer_task(final_output_filepath: str, final_writer_guidance: str, clean_request: str) -> str:
    """Generates the final correction task using a pre-cleaned revision request."""
    return f"""
The merged document requires polishing and correction based on the following clean instructions. Your task is to correct the document at '{final_output_filepath}'.

{clean_request}

**Your Plan:**
1. **Revise Content:** The `Document_Polisher` must execute the revision request.
2. **Save Output:** The `Final_Writer_Proxy` must save the new, polished draft back to '{final_output_filepath}'.
3. **Terminate:** The `Planner` will then confirm the save and terminate the task.
"""

def get_validation_task(section_number: str, llm_config: dict, llm_config_fast: dict):
    """
    Initializes and runs the full validator team for a specific section.
    """
    output_filepath = os.path.join(OUTPUTS_DIR, f"output_s{section_number}.md")
    feedback_filepath = os.path.join(OUTPUTS_DIR, f"feedback_s{section_number}.md")
    validation_guidance_file = os.path.join(INSTRUCTIONS_DIR, f"validation_guidance_s{section_number}.md")
    
    print("\n--- Kicking off Validator Team ---")
    validator_manager = create_validator_team(llm_config=llm_config, llm_config_fast=llm_config_fast)
    
    # Get the proxy agent from the team to initiate the chat
    validator_proxy_agent = validator_manager.groupchat.agent_by_name("Validator_User_Proxy")

    validator_task = f"""
Please perform a full validation of the document at '{output_filepath}'.

**Workflow:**
1.  **Read Initial Files:** `Validator_User_Proxy` will read the validation guidance at '{validation_guidance_file}' and the target document at '{output_filepath}'.
2.  **Quality Check:** `Quality_Assessor` will review the document for structural and rule-based issues based on the files just read.
3.  **Read Source Files for Fact-Checking:** `Validator_User_Proxy` must now list all files in the '{PROCESSED_DOCS_DIR}' directory and use the `read_markdown_file` tool to read the content of **each one**, providing this content to the chat for the next step.
4.  **Fact Check:** Now that the source content is available, the `Fact_Checker` will review the document for factual accuracy.
5.  **Consolidate and Report:** `Quality_Assessor` will create the final, consolidated feedback report, including findings from both agents.
6.  **Save Report:** `Validator_User_Proxy` will save this final report to '{feedback_filepath}'.
7.  **Terminate:** `Validator_User_Proxy` will then terminate by replying with 'VALIDATION_COMPLETE'.

Begin.
"""
    
    validator_proxy_agent.initiate_chat(
        recipient=validator_manager,
        message=validator_task,
        clear_history=True
    )