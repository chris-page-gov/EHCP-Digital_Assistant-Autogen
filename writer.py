import autogen
from autogen import ConversableAgent, UserProxyAgent, GroupChat, GroupChatManager
from typing import List, Dict

from utils import (
    list_files_in_directory,
    is_terminate_message,
    read_markdown_file_async,
    read_multiple_markdown_files_async,
    save_markdown_file_async,
)

# This team is responsible for drafting the document
def create_writer_team(llm_config: Dict, llm_config_fast: Dict) -> GroupChatManager:
    """
    Creates and configures the writer multi-agent team.
    """
    writer_user_proxy = UserProxyAgent(
        name="Writer_User_Proxy",
        is_termination_msg=is_terminate_message,
        human_input_mode="NEVER",
        max_consecutive_auto_reply=30,
        code_execution_config={"work_dir": "outputs", "use_docker": False},
        llm_config=llm_config_fast,
        system_message="""You are the user proxy and tool executor for the writer team.
                        Your job is to execute tool calls as directed by the Planner (e.g., reading and saving files).
                        You must wait for the Planner to confirm the task is complete.
                        The Planner will signal the end of the task by replying with the single word 'TERMINATE'. Your termination condition is set to detect this word."""
    )

    document_writer = ConversableAgent(
        name="Document_Writer",
        llm_config=llm_config,
        system_message= """You are a professional document writer. Your job is to synthesise information from the provided text into a document.
                        If you receive a [REVISION_REQUEST], refine the document based on the instructions provided. Do not start over unless explicitly told to.
                        Any changes which you make must comply with the writer's guidance. 
                        Your response must always follow the writer's guidance and only contain information that is clearly referenced in the source documents.
                        Your entire response must be ONLY the content of the document itself. Do not add conversational text. Do not add comments or parentheses to explain where information was taken from """
    )

    planner = ConversableAgent(
        name="Planner",
        llm_config=llm_config_fast,
        system_message=
        
        """You are a meticulous planner. Your role is to create a step-by-step plan and ensure it is followed precisely.

        **Your plan is ALWAYS:**
        1.  **Read Guidance:** Direct the `Writer_User_Proxy` to read ALL guidance files specified in the task, likely using the `read_multiple_markdown_files_async` tool.
        2.  **Read Sources:** After the guidance is read, direct the `Writer_User_Proxy` to read ALL the source documents from the `processed_docs` folder.
        3.  **Draft Content:** After all sources are read, direct the `Document_Writer` to synthesise ALL the provided information to write the document.
        4.  **Save Output:** After the draft is complete, direct the `Writer_User_Proxy` to save the result.
        5.  **Terminate:** After the save is confirmed, you MUST respond with the single word: "TERMINATE".

        You will output one step of the plan at a time and wait for it to be completed before announcing the next step. Do not combine steps."""
    )
 
    
    # Register tools for the UserProxyAgent to call
    for func in [read_markdown_file_async, list_files_in_directory, save_markdown_file_async, read_multiple_markdown_files_async]:
        autogen.agentchat.register_function(
            func,
            caller=writer_user_proxy,
            executor=writer_user_proxy,
            name=func.__name__,
            description=func.__doc__,
        )
    
    # Create the group chat and manager
    groupchat = GroupChat(
        agents=[writer_user_proxy, document_writer, planner],
        messages=[],
        max_round=30
    )
    
    manager = GroupChatManager(
        groupchat=groupchat,
        llm_config=llm_config_fast,
        system_message="""You are the manager of a writing team. Your goal is to follow the Planner's simple plan to produce and save a single document.
                        """
    )
    
    return manager
