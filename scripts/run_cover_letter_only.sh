#!/bin/bash

# Isolated Cover Letter Regeneration Script
# This script regenerates ONLY the cover letter without touching the resume

set -e  # Exit on any error

TEMP_DIR="$1"
JOB_DESC_FILE="$TEMP_DIR/job-description.txt"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

if [ ! -f "$JOB_DESC_FILE" ]; then
    echo "❌ Job description file not found: $JOB_DESC_FILE"
    exit 1
fi

echo "🔄 Starting isolated cover letter regeneration..."
echo "📁 Working directory: $TEMP_DIR"
echo "🔧 Provider: ${PROVIDER:-gemini}, Model: ${MODEL:-gemini-2.5-flash-lite}"

# Activate virtual environment from project root
source "$SCRIPT_DIR/../venv/bin/activate"

# Navigate to project root for tex-tailor execution
cd "$SCRIPT_DIR/.."

# Set up tex-tailor environment variables
export TEX_TAILOR_PROVIDER="${PROVIDER:-gemini}"
export TEX_TAILOR_MODEL="${MODEL:-gemini-2.5-flash-lite}"
export TEX_TAILOR_PERSONALITY="${PERSONALITY:-career_savvy_colleague}"

echo "🔄 Step 1: Initializing..."
tex-tailor --quiet init

echo "🔄 Step 2: Extracting existing content..."
# Use original baseline files for structure but preserve any existing resume edits
RESUME_FILE="templates/Baseline_Resume/Conner_Jordan_Software_Engineer llm_ready.tex"
COVER_LETTER_FILE="templates/Basline_Cover_Letter/Conner_Jordan_Cover_Letter llm_ready.tex"

# Check if we have an existing tuned resume to preserve
if [ -f "$TEMP_DIR/Conner_Jordan_Software_Engineer.tuned.tex" ]; then
    # Copy existing resume to preserve it
    cp "$TEMP_DIR/Conner_Jordan_Software_Engineer.tuned.tex" out/Conner_Jordan_Software_Engineer.tuned.tex
    echo "✅ Preserved existing resume edits"
else
    # Extract baseline resume
    tex-tailor --quiet extract --resume "$RESUME_FILE" --cover "$COVER_LETTER_FILE"
fi

# Always extract fresh cover letter baseline for regeneration
tex-tailor --quiet extract --cover "$COVER_LETTER_FILE"

echo "🔄 Step 3: Proposing new cover letter edits..."
tex-tailor --quiet propose --jd "$JOB_DESC_FILE" --provider "$TEX_TAILOR_PROVIDER" --model "$TEX_TAILOR_MODEL" --personality "$TEX_TAILOR_PERSONALITY"

echo "🔄 Step 4: Applying cover letter edits only..."
# Apply edits but preserve existing resume
tex-tailor --quiet apply

echo "🔄 Step 5: Rendering new cover letter PDF..."
tex-tailor --quiet render

echo "✅ Cover letter regeneration completed!"
echo "📄 New cover letter: out/Conner_Jordan_Cover_Letter.tuned.pdf"