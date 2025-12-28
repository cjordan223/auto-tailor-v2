#!/bin/bash

echo "🚀 Starting Tex-Tailor Local Development Environment"
echo "=================================================="

# Check if we're in the right directory
if [ ! -f "tex_tailor/cli.py" ]; then
    echo "❌ Error: Please run this script from the project root directory"
    exit 1
fi

# Activate Python virtual environment
echo "🐍 Activating Python virtual environment..."
source venv/bin/activate

# Install tex-tailor in development mode if not already installed
echo "📦 Installing tex-tailor in development mode..."
pip install -e .

# Check if tex-tailor CLI works
echo "🔧 Testing tex-tailor CLI..."
python -m tex_tailor.cli --help > /dev/null 2>&1
if [ $? -ne 0 ]; then
    echo "❌ Error: tex-tailor CLI not working. Check your Python environment."
    exit 1
fi
echo "✅ tex-tailor CLI working"

# Check if LaTeX is available
echo "📄 Testing LaTeX compilation..."
latexmk --version > /dev/null 2>&1
if [ $? -ne 0 ]; then
    echo "⚠️  Warning: LaTeX not found. Install LaTeX for full functionality."
    echo "   On macOS: brew install --cask mactex"
    echo "   On Ubuntu: sudo apt-get install texlive-full"
else
    echo "✅ LaTeX available"
fi

# Navigate to frontend directory
cd frontend

# Install Node.js dependencies if needed
if [ ! -d "node_modules" ]; then
    echo "📦 Installing Node.js dependencies..."
    npm install
fi

# Check if API keys are configured
echo "🔑 Checking API configuration..."
if [ -z "$GEMINI_API_KEY" ] && [ -z "$OPENAI_API_KEY" ] && [ -z "$MISTRAL_API_KEY" ] && [ -z "$GROQ_API_KEY" ]; then
    echo "⚠️  Warning: No API keys found in environment variables"
    echo "   Set at least one of: GEMINI_API_KEY, OPENAI_API_KEY, MISTRAL_API_KEY, or GROQ_API_KEY"
    echo "   You can add them to your shell profile or export them now:"
    echo "   export GEMINI_API_KEY='your_key_here'"
fi

echo ""
echo "🎯 Starting development server..."
export PORT=3501
echo "   Frontend: http://localhost:3500"
echo "   Backend API: http://localhost:3501"
echo "   Health check: http://localhost:3501/health"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

# Start the development server
npm run dev
