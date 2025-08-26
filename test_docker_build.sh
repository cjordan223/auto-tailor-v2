#!/bin/bash

echo "🐳 Testing Tex-Tailor Docker Build Locally"
echo "=========================================="

# Check if we're in the right directory
if [ ! -f "Dockerfile" ]; then
    echo "❌ Error: Please run this script from the project root directory"
    exit 1
fi

# Build the Docker image
echo "📦 Building Docker image..."
docker build -t tex-tailor-local .

if [ $? -ne 0 ]; then
    echo "❌ Docker build failed"
    exit 1
fi

echo "✅ Docker build successful"

# Check if port 3001 is in use
if lsof -Pi :3001 -sTCP:LISTEN -t >/dev/null ; then
    echo "⚠️  Port 3001 is in use. Stopping any existing containers..."
    docker stop tex-tailor-container 2>/dev/null || true
    docker rm tex-tailor-container 2>/dev/null || true
fi

# Run the container
echo "🚀 Starting Docker container on port 3001..."
docker run -d --name tex-tailor-container \
  -p 3001:3001 \
  -e NODE_ENV=development \
  -e GEMINI_API_KEY="${GEMINI_API_KEY}" \
  -e OPENAI_API_KEY="${OPENAI_API_KEY}" \
  -e MISTRAL_API_KEY="${MISTRAL_API_KEY}" \
  -e GROQ_API_KEY="${GROQ_API_KEY}" \
  -e FRONTEND_URL="${FRONTEND_URL:-http://localhost:3000}" \
  tex-tailor-local

if [ $? -eq 0 ]; then
    echo "✅ Container started successfully"
    echo ""
    echo "🎯 Local Docker environment running:"
    echo "   API Server: http://localhost:3001"
    echo "   Health check: http://localhost:3001/health"
    echo "   View endpoint: http://localhost:3001/api/view/{jobId}/{fileType}"
    echo ""
    echo "📋 Useful commands:"
    echo "   docker logs tex-tailor-container  # View logs"
    echo "   docker stop tex-tailor-container  # Stop container"
    echo "   docker rm tex-tailor-container    # Remove container"
    echo ""
    echo "🧪 Test the build by running the frontend locally and connecting to this backend"
else
    echo "❌ Failed to start container"
    exit 1
fi