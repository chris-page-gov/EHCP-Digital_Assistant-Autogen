# EHCP Validator Guidance: Section 5 - Social Care

## Your Current Validation Goal

Your sole focus is to validate the single file: `output_s5.md`.

You will apply the same "Golden Thread," "Provision Specificity," and "SMART Outcome" rules, and also validate the correct classification of provision into H1 and H2 categories.

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

### The Golden Thread (CRITICAL)

*   Every identified Social Care Need MUST have a corresponding Provision (either H1 or H2).
*   Every Provision must link to a Need.
*   Outcomes must be achievable through the stated Provisions. A broken thread is a **CRITICAL** error.

### Provision Specificity (CRITICAL)

*   Vague social care provision is a **CRITICAL** error. Check if each provision specifies the required support, provider, ratio, frequency, and duration.
*   "Support to access the community" is NOT specific. "Support from a youth worker (1:1) for 2 hours per week to attend a local youth club" IS specific.

### SMART Outcomes (Major)

*   Social care outcomes should be SMART (Specific, Measurable, Achievable, Relevant, Time-bound).
*   "To make friends" is NOT a SMART outcome. It is a **Major** error.

### Section-Specific Rules

*   **Relevance to SEN (MAJOR):** The social care needs described MUST relate to the child's SEN or disability.
*   **H1/H2 Classification (MAJOR):** Check if the provision seems correctly placed. For example, 'help with personal care at home' belongs in H1. 'Referral for family support' might belong in H2. Misclassification is a **MAJOR** error.
*   **Structure (MAJOR):** The file MUST contain the headings `Social Care Needs`, `H1 Social Care Provision`, `Other (H2) Social Care Provision`, and `Outcomes`.
*   **No Needs Statement (Correctness Check):** If no social care needs are present, the file MUST contain the exact phrase "Child or young person has no identified special educational needs in this area".

## Feedback Report

Generate a `feedback.md` report.
*   State if `output_s5.md` **PASSES** or **FAILS**.
*   Prioritize **CRITICAL** errors related to the Golden Thread, Specificity, and SMART criteria.
*   Example: "CRITICAL - Golden Thread Broken: A need for 'support to develop independence skills' is listed, but no provision in H1 or H2 addresses this."
*   Example: "MAJOR - Incorrect Classification: 'Assistance with travel to college' is listed under H2 but should be in H1."