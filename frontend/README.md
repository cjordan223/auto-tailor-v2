# Tex-Tailor Frontend

Modern Vue.js frontend for the Tex-Tailor AI resume customization tool.

## ✨ Features

- **Drag & Drop File Upload** - Easy resume template and job description upload
- **Real-time Processing** - Live status updates during AI processing  
- **Provider Selection** - Choose between Gemini, OpenAI, or Ollama
- **Results Dashboard** - Download generated PDFs and view changes
- **Settings Management** - Configure API keys and preferences
- **Responsive Design** - Works on desktop, tablet, and mobile

## 🚀 Quick Start

### Prerequisites

- Node.js 18+ 
- npm or yarn
- Backend Python CLI running

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
- **File Upload:** Multer for handling resume/job description files
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
│   │   ├── ProviderSelector.vue # AI provider selection
│   │   └── ProcessingStatus.vue # Real-time status updates
│   ├── views/               # Page components
│   │   ├── Home.vue         # Main workflow page
│   │   ├── Results.vue      # Results and downloads
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

### Settings

- **API Keys:** Configure in Settings page or environment variables
- **Default Provider:** Choose preferred AI provider
- **Auto-download:** Automatically download results when ready

## 🔌 API Endpoints

### File Processing
- `POST /api/process` - Start resume processing
- `GET /api/status/:jobId` - Check processing status
- `GET /api/results/:jobId` - Get job results

### File Management  
- `POST /api/upload` - Upload individual files
- `GET /api/download/:jobId/:fileType` - Download generated files

### Configuration
- `GET /api/providers` - Get available AI providers
- `GET /api/health` - Health check

## 🎨 UI Components

### FileUpload
- Drag & drop interface
- File type validation
- Progress indicators
- Text input for job descriptions

### ProviderSelector
- Visual provider cards
- Model selection dropdowns
- API key status indicators
- Performance comparisons

### ProcessingStatus
- Real-time progress updates
- Step-by-step workflow display
- Error handling and retry options

## 🔄 Development Workflow

1. **Start Development:**
   ```bash
   npm run dev
   ```

2. **Make Changes:**
   - Frontend: Hot reload at http://localhost:3000
   - Backend: Auto-restart with nodemon at http://localhost:3001

3. **Test Processing:**
   - Upload resume template and job description
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
npm run server
```

### Environment Setup
- Set API keys as environment variables
- Ensure Python CLI dependencies are installed
- Configure file storage permissions

## 🐛 Troubleshooting

### Common Issues

**"Backend not responding"**
- Check if Express server is running on port 3001
- Verify CORS configuration

**"Processing failed"**
- Ensure Python CLI is executable
- Check API keys are configured
- Verify file upload permissions

**"Files not downloading"**
- Check temp directory permissions
- Verify Python CLI output directory

### Debug Mode

```bash
# Enable debug logging
DEBUG=tex-tailor:* npm run dev:server
```

## 🤝 Contributing

1. Fork the repository
2. Create feature branch: `git checkout -b feature/new-feature`
3. Commit changes: `git commit -m 'Add new feature'`
4. Push to branch: `git push origin feature/new-feature`
5. Submit pull request

## 📄 License

MIT License - see LICENSE file for details