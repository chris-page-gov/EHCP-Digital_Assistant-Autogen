# MAD Templates Gallery

This directory contains pre-built templates for different document types. Each template includes everything you need to get started with MAD (Multi-Agentic Document Generator).

## 📁 Template Structure

Each template folder contains:
- `writer_guidance.md` - Document structure and content requirements
- `validator_guidance.md` - Quality rules and validation criteria
- `writer_prompts.yaml` - AI prompts for document generation
- `validator_prompts.yaml` - AI prompts for quality assessment
- `sample-docs/` - Example source documents to try

## 🎯 Available Templates

### Business Report
**Location**: `examples/business-report/`

Professional business analysis and reporting template
- **Use cases**: Quarterly reports, market analysis, strategic planning, research reports
- **Sections**: Executive summary, market analysis, financial overview, recommendations (10 sections)
- **Sample docs**: Company data, market research, financial statements

### Technical Documentation
**Location**: `examples/technical-documentation/`

Comprehensive technical documentation template
- **Use cases**: API docs, user guides, system documentation, developer manuals
- **Sections**: Overview, installation, usage, API reference, troubleshooting (16 sections)
- **Sample docs**: Code files, API specs, architecture diagrams

### Storytelling/Novel Development
**Location**: `examples/storytelling/`

Creative writing project planning template
- **Use cases**: Novel planning, screenplay development, story bibles, narrative design
- **Sections**: Premise, characters, plot structure, world building, chapter outlines (12 sections)
- **Sample docs**: Story concepts, character sketches, plot notes

### EHCP (Education, Health and Care Plan)
**Location**: `examples/ehcp/`

UK special educational needs documentation template
- **Use cases**: EHCP documents, SEN assessments, support planning
- **Sections**: Child details, needs assessment, outcomes, provision (18 sections)
- **Sample docs**: Assessment reports, professional opinions, parental views

## 🚀 Using a Template

### Quick Start with Sample Documents

1. **Choose your template:**
   ```bash
   ls examples/
   ```

2. **Copy template files to output folder:**
   ```bash
   cp examples/business-report/*.yaml examples/business-report/*.md output/instructions/
   ```

3. **Try with sample documents:**
   ```bash
   cp examples/business-report/sample-docs/* output/docs/
   python main.py
   ```

4. **Use your own documents:**
   ```bash
   rm output/docs/*
   cp your-documents/* output/docs/
   python main.py
   ```

### Complete Example

```bash
# Business Report with sample data
cp examples/business-report/*.yaml examples/business-report/*.md output/instructions/
cp examples/business-report/sample-docs/* output/docs/
python main.py

# Check the output
ls output/*.md
```

## 🛠️ Creating Custom Templates

### Starting from Scratch

1. **Create a new folder:**
   ```bash
   mkdir examples/my-template
   ```

2. **Create the 4 required files:**
   ```bash
   cd examples/my-template
   touch writer_guidance.md validator_guidance.md 
   touch writer_prompts.yaml validator_prompts.yaml
   ```

3. **Define your document structure in `writer_guidance.md`:**
   - List all sections with clear names
   - Specify requirements for each section
   - Include formatting guidelines
   - Add examples where helpful

4. **Set validation rules in `validator_guidance.md`:**
   - Define what makes each section valid
   - Set severity levels (CRITICAL/MAJOR/MINOR)
   - Include cross-section consistency checks
   - Specify file naming requirements

5. **Configure AI behavior in the YAML files:**
   - Adapt prompts to your domain
   - Include anti-hallucination instructions
   - Specify output formatting

6. **Add sample documents:**
   ```bash
   mkdir sample-docs
   cp example-files/* sample-docs/
   ```

### Modifying Existing Templates

1. **Copy a similar template:**
   ```bash
   cp -r examples/business-report examples/my-custom-report
   ```

2. **Edit the guidance files:**
   - Modify sections in `writer_guidance.md`
   - Adjust validation rules in `validator_guidance.md`
   - Keep consistency between the two files

3. **Update prompts for your domain:**
   - Change terminology in prompts
   - Adjust tone and style requirements
   - Add domain-specific instructions

4. **Test thoroughly:**
   ```bash
   cp examples/my-custom-report/*.yaml examples/my-custom-report/*.md output/instructions/
   python main.py
   ```

## 📝 Template Best Practices

### Writer Guidance (`writer_guidance.md`)
- ✅ **Be specific**: Clear section names and requirements
- ✅ **Set limits**: Word counts, format requirements
- ✅ **Provide examples**: Show what good output looks like
- ✅ **Define structure**: Hierarchical organization of content
- ✅ **Include file naming**: Specify exact output filenames

### Validator Guidance (`validator_guidance.md`)
- ✅ **Severity levels**: Use CRITICAL, MAJOR, MINOR appropriately
- ✅ **Clear criteria**: Specific, measurable validation rules
- ✅ **Actionable feedback**: Tell users how to fix issues
- ✅ **Complete coverage**: Check all important aspects
- ✅ **File structure validation**: List all expected files

### Prompts (YAML files)
- ✅ **Domain language**: Use terminology specific to your field
- ✅ **Clear instructions**: Unambiguous directions for AI agents
- ✅ **Anti-hallucination**: Emphasize using only source material
- ✅ **Output format**: Specify exactly how results should look
- ✅ **Single feedback file**: Ensure validator creates one comprehensive report

## 🤝 Contributing Templates

We welcome new templates! To contribute:

1. **Create your template** following the structure above
2. **Include comprehensive sample documents**
3. **Test thoroughly** with different inputs
4. **Submit a pull request** with:
   - Template description in this README
   - Clear use cases
   - Any special requirements
   - Sample output examples

### Contribution Checklist
- [ ] All 4 required files present
- [ ] Sample documents included
- [ ] Tested with MAD system
- [ ] Clear documentation
- [ ] No sensitive data in samples
- [ ] Follows naming conventions

## 📚 Template Component Reference

### writer_guidance.md
**Purpose**: Define document structure and requirements

**Must Include**:
- Document overview and purpose
- Complete list of sections
- Requirements for each section
- File naming specifications
- Anti-hallucination rules
- Quality standards

### validator_guidance.md
**Purpose**: Define validation rules and quality standards

**Must Include**:
- Expected files list
- Validation criteria per section
- Issue severity definitions
- Cross-section consistency rules
- Overall quality indicators

### writer_prompts.yaml
**Purpose**: Configure AI writer behavior

**Must Include**:
- `agent_capabilities_context`
- `document_writer_system_prompt`
- `generation_task_template`
- `fix_task_template`

### validator_prompts.yaml
**Purpose**: Configure AI validator behavior

**Must Include**:
- `agent_capabilities_context`
- `quality_assessor_system_prompt`
- `feedback_task_template`
- `feedback_template`

**Important**: Must emphasize creating ONE comprehensive feedback.md file

## 🔍 Template Validation

Before using a template in production:

1. **Test with samples**: Run with provided sample documents
2. **Check all sections**: Verify every section generates
3. **Validate output**: Ensure validation catches real issues
4. **Test edge cases**: Try minimal and maximal inputs
5. **Check file names**: Verify all files named correctly

## ❓ FAQ

**Q: Can I use multiple templates in one project?**
A: No, use one template at a time. Clear output folder between different templates.

**Q: How do I update an existing template?**
A: Edit the files directly, then test with sample documents before using in production.

**Q: What if my document doesn't fit any template?**
A: Start with the closest match and customize, or create a new template from scratch.

**Q: Can templates handle multiple languages?**
A: Yes, but you may need to adjust prompts for better language-specific output.

---

**Need help?** Check the main [README](../readme.md) or [technical documentation](../CLAUDE.md).