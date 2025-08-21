import os
import re
import pypdf
import logging
from typing import List, Dict, Any
import config
import asyncio
import io
from azure.storage.blob import BlobServiceClient
from azure.core.exceptions import ResourceNotFoundError
from docxtpl import DocxTemplate

# ==============================================================================
# 1. AZURE BLOB STORAGE UTILITIES
# ==============================================================================
# Low-level functions for interacting with Azure Blob Storage.
# Includes a singleton client to manage the connection efficiently.

_blob_service_client = None

def _get_blob_service_client():
    global _blob_service_client
    if _blob_service_client is None:
        logging.info("Initializing singleton BlobServiceClient...")
        if not all([config.AZURE_STORAGE_ACCOUNT_URL, config.AZURE_STORAGE_ACCOUNT_KEY]):
            raise ValueError("Storage account URL or Key is not set in the environment.")
        _blob_service_client = BlobServiceClient(
            account_url=config.AZURE_STORAGE_ACCOUNT_URL, credential=config.AZURE_STORAGE_ACCOUNT_KEY
        )
        logging.info("BlobServiceClient initialized successfully.")
    return _blob_service_client

async def list_blobs_async(container_name: str) -> List[str]:
    """Asynchronously lists the names of all blobs in a container."""
    loop = asyncio.get_running_loop()
    def _list_blobs_sync():
        logging.info(f"Listing blobs in container: {container_name}")
        try:
            container_client = _get_blob_service_client().get_container_client(container_name)
            return [blob.name for blob in container_client.list_blobs()]
        except Exception as e:
            logging.error(f"Failed to list blobs in container '{container_name}'. Reason: {e}")
            return []
    return await loop.run_in_executor(None, _list_blobs_sync)

async def upload_blob_async(container_name: str, blob_name: str, data: str | bytes, overwrite: bool = True) -> None:
    """Asynchronously uploads string or byte data to a blob."""
    loop = asyncio.get_running_loop()
    def _upload_blob_sync():
        logging.info(f"Uploading to blob: {container_name}/{blob_name}")
        try:
            container_client = _get_blob_service_client().get_container_client(container_name)
            container_client.upload_blob(name=blob_name, data=data, overwrite=overwrite)
        except Exception as e:
            logging.error(f"Failed to upload blob '{blob_name}'. Reason: {e}")
            raise
    await loop.run_in_executor(None, _upload_blob_sync)

async def download_blob_as_text_async(container_name: str, blob_name: str) -> str:
    """Asynchronously downloads a blob and returns its content as a UTF-8 string."""
    loop = asyncio.get_running_loop()
    def _download_sync():
        logging.info(f"Downloading text blob: {container_name}/{blob_name}")
        try:
            container_client = _get_blob_service_client().get_container_client(container_name)
            blob_client = container_client.get_blob_client(blob_name)
            return blob_client.download_blob().readall().decode("utf-8")
        except ResourceNotFoundError: # Be specific about the most common error
            error_message = f"ERROR: Blob '{blob_name}' was not found in container '{container_name}'."
            logging.error(error_message)
            return error_message
        except Exception as e:
            error_message = f"ERROR: Failed to download blob '{blob_name}' as text. Reason: {e}"
            logging.error(error_message)
            return error_message
    return await loop.run_in_executor(None, _download_sync)

async def download_blob_as_bytes_async(container_name: str, blob_name: str) -> bytes:
    """Asynchronously downloads a blob and returns its content as raw bytes."""
    loop = asyncio.get_running_loop()
    def _download_sync():
        logging.info(f"Downloading bytes blob: {container_name}/{blob_name}")
        try:
            container_client = _get_blob_service_client().get_container_client(container_name)
            blob_client = container_client.get_blob_client(blob_name)
            return blob_client.download_blob().readall()
        except Exception as e:
            logging.error(f"Failed to download blob '{blob_name}' as bytes. Reason: {e}")
            return b""
    return await loop.run_in_executor(None, _download_sync)

async def download_all_sources_from_container_async(container_name: str) -> str:
    """
    Asynchronously lists all blobs in a container, downloads their text content,
    and returns it as a single concatenated string. This is the primary tool
    for providing source context to agents.
    """
    logging.info(f"--- Downloading all source documents from container: {container_name} ---")
    blob_names = await list_blobs_async(container_name)
    if not blob_names:
        logging.warning(f"No blobs found in container '{container_name}'.")
        return "ERROR: No source documents found in the specified container."

    full_content = ""
    for blob_name in blob_names:
        filename = os.path.basename(blob_name)
        logging.info(f"Reading source file: {blob_name}")
        full_content += f"--- START OF FILE {filename} ---\n\n"
        full_content += await download_blob_as_text_async(container_name, blob_name)
        full_content += f"\n\n--- END OF FILE {filename} ---\n\n"
    
    logging.info(f"--- Finished downloading all source documents from {container_name} ---")
    return full_content

async def clear_blob_container_async(container_name: str) -> None:
    """Asynchronously deletes all blobs within a specified Azure Blob Storage container."""
    logging.info(f"--- Starting cleanup of blob container: {container_name} ---")
    try:
        blobs_to_delete = await list_blobs_async(container_name)
        if not blobs_to_delete:
            logging.info(f"Container '{container_name}' is already empty.")
            return

        logging.info(f"Found {len(blobs_to_delete)} blobs to delete in container '{container_name}'.")
        
        # This can be slow if there are many blobs. For this project, it's fine.
        for blob_name in blobs_to_delete:
            logging.info(f"Deleting blob: {blob_name}")
            container_client = _get_blob_service_client().get_container_client(container_name)
            container_client.delete_blob(blob_name)
            
        logging.info(f"--- Cleanup of container '{container_name}' complete. ---")
    except Exception as e:
        logging.error(f"Failed to clear container '{container_name}'. Reason: {e}", exc_info=True)


# ==============================================================================
# 2. DATA PIPELINE UTILITIES
# ==============================================================================
# High-level functions that orchestrate the application's data workflow.

async def preprocess_all_pdfs_async() -> bool:
    """Asynchronously downloads, processes, and re-uploads all PDFs."""
    logging.info("--- Starting PDF Pre-processing from Blob Storage ---")
    try:
        source_container = config.SOURCE_BLOB_CONTAINER
        processed_container = config.PROCESSED_BLOB_CONTAINER
        pdf_blob_names = await list_blobs_async(source_container)
        pdf_blob_names = [name for name in pdf_blob_names if name.lower().endswith('.pdf')]

        if not pdf_blob_names:
            logging.warning(f"No PDF files found in container '{source_container}'.")
            return True

        for pdf_blob_name in pdf_blob_names:
            logging.info(f"Processing blob: {pdf_blob_name}")
            pdf_bytes = await download_blob_as_bytes_async(source_container, pdf_blob_name)
            if not pdf_bytes:
                logging.warning(f"Skipping empty blob: {pdf_blob_name}")
                continue

            reader = pypdf.PdfReader(io.BytesIO(pdf_bytes))
            extracted_text = "".join(page.extract_text() or "" for page in reader.pages)
            cleaned_content = _clean_text(extracted_text)
            
            output_blob_name = pdf_blob_name + ".txt"
            await upload_blob_async(processed_container, output_blob_name, cleaned_content)

        logging.info("--- PDF Pre-processing Finished ---")
        return True
    except Exception as e:
        logging.critical(f"A critical error occurred during PDF pre-processing: {e}", exc_info=True)
        return False

async def merge_output_files_async() -> bool:
    """Asynchronously merges sectional outputs from blob storage."""
    logging.info(f"--- Merging sectional outputs from blob storage ---")
    try:
        output_container = config.OUTPUT_BLOB_CONTAINER
        all_blobs = await list_blobs_async(output_container)
        section_blob_names = sorted([b for b in all_blobs if re.match(r'output_s\d+\.md', b)])
        
        if len(section_blob_names) != config.TOTAL_SECTIONS:
            logging.error(f"Merge failed: Expected {config.TOTAL_SECTIONS} files, found {len(section_blob_names)}.")
            return False

        content_tasks = [download_blob_as_text_async(output_container, blob_name) for blob_name in section_blob_names]
        full_content = await asyncio.gather(*content_tasks)
        merged_content = "\n\n---\n\n".join(full_content)
        
        await upload_blob_async(output_container, config.FINAL_DOCUMENT_FILENAME, merged_content)
        logging.info(f"Successfully merged all sections into blob: {config.FINAL_DOCUMENT_FILENAME}")
        return True
    except Exception as e:
        logging.error(f"An I/O error occurred during blob merging: {e}", exc_info=True)
        return False


# ==============================================================================
# 3. PARSING AND TEXT UTILITIES
# ==============================================================================
# Functions for cleaning, sanitising, and parsing text from documents.

def _clean_text(text: str) -> str:
    """
    Performs basic text cleaning. (Helper function, prefixed with _).
    """
    if not text:
        return ""
    cleaned_text = re.sub(r'\n{3,}', '\n\n', text)
    lines = [line.strip() for line in cleaned_text.split('\n')]
    return '\n'.join(lines)

def _sanitise_key(key: str) -> str:
    """
    A helper function to clean and sanitise a string to be used as a dictionary key.
    - Converts to lowercase
    - Replaces spaces and hyphens with underscores
    - Removes possessive apostrophes ('s or ’s)
    - Removes any other non-alphanumeric characters (except underscores)
    """
    sanitised = key.lower().replace(" ", "_").replace("-", "_")
    sanitised = sanitised.replace("'s", "").replace("’s", "")
    sanitised = re.sub(r'[^\w_]', '', sanitised)
    sanitised = re.sub(r'__+', '_', sanitised)
    return sanitised
        
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

def parse_markdown_to_dict(markdown_content: str) -> dict[str,any]:
    """
    Parses a markdown document assuming every **Key:** is globally unique.
    It ignores all headers and simply extracts all key-value pairs.
    """

    flat_context = {}
    
    # This regex finds a **Key:** at the start of a line, then captures all content
    # (including newlines and bullets) until it hits the next **Key:** or Heading (##) or ---
    pattern = re.compile(r'^\*\*(.*?):\*\*(.*?)(?=^\*\*|^##\s|---\n|\Z)', re.DOTALL | re.MULTILINE)
    
    for match in pattern.finditer(markdown_content):
        # The raw key is something like "Comms & Interaction Need 1"
        key_raw = match.group(1).strip()
        value = match.group(2).strip()
        
        # The sanitiser turns it into "comms_interaction_need_1"
        final_key = _sanitise_key(key_raw)
        
        flat_context[final_key] = value
            
    return flat_context


# ==============================================================================
# 4. DOCUMENT GENERATION UTILITIES
# ==============================================================================
# Functions for creating final output documents (e.g., .docx).

def generate_word_document(context: dict, template_path: str, output_path: str) -> None:
    """
    Generates a Word document by rendering a context dictionary into a docx template.
    """
    try:
        doc = DocxTemplate(template_path)
        doc.render(context)
        doc.save(output_path)
        logging.info(f"Successfully generated Word document at: {output_path}")
    except Exception as e:
        logging.error(f"Failed to generate Word document. Reason: {e}", exc_info=True)


# ==============================================================================
# 5. AUTOGEN AGENT HELPER FUNCTIONS
# ==============================================================================
# Functions required specifically by the AutoGen agent framework.

def is_terminate_message(message):
    """
    Custom function to check for termination message in groupchat.
    Safely handles messages that are not simple strings.
    """
    # Check if the message is a dictionary and has a "content" key
    if isinstance(message, dict) and "content" in message:
        content = message["content"]
        # Check if the content is not None before calling string methods
        if content is not None:
            return content.strip() == "TERMINATE"
    return False





