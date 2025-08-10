import autogen
from autogen import ConversableAgent, UserProxyAgent, GroupChat, GroupChatManager
from typing import Dict

from utils import (
    list_files_in_directory,
    is_terminate_message,
    read_markdown_file_async,
    read_multiple_markdown_files_async,
    save_markdown_file_async,
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
        You will read files when asked and, crucially, you will save the final consolidated feedback report using the `save_markdown_file_async` tool when the `Quality_Assessor` provides it.
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
    for func in [read_markdown_file_async, list_files_in_directory, save_markdown_file_async, read_multiple_markdown_files_async]:
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
