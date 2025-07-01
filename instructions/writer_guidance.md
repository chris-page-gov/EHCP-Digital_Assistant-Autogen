# Document Generation Template Guide

## Overview
This file should contain the template for your specific document type. The MAD (Multi-Agentic Document Generator) system will use this template to generate documents based on your requirements.

## How to Use This System

### Option 1: Use an Example Template
1. Browse the `examples/` folder for pre-built templates:
   - `examples/ehcp/` - Education, Health and Care Plan documents
   - `examples/business-report/` - Business reports and analysis documents
   - `examples/technical-documentation/` - Technical documentation templates

2. Copy the desired template files to the `instructions/` folder:
   - `writer_guidance.md` - Document structure and writing rules
   - `validator_guidance.md` - Validation rules for quality checking

### Option 2: Create Your Own Template
1. Replace this file with your custom document template
2. Define your document sections and requirements
3. Create corresponding validation rules in `validator_guidance.md`

## Template Structure Requirements

Your template should include:

### 1. Required Output Files and Section Names
List all document sections with their exact file names and section names.

### 2. File Management Rules
Specify how files should be named and organized.

### 3. Section Guidelines
For each section, define:
- Purpose
- Required content
- Length constraints
- Formatting requirements
- Style guidelines

### 4. Writing Style Guidelines
Define the overall tone, style, and formatting requirements.

### 5. Quality Standards
Specify what constitutes a high-quality document.

## Example Templates Available

### EHCP (Education, Health and Care Plan)
- **Use Case**: Special educational needs documentation
- **Sections**: 18 structured sections covering personal details, needs assessment, and provisions
- **Location**: `examples/ehcp/`

### Business Report
- **Use Case**: Professional business analysis and reporting
- **Sections**: Executive summary, methodology, findings, recommendations
- **Location**: `examples/business-report/`

### Technical Documentation
- **Use Case**: Software documentation, API guides, technical manuals
- **Sections**: Overview, installation, usage, API reference, troubleshooting
- **Location**: `examples/technical-documentation/`

## Quick Start

To use the EHCP template:
```bash
cp examples/ehcp/writer_guidance.md instructions/
cp examples/ehcp/validator_guidance.md instructions/
```

To use the Business Report template:
```bash
cp examples/business-report/writer_guidance.md instructions/
cp examples/business-report/validator_guidance.md instructions/
```

## Creating Your Own Template

See the examples for inspiration, but feel free to create entirely custom structures. The key is to be specific about:
- What sections you need
- What content goes in each section
- How the content should be formatted
- What quality standards apply

The system is designed to be flexible and work with any document type you can define!