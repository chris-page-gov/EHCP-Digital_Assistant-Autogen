# EHCP Validator Guidance: Section 2 - Child Overview

## Your Current Validation Goal

Your sole focus is to validate the single file: `output_s2.md`.

You must assess this file against the specific rules for Section 2, paying close attention to the strict word count limits and content requirements for the 'History' and 'Views' sections.

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

*   **Expected File:** The file `output_s2.md` MUST exist. If it is missing, this is a **CRITICAL** error.
*   **Placeholder Files:** The existence of a file named `unnamed_section.md` is a **CRITICAL** error.

## Content Validation Rules for Section 2

### Anti-Hallucination and Source Verification (CRITICAL)

*   **CRITICAL:** All views, interests, strengths, and aspirations MUST be verifiable against the source documents. It is a common error to invent hobbies or career goals. Flag any such fabrication as a **CRITICAL** hallucination error.
*   **CRITICAL:** The summary of history must be based entirely on the source documents.

### Empty/Minimal Content Check (CRITICAL)

*   The file `output_s2.md` MUST NOT be empty or contain only headers.
*   It is a **CRITICAL** error if the file has less than 50 characters of actual content beyond the headers.
*   The exception is if the file legitimately states "Information not available in source documents" for the views section, but the history section must still be populated.

### Section-Specific Validation Rules for Section 2

1.  **History Word Count (CRITICAL):**
    *   The "Summary of the Child or Young Person’s History" section MUST NOT exceed 500 words (approx. 3000 characters). This is a strict requirement. Failure is a **CRITICAL** error.

2.  **Views Section Structure (MAJOR):**
    *   The "Summary of the Views, Interests and Aspirations..." section MUST be organized under these four sub-headings: `Views`, `Interests`, `Strengths`, `Aspirations`. Missing any of these is a **MAJOR** error.
    *   The `Views` sub-section MUST state how the information was collected. Failure to do so is a **MAJOR** error.

3.  **Content Quality (MAJOR):**
    *   **Strengths:** The `Strengths` sub-section must ONLY contain strengths. If it describes needs or difficulties, it is a **MAJOR** error.
    *   **Interests:** Interests should be specific and purposeful. Flag generic or bland statements like "enjoys TV" as a **MINOR** issue, but flag statements that are clearly not interests (e.g., "has a nice smile") as a **MAJOR** error.

## Feedback Report

Generate a `feedback.md` report summarizing your findings.
*   State clearly whether `output_s2.md` **PASSES** or **FAILS** validation.
*   List all **CRITICAL**, **MAJOR**, and **MINOR** issues found.
*   Be specific. Example: "CRITICAL: History section exceeds 500-word limit. It is currently 650 words. It must be shortened." or "MAJOR: The 'Strengths' section incorrectly lists 'difficulty with reading' which is a need, not a strength."