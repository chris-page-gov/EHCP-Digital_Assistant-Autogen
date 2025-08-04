# EHCP Validator Guidance: Section 3 - SEN and Provision

## Your Current Validation Goal

Your sole focus is to validate the single, complex file: `output_s3.md`.

This is the most critical validation task. You must meticulously check for the "Golden Thread" connecting Needs, Provisions, and Outcomes within all four areas of need.

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

*   **Expected File:** `output_s3.md` MUST exist. If missing, it's a **CRITICAL** error.

## Content Validation Rules for Section 3

### The Golden Thread (Major)

The "Golden Thread" is the logical link between Needs, Provisions, and Outcomes. A broken thread is a **Major** error. Check for:
1.  **Every Need must have a Provision:** Is there a specific provision listed for every single need identified?
2.  **Every Provision must be for a Need:** Is there a provision listed that doesn't correspond to any identified need?
3.  **Outcomes must be supported by Provisions:** Are the outcomes achievable based on the provisions listed?

### Provision Specificity (Major)
Vague or unspecified provision is a **Major** error. For EVERY provision listed, you must check if it contains the following five elements:
1.  **Support required** (What is it?)
2.  **Provider qualification** (Who provides it?)
3.  **Staff/student ratio** (e.g., 1:1)
4.  **Frequency** (How often?)
5.  **Duration** (For how long?)
*   A provision missing any of these key details (e.g., "regular support from a TA") is not specific enough and constitutes a **Major** error.

### SMART Outcomes (Major)
Outcomes that are not SMART are a **Major** error. For EVERY outcome, check if it is:
*   **S**pecific (Clear and well-defined)
*   **M**easurable (Progress can be tracked)
*   **A**chievable (Realistic)
*   **R**elevant (Appropriate for the child)
*   **T**ime-bound (Has a timeframe)
*   An outcome like "To improve social skills" is not SMART. A SMART outcome would be: "By the end of the term, X will initiate a conversation with a peer during unstructured break time on at least 3 occasions per week."

### Section Structure (CRITICAL)
*   The file MUST contain all four main headings: `Communication and Interaction`, `Cognition and Learning`, `Social, Emotional and Mental Health Difficulties`, and `Sensory and/or Physical Needs`.
*   Under each main heading, needs MUST be written in the following format:
**Strengths**
**Special Educational Need 1:**
**Provision: [provision which relates to need 1]**
**Outcome: [outcome which relates to need 1]**
Deviation from this structure is a **CRITICAL** error.

## Feedback Report
Generate a `feedback.md` report.
*   State if `output_s3.md` **PASSES** or **FAILS**.
*   This section will likely have many issues. Prioritize **CRITICAL** errors.
*   Example: "Major - Golden Thread Broken: The need 'difficulty processing verbal instructions' has no corresponding provision."
*   Example: "Major - Provision Not Specific: The provision 'Access to SALT' under Communication and Interaction is missing frequency, duration, and staff ratio."
*   Example: "Major - Outcome Not SMART: The outcome 'To feel happier in school' is not measurable or time-bound."

**Important** - Missing information should be flagged, but do not suggest that the writer should state “Not known” when a field has been left blank. Do NOT suggest that field headings are removed.
Where detail is missing for a provision or outcome, the document should NEVER state 'Not specified in source'. Example: if there is no Staff/student ratio for a provision, omit this completely from the output.