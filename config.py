"""
Configuration settings for MAD - Multi-Agentic Document Generator.
Central location for all configurable values used throughout the system.
"""

from pathlib import Path

# System Configuration
MAX_ITERATIONS = 5
ITERATION_DELAY_SECONDS = 2
POST_WRITER_DELAY_SECONDS = 1
SUBPROCESS_TIMEOUT_SECONDS = 900  # 15 minutes timeout for subprocesses

# Paths
LOGS_DIR = Path("./logs")
OUTPUT_DIR = Path("./output")
DOCS_DIR = Path("./docs")
LOOP_REPORT_PATH = OUTPUT_DIR / "loop_report.json"
DEFAULT_FEEDBACK_FILENAME = "feedback.md"

# Logging
DATE_FORMAT = '%Y-%m-%d_%H-%M-%S'
LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
LOG_LEVEL = "INFO"
LOG_PREVIEW_LENGTH = 100

# Azure OpenAI
DEFAULT_API_VERSION = "2024-12-01-preview"

# File Patterns
DOCUMENT_FILE_PATTERN = "*.md"
PDF_FILE_PATTERN = "*.pdf"
FILE_ENCODING = "utf-8"

# Filename Sanitization
SPECIAL_CHAR_PATTERN = r'[^\w\s-]'
SPACE_HYPHEN_PATTERN = r'[-\s]+'
REPLACEMENT_CHAR = '_'

# Issue Parsing Patterns
ISSUE_PATTERNS = {
    'critical': [
        r'Critical:\s*(\d+)', 
        r'Critical\s+Issues\s+Identified:\s*(\d+)',
        r'Critical\s+Issues:\s*\[(\d+)\]'
    ],
    'major': [
        r'Major:\s*(\d+)', 
        r'Major\s+Issues\s+Identified:\s*(\d+)',
        r'Major\s+Issues:\s*\[(\d+)\]'
    ],
    'minor': [
        r'Minor:\s*(\d+)', 
        r'Minor\s+Issues\s+Identified:\s*(\d+)',
        r'Minor\s+Issues:\s*\[(\d+)\]'
    ]
}

# Validation Status Patterns
CRITICAL_ISSUE_PATTERNS = [
    r'Critical:\s*(\d+)',
    r'Critical\s+Issues\s+Identified:\s*(\d+)',
    r'CRITICAL\s+issues?\s+found',
    r'Status:\s*FAIL',
    r'Overall\s+Status:\s*FAIL',
    r'Overall\s+Compliance\s+Status:\s*\*\*FAIL\*\*',
    r'Critical\s+Issues:\s*\[(\d+)\]'
]

PASS_STATUS_PATTERNS = [
    r'Status:\s*PASS',
    r'Overall\s+Status:\s*PASS',
    r'Critical:\s*0',
    r'No\s+critical\s+issues'
]

# Exit Codes
EXIT_SUCCESS = 0
EXIT_VALIDATION_FAILED = 1
EXIT_ERROR = 2
EXIT_FIX_MODE = 2
EXIT_USER_INTERRUPT = 130

# Agent Configuration
AGENT_NAMES = {
    "file_surfer": "FileSurfer",
    "document_writer": "DocumentWriter",
    "quality_assessor": "QualityAssessor"
}

# Tool Descriptions
TOOL_DESCRIPTIONS = {
    "save_document": "Save document content to file",
    "save_document_section": "Saves the document section content as a separate file. Each section is saved as its own file for modular management.",
    "save_feedback": "Save validation feedback to file",
    "delete_file": "Safely deletes a file from the output directory. Use this to remove incorrectly named or duplicate files before creating the correct ones."
}

# Environment Variables
REQUIRED_ENV_VARS = [
    "AZURE_OPENAI_API_KEY",
    "AZURE_OPENAI_ENDPOINT",
    "AZURE_OPENAI_MODEL_NAME"
]

OPTIONAL_ENV_VARS = [
    "AZURE_OPENAI_API_VERSION"
]

# Default Values
DEFAULT_SECTION_NAME = "unnamed_section"

# Console Output
SEPARATOR_STANDARD = "=" * 80
SEPARATOR_ITERATION = "#" * 80
SEPARATOR_MINOR = "-" * 80

# External Configuration Paths (for future implementation)
PROMPTS_DIR = Path("./prompts")
WRITER_PROMPTS_FILE = PROMPTS_DIR / "writer_prompts.yaml"
VALIDATOR_PROMPTS_FILE = PROMPTS_DIR / "validator_prompts.yaml"

# Security Configuration
# Valid patterns for Python executable paths (for subprocess security)
VALID_PYTHON_PATH_PATTERNS = [
    r"\.venv[/\\]Scripts[/\\]python\.exe$",  # Windows venv
    r"\.venv[/\\]bin[/\\]python\d*$",        # Unix venv
    r"venv[/\\]Scripts[/\\]python\.exe$",    # Windows venv (no dot)
    r"venv[/\\]bin[/\\]python\d*$",          # Unix venv (no dot)
    r"[/\\]usr[/\\]bin[/\\]python\d*$",      # System Python on Unix
    r"[/\\]usr[/\\]local[/\\]bin[/\\]python\d*$",  # Local Python on Unix
    r"Python\d+[/\\]python\.exe$",           # Windows system Python
]