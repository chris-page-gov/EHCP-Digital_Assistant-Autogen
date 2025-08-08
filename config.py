import os


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
CONCURRENT_SECTIONS = 5  # Number of sections to process in parallel
MAX_SECTION_ITERATIONS = 10  # Max loops for a single section before failure
MAX_FINAL_ITERATIONS = 10  # Max loops for the final merged document

# --------------------------------------------------------------------------
# 2. GUIDANCE FILE PARTIALS
# --------------------------------------------------------------------------
# Define the paths to your reusable instruction components.
_PARTIALS_DIR = os.path.join(INSTRUCTIONS_DIR, "partials")

# Reusable components for WRITER agents
WRITER_COMMON_RULES = os.path.join(_PARTIALS_DIR, "_writer_common_rules.md")
NEEDS_PROVISION_OUTCOMES_RULES = os.path.join(INSTRUCTIONS_DIR, "partials", "_need_provision_outcome_writer_guidance.md")
NEED_CATEGORISATION_GUIDE = os.path.join(_PARTIALS_DIR, "_need_categorisation_guide.md")

# Reusable components for VALIDATOR agents
VALIDATOR_COMMON_FEEDBACK_FORMAT = os.path.join(_PARTIALS_DIR, "_validator_common_feedback_format.md")
PROVISION_SPECIFICITY_RULES = os.path.join(_PARTIALS_DIR, "_provision_specificity_rules.md")
SMART_OUTCOMES_RULES = os.path.join(_PARTIALS_DIR, "_smart_outcomes_rules.md")
GOLDEN_THREAD_RULES = os.path.join(_PARTIALS_DIR, "_golden_thread_rules.md")

# --------------------------------------------------------------------------
# 3. FINAL DOCUMENT PATHS
# --------------------------------------------------------------------------
# Paths for the final, merged document and its related files.
FINAL_DOCUMENT_FILENAME = "final_document.md"
FINAL_DOCUMENT_PATH = os.path.join(OUTPUTS_DIR, FINAL_DOCUMENT_FILENAME)
FINAL_FEEDBACK_PATH = os.path.join(OUTPUTS_DIR, "final_feedback.md")

# Guidance for the finalization phase
FINAL_WRITER_GUIDANCE = os.path.join(INSTRUCTIONS_DIR, "writer_guidance_final.md")
FINAL_VALIDATION_GUIDANCE = [os.path.join(INSTRUCTIONS_DIR, "validation_guidance_final.md"), NEED_CATEGORISATION_GUIDE]

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
    writer_guidance_s = os.path.join(INSTRUCTIONS_DIR, f"writer_guidance_s{section_str}.md")
    validation_guidance_s = os.path.join(INSTRUCTIONS_DIR, f"validation_guidance_s{section_str}.md")

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
        "4": {
            "writer_guidance": [writer_guidance_s, WRITER_COMMON_RULES, NEED_CATEGORISATION_GUIDE, NEEDS_PROVISION_OUTCOMES_RULES],
            "validation_guidance": validation_common_detailed,
        },
        "5": {
            "writer_guidance": [writer_guidance_s, WRITER_COMMON_RULES, NEED_CATEGORISATION_GUIDE, NEEDS_PROVISION_OUTCOMES_RULES],
            "validation_guidance": validation_common_detailed,
        },
    }

    # Base configuration for any section
    config = {
        "output": os.path.join(OUTPUTS_DIR, f"output_s{section_str}.md"),
        "feedback": os.path.join(OUTPUTS_DIR, f"feedback_s{section_str}.md"),
    }
    
    # Add the specific guidance lists from the map
    config.update(path_map.get(section_str, {}))

    return config