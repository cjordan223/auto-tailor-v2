# Tex-Tailor API Documentation

Complete API reference for the Tex-Tailor Express.js backend server.

## 🌐 Base URL

```
Development: http://localhost:3001
Production: [Your deployment URL]
```

## 📋 API Overview

The Tex-Tailor API provides endpoints for resume customization workflow, file management, and system configuration. All endpoints return JSON responses unless specified otherwise.

### Response Format

**Success Response:**
```json
{
  "success": true,
  "data": { /* response data */ },
  "timestamp": "2025-01-20T10:30:00.000Z"
}
```

**Error Response:**
```json
{
  "success": false,
  "error": "Error description",
  "code": "ERROR_CODE",
  "timestamp": "2025-01-20T10:30:00.000Z"
}
```

## 🔄 Core Processing Endpoints

### Start Resume Processing

**Endpoint:** `POST /api/process`  
**Description:** Initiates the resume customization workflow  
**Content-Type:** `multipart/form-data`

**Request Body:**
```javascript
FormData {
  jobDescription: File,     // Job description file (.txt, .pdf, .doc, .docx)
  provider: String,         // AI provider: 'gemini', 'openai', or 'ollama'
  model: String            // Optional: specific model name
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "jobId": "uuid-string",
    "status": "processing",
    "message": "Processing started successfully"
  }
}
```

**Example:**
```javascript
const formData = new FormData()
formData.append('jobDescription', jobFile)
formData.append('provider', 'gemini')
formData.append('model', 'gemini-1.5-pro')

const response = await fetch('/api/process', {
  method: 'POST',
  body: formData
})
```

### Check Processing Status

**Endpoint:** `GET /api/status/:jobId`  
**Description:** Retrieve real-time processing status and progress  

**Parameters:**
- `jobId` (path): UUID of the processing job

**Response:**
```json
{
  "status": "processing|completed|error",
  "progress": 75,
  "step": "Applying AI edits to LaTeX templates...",
  "detail": "Modified 3 resume sections and 4 cover letter paragraphs",
  "provider": "gemini",
  "timestamp": "2025-01-20T10:35:00.000Z"
}
```

**Status Values:**
- `processing`: Job in progress
- `completed`: Successfully finished
- `error`: Processing failed

**Example:**
```javascript
const status = await fetch(`/api/status/${jobId}`)
const data = await status.json()
console.log(`Progress: ${data.progress}% - ${data.step}`)
```

### Get Processing Results

**Endpoint:** `GET /api/results/:jobId`  
**Description:** Retrieve complete results with resilient fallback system

**Parameters:**
- `jobId` (path): UUID of the completed job

**Response:**
```json
{
  "jobId": "uuid-string",
  "status": "completed",
  "progress": 100,
  "step": "Processing complete!",
  "files": {
    "resume": "/api/download/uuid/resume",
    "coverLetter": "/api/download/uuid/cover-letter",
    "edits": "/api/download/uuid/edits"
  },
  "suggestedAdditions": [
    {
      "term": "Flask",
      "why": "Required by job description"
    }
  ],
  "reviewData": {
    "overview": "Successfully analyzed and customized your resume with 3 modifications...",
    "statistics": {
      "total_chunks_modified": 3,
      "skills_sections_updated": 8,
      "cover_letter_paragraphs": 4,
      "suggested_additions": 3
    }
  },
  "skillsChanges": {
    "Programming Languages": {
      "original": "Python, Java",
      "new": "Python, Java, Go",
      "removed": [],
      "added": ["Go"]
    }
  },
  "createdAt": "2025-01-20T10:40:00.000Z"
}
```

**Resilient Fallback:** This endpoint implements a multi-strategy fallback system:
1. **Strategy 1**: Attempts AI provider auto-detection
2. **Strategy 2**: Falls back to direct `edits.json` parsing
3. **Strategy 3**: Provides minimal default data

## 📁 File Management Endpoints

### Upload Files

**Endpoint:** `POST /api/upload`  
**Description:** Upload individual files (used internally by processing)  
**Content-Type:** `multipart/form-data`

**Request Body:**
```javascript
FormData {
  file: File,              // File to upload
  type: String            // File type identifier
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "filename": "uploaded-file.txt",
    "path": "/temp/uuid/uploaded-file.txt",
    "size": 1024
  }
}
```

### Download Generated Files

**Endpoint:** `GET /api/download/:jobId/:fileType`  
**Description:** Download generated files with proper content types

**Parameters:**
- `jobId` (path): UUID of the job
- `fileType` (path): Type of file to download

**Supported File Types:**
- `resume`: Resume PDF
- `cover-letter`: Cover letter PDF  
- `resume-tex`: Resume LaTeX source
- `cover-letter-tex`: Cover letter LaTeX source
- `edits`: Edit details JSON

**Response:** Binary file download with appropriate headers

**Example:**
```javascript
// Download resume PDF
window.open(`/api/download/${jobId}/resume`)

// Download LaTeX source
const response = await fetch(`/api/download/${jobId}/resume-tex`)
const latexContent = await response.text()
```

### View PDF Files Inline

**Endpoint:** `GET /api/view/:jobId/:fileType`  
**Description:** View PDF files inline in browser (for embedding)

**Parameters:**
- `jobId` (path): UUID of the job
- `fileType` (path): `resume` or `cover-letter`

**Response:** PDF file with `application/pdf` content type and inline disposition

**Headers Set:**
```
Content-Type: application/pdf
Content-Disposition: inline; filename="document.pdf"
Cache-Control: no-cache
X-Frame-Options: SAMEORIGIN
X-Content-Type-Options: nosniff
```

**Example Usage in HTML:**
```html
<iframe src="/api/view/uuid/resume" width="100%" height="600px"></iframe>
```

### View LaTeX Source Files

**Endpoint:** `GET /api/view/:jobId/:fileType/tex`  
**Description:** View LaTeX source files as plain text

**Parameters:**
- `jobId` (path): UUID of the job
- `fileType` (path): `resume` or `cover-letter`

**Response:** Plain text LaTeX source code

**Headers Set:**
```
Content-Type: text/plain; charset=utf-8
Content-Disposition: inline; filename="document.tex"
Cache-Control: no-cache
X-Content-Type-Options: nosniff
```

**Example:**
```javascript
const response = await fetch(`/api/view/${jobId}/resume/tex`)
const latexSource = await response.text()
console.log('LaTeX source:', latexSource)
```

## ⚙️ Configuration Endpoints

### Get Available Providers

**Endpoint:** `GET /api/providers`  
**Description:** List available AI providers and their configuration

**Response:**
```json
{
  "success": true,
  "data": {
    "providers": [
      {
        "name": "gemini",
        "displayName": "Google Gemini",
        "available": true,
        "defaultModel": "gemini-1.5-flash",
        "models": ["gemini-1.5-flash", "gemini-1.5-pro"]
      },
      {
        "name": "openai", 
        "displayName": "OpenAI",
        "available": false,
        "defaultModel": "gpt-4o-mini",
        "models": ["gpt-4o-mini", "gpt-4o"]
      },
      {
        "name": "ollama",
        "displayName": "Ollama (Local)",
        "available": true,
        "defaultModel": "qwen2.5:14b-instruct",
        "models": ["qwen2.5:14b-instruct", "llama3:8b"]
      }
    ],
    "default": "gemini"
  }
}
```

### System Health Check

**Endpoint:** `GET /api/health`  
**Description:** Check system health and availability

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2025-01-20T10:45:00.000Z",
  "service": "tex-tailor-api"
}
```

**HTTP Status Codes:**
- `200 OK`: System healthy
- `503 Service Unavailable`: System issues detected

## ❌ Error Handling

### Error Response Format

All API errors follow a consistent format:

```json
{
  "success": false,
  "error": "Human-readable error message",
  "code": "ERROR_CODE", 
  "details": {
    "field": "Additional error context"
  },
  "timestamp": "2025-01-20T10:45:00.000Z"
}
```

### Common Error Codes

#### Processing Errors
- `PROCESSING_FAILED`: General processing failure
- `AI_PROVIDER_ERROR`: AI provider unavailable or error
- `LATEX_COMPILATION_ERROR`: LaTeX compilation failed
- `INVALID_JOB_DESCRIPTION`: Job description format invalid

#### File Errors  
- `FILE_NOT_FOUND`: Requested file doesn't exist
- `FILE_UPLOAD_ERROR`: File upload failed
- `FILE_TOO_LARGE`: File exceeds size limit
- `INVALID_FILE_TYPE`: Unsupported file format

#### Configuration Errors
- `INVALID_PROVIDER`: Unknown AI provider specified
- `MISSING_API_KEY`: Required API key not configured
- `INVALID_MODEL`: Unknown model specified

#### System Errors
- `SYSTEM_ERROR`: Internal server error
- `TIMEOUT_ERROR`: Operation timed out
- `INSUFFICIENT_RESOURCES`: System resource exhaustion

### Error Handling Examples

```javascript
try {
  const response = await fetch('/api/process', {
    method: 'POST',
    body: formData
  })
  
  const data = await response.json()
  
  if (!data.success) {
    switch (data.code) {
      case 'AI_PROVIDER_ERROR':
        console.error('AI provider unavailable:', data.error)
        // Handle provider fallback
        break
      case 'FILE_TOO_LARGE':
        console.error('File too large:', data.details)
        // Show file size warning
        break
      default:
        console.error('Processing error:', data.error)
    }
    return
  }
  
  // Handle success
  console.log('Job started:', data.data.jobId)
  
} catch (error) {
  console.error('Network error:', error)
}
```

## 🔐 Authentication & Security

### Current Implementation
- **No Authentication Required**: Currently operates without user authentication
- **CORS Enabled**: Configured for frontend origin
- **File Validation**: Strict validation of uploaded files
- **Input Sanitization**: All inputs sanitized and validated

### Security Headers
All responses include appropriate security headers:
```
X-Frame-Options: SAMEORIGIN
X-Content-Type-Options: nosniff
Cache-Control: no-cache (for sensitive endpoints)
```

### Rate Limiting
- **File Upload**: Limited by file size and format validation
- **Processing**: One job per session to prevent resource abuse
- **API Calls**: Standard Express.js rate limiting

## 📊 Performance & Monitoring

### Response Times
- **File Upload**: < 1 second for typical job descriptions
- **Processing Status**: < 100ms for status checks
- **File Download**: Varies by file size, typically < 5 seconds
- **Complete Workflow**: 30-120 seconds depending on AI provider

### Monitoring Endpoints
- `GET /api/health`: System health check
- Processing logs: Real-time via status endpoint
- Error tracking: Structured error responses

### Caching Strategy
- **Static Files**: Served with appropriate cache headers
- **Dynamic Content**: No caching to ensure real-time updates
- **Generated Files**: Temporary storage with automatic cleanup

## 🚀 Usage Examples

### Complete Workflow Example

```javascript
class TexTailorAPI {
  constructor(baseUrl = 'http://localhost:3001') {
    this.baseUrl = baseUrl
  }
  
  async processResume(jobDescriptionFile, provider = 'gemini') {
    // 1. Start processing
    const formData = new FormData()
    formData.append('jobDescription', jobDescriptionFile)
    formData.append('provider', provider)
    
    const processResponse = await fetch(`${this.baseUrl}/api/process`, {
      method: 'POST',
      body: formData
    })
    
    const processData = await processResponse.json()
    if (!processData.success) throw new Error(processData.error)
    
    const jobId = processData.data.jobId
    console.log('Processing started:', jobId)
    
    // 2. Poll for completion
    while (true) {
      const statusResponse = await fetch(`${this.baseUrl}/api/status/${jobId}`)
      const statusData = await statusResponse.json()
      
      console.log(`Progress: ${statusData.progress}% - ${statusData.step}`)
      
      if (statusData.status === 'completed') break
      if (statusData.status === 'error') throw new Error('Processing failed')
      
      await new Promise(resolve => setTimeout(resolve, 2000)) // Wait 2 seconds
    }
    
    // 3. Get results
    const resultsResponse = await fetch(`${this.baseUrl}/api/results/${jobId}`)
    const results = await resultsResponse.json()
    
    console.log('Processing complete:', results)
    return { jobId, results }
  }
  
  async downloadFiles(jobId) {
    const fileTypes = ['resume', 'cover-letter', 'resume-tex', 'cover-letter-tex']
    const downloads = {}
    
    for (const fileType of fileTypes) {
      try {
        const response = await fetch(`${this.baseUrl}/api/download/${jobId}/${fileType}`)
        if (response.ok) {
          downloads[fileType] = response.blob()
        }
      } catch (error) {
        console.warn(`Failed to download ${fileType}:`, error)
      }
    }
    
    return downloads
  }
}

// Usage
const api = new TexTailorAPI()

document.getElementById('process').addEventListener('click', async () => {
  const fileInput = document.getElementById('jobDescription')
  const file = fileInput.files[0]
  
  if (!file) {
    alert('Please select a job description file')
    return
  }
  
  try {
    const { jobId, results } = await api.processResume(file, 'gemini')
    console.log('Success! Job ID:', jobId)
    
    // Download all files
    const downloads = await api.downloadFiles(jobId)
    console.log('Downloads ready:', Object.keys(downloads))
    
  } catch (error) {
    console.error('Error:', error.message)
    alert('Processing failed: ' + error.message)
  }
})
```

This comprehensive API documentation covers all endpoints, error handling, security considerations, and practical usage examples for the Tex-Tailor system.