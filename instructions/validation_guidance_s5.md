# EHCP Validator Guidance: Section 5 - Social Care

## Your Current Validation Goal

Your sole focus is to validate the single file: `output_s5.md`.

This is the most critical validation task. You must meticulously check for the "Golden Thread" connecting Needs, Provisions, and Outcomes, and also validate the correct classification of provision into H1 and H2 categories.

## Required Feedback Report Format

This is the most important instruction. Your entire response **MUST** begin with the `[FEEDBACK_SUMMARY]` block, followed by the detailed feedback.

**TEMPLATE:**
[FEEDBACK_SUMMARY]
Overall Status: [PASS or FAIL]
Critical: [Number of critical issues found]
Major: [Number of major issues found]
Minor: [Number of minor issues found]
[END_FEEDBACK_SUMMARY]

## Overall File Structure Validation for This Stage

*   **Expected File:** `output_s5.md` MUST exist. If missing, it's a **CRITICAL** error.

## Content Validation Rules for Section 5

### The Golden Thread (MAJOR)

*   Every identified Social Care Need MUST have a corresponding Provision (either H1 or H2).
*   Every Provision must link to a Need.
*   Outcomes must be achievable through the stated Provisions. A broken thread is a **Major** error.

### Provision Specificity (Major)

*   Vague social care provision is a **Major** error. Check if each provision specifies the required support, provider, ratio, frequency, and duration.
*   "Support to access the community" is NOT specific. "Support from a youth worker (1:1) for 2 hours per week to attend a local youth club" IS specific.

### SMART Outcomes (Major)

*   Social care outcomes should be SMART (Specific, Measurable, Achievable, Relevant, Time-bound).
*   "To make friends" is NOT a SMART outcome. It is a **Major** error.

### Section-Specific Rules

*   **Relevance to SEN (MAJOR):** The social care needs described MUST relate to the child's SEN or disability.
*   **H1/H2 Classification (MAJOR):** Check if the provision seems correctly placed. For example, 'help with personal care at home' belongs in H1. 'Referral for family support' might belong in H2. Misclassification is a **MAJOR** error.
[H1 includes social care provision that is made under the Chronically Sick and Disabled Persons Act 1970. This includes services like:
- Practical assistance in the home (e.g., help with personal care).
- Provision of, or assistance with, recreational and educational facilities.
- Assistance with travel.
- Adaptations to the home.
- Facilitating holidays, meals, or telephone access.

H2 is for any other social care provision reasonably required by the learning difficulties or disabilities which result in the child having SEN. This is provision that does **not** fall under the H1 criteria above]
*   **Needs without provision (CRITICAL):** The social care needs described must be clearly outlined in the source documents by professionals along with clearly defined provisions.
*   **No Needs Statement (Correctness Check):** If no social care needs are present, the file MUST contain the exact phrase "Child or young person has no identified special educational needs in this area".

### Document Structure (CRITICAL)
Needs, provisions and outcomes MUST be written in the following format:
**Social Care Need 1:**
**H1 Provision: [H1 Social Care provision which relates to need 1]**
**H2 Provision: [H2 Social Care provision which relates to need 1]**
**Outcome: [outcome which relates to need 1]**
Deviation from this structure is a **CRITICAL** error.

## Feedback Report

Generate a `feedback.md` report.
*   State if `output_s5.md` **PASSES** or **FAILS**.
*   Prioritize **CRITICAL** errors related to the Golden Thread, Specificity, and SMART criteria.
*   Example: "CRITICAL - Golden Thread Broken: A need for 'support to develop independence skills' is listed, but no provision in H1 or H2 addresses this."
*   Example: "MAJOR - Incorrect Classification: 'Assistance with travel to college' is listed under H2 but should be in H1."

**Important** - Missing information should be flagged, but do not suggest that the writer should state “Not known” when a field has been left blank. Do NOT suggest that field headings are removed.