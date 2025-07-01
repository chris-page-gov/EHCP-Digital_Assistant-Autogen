# MAD Document Templates

This directory contains pre-built templates for different document types that can be used with the MAD (Multi-Agentic Document Generator) system.

## Available Templates

### 1. EHCP (Education, Health and Care Plan)
**Location**: `examples/ehcp/`

**Use Case**: Special educational needs documentation for UK education system

**Structure**: 18 sections covering personal details, needs assessments, outcomes, and provisions

**To Use**:
```bash
cp examples/ehcp/*.yaml examples/ehcp/*.md instructions/
```

### 2. Business Report
**Location**: `examples/business-report/`

**Use Case**: Professional business analysis, market research, strategic reports

**Structure**: 10 sections including executive summary, methodology, findings, and recommendations

**To Use**:
```bash
cp examples/business-report/*.yaml examples/business-report/*.md instructions/
```

### 3. Storytelling/Novel Development
**Location**: `examples/storytelling/`

**Use Case**: Fiction writing, novel planning, screenplay development

**Structure**: 12 sections covering plot, characters, world-building, themes, and opening chapter

**To Use**:
```bash
cp examples/storytelling/*.yaml examples/storytelling/*.md instructions/
```

### 4. Technical Documentation
**Location**: `examples/technical-documentation/`

**Use Case**: API documentation, developer guides, system documentation

**Structure**: 16 sections including installation, configuration, API reference, and troubleshooting

**To Use**:
```bash
cp examples/technical-documentation/*.yaml examples/technical-documentation/*.md instructions/
```

## How Templates Work

Each template consists of four files:

1. **writer_guidance.md** - Defines the document structure and writing requirements
2. **validator_guidance.md** - Defines validation rules and quality standards
3. **writer_prompts.yaml** - Contains AI prompts for document generation
4. **validator_prompts.yaml** - Contains AI prompts for quality validation

## Using a Template

### Quick Start with Examples

Each template includes sample source documents to help you understand what MAD expects:

1. **Try an example first** (recommended):
   ```bash
   # Copy template files to instructions
   cp examples/business-report/*.yaml examples/business-report/*.md instructions/
   
   # Copy sample documents to docs folder
   cp examples/business-report/sample-docs/* docs/
   
   # Run MAD to see what it generates
   python main.py
   ```

2. **Use with your own documents**:
   ```bash
   # Copy template files to instructions  
   cp examples/business-report/*.yaml examples/business-report/*.md instructions/
   
   # Clear docs folder and add your own materials
   rm docs/*
   cp /path/to/your/documents/* docs/
   
   # Run MAD
   python main.py
   ```

### What's in Each Template

- `*.md` and `*.yaml` files → Copy to `instructions/`
- `sample-docs/` folder → Example source materials (copy to `docs/` to try)

## Creating Custom Templates

You can create your own templates by:

1. Starting with the template closest to your needs
2. Modifying the guidance files to match your document structure
3. Updating the prompts to reflect your specific requirements
4. Saving your custom template in a new folder for reuse

## Template Components Explained

### writer_guidance.md
- Lists all required document sections
- Defines file naming conventions
- Specifies content requirements for each section
- Provides formatting guidelines
- Sets quality standards

### validator_guidance.md
- Lists expected output files
- Defines validation rules for each section
- Sets severity levels (CRITICAL/MAJOR/MINOR)
- Specifies cross-section consistency checks
- Provides quality indicators

### writer_prompts.yaml
- Contains system prompts for the AI writer
- Defines generation and fix mode workflows
- Includes capability declarations
- Provides task-specific instructions

### validator_prompts.yaml
- Contains system prompts for the AI validator
- Defines validation workflow
- Includes feedback template structure
- Provides assessment criteria

## Tips for Choosing a Template

- **Business Report**: Best for analytical documents, research reports, strategic plans
- **Storytelling**: Ideal for creative writing, fiction planning, narrative development
- **Technical Documentation**: Perfect for software docs, API guides, user manuals
- **EHCP**: Specific to UK education system special needs documentation

## Customization Guidelines

When customizing templates:

1. Keep the same file structure (4 files)
2. Maintain consistent section naming between guidance and prompts
3. Ensure validation rules match writing requirements
4. Test with sample documents before full use
5. Consider saving customized templates for future reuse

## Support

For questions or issues with templates, please refer to the main README.md or create an issue in the repository.