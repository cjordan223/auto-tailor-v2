# Tex-Tailor System Architecture

Comprehensive overview of the Tex-Tailor AI-powered resume customization system architecture, components, and data flow.

## 🏗️ System Overview

```
┌─────────────────┐    HTTP/API    ┌─────────────────┐    Python CLI    ┌─────────────────┐
│                 │───────────────▶│                 │──────────────────▶│                 │
│   Vue.js        │                │   Express.js    │                   │   Python CLI    │
│   Frontend      │                │   Backend       │                   │   + AI Models   │
│   (Port 3000)   │◀───────────────│   (Port 3001)   │◀──────────────────│                 │
└─────────────────┘    JSON/Files  └─────────────────┘    Generated     └─────────────────┘
                                                          Files
```

### Technology Stack

**Frontend (Vue.js SPA)**
- Vue 3 with Composition API
- Vite for development and building
- Tailwind CSS for styling
- Vue Router for navigation

**Backend (Express.js API)**
- Node.js with Express.js
- ES modules
- Multer for file handling
- Child process spawning for Python CLI

**Processing Engine (Python CLI)**
- Python 3.8+ with click CLI framework
- LLM integrations (OpenAI, Gemini, Ollama)
- LaTeX processing and validation
- JSON schema validation

## 📁 Directory Structure

```
tex-tailor/
├── frontend/                          # Vue.js web application
│   ├── src/
│   │   ├── components/               # Reusable Vue components
│   │   │   ├── LaTeXViewer.vue      # LaTeX source viewer with syntax highlighting
│   │   │   ├── PDFViewer.vue        # PDF preview component
│   │   │   ├── ProcessingStatus.vue # Real-time status updates
│   │   │   └── ...
│   │   ├── views/                   # Page components
│   │   │   ├── Home.vue             # Upload and processing page
│   │   │   ├── Results.vue          # Side-by-side LaTeX/PDF results
│   │   │   └── Settings.vue         # Configuration page
│   │   └── composables/             # Reusable logic
│   │       └── useAPI.js            # API communication layer
│   ├── server/                      # Express.js backend
│   │   ├── routes/                  # API endpoints
│   │   │   ├── process.js           # Main processing workflow
│   │   │   ├── view.js              # File viewing (PDF/LaTeX)
│   │   │   ├── download.js          # File downloads
│   │   │   └── ...
│   │   ├── middleware/              # Express middleware
│   │   └── index.js                 # Server entry point
│   └── temp/                        # Temporary file storage
├── tex_tailor/                      # Python CLI package
│   ├── cli.py                       # Command-line interface
│   ├── proposer.py                  # AI prompt engineering and LLM calls
│   ├── patcher.py                   # LaTeX file patching
│   ├── extractor.py                 # Content extraction from LaTeX
│   ├── schema.py                    # JSON validation schemas
│   └── config.py                    # Configuration management
├── Baseline_Resume/                 # LaTeX resume template
│   └── Conner_Jordan_Software_Engineer llm_ready.tex
├── Basline_Cover_Letter/           # LaTeX cover letter template
│   └── Conner_Jordan_Cover_Letter llm_ready.tex
└── out/                            # Generated output files
    ├── *.pdf                       # Generated PDFs
    ├── *.tex                       # Generated LaTeX files
    ├── base_text.json              # Extracted content
    └── edits.json                  # AI-generated edits
```

## 🔄 Data Flow & Processing Pipeline

### 1. User Input & Upload
```
User → Vue.js Frontend → FileUpload Component → Express.js API → Temp Storage
```

**Components Involved:**
- `FileUpload.vue`: Drag & drop interface
- `POST /api/upload`: File upload endpoint
- Multer middleware: File handling and validation

### 2. Processing Workflow
```
Express.js → Python CLI Spawn → AI Provider → LaTeX Generation → PDF Compilation
```

**Detailed Steps:**
1. **Express.js Backend** (`routes/process.js`):
   - Validates uploaded job description
   - Spawns Python CLI subprocess
   - Streams real-time output back to frontend

2. **Python CLI Workflow** (`tex_tailor/cli.py`):
   ```bash
   extract → propose → apply → render
   ```

3. **Content Extraction** (`extractor.py`):
   - Parses LaTeX templates with LLM markers
   - Extracts editable chunks (RESUME.SUMMARY, SKILLS.*, COVER.*)
   - Preserves LaTeX structure and commands

4. **AI Processing** (`proposer.py`):
   - Sends job description + extracted content to LLM
   - Uses enhanced prompts for compelling summaries and conversational cover letters
   - Validates JSON responses against strict schemas

5. **Content Application** (`patcher.py`):
   - Applies AI edits to LaTeX templates
   - Escapes special LaTeX characters
   - Preserves document structure and formatting

6. **PDF Generation** (LaTeX compiler):
   - Compiles modified LaTeX files to PDFs
   - Handles compilation errors and dependencies

### 3. Results Display
```
Generated Files → Express.js Endpoints → Vue.js Results Page → LaTeX/PDF Viewers
```

**Components Involved:**
- `Results.vue`: Main results page with two-column layout
- `LaTeXViewer.vue`: Syntax-highlighted source code viewer
- `PDFViewer.vue`: Embedded PDF preview
- API endpoints: `/api/view/:jobId/:fileType` and `/api/view/:jobId/:fileType/tex`

## 🔍 Key Components Deep Dive

### LaTeX Source Code Viewer

**Location**: `frontend/src/components/LaTeXViewer.vue`

**Features**:
- Real-time syntax highlighting for LaTeX
- Line numbers for code reference
- One-click copy to clipboard functionality
- Responsive design adapting to screen size
- Error handling for missing files

**API Integration**:
- Fetches LaTeX source via `GET /api/view/:jobId/:fileType/tex`
- Displays loading states and error messages
- Handles clipboard operations with visual feedback

**Syntax Highlighting Rules**:
```javascript
// Commands: \textbf, \section, etc.
.replace(/\\([a-zA-Z]+)/g, '<span class="latex-command">\\$1</span>')

// Environments: \begin{document}, \end{itemize}
.replace(/\\(begin|end)\{([^}]+)\}/g, '<span class="latex-environment">\\$1{<span class="latex-env-name">$2</span>}</span>')

// Comments: % This is a comment
.replace(/(%.*$)/gm, '<span class="latex-comment">$1</span>')

// Math mode: $equation$
.replace(/\$([^$]+)\$/g, '<span class="latex-math">$$1$</span>')
```

### Resilient API Fallback System

**Location**: `frontend/server/index.js` (results endpoint)

**Multi-Strategy Approach**:

1. **Strategy 1: Auto-Detect Provider**
   ```javascript
   const reviewResponse = await fetch(`http://localhost:${PORT}/api/review?format=json`)
   ```
   - Attempts to use any available AI provider
   - No hard dependency on specific provider

2. **Strategy 2: Direct File Fallback**
   ```javascript
   const editsRaw = await fs.readFile(editsPath, 'utf8')
   const edits = JSON.parse(editsRaw)
   suggestedAdditions = edits.suggested_additions || []
   ```
   - Reads directly from `edits.json` if AI unavailable
   - Computes statistics matching Python CLI logic

3. **Strategy 3: Minimal Default**
   ```javascript
   reviewData = {
     overview: 'Resume generation completed successfully.',
     statistics: { /* default values */ }
   }
   ```
   - Ensures UI always displays meaningful content

### Enhanced AI Prompt System

**Location**: `tex_tailor/proposer.py`

**Key Enhancements**:
- **Compelling Summaries**: Detailed narratives with quantified achievements
- **Conversational Cover Letters**: Natural, engaging tone avoiding corporate jargon
- **Specific Examples**: Before/after examples showing transformation quality

**System Prompt Structure**:
```python
SYSTEM_PROMPT = """You are a deterministic résumé/cover-letter tailor.
CRITICAL CONSTRAINTS:
- Summary: Create a COMPELLING, DETAILED summary that showcases specific expertise...
- Cover letter: Write with a NATURAL, CONVERSATIONAL tone that flows like genuine human communication...
EXAMPLES OF VALID EDITS:
- Summary: Transform bland summaries into compelling narratives:
  AVOID: "I am a software engineer with experience in Python."
  PREFER: "I am a passionate Software Engineer with over three years of hands-on experience..."
"""
```

## 🛠️ API Endpoints Reference

### Core Processing
- `POST /api/process` - Start resume customization workflow
- `GET /api/status/:jobId` - Poll processing status with real-time updates
- `GET /api/results/:jobId` - Get complete results with fallback strategies

### File Operations
- `POST /api/upload` - Upload job description files
- `GET /api/download/:jobId/:fileType` - Download generated files
  - Support for: `resume`, `cover-letter`, `resume-tex`, `cover-letter-tex`, `edits`
- `GET /api/view/:jobId/:fileType` - View PDF files inline (browser preview)
- `GET /api/view/:jobId/:fileType/tex` - View LaTeX source files as text

### Configuration & Health
- `GET /api/providers` - List available AI providers and their status
- `GET /api/health` - System health check
- `GET /api/validate` - Validate configuration and dependencies

## 🔒 Security & Safety Features

### LaTeX Safety
- **Command Filtering**: Prevents injection of malicious LaTeX commands
- **Character Escaping**: Automatic escaping of special LaTeX characters
- **Marker System**: Only designated chunks are editable by AI
- **Structure Preservation**: Document structure and formatting remain intact

### Data Handling
- **Temporary Storage**: Files automatically cleaned up after processing
- **No Persistent User Data**: No long-term storage of personal information
- **API Key Security**: Keys stored client-side only, passed to server during processing
- **Input Validation**: Strict validation of all user inputs and AI responses

### AI Response Validation
- **JSON Schema Validation**: All AI responses validated against strict schemas
- **Business Rule Enforcement**: Additional validation for content quality
- **Retry Logic**: Automatic retries with exponential backoff (2, 4, 8 second delays)
- **Rate Limiting**: Frontend protection (5-second intervals) and AI provider rate limit awareness
- **Factual Integrity**: AI cannot modify dates, employers, or quantified metrics

## 🧪 Development & Testing

### Development Setup
```bash
# Backend development
cd frontend
npm install
npm run dev:server  # Express.js on port 3001

# Frontend development  
npm run dev:client  # Vue.js on port 3000

# Or run both together
npm run dev
```

### Testing Strategy
- **Unit Tests**: Python CLI components (`tex_tailor/tests/`)
- **Integration Tests**: API endpoints and workflow
- **Manual Testing**: Complete end-to-end workflow validation
- **LaTeX Validation**: ChkTeX linting for generated LaTeX quality

### Debugging Features
- **Real-time Logging**: Detailed CLI output streamed to frontend
- **Status Tracking**: Step-by-step progress monitoring
- **Error Categories**: Structured error handling with actionable guidance
- **Health Checks**: Comprehensive system health monitoring

## 🚀 Deployment Considerations

### Frontend Deployment
- **Static Hosting**: Can be deployed to Vercel, Netlify, or similar
- **Build Process**: `npm run build` creates optimized production bundle
- **Environment Variables**: Configure API endpoints and settings

### Backend Deployment
- **Node.js Hosting**: Deploy to Railway, Render, or similar platforms
- **Python Dependencies**: Ensure Python CLI and LaTeX are available
- **File System Access**: Temporary file storage permissions required
- **Environment Variables**: AI provider API keys and configuration

### System Requirements
- **LaTeX Distribution**: Required for PDF compilation
- **Python 3.8+**: For CLI processing engine
- **Node.js 18+**: For Express.js backend
- **AI Provider Access**: At least one configured (OpenAI, Gemini, or Ollama)

## 🔧 Configuration Management

### Environment Variables
```bash
# AI Provider API Keys
GEMINI_API_KEY=your_key_here
OPENAI_API_KEY=your_key_here

# Model Selection
GEMINI_MODEL=gemini-1.5-pro
OPENAI_MODEL=gpt-4o

# Server Configuration
PORT=3001
FRONTEND_URL=http://localhost:3000
```

### Configuration Files
- `tex_tailor/config.py`: Centralized Python configuration
- `frontend/server/index.js`: Express.js server configuration
- `frontend/src/config/api.js`: Frontend API configuration

This architecture provides a robust, scalable, and user-friendly system for AI-powered resume customization with comprehensive safety features and excellent user experience.