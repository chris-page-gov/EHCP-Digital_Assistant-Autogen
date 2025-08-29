### Universal Validation Rules

#### Anti-Hallucination and Source Verification
*   **(CRITICAL)** All information in the file being validated MUST be verifiable against the source documents. Flag any content that appears fabricated or cannot be traced back to the source PDFs as a **CRITICAL** hallucination error.
*   **(CRITICAL)** The presence of placeholder text such as `[INSERT]` is a CRITICAL error.
*   **(CRITICAL)** The presence of conversational text such as "information not provided in the source documents" is a CRITICAL error.

#### File Structure Rules
*   **(CRITICAL)** The file being validated MUST NOT be empty or contain only headers. It is a **CRITICAL** error if the file has less than 50 characters of actual content beyond the headers.