# Render Deployment Issues - Debug Log

## Issue Summary
Render backend deployment failing with various errors while trying to deploy Tex-Tailor backend API server.

## Current Status
- **MongoDB**: ✅ Successfully connecting to Atlas
- **Server**: ✅ Starting on port 10000
- **Problem**: Getting 404 errors and SIGTERM signal termination

## Architecture Context
- **Frontend**: Deployed on Vercel (separate deployment)
- **Backend**: Should deploy on Render (API-only server)
- **Database**: MongoDB Atlas (working correctly)
- **Authentication**: JWT-based with user registration/login

## Chronological Fix Attempts

### Attempt 1: Node.js Version Compatibility
**Problem**: `crypto.hash is not a function` - Node.js 18 incompatible with Vite 7.1.3
**Solution**: 
- Updated `frontend/Dockerfile`: `FROM node:18-slim` → `FROM node:20-slim`
- Updated `render.yaml`: `NODE_VERSION: "18"` → `NODE_VERSION: "20"`
**Result**: ❌ Still using wrong Dockerfile

### Attempt 2: Root Dockerfile Discovery
**Problem**: Render using `./Dockerfile` (root) not `frontend/Dockerfile`
**Root Dockerfile Issues Found**:
- Using Node.js 18: `FROM node:18-slim`
- Had frontend build step: `RUN npm run build` (shouldn't exist for API-only backend)
**Solution**:
- Updated root `Dockerfile`: `FROM node:18-slim` → `FROM node:20-slim`
- Removed `RUN npm run build` step
**Result**: ✅ Build succeeded, but runtime 403 errors

### Attempt 3: Static File Serving Removal
**Problem**: Backend trying to serve frontend static files from `/app/frontend/dist/index.html`
**Error**: `ENOENT: no such file or directory, stat '/app/frontend/dist/index.html'`
**Cause**: Server configured to serve frontend but dist files don't exist (frontend on Vercel)
**Solution**:
- Removed: `app.use(express.static(path.join(__dirname, '../dist')))`
- Removed: Catch-all SPA handler `res.sendFile('../dist/index.html')`
**Result**: ❌ New error - SIGTERM and npm error

### Current Problem (Attempt 4)
**Symptoms**:
- Server starts successfully on port 10000
- MongoDB connects properly
- Gets `HEAD /` requests returning 404
- npm process terminates with SIGTERM
- Process gets restarted by Render

**Likely Causes**:
1. **Health Check Failing**: Render health check on wrong endpoint
2. **Missing Root Route**: No handler for `GET /` or `HEAD /`
3. **Port Detection Issues**: Render detecting port but process dies

## Environment Variables Set
- `JWT_SECRET`: ✅ (required for auth)
- `MONGODB_ATLAS_URI`: ✅ (working - connects successfully)
- `NODE_VERSION`: "20" ✅
- `NODE_ENV`: "production" ✅

## render.yaml Configuration
```yaml
services:
  - type: web
    name: tex-tailor-backend
    env: docker
    plan: free
    healthCheckPath: /health  # ← This should work
    dockerfilePath: ./Dockerfile
```

## Key Files Modified
1. `./Dockerfile` - Root dockerfile (used by Render)
2. `./render.yaml` - Render service configuration
3. `frontend/server/index.js` - Express server configuration
4. Frontend auth files - Login/Register/Welcome pages

## Next Investigation Steps
1. ✅ Check if `/health` endpoint is actually accessible
2. ✅ Add root route handler to prevent 404s
3. ✅ Investigate why npm process receives SIGTERM
4. ✅ Check if health check is causing process termination
5. ✅ Review Express server middleware configuration

## FINAL FIX APPLIED (Attempt 5)
**Root Cause**: Port mismatch between Render's expected port (10000) and application's default port (3001)

**Solution Applied**:
1. **Port Configuration**: Changed `PORT` default from 3001 to 10000 in `frontend/server/index.js`
2. **Docker Port**: Updated `EXPOSE 3001` to `EXPOSE 10000` in `Dockerfile`
3. **Root Route**: Added `GET /` and `HEAD /` handlers to prevent 404 errors
4. **Health Check**: Ensured `/health` endpoint is properly accessible

**Expected Result**: Server should now start on port 10000 and respond to Render's health checks without SIGTERM termination.

## Test Commands for Verification
```bash
# Test health endpoint
curl -I https://tex-tailor-backend.onrender.com/health

# Test root endpoint
curl https://tex-tailor-backend.onrender.com/

# Test HEAD request (what Render health check uses)
curl -I https://tex-tailor-backend.onrender.com/

# Test API endpoints
curl https://tex-tailor-backend.onrender.com/api/auth/login

# Test database health
curl https://tex-tailor-backend.onrender.com/api/applications/health
```

## Expected Working State
- Backend serves API endpoints only (`/health`, `/api/auth/*`, `/api/*`)
- Frontend (Vercel) connects to backend via `VITE_API_URL`
- Users can register/login through frontend
- No static file serving from backend