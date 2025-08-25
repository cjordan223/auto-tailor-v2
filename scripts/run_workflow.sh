#!/bin/bash

set -e # Exit immediately if a command exits with a non-zero status.

# --- Configuration ---
RESUME_FILE="templates/Baseline_Resume/Conner_Jordan_Software_Engineer llm_ready.tex"
COVER_LETTER_FILE="templates/Basline_Cover_Letter/Conner_Jordan_Cover_Letter llm_ready.tex"
LOG_FILE="workflow.log"

# --- Functions ---
function print_header() {
  echo ""
  echo "================================================================================"
  echo " $1"
  echo "================================================================================"
}

function log_message() {
  echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1"
}

# --- Main Script ---
if [ -z "$1" ]; then
  echo "Usage: $0 <path_to_job_description_file>"
  echo ""
  echo "Note: All output is automatically logged to workflow.log"
  exit 1
fi

JD_FILE=$1

# Start logging - redirect all output to both terminal and log file
exec > >(tee "$LOG_FILE") 2>&1

log_message "Starting workflow for job description: $JD_FILE"

print_header "Activating Virtual Environment"
source venv/bin/activate

print_header "Step 1: Initializing tex-tailor"
tex-tailor init

print_header "Step 2: Extracting content from LaTeX files"
tex-tailor extract --resume "$RESUME_FILE" --cover "$COVER_LETTER_FILE"

print_header "Step 3: Proposing edits based on Job Description"
tex-tailor propose --jd "$JD_FILE"

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
log_message "Workflow completed successfully"
