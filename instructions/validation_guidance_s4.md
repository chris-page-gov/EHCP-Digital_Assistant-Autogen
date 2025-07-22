# EHCP Validator Guidance: Section 4 - Health Care

## Your Current Validation Goal

Your sole focus is to validate the single file: `output_s4.md`.

This is the most critical validation task. You must meticulously check for the "Golden Thread" connecting Needs, Provisions, and Outcomes.

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

*   **Expected File:** `output_s4.md` MUST exist. If missing, it's a **CRITICAL** error.

## Content Validation Rules for Section 4

### The Golden Thread (Major)

*   Every identified Health Care Need MUST have a corresponding Health Care Provision.
*   Every Provision must link to a Need.
*   Outcomes must be achievable through the stated Provisions. A broken thread is a **Major** error.

### Provision Specificity (Major)

*   Vague health provision is a **Major** error. Check if each provision specifies the required support, provider, ratio, frequency, and duration.
*   "Ongoing access to nursing team" is NOT specific. "Weekly 30-minute check-in with the school nurse (1:1) to monitor condition" IS specific.

### SMART Outcomes (Major)

*   Health outcomes MUST be SMART (Specific, Measurable, Achievable, Relevant, Time-bound).
*   "To manage his condition" is NOT a SMART outcome. It is a **Major** error.

### Section-Specific Rules

*   **Relevance to SEN (CRITICAL):** The health needs described MUST relate to the child's special educational needs. A purely medical need with no impact on education should not be here. Flagging this is a **CRITICAL** issue.
*   **Prohibited Content (CRITICAL):** The file MUST NOT mention the names of specific prescribed drugs or medications. This is a **CRITICAL** error.
*   **Needs without provision (CRITICAL):** The health needs described must be clearly outlined in the source documents by professionals along with clearly defined provisions.
*   **No Needs Statement (Correctness Check):** If no health needs are present, the file MUST contain the exact phrase "Child or young person has no identified special educational needs in this area".

### Document Structure (CRITICAL)
Needs, provisions and outcomes MUST be written in the following format:
**Health Care Need 1:**
**Provision: [provision which relates to need 1]**
**Outcome: [outcome which relates to need 1]**
Deviation from this structure is a **CRITICAL** error.

## Feedback Report

Generate a `feedback.md` report.
*   State if `output_s4.md` **PASSES** or **FAILS**.
*   Prioritize **CRITICAL** errors.
*   Example: "CRITICAL - Prohibited Content: The file mentions 'is prescribed Ritalin'. This must be removed."
*   Example: "CRITICAL - Provision Not Specific: The provision for managing anxiety is listed as 'access to CAMHS' but lacks detail on what this entails, how often, and for how long."

**Important** - Missing information should be flagged, but do not suggest that the writer should state “Not known” when a field has been left blank. Do NOT suggest that field headings are removed.
Where detail is missing for a provision or outcome, the document should NEVER state 'Not specified in source'. Example: if there is no Staff/student ratio for a provision, omit this completely from the output.