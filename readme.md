### AutoGen Document Summarization & Validation Engine

This project demonstrates a sophisticated multi-agent system built with Microsoft's AutoGen framework. It automates the process of generating summary documents from a collection of source PDFs, followed by a rigorous, iterative validation and correction cycle.
The system is designed as two collaborating multi-agent teams: a Writer Team and a Validator Team. This "dual-loop" architecture ensures that the final output not only meets the initial requirements but is also refined based on a strict set of quality and accuracy rules until it passes validation.


## Key Features
**Multi-Agent Collaboration:** Utilizes two distinct agent teams (Writer and Validator) that communicate and pass tasks between each other.
**Sequential Document Generation:** Builds a final document section-by-section (e.g., Section 1, Section 2, etc.), ensuring each part is validated before starting the next.
**Iterative Refinement:** If a generated section fails validation, it is passed back to the Writer team with specific feedback for correction. This loop continues until the section passes or max retries are reached.
**Tool-Augmented Agents:** Agents are equipped with tools to perform real-world tasks like reading PDF and Markdown files and saving output to the filesystem.
**Multi-Model Integration:** Demonstrates how to integrate and use multiple LLM models within a single workflow. A primary model (e.g., GPT-4) handles general tasks, while a specialist model (e.g., "o3") can be queried for specific knowledge.
**Robust Error Handling:** Implements exponential backoff for API rate limiting (429 errors) and transient errors, making the system more reliable.
**Structured Logging:** Generates two types of logs for each run, timestamped to prevent overwrites:
   - full_run_[timestamp].log: A complete, verbose log of the entire agent conversation.
   - loop_trace_[timestamp].log: A high-level log tracking key milestones, timings, and final token/cost summaries.


## Project Structure
.
├── docs/               # Input: Place your source PDF documents here.
├── instructions/       # Input: Configuration files for agent guidance.
│   ├── writer_guidance_s1.md
│   └── validation_guidance_s1.md
├── logs/               # Output: Contains all generated log files.
├── outputs/            # Output: Generated documents and feedback reports.
├── .env                # Input: Your secret API keys and endpoints.
├── main.py             # Main application entry point and orchestrator.
├── writer.py           # Defines the Writer agent team.
├── validator.py        # Defines the Validator agent team.
├── utils.py            # Contains shared tool functions and utilities.
├── requirements.txt    # Lists all Python package dependencies.
└── README.md           # This file.


## Getting Started
# 1. Prerequisites
- Python 3.10+
- An Azure OpenAI account with at least two model deployments (a primary model like GPT-4 and your specialist "o3" model).
- Access to a terminal or command prompt.
- Git (for cloning the repository).
# 2. Installation
**1. Clone the repository:**
git clone <your-repository-url>
cd autogen-doc-summarizer

**2. Create a virtual environment (recommended):**
python -m venv venv
source venv/bin/activate  # On Windows, use `venv\Scripts\activate`

**3. Install the required packages:**
pip install -r requirements.txt


# 3. Configuration
**1. Set up your API Keys in .env:**
Create a file named .env in the root of the project directory. Copy the contents of .env.example (or the structure below) and fill in your actual Azure OpenAI credentials.

# Primary Model Credentials (e.g., GPT-4)
AZURE_OPENAI_API_KEY="YOUR_PRIMARY_API_KEY"
AZURE_OPENAI_ENDPOINT="https://YOUR_PRIMARY_ENDPOINT.openai.azure.com/"
AZURE_OPENAI_MODEL_NAME="YOUR_PRIMARY_DEPLOYMENT_NAME"
AZURE_OPENAI_API_VERSION="2023-07-01-preview"

# Specialist "o3" Model Credentials
O3_AZURE_OPENAI_API_KEY="YOUR_O3_API_KEY"
O3_AZURE_OPENAI_ENDPOINT="https://YOUR_O3_ENDPOINT.openai.azure.com/"
O3_AZURE_OPENAI_MODEL_NAME="YOUR_O3_DEPLOYMENT_NAME"
O3_AZURE_OPENAI_API_VERSION="2023-07-01-preview"

**2. Add Source Documents:**
Place one or more PDF files into the docs/ directory. These will be the source material for the writer agents.

**3. Review Guidance Documents:**
Inspect the writer_guidance_sX.md and validation_guidance_sX.md files in the instructions/ directory. These files control the behavior, structure, and quality criteria for the agents. Modify them to suit your specific needs.

## How to Run the Application
Once the installation and configuration are complete, you can run the entire process with a single command from the project's root directory:

python main.py 


You can monitor the progress in your terminal. As the application runs, it will create:
Sectional outputs (output_s1.md, etc.) in the outputs/ folder.
Feedback reports (feedback_s1.md, etc.) in the outputs/ folder.
Two new log files in the logs/ folder for that specific run.

At the end of the run, check the loop_trace_[timestamp].log for a summary of the total time taken and the token/cost usage.