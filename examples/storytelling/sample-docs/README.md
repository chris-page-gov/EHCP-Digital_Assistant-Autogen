# Sample Storytelling Source Documents

This folder contains example source materials that demonstrate what a writer might provide to MAD for developing a complete story bible and development documents.

## Included Documents

1. **character-notes.md** - Detailed character profiles and development notes
2. **plot-outline.md** - Three-act structure with key plot points
3. **world-building.md** - Setting, technology, and universe rules
4. **dialogue-samples.md** - Key scenes and character voice examples

## Usage

1. Copy these sample documents to your `docs/` folder:
   ```bash
   cp examples/storytelling/sample-docs/* docs/
   ```

2. Copy the storytelling templates to instructions:
   ```bash
   cp examples/storytelling/*.yaml examples/storytelling/*.md instructions/
   ```

3. Run MAD to generate complete story development documents:
   ```bash
   python main.py
   ```

## What MAD Will Generate

From these source materials, MAD will create:
- **Story Premise** - Polished logline and elevator pitch
- **Character Profiles** - Fully developed character sheets with arcs
- **Plot Structure** - Detailed scene-by-scene breakdown
- **World Building Guide** - Comprehensive setting bible
- **Theme Analysis** - Deeper exploration of story themes
- **Dialogue Style Guide** - Character voice consistency
- **Opening Chapter** - Polished first chapter
- **Scene Outlines** - Key scenes fully planned
- **Research Notes** - Organized background information
- **Series Potential** - Franchise possibilities
- **Marketing Angles** - Genre positioning and comp titles

## Creating Your Own Story Materials

You can provide various types of source documents:

### Character Development
- Character sketches and backstories
- Relationship maps
- Voice/dialogue samples
- Visual references or mood boards

### Plot Development  
- Beat sheets or outlines
- Scene ideas and fragments
- Conflict charts
- Timeline of events

### World Building
- Setting descriptions
- Technology/magic system notes  
- Historical background
- Maps or location descriptions
- Cultural details

### Themes and Tone
- Thematic statements
- Mood/atmosphere notes
- Genre conventions to follow/subvert
- Comparable works

### Research Materials
- Scientific articles (for sci-fi)
- Historical documents (for historical fiction)
- Location research
- Technical specifications

## Tips for Best Results

1. **Be Specific** - The more detail you provide, the richer the output
2. **Show Voice** - Include dialogue samples to establish character voices
3. **World Rules** - Clearly establish what's possible in your world
4. **Conflicts** - Highlight internal and external conflicts
5. **Stakes** - Make clear what characters stand to gain/lose

## File Formats

MAD can read various formats:
- Markdown (.md)
- Plain text (.txt)
- PDF extracts (.pdf.txt)
- Even rough notes and fragments

The AI will synthesize all materials into cohesive, professional story development documents ready for drafting your novel, screenplay, or series.