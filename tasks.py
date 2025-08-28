import os
import logging
from validator import create_validator_team
import config
import asyncio

async def _read_local_guidance_files_async(file_paths: list) -> str:
    """Asynchronously reads local guidance files without blocking."""
    loop = asyncio.get_running_loop()
    def _read_sync():
        full_content = ""
        for path in file_paths:
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    full_content += f"--- START OF GUIDANCE FILE: {os.path.basename(path)} ---\n"
                    full_content += f.read()
                    full_content += f"\n--- END OF GUIDANCE FILE ---\n\n"
            except FileNotFoundError:
                logging.error(f"Guidance file not found: {path}")
        return full_content
    return await loop.run_in_executor(None, _read_sync)

async def get_creation_task(section_number: str, output_blob_name: str) -> str:
    """Asynchronously generates the initial creation task prompt."""
    paths = config.get_section_config(section_number) 
    guidance_content = await _read_local_guidance_files_async(paths["writer_guidance"])
    
    return f"""
    Your task is to generate the summary document for section '{section_number}'.
    Your full instructions and rules are provided below:
    {guidance_content}
    First, list all source documents by calling `list_blobs_async` on the '{config.PROCESSED_BLOB_CONTAINER}' container. Then read their content.
    Finally, save your completed document by calling `upload_blob_async` with container '{config.OUTPUT_BLOB_CONTAINER}' and blob name '{output_blob_name}'.
    The Planner must now create a plan.
    """

async def get_correction_task(section_number: str, clean_request: str, output_blob_name: str) -> str:
    """Asynchronously generates the correction task prompt."""
    paths = config.get_section_config(section_number) 
    guidance_content = await _read_local_guidance_files_async(paths["writer_guidance"])

    return f"""
    The document for section '{section_number}' requires revision. Your general guidance is below:
    {guidance_content}
    **To the Document_Writer:** Execute the revision based ONLY on the [REVISION_REQUEST] block.
    **To the Planner:** Ensure the revised text is saved to blob '{output_blob_name}' in container '{config.OUTPUT_BLOB_CONTAINER}' and then terminate.
    {clean_request}
    """

async def run_validation_async(section_number: str, llm_config: dict, llm_config_fast: dict, output_blob_name: str, feedback_blob_name: str):
    """Asynchronously runs the validator team for a section."""
    logging.info(f"\n--- Kicking off Validator Team for Section {section_number} ---")
    paths = config.get_section_config(section_number)
    guidance_content = await _read_local_guidance_files_async(paths["validation_guidance"])

    validator_manager = create_validator_team(llm_config, llm_config_fast)
    validator_proxy_agent = validator_manager.groupchat.agent_by_name("Validator_User_Proxy")

    validator_task = f"""
    Validate the document '{output_blob_name}'. Your rules are below:
    {guidance_content}
    **Workflow:**
    1. Call `download_blob_as_text_async` on container '{config.OUTPUT_BLOB_CONTAINER}' to read '{output_blob_name}'.
    2. Call `download_all_sources_from_container_async` on container '{config.PROCESSED_BLOB_CONTAINER}' to get all source documents.
    3. `Fact_Checker` reviews.
    4. `Quality_Assessor` creates the final report.
    5. Call `upload_blob_async` on container '{config.OUTPUT_BLOB_CONTAINER}' to save the report as '{feedback_blob_name}'.
    6. `Quality_Assessor` terminates.
    Begin.
    """
    await validator_proxy_agent.a_initiate_chat(
        recipient=validator_manager, 
        message=validator_task, 
        clear_history=True
    )
    