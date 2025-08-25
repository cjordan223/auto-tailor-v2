# Tex-Tailor

AI-powered resume and cover letter customization with a modern web interface and powerful automation tools. Tex-Tailor intelligently tailors your LaTeX documents to a specific job description using your choice of LLM, while safely preserving your document's structure and formatting.

<p align="center">
  <img src="https://user-images.githubusercontent.com/12345/your-demo-image.gif" alt="Tex-Tailor Demo">
</p>

## 🎯 Core Features

- **🤖 AI-Powered Customization**: Leverages Gemini, OpenAI, or local Ollama models to tailor resumes and cover letters.
- **📄 Interactive LaTeX Editor**: Edit LaTeX source code with a real-time, side-by-side PDF preview.
- **📊 Application Dashboard**: View, manage, and track all your saved and applied-to job applications in a central dashboard.
- **📦 One-Click Download**: Download all generated files (PDF, TeX, JSON) as a single ZIP archive.
- **⚡ Real-time Processing**: Watch the AI work with live status updates and progress tracking.
- **⚙️ Multi-Platform Support**: Use the web UI, CLI, or the included Raycast script for full workflow automation.

## 🚀 Quick Start

The recommended way to use Tex-Tailor is via the web interface.

### Development Setup

```bash
# 1. Navigate to the frontend directory
cd frontend

# 2. Install dependencies
npm install

# 3. Start the development server for the UI and API
npm run dev
```
Now, open **[http://localhost:3000](http://localhost:3000)** in your browser.

On your first visit, go to the **Settings** page to configure your AI provider API keys.

### Production Deployment

For production deployment on platforms like Render, see the **[Deployment Guide](./docs/DEPLOYMENT.md)** for detailed instructions on:

- Setting up Docker containers
- Configuring environment variables
- Deploying to cloud platforms
- Database setup with MongoDB Atlas

## 📚 Learn More

For more detailed information, please refer to the documentation:

- **[Architecture Overview](./docs/ARCHITECTURE.md)**: A deep dive into the tech stack, data flow, and system components.
- **[API Reference](./docs/API.md)**: Complete documentation for the backend API endpoints.
- **[Configuration Guide](./docs/CONFIG.md)**: Detailed information on setting up the environment and configuring the application.
- **[Deployment Guide](./docs/DEPLOYMENT.md)**: Production deployment instructions for cloud platforms like Render and Vercel.
- **[Custom Model Training](./docs/CUSTOM_OLLAMA_MODEL_TRAINING.md)**: Instructions for training your own specialized Ollama model.

## 🤖 Supported AI Providers

- **Google Gemini** (Recommended)
- **OpenAI**
- **Mistral**
- **Groq**
- **Ollama** (for local models)
