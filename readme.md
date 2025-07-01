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
- 🎓 Educational plans and assessments
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
   cp sample.env .env
   # Edit .env with your Azure OpenAI credentials
   ```

4. **Try an example (optional)**
   ```bash
   # Copy example template files
   cp examples/business-report/*.yaml examples/business-report/*.md instructions/
   
   # Copy example source documents
   cp examples/business-report/sample-docs/* docs/
   
   # Run MAD to see it in action
   python main.py
   ```

5. **Use your own documents**
   ```bash
   # Choose a template (e.g., business report)
   cp examples/business-report/*.yaml examples/business-report/*.md instructions/
   
   # Clear the docs folder and add your own source materials
   rm docs/*
   cp your-documents/* docs/
   ```

6. **Run MAD**
   ```bash
   python main.py
   ```

That's it! MAD will generate your documents in the `output/` folder.

## 🎪 Try It Now!

Want to see MAD in action? Try any of these examples:

```bash
# Business Report Example
cp examples/business-report/*.yaml examples/business-report/*.md instructions/
cp examples/business-report/sample-docs/* docs/
python main.py

# Technical Documentation Example  
cp examples/technical-documentation/*.yaml examples/technical-documentation/*.md instructions/
cp examples/technical-documentation/sample-docs/* docs/
python main.py

# Story Development Example
cp examples/storytelling/*.yaml examples/storytelling/*.md instructions/
cp examples/storytelling/sample-docs/* docs/
python main.py
```

After seeing the example output, clear the `docs/` folder and add your own materials!

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

[See all templates →](examples/README.md)

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

1. **FileSurfer Agent** reads your source documents
2. **DocumentWriter Agent** creates structured content
3. **QualityAssessor Agent** validates against rules
4. **Feedback Loop** automatically fixes any issues
5. **Final Output** is saved as markdown files

### Key Features

- 🔄 **Automated Feedback Loop**: Iteratively improves documents until they pass validation
- 📏 **Template-Based**: Define your document structure once, use it repeatedly
- 🎯 **Validation Rules**: Ensure quality and completeness
- 🛠️ **Extensible**: Create custom templates for any document type
- 🤝 **Multi-Agent**: Specialized agents for different tasks

## 📝 Creating Custom Templates

### Template Structure

Each template consists of 4 files:

1. **writer_guidance.md** - Document structure and requirements
2. **validator_guidance.md** - Quality rules and validation criteria  
3. **writer_prompts.yaml** - AI prompts for content generation
4. **validator_prompts.yaml** - AI prompts for quality assessment

### Creating Your Own Template

1. Start with an existing template:
   ```bash
   cp -r examples/business-report examples/my-template
   ```

2. Edit the guidance files to define your document:
   - Specify required sections
   - Set content requirements
   - Define quality standards

3. Update the prompt files:
   - Adjust AI instructions
   - Customize for your domain

4. Test with sample documents:
   ```bash
   cp examples/my-template/* instructions/
   python main.py
   ```

[Full template guide →](examples/README.md)

## 🔧 Configuration

### Environment Variables (.env)

```bash
# Azure OpenAI Configuration
AZURE_OPENAI_API_KEY=your-api-key
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_DEPLOYMENT=your-deployment-name
AZURE_OPENAI_API_VERSION=2024-06-01

# Optional: Custom settings
MAX_ITERATIONS=5  # Maximum improvement cycles
TIMEOUT_SECONDS=900  # Process timeout
```

### Advanced Configuration

Edit `config.py` for more options:
- File paths and patterns
- Timeout settings
- Agent parameters
- Validation thresholds

## 📁 Project Structure

```
mad-document-generator/
├── docs/                    # Your source documents go here
├── output/                  # Generated documents appear here
├── instructions/            # Active template files
├── examples/               # Pre-built templates with sample docs
│   ├── business-report/
│   │   ├── sample-docs/    # Example source materials
│   │   └── *.md/*.yaml     # Template files
│   ├── technical-documentation/
│   ├── storytelling/
│   └── ehcp/
├── main.py                 # Main application entry
├── writer.py               # Document generation module
├── validator.py            # Quality validation module
├── config.py               # Configuration settings
├── utils.py                # Shared utilities
└── requirements.txt        # Python dependencies
```

### Important Notes About the docs/ Folder

- The `docs/` folder is your **working directory** for source materials
- Before running MAD, place your source documents (PDFs, text files, etc.) here
- Each template includes `sample-docs/` you can copy to `docs/` to try it out
- **Clear the docs/ folder** between different projects to avoid mixing documents

## 🤝 Contributing

We welcome contributions! Here's how you can help:

### Adding New Templates
1. Create a new folder in `examples/`
2. Add the 4 required template files
3. Include sample documents if possible
4. Submit a pull request

### Improving Core Features
- Check existing issues
- Propose enhancements
- Submit pull requests

### Reporting Issues
- Use issue templates
- Include error messages
- Provide minimal examples

[Contributing Guide →](CONTRIBUTING.md)

## 🐛 Troubleshooting

### Common Issues

**Authentication Errors**
```bash
# Check your .env file has correct Azure credentials
python -c "from utils import check_environment_variables; check_environment_variables()"
```

**Missing Dependencies**
```bash
pip install -r requirements.txt --upgrade
```

**Template Not Working**
- Ensure all 4 template files are copied to `instructions/`
- Check file names match exactly
- Verify source documents are in `docs/`

### Getting Help

- 📖 Check the [documentation](CLAUDE.md)
- 🐛 [Report issues](https://github.com/yourusername/mad-document-generator/issues)
- 💬 Join discussions
- 📧 Contact maintainers

## 🔒 Security

- API keys are stored locally in `.env` (never committed)
- File operations are sandboxed to project directories
- No external data transmission except to your AI provider
- Regular security updates for dependencies

## 📊 Performance

- Typical document generation: 2-5 minutes
- Validation and fixes: 1-2 minutes per iteration
- Supports documents up to 100MB
- Handles 50+ page PDFs efficiently

## 🗺️ Roadmap

- [ ] Web interface for non-technical users
- [ ] Support for more AI providers
- [ ] Real-time collaboration features
- [ ] Cloud deployment options
- [ ] Plugin system for custom processors

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Built with [AutoGen](https://github.com/microsoft/autogen) and MagenticOne
- Inspired by the need for better document automation
- Thanks to all contributors and early users

---

**Ready to generate awesome documents?** [Get started now!](#-quick-start)

*Made with ❤️ by the MAD community*