# LaTeX Tailor

A deterministic CLI tool that tailors LaTeX résumés and cover letters to job descriptions using LLMs, while preserving document structure and preventing LaTeX corruption.

## ✅ CURRENT STATUS: FULLY FUNCTIONAL

**Working**: Complete end-to-end pipeline, PDF generation, LaTeX compilation, character escaping, file structure  
**Fixed**: Overly conservative LLM prompting that was causing trivial edits instead of meaningful content changes  
**Fixed**: LLM constraint adherence issues resolved with automatic truncation and enhanced prompting  
**Fixed**: Cover letter salutation now dynamically replaces [Company Name] with actual company name  
**Progress**: Added OpenAI provider support, post-processing truncation, and dynamic salutation handling  

## Quick Start

```bash
# 1. Install the package
pip install -e .

# 2. Initialize baseline files with markers
tex-tailor init

# 3. Extract editable content (uses smart defaults)
tex-tailor extract --resume "Baseline_Resume/Conner_Jordan_Software_Engineer llm_ready.tex" --cover "Basline_Cover_Letter/Conner_Jordan_Cover_Letter llm_ready.tex"

# 4. Generate edits from job description (uses smart defaults)
tex-tailor propose --jd job_description.txt --provider gemini

# 5. Apply edits safely (uses smart defaults)
tex-tailor apply

# 6. See what changed (enhanced display)
tex-tailor diff

# 7. Generate PDFs
tex-tailor render

# 8. Check LaTeX quality (optional)
./check_latex.sh

# 9. View workflow log (optional)
tex-tailor log
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
- ChkTeX (for LaTeX linting) - included with TeX Live

### Setup
```bash
# Clone and install
git clone <repository>
cd tex_tailor
pip install -e .

# Verify installation
tex-tailor --help
```

## Configuration Management

Tex-tailor now uses a centralized configuration system that eliminates hardcoded values and makes customization easier.

### Default Configuration
The application ships with sensible defaults:
- **Ollama**: `qwen2.5:14b-instruct` at `http://127.0.0.1:11434`
- **OpenAI**: `gpt-4o-mini` (requires API key)
- **Gemini**: `gemini-1.5-pro` (requires API key)
- **Paths**: `out/` directory for outputs, standard baseline paths

### LLM Provider Setup

#### Option A: Ollama (Recommended)
```bash
# Install Ollama
curl -fsSL https://ollama.ai/install.sh | sh

# Pull a model
ollama pull qwen2.5:14b-instruct

# Optional: Override defaults with environment variables
export OLLAMA_BASE_URL="http://127.0.0.1:11434"  # default
export OLLAMA_MODEL="qwen2.5:14b-instruct"       # default
```

#### Option B: OpenAI (Recommended for Constraint Adherence)
```bash
# Set API key (required)
export OPENAI_API_KEY="your-api-key-here"

# Optional: Override default model
export OPENAI_MODEL="gpt-4"  # default is gpt-4o-mini
```

#### Option C: Gemini
```bash
# Set API key (required)
export GEMINI_API_KEY="your-api-key-here"

# Optional: Override default model  
export GEMINI_MODEL="gemini-1.5-flash"  # default is gemini-1.5-pro
```

### Configuration Details
For advanced configuration options, see [CONFIG.md](CONFIG.md)

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
# 1. Initialize with markers (creates llm_ready.tex files)
tex-tailor init

# 2. Extract editable content (uses default output path)
tex-tailor extract --resume "Baseline_Resume/Conner_Jordan_Software_Engineer llm_ready.tex" --cover "Basline_Cover_Letter/Conner_Jordan_Cover_Letter llm_ready.tex"

# 3. Generate edits from job description (uses default paths)
tex-tailor propose --jd job_posting.txt --provider gemini

# 4. Apply edits and render PDFs (uses default paths)
tex-tailor apply
tex-tailor render

# 5. Check quality (optional)
./check_latex.sh
```

**Status**: All commands working perfectly. Complete end-to-end pipeline functional with enhanced diff display, logging, and centralized configuration management.

### Advanced Usage
```bash
# Use specific model
tex-tailor propose --jd job.txt --provider gemini --model "gemini-1.5-pro"

# Extract to custom location (otherwise uses out/base_text.json)
tex-tailor extract --resume resume.tex --cover cover.tex --out custom/base.json

# Apply custom edits (otherwise uses default paths)
tex-tailor apply --edits custom/edits.json --resume resume.tex --cover cover.tex

# Use completely default paths (recommended)
tex-tailor extract --resume "Baseline_Resume/..." --cover "Basline_Cover_Letter/..."
tex-tailor propose --jd job.txt
tex-tailor apply

# Export diff report
tex-tailor diff --export diff_report.txt

# Run complete workflow with logging
tex-tailor workflow job_description.txt --with-logging

# View latest workflow log
tex-tailor log
```

## Edit Rules & Validation

The tool enforces strict limits to prevent over-editing:

### Summary
- ≤ 5 sentence-level changes (updated from 2 to allow meaningful changes)
- No LaTeX commands allowed

### Skills
- ≤ 8 replacements per skill category (updated from 2 to allow meaningful changes)
- Must remain comma-separated format
- 8 categories: Programming Languages, Frontend, Backend, Cloud & DevOps, AI & LLM Tools, Automation & Productivity, Security & Operating Systems, Databases

### Cover Letter
- ≤ 4 paragraphs total can be edited (updated from 2 for better customization)
- Dynamic salutation that replaces [Company Name] with actual company name
- 4 paragraphs exactly in structure
- Preserves formal business letter format

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
**Problem**: `Too many replacements: 9 (max: 8)` or `'why' too long (95 chars, max: 80)`
**Solution**: 
- **Automatic Truncation**: Long "why" explanations are automatically truncated to fit within limits
- **Enhanced Prompting**: Improved constraint instructions with explicit character counting
- **Provider Options**: Try OpenAI (better constraint adherence) or different models
- **Retry Logic**: Tool auto-retries with detailed feedback on violations

### Enhanced Diff Display
The diff output now features:
- **Color-coded changes**: Red background for deletions, green background for additions
- **Emoji indicators**: Visual cues for different sections (🔧 chunks, 📊 statistics, 📋 summary)
- **Better formatting**: Clear separation between sections with colored headers
- **Improved readability**: White text on colored backgrounds for better contrast

### Workflow Logging
Capture complete workflow output to timestamped log files:
```bash
# Run workflow with logging
tex-tailor workflow job_description.txt --with-logging

# View latest log
tex-tailor log

# Or use the shell script with logging
./run_workflow.sh job_description.txt --log
```

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

### Cover Letter Chunks (Editable)
- `COVER.SALUTATION` - Dynamic greeting (e.g., "Hello [Company Name] team,")
- `COVER.P1`, `COVER.P2`, `COVER.P3`, `COVER.P4` - Paragraph content

### Cover Letter Locks (Protected)
- `COVER.PREAMBLE`, `COVER.HEADER`, `COVER.DATE`, `COVER.SIGNOFF` - Structure elements

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

# Test LLM connection
tex-tailor propose --jd <(echo "Software engineer position") --provider gemini

# Validate LaTeX compilation
tex-tailor render

# Check LaTeX quality with ChkTeX
./check_latex.sh

# View generated PDFs
open out/*.pdf
```

### Performance Tips
- **OpenAI GPT-4o-mini** (recommended): Best constraint adherence, reliable results
- **Gemini 2.0 Flash**: Fast, high-quality results with occasional constraint issues
- **Local Ollama**: Privacy-focused option for sensitive documents
- Smaller models (7B-14B) work well for this task
- Job descriptions >2000 words may hit token limits
- Use ChkTeX for quality assurance before important submissions

## Current Status & Metrics

### ✅ Current Status (January 2025)
- **Pipeline Infrastructure**: ✅ 100% (init → extract → propose → apply → render)
- **PDF Generation**: ✅ Both résumé and cover letter compile successfully  
- **LaTeX Validation**: ✅ Proper character escaping and structure preservation
- **LLM Integration**: ✅ Multiple providers with automatic constraint adherence
- **File Structure**: ✅ All custom LaTeX commands preserved correctly
- **Configuration Management**: ✅ Centralized config system with smart defaults

### Recent Progress & Fixes
- **✅ Critical Fix**: Resolved overly conservative LLM prompting causing trivial edits (and → &)
- **✅ Constraint Updates**: Increased limits from 2→8 skill replacements, 30→80→200 char explanations
- **✅ Improved Prompting**: Added explicit examples and retry feedback for better constraint adherence
- **✅ Constraint Resolution**: Implemented automatic truncation for long explanations
- **✅ Provider Expansion**: Added OpenAI support with better constraint adherence
- **✅ Enhanced UI**: Improved diff display with colors, emojis, and better readability
- **✅ Logging System**: Added workflow logging with timestamped log files
- **✅ Dynamic Salutation**: Cover letter salutation now replaces [Company Name] with actual company name
- **✅ Configuration Management**: Centralized all hardcoded values into configurable system
- **✅ Smart Defaults**: CLI commands now use intelligent defaults, reducing required parameters
- **✅ Core Infrastructure**: Init, extraction, application, and rendering work perfectly

## LaTeX Quality Control

### ChkTeX Integration
The project includes ChkTeX for LaTeX linting and quality control:

```bash
# Check single file
/usr/local/texlive/2025/bin/universal-darwin/chktex --localrc .chktexrc "your-file.tex"

# Check all LaTeX files
./check_latex.sh
```

**Configuration**: The `.chktexrc` file suppresses noise (command termination warnings) while preserving important checks:
- ✅ **Dash length warnings** - reminds you to use `--` for date ranges
- ✅ **Punctuation spacing** - catches typography issues  
- ❌ **Command termination** - suppressed (common in resume templates)

### Security Notes
- Never commit API keys to version control
- LLM providers may log requests - avoid sensitive information
- Generated files are deterministic (same JD = same edits)
- Baseline files are read-only reference points - application never modifies them