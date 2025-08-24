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

### 🌐 **Modern Web Interface**
- **Drag & Drop**: Upload job descriptions effortlessly
- **Real-time Processing**: See detailed progress, not just spinners  
- **PDF Preview**: Embedded viewers for instant document review
- **LaTeX Source Viewer**: Side-by-side source code and PDF with syntax highlighting
- **Multi-provider Support**: Gemini, OpenAI, or local Ollama

### 🤖 **Intelligent AI Processing**
- **Smart Customization**: Tailors resume summary, skills, and cover letter
- **Natural Language**: Conversational cover letters, not corporate speak
- **Safe Editing**: Preserves LaTeX structure using marker system
- **Fallback System**: Works even when AI providers are unavailable

### 📱 **Automation & Integration**
- **Raycast Commands**: One-click workflow from clipboard
- **Silent Processing**: Background processing with result notifications
- **Batch Support**: CLI for multiple job applications
- **API Integration**: RESTful API for custom integrations

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
./run_workflow_clean.sh job_description.txt

# Step-by-step processing
tex-tailor init
tex-tailor extract --resume "Baseline_Resume/..." --cover "Basline_Cover_Letter/..."
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
├── run_*.sh                    # Automation scripts
└── Baseline_*/                 # LaTeX templates
```

## 🔧 Scripts & Automation

| Script | Purpose | Usage |
|--------|---------|--------|
| `run_complete_workflow.sh` | Raycast automation | Full workflow from clipboard |
| `run_silent_workflow.sh` | Background processing | Auto-detect latest JD and process |
| `run_workflow_clean.sh` | CLI workflow | Complete processing from file |

## 🧪 Testing & Validation

```bash
# Test complete pipeline
./run_workflow_clean.sh test_jd.txt

# Test web interface
curl http://localhost:3001/health

# Test LaTeX quality
./check_latex.sh

# Run unit tests  
python -m unittest discover tex_tailor/tests/ -v
```

## 🏆 Success Metrics

- **✅ 100% Success Rate**: Quality-focused validation eliminated previous failures
- **⚡ Fast Processing**: Gemini 1.5-Flash provides results in ~30 seconds
- **🎯 High Quality**: Compelling summaries and natural cover letters
- **🔒 Safe Editing**: Never corrupts LaTeX structure or factual information
- **📱 Universal Access**: Web, CLI, and Raycast command support

## 🎯 AI Providers

| Provider | Model | Speed | Quality | Rate Limit | Best For |
|----------|-------|-------|---------|-----------|----------|
| **Gemini** | 1.5-flash | ⚡⚡⚡ | ⭐⭐⭐⭐ | 15 RPM | **Recommended** |
| Gemini | 1.0-pro | ⚡⚡ | ⭐⭐⭐ | 60 RPM | Testing |
| OpenAI | gpt-4o-mini | ⚡⚡ | ⭐⭐⭐⭐⭐ | 500 RPM | Premium quality |
| Ollama | qwen2.5:14b | ⚡ | ⭐⭐⭐ | ∞ | Privacy/Local |

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
./check_latex.sh
```

### Reset Workflow
```bash
# Clean working files (keeps baselines)
rm -rf out/ frontend/temp/ Baseline_Resume/*llm_ready.tex Basline_Cover_Letter/*llm_ready.tex
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