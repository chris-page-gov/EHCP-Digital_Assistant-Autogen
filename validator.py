import autogen
from autogen import ConversableAgent, UserProxyAgent, GroupChat, GroupChatManager
from typing import Dict

from utils import (
    read_markdown_file,
    save_markdown_file,
    list_files_in_directory,
    read_multiple_markdown_files,
    is_terminate_message,
    OUTPUTS_DIR,
)



# This team is responsible for validating the document against criteria and generating a feedback report.
def create_validator_team(llm_config: Dict, llm_config_fast: Dict) -> GroupChatManager:
    """
    Creates and configures the validator multi-agent team.
    """
    validator_user_proxy = UserProxyAgent(
        name="Validator_User_Proxy",
        is_termination_msg=is_terminate_message,
        human_input_mode="NEVER",
        max_consecutive_auto_reply=20,
        code_execution_config={"use_docker": False},
        llm_config=llm_config_fast,
        system_message="""You are the user proxy and tool executor for the validation team.
        Your job is to execute tool calls as directed by other agents.
        You will read files when asked and, crucially, you will save the final consolidated feedback report using the `save_markdown_file` tool when the `Quality_Assessor` provides it.
        You will listen for the `Quality_Assessor` to say 'TERMINATE', at which point the task will end."""
    )

    quality_assessor = ConversableAgent(
        name="Quality_Assessor",
        llm_config=llm_config,
        system_message="""You are a Quality Assurance expert. Your role is to lead the validation process and produce the final report.

        **Your workflow is:**
        1.  First, you will assess the document against the validation criteria for structure, formatting, and rules, and you will output your initial findings.
        2.  Next, you will wait for the `Fact_Checker` to add its findings on factual accuracy.
        3.  After the `Fact_Checker` has spoken, it is your job to create the **final, consolidated feedback report** in the correct markdown format, which includes both your findings and the Fact_Checker's findings.
        4.  After the `Validator_User_Proxy` has successfully saved your final report to a file, you will be called on one last time. At this point, your **entire response must be the single word `TERMINATE`** to end the task.

        Do not call any tools yourself.

        If the fact checker identifies any facts which are wholly unsupported, or significantly incorrect these must be included as CRITICAL errors in your final report.

        """
    )

    fact_checker = ConversableAgent(
        name="Fact_Checker",
        llm_config=llm_config,
        system_message="""You are a meticulous Fact Checker. Your role is to validate the content of a document against the original source materials.
        Your SOLE FOCUS is on factual accuracy. You must verify every name, date, address, number, and statement in the summary document by comparing it to the text in the source documents.
        **You will wait until the content of the source documents has been provided in the chat history.**
        You will produce a clear, concise list of all factual discrepancies or unsupported claims you find.
        Do not comment on formatting, rules, or structure; that is the Quality_Assessor's job.
        If all facts are correct and verifiable, your entire response should be "ALL FACTS VERIFIED".
        Do not call any tools yourself."""
    )

    # Register tools for the UserProxyAgent to call
    for func in [read_markdown_file, list_files_in_directory, save_markdown_file, read_multiple_markdown_files]:
        autogen.agentchat.register_function(
            func,
            caller=validator_user_proxy,
            executor=validator_user_proxy,
            name=func.__name__,
            description=func.__doc__,
        )

    groupchat = GroupChat(
        agents=[validator_user_proxy, quality_assessor, fact_checker],
        messages=[],
        max_round=40
    )
    
    manager = GroupChatManager(
        groupchat=groupchat,
        llm_config=llm_config_fast,
        system_message="""You are the manager of the validation team. Your role is to coordinate the agents to produce a single, consolidated feedback report.
        Follow the workflow:
        1. `Quality_Assessor` (initial review).
        2. `Fact_Checker` (factual review).
        3. `Quality_Assessor` (consolidate report).
        4. `Validator_User_Proxy` (save report).
        5. `Quality_Assessor` (final termination signal).
        Ensure the conversation flows in this exact order."""
    )
    
    return manager


# Create final validator team for holistic review.
# This team is responsible for the final validation of the document, ensuring consistency and logical flow.
# It will produce a structured feedback report based on final validation guidelines.
def create_final_validator_team(llm_config: Dict, llm_config_fast: Dict) -> GroupChatManager:
    """
    Creates and configures the FINAL validator team for holistic review.
    """
    final_validator_proxy = UserProxyAgent(
        name="Final_Validator_Proxy",
        is_termination_msg=is_terminate_message,
        human_input_mode="NEVER",
        max_consecutive_auto_reply=10,
        code_execution_config={"use_docker": False},
        llm_config=llm_config_fast,
        system_message="""You are the user proxy for the final validation team. 
        Your job is to execute tool calls as directed.
        After the `Holistic_Assessor` provides the final feedback report, you MUST save it using `save_markdown_file`. 
        You will listen for the `Holistic_Assessor` to say 'TERMINATE', at which point the task will end."""
    )

    holistic_assessor = ConversableAgent(
        name="Holistic_Assessor",
        llm_config=llm_config,
        system_message="""You are a senior Quality Assurance editor. Your task is a **holistic review** of a complete, merged document. Your focus is on consistency, logical flow, and eliminating redundancy.

**CRITICAL INSTRUCTION:** For every issue you find, you MUST provide the **exact, complete, and corrected text** that should be used as the replacement. Do NOT just describe the problem; you must provide the solution.

**Your Feedback Format:**
For each issue, you must provide:
1.  **Issue:** A brief description (e.g., "Duplicated content about 'interest in music'").
2.  **Location:** The section and heading where the incorrect text is located.
3.  **Action:** A clear instruction, either 'REPLACE' or 'DELETE'.
4.  **Content:**
    - If the action is 'REPLACE', you must provide the **full, corrected paragraph or block of text** that should be used.
    - If the action is 'DELETE', you can leave this blank or state "N/A".

**Example Finding:**
- **Issue:** Duplicated content about 'interest in music'.
- **Location:** Section B, under 'Hobbies and Interests'.
- **Action:** DELETE
- **Content:** N/A

- **Issue:** Contradictory information about therapy provision.
- **Location:** Section H, under 'Health Care Provision'.
- **Action:** REPLACE
- **Content:** [Provide the full, correct, and consolidated paragraph about the therapy provision here.]

Your final output is a structured feedback report containing a list of these explicit findings.

Once the final report is ready, you will instruct the `Final_Validator_Proxy` to save it using the `save_markdown_file` tool. After saving, you will signal the end of the task by replying with 'TERMINATE'.
"""
    )

    # Register tools for the proxy agent to call
    for func in [read_markdown_file, save_markdown_file, read_multiple_markdown_files]:
        autogen.agentchat.register_function(
            func,
            caller=final_validator_proxy,
            executor=final_validator_proxy,
            name=func.__name__,
            description=func.__doc__,
        )

    groupchat = GroupChat(
        agents=[final_validator_proxy, holistic_assessor],
        messages=[],
        max_round=20
    )
    
    manager = GroupChatManager(
        groupchat=groupchat,
        llm_config=llm_config_fast,
        system_message=""" You are the manager of the final validation team. Your role is to coordinate the agents to produce a final feedback report.
        Follow the workflow:
        1. Validator_User_Proxy (reads the final output document, source documents and final validation guidelines).
        2. `Holistic_Assessor` (completes review).
        3. `Validator_User_Proxy` (save report).
        4. `Holistic_Assessor` (final termination signal).
        Ensure the conversation flows in this exact order. """
    )
    
    return manager