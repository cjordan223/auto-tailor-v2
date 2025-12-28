#!/bin/bash

set -e # Exit immediately if a command exits with a non-zero status.

# --- Configuration ---
# Resolve all paths relative to this script's directory so execution is cwd-agnostic
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
RESUME_FILE="$SCRIPT_DIR/../templates/Baseline_Resume/Conner_Jordan_Software_Engineer llm_ready.tex"
COVER_LETTER_FILE="$SCRIPT_DIR/../templates/Basline_Cover_Letter/Conner_Jordan_Cover_Letter llm_ready.tex"
LOG_FILE="$SCRIPT_DIR/workflow.log"

# --- Functions ---
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

# Convert job description file to absolute path
if [[ "$1" = /* ]]; then
  # Already absolute path
  JD_FILE="$1"
else
  # Convert relative path to absolute
  JD_FILE="$(cd "$(dirname "$1")" && pwd)/$(basename "$1")"
fi

# Start logging - redirect all output to both terminal and log file
exec > >(tee "$LOG_FILE") 2>&1

log_message "Starting clean workflow for job description: $JD_FILE"

# Activate virtual environment (Docker uses /opt/venv)
source /opt/venv/bin/activate

echo "🔄 Processing job description..."
tex-tailor --quiet init
tex-tailor --quiet extract --resume "$RESUME_FILE" --cover "$COVER_LETTER_FILE"
tex-tailor --quiet propose --jd "$JD_FILE"
tex-tailor --quiet apply

echo "📊 Summary of changes:"
tex-tailor --quiet diff

echo "📄 Generating PDFs..."
tex-tailor --quiet render

echo "🎯 Opening PDFs..."
tex-tailor --quiet open

echo "✅ Workflow complete! PDFs are in the 'out' directory."
log_message "Clean workflow completed successfully"