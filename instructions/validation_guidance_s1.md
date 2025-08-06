# Validation Guidance: Section 1 - Personal Details

Your task is to validate a single file, `output_s1.md`, and produce a feedback report. You MUST strictly follow the required format for the report and use the validation rules below to identify and categorize issues.

---

## 1. Required Feedback Report Format

This is the most important instruction. Your entire response **MUST** begin with the `[FEEDBACK_SUMMARY]` block, followed by the detailed feedback.

**TEMPLATE:**
[FEEDBACK_SUMMARY]
Overall Status: [PASS or FAIL]
Critical: [Number of critical issues found]
Major: [Number of major issues found]
Minor: [Number of minor issues found]
[END_FEEDBACK_SUMMARY]

### Detailed Feedback

**Overall Assessment:**
[State clearly whether the document PASSES or FAILS. Provide a brief summary of the quality and what the writer should focus on.]
**Critical Issues:**
[List all critical issues found, or write "None". Provide specific examples and recommend actions for the writer, e.g., "CRITICAL: Remove hallucinated GP name 'Dr. Smith' and replace with information from the source documents."]
**Major Issues:**
[List all major issues found, or write "None". e.g., "Correct the file to include the 'Services Currently Involved' heading."]
**Minor Issues:**
[List all minor issues found, or write "None".]

**Note:** A document automatically FAILS if there is one or more CRITICAL issue.

---

## 2. Validation Rules

Use these rules to assess the document and populate your report.

### Rule Set A: Overall File Structure

*   **Expected File (CRITICAL):** The file `output_s1.md` MUST exist. If it is missing, this is a **CRITICAL** error.
*   **Placeholder Files (CRITICAL):** The existence of a file named `unnamed_section.md` is a **CRITICAL** error.
*   **Unexpected Files (MAJOR):** There should be NO other document files (e.g., `section_2...md`, `main_contact_details.md`). The presence of other section files at this stage is a **MAJOR** error.

### Rule Set B: Content Validation for `output_s1.md`

#### Anti-Hallucination and Source Verification
*   **(CRITICAL)** All information (names, dates, addresses, services involved) MUST be verifiable against the source documents. Flag any content that appears fabricated or cannot be traced back to the source PDFs as a **CRITICAL** hallucination error.
*   **(MAJOR)** Flag any content that seems embellished (e.g., adding details not present in the sources).

#### Empty/Minimal Content Check
*   **(CRITICAL)** The file `output_s1.md` MUST NOT be empty or contain only headers.
*   **(CRITICAL)** It is a **CRITICAL** error if the file has less than 50 characters of actual content beyond the headers.
*   **(CRITICAL)** It is a **CRITICAL** error if key fields like the child's name and date of birth are missing or contain only placeholder text like `[INSERT]`.

#### Section-Specific Content and Structure
1.  **Required Structure (MAJOR):** The file MUST contain these three specific sub-headings:
    *   `Child or Young Person’s Personal Details`
    *   `Main Contact Details`
    *   `Services Currently Involved with this Child or Young Person`
    *   *Failure to include all three is a **MAJOR** error.*

2.  **Required Content (CRITICAL):**
    *   Under `Child or Young Person’s Personal Details`, the file must contain at least the child's full name and date of birth.
    *   Under `Main Contact Details`, the file must contain at least one parent/carer with a name and relationship.
    *   Under `Services Currently Involved...`, the file must clearly identify the education setting.
    *   *Failure to include any of these is a **CRITICAL** error.*

3.  **Quality Checks (MINOR):**
    *   Check for inconsistent formatting (e.g., Date of Birth format is not DD/MM/CCYY).
    *   Ensure professional services are listed by department/practice name, not by individuals' names.


**Important** - Missing information should be flagged, but do not suggest that the writer should state “Not known” when a field has been left blank. Do NOT suggest that field headings are removed.