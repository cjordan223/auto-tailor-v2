# Workflow Logging System

## Overview

The Tex-Tailor application now features an enhanced logging system that provides clean, filtered workflow logs for individual runs while reducing noise from server operations.

## Key Features

### 1. Individual Run Logging
- Each workflow run is saved to a temporary file (`temp_workflow.txt`)
- The file is cleared and overwritten on each new run
- Provides a clean view of just the current workflow execution

### 2. Noise Filtering
The system automatically filters out noise from:
- Health checks (`GET /health`)
- Status checks (`GET /api/status`)
- Provider validation (`GET /api/providers`)
- Log retrieval requests (`GET /api/process/log`)
- CORS preflight requests (`OPTIONS`)
- Static file requests (CSS, JS, images)
- API validation requests

### 3. Workflow Output Detection
Only meaningful workflow output is captured:
- Step indicators (`🔄`, `✅`, `❌`)
- Progress messages (`📋`, `🔍`, `🔧`, `📊`, `🎉`)
- File operations (`Created:`, `Extracted`, `Saved`, `Applied`)
- Processing steps (`Step`, `Workflow`, `Processing`)
- Error messages (`Error`, `Failed`, `Warning`)

## Implementation Details

### Files Modified

1. **`frontend/server/utils/workflowLogger.js`** - New workflow logger utility
2. **`frontend/server/routes/process.js`** - Updated to use new logger
3. **`frontend/server/middleware/requestLogger.js`** - Added noise filtering
4. **`frontend/src/views/Settings.vue`** - Updated UI labels

### Workflow Logger Class

The `WorkflowLogger` class provides:

```javascript
// Start a new workflow run
await workflowLogger.startWorkflow(jobId)

// Write workflow log entries
await workflowLogger.writeWorkflowLog(jobId, message, type)

// Filter and log server output
await workflowLogger.logServerOutput(jobId, output, isError)

// Get current temp log
const log = await workflowLogger.getTempLog()

// Clear temp log
await workflowLogger.clearTempLog()

// End workflow run
await workflowLogger.endWorkflow()
```

### Log File Structure

The temporary log file (`temp_workflow.txt`) contains:

```
=== Workflow Run Started ===
Job ID: [job-id]
Started: [timestamp]
==================================================

[INFO] Workflow started - Provider: gemini, Model: gemini-1.5-flash, Personality: career_savvy_colleague
[WORKFLOW] ⚙️ Step 1: Initializing...
[WORKFLOW] Created: templates/Baseline_Resume/Conner_Jordan_Software_Engineer llm_ready.tex
[WORKFLOW] ✔ Initialization complete
[WORKFLOW] ⚙️ Step 2: Extracting content...
[WORKFLOW] Extracted base text to: out/base_text.json
[WORKFLOW] ✔ Text extraction complete
...

==================================================
=== Workflow Run Completed ===
Job ID: [job-id]
Completed: [timestamp]
```

## Usage

### Frontend
The Settings page now shows "Current Run Log" instead of "Workflow Log", displaying only the current workflow execution.

### API Endpoints
- `GET /api/process/log` - Returns the current temporary log
- `DELETE /api/process/log` - Clears the temporary log

### Server Terminal
The server terminal now only logs meaningful requests, filtering out:
- Health checks
- Status checks
- Static file requests
- CORS preflight requests

## Benefits

1. **Cleaner Debugging**: Each run provides a focused view of just that workflow
2. **Reduced Noise**: Server logs are filtered to show only relevant information
3. **Better UX**: Users see only meaningful workflow progress
4. **Easier Troubleshooting**: Clear separation between workflow output and server noise

## Configuration

No additional configuration is required. The system automatically:
- Creates the logs directory if it doesn't exist
- Filters noise based on predefined patterns
- Manages temporary log files
- Integrates with existing workflow processes
