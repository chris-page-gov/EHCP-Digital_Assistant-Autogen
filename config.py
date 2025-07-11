"""
Configuration settings for the Multi-Agentic Document (MAD) system.
This file centralizes all paths, constants, and patterns used across the project.
"""

from pathlib import Path

# --- Base Directories ---
# This assumes config.py is in the project's root directory.
PROJECT_ROOT = Path(__file__).parent
OUTPUT_DIR = PROJECT_ROOT / "output"
LOGS_DIR = PROJECT_ROOT / "logs"

# Standard locations for instruction and source document files.
# The orchestrator will ensure these exist and are populated.
INSTRUCTIONS_DIR = OUTPUT_DIR / "instructions"
DOCS_DIR = OUTPUT_DIR / "docs"

# --- File Definitions ---
# Prompts and guidance files are now expected to be in the INSTRUCTIONS_DIR
WRITER_PROMPTS_FILE = INSTRUCTIONS_DIR / "writer_prompts.yaml"
VALIDATOR_PROMPTS_FILE = INSTRUCTIONS_DIR / "validator_prompts.yaml"

# Default names for feedback and status files, saved in OUTPUT_DIR
DEFAULT_FEEDBACK_FILENAME = "feedback.md"
VALIDATION_STATUS_FILENAME = "validation_status.json"
LOOP_REPORT_PATH = OUTPUT_DIR / "loop_report.json"

# --- Process Control ---
MAX_ITERATIONS = 5
SUBPROCESS_TIMEOUT_SECONDS = 600  # 10 minutes (kept for reference, not used by new main.py)
ITERATION_DELAY_SECONDS = 3
POST_WRITER_DELAY_SECONDS = 2
MAX_CHAT_ROUNDS = 100 # New setting to prevent runaway conversations

# --- Exit Codes ---
EXIT_SUCCESS = 0
EXIT_VALIDATION_FAILED = 1
EXIT_ERROR = 2
# EXIT_FIX_MODE = 2 # No longer needed; logic is now internal
EXIT_USER_INTERRUPT = 130

# --- Agent and Team Configuration ---
AGENT_NAMES = {
    "user_proxy": "UserProxy",
    "file_surfer": "FileSurfer",
    "document_writer": "DocumentWriter",
    "quality_assessor": "QualityAssessor",
}

# --- Logging Configuration ---
LOG_LEVEL = "INFO"  # e.g., "DEBUG", "INFO", "WARNING"
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
DATE_FORMAT = "%Y-%m-%d_%H-%M-%S"
LOG_PREVIEW_LENGTH = 200

# --- File and Pattern Matching ---
PDF_FILE_PATTERN = "*.pdf"
DOCUMENT_FILE_PATTERN = "*.md"
DEFAULT_SECTION_NAME = "unnamed_section"
FILE_ENCODING = "utf-8"
SPECIAL_CHAR_PATTERN = r'[^a-zA-Z0-9\s-]'
SPACE_HYPHEN_PATTERN = r'[\s-]+'
REPLACEMENT_CHAR = '_'

# --- Regex Patterns for Feedback Parsing ---
ISSUE_PATTERNS = {
    'critical': [r'critical issues: (\d+)', r'critical: (\d+)'],
    'major': [r'major issues: (\d+)', r'major: (\d+)'],
    'minor': [r'minor issues: (\d+)', r'minor: (\d+)']
}
CRITICAL_ISSUE_PATTERNS = [
    r"critical issues: (\d+)",
    r"critical: (\d+)",
    r"validation FAILED"
]
PASS_STATUS_PATTERNS = [r"validation PASSED"]
VALID_PYTHON_PATH_PATTERNS = [r"/bin/python\d?(\.\d+)?$", r"/usr/bin/python\d?(\.\d+)?$", r"\\Scripts\\python.exe$"]

# --- Tool Descriptions (for agent prompts) ---
TOOL_DESCRIPTIONS = {
    "save_document": "Save document content to a file in the output directory.",
    "save_document_section": "Save a named section of the document to a markdown file in the output directory.",
    "delete_file": "Safely delete a specific file from the output directory.",
    "save_feedback": "Save the complete validation feedback report to a markdown file.",
}

# --- NEW: STAGE MAPPING FOR ORCHESTRATOR ---
STAGE_TO_FILENAME_MAP = {
    "s1": "section_1_personal_details.md",
    "s2": "section_2_child_overview.md",
    "s3": "section_3_special_educational_needs_and_provision.md",
    "s4": "section_4_health_care_needs_and_health_care_provision.md",
    "s5": "section_5_social_care_needs_and_social_care_provision.md",
}

ALL_SECTION_FILENAMES = list(STAGE_TO_FILENAME_MAP.values())

# --- Display Separators ---
SEPARATOR_STANDARD = "=" * 80
SEPARATOR_MAJOR = "-" * 80
SEPARATOR_ITERATION = "#" * 80
SEPARATOR_MINOR = "-" * 40

# --- Environment Variables ---
REQUIRED_ENV_VARS = [
    "AZURE_OPENAI_API_KEY",
    "AZURE_OPENAI_ENDPOINT",
    "AZURE_OPENAI_MODEL_NAME"
]
DEFAULT_API_VERSION = "2024-05-01-preview"