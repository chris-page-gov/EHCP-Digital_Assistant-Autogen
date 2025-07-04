# MAD - Multi-Agentic Document Generator

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![AutoGen](https://img.shields.io/badge/AutoGen-0.4.0+-green.svg)](https://github.com/microsoft/autogen)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**Make Awesome Documents with AI** - An intelligent document generation system that uses multiple AI agents to create structured, validated documents from your source materials.

## 🎯 What is MAD?

MAD is an automated document generation system that:
- 📚 Reads your source materials (PDFs, text files, markdown, etc.)
- 🤖 Uses AI agents to understand and extract information
- 📝 Generates structured documents following your templates
- ✅ Validates output quality and completeness
- 🔄 Automatically fixes issues through feedback loops

Perfect for creating:
- 📊 Business reports and analysis documents
- 📖 Technical documentation and API guides
- ✍️ Story development and creative writing plans
- 🎓 Educational plans and assessments (EHCP)
- 📋 Any structured document you can define!

## 🚀 Quick Start

### Prerequisites
- Python 3.11 or higher
- Azure OpenAI API access (or compatible endpoint)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/mad-document-generator.git
   cd mad-document-generator
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**
   ```bash
   cp "sample .env" .env
   # Edit .env with your Azure OpenAI credentials
   ```

4. **Choose a template**
   ```bash
   # List available templates
   ls examples/
   
   # Copy a template to the output folder (e.g., business report)
   cp examples/business-report/*.yaml examples/business-report/*.md output/instructions/
   ```

5. **Add your source documents**
   ```bash
   # Copy sample documents to try it out
   cp examples/business-report/sample-docs/* output/docs/
   
   # Or add your own documents
   cp your-documents/* output/docs/
   ```

6. **Run MAD**
   ```bash
   python main.py
   ```

That's it! MAD will generate your documents in the `output/` folder.

## 🎪 Try Examples

Want to see MAD in action? Try any of these examples:

```bash
# Business Report Example
cp examples/business-report/*.yaml examples/business-report/*.md output/instructions/
cp examples/business-report/sample-docs/* output/docs/
python main.py

# Technical Documentation Example  
cp examples/technical-documentation/*.yaml examples/technical-documentation/*.md output/instructions/
cp examples/technical-documentation/sample-docs/* output/docs/
python main.py

# Story Development Example
cp examples/storytelling/*.yaml examples/storytelling/*.md output/instructions/
cp examples/storytelling/sample-docs/* output/docs/
python main.py

# EHCP (Educational Health Care Plan) Example
cp examples/ehcp/*.yaml examples/ehcp/*.md output/instructions/
cp examples/ehcp/sample-docs/* output/docs/
python main.py
```

After seeing the example output, clear the `output/docs/` folder and add your own materials!

## 📋 Available Templates

### Business Report
Professional business analysis and reporting
- Executive summaries
- Market analysis
- Financial reporting
- Strategic recommendations

### Technical Documentation
Comprehensive technical guides
- API documentation
- Installation guides
- Troubleshooting sections
- Code examples

### Storytelling/Novel Development
Creative writing project planning
- Character profiles
- Plot structures
- World building
- Chapter outlines

### EHCP (Education, Health and Care Plan)
UK special educational needs documentation
- Needs assessments
- Outcome planning
- Provision specifications
- Support requirements

[See all templates →](examples/)

## 🏗️ How It Works

### The MAD Architecture

```
┌─────────────┐     ┌──────────────┐     ┌─────────────┐
│   Source    │────▶│  FileSurfer  │────▶│  Document   │
│ Documents   │     │    Agent     │     │   Writer    │
└─────────────┘     └──────────────┘     │    Agent    │
                                         └──────┬──────┘
                                                │
                                                ▼
┌─────────────┐     ┌──────────────┐     ┌─────────────┐
│  Validated  │◀────│   Quality    │◀────│  Feedback   │
│  Documents  │     │  Assessor    │     │    Loop     │
└─────────────┘     └──────────────┘     └─────────────┘
```

1. **FileSurfer Agent** reads your source documents (PDFs, text, etc.)
2. **DocumentWriter Agent** creates structured content following your template
3. **QualityAssessor Agent** validates against your rules
4. **Feedback Loop** automatically fixes any issues (up to 5 iterations)
5. **Final Output** is saved as markdown files (one per section)

### Key Features

- 🔄 **Automated Feedback Loop**: Iteratively improves documents until they pass validation
- 📏 **Template-Based**: Define your document structure once, use it repeatedly
- 🎯 **Validation Rules**: Ensure quality and completeness
- 🛠️ **Extensible**: Create custom templates for any document type
- 🤝 **Multi-Agent**: Specialized agents for different tasks
- 📂 **Section-Based Output**: Each section saved separately for flexible editing

## 📝 Creating Custom Templates

### Template Structure

Each template consists of 4 files in the `output/instructions/` folder:

1. **writer_guidance.md** - Document structure and requirements
2. **validator_guidance.md** - Quality rules and validation criteria  
3. **writer_prompts.yaml** - AI prompts for content generation
4. **validator_prompts.yaml** - AI prompts for quality assessment

### Creating Your Own Template

1. **Start with an existing template:**
   ```bash
   cp -r examples/business-report examples/my-template
   ```

2. **Edit the guidance files to define your document:**
   - `writer_guidance.md`: Specify sections, content requirements, formatting
   - `validator_guidance.md`: Define quality standards and validation rules

3. **Update the prompt files:**
   - Adjust AI instructions for your domain
   - Customize agent behaviors

4. **Test with sample documents:**
   ```bash
   cp examples/my-template/*.yaml examples/my-template/*.md output/instructions/
   python main.py
   ```

[Full template guide →](examples/README.md)

## 🔧 Configuration

### Environment Variables (.env)

```bash
# Azure OpenAI Configuration (REQUIRED)
AZURE_OPENAI_API_KEY=your-api-key-here
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_MODEL_NAME=your-deployment-name
AZURE_OPENAI_API_VERSION=2024-12-01-preview

# Optional Settings
MAX_ITERATIONS=5          # Maximum improvement cycles
SUBPROCESS_TIMEOUT_SECONDS=3600  # Process timeout (60 minutes)
LOG_LEVEL=INFO           # Logging detail level
```

See `sample .env` for detailed setup instructions.

### Advanced Configuration

Edit `config.py` for more options:
- File paths and patterns
- Timeout settings
- Agent parameters
- Validation thresholds
- Issue severity patterns

## 📁 Project Structure

```
mad-document-generator/
├── output/                      # Main working directory
│   ├── instructions/            # Active template files
│   │   ├── writer_prompts.yaml
│   │   ├── validator_prompts.yaml
│   │   ├── writer_guidance.md
│   │   └── validator_guidance.md
│   ├── docs/                    # Your source documents go here
│   ├── *.md                     # Generated document sections
│   ├── feedback.md              # Validation feedback
│   ├── validation_status.json   # Validation results
│   └── loop_report.json         # Iteration history
├── examples/                    # Pre-built templates
│   ├── business-report/
│   ├── technical-documentation/
│   ├── storytelling/
│   └── ehcp/
├── logs/                        # Application logs
├── main.py                      # Main application (feedback loop)
├── writer.py                    # Document generation module
├── validator.py                 # Quality validation module
├── config.py                    # Configuration settings
├── utils.py                     # Shared utilities
├── requirements.txt             # Python dependencies
└── sample .env                  # Environment template
```

### Important Notes

- The `output/` folder contains everything agents need in one place
- Place source documents in `output/docs/` 
- Templates go in `output/instructions/`
- Each document section is saved as a separate `.md` file
- Clear `output/docs/` between different projects

## 🔄 The Feedback Loop

MAD's intelligent feedback loop ensures high-quality output:

1. **Generation**: Writer creates initial document
2. **Validation**: Validator checks against rules
3. **Feedback**: Issues identified with severity levels
4. **Revision**: Writer fixes issues based on feedback
5. **Repeat**: Up to 5 iterations until validation passes

Monitor progress in `output/loop_report.json`.

## 🤝 Contributing

We welcome contributions! Here's how you can help:

### Adding New Templates
1. Create a new folder in `examples/`
2. Add the 4 required template files
3. Include sample documents
4. Submit a pull request

### Improving Core Features
- Check existing issues
- Propose enhancements
- Submit pull requests

### Reporting Issues
- Use issue templates
- Include error messages
- Provide minimal examples

## 🐛 Troubleshooting

### Common Issues

**Authentication Errors**
```bash
# Test your Azure OpenAI configuration
python -c "from utils import check_environment_variables; check_environment_variables()"
```

**Missing Dependencies**
```bash
pip install -r requirements.txt --upgrade
```

**Template Not Working**
- Ensure all 4 template files are in `output/instructions/`
- Check file names match exactly
- Verify source documents are in `output/docs/`

**Validator Creates Multiple Feedback Files**
- Fixed in latest version!
- Ensure you're using the latest `validator_prompts.yaml`
- The system now creates one comprehensive `feedback.md`

**Path Issues**
- The system now handles paths correctly
- Writer and validator work from the output directory
- All paths are relative from output/

### Debug Mode

Enable debug logging:
```bash
# In .env file
LOG_LEVEL=DEBUG
```

Check logs in the `logs/` folder for detailed information.

### Getting Help

- 📖 Check the [technical documentation](CLAUDE.md)
- 🐛 [Report issues](https://github.com/yourusername/mad-document-generator/issues)
- 💬 Join discussions
- 📧 Contact maintainers

## 🔒 Security

- API keys stored locally in `.env` (never committed)
- File operations sandboxed to project directories
- No external data transmission except to your AI provider
- Input validation on all file operations
- Regular dependency updates

## 📊 Performance

- Document generation: 2-5 minutes typical
- Validation: 1-2 minutes per iteration
- Supports documents up to 100MB total
- Handles 50+ page PDFs efficiently
- Concurrent processing for better performance

## 🗺️ Roadmap

- [ ] Web interface for non-technical users
- [ ] Support for more AI providers (OpenAI, Anthropic, etc.)
- [ ] Real-time collaboration features
- [ ] Cloud deployment options
- [ ] Plugin system for custom processors
- [ ] Direct Word/Google Docs export

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Built with [AutoGen](https://github.com/microsoft/autogen) and MagenticOne
- Powered by Azure OpenAI
- Thanks to all contributors and early users

## 🚨 Known Issues

- Validator may occasionally create individual section feedback files instead of one comprehensive report
- Some AI models may not follow the accumulation instructions perfectly
- Working on enforcing single feedback file generation

---

**Ready to generate awesome documents?** [Get started now!](#-quick-start)

*Made with ❤️ by the MAD community*