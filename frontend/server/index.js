import express from 'express'
import cors from 'cors'
import path from 'path'
import { fileURLToPath } from 'url'
import uploadRoutes from './routes/upload.js'
import processRoutes from './routes/process.js'
import downloadRoutes from './routes/download.js'
import statusRoutes from './routes/status.js'
import providersRoutes from './routes/providers.js'
import { errorHandler } from './middleware/errorHandler.js'
import { requestLogger } from './middleware/requestLogger.js'

const __filename = fileURLToPath(import.meta.url)
const __dirname = path.dirname(__filename)

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

// Results endpoint
app.get('/api/results/:jobId', async (req, res) => {
  try {
    const { jobId } = req.params
    
    // In a real app, this would fetch from a database
    // For now, we'll check if files exist
    const resultData = {
      jobId,
      status: 'completed',
      files: {
        resume: `/api/download/${jobId}/resume`,
        coverLetter: `/api/download/${jobId}/cover-letter`,
        edits: `/api/download/${jobId}/edits`
      },
      suggestedAdditions: [
        {
          term: "Example Skill",
          why: "Relevant to job requirements"
        }
      ],
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