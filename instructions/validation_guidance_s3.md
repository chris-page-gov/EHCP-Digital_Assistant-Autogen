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

### The Golden Thread (CRITICAL)

The "Golden Thread" is the logical link between Needs, Provisions, and Outcomes. A broken thread is a **CRITICAL** error. Check for:
1.  **Every Need must have a Provision:** Is there a specific provision listed for every single need identified?
2.  **Every Provision must be for a Need:** Is there a provision listed that doesn't correspond to any identified need?
3.  **Outcomes must be supported by Provisions:** Are the outcomes achievable based on the provisions listed?

### Provision Specificity (CRITICAL)

Vague or unspecified provision is a **CRITICAL** error. For EVERY provision listed, you must check if it contains the following five elements:
1.  **Support required** (What is it?)
2.  **Provider qualification** (Who provides it?)
3.  **Staff/student ratio** (e.g., 1:1)
4.  **Frequency** (How often?)
5.  **Duration** (For how long?)
*   A provision missing any of these key details (e.g., "regular support from a TA") is not specific enough and constitutes a **Major** error.

### SMART Outcomes (CRITICAL)

Outcomes that are not SMART are a **CRITICAL** error. For EVERY outcome, check if it is:
*   **S**pecific (Clear and well-defined)
*   **M**easurable (Progress can be tracked)
*   **A**chievable (Realistic)
*   **R**elevant (Appropriate for the child)
*   **T**ime-bound (Has a timeframe)
*   An outcome like "To improve social skills" is not SMART. A SMART outcome would be: "By the end of the term, X will initiate a conversation with a peer during unstructured break time on at least 3 occasions per week."

### Section Structure (MAJOR)

*   The file MUST contain all four main headings: `Communication and Interaction`, `Cognition and Learning`, `Social, Emotional and Mental Health Difficulties`, and `Sensory and/or Physical Needs`.
*   Under each main heading, it MUST contain the three sub-headings: `Identified Special Educational Need(s)`, `Provision Relating to That Need`, and `Intended Outcomes`. Missing structure is a **MAJOR** error.

## Feedback Report

Generate a `feedback.md` report.
*   State if `output_s3.md` **PASSES** or **FAILS**.
*   This section will likely have many issues. Prioritize **CRITICAL** errors.
*   Example: "CRITICAL - Golden Thread Broken: The need 'difficulty processing verbal instructions' has no corresponding provision."
*   Example: "CRITICAL - Provision Not Specific: The provision 'Access to SALT' under Communication and Interaction is missing frequency, duration, and staff ratio."
*   Example: "CRITICAL - Outcome Not SMART: The outcome 'To feel happier in school' is not measurable or time-bound."