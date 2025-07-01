# Technical Documentation Template

## CRITICAL INSTRUCTIONS FOR DOCUMENT GENERATION

### Purpose
This template is designed for creating comprehensive technical documentation including API references, developer guides, system documentation, and technical manuals. It emphasizes clarity, accuracy, and usability for technical audiences.

### Required Output Files and Section Names

The documentation MUST be saved as separate files with these EXACT names:

1. **overview.md** - Section name: "Overview"
2. **getting_started.md** - Section name: "Getting Started"
3. **installation.md** - Section name: "Installation"
4. **configuration.md** - Section name: "Configuration"
5. **architecture.md** - Section name: "Architecture"
6. **api_reference.md** - Section name: "API Reference"
7. **code_examples.md** - Section name: "Code Examples"
8. **cli_reference.md** - Section name: "CLI Reference"
9. **troubleshooting.md** - Section name: "Troubleshooting"
10. **performance.md** - Section name: "Performance"
11. **security.md** - Section name: "Security"
12. **deployment.md** - Section name: "Deployment"
13. **migration_guide.md** - Section name: "Migration Guide"
14. **faq.md** - Section name: "FAQ"
15. **glossary.md** - Section name: "Glossary"
16. **changelog.md** - Section name: "Changelog"

### IMPORTANT FILE MANAGEMENT RULES

1. **DO NOT** create duplicate files with variations of these names
2. **DO NOT** add .md extension in the section_name parameter (it's added automatically)
3. **CONSOLIDATE** all API endpoints into the single api_reference.md file
4. **CONSOLIDATE** all code examples into the single code_examples.md file
5. **DELETE** any incorrectly named files before creating the correct ones
6. **VERIFY** file names match exactly - the system converts section names to lowercase with underscores

### Section Guidelines

#### Overview
**Purpose**: Provide high-level understanding of the system/product
**Required Elements:**
- Product/system name and version
- Brief description (2-3 sentences)
- Key features and capabilities (bullet list)
- Use cases and target audience
- Technology stack
- Prerequisites and system requirements
- Links to quick start and installation

**Style Notes:**
- Keep it concise (300-500 words)
- Use present tense
- Include a simple architecture diagram description
- No deep technical details here

#### Getting Started
**Purpose**: Get users up and running in under 15 minutes
**Required Sections:**
1. **Prerequisites Checklist**
   - Required software with versions
   - Account requirements
   - Access permissions needed

2. **Quick Installation**
   - Simplest installation method
   - Verification steps

3. **Hello World Example**
   - Minimal working example
   - Expected output
   - Common gotchas

4. **Next Steps**
   - Links to full installation guide
   - Links to tutorials
   - Links to examples

**Format Requirements:**
- Step-by-step numbered lists
- Code blocks with syntax highlighting markers
- Clear success indicators
- Estimated time for each step

#### Installation
**Comprehensive Installation Guide:**
1. **System Requirements**
   - Operating systems supported
   - Hardware requirements (CPU, RAM, disk)
   - Software dependencies with versions
   - Network requirements

2. **Installation Methods**
   - Package managers (npm, pip, apt, etc.)
   - Binary downloads
   - Building from source
   - Container/Docker installation

3. **Platform-Specific Instructions**
   - Windows
   - macOS  
   - Linux distributions
   - Cloud platforms

4. **Verification**
   - How to verify successful installation
   - Version checking commands
   - Basic functionality tests

5. **Uninstallation**
   - Clean removal instructions
   - Data backup considerations

**Include:**
- Command examples for each platform
- Troubleshooting common installation issues
- Proxy/firewall configuration if needed

#### Configuration
**Structure:**
1. **Configuration Files**
   - Location of config files
   - File format (JSON, YAML, etc.)
   - Loading precedence

2. **Configuration Options**
   - Table format:
     | Option | Type | Default | Description | Example |
     |--------|------|---------|-------------|---------|
   - Required vs optional settings
   - Environment variables

3. **Common Configurations**
   - Development setup
   - Production setup
   - High-availability setup

4. **Dynamic Configuration**
   - Runtime changes
   - Configuration API
   - Hot reload capabilities

5. **Validation**
   - Config validation tools
   - Common misconfigurations

#### Architecture
**Required Components:**
1. **System Overview**
   - High-level architecture diagram (describe in text)
   - Component descriptions
   - Data flow

2. **Core Components**
   - Purpose of each component
   - Interfaces between components
   - Dependencies

3. **Design Principles**
   - Architectural patterns used
   - Design decisions and rationale
   - Trade-offs made

4. **Scalability**
   - Horizontal/vertical scaling
   - Bottlenecks and limitations
   - Performance characteristics

5. **Integration Points**
   - External system interfaces
   - Plugin architecture
   - Extension mechanisms

#### API Reference
**Format for Each Endpoint:**
```markdown
### [HTTP_METHOD] /path/to/endpoint

**Description**: Brief description of what this endpoint does

**Authentication**: Required/Optional - Type (Bearer, API Key, etc.)

**Parameters**:
| Name | Type | Required | Description | Example |
|------|------|----------|-------------|---------|

**Request Body**:
```json
{
  "field": "type and description"
}
```

**Response**:
- **Success (200)**:
```json
{
  "result": "example response"
}
```
- **Error (4xx/5xx)**:
```json
{
  "error": "error description"
}
```

**Example**:
```bash
curl -X GET https://api.example.com/endpoint
```
```

**Organization:**
- Group by resource/functionality
- Include rate limits
- Versioning information
- Deprecation notices

#### Code Examples
**Structure:**
1. **Basic Examples**
   - Simple use cases
   - Minimal dependencies
   - Clear comments

2. **Advanced Examples**
   - Complex scenarios
   - Best practices demonstrated
   - Performance optimizations

3. **Integration Examples**
   - Common integrations
   - Third-party libraries
   - Framework-specific

4. **Complete Applications**
   - Small working apps
   - Architecture patterns
   - Testing included

**For Each Example:**
- Purpose statement
- Prerequisites
- Full code with comments
- Expected output
- Common variations
- Error handling

#### CLI Reference
**Format for Each Command:**
```markdown
### command-name

**Description**: What the command does

**Syntax**:
```bash
command-name [options] [arguments]
```

**Options**:
| Option | Short | Description | Default |
|--------|-------|-------------|---------|

**Arguments**:
| Argument | Required | Description |
|----------|----------|-------------|

**Examples**:
```bash
# Example 1: Basic usage
command-name --option value

# Example 2: Advanced usage
command-name --flag --option=value argument
```

**Output**: Description of output format
```

**Include:**
- Global options
- Command chaining
- Configuration via CLI
- Exit codes

#### Troubleshooting
**Structure:**
1. **Common Issues**
   - Problem description
   - Symptoms
   - Solution steps
   - Prevention tips

2. **Error Messages**
   - Error code/message
   - Meaning
   - Common causes
   - Resolution steps

3. **Debugging Tools**
   - Built-in debugging features
   - Log locations and levels
   - Debug mode activation
   - Profiling tools

4. **Getting Help**
   - Support channels
   - Information to provide
   - Community resources

#### Performance
**Required Sections:**
1. **Benchmarks**
   - Standard operations
   - Hardware used
   - Methodology

2. **Optimization Guide**
   - Configuration tuning
   - Code optimization tips
   - Caching strategies

3. **Monitoring**
   - Metrics to track
   - Monitoring tools
   - Alert thresholds

4. **Capacity Planning**
   - Resource requirements
   - Scaling guidelines
   - Load testing results

#### Security
**Critical Sections:**
1. **Security Model**
   - Authentication methods
   - Authorization framework
   - Encryption in transit/at rest

2. **Best Practices**
   - Secure configuration
   - Secret management
   - Network security

3. **Vulnerability Management**
   - Reporting vulnerabilities
   - Update process
   - Security advisories

4. **Compliance**
   - Standards supported
   - Audit logging
   - Data privacy

#### Deployment
**Deployment Scenarios:**
1. **Local Development**
   - Setup instructions
   - Hot reload configuration
   - Debugging setup

2. **Production Deployment**
   - Pre-deployment checklist
   - Deployment methods
   - Rollback procedures

3. **Cloud Deployments**
   - AWS/Azure/GCP guides
   - Container orchestration
   - Serverless options

4. **CI/CD Integration**
   - Pipeline examples
   - Automated testing
   - Deployment automation

#### Migration Guide
**For Version Upgrades:**
1. **Breaking Changes**
   - What changed
   - Why it changed
   - Impact assessment

2. **Migration Steps**
   - Pre-migration checklist
   - Step-by-step process
   - Rollback plan

3. **Code Changes**
   - Before/after examples
   - Automated migration tools
   - Manual updates required

4. **Testing Migration**
   - Test strategy
   - Validation steps
   - Performance impact

#### FAQ
**Categories:**
- General Questions
- Installation Issues
- Configuration Problems
- API Questions
- Performance Concerns
- Licensing

**Format:**
```markdown
**Q: Question text?**

A: Clear, concise answer with examples if needed.
```

#### Glossary
**Format:**
```markdown
**Term**: Definition that's clear to target audience. May include links to more detailed explanations.
```

**Organization:**
- Alphabetical order
- Cross-references
- Acronym expansions
- Domain-specific terms

#### Changelog
**Format:**
```markdown
## [Version] - YYYY-MM-DD

### Added
- New features

### Changed
- Modified functionality

### Deprecated
- Features marked for removal

### Removed
- Deleted features

### Fixed
- Bug fixes

### Security
- Security updates
```

### Writing Style Guidelines

1. **Clarity First**: Simple, clear language over complex terminology
2. **Consistency**: Same terms throughout, consistent formatting
3. **Completeness**: All information needed to use the feature
4. **Correctness**: Technically accurate and tested
5. **Conciseness**: No unnecessary words, get to the point
6. **Code Formatting**:
   - Syntax highlighting language specified
   - Consistent indentation
   - Meaningful variable names
   - Comments for complex logic

### Technical Standards

1. **Code Examples**:
   - Must be executable
   - Include all imports/requires
   - Handle errors appropriately
   - Follow language best practices

2. **Commands**:
   - Show both input and output
   - Include $ or > prompt indicators
   - Explain any placeholders

3. **Version Information**:
   - Clearly state version compatibility
   - Note deprecated features
   - Highlight breaking changes

### Common Pitfalls to Avoid

1. **Assuming Knowledge**: Define terms before using
2. **Missing Context**: Always explain why, not just how
3. **Outdated Examples**: Keep synchronized with code
4. **Platform Bias**: Cover all supported platforms
5. **Incomplete Instructions**: Test every procedure
6. **Poor Organization**: Information should be findable
7. **No Troubleshooting**: Anticipate common problems
8. **Ignoring Edge Cases**: Document limitations

### Quality Checklist
- [ ] All required sections present
- [ ] Code examples tested and working
- [ ] Clear navigation between sections
- [ ] Consistent formatting throughout
- [ ] No broken internal links
- [ ] Version information accurate
- [ ] Security considerations addressed
- [ ] Performance impacts noted
- [ ] Troubleshooting comprehensive
- [ ] Examples cover common use cases