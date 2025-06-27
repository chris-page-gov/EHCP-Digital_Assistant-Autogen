"""
Document Writer

This module generates documents from source materials using AI agents.
It reads guidance from guidance.md and creates structured documents based on the template provided.

Exit codes:
- 0: Success - normal generation completed
- 1: Error during execution
- 2: Fix mode - attempted to fix issues from validation feedback
"""

import asyncio
from pathlib import Path
import sys
from typing import Annotated

from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.teams import MagenticOneGroupChat
from autogen_agentchat.ui import Console
from autogen_ext.agents.file_surfer import FileSurfer
from autogen_core.tools import FunctionTool

import config

# Import shared utilities
from utils import (
    setup_logging, check_environment_variables, create_azure_client,
    ensure_directories, sanitize_filename, run_with_error_handling,
    load_prompts
)

# Setup logging
logger, log_filename = setup_logging("document_session")


async def save_document_section(
    content: Annotated[str, "The document content to save"],
    section_name: Annotated[str, "The name of the section being saved"] = ""
) -> str:
    """Save document section content as a separate file. Each section is saved as its own .md file."""
    logger.info(f"=== save_document_section CALLED ===")
    logger.info(f"Section name: '{section_name}'")
    logger.info(f"Content length: {len(content)} characters")
    logger.info(f"Content preview: {content[:config.LOG_PREVIEW_LENGTH]}..." if len(content) > config.LOG_PREVIEW_LENGTH else f"Content: {content}")
    
    ensure_directories(config.OUTPUT_DIR)
    
    try:
        # Generate filename from section name
        if not section_name:
            section_name = config.DEFAULT_SECTION_NAME
            logger.warning("No section name provided, using 'unnamed_section'")
        
        # Strip any file extensions from section_name to prevent double extensions
        if section_name.lower().endswith('.md'):
            logger.warning(f"Section name '{section_name}' contains .md extension - removing it")
            section_name = section_name[:-3]
        elif section_name.lower().endswith('.markdown'):
            logger.warning(f"Section name '{section_name}' contains .markdown extension - removing it")
            section_name = section_name[:-9]
        
        # Sanitize filename
        filename = f"{sanitize_filename(section_name)}.md"
        
        output_path = config.OUTPUT_DIR / filename
        
        # Check if file already exists
        if output_path.exists():
            logger.warning(f"File {filename} already exists - it will be overwritten")
        
        # Log the section being saved
        logger.info(f"Saving section '{section_name}' to {filename}")
        logger.info(f"Full path: {output_path.absolute()}")
        
        # Write the content to the section file
        output_path.write_text(content, encoding=config.FILE_ENCODING)
        
        # Verify file was written
        if output_path.exists():
            file_size = output_path.stat().st_size
            logger.info(f"File written successfully. Size: {file_size} bytes")
        else:
            logger.error(f"File was not created at {output_path}")
        
        logger.info(f"Successfully saved section '{section_name}' to {output_path}")
        logger.info(f"=== save_document_section COMPLETED ===")
        return f"Successfully saved section '{section_name}' to {output_path}"
    
    except Exception as e:
        logger.error(f"Error saving document section '{section_name}': {str(e)}")
        logger.error(f"Exception type: {type(e).__name__}")
        logger.error(f"Full traceback:", exc_info=True)
        return f"Error saving document section '{section_name}': {str(e)}"


async def delete_file(
    filename: Annotated[str, "The name of the file to delete (e.g., 'main_contact_details.md')"]
) -> str:
    """Safely delete a file from the output directory. Only files in the output directory can be deleted."""
    logger.info(f"=== delete_file CALLED ===")
    logger.info(f"Filename to delete: '{filename}'")
    
    try:
        # Ensure we're only deleting files in the output directory
        file_path = config.OUTPUT_DIR / filename
        
        # Security check - ensure the path is within output directory
        try:
            resolved_path = file_path.resolve()
            output_dir_resolved = config.OUTPUT_DIR.resolve()
            
            # Check if the resolved path is within the output directory
            if not str(resolved_path).startswith(str(output_dir_resolved)):
                logger.error(f"Security violation: Attempted to delete file outside output directory: {resolved_path}")
                return f"Error: Cannot delete files outside the output directory"
        except Exception as e:
            logger.error(f"Error resolving path: {e}")
            return f"Error: Invalid file path"
        
        # Check if file exists
        if not file_path.exists():
            logger.warning(f"File not found: {file_path}")
            return f"File not found: {filename}"
        
        # Check if it's a file (not a directory)
        if not file_path.is_file():
            logger.error(f"Not a file: {file_path}")
            return f"Error: {filename} is not a file"
        
        # Log file details before deletion
        file_size = file_path.stat().st_size
        logger.info(f"Deleting file: {file_path} (size: {file_size} bytes)")
        
        # Delete the file
        file_path.unlink()
        
        # Verify deletion
        if not file_path.exists():
            logger.info(f"Successfully deleted file: {filename}")
            logger.info(f"=== delete_file COMPLETED ===")
            return f"Successfully deleted file: {filename}"
        else:
            logger.error(f"File still exists after deletion attempt: {file_path}")
            return f"Error: Failed to delete file {filename}"
            
    except PermissionError:
        logger.error(f"Permission denied when trying to delete: {filename}")
        return f"Error: Permission denied to delete {filename}"
    except Exception as e:
        logger.error(f"Error deleting file '{filename}': {str(e)}")
        logger.error(f"Exception type: {type(e).__name__}")
        logger.error(f"Full traceback:", exc_info=True)
        return f"Error deleting file '{filename}': {str(e)}"


async def main():
    """Main function to run the document writer system."""
    logger.info("Starting Document Writer System")
    print("--- Initializing Document Writer System ---")
    logger.info("=" * 80)
    logger.info("SYSTEM STARTUP - Section-based file output enabled")
    logger.info("=" * 80)
    
    # Check environment
    check_environment_variables(logger)
    
    # Load prompts
    try:
        prompts = load_prompts('writer_prompts.yaml', logger)
        logger.info("Prompts loaded successfully")
    except Exception as e:
        logger.error(f"Failed to load prompts: {e}")
        print(f"ERROR: Failed to load prompts: {e}")
        return config.EXIT_ERROR
    
    # Ensure output directory exists
    ensure_directories(config.OUTPUT_DIR)
    print(f"[OK] Output directory ready at '{config.OUTPUT_DIR}'")
    logger.info(f"Output directory ready at '{config.OUTPUT_DIR}'")
    
    # Setup LLM client
    model_client = create_azure_client(logger)
    
    # Create file management tools
    save_document_tool = FunctionTool(save_document_section, description=config.TOOL_DESCRIPTIONS.get("save_document_section", config.TOOL_DESCRIPTIONS["save_document"]))
    delete_file_tool = FunctionTool(delete_file, description=config.TOOL_DESCRIPTIONS["delete_file"])
    
    # Define agents (no UserProxy needed for streamlined operation)
    
    # Native MagenticOne FileSurfer agent - can read files including PDFs
    file_surfer = FileSurfer(
        name=config.AGENT_NAMES["file_surfer"],
        model_client=model_client
    )
    
    document_writer = AssistantAgent(
        name=config.AGENT_NAMES["document_writer"],
        model_client=model_client,
        tools=[save_document_tool, delete_file_tool],
        system_message=prompts['document_writer_system_prompt']
    )
    
    print("[OK] Agents configured (FileSurfer, DocumentWriter)")
    logger.info("Agents configured")
    
    # Setup team
    team = MagenticOneGroupChat(
        participants=[file_surfer, document_writer],
        model_client=model_client
    )
    print("[OK] Document writing team assembled with MagenticOne")
    logger.info("Document writing team assembled")
    
    print("\n--- Document Writer System Ready ---")
    print("Available PDF documents in docs folder:")
    docs_dir = config.DOCS_DIR
    pdf_files = list(docs_dir.glob(config.PDF_FILE_PATTERN))
    for pdf in pdf_files:
        print(f"  - {pdf.name}")
        logger.info(f"Found PDF: {pdf.name}")
    
    print(config.SEPARATOR_MINOR)
    
    # Check if feedback.md exists
    feedback_path = config.OUTPUT_DIR / config.DEFAULT_FEEDBACK_FILENAME
    if feedback_path.exists():
        print("\n>>> FEEDBACK DETECTED - Switching to Fix Mode <<<")
        print(f"Found feedback at: {feedback_path}")
        print(f"Absolute path: {feedback_path.absolute()}")
        logger.info(f"Feedback detected at {feedback_path.absolute()} - switching to fix mode")
        
        # Create task for fixing issues
        pdf_files_str = ', '.join([pdf.name for pdf in pdf_files])
        task = prompts['fix_mode_task_template'].format(pdf_files=pdf_files_str)
    else:
        # Auto-generate the document request
        print("\n>>> Starting Document Generation <<<")
        logger.info("Starting document generation")
        
        # Create the task for new document generation
        pdf_files_str = ', '.join([pdf.name for pdf in pdf_files])
        task = prompts['generation_mode_task_template'].format(pdf_files=pdf_files_str)
    
    exit_code = config.EXIT_SUCCESS  # Default to success
    
    try:
        stream = team.run_stream(task=task)
        console = Console(stream)
        await console
        print("\n[OK] Document generation completed.")
        logger.info("Document generation completed successfully")
        
        # Set exit code based on mode
        if feedback_path.exists():
            # Fix mode - return 2 to indicate fixes were attempted
            exit_code = config.EXIT_FIX_MODE
        else:
            # Normal generation mode - return 0 for success
            exit_code = config.EXIT_SUCCESS
    except Exception as e:
        error_msg = f"ERROR during processing: {e}"
        print(error_msg)
        logger.error(error_msg, exc_info=True)
        exit_code = config.EXIT_ERROR  # Set 1 for errors
    
    print("\n" + config.SEPARATOR_MINOR)
    
    # Cleanup
    await model_client.close()
    print("[OK] System shutdown complete.")
    logger.info("System shutdown complete")
    logger.info(f"Session log saved to: {log_filename}")
    
    return exit_code

if __name__ == "__main__":
    run_with_error_handling(main, "Document Writer")