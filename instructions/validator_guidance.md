# Document Validation Template Guide

## Overview
This file should contain the validation rules for your specific document type. The MAD (Multi-Agentic Document Generator) system will use these rules to assess document quality and provide feedback.

## How to Use This System

### Option 1: Use an Example Template
1. Browse the `examples/` folder for pre-built validation templates that match your document type
2. Copy the `validator_guidance.md` from your chosen example to the `instructions/` folder

### Option 2: Create Your Own Validation Rules
1. Replace this file with your custom validation rules
2. Define what makes a valid, high-quality document for your use case
3. Specify severity levels for different types of issues

## Validation Template Structure

Your validation rules should include:

### 1. File Structure Validation
- List of expected files
- File naming conventions
- Required vs. optional files
- System files to ignore

### 2. Content Validation Rules
For each document section, define:
- Required elements
- Minimum/maximum length requirements
- Format requirements
- Prohibited content
- Quality indicators

### 3. Severity Levels
Define what constitutes:
- **CRITICAL**: Issues that must be fixed
- **MAJOR**: Important issues that should be addressed
- **MINOR**: Suggestions for improvement

### 4. Cross-Section Validation
- Consistency checks between sections
- Dependencies between sections
- Overall document coherence

### 5. Style and Formatting Rules
- Language requirements
- Formatting standards
- Citation requirements
- Professional standards

## Example Validation Templates

### EHCP Validation
- Comprehensive rules for Education, Health and Care Plans
- Strict file structure requirements
- Section-specific content validation
- Legal compliance checks

### Business Report Validation
- Professional document standards
- Data accuracy requirements
- Executive summary alignment
- Recommendation feasibility

### Technical Documentation Validation
- Code example validation
- API consistency checks
- Version compatibility
- Completeness of examples

## Creating Custom Validation Rules

When creating your own validation rules, consider:

1. **Completeness**: Are all required sections present?
2. **Accuracy**: Is the information correct and verifiable?
3. **Consistency**: Do all sections align with each other?
4. **Clarity**: Is the content clear and understandable?
5. **Compliance**: Does it meet any regulatory requirements?
6. **Professionalism**: Does it meet quality standards?

## Best Practices

1. Be specific about what constitutes an error vs. a suggestion
2. Provide clear criteria for each validation rule
3. Include examples of both good and bad practices
4. Consider the document's intended audience
5. Balance thoroughness with practicality

## Integration with Writer Guidance

Your validation rules should align with your writer guidance:
- Every requirement in writer_guidance.md should have a corresponding validation rule
- Validation should check that guidelines were followed
- Severity levels should reflect the importance stated in guidance

Remember: Good validation rules help ensure consistent, high-quality document generation!