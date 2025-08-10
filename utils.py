import os
import re
import pypdf
import logging
from typing import List, Dict
from functools import lru_cache
import aiofiles
import asyncio
import config
import shutil
import logging

# --- Tool Functions ---

_single_file_cache: Dict[str, str] = {}
    
@lru_cache(maxsize=10)
def _cached_read_files(filepaths_tuple: tuple[str]) -> str:
    """
    Internal, cached function for reading multiple files.
    IMPORTANT: This function MUST take a tuple as input, because lists are not hashable for caching.
    """
    full_content = ""
    for filepath in filepaths_tuple:
        filename = os.path.basename(filepath)
        full_content += f"--- START OF FILE {filename} ---\n\n"
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                full_content += f.read()
        except FileNotFoundError:
            full_content += f"Error: File not found at {filepath}"
        except Exception as e:
            full_content += f"Error reading file {filepath}: {e}"
        
        full_content += f"\n\n--- END OF FILE {filename} ---\n\n"
        
    return full_content
        
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
        if not os.path.exists(config.PROCESSED_DOCS_DIR):
            os.makedirs(config.PROCESSED_DOCS_DIR)
            logging.info(f"Created directory: '{config.PROCESSED_DOCS_DIR}'")

        if not os.path.exists(config.DOCS_DIR):
            logging.error(f"Source directory '{config.DOCS_DIR}' not found. Cannot pre-process PDFs.")
            return False

        pdf_files: List[str] = [f for f in os.listdir(config.DOCS_DIR) if f.lower().endswith('.pdf')]

        if not pdf_files:
            logging.warning(f"No PDF files found in '{config.DOCS_DIR}'. Pre-processing step will be skipped.")
            return True # Not an error, just nothing to do.

        logging.info(f"Found {len(pdf_files)} PDF(s) to process.")

        for pdf_file in pdf_files:
            pdf_path = os.path.join(config.DOCS_DIR, pdf_file)
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
            output_path = os.path.join(config.PROCESSED_DOCS_DIR, output_filename)

            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(cleaned_content)
            logging.info(f"Successfully saved cleaned text to '{output_path}'")

        logging.info("--- PDF Pre-processing Finished ---")
        return True

    except Exception as e:
        logging.critical(f"A critical error occurred during PDF pre-processing: {e}")
        return False

def clear_directory(directory_path: str):
    """
    Deletes all files and subdirectories within a given directory,
    but does not delete the directory itself.
    """
    logging.info(f"--- Starting cleanup of directory: {directory_path} ---")
    if not os.path.isdir(directory_path):
        logging.warning(f"Cleanup skipped: Directory '{directory_path}' does not exist.")
        return

    # Loop through all the items in the directory
    for filename in os.listdir(directory_path):
        file_path = os.path.join(directory_path, filename)
        try:
            # If it's a file or a symbolic link, delete it
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            # If it's a subdirectory, delete it and all its contents
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as e:
            # Log an error if a specific file couldn't be deleted, but continue the process
            logging.error(f"Failed to delete {file_path}. Reason: {e}")
    
    logging.info(f"--- Cleanup of {directory_path} complete. ---")

def merge_output_files(num_sections: int, output_dir: str, final_filename: str) -> bool:
    """
    Merges sectional output files into a single final document.

    Args:
        num_sections (int): The total number of sections to merge.
        output_dir (str): The directory containing the output files.
        final_filename (str): The name of the final merged file.

    Returns:
        bool: True if merging was successful, False otherwise.
    """
    final_doc_path = os.path.join(output_dir, final_filename)
    logging.info(f"Starting merge process for {final_doc_path}")
    
    try:
        with open(final_doc_path, 'w', encoding='utf-8') as outfile:
            for i in range(1, num_sections + 1):
                section_filename = f"output_s{i}.md"
                section_filepath = os.path.join(output_dir, section_filename)
                
                if not os.path.exists(section_filepath):
                    logging.error(f"Merge failed: Section file not found at {section_filepath}")
                    return False
                
                with open(section_filepath, 'r', encoding='utf-8') as infile:
                    outfile.write(infile.read())
                    # Add a separator between sections for clarity, except for the last one
                    if i < num_sections:
                        outfile.write("\n\n---\n\n")
            
            logging.info(f"Successfully merged all sections into {final_doc_path}")
            return True
    except IOError as e:
        logging.error(f"An I/O error occurred during merging: {e}")
        return False

_async_single_file_cache: Dict[str, str] = {}

async def read_markdown_file_async(filepath: str) -> str:
    """Asynchronously reads a markdown file using a custom in-memory cache."""
    if filepath in _async_single_file_cache:
        return _async_single_file_cache[filepath]
    
    try:
        async with aiofiles.open(filepath, 'r', encoding='utf-8') as f:
            content = await f.read()
            _async_single_file_cache[filepath] = content
            return content
    except FileNotFoundError:
        return f"Error: File not found at {filepath}"
    except Exception as e:
        return f"Error reading file {filepath}: {e}"

async def save_markdown_file_async(filepath: str, content: str) -> str:
    """Asynchronously saves content to a markdown file and invalidates its cache entry."""
    try:
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        async with aiofiles.open(filepath, 'w', encoding='utf-8') as f:
            await f.write(content)
        
        if filepath in _async_single_file_cache:
            del _async_single_file_cache[filepath]
            
        return f"Successfully saved file to {filepath} and invalidated its cache entry."
    except Exception as e:
        return f"Error saving file {filepath}: {e}"    

@lru_cache(maxsize=10)
def _read_and_cache_multiple_files_sync(filepaths_tuple: tuple[str]) -> str:
    """
    Internal SYNCHRONOUS function to read and cache the combined source documents.
    This will block ONCE per run, the very first time it's called. All subsequent
    calls will be instantaneous memory reads.
    """
    full_content = ""
    for filepath in filepaths_tuple:
        filename = os.path.basename(filepath)
        full_content += f"--- START OF FILE {filename} ---\n\n"
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                full_content += f.read()
        except FileNotFoundError:
            full_content += f"Error: File not found at {filepath}"
        except Exception as e:
            full_content += f"Error reading file {filepath}: {e}"
        
        full_content += f"\n\n--- END OF FILE {filename} ---\n\n"
        
    return full_content

async def read_multiple_markdown_files_async(filepaths: list[str]) -> str:
    """
    Asynchronously reads multiple markdown files.
    This tool is now a non-blocking wrapper around a synchronous, cached function.
    """
    filepaths_tuple = tuple(sorted(filepaths))
    
    # Run the synchronous, blocking function in a separate thread pool executor
    # so that it doesn't block the main asyncio event loop.
    loop = asyncio.get_running_loop()
    content = await loop.run_in_executor(
        None,  # Use the default thread pool executor
        _read_and_cache_multiple_files_sync,
        filepaths_tuple
    )
    return content

def is_terminate_message(message):
    """
    Custom function to check for termination message.
    Safely handles messages that are not simple strings.
    """
    # Check if the message is a dictionary and has a "content" key
    if isinstance(message, dict) and "content" in message:
        content = message["content"]
        # Check if the content is not None before calling string methods
        if content is not None:
            return content.rstrip().endswith("TERMINATE")
    return False

