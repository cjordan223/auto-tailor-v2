#!/bin/bash

# Silent Tex-Tailor Workflow Script
# This script automates the tex-tailor workflow for Raycast command usage.
# It finds the latest job description, runs the workflow silently,
# and opens the frontend application.

set -e  # Exit on any error

echo "🚀 Starting silent tex-tailor workflow..."

# Change to the script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Activate virtual environment
if [ ! -d "venv" ]; then
    echo "❌ Error: Python virtual environment not found at venv/"
    exit 1
fi

source venv/bin/activate

# Find the most recent job description file in the jd-repo directory
JD_REPO_DIR="$SCRIPT_DIR/jd-repo"
if [ ! -d "$JD_REPO_DIR" ]; then
    echo "❌ Error: jd-repo directory not found at $JD_REPO_DIR"
    deactivate
    exit 1
fi

JD_FILE=$(ls -t "$JD_REPO_DIR"/* 2>/dev/null | head -1)

if [ -z "$JD_FILE" ]; then
    echo "❌ Error: No job description file found in jd-repo."
    deactivate
    exit 1
fi

echo "📄 Using job description: $(basename "$JD_FILE")"

# Check if frontend server is running
if ! curl -s http://localhost:3000 > /dev/null 2>&1; then
    echo "⚠️  Warning: Frontend server doesn't appear to be running on localhost:3000"
    echo "   Make sure to start it with: npm run dev"
fi

# Run the tex-tailor workflow via frontend API
echo "⚙️  Running tex-tailor workflow via API..."

# Submit job to frontend API and capture the response
API_RESPONSE=$(curl -s -X POST http://localhost:3001/api/process \
    -F "jobDescription=@$JD_FILE" \
    -H "Content-Type: multipart/form-data")

if [ $? -eq 0 ]; then
    # Extract job ID from the response using basic text processing
    JOB_ID=$(echo "$API_RESPONSE" | grep -o '"jobId":"[^"]*"' | cut -d'"' -f4)
    
    if [ -n "$JOB_ID" ]; then
        echo "✅ Workflow submitted successfully (Job ID: $JOB_ID)"
        
        # Wait for the workflow to complete
        echo "⏳ Waiting for workflow to complete..."
        while true; do
            STATUS_RESPONSE=$(curl -s "http://localhost:3001/api/status/$JOB_ID")
            STATUS=$(echo "$STATUS_RESPONSE" | grep -o '"status":"[^"]*"' | cut -d'"' -f4)
            
            if [ "$STATUS" = "completed" ]; then
                echo "✅ Workflow completed successfully!"
                break
            elif [ "$STATUS" = "failed" ] || [ "$STATUS" = "error" ]; then
                echo "❌ Workflow failed with status: $STATUS"
                deactivate
                exit 1
            fi
            
            sleep 2
        done
        
        RESULTS_URL="http://localhost:3000/results/$JOB_ID"
        echo "🌐 Opening results page: $RESULTS_URL"
        open "$RESULTS_URL"
    else
        echo "❌ Could not extract job ID from API response"
        deactivate
        exit 1
    fi
else
    echo "❌ Failed to submit workflow to API"
    deactivate
    exit 1
fi

# Deactivate virtual environment
deactivate

echo "🎉 Silent workflow completed successfully!"