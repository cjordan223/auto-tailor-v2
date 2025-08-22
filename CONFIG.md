# Configuration Management

Tex-tailor uses a centralized configuration system for both CLI and web interface. The CLI configuration is in `tex_tailor/config.py`, while the web interface has its own settings management system.

## ✅ Implementation Status: COMPLETE

All hardcoded values have been successfully centralized:
- ✅ Model names and API endpoints moved to config
- ✅ File paths and directory structures configurable  
- ✅ CLI commands use smart defaults with runtime path resolution
- ✅ Environment variable overrides preserved and enhanced
- ✅ Web interface configuration system implemented
- ✅ API server configuration with Express.js
- ✅ Backward compatibility maintained
- ✅ Path handling issues resolved - workflow works from any directory
- ✅ File upload integration fully functional
- ✅ Real-time processing with live CLI output streaming

## Configuration Structure

### LLM Providers
```python
# Default models (can be overridden by environment variables)
providers:
  ollama:
    default_model: "qwen2.5:14b-instruct"
    timeout: 120
    temperature: 0
    top_k: 1
    max_tokens: 2048
    
  openai:
    default_model: "gpt-4o-mini"
    timeout: 120
    temperature: 0
    max_tokens: 2048
    
  gemini:
    default_model: "gemini-1.5-flash"
    timeout: 120
    temperature: 0
    top_k: 1
    max_tokens: 2048
```

### API Endpoints
```python
apis:
  ollama_base_url: "http://127.0.0.1:11434"
  openai_base_url: "https://api.openai.com/v1"
  gemini_base_url: "https://generativelanguage.googleapis.com/v1beta/models"
```

### File Paths
```python
paths:
  output_dir: "out"
  baseline_resume_dir: "Baseline_Resume"
  baseline_cover_dir: "Basline_Cover_Letter"
  base_text_file: "base_text.json"
  edits_file: "edits.json"
  resume_llm_ready: "Conner_Jordan_Software_Engineer llm_ready.tex"
  cover_llm_ready: "Conner_Jordan_Cover_Letter llm_ready.tex"
```

## Environment Variable Overrides

The following environment variables can override default configuration:

- `OLLAMA_BASE_URL` - Override Ollama server URL
- `OLLAMA_MODEL` - Override default Ollama model
- `OPENAI_MODEL` - Override default OpenAI model  
- `GEMINI_MODEL` - Override default Gemini model

Example:
```bash
# Override models
export OLLAMA_MODEL="llama3.1:8b"
export OPENAI_MODEL="gpt-4"
export GEMINI_MODEL="gemini-1.5-flash"

# Override API endpoints
export OLLAMA_BASE_URL="http://192.168.1.100:11434"

# Use with any provider
tex-tailor propose --jd job.txt --provider ollama
tex-tailor propose --jd job.txt --provider openai
tex-tailor propose --jd job.txt --provider gemini
```

## Web Interface Configuration

### Frontend (Vue.js)

The web frontend configuration is handled through:

1. **Environment Variables**: Set in `.env` file or system environment
2. **Settings Page**: User interface at `http://localhost:3000/settings`
3. **Local Storage**: Browser-based settings persistence

#### Environment Variables
```bash
# API Server Configuration
PORT=3001                           # Express.js server port
FRONTEND_URL=http://localhost:3000   # CORS allowed origin

# AI Provider API Keys (same as CLI)
GEMINI_API_KEY=your_gemini_key
OPENAI_API_KEY=your_openai_key
OLLAMA_BASE_URL=http://localhost:11434

# Model Overrides (same as CLI)
GEMINI_MODEL=gemini-1.5-pro
OPENAI_MODEL=gpt-4o
OLLAMA_MODEL=qwen2.5:14b-instruct
```

#### Settings Page Configuration

Access via `http://localhost:3000/settings`:

**API Key Management:**
- **Secure Input**: Password-masked input fields with show/hide toggle
- **Real-time Validation**: Test button (🧪) makes actual API calls to verify keys
- **Visual Feedback**: Status indicators show ✓ configured / ⚠ required / ❌ invalid
- **Automatic Storage**: Keys saved to browser localStorage on input
- **Direct Links**: Quick access to provider API key pages

**Provider Configuration:**
- **Gemini Setup**: API key from Google AI Studio with validation
- **OpenAI Setup**: API key from OpenAI Platform with validation  
- **Ollama Setup**: Server URL configuration with connection testing
- **Default Provider**: Choose preferred AI provider for new jobs
- **Auto-download**: Automatically download generated files when processing completes

**Additional Features:**
- **Processing History**: View and clear previous jobs
- **Backend Status**: Real-time connection indicator
- **Settings Export**: All settings stored in localStorage

#### Local Storage Settings

Settings are persisted in browser local storage:
```javascript
{
  "apiKeys": {
    "gemini": "user_provided_key",    // Securely stored, only sent during processing
    "openai": "user_provided_key"     // Validated with real API calls
  },
  "ollamaUrl": "http://localhost:11434",  // Server URL for local models
  "defaultProvider": "gemini",            // Auto-selected on new jobs
  "autoDownload": false                   // Auto-download completed files
}
```

#### API Key Security
- **Browser Storage**: Keys stored in localStorage, never transmitted except during processing
- **Environment Fallback**: System environment variables used if localStorage keys not available
- **Frontend Priority**: Browser-stored keys override environment variables
- **Validation**: Real API calls test key validity before first use

### Backend (Express.js)

The Express.js API server configuration:

#### Server Configuration
```javascript
// server/index.js
const PORT = process.env.PORT || 3001
const FRONTEND_URL = process.env.FRONTEND_URL || 'http://localhost:3000'

// CORS configuration
app.use(cors({
  origin: FRONTEND_URL,
  credentials: true
}))
```

#### File Upload Configuration
```javascript
// Multer configuration for job description uploads only
const storage = multer.diskStorage({
  destination: 'temp/',  // Temporary file storage
  filename: (req, file, cb) => {
    // UUID-based unique filenames
  }
})

const upload = multer({ 
  storage,
  limits: { fileSize: 10 * 1024 * 1024 },  // 10MB limit
  fileFilter: (req, file, cb) => {
    // Job descriptions only: .txt, .pdf, .doc, .docx
    const allowedTypes = ['.txt', '.pdf', '.doc', '.docx']
    const ext = path.extname(file.originalname).toLowerCase()
    cb(null, allowedTypes.includes(ext))
  }
})
```

#### API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/process` | POST | Start resume processing (job description + baseline template) |
| `/api/status/:jobId` | GET | Check processing status |
| `/api/download/:jobId/:fileType` | GET | Download generated files (attachment disposition) |
| `/api/view/:jobId/:fileType` | GET | View PDFs inline for embedded preview (inline disposition) |
| `/api/results/:jobId` | GET | Get complete job results with skills changes and review data |
| `/api/providers` | GET | Get available AI providers |
| `/api/validate` | POST | Validate API keys with real API calls |
| `/api/health` | GET | Health check |

#### PDF Viewing Endpoints

**Download vs View Endpoints:**
- **Download**: `/api/download/:jobId/:fileType` - Sets `Content-Disposition: attachment` for file downloads
- **View**: `/api/view/:jobId/:fileType` - Sets `Content-Disposition: inline` for iframe embedding

**Supported File Types:**
- `resume` - Generated resume PDF
- `cover-letter` - Generated cover letter PDF  
- `edits` - JSON file with all edits (download only)

**Example Usage:**
```javascript
// Embed PDF in iframe for preview
<iframe src="/api/view/abc123/resume" width="100%" height="400px"></iframe>

// Download file
window.location.href = "/api/download/abc123/resume"
```

**Security Headers:**
- `Content-Type: application/pdf`
- `X-Frame-Options: SAMEORIGIN` (allows iframe embedding from same origin)
- `Cache-Control: no-cache` (ensures fresh content)
- CORS headers for cross-origin requests

#### Real-time Output Streaming

The Express.js backend now provides real-time streaming of Python CLI output:

**Output Parsing Engine:**
```javascript
// Parse CLI stdout/stderr in real-time
parseOutputAndUpdateStatus(statusFile, output, jobId)

// Intelligent progress mapping
"🔄 Processing job description" → 10% "Processing job description..."
"✓ Initialization complete" → 20% "Baseline files prepared"
"Generated 12 edits" → 60% "Generated 12 targeted edits"
```

**Enhanced Status Response:**
```json
{
  "status": "processing",
  "progress": 40,
  "step": "AI analysis in progress...",
  "detail": "Sending content to AI provider for analysis",
  "provider": "Gemini",
  "error": null,
  "updatedAt": "2025-08-21T07:00:00.000Z"
}
```

**✅ Recent Fixes Applied:**
- **Path Resolution**: All file paths now converted to absolute paths for reliable CLI execution
- **File Upload**: Complete integration between frontend upload and backend processing
- **Real-time Updates**: Live streaming of CLI output with detailed progress tracking

**Error Categorization:**
- API Authentication → "Invalid or missing API key"
- Timeout → "AI provider request timed out"
- Rate Limit → "API rate limit reached"
- General → "Processing error with logs"

### Development vs Production

#### Development Configuration
```bash
# Start both frontend and backend
cd frontend
npm run dev  # Starts both servers concurrently

# Frontend: http://localhost:3000
# Backend:  http://localhost:3001
```

#### Production Configuration
```bash
# Build frontend
npm run build

# Start production server
npm run server

# Or deploy separately:
# - Frontend: Deploy 'dist' to Vercel/Netlify
# - Backend: Deploy Express.js to Railway/Render
```

## CLI Changes

All CLI commands now use sensible defaults from the configuration:

- ✅ **Smart Defaults**: Output paths automatically resolved at runtime
- ✅ **Optional Parameters**: Most file paths now optional in CLI
- ✅ **Backward Compatibility**: Existing scripts continue to work
- ✅ **Environment Variables**: Still work as before, now handled through config

### Before and After Examples

```bash
# BEFORE: Required explicit paths everywhere
tex-tailor extract --resume "Baseline_Resume/..." --cover "Basline_Cover_Letter/..." --out "out/base_text.json"
tex-tailor propose --jd job.txt --base-text "out/base_text.json" --out "out/edits.json"
tex-tailor apply --edits "out/edits.json" --resume "Baseline_Resume/..." --cover "Basline_Cover_Letter/..."

# AFTER: Uses intelligent defaults
tex-tailor extract --resume "Baseline_Resume/..." --cover "Basline_Cover_Letter/..."
tex-tailor propose --jd job.txt
tex-tailor apply

# Still works with explicit paths when needed
tex-tailor extract --resume custom.tex --cover custom_cover.tex --out custom/output.json
```

### CLI Help Text
All commands now show parameters as optional (no hardcoded defaults visible):
```bash
$ tex-tailor propose --help
Options:
  --base-text TEXT    Path to base text JSON        # No default shown
  --out TEXT          Output edits JSON file        # No default shown
```

## Programmatic Usage

```python
from tex_tailor.config import config, get_model_for_provider, get_default_paths

# Get default paths (used by CLI commands)
paths = get_default_paths()
print(paths["base_text"])     # "out/base_text.json"
print(paths["edits"])        # "out/edits.json" 
print(paths["baseline_resume"]) # "Baseline_Resume/Conner_Jordan_Software_Engineer llm_ready.tex"

# Get model for provider (respects env var overrides)
model = get_model_for_provider("ollama")  # "qwen2.5:14b-instruct" or OLLAMA_MODEL
model = get_model_for_provider("openai")  # "gpt-4o-mini" or OPENAI_MODEL

# Access configuration directly
timeout = config.providers.ollama.timeout        # 120
output_dir = config.paths.output_dir             # "out"
api_url = config.apis.ollama_base_url            # "http://127.0.0.1:11434"
max_changes = config.validation.max_skills_changes # 8

# Get API configuration for provider
api_config = get_api_config_for_provider("gemini")
print(api_config["base_url"])     # Gemini API endpoint
print(api_config["timeout"])      # 120
print(api_config["temperature"])  # 0
```

## Testing the Configuration

```bash
# Test basic configuration loading
source venv/bin/activate
python -c "from tex_tailor.config import config; print('Config loaded:', config.providers.ollama.default_model)"

# Test environment variable overrides
OLLAMA_MODEL=llama3.1:8b python -c "from tex_tailor.config import get_model_for_provider; print(get_model_for_provider('ollama'))"

# Test CLI with defaults
tex-tailor status  # Shows all current configuration values
```

## Implementation Details

### Configuration Structure
The config system uses Python dataclasses for type safety:

```python
@dataclass
class Config:
    providers: ProviderConfig     # LLM model settings
    apis: APIConfig              # API endpoints and timeouts
    paths: PathConfig            # File paths and directories  
    validation: ValidationConfig # Edit limits and constraints
```

### Runtime Default Resolution
CLI commands follow this pattern:

1. **Decorator**: `@click.option("--out", default=None, help="...")`
2. **Function Signature**: `def command(out: Optional[str]):`
3. **Runtime Logic**: 
   ```python
   if not out:
       out = get_default_paths()["edits"]
   ```

This provides smart defaults while preserving user override capability.

### Environment Variable Integration
Environment variables are processed during config initialization:

```python
def __post_init__(self):
    """Apply environment variable overrides."""
    if os.getenv("OLLAMA_MODEL"):
        self.providers.ollama.default_model = os.getenv("OLLAMA_MODEL")
    # ... other overrides
```

## Benefits

1. ✅ **Centralized Configuration**: All settings in one place (`config.py`)
2. ✅ **Environment Override Support**: Easy customization via env vars
3. ✅ **Type Safety**: Configuration is type-checked with dataclasses
4. ✅ **Smart Defaults**: CLI commands require fewer parameters
5. ✅ **Backward Compatibility**: Existing environment variables still work
6. ✅ **Easier Testing**: Configuration can be easily mocked for tests
7. ✅ **Better Maintainability**: No more scattered hardcoded values
8. ✅ **User Experience**: Simpler command line usage

## Migration

**✅ FULLY BACKWARD COMPATIBLE**: Existing scripts and environment variables continue to work without modification.

## ✅ Verification Status (August 2025)

**All systems verified and working:**
- ✅ **CLI Workflow**: `./run_workflow_clean.sh test_jd.txt` completes successfully
- ✅ **Web Interface**: Frontend (port 3000) and backend (port 3001) both functional
- ✅ **File Upload**: Job description uploads process correctly
- ✅ **Path Handling**: Works from any directory with absolute path resolution
- ✅ **Real-time Processing**: Live status updates with detailed CLI output
- ✅ **PDF Generation**: Both resume and cover letter PDFs generated successfully

### What Changed
- Hardcoded defaults removed from CLI option decorators
- Runtime default resolution added to command functions
- Configuration centralized in `config.py`
- All existing functionality preserved

### What Stayed the Same
- Environment variable names and behavior
- CLI command syntax and options
- Output file formats and locations
- API integrations and provider support