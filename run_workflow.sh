#!/bin/bash

set -e # Exit immediately if a command exits with a non-zero status.

# --- Configuration ---
RESUME_FILE="Baseline_Resume/Conner_Jordan_Software_Engineer llm_ready.tex"
COVER_LETTER_FILE="Basline_Cover_Letter/Conner_Jordan_Cover_Letter llm_ready.tex"
# PROVIDER="gemini" # No longer needed, determined dynamically

# --- Functions ---
function print_header() {
  echo ""
  echo "================================================================================"
  echo " $1"
  echo "================================================================================"
}

# --- Main Script ---
if [ -z "$1" ]; then
  echo "Usage: $0 <path_to_job_description_file>"
  exit 1
fi

JD_FILE=$1

print_header "Activating Virtual Environment"
source venv/bin/activate

print_header "Step 1: Initializing tex-tailor"
tex-tailor init

print_header "Step 2: Extracting content from LaTeX files"
tex-tailor extract --resume "$RESUME_FILE" --cover "$COVER_LETTER_FILE"

print_header "Step 3: Proposing edits based on Job Description"

# Determine which provider to use
if [ -n "$GEMINI_API_KEY" ]; then
    PROVIDER="gemini"
    echo "Using Gemini provider."
else
    echo "GEMINI_API_KEY not set, defaulting to Ollama."
    PROVIDER="ollama"
fi

tex-tailor propose --jd "$JD_FILE" --provider "$PROVIDER"

print_header "Step 4: Applying edits"
tex-tailor apply

print_header "Step 5: Checking LaTeX quality"
./check_latex.sh

print_header "Step 6: Showing differences"
tex-tailor diff

print_header "Step 7: Rendering PDFs"
tex-tailor render

print_header "Step 8: Opening PDFs"
tex-tailor open

print_header "Workflow complete! PDFs are in the 'out' directory."
