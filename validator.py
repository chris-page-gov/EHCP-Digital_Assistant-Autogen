import autogen
from autogen import ConversableAgent, UserProxyAgent, GroupChat, GroupChatManager
from typing import Dict

from utils import (
    read_markdown_file,
    save_markdown_file,
    OUTPUTS_DIR,
)

# Create main validator team with agents for validation and quality assessment.
# This team is responsible for validating the document against criteria and generating a feedback report.
def create_validator_team(llm_config: Dict) -> GroupChatManager:
    """
    Creates and configures the validator multi-agent team.
    """
    validator_user_proxy = UserProxyAgent(
        name="Validator_User_Proxy",
        is_termination_msg=lambda x: x.get("content", "") and "FINAL" in x.get("content", ""),
        human_input_mode="NEVER",
        max_consecutive_auto_reply=10,
        code_execution_config={"use_docker": False},
        llm_config=llm_config,
        system_message="You are the user proxy for the validation team. "
                       "Your job is to manage the validation workflow by calling the correct tools. "
                       "Ensure the feedback report is generated and then you MUST save it correctly to a file using the save_markdown_file tool. "
                       "After the feedback file is saved, reply with the word 'FINAL' to terminate."
    )

    quality_assessor = ConversableAgent(
        name="Quality_Assessor",
        llm_config=llm_config,
        system_message="You are a quality assurance expert. Your role is to assess a given document "
                       "against a set of validation criteria. You must be objective and identify issues, "
                       "categorizing them as Critical, Major, or Minor. "
                       "You will produce a structured feedback report in markdown format as instructed. Do not call any tools."
    )

    # Register tools for the UserProxyAgent to call
    for func in [read_markdown_file, save_markdown_file]:
        autogen.agentchat.register_function(
            func,
            caller=validator_user_proxy,
            executor=validator_user_proxy,
            name=func.__name__,
            description=func.__doc__,
        )

    groupchat = GroupChat(
        agents=[validator_user_proxy, quality_assessor],
        messages=[],
        max_round=10
    )
    
    manager = GroupChatManager(
        groupchat=groupchat,
        
        llm_config=llm_config
    )
    
    return manager


# Create final validator team for holistic review.
# This team is responsible for the final validation of the document, ensuring consistency and logical flow.
# It will produce a structured feedback report based on final validation guidelines.
def create_final_validator_team(llm_config: Dict) -> GroupChatManager:
    """
    Creates and configures the FINAL validator team for holistic review.
    """
    final_validator_proxy = UserProxyAgent(
        name="Final_Validator_Proxy",
        is_termination_msg=lambda x: x.get("content", "") and "FINAL" in x.get("content", ""),
        human_input_mode="NEVER",
        max_consecutive_auto_reply=10,
        code_execution_config={"use_docker": False},
        llm_config=llm_config,
        system_message="You are the user proxy for the final validation team. "
                       "Manage the workflow by calling tools to read the document and save the feedback report. "
                       "Reply with 'FINAL' after the report is saved."
    )

    holistic_assessor = ConversableAgent(
        name="Holistic_Assessor",
        llm_config=llm_config,
        system_message="You are an expert Quality Assurance editor. Your task is a **holistic review** of a complete document. "
                       "Your primary focus is on ensuring **consistency, logical flow, and eliminating redundancy** between sections. "
                       "You must identify contradictions and significant duplication, recommending where duplicated content should be moved. "
                       "You will produce a structured feedback report based on final validation guidelines."
    )

    # Register tools for the proxy agent to call
    for func in [read_markdown_file, save_markdown_file]:
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
        max_round=10
    )
    
    manager = GroupChatManager(
        groupchat=groupchat,
        llm_config=llm_config
    )
    
    return manager