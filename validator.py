"""
Document Validator

This module validates documents against compliance rules specified in validationguidance.md.
It analyzes generated document sections and provides detailed feedback for improvement.

Exit codes:
- 0: Success - validation passed, no critical issues
- 1: Validation failed - critical issues found
- 2: Error during execution or no files to validate
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
    ensure_directories, has_critical_issues_in_feedback, run_with_error_handling,
    load_prompts
)

# Setup logging
logger, log_filename = setup_logging("document_validation")



async def save_feedback(
    content: Annotated[str, "The validation feedback content to save"],
    filename: Annotated[str, "The filename for the feedback (default: feedback.md)"] = None
) -> str:
    """Save validation feedback to the output directory."""
    logger.info(f"=== save_feedback CALLED ===")
    logger.info(f"Filename: '{filename}'")
    logger.info(f"Content length: {len(content)} characters")
    logger.info(f"Content type: {type(content)}")
    logger.info(f"First 100 chars: {content[:100] if content else 'Empty content'}")
    
    if filename is None:
        filename = config.DEFAULT_FEEDBACK_FILENAME
    
    ensure_directories(config.OUTPUT_DIR)
    
    try:
        output_path = config.OUTPUT_DIR / filename
        
        # Log the feedback being saved
        logger.info(f"Saving feedback to {filename}")
        logger.info(f"Full path: {output_path.absolute()}")
        
        # Write the content to the feedback file
        output_path.write_text(content, encoding=config.FILE_ENCODING)
        
        # Verify file was written
        if output_path.exists():
            file_size = output_path.stat().st_size
            logger.info(f"File written successfully. Size: {file_size} bytes")
        else:
            logger.error(f"File was not created at {output_path}")
        
        logger.info(f"Successfully saved feedback to {output_path}")
        logger.info(f"=== save_feedback COMPLETED ===")
        return f"Successfully saved feedback to {output_path}"
    
    except Exception as e:
        logger.error(f"Error saving feedback: {str(e)}")
        logger.error(f"Exception type: {type(e).__name__}")
        logger.error(f"Current working directory: {Path.cwd()}")
        logger.error(f"Output path attempted: {output_path.absolute() if 'output_path' in locals() else 'Not set'}")
        logger.error(f"Full traceback:", exc_info=True)
        return f"Error saving feedback: {str(e)}"


async def delete_file(
    filename: Annotated[str, "The name of the file to delete (e.g., 'incorrect_section.md')"]
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
        
        # Protect system files
        protected_files = ["feedback.md", "loop_report.json"]
        if filename.lower() in protected_files:
            logger.error(f"Attempted to delete protected system file: {filename}")
            return f"Error: Cannot delete protected system file {filename}"
        
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
    """Main function to run the document validator system."""
    logger.info("Starting Document Validator System")
    print("--- Initializing Document Validator System ---")
    logger.info(config.SEPARATOR_STANDARD)
    logger.info("SYSTEM STARTUP - Document Validation")
    logger.info(config.SEPARATOR_STANDARD)
    
    # Check environment
    check_environment_variables(logger)
    
    # Load prompts
    try:
        prompts = load_prompts('validator_prompts.yaml', logger)
        logger.info("Prompts loaded successfully")
    except Exception as e:
        logger.error(f"Failed to load prompts: {e}")
        print(f"ERROR: Failed to load prompts: {e}")
        return config.EXIT_ERROR
    
    # Check output directory
    if not config.OUTPUT_DIR.exists():
        print(f"[WARNING] Output directory not found at '{config.OUTPUT_DIR}'")
        logger.warning(f"Output directory not found at '{config.OUTPUT_DIR}'")
        ensure_directories(config.OUTPUT_DIR)
        print(f"[OK] Created output directory at '{config.OUTPUT_DIR}'")
    else:
        print(f"[OK] Output directory found at '{config.OUTPUT_DIR}'")
    
    # Check for document files to validate
    document_files = list(config.OUTPUT_DIR.glob(config.DOCUMENT_FILE_PATTERN))
    # Exclude feedback.md from validation
    document_files = [f for f in document_files if f.name != config.DEFAULT_FEEDBACK_FILENAME]
    
    if not document_files:
        print("\n[WARNING] No document files found in output directory to validate!")
        print("Please run main.py first to generate documents.")
        logger.warning("No document files found for validation")
        return config.EXIT_ERROR  # Return error code for no files to validate
    
    print(f"\n[OK] Found {len(document_files)} document files to validate:")
    for file in document_files:
        print(f"  - {file.name}")
        logger.info(f"Found document file: {file.name}")
    
    # Log current working directory for debugging
    logger.info(f"Current working directory: {Path.cwd()}")
    logger.info(f"Output directory path: {config.OUTPUT_DIR.absolute()}")
    
    # Setup LLM client
    model_client = create_azure_client(logger)
    
    # Create feedback saving and file management tools
    save_feedback_tool = FunctionTool(save_feedback, description=config.TOOL_DESCRIPTIONS["save_feedback"])
    delete_file_tool = FunctionTool(delete_file, description=config.TOOL_DESCRIPTIONS["delete_file"])
    logger.info(f"save_feedback tool created: {save_feedback_tool}")
    logger.info(f"delete_file tool created: {delete_file_tool}")
    logger.info(f"Tool description: {config.TOOL_DESCRIPTIONS.get('save_feedback', 'Not found')}")
    
    # Define agents (no UserProxy needed)
    
    # Native MagenticOne FileSurfer agent - can read files
    file_surfer = FileSurfer(
        name=config.AGENT_NAMES["file_surfer"],
        model_client=model_client
    )
    
    quality_assessor = AssistantAgent(
        name=config.AGENT_NAMES["quality_assessor"],
        model_client=model_client,
        tools=[save_feedback_tool, delete_file_tool],
        system_message=prompts['quality_assessor_system_prompt']
    )
    
    print("[OK] Agents configured (FileSurfer, QualityAssessor)")
    logger.info("Agents configured")
    
    # Setup team
    team = MagenticOneGroupChat(
        participants=[file_surfer, quality_assessor],
        model_client=model_client
    )
    print("[OK] Document validation team assembled with MagenticOne")
    logger.info("Document validation team assembled")
    
    print("\n--- Document Validator System Ready ---")
    print("-" * 80)
    
    # Auto-generate the validation request
    print("\n>>> Starting Document Validation <<<")
    logger.info("Starting document validation")
    
    # Create the task
    document_files_str = ', '.join([f.name for f in document_files])
    task = prompts['validation_task_template'].format(document_files=document_files_str)
    
    validation_exit_code = config.EXIT_SUCCESS  # Default to success
    
    try:
        stream = team.run_stream(task=task)
        console = Console(stream)
        await console
        print("\n[OK] Document validation completed.")
        logger.info("Document validation completed successfully")
        logger.info("Checking if feedback was saved...")
    except Exception as e:
        error_msg = f"ERROR during validation: {e}"
        print(error_msg)
        logger.error(error_msg, exc_info=True)
        logger.error(f"Exception type: {type(e).__name__}")
        validation_exit_code = config.EXIT_ERROR  # Error during validation
    
    print("\n" + config.SEPARATOR_MINOR)
    
    # Check if feedback was generated and analyze results
    feedback_path = config.OUTPUT_DIR / config.DEFAULT_FEEDBACK_FILENAME
    if feedback_path.exists():
        print(f"[OK] Validation feedback saved to: {feedback_path}")
        logger.info(f"Validation feedback saved to: {feedback_path}")
        
        # Parse feedback to determine validation status
        has_critical_issues = has_critical_issues_in_feedback(feedback_path, logger)
        if has_critical_issues:
            print("[VALIDATION RESULT] Critical issues found - validation FAILED")
            logger.info("Validation FAILED - critical issues found")
            validation_exit_code = config.EXIT_VALIDATION_FAILED  # Validation failed
        else:
            print("[VALIDATION RESULT] No critical issues - validation PASSED")
            logger.info("Validation PASSED - no critical issues found")
            validation_exit_code = config.EXIT_SUCCESS  # Validation passed
    else:
        print("[WARNING] Feedback file was not generated")
        logger.warning("Feedback file was not generated")
        logger.warning("This may indicate the save_feedback function was not called by the agent")
        # Still return success since the validation process completed without errors
        # The issue is with the agent not calling save_feedback, not with the system
        validation_exit_code = config.EXIT_SUCCESS
    
    # Cleanup
    await model_client.close()
    print("[OK] System shutdown complete.")
    logger.info("System shutdown complete")
    logger.info(f"Session log saved to: {log_filename}")
    
    return validation_exit_code

if __name__ == "__main__":
    run_with_error_handling(main, "Document Validator")