# EHCP Writer Guidance: Section 5 - Social Care Needs and Provision

## Your Current Goal

Your sole focus for this task is to create **one single file**: `output_s5.md`.

You must identify any social care needs from the source documents that are related to the child's SEN or disability. For each need, you must detail the specific **Provision** required (classifying it as H1 or H2) and the intended **Outcomes**.

---

## CRITICAL INSTRUCTIONS FOR DOCUMENT GENERATION

### ANTI-HALLUCINATION REQUIREMENTS

**ABSOLUTE RULE: Only include information that can be directly found in or clearly inferred from the source documents.**
**ABSOLUTE RULE: Do not include any information from Appendix A/App A for this section. This should not include any parent views.**

1.  **NO FABRICATION:** Never create fictional information. Do not invent needs, provisions, or outcomes. If details for a provision (like frequency) are not in the source, state that.
2.  **MISSING INFORMATION:** If there are no social care needs related to SEN, you MUST state this clearly. Do not invent content to fill the section.
3.  **SOURCE VERIFICATION:** Every piece of information must be traceable to the source documents.

---

## Required Output File for This Stage

You must create **only one file** in this stage. Use the `save_document_section` tool with the following parameters:

*   **Filename to create:** `output_s5.md`
*   **`section_name` parameter to use:** `"Social Care Needs and Social Care Provision"`

### Important File Management Rules

*   **One File Only:** Do not create any other files. Your only task is to create this single, consolidated Section 5 file.
*   **Correct Naming:** Use the exact `section_name` provided above in the tool.
*   **Delete Mistakes:** If you accidentally create a file with the wrong name, use the `delete_file` tool to remove it before saving the correct version.

---

## Section 5: Content and Structure Template

The file `output_s5.md` must be structured with the following four sub-headings.

### Social Care Needs

[This should detail the social care needs identified which relate to the child's SEN or disability. You must describe the impact of those needs on the child/young person.
If there are no relevant social care needs identified in the source documents, you must enter: ‘Child or young person has no identified special educational needs in this area’.]

### H1 Social Care Provision

[This section is for any social care provision that is made under the Chronically Sick and Disabled Persons Act 1970. This includes services like:
- Practical assistance in the home (e.g., help with personal care).
- Provision of, or assistance with, recreational and educational facilities.
- Assistance with travel.
- Adaptations to the home.
- Facilitating holidays, meals, or telephone access.

For each provision, specify the details if available in the source documents. If no provisions meet this criteria, enter 'No provision identified'.]

### Other (H2) Social Care Provision

[This section is for any other social care provision reasonably required by the learning difficulties or disabilities which result in the child having SEN. This is provision that does **not** fall under the H1 criteria above.

For each H1 and H2 provision, include the following five elements where available:
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
The outcome should be personal and not expressed from a service perspective. It must be clearly underpinned by the H1/H2 provision linked to it. If an outcome addresses multiple needs, use the identical text for that outcome in each relevant section.]