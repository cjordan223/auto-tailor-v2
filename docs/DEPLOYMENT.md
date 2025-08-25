# Deployment Guide

This guide covers deploying Tex-Tailor to production environments, with a focus on cloud platforms like Render.

## Overview

Tex-Tailor consists of:
- **Frontend**: Vue.js application (recommended: Vercel)
- **Backend**: Node.js/Express API server with Python CLI integration (recommended: Render)
- **Database**: MongoDB Atlas (cloud database)

## Backend Deployment (Render)

### Prerequisites

1. **MongoDB Atlas Setup**
   - Create a MongoDB Atlas account
   - Create a cluster and database user
   - Get your connection string
   - Replace `<password>` with your database user password

2. **AI Provider API Keys**
   - Set up accounts with your preferred AI providers:
     - Google Gemini (recommended)
     - OpenAI
     - Mistral
     - Groq
     - Ollama (for local deployments)

### Step 1: Prepare Repository

The repository already includes the necessary deployment files:

- `render.yaml` - Render blueprint configuration
- `frontend/Dockerfile` - Docker container definition
- `tex_tailor/requirements.txt` - Python dependencies
- `.dockerignore` - Docker build optimization

### Step 2: Deploy to Render

1. **Connect Repository**
   - Sign up for [Render](https://render.com)
   - Connect your GitHub/GitLab repository
   - Create a new "Blueprint" service

2. **Configure Environment Variables**
   
   In your Render dashboard, set these environment variables:
   
   ```bash
   # Database
   MONGODB_ATLAS_URI=mongodb+srv://username:password@cluster.mongodb.net/database?retryWrites=true&w=majority
   
   # Frontend URL (your Vercel URL)
   FRONTEND_URL=https://your-app.vercel.app
   
   # AI Provider Keys (set only the ones you plan to use)
   GEMINI_API_KEY=your_gemini_key_here
   OPENAI_API_KEY=your_openai_key_here
   MISTRAL_API_KEY=your_mistral_key_here
   GROQ_API_KEY=your_groq_key_here
   OLLAMA_BASE_URL=http://your-ollama-instance:11434  # if using Ollama
   ```

3. **Deploy**
   - Render will automatically use the `render.yaml` file
   - The build process will:
     - Install Node.js dependencies
     - Install Python and LaTeX
     - Set up the container environment
   - First deployment may take 5-10 minutes due to LaTeX installation

### Step 3: Verify Backend Deployment

Once deployed, your backend will be available at:
```
https://your-service-name.onrender.com
```

Test the health check:
```bash
curl https://your-service-name.onrender.com/health
```

Expected response:
```json
{
  "status": "healthy",
  "timestamp": "2025-08-25T22:20:35.310Z",
  "service": "tex-tailor-api"
}
```

## Frontend Deployment (Vercel)

### Step 1: Configure API URL

Set the `VITE_API_URL` environment variable in Vercel:

```bash
VITE_API_URL=https://your-service-name.onrender.com
```

### Step 2: Deploy

The frontend will automatically connect to your backend using the configured API URL.

## Environment Variables Reference

### Backend (Render)

| Variable | Required | Description |
|----------|----------|-------------|
| `MONGODB_ATLAS_URI` | Yes | MongoDB connection string |
| `FRONTEND_URL` | Yes | Your frontend URL for CORS |
| `GEMINI_API_KEY` | Optional | Google Gemini API key |
| `OPENAI_API_KEY` | Optional | OpenAI API key |
| `MISTRAL_API_KEY` | Optional | Mistral API key |
| `GROQ_API_KEY` | Optional | Groq API key |
| `OLLAMA_BASE_URL` | Optional | Ollama instance URL |
| `PORT` | No | Port (auto-configured by Render) |

### Frontend (Vercel)

| Variable | Required | Description |
|----------|----------|-------------|
| `VITE_API_URL` | Yes | Backend API URL |

## Database Setup

### MongoDB Atlas Configuration

1. **Create Collections**
   The application will automatically create the required collections:
   - `generated_applications` (capped collection for temporary data)
   - `saved_applications` (persistent user applications)

2. **Indexes**
   Indexes are automatically created for optimal performance:
   - User ID and timestamp indexes
   - Text search indexes for job descriptions
   - Compound indexes for filtering

3. **Connection Settings**
   Recommended connection settings (already configured):
   - `maxPoolSize: 10`
   - `serverSelectionTimeoutMS: 5000`
   - `socketTimeoutMS: 45000`

## Troubleshooting

### Common Issues

1. **Build Timeouts**
   - LaTeX installation can be slow on first build
   - Subsequent builds use cached layers and are faster

2. **Memory Issues**
   - Consider upgrading to Render's Starter plan for more memory
   - Monitor memory usage in production

3. **Database Connection Errors**
   - Verify MongoDB Atlas connection string
   - Check network access settings in MongoDB Atlas
   - Ensure database user has proper permissions

4. **CORS Errors**
   - Verify `FRONTEND_URL` environment variable
   - Ensure it matches your frontend deployment URL exactly

### Debug Commands

Check backend logs in Render dashboard for:
```
✅ Connected to MongoDB Atlas
🚀 Tex-Tailor API Server running on port XXXX
```

Test API endpoints:
```bash
# Health check
curl https://your-backend.onrender.com/health

# List providers
curl https://your-backend.onrender.com/api/providers
```

## Performance Optimization

### Backend

- Uses capped collections for temporary data
- Implements proper database indexing
- Graceful shutdown handling
- Error logging and monitoring

### Frontend

- Environment-based API configuration
- Lazy loading of components
- Optimized build process

## Security Considerations

- Environment variables for sensitive data
- CORS configuration for frontend access
- MongoDB connection encryption
- No API keys exposed in client-side code

## Scaling

For high-traffic deployments:

1. **Backend Scaling**
   - Upgrade Render plan for more resources
   - Consider horizontal scaling with multiple instances

2. **Database Scaling**
   - MongoDB Atlas auto-scales
   - Monitor connection pool usage

3. **Frontend Scaling**
   - Vercel handles scaling automatically
   - Consider CDN for global distribution

## Cost Optimization

- **Free Tiers Available**:
  - Render: Free tier with limitations
  - Vercel: Generous free tier
  - MongoDB Atlas: Free tier (512MB)

- **Paid Recommendations**:
  - Render Starter ($7/month): More reliable for production
  - MongoDB Atlas M2+ for larger datasets