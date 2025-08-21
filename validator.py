import autogen
from autogen import ConversableAgent, UserProxyAgent, GroupChat, GroupChatManager
from typing import Dict

from utils import (
    is_terminate_message,
    download_blob_as_text_async,
    upload_blob_async,
    download_all_sources_from_container_async
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
        You will read files when asked and, crucially, you will save the final consolidated feedback report using the `upload_blob` tool when the `Quality_Assessor` provides it.
        You will listen for the `Quality_Assessor` to say 'TERMINATE', at which point the task will end."""
    )

    quality_assessor = ConversableAgent(
        name="Quality_Assessor",
        llm_config=llm_config,
        system_message="""You are a Quality Assurance expert and report compiler. Your role is to manage the final stages of validation and assemble the report.

        **Your role is strictly limited to:**
        1.  Assessing the draft document ONLY for **structure, formatting, and file rules** (e.g., checking for correct headings, placeholder files, etc.) as defined in the validation guidance.
        2.  Compiling the final feedback report in the **exact format** specified in the guidance.

        **Your workflow is:**
        1.  **Wait** for the `Fact_Checker` to provide its complete and detailed report on all content-related matters.
        2.  **After** the `Fact_Checker` has spoken, you will perform your structural/formatting check.
        3.  You will then create the **single, consolidated feedback report**. This report must integrate your structural findings with the `Fact_Checker`'s entire factual report.
        4.  After the report is saved, your entire response must be the single word TERMINATE to end the task.

        You MUST treat the `Fact_Checker`'s report as the absolute truth for all content issues. You are a report compiler, not a second-level fact-checker. You do not need to consult the source documents.
        """

    )

    fact_checker = ConversableAgent(
        name="Fact_Checker",
        llm_config=llm_config,
        system_message="""You are a meticulous Fact Checker. Your role is to be the ultimate authority on the factual accuracy of a document when compared against the original source materials.

        Your SOLE FOCUS is content verification. Your specific rules for what constitutes a CRITICAL, MAJOR, or MINOR factual error are detailed in the validation guidance provided in the main user prompt. **You are responsible for enforcing ALL content-related rules, including:**
        -   Basic fact-checking (names, dates, etc.).
        -   Anti-hallucination rules.
        -   The "Golden Thread" rules.
        -   The "Provision Specificity" rules.
        -   The "SMART Outcomes" rules.

        **Workflow:**
        1.  Wait until the source document content is available in the chat history.
        2.  Analyze the draft document against the source text, strictly applying all content-related rules from the validation guidance.
        3.  Report your findings as a detailed, clear list of all discrepancies. If there are no issues, your entire response MUST be "ALL FACTS VERIFIED".

        You must not comment on the final report's formatting. You do not call any tools."""
    )


    agent_tools = [
        download_blob_as_text_async,
        upload_blob_async,
        download_all_sources_from_container_async
    ]

    for func in agent_tools:
        description = f"{func.__doc__} The `container_name` argument is required."
        
        autogen.agentchat.register_function(
            func,
            caller=validator_user_proxy,
            executor=validator_user_proxy,
            name=func.__name__,
            description=description
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
        1. `Fact_Checker` (factual review).
        2. `Quality_Assessor` (consolidate and create the single, final report).
        3. `Validator_User_Proxy` (save report).
        4. `Quality_Assessor` (final termination signal).
        Ensure the conversation flows in this exact order."""
    )
    
    return manager
