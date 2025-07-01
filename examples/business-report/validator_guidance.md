# Business Report Validation Guidance

## Overview
This document outlines comprehensive validation rules for assessing the quality, accuracy, and compliance of professional business reports. The validator system uses these rules to analyze report sections and generate feedback.

## File Structure Validation

### Expected Files
The following files MUST exist in the output directory. Missing files should be flagged as CRITICAL errors:

1. **executive_summary.md** - High-level overview and key findings
2. **introduction.md** - Context, objectives, and scope
3. **background_analysis.md** - Historical context and current state
4. **methodology.md** - Research and analysis methods
5. **findings_and_results.md** - Data analysis and discoveries
6. **discussion.md** - Interpretation and implications
7. **recommendations.md** - Actionable suggestions
8. **conclusion.md** - Summary and next steps
9. **appendices.md** - Supporting materials
10. **references.md** - Citations and sources

### System Files (Should be Ignored)
These files are created by the system and should NOT be validated as document sections:
- **feedback.md** - Validation feedback report
- **loop_report.json** - Automated loop runner report
- Any log files (*.log)

### File Naming Validation Rules
1. **No duplicate files** - Flag as CRITICAL if multiple versions of the same section exist
2. **No unexpected files** - Flag as MAJOR if files don't match expected patterns
3. **Correct naming** - All files must be lowercase with underscores, ending in .md
4. **No placeholder files** - Flag as CRITICAL if files like "draft_section.md" exist

### Common File Errors to Check
- **Split sections**: Recommendations split into multiple files instead of consolidated
- **Wrong names**: Files like "exec_summary.md" instead of "executive_summary.md"
- **Missing sections**: Core sections not created
- **Extra files**: Temporary or working files left in output

## Section-Specific Validation Rules

### Executive Summary
**Strict requirements:**
- MUST NOT exceed 300 words
- Must include ALL of the following:
  - Purpose/objective statement
  - Key findings (3-5 bullet points)
  - Main recommendations (3-5 bullet points)
  - Expected impact/ROI
  - Call to action

**Quality checks:**
- No technical jargon without explanation
- Clear, actionable language
- Quantifiable metrics where possible
- Alignment with detailed findings in report body

**Severity levels:**
- CRITICAL: Missing key findings or recommendations
- MAJOR: Exceeds word limit, lacks metrics
- MINOR: Could be more concise, minor formatting issues

### Introduction
**Required elements:**
- Clear problem statement or business opportunity
- Specific objectives (numbered list)
- Scope definition (what's included/excluded)
- Report structure overview
- Key stakeholders identified

**Length:** 200-400 words

**Quality indicators:**
- Sets clear expectations
- Defines success criteria
- Acknowledges limitations
- Professional tone

### Background Analysis
**Must contain:**
- Historical context (relevant timeframe)
- Current state assessment
- Market/industry analysis
- Competitive landscape (if applicable)
- Key challenges and opportunities
- Stakeholder mapping

**Quality checks:**
- Data must be recent (flag if >2 years old without justification)
- Sources must be credible and cited
- Analysis must be objective and balanced
- Visual elements should be described (charts, graphs)

### Methodology
**Required components:**
- Data collection methods
- Analysis frameworks used
- Tools and technologies
- Sample size/scope
- Timeline of research
- Limitations and assumptions
- Ethical considerations (if applicable)

**Validation rules:**
- All data sources must be specified
- Statistical methods must be appropriate
- Limitations must be honestly addressed
- Reproducibility should be possible

### Findings and Results
**Structure requirements:**
- Organized by theme or objective
- Each finding must be:
  - Numbered
  - Supported by data
  - Clearly stated
  - Objectively presented

**Quality indicators:**
- Quantitative data includes units and context
- Qualitative findings are properly attributed
- No interpretation in this section (facts only)
- Visual representations are described
- Key statistics are highlighted

**Common issues:**
- Mixing findings with recommendations
- Unsupported claims
- Cherry-picking data
- Lack of structure

### Discussion
**Must include:**
- Interpretation of each major finding
- Implications for the business
- Comparison with expectations/benchmarks
- Addressing contradictory findings
- Risk assessment
- Opportunity analysis

**Quality standards:**
- Links findings to business objectives
- Considers multiple perspectives
- Acknowledges uncertainty
- Provides context for recommendations

### Recommendations
**Format requirements:**
- Numbered list (typically 5-10 items)
- Each recommendation must include:
  - Specific action
  - Priority level (High/Medium/Low)
  - Timeline (Immediate/Short-term/Long-term)
  - Resource requirements
  - Expected outcome/benefit
  - Success metrics

**Validation checks:**
- Recommendations directly address findings
- Actions are specific and measurable
- Resource requirements are realistic
- Dependencies are identified
- Quick wins are highlighted

**Quality issues to flag:**
- Vague recommendations ("improve processes")
- Missing implementation details
- Unrealistic timelines
- No success metrics
- Not prioritized

### Conclusion
**Required elements:**
- Summary of main findings (2-3 sentences)
- Restatement of critical recommendations
- Expected impact if implemented
- Next steps
- Final call to action

**Length:** 200-300 words

**Quality checks:**
- No new information introduced
- Aligns with executive summary
- Inspiring but realistic tone
- Clear closure

### Appendices
**Should contain:**
- Detailed data tables
- Survey instruments
- Technical specifications
- Glossary of terms
- Additional analysis
- Supporting documents

**Validation:**
- All appendices referenced in main text
- Properly labeled (Appendix A, B, etc.)
- Relevant to report content

### References
**Requirements:**
- Consistent citation format (APA, MLA, or Chicago)
- All sources cited in text appear in references
- Minimum 10 credible sources for substantial reports
- Mix of source types (academic, industry, data)
- Recent sources (majority within 5 years)

**Quality checks:**
- No broken links
- Reputable sources
- Proper formatting
- Alphabetical order

## Cross-Section Validation

### Consistency Checks
1. **Executive Summary Alignment**
   - Findings match those in results section
   - Recommendations consistent throughout
   - Metrics align across sections

2. **Data Consistency**
   - Numbers/statistics consistent across sections
   - Terminology used consistently
   - Dates and timelines align

3. **Logical Flow**
   - Each section builds on previous
   - No gaps in logic
   - Recommendations follow from findings

### Professional Standards
1. **Language and Tone**
   - Professional throughout
   - Industry-appropriate terminology
   - Active voice preferred
   - No colloquialisms

2. **Formatting**
   - Consistent heading hierarchy
   - Proper markdown usage
   - Bullet points for lists
   - Tables for comparative data

3. **Evidence-Based**
   - All claims supported
   - Data properly attributed
   - Assumptions clearly stated
   - Limitations acknowledged

## Severity Level Definitions

### CRITICAL (Must Fix)
- Missing required sections
- Unsupported major claims
- Incorrect or manipulated data
- Missing executive summary elements
- No actionable recommendations
- Exceeds strict word limits by >50%

### MAJOR (Should Fix)
- Weak methodology description
- Inconsistent data between sections
- Vague recommendations
- Poor source quality
- Missing key stakeholders
- Unclear objectives

### MINOR (Consider Fixing)
- Minor formatting inconsistencies
- Could be more concise
- Additional context would help
- More recent sources available
- Visual elements could enhance
- Minor grammatical issues

## Final Quality Checklist
- [ ] All required files present
- [ ] Word limits respected
- [ ] Professional tone throughout
- [ ] Data properly supported
- [ ] Recommendations actionable
- [ ] Consistent formatting
- [ ] Proper citations
- [ ] Logical flow
- [ ] Executive-ready
- [ ] Value clearly demonstrated