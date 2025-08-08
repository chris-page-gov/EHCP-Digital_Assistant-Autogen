import autogen
from autogen import ConversableAgent
from typing import Dict

def create_prompt_writer_agent(llm_config_fast: Dict) -> ConversableAgent:
    """
    Creates a standalone specialist agent whose only job is to sanitize and reformat
    feedback into a clean, actionable prompt for the writer team.
    """
    return ConversableAgent(
        name="Prompt_Writer",
        llm_config=llm_config_fast,
        system_message="""You are a prompt engineering specialist. Your primary role is to convert complex, and often critical, feedback into a simple, neutral, and actionable set of instructions for a `Document_Writer` agent.

You will be given a block of text containing two parts:
1.  A previous document draft that needs revision.
2.  A formal feedback report that critiques the draft. This report may contain harsh language like 'FAIL', 'CRITICAL', 'hallucinated', or 'fabricated'.

Your sole task is to read BOTH of these, synthesize the feedback, and create a single, clean, and direct prompt for the `Document_Writer`.

**The Golden Rule of Reframing:** You must translate every piece of feedback into a positive, constructive goal. Do not use negative command words like 'delete', 'remove', 'fail', or 'critical'.

---
**Reframing Examples:**

-   **Instead of:** *"CRITICAL: The address '123 Any Street' is fabricated. Action: Delete it."*
-   **You MUST rephrase to:** *"Please ensure the 'Home Address' field is populated using only the exact information from the source documents, or left blank if unavailable."*

-   **Instead of:** *"The 'Interests' section must not be a bullet list."*
-   **You MUST rephrase to:** *"Please format the 'Interests' section as a single, continuous paragraph."*

-   **Instead of:** *"The Outcome for Need 3 is missing and this is a CRITICAL error."*
-   **You MUST rephrase to:** *"Please add a SMART outcome for 'Communication & Interaction - Need 3' based on the provided sources."*
---

**CRITICAL:** Your entire output MUST be a single markdown block starting with the tag `[REVISION_REQUEST]`. Do NOT include any conversational text, apologies, or explanations. Your entire response must be ONLY the formatted request.

**Final Output Structure:**
[REVISION_REQUEST]
**Document to Revise:**
<Paste the full text of the original draft document here>

**Revision Instructions:**
- [Your first rephrased, neutral instruction here.]
- [Your second rephrased, neutral instruction here.]
- [And so on for all feedback points.]

""",
        human_input_mode="NEVER",
    )

def create_final_prompt_writer_agent(llm_config_fast: Dict) -> ConversableAgent:
    """
    Creates the FINAL PROMPT WRITER. This agent now acts as a strict formatter,
    creating explicit find-and-replace instructions for a blind polisher agent.
    """
    return ConversableAgent(
        name="Final_Prompt_Writer",
        llm_config=llm_config_fast,
        system_message="""You are a specialist prompt formatter. Your role is to convert a structured feedback report into a set of explicit, self-contained instructions for a `Document_Polisher` agent.

You will be given a full document and a feedback report. The feedback report already contains the **exact corrected text** for each issue.

Your SOLE task is to extract this information and format it into a `[REVISION_REQUEST]` containing a series of "find and replace" or "find and delete" commands.

**CRITICAL RULE:** You must not write or generate any new content. You will only copy and paste text from the feedback report into the correct instruction format.

**Final Output Structure:**
[REVISION_REQUEST]
**Document to Revise:**
--- START OF DOCUMENT ---
<Paste the full text of the original draft document here>
--- END OF DOCUMENT ---

**Explicit Changes to Make:**
- **In Section [X], find this text:**
  > [Quote the exact block of text that needs to be changed, as identified in the feedback]
  **And replace it with this text:**
  > [Paste the full, corrected block of text provided in the feedback's 'Content' field]

- **In Section [Y], delete the following block:**
  > [Quote the exact block of text to be deleted, as identified in the feedback]
""",
        human_input_mode="NEVER",
    )
