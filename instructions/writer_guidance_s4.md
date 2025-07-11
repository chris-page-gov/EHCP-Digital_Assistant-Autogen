# EHCP Writer Guidance: Section 4 - Health Care Needs and Provision

## Your Current Goal

Your sole focus for this task is to create **one single file**: `output_s4.md`.

You must identify any health care needs from the source documents that are related to the child's Special Educational Needs (SEN). For each need, you must detail the specific **Provision** required and the intended **Outcomes**.

---

## CRITICAL INSTRUCTIONS FOR DOCUMENT GENERATION

### ANTI-HALLUCINATION REQUIREMENTS

**ABSOLUTE RULE: Only include information that can be directly found in or clearly inferred from the source documents.**
**ABSOLUTE RULE: Do not include any information from Appendix A/App A for this section. This should not include any parent views.**

1.  **NO FABRICATION:** Never create fictional information. Do not invent needs, provisions, or outcomes. If details like frequency or duration of a provision are not in the source, state that.
2.  **MISSING INFORMATION:** If there are no health care needs related to SEN, you MUST state this clearly. Do not invent content to fill the section.
3.  **SOURCE VERIFICATION:** Every piece of information must be traceable to the source documents.
4.  **PROHIBITED CONTENT:** Do not mention specific names of prescribed drugs or medications.

---

## Required Output File for This Stage

You must create **only one file** in this stage. Use the `save_document_section` tool with the following parameters:

*   **Filename to create:** `output_s4.md`
*   **`section_name` parameter to use:** `"Health Care Needs and Health Care Provision"`

### Important File Management Rules

*   **One File Only:** Do not create any other files. Your only task is to create this single, consolidated Section 4 file.
*   **Correct Naming:** Use the exact `section_name` provided above in the tool.
*   **Delete Mistakes:** If you accidentally create a file with the wrong name, use the `delete_file` tool to remove it before saving the correct version.

---

## Section 4: Content and Structure Template

The file `output_s4.md` must be structured with the following three sub-headings.

### Health Care Needs Which Relate to Their Special Educational Needs

[This should capture the child or young person’s health care needs that are directly related to their special educational needs. Describe the need and its impact on their education.
If there are no relevant health needs identified in the source documents, you must enter: ‘Child or young person has no identified special educational needs in this area’.]

### Health Care Provision Reasonably Required

[**CRITICAL:** Provision must be specified for **each and every health need** identified above. The provision must be specific, detailed, and quantified. It must clearly state how it will support the achievement of the outcomes. Include the following five elements for each provision where available in the source documents:
1.  **Support required:** What specific support or intervention is needed.
2.  **Who will provide it:** The required qualification or level of expertise of the provider.
3.  **Staff/student ratio:** e.g., 1:1, 2:1, or group work.
4.  **How often:** The frequency, e.g., daily, weekly, termly.
5.  **How long for:** The duration for each session, e.g., hours or minutes.]

### Outcomes

[**CRITICAL:** An outcome is the benefit or difference made to an individual as a result of an intervention. All outcomes must be **SMART**:
- **S**pecific: Clear and well-defined.
- **M**easurable: Progress can be monitored with clear metrics.
- **A**chievable: Realistic given the provisions.
- **R**elevant: Appropriate for the child's abilities.
- **T**ime-bound: A clear timeframe is specified.
The outcome should be personal and not expressed from a service perspective. It must be clearly underpinned by the provision linked to it. If an outcome addresses multiple needs, use the identical text for that outcome in each relevant section.]