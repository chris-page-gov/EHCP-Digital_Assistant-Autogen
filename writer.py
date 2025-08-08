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
        system_message= """You are a professional document writer. Your job is to synthesize information from the provided text into a document.
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
        1.  **Read Guidance:** Direct the `Writer_User_Proxy` to read ONLY the single guidance file specified in the task.
        2.  **Read Sources:** After the guidance is read, direct the `Writer_User_Proxy` to read ALL the source documents from the `processed_docs` folder.
        3.  **Draft Content:** After all sources are read, direct the `Document_Writer` to synthesize ALL the provided information to write the document.
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


# Create final writer team for polishing and correction.
# This team is responsible for the final polishing of the document
def create_final_writer_team(llm_config: Dict, llm_config_fast: Dict) -> GroupChatManager:
    """
    Creates and configures the FINAL writer team for polishing and correction.
    """
    final_writer_proxy = UserProxyAgent(
        name="Final_Writer_Proxy",
        is_termination_msg=is_terminate_message,
        human_input_mode="NEVER",
        max_consecutive_auto_reply=30,
        code_execution_config={"use_docker": False},
        llm_config=llm_config_fast,
        system_message="""You are the user proxy for the final polishing team.
        You execute tool calls as directed by the Planner.
        After successfully saving the corrected final document, your job is complete.
        The Planner will signal the end of the task by replying with the single word 'TERMINATE'."""
    )

    document_polisher = ConversableAgent(
        name="Document_Polisher",
        llm_config=llm_config,
        system_message="""You are a hyper-literal text processing bot. You will perform a series of 'find and replace' or 'find and delete' operations on a given document.

        **Your process is a strict, unchangeable algorithm:**
        1.  **Identify the Baseline:** Locate the full, original document text provided in the prompt under the `**Document to Revise:**` heading.
        2.  **Execute Changes Sequentially:** Go through the list under `**Explicit Changes to Make:**` one by one. For each instruction, perform the find-and-replace or find-and-delete operation on the baseline text.
        3.  **Preserve Everything Else:** The Golden Rule is that any text not explicitly targeted by a 'find' instruction MUST be preserved in its original form and position.

        **CRITICAL OUTPUT RULE:** Your final, entire response must be the **complete and full text of the document** after all modifications have been made. Do not output conversational text, explanations, or just the sections you changed. The output must be the whole document, from the first character to the last.

        **NEVER say anything like 'See original text above for full body'. ALWAYS include the full text in your output**
        """
        
    )
    
    planner = ConversableAgent(
        name="Planner",
        llm_config=llm_config_fast,
        system_message="""You are a meticulous planner for the final polishing team.
        Your plan is simple:
        1. **Revise Content:** Direct the `Document_Polisher` to execute the revision request from the prompt.
        2. **Save Output:** Direct the `Final_Writer_Proxy` to save the polished document.
        After the file is saved, you MUST confirm the task is complete by replying with the single word: "TERMINATE"."""
    ) 
    
    tools_to_register = [
        # read_markdown_file,
        # read_multiple_markdown_files, 
        # list_files_in_directory, 
        save_markdown_file_async,
    ]
    for func in tools_to_register:
        autogen.agentchat.register_function(
            func,
            caller=final_writer_proxy,
            executor=final_writer_proxy,
            name=func.__name__,
            description=func.__doc__,
        )

    # The group chat for the final team.
    groupchat = GroupChat(
        agents=[final_writer_proxy, document_polisher, planner],
        messages=[],
        max_round=25
    )
    
    manager = GroupChatManager(
        groupchat=groupchat,
        llm_config=llm_config_fast,
        system_message="You are the manager of the final writing team. Follow the Planner's simple plan to revise and save the document."
    )
    
    return manager