import express from 'express'
import cors from 'cors'
import path from 'path'
import { fileURLToPath } from 'url'
import fs from 'fs/promises'
import dotenv from 'dotenv'
import uploadRoutes from './routes/upload.js'
import processRoutes from './routes/process.js'
import downloadRoutes from './routes/download.js'
import statusRoutes from './routes/status.js'
import providersRoutes from './routes/providers.js'
import validateRoutes from './routes/validate.js'
import reviewRoutes from './routes/review.js'
import { errorHandler } from './middleware/errorHandler.js'
import { requestLogger } from './middleware/requestLogger.js'

const __filename = fileURLToPath(import.meta.url)
const __dirname = path.dirname(__filename)

// Load .env file
const envPath = path.join(__dirname, '../../.env')
const envResult = dotenv.config({ path: envPath })

if (envResult.error) {
  console.log('📝 No .env file found, using system environment variables')
} else {
  console.log('✅ Loaded .env file successfully')
  // Show which API keys are available (without exposing the actual keys)
  const hasGemini = !!process.env.GEMINI_API_KEY
  const hasOpenAI = !!process.env.OPENAI_API_KEY
  const hasOllama = !!process.env.OLLAMA_BASE_URL
  console.log(`🔑 API Keys loaded: Gemini: ${hasGemini ? '✓' : '✗'}, OpenAI: ${hasOpenAI ? '✓' : '✗'}, Ollama: ${hasOllama ? '✓' : '✗'}`)
}

const app = express()
const PORT = process.env.PORT || 3001

// Middleware
app.use(cors({
  origin: process.env.FRONTEND_URL || 'http://localhost:3000',
  credentials: true
}))

app.use(express.json({ limit: '50mb' }))
app.use(express.urlencoded({ extended: true, limit: '50mb' }))
app.use(requestLogger)

// Static files (for serving generated PDFs temporarily)
app.use('/static', express.static(path.join(__dirname, '../temp')))

// Health check
app.get('/health', (req, res) => {
  res.json({ 
    status: 'healthy', 
    timestamp: new Date().toISOString(),
    service: 'tex-tailor-api'
  })
})

// API Routes
app.use('/api/upload', uploadRoutes)
app.use('/api/process', processRoutes)
app.use('/api/download', downloadRoutes)
app.use('/api/status', statusRoutes)
app.use('/api/providers', providersRoutes)
app.use('/api/validate', validateRoutes)
app.use('/api/review', reviewRoutes)

// Results endpoint
app.get('/api/results/:jobId', async (req, res) => {
  try {
    const { jobId } = req.params
    const tempDir = path.join(__dirname, '../temp', jobId)
    const statusFile = path.join(tempDir, 'status.json')

    let status = 'processing'
    let progress = 0
    let step = 'Initializing...'

    try {
      const statusRaw = await fs.readFile(statusFile, 'utf8')
      const statusJson = JSON.parse(statusRaw)
      status = statusJson.status || status
      progress = Number(statusJson.progress ?? progress)
      step = statusJson.step || step
    } catch (_) {
      // If status file not yet available, remain in processing
    }

    // Build file map only if completed
    const files = {}
    if (status === 'completed') {
      files.resume = `/api/download/${jobId}/resume`
      files.coverLetter = `/api/download/${jobId}/cover-letter`
      files.edits = `/api/download/${jobId}/edits`
    }

    // Get review data if completed
    let reviewData = null
    let suggestedAdditions = []
    
    if (status === 'completed') {
      try {
        // Call the review API to get actual data (use Ollama to avoid rate limits)
        const reviewResponse = await fetch(`http://localhost:${PORT}/api/review?format=json&provider=ollama`)
        if (reviewResponse.ok) {
          const reviewResult = await reviewResponse.json()
          if (reviewResult.success && reviewResult.data) {
            reviewData = reviewResult.data
            suggestedAdditions = reviewResult.data.raw_edits?.suggested_additions || []
          }
        }
      } catch (error) {
        console.warn('Failed to fetch review data:', error.message)
        // Fall back to empty array if review fails
        suggestedAdditions = []
      }
    }

    const resultData = {
      jobId,
      status,
      progress,
      step,
      files,
      suggestedAdditions,
      reviewData,
      createdAt: new Date().toISOString()
    }

    res.json(resultData)
  } catch (error) {
    res.status(500).json({ message: error.message })
  }
})

// History endpoint
app.get('/api/history', (req, res) => {
  // In a real app, this would fetch from a database
  res.json({ jobs: [] })
})

// Error handling
app.use(errorHandler)

// 404 handler
app.use('*', (req, res) => {
  res.status(404).json({ 
    message: 'Endpoint not found',
    path: req.originalUrl
  })
})

// Start server
app.listen(PORT, () => {
  console.log(`🚀 Tex-Tailor API Server running on port ${PORT}`)
  console.log(`📱 Frontend should connect to: http://localhost:${PORT}`)
  console.log(`🔍 Health check: http://localhost:${PORT}/health`)
})

export default app