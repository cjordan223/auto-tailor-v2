#!/bin/bash

# ChkTeX LaTeX checker script with custom configuration
CHKTEX="/usr/local/texlive/2025/bin/universal-darwin/chktex"
CONFIG_FILE=".chktexrc"

echo "Running ChkTeX on all LaTeX files..."
echo "Using custom configuration: $CONFIG_FILE"
echo "========================================="

# Find all .tex files recursively
find . -name "*.tex" -type f | while read -r file; do
    echo ""
    echo "Checking: $file"
    echo "----------------------------------------"
    if [[ -f "$CONFIG_FILE" ]]; then
        $CHKTEX --localrc "$CONFIG_FILE" "$file" || true
    else
        $CHKTEX "$file" || true
    fi
done

# Always exit successfully - warnings are informational, not failures
echo ""
echo "ChkTeX quality check completed."
exit 0