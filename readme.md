# AutoGen EHCP Document Automation Pipeline

Version: 0.2.0  
Test Coverage: ~95% (pytest --cov)

This project is a sophisticated multi-agent system designed to automate the generation of complex, multi-section Education, Health, and Care Plan (EHCP) documents. It leverages the Microsoft AutoGen framework to orchestrate teams of AI agents that perform specialized roles, moving from raw source documents to a fully validated and merged final output in a robust, parallel, and fault-tolerant manner.

## Key Features (v0.2.0)

-   **Multi-Agent System:** Utilises distinct agent teams for writing and validation, each with specialised roles (`Planner`, `Document_Writer`, `Quality_Assessor`, `Fact_Checker`).
-   **Parallel Processing:** Employs Python's `asyncio` and a semaphore to concurrently generate and validate multiple document sections, significantly reducing total runtime.
-   **Iterative Validation Loop:** Each document section is put through a rigorous write-validate-refine loop, ensuring high quality before the final merge. A mandatory second loop is enforced for robustness.
-   **Word Document Export:** Automatically parses the final structured Markdown output and populates a custom `.docx` template, producing a professionally formatted, ready-to-use final document.
-   **Configuration-Driven:** A central `config.py` file manages all application settings, file paths, and LLM configurations, making the system easy to manage and reconfigure.
-   **Modular Agent Guidance:** Agent instructions and validation rules are externalised into a version-controllable `instructions/` directory with reusable "partials" to ensure consistency and maintain the DRY (Don't Repeat Yourself) principle.
-   **Comprehensive Logging:** The system generates detailed run logs and a high-level process trace for debugging and monitoring.
-   **Automated File Management:** Includes a pre-processing step to convert source PDFs to clean text and a guaranteed cleanup process to ensure a clean state for every run.
-   **Tiered LLM Strategy:** Uses two different LLM tiers—a powerful model for content generation and a faster model for orchestration and planning.

## Architectural Overview

The application follows a robust, multi-stage pipeline designed to maximise quality and efficiency.

**Stage 1: Pre-processing**
-   The script begins by scanning the `/docs` directory for all PDF source documents.
-   Each PDF is read, its text is extracted, cleaned, and then saved as a `.txt` file in the `/processed_docs` directory. This ensures that the AI agents work with a clean, consistent data source.

**Stage 2: Concurrent Sectional Generation**
-   The system initiates a writer and validator team for each of the 3 document sections.
-   Using `asyncio`, these teams work in parallel, up to the concurrency limit set in `config.py`.

**Stage 3: The Write-Validate-Refine Loop**
-   For each section, the process is as follows:
    1.  **Writer Team:** A `Planner` agent orchestrates the `Document_Writer` to draft the section's content (`output_sX.md`) based on the source documents and modular guidance files.
    2.  **Validator Team:** A `Quality_Assessor` and `Fact_Checker` agent team reviews the draft against a strict set of rules, producing a feedback report (`feedback_sX.md`).
    3.  **Assessment & Loop:** The main script parses the feedback.
        -   If critical issues are found, a specialist `Prompt_Writer` agent reframes the feedback into constructive, neutral instructions. The process loops back to the Writer Team for revision.
        -   If no critical issues are found, the section is considered "passed." The process includes a mandatory second loop to ensure robustness.
-   This loop continues until the section passes validation or `MAX_SECTION_ITERATIONS` is reached.

**Stage 4: Final Merge**
-   Once all 3 sections have been successfully validated, the `merge_output_files` utility is called.
-   It concatenates `output_s1.md`, `output_s2.md`, and `output_s3.md` into a single, complete intermediate document: `final_document.md`.

**Stage 5: Word Document Generation**
-   A robust Python parser reads the structured `final_document.md`.
-   The parsed data is converted into a flat key-value dictionary.
-   The `docxtpl` library is used to render this dictionary into a pre-defined Microsoft Word template (`template.docx`).
-   The final, professionally formatted output is saved as `final_output_document.docx`.

**Stage 6: Cleanup**
-   Finally, the `clear_directory` function is called to empty the `/processed_docs` directory, ensuring the next run starts from a clean state. This step is guaranteed to run, even if the process fails or is interrupted.

## Agent Team Structure

#### 1. The Writer Team (`create_writer_team`)
-   **Purpose:** To draft and revise a specific document section from source files.
-   **Agents:**
    -   `Planner`: The orchestrator. Follows a strict plan to read guidance, read sources, delegate drafting, and order the saving of the file. It is the only agent in this team authorised to issue the `TERMINATE` signal.
    -   `Document_Writer`: The content specialist. Its sole job is to synthesise information and write the document text. It does not engage in conversation.
    -   `Writer_User_Proxy`: The tool user. Executes file I/O operations (`read`, `save`, `list`) on behalf of the Planner.

#### 2. The Validator Team (`create_validator_team`)
-   **Purpose:** To validate a single section draft for factual accuracy, structural integrity, and rule compliance.
-   **Agents:**
    -   `Quality_Assessor`: The lead validator. It performs structural checks and consolidates all findings into the final feedback report. It is the only agent in this team authorised to issue the `TERMINATE` signal.
    -   `Fact_Checker`: The accuracy specialist. Its sole job is to compare the draft against the source documents and report any factual discrepancies.
    -   `Validator_User_Proxy`: The tool user for this team.

## Project Structure

## Project Structure

```text
.
├── 📂 docs/                # Input source PDF documents go here.
├── 📂 instructions/         # Guidance prompts for all agents.
│   ├── 📂 partials/         # Reusable markdown components for guidance files.
│   ├── writer_guidance_s1.md
│   └── ...
├── 📂 logs/                 # All output logs are saved here.
├── 📂 outputs/              # Generated documents and feedback files.
├── 📂 processed_docs/       # Cleaned text versions of source PDFs.
├── 📄 config.py             # Central configuration for all paths, settings, and LLMs.
├── 📄 main.py               # Main application entry point and high-level orchestration.
├── 📄 orchestrator.py        # Contains the core logic for processing and correcting sections.
├── 📄 tasks.py               # Generates the initial prompts for all agent teams.
├── 📄 utils.py               # Helper functions, parsers, and tool functions.
├── 📄 writer.py              # Defines the agent teams responsible for writing.
├── 📄 validator.py           # Defines the agent teams responsible for validation.
├── 📄 specialist_agents.py   # Defines standalone specialist agents like the Prompt_Writer.
├── 📄 .env                   # Environment variables for API keys and endpoints.
├── 📄 requirements.txt       # Python package dependencies.
├── 📄 template.docx          # The Word template for the final output document.

```

## Setup and Installation

1.  **Clone the repository:**
    ```bash
    git clone <your-repo-url>
    cd <your-repo-directory>
    ```

2.  **Create and activate a virtual environment:**
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
    ```

3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Configure environment variables:**
    -   Create a file named `.env` in the root of the project.
    -   Add your Azure OpenAI credentials to this file. Use the template below:

    ```env
    AZURE_OPENAI_API_KEY="your_api_key"
    AZURE_OPENAI_ENDPOINT="https://your_endpoint.openai.azure.com/"
    AZURE_OPENAI_API_VERSION="2024-02-15-preview"

    # Deployment name for your powerful reasoning model 
    AZURE_OPENAI_MODEL_NAME=""

    # Deployment name for your fast orchestration model 
    AZURE_OPENAI_MODEL_NAME2=""
    ```

5.  **Create the Word Template:**
    -   Create a Microsoft Word document named `template.docx` in the project's root directory.
    -   Design this document with your desired final formatting.
    -   Fill it with Jinja2-style placeholders (e.g., `{{ name }}`, `{{ history_summary }}`) where data should be inserted.

### (Optional) Local Mode with Ollama

You can run the pipeline without Azure by using a locally hosted model via [Ollama](https://ollama.com/). A switch in `config.py` enables this (`USE_OLLAMA`).

1. Install Ollama (Linux/macOS):
    ```bash
    curl -fsSL https://ollama.com/install.sh | sh
    ```
2. Pull the desired model (default assumed in config: `gpt-oss:20b`):
    ```bash
    ollama pull gpt-oss:20b
    ```
3. Add (or modify) these entries in your `.env` (keep Azure vars if you also use cloud mode):
    ```env
    USE_OLLAMA=true
    OLLAMA_MODEL_NAME=gpt-oss:20b
    OLLAMA_BASE_URL=http://localhost:11434
    OLLAMA_API_KEY=ollama
    ```
4. Run the app as normal: `python main.py`.

To switch back to Azure set `USE_OLLAMA=false` (or remove it) and ensure Azure variables are populated.

## How to Run

1.  Place all your source PDF documents into the `/docs` directory.
2.  Ensure your guidance files in `/instructions` and your `template.docx` are configured as needed.
3.  Run the main script from the root directory:
    ```bash
    python main.py
    ```

## Outputs and Logging

After a successful run, you will find:
-   **The Final Document:** `/outputs/draft_EHCP.docx`
-   **Intermediate Markdown:** The merged `/outputs/final_document.md`.
-   **Sectional Drafts:** `/outputs/output_sX.md` and their corresponding `/outputs/feedback_sX.md` files.
-   **Full Console Log:** `/logs/full_run_YYYY-MM-DD_HH-MM-SS.log`
-   **High-Level Trace Log:** `/logs/loop_trace_YYYY-MM-DD_HH-MM-SS.log`
