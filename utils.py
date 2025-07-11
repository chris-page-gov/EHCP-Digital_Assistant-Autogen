import os
import re
import pypdf
import logging
from typing import List, Dict, Any


# Define base directories
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DOCS_DIR = os.path.join(BASE_DIR, "docs")
PROCESSED_DOCS_DIR = os.path.join(BASE_DIR, "processed_docs")
OUTPUTS_DIR = os.path.join(BASE_DIR, "outputs")
INSTRUCTIONS_DIR = os.path.join(BASE_DIR, "instructions")
LOGS_DIR = os.path.join(BASE_DIR, "logs")

# --- Tool Functions ---

def read_markdown_file(filepath: str) -> str:
    """
    Reads the content of a markdown file.
    Args:
        filepath (str): The path to the markdown file.
    Returns:
        str: The content of the file.
    """
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        return f"Error: File not found at {filepath}"
    except Exception as e:
        return f"Error reading file {filepath}: {e}"

def read_pdf_file(filepath: str) -> str:
    """
    Reads the text content of a single PDF file.
    Args:
        filepath (str): The path to the PDF file.
    Returns:
        str: The extracted text content of the PDF.
    """
    try:
        with open(filepath, 'rb') as f:
            reader = pypdf.PdfReader(f)
            text = ""
            for page in reader.pages:
                text += page.extract_text() or ""
        return text
    except FileNotFoundError:
        return f"Error: PDF file not found at {filepath}"
    except Exception as e:
        return f"Error reading PDF file {filepath}: {e}"

def list_files_in_directory(directory: str) -> List[str]:
    """
    Lists all files in a given directory.
    Args:
        directory (str): The path to the directory.
    Returns:
        List[str]: A list of filenames in the directory.
    """
    try:
        return [os.path.join(directory, f) for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f))]
    except FileNotFoundError:
        return []

def save_markdown_file(filepath: str, content: str) -> str:
    """
    Saves content to a markdown file.
    Args:
        filepath (str): The path to the file to be saved.
        content (str): The content to write to the file.
    Returns:
        str: A confirmation message.
    """
    try:
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        return f"Successfully saved file to {filepath}"
    except Exception as e:
        return f"Error saving file {filepath}: {e}"

def parse_feedback_and_count_issues(feedback_content: str) -> Dict[str, int]:
    """
    Parses a feedback document to find a [FEEDBACK_SUMMARY] block and extract issue counts.
    This is robust against formatting changes in the rest of the document.
    """
    counts = {"critical": 0, "major": 0, "minor": 0}
    
    try:
        # Use regex to find the content within the [FEEDBACK_SUMMARY] block
        # re.DOTALL allows '.' to match newline characters
        summary_match = re.search(r"\[FEEDBACK_SUMMARY\](.*?)\[END_FEEDBACK_SUMMARY\]", feedback_content, re.DOTALL)
        
        if not summary_match:
            print("Warning: [FEEDBACK_SUMMARY] block not found in feedback.md. Assuming 0 issues.")
            return counts

        summary_block = summary_match.group(1)
        
        # Use regex to find all "Key: Value" pairs within the block
        # This is flexible to extra whitespace or different line endings
        found_issues = re.findall(r"(\w+):\s*(\d+)", summary_block)
        
        for key, value in found_issues:
            key_lower = key.strip().lower()
            if key_lower in counts:
                counts[key_lower] = int(value.strip())
                
    except Exception as e:
        print(f"Error parsing feedback summary block: {e}. Returning default counts.")
        # Return the default counts in case of any parsing error
        return {"critical": 0, "major": 0, "minor": 0}

    return counts

# def calculate_total_cost_and_tokens(agents: List[Any]) -> Dict[str, Any]:
#     """
#     Calculates the total cost and token usage across all agents.

#     Args:
#         agents (List[Any]): A list of Autogen agent objects.

#     Returns:
#         Dict[str, Any]: A dictionary containing total tokens, prompt tokens,
#                         completion tokens, and the total cost.
#     """
#     total_cost = 0
#     total_tokens = 0
#     total_prompt_tokens = 0
#     total_completion_tokens = 0

#     # The oai_client is a class variable, so we access it from one of the agents
#     # to get the cost. It's the same client for all.
#     client = agents[0].client if agents else None

#     if not client:
#         return {
#             "total_tokens": 0,
#             "prompt_tokens": 0,
#             "completion_tokens": 0,
#             "total_cost": 0.0,
#         }

#     for agent in agents:
#         if hasattr(agent, "client") and hasattr(agent.client, "total_cost"):
#             total_cost += agent.client.total_cost

#         # Accessing the "private" _oai_messages is the most reliable way to get all message histories
#         if hasattr(agent, '_oai_messages'):
#             for a, messages in agent._oai_messages.items():
#                 for msg in messages:
#                     if isinstance(msg, dict) and 'usage' in msg and msg['usage'] is not None:
#                         usage = msg['usage']
#                         total_prompt_tokens += usage.get("prompt_tokens", 0)
#                         total_completion_tokens += usage.get("completion_tokens", 0)
#                         total_tokens += usage.get("total_tokens", 0)
    
#     return {
#         "total_tokens": total_tokens,
#         "prompt_tokens": total_prompt_tokens,
#         "completion_tokens": total_completion_tokens,
#         "total_cost": round(total_cost, 4), # Round to 4 decimal places
#     }

def _clean_text(text: str) -> str:
    """
    Performs basic text cleaning. (Helper function, prefixed with _).
    """
    if not text:
        return ""
    cleaned_text = re.sub(r'\n{3,}', '\n\n', text)
    lines = [line.strip() for line in cleaned_text.split('\n')]
    return '\n'.join(lines)

def preprocess_all_pdfs() -> bool:
    """
    Finds all PDFs in the DOCS_DIR, extracts clean text, and saves them
    to PROCESSED_DOCS_DIR. This function orchestrates the pre-processing.

    Returns:
        bool: True if successful, False if a critical error occurred.
    """
    logging.info("--- Starting PDF Pre-processing ---")
    
    try:
        if not os.path.exists(PROCESSED_DOCS_DIR):
            os.makedirs(PROCESSED_DOCS_DIR)
            logging.info(f"Created directory: '{PROCESSED_DOCS_DIR}'")

        if not os.path.exists(DOCS_DIR):
            logging.error(f"Source directory '{DOCS_DIR}' not found. Cannot pre-process PDFs.")
            return False

        pdf_files: List[str] = [f for f in os.listdir(DOCS_DIR) if f.lower().endswith('.pdf')]

        if not pdf_files:
            logging.warning(f"No PDF files found in '{DOCS_DIR}'. Pre-processing step will be skipped.")
            return True # Not an error, just nothing to do.

        logging.info(f"Found {len(pdf_files)} PDF(s) to process.")

        for pdf_file in pdf_files:
            pdf_path = os.path.join(DOCS_DIR, pdf_file)
            logging.info(f"Processing '{os.path.basename(pdf_path)}'...")
            
            reader = pypdf.PdfReader(pdf_path)
            extracted_text = ""
            for page in reader.pages:
                page_text = page.extract_text()
                if page_text:
                    extracted_text += page_text + "\n\n"

            if not extracted_text.strip():
                logging.warning(f"No text extracted from '{pdf_path}'. Skipping.")
                continue

            cleaned_content = _clean_text(extracted_text)
            
            output_filename = os.path.basename(pdf_path) + ".txt"
            output_path = os.path.join(PROCESSED_DOCS_DIR, output_filename)

            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(cleaned_content)
            logging.info(f"Successfully saved cleaned text to '{output_path}'")

        logging.info("--- PDF Pre-processing Finished ---")
        return True

    except Exception as e:
        logging.critical(f"A critical error occurred during PDF pre-processing: {e}")
        return False