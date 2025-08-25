import express from 'express'
import cors from 'cors'
import path from 'path'
import { fileURLToPath } from 'url'
import fs from 'fs/promises'
import dotenv from 'dotenv'
import uploadRoutes from './routes/upload.js'
import processRoutes from './routes/process.js'
import downloadRoutes from './routes/download.js'
import viewRoutes from './routes/view.js'
import statusRoutes from './routes/status.js'
import providersRoutes from './routes/providers.js'
import validateRoutes from './routes/validate.js'
import reviewRoutes from './routes/review.js'
import recompileRoutes from './routes/recompile.js'
import resultsRoutes from './routes/results.js'
import applicationsRoutes from './routes/applications.js'
import regenerateRoutes from './routes/regenerate.js'
import { errorHandler } from './middleware/errorHandler.js'
import { requestLogger } from './middleware/requestLogger.js'
import databaseConnection from './config/database.js'
import applicationService from './services/ApplicationService.js'

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
  const hasMistral = !!process.env.MISTRAL_API_KEY
  const hasGroq = !!process.env.GROQ_API_KEY
  const hasOllama = !!process.env.OLLAMA_BASE_URL
  const hasMongoDB = !!process.env.MONGODB_ATLAS_URI
  console.log(`🔑 API Keys loaded: Gemini: ${hasGemini ? '✓' : '✗'}, OpenAI: ${hasOpenAI ? '✓' : '✗'}, Mistral: ${hasMistral ? '✓' : '✗'}, Groq: ${hasGroq ? '✓' : '✗'}, Ollama: ${hasOllama ? '✓' : '✗'}`)
  console.log(`🗄️  Database: MongoDB: ${hasMongoDB ? '✓' : '✗'}`)
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
app.use('/api/view', viewRoutes) // Dedicated view routes for inline PDF viewing
app.use('/api/status', statusRoutes)
app.use('/api/providers', providersRoutes)
app.use('/api/validate', validateRoutes)
app.use('/api/review', reviewRoutes)
app.use('/api/recompile', recompileRoutes)
app.use('/api/results', resultsRoutes)
app.use('/api/applications', applicationsRoutes)
app.use('/api/regenerate', regenerateRoutes)

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

// Initialize database connection and start server
async function startServer() {
  try {
    // Connect to MongoDB Atlas if URI is provided
    if (process.env.MONGODB_ATLAS_URI && !process.env.MONGODB_ATLAS_URI.includes('<password>')) {
      console.log('🔗 Connecting to MongoDB Atlas...')
      try {
        await databaseConnection.connect()
        await applicationService.initialize()
        console.log('✅ Database services initialized')
      } catch (error) {
        console.error('⚠️  MongoDB connection failed:', error.message)
        console.log('🔄 Continuing without database - applications will not be saved')
        console.log('   Check your MONGODB_ATLAS_URI in .env file')
      }
    } else {
      console.log('⚠️  No valid MongoDB URI provided - database features disabled')
      console.log('   Replace <password> in MONGODB_ATLAS_URI in your .env file to enable database')
    }

    // Start the server
    app.listen(PORT, () => {
      console.log(`🚀 Tex-Tailor API Server running on port ${PORT}`)
      console.log(`📱 Frontend should connect to: http://localhost:${PORT}`)
      console.log(`🔍 Health check: http://localhost:${PORT}/health`)
      console.log(`📊 Applications API: http://localhost:${PORT}/api/applications`)
    })
  } catch (error) {
    console.error('❌ Failed to start server:', error)
    process.exit(1)
  }
}

// Graceful shutdown
process.on('SIGTERM', async () => {
  console.log('🛑 SIGTERM received, shutting down gracefully...')
  await databaseConnection.close()
  process.exit(0)
})

process.on('SIGINT', async () => {
  console.log('🛑 SIGINT received, shutting down gracefully...')
  await databaseConnection.close()
  process.exit(0)
})

startServer()

export default app