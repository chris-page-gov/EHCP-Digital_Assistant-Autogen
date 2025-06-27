# MAD - Multi-Agentic Document Generator
*Make Awesome Documents with AI*

An automated system for generating structured documents from source materials using AI agents. The system reads your source files and creates documents following the template you specify in guidance.yaml.

## Overview

This system uses Microsoft's AutoGen framework with MagenticOne orchestration to automate document creation and validation. It's completely generic - you can use it to generate any type of document by providing appropriate guidance files.

### Document Generation (writer.py)
Two specialized AI agents work together:
- **FileSurfer**: Reads source documents and extracts relevant information (read-only)
- **DocumentWriter**: Creates structured documents following your template (can save and delete files)

### Document Validation (validator.py)
Two specialized AI agents assess quality:
- **FileSurfer**: Reads validation rules and generated documents (read-only)
- **QualityAssessor**: Analyzes compliance and generates feedback (can save feedback and delete files)

### Automated Feedback Loop (main.py)
An intelligent orchestrator that:
- **Runs writer and validator in sequence**
- **Automatically fixes issues** based on validation feedback
- **Iterates until validation passes** (max 5 iterations)
- **Tracks progress** and generates detailed reports

## How It Works

The system is driven by configuration files in the `instructions/` directory:
- **guidance.yaml**: Defines what document to create (structure, sections, requirements)
- **validation_guidance.yaml**: Defines how to validate the document (rules, criteria, quality standards)
- **writer_prompts.yaml**: Prompts for document generation with agent capabilities
- **validator_prompts.yaml**: Prompts for validation with agent capabilities

Simply replace these files with your own templates to generate different document types!

## Features

### Document Generation
- **Template-Driven**: Follows the structure defined in guidance.yaml
- **Section-Based Output**: Each section saved as a separate file for flexible updates
- **Multiple Source Formats**: Processes PDFs, text files, and other documents
- **Professional Formatting**: Generates clean, formatted markdown documents
- **Intelligent Processing**: AI agents understand context and requirements
- **Clear Agent Capabilities**: Explicit declarations prevent tool confusion

### Quality Validation
- **Automated Compliance Checking**: Validates against rules in validation_guidance.yaml
- **Multi-Level Issue Detection**: Customizable severity levels
- **Detailed Feedback Report**: Generates actionable feedback with specific recommendations
- **Compliance Scoring**: Provides quantitative assessment of document quality
- **Rule-Based Validation**: All rules defined in YAML, not hardcoded
- **File Structure Validation**: Checks for missing, unexpected, or misnamed files

## Prerequisites

- Python 3.9 or higher
- Azure OpenAI account with deployed model
- Source documents for processing

## Installation

1. **Clone or download this repository**

2. **Create a Python virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure Azure OpenAI:**
   - Copy `sample .env` to `.env`
   - Fill in your Azure OpenAI credentials:
     - `AZURE_OPENAI_API_KEY`
     - `AZURE_OPENAI_ENDPOINT`
     - `AZURE_OPENAI_MODEL_NAME`
     - `AZURE_OPENAI_API_VERSION` (default: 2024-12-01-preview)

5. **Set up your document type:**
   - Replace `guidance.md` with your document template
   - Replace `validationguidance.md` with your validation rules
   - Place source documents in the `docs/` folder

## Usage

### Option 1: Automated Feedback Loop (Recommended)

Run the main feedback loop runner:

```bash
python main.py
# On Windows with venv: .venv\Scripts\python.exe main.py
```

This will automatically:
1. Generate documents from source materials
2. Validate the output against your requirements
3. Fix any issues identified by the validator
4. Repeat until validation passes (maximum 5 iterations)
5. Generate a comprehensive report in `output/loop_report.json`

### Option 2: Run Components Separately

#### Generating Documents

```bash
python writer.py
# On Windows with venv: .venv\Scripts\python.exe writer.py
```

The writer will:
1. Read instructions/guidance.yaml to understand document structure
2. Process all source documents in the docs folder
3. Generate document sections as specified
4. Save each section as a separate file in the `output/` folder

#### Validating Documents

```bash
python validator.py
# On Windows with venv: .venv\Scripts\python.exe validator.py
```

The validator will:
1. Read validation rules from `instructions/validation_guidance.yaml`
2. Analyze all document sections in the `output/` folder
3. Check compliance with your requirements
4. Generate a detailed `feedback.md` report in the `output/` folder

## Output Structure

### Generated Documents

Each document section is saved as a separate file in the `output/` folder. Filenames are automatically generated from section names, with spaces and special characters converted to underscores.

Example output structure:
- `introduction.md`
- `chapter_1_overview.md`
- `chapter_2_methodology.md`
- etc.

### Validation Report

After running the validator:
- `feedback.md` - Comprehensive validation report including:
  - Executive summary with overall compliance status
  - Section-by-section analysis
  - Issue severity levels (as defined in your validation rules)
  - Compliance scores
  - Specific recommendations for improvement

### Feedback Loop Output

When using the automated feedback loop (main.py):
- `loop_report.json` - Detailed iteration history including:
  - Total iterations and duration
  - Issue counts per iteration
  - Final validation status
  - Complete iteration history with timestamps

## Customizing for Different Document Types

### Example: Technical Documentation
1. Create `instructions/guidance.yaml` with sections like:
   - Overview
   - Architecture
   - API Reference
   - Examples
   - Troubleshooting

2. Create `instructions/validation_guidance.yaml` with rules like:
   - All code examples must be tested
   - API endpoints must include request/response examples
   - Architecture diagrams required

### Example: Research Papers
1. Create `instructions/guidance.yaml` with sections like:
   - Abstract (max 250 words)
   - Introduction
   - Literature Review
   - Methodology
   - Results
   - Discussion
   - Conclusion

2. Create `instructions/validation_guidance.yaml` with rules like:
   - Abstract word limit enforcement
   - Citation format checking
   - Statistical significance requirements

### Example: Business Reports
1. Create `instructions/guidance.yaml` with sections like:
   - Executive Summary
   - Market Analysis
   - Financial Projections
   - Risk Assessment
   - Recommendations

2. Create `instructions/validation_guidance.yaml` with rules like:
   - Financial data accuracy
   - Risk mitigation strategies required
   - Executive summary page limit

## Important Notes

- The system processes documents based entirely on your guidance files
- Each section is saved independently, allowing individual updates
- All requirements and rules are defined in YAML files, not in code
- The AI agents adapt to any document type based on your templates

## Troubleshooting

- **Missing environment variables**: Ensure all Azure OpenAI credentials are set in `.env`
- **No documents found**: Check that source documents are in the `docs/` folder
- **Template missing**: Ensure guidance and validation files are in the `instructions/` directory
- **API errors**: Verify your Azure OpenAI endpoint and API key are correct

## Recent Updates

### Version 2.0 Improvements
- **Configuration Management**: All settings now centralized in `config.py`
- **Security Enhancements**: Added subprocess validation and dependency scanning
- **Prompt Externalization**: All AI prompts now in YAML files for easy customization
- **Performance Optimization**: Agents now only read sections that need validation/fixes
- **Bug Fixes**: Resolved section duplication and improved error handling
- **Dependency Updates**: Support for latest AI models including o4-mini

### Version 2.1 Improvements (Latest)
- **Agent Capability Management**: Added explicit declarations to prevent tool confusion
- **Restructured Configuration**: All prompts and instructions moved to `instructions/` directory
- **YAML Format**: Converted all configuration files from markdown to structured YAML
- **Clear Tool Distribution**: FileSurfer is read-only, DocumentWriter and QualityAssessor can save/delete
- **Enhanced Error Prevention**: Orchestrator now knows exactly which agent has which tools

### Key Files Added/Updated
- `config.py` - Central configuration management
- `utils.py` - Shared utilities with updated prompt loading
- `instructions/writer_prompts.yaml` - Writer prompts with agent capabilities
- `instructions/validator_prompts.yaml` - Validator prompts with agent capabilities
- `instructions/guidance.yaml` - Document structure definition (converted from .md)
- `instructions/validation_guidance.yaml` - Validation rules (converted from .md)
- `requirements-dev.txt` - Development dependencies including security tools

### File Management Features (Latest Update)
- **Explicit File Naming**: Added comprehensive file naming instructions in guidance.md
- **File Structure Validation**: Validator now checks for unexpected/missing files
- **File Deletion Capability**: Both writer and validator can delete incorrect files
- **Automatic Cleanup**: Writer can remove duplicate or incorrectly named files
- **Protected System Files**: feedback.md and loop_report.json cannot be deleted
- **Clear Section Mapping**: Exact section names mapped to expected filenames

## Support

For detailed implementation information and technical documentation, refer to the CLAUDE.md file.