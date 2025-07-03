"""
Shared utilities for the document generation system.

This module contains common functionality used across writer.py, validator.py, and main.py
to reduce code duplication and improve maintainability.
"""

import os
import sys
import logging
from pathlib import Path
from datetime import datetime
import re
from typing import Dict, Optional, Tuple, Any

import dotenv
import nest_asyncio
from autogen_ext.models.openai import AzureOpenAIChatCompletionClient

import config


# Load environment variables once
dotenv.load_dotenv()
nest_asyncio.apply()

# Azure OpenAI Configuration (loaded once)
AZURE_CONFIG = {
    "api_key": os.getenv("AZURE_OPENAI_API_KEY"),
    "endpoint": os.getenv("AZURE_OPENAI_ENDPOINT"),
    "model_name": os.getenv("AZURE_OPENAI_MODEL_NAME"),
    "api_version": os.getenv("AZURE_OPENAI_API_VERSION", config.DEFAULT_API_VERSION)
}


def ensure_directories(*directories: Path) -> None:
    """Create directories if they don't exist."""
    for directory in directories:
        directory.mkdir(exist_ok=True)


def get_path_context(logger: Optional[logging.Logger] = None) -> str:
    """
    Generate a path context string for agents to understand file locations.
    
    Args:
        logger: Optional logger instance for logging messages
    
    Returns:
        String containing working directory and key path information
    """
    cwd = Path.cwd()
    context = f"""
WORKING DIRECTORY:
- You are in: {cwd}
- This is the output directory where all files are located

DIRECTORY STRUCTURE:
- instructions/ - Contains guidance and validation rules
- docs/ - Contains source PDF documents  
- *.md files - Document sections and feedback

FILE ACCESS TIPS:
- All files are in the current directory or subdirectories
- Use simple relative paths:
  * "instructions/writer_guidance.md"
  * "docs/Felicia Bailey app A(2).pdf"
  * "feedback.md"
- To list current directory: use path "."
- To list a subdirectory: use path "instructions" or "docs"
"""
    return context


def setup_logging(log_prefix: str) -> Tuple[logging.Logger, Path]:
    """
    Setup logging configuration with file and console handlers.
    
    Args:
        log_prefix: Prefix for the log filename (e.g., 'document_session', 'validation')
    
    Returns:
        Tuple of (logger instance, log file path)
    """
    ensure_directories(config.LOGS_DIR)
    
    log_filename = config.LOGS_DIR / f"{log_prefix}_{datetime.now().strftime(config.DATE_FORMAT)}.log"
    
    logging.basicConfig(
        level=getattr(logging, config.LOG_LEVEL),
        format=config.LOG_FORMAT,
        handlers=[
            logging.FileHandler(log_filename),
            logging.StreamHandler(sys.stdout)
        ],
        force=True  # Reconfigure logging even if already configured
    )
    
    logger = logging.getLogger(log_prefix)
    return logger, log_filename


def check_environment_variables(logger: Optional[logging.Logger] = None) -> None:
    """
    Check for required environment variables and exit if missing.
    
    Args:
        logger: Optional logger instance for logging messages
    """
    required_vars = {}
    for var in config.REQUIRED_ENV_VARS:
        required_vars[var] = os.getenv(var)
    
    missing_vars = [var for var, val in required_vars.items() if val is None]
    
    if missing_vars:
        error_msg = f"Missing environment variables: {', '.join(missing_vars)}"
        if logger:
            logger.error(error_msg)
        print(f"ERROR: The following environment variables are not set: {', '.join(missing_vars)}")
        print("Please set them in your environment or in a .env file.")
        sys.exit(1)
    
    if logger:
        logger.info("Azure OpenAI environment variables found")
    print("[OK] Azure OpenAI environment variables found.")


def create_azure_client(logger: Optional[logging.Logger] = None) -> AzureOpenAIChatCompletionClient:
    """
    Create and return configured Azure OpenAI client.
    
    Args:
        logger: Optional logger instance for logging messages
    
    Returns:
        Configured AzureOpenAIChatCompletionClient instance
    """
    client = AzureOpenAIChatCompletionClient(
        model=AZURE_CONFIG["model_name"],
        azure_endpoint=AZURE_CONFIG["endpoint"],
        api_version=AZURE_CONFIG["api_version"],
        api_key=AZURE_CONFIG["api_key"],
        azure_deployment=AZURE_CONFIG["model_name"]
    )
    
    if logger:
        logger.info("Azure OpenAI Client configured")
    print("[OK] Azure OpenAI Client configured.")
    
    return client


def sanitize_filename(name: str) -> str:
    """
    Sanitize a string to be used as a filename.
    
    Args:
        name: The string to sanitize
    
    Returns:
        Sanitized filename safe for filesystem use
    """
    # Remove special characters, keep only alphanumeric, spaces, and hyphens
    filename = re.sub(config.SPECIAL_CHAR_PATTERN, '', name.lower())
    # Replace spaces and multiple hyphens with single underscore
    filename = re.sub(config.SPACE_HYPHEN_PATTERN, config.REPLACEMENT_CHAR, filename)
    return filename


def parse_feedback_issues(feedback_path: Path, logger: Optional[logging.Logger] = None) -> Dict[str, int]:
    """
    Parse feedback.md to extract issue counts.
    
    Args:
        feedback_path: Path to the feedback.md file
        logger: Optional logger instance
    
    Returns:
        Dictionary with issue counts for 'critical', 'major', and 'minor'
    """
    try:
        content = feedback_path.read_text(encoding=config.FILE_ENCODING)
        
        issue_counts = {
            'critical': 0,
            'major': 0,
            'minor': 0
        }
        
        # Patterns to match different formats of issue reporting
        patterns = config.ISSUE_PATTERNS
        
        for issue_type, type_patterns in patterns.items():
            for pattern in type_patterns:
                match = re.search(pattern, content, re.IGNORECASE)
                if match:
                    issue_counts[issue_type] = int(match.group(1))
                    break
        
        return issue_counts
        
    except Exception as e:
        if logger:
            logger.error(f"Error parsing feedback issues: {e}")
        return {'critical': -1, 'major': -1, 'minor': -1}


def has_critical_issues_in_feedback(feedback_path: Path, logger: Optional[logging.Logger] = None) -> bool:
    """
    Check if feedback contains critical issues.
    
    Args:
        feedback_path: Path to the feedback.md file
        logger: Optional logger instance
    
    Returns:
        True if critical issues found, False otherwise
    """
    try:
        content = feedback_path.read_text(encoding=config.FILE_ENCODING)
        
        # Look for critical issues indicators
        critical_patterns = config.CRITICAL_ISSUE_PATTERNS
        
        for pattern in critical_patterns:
            match = re.search(pattern, content, re.IGNORECASE)
            if match:
                if match.groups():
                    # If there's a number, check if it's > 0
                    count = int(match.group(1))
                    if count > 0:
                        if logger:
                            logger.info(f"Found {count} critical issues in feedback")
                        return True
                else:
                    # Pattern matched without number (e.g., "CRITICAL issues found")
                    if logger:
                        logger.info("Found critical issues indicator in feedback")
                    return True
        
        # Also check for explicit pass status
        pass_patterns = config.PASS_STATUS_PATTERNS
        
        for pattern in pass_patterns:
            if re.search(pattern, content, re.IGNORECASE):
                if logger:
                    logger.info("Validation passed - no critical issues found")
                return False
        
        # If no clear indicators, log warning
        if logger:
            logger.warning("Could not determine validation status from feedback")
        return False
        
    except Exception as e:
        if logger:
            logger.error(f"Error parsing feedback: {e}")
        return False


def read_validation_status(status_path: Path, logger: Optional[logging.Logger] = None) -> Optional[Dict[str, Any]]:
    """
    Read the structured validation status from JSON file.
    
    Args:
        status_path: Path to the validation_status.json file
        logger: Optional logger instance
    
    Returns:
        Dictionary with validation status or None if file doesn't exist
    """
    import json
    
    try:
        if not status_path.exists():
            if logger:
                logger.warning(f"Validation status file not found: {status_path}")
            return None
            
        with open(status_path, 'r', encoding=config.FILE_ENCODING) as f:
            status_data = json.load(f)
            
        if logger:
            logger.info(f"Loaded validation status: {status_data}")
            
        return status_data
        
    except Exception as e:
        if logger:
            logger.error(f"Error reading validation status: {e}")
        return None


def run_with_error_handling(main_func, script_name: str):
    """
    Wrapper to run a main function with standard error handling.
    
    Args:
        main_func: The async main function to run
        script_name: Name of the script for logging purposes
    """
    import asyncio
    
    try:
        exit_code = asyncio.run(main_func())
        sys.exit(exit_code if exit_code is not None else config.EXIT_SUCCESS)
    except KeyboardInterrupt:
        print(f"\n{script_name} terminated by user.")
        logging.info(f"{script_name} terminated by user")
        sys.exit(config.EXIT_USER_INTERRUPT)  # Standard exit code for Ctrl+C
    except Exception as e:
        error_msg = f"Unexpected error in {script_name}: {e}"
        print(error_msg)
        logging.error(error_msg, exc_info=True)
        sys.exit(config.EXIT_ERROR)  # Use consistent error code


def load_prompts(prompt_file: str, logger: Optional[logging.Logger] = None) -> Dict[str, str]:
    """
    Load prompts from a YAML file.
    
    Args:
        prompt_file: Name of the YAML file (e.g., 'writer_prompts.yaml')
        logger: Optional logger instance
    
    Returns:
        Dictionary of prompt names to prompt texts
    """
    import yaml
    
    # Check if we're already in the output directory
    cwd = Path.cwd()
    if cwd.name == 'output' and cwd.parent.name == 'ehcp-somerset':
        # We're already in output directory, use relative path
        prompt_path = Path('instructions') / prompt_file
    else:
        # We're in the project root, use full path
        prompt_path = config.INSTRUCTIONS_DIR / prompt_file
    
    # Fall back to old prompts directory if file doesn't exist (for migration)
    if not prompt_path.exists() and hasattr(config, 'OLD_PROMPTS_DIR'):
        old_path = config.OLD_PROMPTS_DIR / prompt_file
        if old_path.exists():
            prompt_path = old_path
            if logger:
                logger.warning(f"Loading prompt from old location: {old_path}")
    
    if not prompt_path.exists():
        error_msg = f"Prompt file not found: {prompt_path}"
        if logger:
            logger.error(error_msg)
        raise FileNotFoundError(error_msg)
    
    try:
        with open(prompt_path, 'r', encoding=config.FILE_ENCODING) as f:
            prompts = yaml.safe_load(f)
        
        if logger:
            logger.info(f"Loaded {len(prompts)} prompts from {prompt_file}")
        
        return prompts
    
    except Exception as e:
        error_msg = f"Error loading prompts from {prompt_file}: {e}"
        if logger:
            logger.error(error_msg)
        raise RuntimeError(error_msg)