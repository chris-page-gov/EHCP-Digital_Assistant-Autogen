# Sample Technical Documentation Source Materials

This folder contains example source materials that demonstrate what developers might provide to MAD for generating comprehensive technical documentation.

## Included Documents

1. **api-spec.yaml.txt** - OpenAPI specification defining all endpoints
2. **architecture-notes.md** - System architecture and design decisions
3. **cli-commands.txt** - Command-line interface reference
4. **code-examples.md** - SDK usage examples in multiple languages

## Usage

1. Copy these sample documents to your `docs/` folder:
   ```bash
   cp examples/technical-documentation/sample-docs/* docs/
   ```

2. Copy the technical documentation templates to instructions:
   ```bash
   cp examples/technical-documentation/*.yaml examples/technical-documentation/*.md instructions/
   ```

3. Run MAD to generate complete technical documentation:
   ```bash
   python main.py
   ```

## What MAD Will Generate

From these source materials, MAD will create professional documentation including:

- **Overview** - System description, features, and use cases
- **Getting Started** - Quick setup guide achievable in <15 minutes
- **Installation Guide** - Detailed setup for all platforms
- **Configuration** - All options with examples and defaults
- **Architecture** - System design with diagrams
- **API Reference** - Complete endpoint documentation
- **CLI Reference** - All commands with examples
- **Code Examples** - Working examples in multiple languages
- **Troubleshooting** - Common issues and solutions
- **Performance** - Benchmarks and optimization tips
- **Security** - Security model and best practices
- **Deployment** - Production deployment guide
- **Migration Guide** - Upgrading between versions
- **FAQ** - Frequently asked questions
- **Glossary** - Technical terms explained
- **Changelog** - Version history

## Types of Source Materials You Can Provide

### API Documentation
- OpenAPI/Swagger specifications
- Postman collections
- API design documents
- Example requests/responses
- Error code definitions

### Architecture Documents
- System design documents
- Database schemas
- Network diagrams
- Sequence diagrams
- Technology decisions

### Code References
- Interface definitions
- SDK source code
- Example applications
- Integration tests
- Configuration files

### Command Line Tools
- CLI help output
- Command examples
- Shell scripts
- Installation procedures
- Environment setup

### Development Guides
- README files
- Setup instructions
- Development workflows
- Build processes
- Testing procedures

### Operations Documentation
- Deployment procedures
- Monitoring setup
- Performance metrics
- Scaling guidelines
- Disaster recovery

## Best Practices for Source Materials

1. **Include Real Examples** - Actual code, commands, and responses
2. **Document Edge Cases** - Error scenarios and limitations
3. **Show Common Workflows** - Step-by-step procedures
4. **Explain Design Decisions** - Why things work the way they do
5. **Include Performance Data** - Benchmarks and optimization tips

## File Format Support

MAD can process various technical document formats:
- YAML/JSON (API specs, configs)
- Markdown files
- Plain text files
- Code files (for parsing examples)
- PDF extracts

The system will synthesize all materials into well-structured, professional technical documentation that developers will actually want to read and use.

## Customization

After generating initial documentation, you can:
1. Add company-specific styling guides
2. Include proprietary examples
3. Add internal system details
4. Customize for your audience level
5. Add diagrams and screenshots

MAD will incorporate your customizations while maintaining professional documentation standards.