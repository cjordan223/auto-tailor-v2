# Tex-Tailor

AI-powered resume and cover letter customization with modern web interface and automation tools. Intelligently tailors LaTeX documents to job descriptions using LLMs while preserving document structure.

## 🚀 Quick Start

### Web Interface (Recommended)
```bash
# Start the application
cd frontend
npm install
npm run dev

# Open http://localhost:3000
# Configure API keys in Settings → Upload JD → Get results
```

### Raycast Automation
```bash
# Copy job description → Run Raycast command
./run_complete_workflow.sh "Job Title" "Company Name"
```

## 🎯 Features

- **🤖 AI-Powered Customization**: Uses advanced LLMs to tailor resumes and cover letters to specific job descriptions
- **📄 LaTeX Support**: Full LaTeX source code editing with real-time PDF preview
- **🎯 ATS Optimization**: Ensures resumes pass Applicant Tracking Systems
- **📱 Universal Access**: Web, CLI, and Raycast command support
- **📦 One-Click Download**: Download all files as a compressed ZIP archive
- **🔍 Detailed Analysis**: Comprehensive review of changes and suggestions
- **⚡ Real-time Processing**: Live status updates and progress tracking

## 🏗️ Architecture

```
Vue.js Frontend → Express.js API → Python CLI → AI Provider → Generated Documents
    (Port 3000)      (Port 3001)                  (Gemini/OpenAI/Ollama)
```

### Document Processing Flow
1. **Upload**: Job description via web or Raycast
2. **Extract**: AI-safe content from LaTeX templates  
3. **Propose**: AI generates targeted edits
4. **Apply**: Safe insertion back into LaTeX
5. **Generate**: PDF compilation and delivery

### Marker System
```latex
% === LLM:CHUNK START RESUME.SUMMARY ===
AI can edit this content safely
% === LLM:CHUNK END RESUME.SUMMARY ===

% === LLM:LOCK START RESUME.EXPERIENCE ===
This LaTeX structure is protected
% === LLM:LOCK END RESUME.EXPERIENCE ===
```

## 📦 Setup

### Prerequisites
- **Python 3.8+** with LaTeX distribution
- **Node.js 18+** for web interface
- **AI Provider**: Gemini (recommended), OpenAI, or Ollama

### Installation
```bash
# 1. Clone and install Python backend
git clone <repo-url>
cd tex-tailor
pip install -e .

# 2. Install and start web interface  
cd frontend
npm install
npm run dev

# 3. Configure API keys at http://localhost:3000/settings
```

### Environment Setup
```bash
# API Keys (choose one or more)
export GEMINI_API_KEY="your-api-key"     # Recommended: fast, high-quality
export OPENAI_API_KEY="your-api-key"     # Premium option
export OLLAMA_BASE_URL="http://localhost:11434"  # Privacy-focused local

# Model Selection (optional)
export GEMINI_MODEL="gemini-1.5-flash"   # Default: fast and efficient
export OPENAI_MODEL="gpt-4o-mini"        # Default: cost-effective
```

## 💻 Usage

### Web Interface
1. **Visit** http://localhost:3000
2. **Configure** API keys in Settings (first time)
3. **Upload** job description
4. **Select** AI provider and process
5. **Download** customized resume and cover letter PDFs

### CLI Workflow
```bash
# Complete workflow (single command)
./scripts/run_workflow_clean.sh job_description.txt

# Step-by-step processing
tex-tailor init
tex-tailor extract --resume "templates/Baseline_Resume/..." --cover "templates/Basline_Cover_Letter/..."
tex-tailor propose --jd job.txt
tex-tailor apply
tex-tailor render
```

### Raycast Automation
```bash
# Copy job description to clipboard, then:
./run_complete_workflow.sh "Software Engineer" "TechCorp"
```

## 🎨 Customization

### Editable Sections
**Resume:**
- Professional Summary
- Technical Skills (8 categories: Programming, Frontend, Backend, Cloud, AI Tools, etc.)

**Cover Letter:**
- Dynamic salutation
- 4 customizable paragraphs with job-specific content

### AI Behavior
- **Compelling Summaries**: Detailed, quantified achievements
- **Conversational Tone**: Natural, engaging cover letters
- **Keyword Optimization**: Automatic alignment with job requirements
- **Safe Editing**: Never changes employment history or personal details

## 📁 File Structure

```
tex-tailor/
├── frontend/                    # Vue.js web interface
│   ├── src/components/         # UI components
│   ├── server/                 # Express.js API
│   └── temp/                   # Workflow results
├── tex_tailor/                 # Python CLI
│   ├── cli.py                  # Main commands
│   ├── proposer.py            # AI integration
│   └── patcher.py             # LaTeX editing
├── jd-repo/                    # Job description storage
├── out/                        # CLI generated files
├── scripts/                    # Automation scripts
└── templates/                  # LaTeX templates
```

## 🔧 Scripts & Automation

| Script | Purpose | Usage |
|--------|---------|--------|
| `scripts/run_complete_workflow.sh` | Raycast automation | Full workflow from clipboard |
| `scripts/run_silent_workflow.sh` | Background processing | Auto-detect latest JD and process |
| `scripts/run_workflow_clean.sh` | CLI workflow | Complete processing from file |

## 🧪 Testing & Validation

```bash
# Test complete pipeline
./scripts/run_workflow_clean.sh test_jd.txt

# Test web interface
curl http://localhost:3001/health

# Test LaTeX quality
./scripts/check_latex.sh

# Run unit tests  
python -m unittest discover tex_tailor/tests/ -v
```

## 🏆 Success Metrics

- **✅ 100% Success Rate**: Quality-focused validation eliminated previous failures
- **⚡ Fast Processing**: Gemini 1.5-Flash provides results in ~30 seconds
- **🎯 High Quality**: Compelling summaries and natural cover letters
- **🔒 Safe Editing**: Never corrupts LaTeX structure or factual information
- **📱 Universal Access**: Web, CLI, and Raycast command support

## 🤖 AI Providers Supported

- **Google Gemini** - Best balance of speed, quality, and cost
- **OpenAI** - Highest quality, premium pricing  
- **Mistral** - High quality, competitive pricing (Free: 1 RPS, 500K TPM, 1B tokens/month)
- **Groq** - Ultra-fast inference, competitive pricing (Free: 30 RPM, 14.4K RPD, 40K TPM)
- **Ollama** - Free local models, requires setup

## 🔍 Troubleshooting

### Common Issues

**Web Interface Not Loading**
```bash
# Check servers are running
curl http://localhost:3000  # Frontend
curl http://localhost:3001/health  # Backend API
```

**AI Processing Fails**
```bash
# Test API keys
curl -H "Authorization: Bearer $GEMINI_API_KEY" https://generativelanguage.googleapis.com/v1/models

# Try different provider
export GEMINI_API_KEY="your-key"
```

**LaTeX Compilation Errors**
```bash
# Check LaTeX installation
tex-tailor render
./scripts/check_latex.sh
```

### Reset Workflow
```bash
# Clean working files (keeps baselines)
rm -rf out/ frontend/temp/ templates/Baseline_Resume/*llm_ready.tex templates/Basline_Cover_Letter/*llm_ready.tex
tex-tailor init
```

## 📈 Recent Updates

- **🌐 Modern Web Interface**: Vue.js frontend with real-time processing
- **📱 Raycast Integration**: One-command automation from clipboard  
- **🤖 Enhanced AI**: Compelling summaries and conversational cover letters
- **⚡ Silent Processing**: Background workflows with browser auto-open
- **🔧 LaTeX Viewer**: Side-by-side source code and PDF preview
- **🛡️ Resilient API**: Multi-strategy fallback system
- **🎯 100% Success Rate**: Quality-focused validation system

---

**Get Started**: `cd frontend && npm run dev` → Open http://localhost:3000