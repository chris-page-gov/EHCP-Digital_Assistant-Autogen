# Sample EHCP Source Documents

This folder contains example source materials that demonstrate what might be provided to MAD for generating a comprehensive Education, Health and Care Plan (EHCP) document.

## Included Documents

1. **child-assessment.md** - Comprehensive educational assessment
2. **school-report.pdf.txt** - School's SEN support report (simulated PDF extract)
3. **parental-views.md** - Parents' detailed input and concerns
4. **professional-reports.md** - Summary of all professional assessments

## Usage

1. Copy these sample documents to your `docs/` folder:
   ```bash
   cp examples/ehcp/sample-docs/* docs/
   ```

2. Copy the EHCP templates to instructions:
   ```bash
   cp examples/ehcp/*.yaml examples/ehcp/*.md instructions/
   ```

3. Run MAD to generate a complete EHCP document:
   ```bash
   python main.py
   ```

## What MAD Will Generate

From these source materials, MAD will create a comprehensive EHCP including:

### Section A: Views, Interests and Aspirations
- Child's views in their own words
- Parents' views and aspirations
- Professional perspectives

### Section B: Special Educational Needs
- Cognition and Learning
- Communication and Interaction
- Social, Emotional and Mental Health
- Sensory and Physical
- All needs clearly identified from assessments

### Section C: Health Needs
- Medical conditions
- Therapy needs
- Mental health considerations

### Section D: Social Care Needs
- Current social care involvement
- Respite needs
- Family support requirements

### Section E: Outcomes
- SMART outcomes across all areas
- Academic, social, independence, and preparation for adulthood
- Measurable and time-bound

### Section F: Special Educational Provision
- Detailed provision to meet each need
- Staffing ratios and qualifications
- Specific interventions and approaches

### Section G: Health Provision
- Therapy schedules
- Medical monitoring
- Equipment needs

### Section H1: Social Care Provision
- Any social care support required

### Section H2: Other Provision
- Transport arrangements
- Extended school services

### Section I: Placement
- Type of placement required
- Specific school if named

### Section J: Personal Budget
- Details of any personal budget arrangements

### Section K: Advice and Information
- List of all reports considered

## Types of Source Documents You Can Provide

### Educational Evidence
- School reports and assessments
- Previous IEPs or SEN support plans
- Academic progress data
- Examples of child's work
- Attendance records

### Professional Assessments
- Educational Psychology reports
- Speech and Language assessments
- Occupational Therapy reports
- Clinical Psychology/CAMHS reports
- Pediatric assessments
- Specialist teacher assessments

### Family Input
- Parental views forms
- Day-in-the-life accounts
- Video observations (transcribed)
- Communication from child
- Impact statements

### Supporting Evidence
- Previous tribunal decisions
- Private assessment reports
- Charity/support group input
- Advocate reports

## Best Practices for EHCP Evidence

1. **Be Specific** - Include detailed examples of needs and difficulties
2. **Show Impact** - Demonstrate how needs affect learning and daily life
3. **Include Strengths** - Balance with child's abilities and interests
4. **Use Child's Voice** - Include direct quotes where possible
5. **Provide Evidence** - Back up statements with professional assessments

## Important Notes

- All personal information in these samples is fictional
- Real EHCPs must comply with local authority formats
- This is an example only - seek professional advice for actual applications
- EHCPs are legal documents with specific requirements

## Customization

After generating the initial EHCP, you can:
1. Adjust language to match local authority preferences
2. Add specific local services information
3. Include additional professional reports
4. Refine outcomes to be more specific
5. Add placement preferences

MAD will help create a comprehensive, well-evidenced EHCP that clearly describes the child's needs and required provision while maintaining professional standards and legal compliance.