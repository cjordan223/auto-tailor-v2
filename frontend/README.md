# Tex-Tailor Frontend

Modern Vue.js frontend for the Tex-Tailor AI resume customization tool.

## ✨ Features

- **Job Description Upload** - Upload or paste job descriptions for AI customization
- **Pre-configured Baseline Resume** - Uses optimized LaTeX template with LLM markers
- **Real-time Processing** - Live status updates during AI processing  
- **LaTeX Source Code Viewer** - Side-by-side LaTeX source and PDF preview with syntax highlighting
- **Provider Selection** - Choose between Gemini (1.5 Flash, 1.5 Pro, 1.0 Pro), OpenAI, or Ollama
- **Rate Limiting Protection** - Exponential backoff and frontend request throttling
- **Results Dashboard** - Download generated PDFs and LaTeX files, view analysis
- **Resilient Fallback System** - Works even when AI providers are unavailable
- **Settings Management** - Configure API keys and preferences
- **Responsive Design** - Works on desktop, tablet, and mobile

## 🚀 Quick Start

### Prerequisites

- Node.js 18+ 
- npm or yarn
- Backend Python CLI running
- Baseline resume template file: `templates/Baseline_Resume/Conner_Jordan_Software_Engineer llm_ready.tex`

### Installation

```bash
# Install dependencies
npm install

# Start development servers (frontend + backend)
npm run dev

# Or start individually
npm run dev:client  # Frontend only (port 3000)
npm run dev:server  # Backend only (port 3001)
```

### Production Build

```bash
# Build for production
npm run build

# Preview production build
npm run preview

# Start production server
npm run server
```

## 🏗️ Architecture

### Frontend (Vue 3 + Vite)
- **Port:** 3000
- **Framework:** Vue 3 with Composition API
- **Build Tool:** Vite for fast development
- **Styling:** Tailwind CSS for rapid UI development
- **Routing:** Vue Router for SPA navigation

### Backend API (Express.js)
- **Port:** 3001  
- **Framework:** Express.js with ES modules
- **File Upload:** Multer for handling job description files only
- **Process Management:** Spawns Python CLI as subprocess
- **File Serving:** Serves generated PDFs for download

### Communication Flow
```
Vue Frontend → Express API → Python CLI → AI Provider → Generated Files
```

## 📁 Project Structure

```
frontend/
├── src/
│   ├── components/          # Reusable Vue components
│   │   ├── FileUpload.vue   # Drag & drop file upload
│   │   ├── LaTeXViewer.vue  # LaTeX source code viewer with syntax highlighting
│   │   ├── PDFViewer.vue    # Embedded PDF preview
│   │   ├── ProviderSelector.vue # AI provider selection
│   │   └── ProcessingStatus.vue # Real-time status updates
│   ├── views/               # Page components
│   │   ├── Home.vue         # Main workflow page (job description only)
│   │   ├── Results.vue      # Results with side-by-side LaTeX/PDF viewing
│   │   └── Settings.vue     # Configuration page
│   ├── composables/         # Reusable logic
│   │   └── useAPI.js        # API communication
│   └── assets/              # Styles and static files
├── server/                  # Express.js backend
│   ├── routes/              # API route handlers
│   ├── middleware/          # Express middleware
│   └── index.js             # Server entry point
└── temp/                    # Temporary file storage
```

## 🔧 Configuration

### Environment Variables

```bash
# API Configuration
PORT=3001
FRONTEND_URL=http://localhost:3000

# AI Provider API Keys (passed to Python CLI)
GEMINI_API_KEY=your_gemini_key
OPENAI_API_KEY=your_openai_key
```

### Baseline Resume Template

The application uses a pre-configured baseline resume template located at:
```
templates/Baseline_Resume/Conner_Jordan_Software_Engineer llm_ready.tex
```

This template includes LLM markers for optimal AI processing and consistent formatting.

### Settings

- **API Keys:** Configure in Settings page or environment variables
- **Default Provider:** Choose preferred AI provider
- **Auto-download:** Automatically download results when ready

## 🔌 API Endpoints

### File Processing
- `POST /api/process` - Start resume processing (job description only)
- `GET /api/status/:jobId` - Check processing status
- `GET /api/results/:jobId` - Get job results

### File Management  
- `POST /api/upload` - Upload individual files
- `GET /api/download/:jobId/:fileType` - Download generated files
- `GET /api/view/:jobId/:fileType` - View PDF files inline
- `GET /api/view/:jobId/:fileType/tex` - View LaTeX source files

### Configuration
- `GET /api/providers` - Get available AI providers
- `GET /api/health` - Health check

## 🎨 UI Components

### FileUpload
- Drag & drop interface for job descriptions
- File type validation (.txt, .pdf, .doc, .docx)
- Text input for pasting job descriptions
- Progress indicators

### ProviderSelector
- Visual provider cards
- Model selection dropdowns
- API key status indicators
- Performance comparisons

### ProcessingStatus
- Real-time progress updates
- Step-by-step workflow display
- Error handling and retry options

### LaTeXViewer
- **Syntax Highlighting**: Color-coded LaTeX commands, environments, comments, math mode
- **Line Numbers**: Easy code reference and navigation
- **Copy to Clipboard**: One-click copying with visual feedback
- **Responsive Design**: Adapts to different screen sizes
- **Error Handling**: Graceful fallbacks for missing files
- **Real-time Loading**: Fetches LaTeX source via API
- **Monospace Font**: Proper code display with syntax highlighting

#### Syntax Highlighting Features
- **Commands**: Green highlighting for `\textbf`, `\section`, etc.
- **Environments**: Red highlighting for `\begin{document}`, `\end{itemize}`
- **Comments**: Gray italic for `% comments`
- **Math Mode**: Orange with background for `$equations$`
- **Braces**: Blue highlighting for `{` and `}`
- **Optional Arguments**: Purple for `[optional]` parameters

### PDFViewer
- **Inline Preview**: Embedded PDF viewing without downloads
- **Fallback Support**: Browser compatibility handling
- **Loading States**: Visual feedback during PDF loading
- **Error Recovery**: Graceful handling of PDF load failures

## 🔄 Development Workflow

1. **Start Development:**
   ```bash
   npm run dev
   ```

2. **Make Changes:**
   - Frontend: Hot reload at http://localhost:3000
   - Backend: Auto-restart with nodemon at http://localhost:3001

3. **Test Processing:**
   - Upload or paste job description
   - Select AI provider
   - Monitor real-time status updates
   - Download generated files

4. **Build for Production:**
   ```bash
   npm run build
   ```

## 🚢 Deployment

### Frontend (Static)
Deploy to Vercel, Netlify, or any static hosting:

```bash
npm run build
# Deploy 'dist' directory
```

### Backend (Node.js)
Deploy to Railway, Render, or any Node.js hosting:

```bash
# Ensure Python CLI is available on server
# Ensure baseline resume template is present
npm run server
```

### Environment Setup
- Set API keys as environment variables
- Ensure Python CLI dependencies are installed
- Configure file storage permissions
- Verify baseline resume template exists

## 🐛 Troubleshooting

### Common Issues

**"Backend not responding"**
- Check if Express server is running on port 3001
- Verify CORS configuration

**"Processing failed"**
- Ensure Python CLI is executable
- Check API keys are configured
- Verify file upload permissions
- Confirm baseline resume template exists

**"Files not downloading"**
- Check temp directory permissions
- Verify Python CLI output directory

**"Baseline resume template not found"**
- Ensure `templates/Baseline_Resume/Conner_Jordan_Software_Engineer llm_ready.tex` exists
- Check file permissions and path configuration

### Debug Mode

```bash
# Enable debug logging
DEBUG=tex-tailor:* npm run dev:server
```

## 🔮 Future Enhancements

### Custom LaTeX Template Support
The current version uses a pre-configured baseline resume template. Future releases will include:

- **Custom Template Upload** - Allow users to upload their own LaTeX templates
- **Marker Detection** - Automatically detect LLM markers in uploaded templates
- **Template Validation** - Validate LaTeX syntax and marker placement
- **Chunk Extraction** - Extract customizable sections from templates

### Implementation Requirements
- Marker detection algorithm
- Template validation system
- Chunk extraction logic
- Backward compatibility with baseline template

## 🤝 Contributing

1. Fork the repository
2. Create feature branch: `git checkout -b feature/new-feature`
3. Commit changes: `git commit -m 'Add new feature'`
4. Push to branch: `git push origin feature/new-feature`
5. Submit pull request

## 📄 License

MIT License - see LICENSE file for details