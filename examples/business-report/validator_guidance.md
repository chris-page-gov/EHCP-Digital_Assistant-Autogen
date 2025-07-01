Business Report Validation Guidance

Overview
This document outlines comprehensive validation rules for assessing the quality, accuracy, and compliance of professional business reports. The validator system uses these rules to analyze report sections and generate feedback.

File Structure Validation

Expected Files
The following files MUST exist in the output directory. Missing files should be flagged as CRITICAL errors:

1. executive_summary.md - High-level overview and key findings
2. introduction.md - Context, objectives, and scope
3. background_analysis.md - Historical context and current state
4. methodology.md - Research and analysis methods
5. findings_and_results.md - Data analysis and discoveries
6. discussion.md - Interpretation and implications
7. recommendations.md - Actionable suggestions
8. conclusion.md - Summary and next steps
9. appendices.md - Supporting materials
10. references.md - Citations and sources

System Files (Should be Ignored)
These files are created by the system and should NOT be validated as document sections:
- feedback.md - Validation feedback report
- loop_report.json - Automated loop runner report
- Any log files (*.log)

File Naming Validation Rules
1. No duplicate files - Flag as CRITICAL if multiple versions of the same section exist
2. No unexpected files - Flag as MAJOR if files don't match expected patterns
3. Correct naming - All files must be lowercase with underscores, ending in .md
4. No placeholder files - Flag as CRITICAL if files like "draft_section.md" exist

Common File Errors to Check
- Split sections: Recommendations split into multiple files instead of consolidated
- Wrong names: Files like "exec_summary.md" instead of "executive_summary.md"
- Missing sections: Core sections not created
- Extra files: Temporary or working files left in output

Section-Specific Validation Rules

Executive Summary
Strict requirements:
- MUST NOT exceed 300 words
- Must include ALL of the following:
  - Purpose/objective statement
  - Key findings (3-5 bullet points)
  - Main recommendations (3-5 bullet points)
  - Expected impact/ROI
  - Call to action

Quality checks:
- No technical jargon without explanation
- Clear, actionable language
- Quantifiable metrics where possible
- Alignment with detailed findings in report body

Severity levels:
- CRITICAL: Missing key findings or recommendations
- MAJOR: Exceeds word limit, lacks metrics
- MINOR: Could be more concise, minor formatting issues

Introduction
Required elements:
- Clear problem statement or business opportunity
- Specific objectives (numbered list)
- Scope definition (what's included/excluded)
- Report structure overview
- Key stakeholders identified

Length: 200-400 words

Quality indicators:
- Sets clear expectations
- Defines success criteria
- Acknowledges limitations
- Professional tone

Background Analysis
Must contain:
- Historical context (relevant timeframe)
- Current state assessment
- Market/industry analysis
- Competitive landscape (if applicable)
- Key challenges and opportunities
- Stakeholder mapping

Quality checks:
- Data must be recent (flag if >2 years old without justification)
- Sources must be credible and cited
- Analysis must be objective and balanced
- Visual elements should be described (charts, graphs)

Methodology
Required components:
- Data collection methods
- Analysis frameworks used
- Tools and technologies
- Sample size/scope
- Timeline of research
- Limitations and assumptions
- Validation approach

Validation criteria:
- Methods must be appropriate for objectives
- Limitations must be clearly stated
- Reproducibility should be possible
- Ethical considerations addressed (if applicable)

Findings and Results
Structure requirements:
- Organized by theme or research question
- Clear data presentation
- Visual elements described
- Statistical significance noted (where applicable)
- Both positive and negative findings included

Quality validation:
- Data must support conclusions
- No cherry-picking of results
- Appropriate use of statistics
- Clear labeling of all figures/tables
- Objective presentation without bias

Discussion
Must include:
- Interpretation of all major findings
- Comparison with initial hypotheses/expectations
- Implications for the business
- Relationship to industry benchmarks
- Unexpected findings explained
- Limitations acknowledged

Quality criteria:
- Balanced analysis (pros and cons)
- Evidence-based reasoning
- Clear link between findings and interpretations
- Addresses potential objections
- Future considerations mentioned

Recommendations
Required format:
Each recommendation must include:
- Clear action statement
- Priority level (High/Medium/Low)
- Timeline (immediate/short-term/long-term)
- Resource requirements
- Expected outcomes/benefits
- Success metrics
- Risk assessment

Validation checks:
- Recommendations must flow from findings
- Must be specific and actionable
- Resource requirements must be realistic
- Success metrics must be measurable
- At least one quick win included

Conclusion
Must contain:
- Summary of key findings (2-3 sentences)
- Reiteration of main recommendations
- Overall impact assessment
- Clear next steps
- Final call to action

Length: 200-300 words

Quality checks:
- No new information introduced
- Consistent with executive summary
- Motivating and forward-looking
- Professional close

Appendices
Should include:
- Detailed data tables
- Technical specifications
- Survey instruments
- Interview guides
- Glossary of terms
- Additional charts/graphs
- Detailed calculations

Validation:
- All appendices must be referenced in main text
- Clear labeling and numbering
- Appropriate level of detail
- No redundant information

References
Requirements:
- Consistent citation format (APA, MLA, Chicago, etc.)
- All sources cited in text must appear in references
- Minimum 10 credible sources for substantial reports
- Mix of primary and secondary sources
- Recent sources (majority within last 5 years)

Quality checks:
- Proper formatting throughout
- URLs must be functional (if included)
- Author credentials verifiable
- Reputable publications/sources

Cross-Document Validation

Consistency Checks
- Findings in executive summary match detailed findings
- Recommendations consistent throughout document
- Data/statistics consistent across sections
- Terminology used consistently
- Tone and style uniform

Flow and Logic
- Each section builds on previous
- Clear transitions between sections
- Logical argument progression
- No gaps in reasoning
- Conclusions supported by evidence

Language and Style Standards

Professional Standards
- Formal business language
- Third-person perspective (unless specified otherwise)
- Active voice preferred
- Concise sentences (average 15-20 words)
- Paragraphs 3-5 sentences

Prohibited Elements
- Colloquialisms or slang
- Unsubstantiated claims
- Emotional language
- Personal opinions without evidence
- Discriminatory language
- Excessive use of acronyms

Data Presentation
- All numbers formatted consistently
- Percentages include base numbers
- Currency symbols used correctly
- Dates in consistent format
- Measurements include units

Validation Severity Levels

Critical Errors (Must Fix)
- Missing required sections
- Executive summary exceeds word limit
- Recommendations not actionable
- No supporting evidence for claims
- Broken logical flow
- Missing methodology
- Plagiarism or uncited sources

Major Issues (Should Fix)
- Inconsistent data across sections
- Weak evidence for recommendations
- Poor organization within sections
- Missing visual element descriptions
- Outdated sources (>5 years)
- Unclear success metrics
- Technical jargon without explanation

Minor Issues (Consider Fixing)
- Minor formatting inconsistencies
- Could be more concise
- Some passive voice usage
- Minor grammatical errors
- Some undefined acronyms
- Slightly verbose sections

Feedback Report Structure

The validator should generate feedback.md with:

1. Executive Summary
   - Overall document quality score
   - Number of critical/major/minor issues
   - Key strengths identified
   - Priority improvements needed

2. File Structure Analysis
   - List of missing files
   - Incorrectly named files
   - Unexpected files found
   - Recommendations for fixes

3. Section-by-Section Analysis
   - Compliance score for each section
   - Specific issues with examples
   - Line-by-line feedback where needed
   - Suggestions for improvement

4. Cross-Document Issues
   - Consistency problems
   - Flow and logic gaps
   - Style inconsistencies

5. Data and Evidence Review
   - Quality of sources
   - Strength of evidence
   - Data presentation issues

6. Recommendations Priority List
   - Critical fixes required
   - Major improvements suggested
   - Minor enhancements
   - Timeline for fixes

7. Overall Compliance Score
   - Score by category (structure, content, style)
   - Total document score
   - Comparison to quality benchmarks