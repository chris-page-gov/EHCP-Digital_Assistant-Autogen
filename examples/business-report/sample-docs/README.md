# Sample Business Report Source Documents

This folder contains example source documents that demonstrate the types of materials MAD can process to generate a comprehensive business report.

## Included Documents

1. **market-research-data.md** - Market analysis and trends data
2. **financial-analysis.md** - Financial metrics and projections
3. **competitor-analysis.pdf.txt** - Competitive landscape analysis (simulated PDF extract)

## Usage

1. Copy these sample documents to your `docs/` folder:
   ```bash
   cp examples/business-report/sample-docs/* docs/
   ```

2. Copy the business report templates to instructions:
   ```bash
   cp examples/business-report/*.yaml examples/business-report/*.md instructions/
   ```

3. Run MAD to generate a comprehensive business report:
   ```bash
   python main.py
   ```

## What MAD Will Generate

From these source documents, MAD will create a structured business report including:
- Executive Summary synthesizing all findings
- Detailed methodology section
- Market analysis with trends and projections
- Competitive landscape assessment
- Financial analysis and metrics
- Strategic recommendations
- Risk assessment
- Implementation roadmap

## Adding Your Own Documents

You can add additional source materials such as:
- Customer survey results
- Internal performance metrics
- Industry reports
- Strategic planning documents
- SWOT analyses
- Product roadmaps

MAD will intelligently incorporate all provided materials into a cohesive business report following professional standards.