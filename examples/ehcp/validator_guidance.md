EHCP Validation Guidance

Overview
This document outlines comprehensive validation rules for assessing the quality, accuracy, and compliance of Education, Health and Care Plan (EHCP) documents. The validator system uses these rules to analyze EHCP sections and generate feedback.

Content Verification and Anti-Hallucination Rules

CRITICAL: Source Document Verification
All content MUST be verifiable against source documents. The validator should check for:

1. Hallucinated Content (CRITICAL severity):
   - Names not found in source documents
   - Activities, interests, or aspirations not mentioned in sources
   - Dates or events not documented
   - Career goals or specific preferences not in sources
   - Any detailed claims that cannot be traced to source materials

2. Embellished Content (MAJOR severity):
   - Exaggerated descriptions beyond source material
   - Added qualifiers or adjectives not in sources
   - Specific percentages or metrics not from assessments
   - Terminology variations that change meaning

3. Missing Source Indicators (MAJOR severity):
   - Sections that should state "Information not available in source documents"
   - Content that appears generated rather than sourced
   - Suspicious level of detail for areas typically sparse in assessments

Validation Approach
- Flag any content that seems too specific or detailed without source verification
- Check for common hallucination patterns (career aspirations, specific hobbies, detailed preferences)
- Verify professional names and dates against expected patterns
- Look for sections with suspiciously complete information

File Structure Validation

Expected Files
The following files MUST exist in the output directory. Missing files should be flagged as CRITICAL errors:

1. personal_details.md - Contains both personal details AND main contact details
2. section_a1_summary_of_history.md - Child's history (max 500 words)
3. section_a2_views_interests_aspirations.md - Views, interests, strengths, and aspirations
4. section_b_communication_and_interaction.md - Communication and interaction needs
5. section_b_cognition_and_learning.md - Cognition and learning needs
6. section_b_social_emotional_mental_health.md - Social, emotional and mental health needs
7. section_b_sensory_physical_needs.md - Sensory and/or physical needs
8. section_c_health_care_needs.md - Health care needs related to SEN
9. section_d_social_care_needs.md - Social care needs
10. section_e_outcomes.md - ALL outcomes consolidated in one file
11. section_f_special_educational_provision.md - ALL special educational provisions consolidated
12. section_g_health_care_provision.md - Health care provision
13. section_h1_social_care_provision_csdpa.md - Social care under CSDPA 1970
14. section_h2_other_social_care_provision.md - Other social care provision
15. section_i_placement.md - Placement details
16. section_j_direct_payments.md - Direct payments information
17. section_k_advice_and_information.md - Professional advice gathered
18. sign_off.md - Local authority sign-off

System Files (Should be Ignored)
These files are created by the system and should NOT be validated as document sections:
- feedback.md - Validation feedback report
- loop_report.json - Automated loop runner report
- Any log files (*.log)

File Naming Validation Rules
1. No duplicate files - Flag as CRITICAL if multiple versions of the same section exist
2. No unexpected files - Flag as MAJOR if files don't match expected patterns
3. Correct naming - All files must be lowercase with underscores, ending in .md
4. No placeholder files - Flag as CRITICAL if files like "unnamed_section.md" exist

Common File Errors to Check
- Split sections: Section E outcomes or Section F provisions split into multiple files
- Wrong names: Files like "main_contact_details.md" instead of being in personal_details.md
- Missing consolidation: Multiple outcome files instead of single section_e_outcomes.md
- Typos in names: e.g., "section_a1_summary_history.md" missing "of"
- Empty sections: Files containing only headers with no content (CRITICAL error)
- Minimal content: Sections with less than 50 characters of actual content beyond the header (CRITICAL error)

Content Validation Rules

Empty Content Check (CRITICAL)
Each section file MUST contain substantive content beyond just the header. The validator must:
1. Check file size - files under 100 bytes are likely empty
2. Verify content exists after the header line
3. Count actual content characters (excluding header and whitespace)
4. Flag as CRITICAL if section contains:
   - Only a header with no body content
   - Less than 50 characters of actual content
   - Only "Information not available" without attempting to provide any context
5. Exception: Section A2 may legitimately contain only "Information not available in source documents" if views were not gathered

Minimum Content Requirements
- Personal Details: Must have at least name, DOB, and one contact
- Section A1: Must have substantive history (minimum 100 words)
- Section B subsections: Must describe the need even if brief
- Sections C-K: Must have content or explicit statement why not applicable
- Sign-off: Must have authority details and date

Required Sections
All EHCP documents must contain the following sections. Missing sections should be flagged as critical errors:

1. Personal Details - Child/young person information, contacts, and services
2. Section A1 - Summary of history
3. Section A2 - Views, interests, strengths, and aspirations
4. Section B - Special Educational Needs (4 subsections):
   - Communication and interaction
   - Cognition and learning
   - Social, emotional and mental health
   - Sensory and/or physical needs
5. Section C - Health care needs
6. Section D - Social care needs
7. Section E - Outcomes
8. Section F - Special educational provision
9. Section G - Health care provision
10. Section H1 & H2 - Social care provision
11. Section I - Placement details
12. Section J & K - Direct payments and advice gathered

Section-Specific Validation Rules

Personal Details
Required elements:
- Child/young person's full name
- Date of birth (format: YYYY-MM-DD)
- Sex and ethnicity
- Main contact details (parent/carer name, relationship, email, phone, address)
- Current education setting
- GP/key health professional details
- NHS number (if available)
- Social care status
- Looked after child status (current and historical)

Quality checks:
- All required fields must be populated (no placeholders like [INSERT])
- Contact details must be complete and formatted correctly
- Professional services must be clearly identified

Section A1 - Summary of History
Strict requirements:
- MUST NOT exceed 500 words (3000 characters)
- Must include:
  - Brief overview of child's circumstances
  - Proposed future learning and development
  - Communication preferences and engagement methods

Quality indicators:
- Concise and focused content
- No unnecessary repetition
- Clear, professional language
- Child-centered perspective

Section A2 - Views, Interests, Strengths, and Aspirations
Content requirements:
- Should be approximately one page (500 words/3000 characters)
- Must clearly state how information was collected
- Must identify if someone provided information on child's behalf

CRITICAL ANTI-HALLUCINATION CHECKS for Section A2:
- RED FLAGS: Career aspirations (teacher, doctor, etc.) not in sources
- RED FLAGS: Specific hobbies (creative writing, art club, etc.) not documented
- RED FLAGS: Detailed preferences (fantasy books, painting) without source
- REQUIRED: If no views/interests documented, must state "Information not available in source documents"
- VERIFY: Any specific activity mentioned must appear in source materials

Sub-sections validation:
- Views: Must reflect child/young person's perspective FROM SOURCES
- Interests: Specific and purposeful FROM DOCUMENTED EVIDENCE
- Strengths: Only strengths MENTIONED IN ASSESSMENTS
- Aspirations: Child's ambitions ONLY IF STATED IN SOURCES

Section B - Special Educational Needs
Structure validation:
- Must cover all four areas (even if stating "no identified needs")
- Each need must be clearly described with impact explained
- Needs must link to provisions in Section F

Quality checks:
- Professional terminology used appropriately
- Specific rather than generic descriptions
- Clear explanation of impact on learning

Section C - Health Care Needs
Requirements:
- Only health needs related to SEN
- Clear description of each health need
- Impact on education must be explained
- If no needs, must explicitly state: "Child or young person has no identified special educational needs in this area"

Section D - Social Care Needs
Requirements:
- Only social care needs related to SEN or disability
- Clear impact description
- Must relate to educational context
- If no needs, must explicitly state this

Section E - Outcomes
SMART Criteria - ALL outcomes must be:
- Specific: Clear and well-defined
- Measurable: Progress can be monitored with clear metrics
- Achievable: Realistic given the provisions
- Relevant: Appropriate for the child's abilities
- Time-bound: Clear timeframe specified

Additional outcome requirements:
- Personal and child-centered (not service-focused)
- Based on achievement, independence, participation in society, health
- Must clearly link to identified needs
- Must be underpinned by specified provisions

Section F - Special Educational Provision
Five mandatory elements for EACH provision:
1. Support required - What specific support/intervention
2. Provider qualification - Who provides it and required expertise
3. Staff/student ratio - e.g., 1:1, 2:1, 6:1 group work
4. Frequency - Daily, weekly, termly (must be specific)
5. Duration - Hours must be specified

Quality validation:
- Every need in Section B must have corresponding provision
- Provisions must be specific and quantifiable
- No vague terms like "regular support" or "as needed"

Section G - Health Care Provision
Requirements:
- Must address all needs identified in Section C
- Same five elements as Section F
- Clear specification of therapy/medical support
- Distinguish between education and health funding

Section H1 & H2 - Social Care Provision
Structure:
- H1: Provision under Chronically Sick and Disabled Persons Act 1970
- H2: Other social care provision related to SEN
- Must address all needs in Section D
- Clear specification of support type and frequency

Section I - Placement
Required information:
- Type of institution (mainstream/special/other)
- Specific school/setting name
- Any special arrangements or resources
- Transport arrangements if applicable

Section J & K - Direct Payments and Advice
Validation:
- Clear statement on direct payments (yes/no and details)
- List of all professionals who provided advice
- Summary of key recommendations from advice

Golden Thread Validation

The validator must check for the "golden thread" - clear connections between:
1. Needs (Sections B, C, D) ->
2. Provisions (Sections F, G, H) ->
3. Outcomes (Section E)

Golden thread requirements:
- Every identified need must have corresponding provision
- Every provision must link to specific outcomes
- Outcomes must be achievable through the stated provisions
- No provisions without corresponding needs
- No outcomes without supporting provisions

Cross-Section Consistency Checks

Information consistency:
- Child's name must be consistent throughout
- Date of birth must match across sections
- School/placement information must align
- Professional involvement must be consistent

Logical consistency:
- Severity of needs should match level of provision
- Outcomes should be proportionate to provisions
- No contradictions between sections

Language and Quality Standards

Professional language requirements:
- Person-first language (e.g., "child with autism" not "autistic child")
- Positive and respectful tone
- Avoid jargon where possible
- Clear explanations of technical terms

Prohibited content:
- Generic or copied text
- Placeholder text (e.g., [INSERT], [TO BE COMPLETED])
- Discriminatory or judgmental language
- Unnecessary medical details unrelated to education

Formatting Standards

Document structure:
- Clear section headers
- Consistent formatting throughout
- Proper markdown syntax
- Logical flow between sections

File naming:
- Must follow expected patterns (e.g., section_a1.md, personal_details.md)
- All lowercase with underscores
- No special characters

Validation Severity Levels

Critical Errors (Must Fix)
- Missing required sections
- Section A1 exceeding 500 words
- Missing provision elements (any of the 5 required)
- Broken golden thread
- Outcomes not meeting SMART criteria
- Placeholder text remaining
- Hallucinated content in Section A2

Major Issues (Should Fix)
- Inconsistent information between sections
- Vague or non-specific provisions
- Generic outcomes
- Missing impact descriptions for needs
- Poor professional language
- Embellished content beyond sources

Minor Issues (Consider Fixing)
- Formatting inconsistencies
- Minor grammatical errors
- Overly technical language
- Slightly verbose sections

Feedback Report Structure

The validator should generate feedback.md with:
1. Executive Summary
   - Overall compliance status
   - Number of critical/major/minor issues
   - Key strengths identified

2. File Structure Analysis
   - List of expected files that are missing
   - List of unexpected files found
   - File naming issues identified
   - Recommendations for file cleanup/deletion

3. Section-by-Section Analysis
   - Compliance with specific rules
   - Issues found with examples
   - Specific line references where applicable

4. Golden Thread Analysis
   - Mapping of needs to provisions to outcomes
   - Gaps or misalignments identified

5. Recommendations
   - Prioritized list of improvements
   - Specific suggestions for each issue
   - Files to delete or rename

6. Compliance Scores
   - Score for each section (0-100%)
   - Overall document score
   - Breakdown by validation category
   - File structure compliance score