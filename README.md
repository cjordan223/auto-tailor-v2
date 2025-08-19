# LaTeX Tailor

A deterministic CLI tool that tailors LaTeX résumés and cover letters to job descriptions using LLMs, while preserving document structure and preventing LaTeX corruption.

## ⚠️ CURRENT STATUS: FUNCTIONAL WITH LIMITATIONS

**Working**: PDF generation, LaTeX compilation, character escaping, file structure  
**Issue**: Validation constraints too strict - prevents most job descriptions from processing  
**Quick Fix**: See SITUATION_REPORT.txt for details and immediate solutions needed  

## Quick Start

```bash
# 1. Install the package
pip install -e .

# 2. Check status
tex-tailor status

# 3. Extract editable content (SKIP tex-tailor init - it's broken)
tex-tailor extract --resume "Baseline_Resume/Conner_Jordan_Software_Engineer llm_ready.tex" --cover "Basline_Cover_Letter/Conner_Jordan_Cover_Letter llm_ready.tex"

# 5. Generate edits from job description
tex-tailor propose --jd job_description.txt --provider ollama

# 6. Apply edits safely
tex-tailor apply

# 7. See what changed
tex-tailor diff

# 8. Generate PDFs (optional)
tex-tailor render
```

## How It Works

### 1. **Marker System** 
The tool inserts special comment markers around editable content:

```latex
% === LLM:CHUNK START RESUME.SUMMARY ===
Experienced software engineer with 5 years of development experience...
% === LLM:CHUNK END RESUME.SUMMARY ===

% === LLM:LOCK START RESUME.EXPERIENCE ===
\section{Experience}
\textbf{Senior Developer} at TechCorp (2020-2024)
% === LLM:LOCK END RESUME.EXPERIENCE ===
```

- **CHUNK**: Editable text-only content
- **LOCK**: Protected LaTeX commands and structure

### 2. **Section Reordering**
Automatically reorders résumé sections to: Header → Summary → Work Experience → Technical Skills → Education → Certifications

### 3. **Safe Text Extraction**
Only CHUNK content is sent to LLMs. LaTeX commands stay protected.

### 4. **LLM Integration**
- Sends job description + base text to LLM
- Receives structured JSON edits
- Validates against strict schema and business rules

### 5. **Secure Application**
- Escapes special LaTeX characters (`&`, `%`, `_`, etc.)
- Validates no LaTeX commands in responses
- Enforces edit limits (≤2 changes per section)

## Installation

### Prerequisites
- Python 3.8+
- LaTeX distribution (for PDF rendering)
- LLM provider (Ollama or Gemini)

### Setup
```bash
# Clone and install
git clone <repository>
cd tex_tailor
pip install -e .

# Verify installation
tex-tailor --help
```

## LLM Provider Setup

### Option A: Ollama (Recommended)
```bash
# Install Ollama
curl -fsSL https://ollama.ai/install.sh | sh

# Pull a model
ollama pull qwen2.5:14b-instruct

# Set environment variables (optional)
export OLLAMA_BASE_URL="http://127.0.0.1:11434"
export OLLAMA_MODEL="qwen2.5:14b-instruct"
```

### Option B: Gemini
```bash
# Set API key
export GEMINI_API_KEY="your-api-key-here"
export GEMINI_MODEL="gemini-1.5-pro"  # optional
```

## File Structure

### Required Source Files (Static Reference)
Your baseline LaTeX files should be at:
- `~/Doc/Sandbox_v3/Baseline_Resume/Conner_Jordan_Software_Engineer copy.tex`
- `~/Doc/Sandbox_v3/Basline_Cover_Letter/Conner_Jordan_Cover_Letter copy.tex`

**Note**: These baseline files are static reference points and should not be modified by the application. Any changes to the baseline content would be handled outside this tool's scope.

### Generated Files
```
project/
├── Baseline_Resume/
│   └── Conner_Jordan_Software_Engineer llm_ready.tex  # Marked version
├── Basline_Cover_Letter/
│   └── Conner_Jordan_Cover_Letter llm_ready.tex       # Marked version
└── out/
    ├── base_text.json                                 # Extracted text
    ├── edits.json                                     # LLM proposed edits
    ├── Conner_Jordan_Software_Engineer.tuned.tex     # Final résumé
    ├── Conner_Jordan_Cover_Letter.tuned.tex          # Final cover letter
    └── *.pdf                                          # Generated PDFs
```

## Usage Examples

### Basic Workflow
```bash
# ⚠️ CURRENT WORKAROUND (tex-tailor init is broken):

# 1. Clean output if needed
rm -f out/*

# 2. Extract from existing baseline files
tex-tailor extract --resume "Baseline_Resume/Conner_Jordan_Software_Engineer llm_ready.tex" --cover "Basline_Cover_Letter/Conner_Jordan_Cover_Letter llm_ready.tex"

# 3. Generate edits (currently fails due to strict validation)
tex-tailor propose --jd job_posting.txt --provider gemini

# 4. Apply and render (when validation passes)
tex-tailor apply --resume "Baseline_Resume/..." --cover "Basline_Cover_Letter/..." --edits out/edits.json
tex-tailor render
```

**Note**: See SITUATION_REPORT.txt for validation constraint fixes needed.

### Advanced Usage
```bash
# Use specific model
tex-tailor propose --jd job.txt --provider gemini --model "gemini-1.5-pro"

# Extract to custom location
tex-tailor extract --resume resume.tex --cover cover.tex --out custom/base.json

# Apply custom edits
tex-tailor apply --edits custom/edits.json --resume resume.tex --cover cover.tex

# Export diff report
tex-tailor diff --export diff_report.txt
```

## Edit Rules & Validation

The tool enforces strict limits to prevent over-editing:

### Summary
- ≤ 2 sentence-level changes
- No LaTeX commands allowed

### Skills
- ≤ 2 replacements per skill category
- Must remain comma-separated format
- 8 categories: Programming Languages, Frontend, Backend, Cloud & DevOps, AI & LLM Tools, Automation & Productivity, Security & Operating Systems, Databases

### Cover Letter
- ≤ 1 edit per paragraph
- ≤ 2 paragraphs total edited
- 4 paragraphs exactly

### Forbidden Content
- LaTeX commands (`\textbf`, `\section`, etc.)
- Special characters (`{`, `}`, `%`, `_`, `^`, `~`, etc.)
- New paragraph breaks

## Parsing & Error Resolution

### How the Parser Works

1. **Regex-Based Extraction**: Uses multiline regex to find CHUNK boundaries
2. **Whitespace Preservation**: Maintains original indentation and spacing
3. **Order Independence**: Processes chunks by ID, not position
4. **Error Tolerance**: Skips malformed chunks with warnings

### Common Issues & Solutions

#### Missing Markers
**Problem**: `Warning: Could not find start marker for chunk: RESUME.SUMMARY`
**Solution**: 
```bash
# Re-run initialization
tex-tailor init
# Or manually add missing markers to your .tex files
```

#### LaTeX Compilation Errors
**Problem**: Generated .tex files won't compile
**Solution**:
```bash
# Check validation warnings
tex-tailor apply  # Look for LaTeX validation output

# Common fixes:
# 1. Unmatched braces - check for {/} in edits
# 2. Special characters - tool auto-escapes, but check manual edits
# 3. Missing packages - add to original template
```

#### LLM Response Issues
**Problem**: `Validation failed: JSON schema validation failed`
**Solution**:
```bash
# Tool auto-retries, but if persistent:
# 1. Check LLM provider connection
# 2. Try different model
# 3. Simplify job description

# Test provider:
curl http://127.0.0.1:11434/api/tags  # Ollama
```

#### Edit Limit Violations
**Problem**: `Too many replacements: 5 (max: 2)`
**Solution**: This is intentional - limits prevent over-editing. The tool will reject the response and retry with stricter instructions.

### Debug Mode
```bash
# Enable verbose output
tex-tailor status  # Shows file states
tex-tailor diff    # Shows exactly what changed

# Check extracted content
cat out/base_text.json | jq .

# Validate edits manually
cat out/edits.json | jq .
```

## Chunk IDs Reference

### Résumé Chunks (Editable)
- `RESUME.SUMMARY` - Professional summary paragraph
- `SKILLS.Programming Languages` - Programming languages list
- `SKILLS.Frontend` - Frontend technologies
- `SKILLS.Backend` - Backend technologies  
- `SKILLS.Cloud & DevOps` - Cloud and DevOps tools
- `SKILLS.AI & LLM Tools` - AI and LLM tools
- `SKILLS.Automation & Productivity` - Automation tools
- `SKILLS.Security & Operating Systems` - Security and OS
- `SKILLS.Databases` - Database technologies

### Résumé Locks (Protected)
- `RESUME.PREAMBLE` - Document class and packages
- `RESUME.HEADER` - Name, contact information
- `RESUME.EXPERIENCE` - Work experience section
- `RESUME.EDUCATION` - Education section
- `RESUME.CERTS` - Certifications section

### Cover Letter
- `COVER.P1`, `COVER.P2`, `COVER.P3`, `COVER.P4` - Paragraph content (editable)
- `COVER.PREAMBLE`, `COVER.HEADER`, `COVER.DATE`, `COVER.SALUTATION`, `COVER.SIGNOFF` - Structure (protected)

## Testing

```bash
# Run all tests
python -m unittest discover tex_tailor/tests/ -v

# Test specific functionality
python -m unittest tex_tailor.tests.test_patcher -v
python -m unittest tex_tailor.tests.test_schema -v
python -m unittest tex_tailor.tests.test_extractor -v
```

## Troubleshooting

### Common Commands
```bash
# Reset working files (baselines stay untouched)
rm -rf out/ Baseline_Resume/*llm_ready.tex Basline_Cover_Letter/*llm_ready.tex
tex-tailor init

# Check file status
tex-tailor status

# Test LLM connection
tex-tailor propose --jd <(echo "Software engineer position") --provider ollama

# Validate LaTeX files
pdflatex out/Conner_Jordan_Software_Engineer.tuned.tex
```

### Performance Tips
- Use local Ollama for privacy and speed
- Smaller models (7B) work well for this task
- Job descriptions >2000 words may hit token limits

### Security Notes
- Never commit API keys to version control
- LLM providers may log requests - avoid sensitive information
- Generated files are deterministic (same JD = same edits)
- Baseline files are read-only reference points - application never modifies them