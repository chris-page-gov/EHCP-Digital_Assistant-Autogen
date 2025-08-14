import os
from typing import Any
from dotenv import load_dotenv
from pathlib import Path

load_dotenv()

# --------------------------------------------------------------------------
# 0. BASE DIRECTORY DEFINITIONS
# --------------------------------------------------------------------------
# Core project paths. All other paths are derived from these.
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DOCS_DIR = os.path.join(BASE_DIR, "docs")
PROCESSED_DOCS_DIR = os.path.join(BASE_DIR, "processed_docs")
OUTPUTS_DIR = os.path.join(BASE_DIR, "outputs")
INSTRUCTIONS_DIR = os.path.join(BASE_DIR, "instructions")
LOGS_DIR = os.path.join(BASE_DIR, "logs")

# --------------------------------------------------------------------------
# 1. APPLICATION-LEVEL SETTINGS
# --------------------------------------------------------------------------
# High-level controls for the main process run.
TOTAL_SECTIONS = 3
CONCURRENT_SECTIONS = 3  # Number of sections to process in parallel
MAX_SECTION_ITERATIONS = 10  # Max loops for a single section before failure

# --------------------------------------------------------------------------
# 2. GUIDANCE FILE PARTIALS
# --------------------------------------------------------------------------
# Define the paths to your reusable instruction components.
_PARTIALS_DIR = os.path.join(INSTRUCTIONS_DIR, "partials")

# Reusable components for WRITER agents
WRITER_COMMON_RULES = os.path.join(_PARTIALS_DIR, "_writer_common_rules.md")
NEEDS_PROVISION_OUTCOMES_RULES = os.path.join(
    INSTRUCTIONS_DIR, "partials", "_need_provision_outcome_writer_guidance.md")
NEED_CATEGORISATION_GUIDE = os.path.join(
    _PARTIALS_DIR, "_need_categorisation_guide.md")

# Reusable components for VALIDATOR agents
VALIDATOR_COMMON_FEEDBACK_FORMAT = os.path.join(
    _PARTIALS_DIR, "_validator_common_feedback_format.md")
PROVISION_SPECIFICITY_RULES = os.path.join(
    _PARTIALS_DIR, "_provision_specificity_rules.md")
SMART_OUTCOMES_RULES = os.path.join(_PARTIALS_DIR, "_smart_outcomes_rules.md")
GOLDEN_THREAD_RULES = os.path.join(_PARTIALS_DIR, "_golden_thread_rules.md")

# --------------------------------------------------------------------------
# 3. FINAL DOCUMENT PATHS
# --------------------------------------------------------------------------
# Paths for the final, merged document and its related files.
FINAL_DOCUMENT_FILENAME = "final_document.md"
FINAL_DOCUMENT_PATH = os.path.join(OUTPUTS_DIR, FINAL_DOCUMENT_FILENAME)
FINAL_FEEDBACK_PATH = os.path.join(OUTPUTS_DIR, "final_feedback.md")

# --------------------------------------------------------------------------
# 4. DYNAMIC PATH CONFIGURATION FUNCTION
# --------------------------------------------------------------------------
# A centralized function to get all paths and guidance files for a given section.


def get_path_config(section_number: str) -> dict:
    """
    Returns a dictionary of all necessary file paths and guidance lists
    for a specific section number.
    """
    section_str = str(section_number)

    # Define the unique guidance file for this specific section
    writer_guidance_s = os.path.join(
        INSTRUCTIONS_DIR, f"writer_guidance_s{section_str}.md")
    validation_guidance_s = os.path.join(
        INSTRUCTIONS_DIR, f"validation_guidance_s{section_str}.md")

    # Define common validation guidance for sections needing detailed checks
    validation_common_detailed = [
        validation_guidance_s,
        VALIDATOR_COMMON_FEEDBACK_FORMAT,
        PROVISION_SPECIFICITY_RULES,
        SMART_OUTCOMES_RULES,
        GOLDEN_THREAD_RULES,
    ]

    path_map = {
        "1": {
            "writer_guidance": [writer_guidance_s, WRITER_COMMON_RULES],
            "validation_guidance": [validation_guidance_s, VALIDATOR_COMMON_FEEDBACK_FORMAT],
        },
        "2": {
            "writer_guidance": [writer_guidance_s, WRITER_COMMON_RULES],
            "validation_guidance": [validation_guidance_s, VALIDATOR_COMMON_FEEDBACK_FORMAT],
        },
        "3": {
            "writer_guidance": [writer_guidance_s, WRITER_COMMON_RULES, NEED_CATEGORISATION_GUIDE, NEEDS_PROVISION_OUTCOMES_RULES],
            "validation_guidance": validation_common_detailed,
        },
    }

    # Base configuration for any section
    config: dict[str, Any] = {
        "output": os.path.join(OUTPUTS_DIR, f"output_s{section_str}.md"),
        "feedback": os.path.join(OUTPUTS_DIR, f"feedback_s{section_str}.md"),
    }

    # Add the specific guidance lists from the map
    config.update(path_map.get(section_str, {}))

    return config


# --------------------------------------------------------------------------
# 5. LLM AND API CONFIGURATIONS
# --------------------------------------------------------------------------
"""Centralised configuration for model backends.

Supports two modes:
1. Azure OpenAI (default) - requires all AZURE_* env vars.
2. Local Ollama (set USE_OLLAMA=true) - uses an OpenAI-compatible / litellm route.

Environment variables for Ollama mode:
  USE_OLLAMA=true
  OLLAMA_MODEL_NAME=gpt-oss:20b   # default
  OLLAMA_BASE_URL=http://localhost:11434    (or http://localhost:11434/v1 for OpenAI-style)
  OLLAMA_API_KEY=ollama           # optional dummy

Both tiers (fast + main) currently share the same local model; can be split later.
"""

# Feature toggle
USE_OLLAMA = os.getenv("USE_OLLAMA", "false").lower() == "true"
_VERSION_FILE = Path(__file__).parent / "VERSION"
try:
    __version__ = _VERSION_FILE.read_text(encoding="utf-8").strip()
except Exception:
    __version__ = "0.0.0"

def get_version() -> str:
    return __version__

if USE_OLLAMA:
    # --- Local Ollama configuration ---
    ollama_model = os.getenv("OLLAMA_MODEL_NAME", "gpt-oss:20b")
    # Allow either base root or explicit /v1; downstream libraries typically append /v1 if needed.
    ollama_base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    # dummy accepted by most clients
    ollama_api_key = os.getenv("OLLAMA_API_KEY", "ollama")

    # Main (powerful) and fast (orchestration) configs can be separated later if desired.
    config_list = [
        {
            "model": ollama_model,
            "api_key": ollama_api_key,
            "base_url": ollama_base_url,
            # Treat as OpenAI-compatible; litellm/autogen will route appropriately.
            "api_type": "openai",
        }
    ]
    config_list_fast = [
        {
            "model": ollama_model,
            "api_key": ollama_api_key,
            "base_url": ollama_base_url,
            "api_type": "openai",
        }
    ]
else:
    # --- Azure OpenAI credentials ---
    azure_api_key = os.getenv("AZURE_OPENAI_API_KEY")
    azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
    azure_model_name = os.getenv("AZURE_OPENAI_MODEL_NAME")
    azure_model_name2 = os.getenv("AZURE_OPENAI_MODEL_NAME2")
    azure_api_version = os.getenv("AZURE_OPENAI_API_VERSION")

    if not all([azure_api_key, azure_endpoint, azure_model_name, azure_model_name2, azure_api_version]):
        raise ValueError(
            "One or more critical Azure OpenAI environment variables are not set in .env (or set USE_OLLAMA=true)")

    config_list = [
        {
            "model": azure_model_name,
            "api_key": azure_api_key,
            "base_url": azure_endpoint,
            "api_type": "azure",
            "api_version": azure_api_version,
        }
    ]
    config_list_fast = [
        {
            "model": azure_model_name2,
            "api_key": azure_api_key,
            "base_url": azure_endpoint,
            "api_type": "azure",
            "api_version": azure_api_version,
        }
    ]

llm_config = {
    "config_list": config_list,
    "timeout": 300,
}

llm_config_fast = {
    "config_list": config_list_fast,
    "timeout": 300,
}
