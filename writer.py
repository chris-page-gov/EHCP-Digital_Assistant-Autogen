import autogen
from autogen import ConversableAgent, UserProxyAgent, GroupChat, GroupChatManager
from typing import List, Dict

from utils import (
    read_markdown_file,
    read_multiple_markdown_files,
    #read_pdf_file,
    list_files_in_directory,
    save_markdown_file,
    is_terminate_message,
    DOCS_DIR,
    OUTPUTS_DIR,
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
                        Your response must always follow the writer's guidance and only contain information that is clearly referenced in the source documents.
                        Your entire response must be ONLY the content of the document itself. Do not add conversational text. Do not add comments or parentheses to explain where information was taken from """
    )

    planner = ConversableAgent(
        name="Planner",
        llm_config=llm_config_fast,
        system_message=
        
        """You are a meticulous planner. Your role is to create a simple, step-by-step plan for the writer team. You do not write content or call tools yourself. Your output must ONLY be the plan.

        **Your plan should always follow this structure:**
        1.  **Read Files:** Direct the `Writer_User_Proxy` to read all necessary files as described in the user's request using the read_multiple_markdown_files tool.
        2.  **Draft/Revise Content:** Direct the `Document_Writer` to synthesize the information and write the document.
        3.  **Save Output:** Direct the `Writer_User_Proxy` to save the resulting draft to the specified file.

        After the file is saved, you must confirm the entire task is complete.
        **Once you see a message confirming the file has been successfully saved, your next response must be one single word: TERMINATE**
        """
    )
 
    
    # Register tools for the UserProxyAgent to call
    for func in [read_markdown_file, list_files_in_directory, save_markdown_file, read_multiple_markdown_files]:
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
        system_message="""You are a 'find and replace' text editor bot.
You will be given a document and a list of explicit "find and replace" or "find and delete" instructions inside a [REVISION_REQUEST].
Your SOLE task is to execute these instructions literally and exactly as they are written.
- **Do not** add any new information.
- **Do not** rephrase or "improve" any text you are not explicitly told to change.
- **Do not** change any formatting unless the instructions tell you to.
- If an instruction says to "replace", you will replace the entire found block with the provided replacement block.
- If an instruction says to "delete", you will delete the entire found block.

Your output must be ONLY the full document text after you have performed all the find-and-replace/delete operations.
"""
        
    )
    
    planner = ConversableAgent(
        name="Planner",
        llm_config=llm_config_fast,
        system_message="""You are a meticulous planner for the final polishing team.
        Your plan is simple:
        1. **Revise Content:** Direct the `Document_Polisher` to execute the revision request from the prompt.
        2. **Save Output:** Direct the `Final_Writer_Proxy` to save the polished document.
        After the file is saved, you MUST confirm the task is complete by replying with the single word: TERMINATE"""
    ) 
    
    tools_to_register = [
        # read_markdown_file,
        # read_multiple_markdown_files, 
        # list_files_in_directory, 
        save_markdown_file,
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
        agents=[final_writer_proxy, document_polisher],
        messages=[],
        max_round=25
    )
    
    manager = GroupChatManager(
        groupchat=groupchat,
        llm_config=llm_config_fast,
        system_message="You are the manager of the final writing team. Follow the Planner's simple plan to revise and save the document."
    )
    
    return manager