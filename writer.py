import autogen
from autogen import ConversableAgent, UserProxyAgent, GroupChat, GroupChatManager
from typing import List, Dict

from utils import (
    read_markdown_file,
    #read_pdf_file,
    list_files_in_directory,
    save_markdown_file,
    DOCS_DIR,
    OUTPUTS_DIR,
)

# Create main writer team with agents for writing, planning, fact-checking, and prompt engineering.
# This team is responsible for drafting the document, fact-checking it, and generating prompts for revisions.
def create_writer_team(llm_config: Dict) -> GroupChatManager:
    """
    Creates and configures the writer multi-agent team.
    """
    writer_user_proxy = UserProxyAgent(
        name="Writer_User_Proxy",
        is_termination_msg=lambda msg: isinstance(msg.get("content"), str) and msg.get("content", "").strip() == "FINAL",
        human_input_mode="NEVER",
        max_consecutive_auto_reply=10,
        code_execution_config={"work_dir": "outputs", "use_docker": False},
        llm_config=llm_config,
        system_message="""You are the user proxy and tool executor for the writer team.
        Your role is to execute file operations precisely when instructed by the Planner.
        - When a task begins, you will read the files as instructed.
        - When the Planner confirms a document is APPROVED and instructs you to save, you MUST use the `save_markdown_file` tool to save the final content.
        - After successfully saving the file, your response MUST be only the single word 'FINAL'. This is your only function after a successful save.
        """
    )

    document_writer = ConversableAgent(
        name="Document_Writer",
        llm_config=llm_config,
        system_message= "You are a professional document writer. Your job is to synthesize information into a clear document. "
                        "If you are given feedback on a previous version, your primary goal is to **refine the existing content** to address "
                        "the specific issues raised. Do not start over unless explicitly told to."
                        "Your generated content must be based entirely on the provided guidance and source documents. "
    )

    planner = ConversableAgent(
        name="Planner",
        llm_config=llm_config,
        system_message="""You are a meticulous planner and workflow manager. Your primary role is to create a precise, step-by-step plan for the team. You do not write content or call tools yourself.

                        Your output is typically ONLY the plan. However, you have one critical exception to this rule for managing the end of the workflow.

                        ---
                        **CRITICAL RULE: Workflow Management and Termination**

                        Your most important responsibility is to recognize when the writing task is complete.
                        1.  The task is complete ONLY when the `Fact_Checker` agent's message is "APPROVED".
                        2.  When you see "APPROVED", your next action is NOT to create a new plan.
                        3.  Instead, your response must be to explicitly instruct the `Writer_User_Proxy` to perform the final save and terminate the conversation.

                        **Your required final response must be:**
                        "The document has been approved. Writer_User_Proxy, please save the final document and then reply with the single word 'FINAL'."

                        This instruction takes priority over all other planning functions once the 'APPROVED' state is reached.
                        ---

                        **Planning for Initial Creation (Iteration 1):**
                        When the initial task is given, your plan MUST follow this structure:
                        1.  **Read Guidance & Sources:** Direct the `Writer_User_Proxy` to read the writer's guidance and all source documents from the `processed_docs` folder.
                        2.  **Draft Content:** Direct the `Document_Writer` to synthesize the gathered information into a DRAFT of the document section.
                        3.  **Fact-Check Draft:** Direct the `Fact_Checker` to review the draft produced by the `Document_Writer` against the source document content. The `Fact_Checker` must either state "APPROVED" or provide a list of corrections.
                        4.  **Generate Revision Request:** If the `Fact_Checker` finds issues, direct the `Prompt_Writer` to create a concise, actionable prompt for the `Document_Writer` to revise the draft.
                        5.  **Finalize Content:** If corrections are needed, direct the `Document_Writer` to create a corrected version and send it back to the `Fact_Checker`. This loop continues until the draft is approved.

                        **Planning for Correction (Based on Validator Feedback):**
                        When the task is to correct a failed validation, your plan MUST follow this structure:
                        1.  **Analyze Feedback & Read Files:** Direct the `Writer_User_Proxy` to read the feedback and the existing incorrect output file.
                        2.  **Generate Concise Revision Request:** Direct the `Prompt_Writer` to create a clean, direct prompt for the `Document_Writer`.
                        3.  **Generate Corrected Draft:** Direct the `Document_Writer` to generate a new DRAFT of the content, focusing on fixing the issues from the feedback.
                        4.  **Fact-Check Corrected Draft:** Direct the `Fact_Checker` to review the new draft against the source documents to ensure no new factual errors were introduced.
                        5.  **Generate Revision Request:** If the `Fact_Checker` finds issues, direct the `Prompt_Writer` to create a concise, actionable prompt for the `Document_Writer` to revise the draft.
                        6.  **Finalize Content:** If corrections are needed, direct the `Document_Writer` to create a corrected version and send it back to the `Fact_Checker`. This loop continues until the draft is approved.
                        
                        """
    )

    fact_checker = ConversableAgent(
        name="Fact_Checker",
        llm_config=llm_config,
        system_message="""You are a meticulous Fact Checker. Your sole purpose is to verify the factual accuracy of text generated by the Document_Writer.

                        You will be given:
                        1.  The full content of the source documents.
                        2.  The draft text generated by the Document_Writer.

                        Your task is to compare the draft text against the source documents and identify any discrepancies, hallucinations, or information that cannot be verified.

                        Your output should be a list of findings. If there are no issues, you MUST respond with the single word "APPROVED". If there are issues, list them clearly, for example:
                        - "The draft mentions the subject's birth date is 10-JAN-2010, but the source document states it is 12-JAN-2010."
                        - "The draft includes the service 'Speech Therapy', which is not mentioned in any of the source documents."
                        """
    )

    prompt_writer = autogen.ConversableAgent(
    name="Prompt_Writer",
    llm_config=llm_config,
    system_message="""You are a prompt engineering specialist. Your primary role is to convert complex, critical feedback into simple, neutral, and actionable instructions for a `Document_Writer` agent.

                    Your input will arrive in one of two forms:
                    1.  **A conversational history** from an internal `Fact_Checker`, containing a draft and a list of required corrections.
                    2.  **A formal feedback report** from an external `Validator`, which critiques a previous draft. This report may contain harsh language like 'FAIL', 'CRITICAL', or 'hallucination'.

                    Regardless of the input's source or tone, your task is always the same:
                    1.  Identify the full text of the document that needs revision.
                    2.  Identify all the required changes from the feedback.
                    3.  **Crucially, you must rephrase all feedback into positive, constructive goals.** Do not use negative command words like 'delete', 'remove', 'fail', or 'critical'. Frame everything as a neutral objective for the next version of the document.

                    ---
                    **The Golden Rule of Reframing:**

                    - **Instead of:** *"CRITICAL: The address is fabricated. Action: Delete it."*
                    - **You should write:** *"Please ensure the 'Home Address' field is populated using only the exact information from the source documents."*

                    - **Instead of:** *"The 'Interests' section must not be a bullet list."*
                    - **You should write:** *"Please format the 'Interests' section as a single, continuous paragraph."*

                    - **Instead of:** *"The Outcome for Need 3 is missing."*
                    - **You should write:** *"Please add a SMART outcome for 'Communication & Interaction - Need 3' based on the provided sources."*
                    ---

                    4.  Combine the original document and your rephrased instructions into a single, clean prompt.

                    **CRITICAL:** Your entire output MUST be a single markdown block starting with the tag [REVISION_REQUEST]. Do NOT include any conversational text, apologies, or explanations. Your entire response must be ONLY the formatted request.

                    **Example Output Format:**
                    [REVISION_REQUEST]
                    **Document to Revise:**
                    <Paste the full text of the original draft document here>

                    **Revision Instructions:**
                    - Please ensure the 'Home Address' field is populated only with verifiable information from the source documents.
                    - Please format the 'NHS Number' as a single string of digits without dashes.
                    - The 'Interests' and 'Strengths' sections should be presented as continuous paragraphs, not bullet points.
                    - A SMART outcome should be added for 'Communication & Interaction - Need 3'.

                    Please provide the fully revised document that meets these requirements.
                    """,
    human_input_mode="NEVER",
)
    
    
    # Register tools for the UserProxyAgent to call
    for func in [read_markdown_file, list_files_in_directory, save_markdown_file]:
        autogen.agentchat.register_function(
            func,
            caller=writer_user_proxy,
            executor=writer_user_proxy,
            name=func.__name__,
            description=func.__doc__,
        )

    # Create the group chat and manager
    groupchat = GroupChat(
        agents=[writer_user_proxy, document_writer, planner, fact_checker, prompt_writer],
        messages=[],
        max_round=25
    )
    
    manager = GroupChatManager(
        groupchat=groupchat,
        llm_config=llm_config
    )
    
    return manager


# Create final writer team for polishing and correction.
# This team is responsible for the final review, fact-checking, and polishing of the document
def create_final_writer_team(llm_config: Dict) -> GroupChatManager:
    """
    Creates and configures the FINAL writer team for polishing and correction.
    """
    final_writer_proxy = UserProxyAgent(
        name="Final_Writer_Proxy",
        is_termination_msg=lambda x: x.get("content", "") and "FINAL" in x.get("content", ""),
        human_input_mode="NEVER",
        max_consecutive_auto_reply=20,
        code_execution_config={"use_docker": False},
        llm_config=llm_config,
        system_message="You are the user proxy for the final polishing team. "
                       "Your job is to manage the correction workflow by calling tools to read the full document, read source documents for verification, and save the final corrected version."
    )

    document_polisher = ConversableAgent(
        name="Document_Polisher",
        llm_config=llm_config,
        system_message="You are a senior editor. Your task is to **polish a complete document**, not create content from scratch. "
                       "You will receive feedback about any inconsistencies and duplication within the final document."
                       "Your job is to resolve these issues by editing, moving, or rephrasing content to improve the overall cohesion and quality of the final document. " \
                       "Do not amend any content that is not mentioned in the feedback. " \
                       "Do not add comments like 'I have fixed issues' or 'No changes made'. Your output should be the polished document content only. "
    )
    
    # 
    fact_checker = ConversableAgent(
        name="Fact_Checker",
        llm_config=llm_config,
        system_message="""You are a meticulous Fact Checker. Your sole purpose is to verify the factual accuracy of text generated by the Document_Writer.

                        You will be given:
                        1.  The full content of the source documents.
                        2.  The draft text generated by the Document_Writer.

                        Your task is to compare the finished text against the source documents and identify any discrepancies, hallucinations, or information that cannot be verified.

                        Your output should be a list of findings. If there are no issues, you MUST respond with the single word "APPROVED". If there are issues, list them clearly, for example:
                        - "The draft mentions the subject's birth date is 10-JAN-2010, but the source document states it is 12-JAN-2010."
                        - "The draft includes the service 'Speech Therapy', which is not mentioned in any of the source documents."
                        """
    )

    tools_to_register = [
        read_markdown_file, 
        #read_pdf_file, 
        list_files_in_directory, 
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
        agents=[final_writer_proxy, document_polisher, fact_checker],
        messages=[],
        max_round=25
    )
    
    manager = GroupChatManager(
        groupchat=groupchat,
        llm_config=llm_config
    )
    
    return manager
