# Vercel Deployment Fix Guide

## Issue Summary
Vercel frontend deployment is returning 403 Forbidden errors due to configuration issues.

## Root Cause Analysis
1. **vercel.json Configuration**: Using outdated build configuration format
2. **Environment Variables**: Missing `VITE_API_URL` pointing to Render backend
3. **Build Process**: Vercel needs proper build command and output directory configuration

## Fix Applied

### 1. Updated vercel.json Configuration
**File**: `frontend/vercel.json`
```json
{
  "buildCommand": "npm run build",
  "outputDirectory": "dist",
  "rewrites": [
    {
      "source": "/(.*)",
      "destination": "/index.html"
    }
  ],
  "headers": [
    {
      "source": "/assets/(.*)",
      "headers": [
        {
          "key": "Cache-Control",
          "value": "public, max-age=31536000, immutable"
        }
      ]
    }
  ]
}
```

### 2. Required Environment Variables
The following environment variable must be set in Vercel:

**VITE_API_URL**: `https://tex-tailor-backend.onrender.com`

This tells the frontend where to find the backend API server.

## How to Set Environment Variables in Vercel

### Option 1: Vercel Dashboard
1. Go to your Vercel project dashboard
2. Navigate to Settings → Environment Variables
3. Add:
   - **Name**: `VITE_API_URL`
   - **Value**: `https://tex-tailor-backend.onrender.com`
   - **Environment**: Production, Preview, Development
4. Save and redeploy

### Option 2: Vercel CLI
```bash
vercel env add VITE_API_URL
# Enter: https://tex-tailor-backend.onrender.com
```

## Expected Result After Fix
- ✅ Vercel deployment succeeds without 403 errors
- ✅ Frontend loads properly at `https://auto-tailor-v2.vercel.app/`
- ✅ Frontend can connect to Render backend API
- ✅ Authentication system works end-to-end

## Verification Steps
1. **Deploy**: Push changes to trigger Vercel deployment
2. **Test Frontend**: Visit `https://auto-tailor-v2.vercel.app/`
3. **Test API Connection**: Check browser console for API requests
4. **Test Authentication**: Try logging in/registering

## Architecture Overview
```
Frontend (Vercel) ←→ Backend (Render) ←→ MongoDB Atlas
     ↓                    ↓                    ↓
https://auto-tailor-v2.vercel.app  https://tex-tailor-backend.onrender.com  Database
```

## Troubleshooting
If issues persist:
1. Check Vercel deployment logs
2. Verify environment variables are set correctly
3. Ensure Render backend is running and accessible
4. Check browser console for API connection errors

---
*Fix applied on: $(date)*
*Issue: Vercel 403 Forbidden deployment error*
*Resolution: Updated vercel.json configuration and environment variables*
