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
app.use('/api/view', viewRoutes) // Dedicated view routes for inline PDF viewing
app.use('/api/status', statusRoutes)
app.use('/api/providers', providersRoutes)
app.use('/api/validate', validateRoutes)
app.use('/api/review', reviewRoutes)
app.use('/api/recompile', recompileRoutes)

// Results endpoint with validation status
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
    let skillsChanges = null
    let validationStatus = null
    let jobDescription = null
    
    if (status === 'completed') {
      // Load job description if available
      try {
        const jobDescPath = path.join(tempDir, 'job-description.txt')
        jobDescription = await fs.readFile(jobDescPath, 'utf-8')
      } catch (error) {
        // Job description not available, that's okay
        console.warn(`Could not load job description for job ${jobId}:`, error.message)
      }
      
      // Load edits.json to get validation status and suggested additions
      try {
        const editsPath = path.join(tempDir, 'edits.json')
        const editsRaw = await fs.readFile(editsPath, 'utf8')
        const edits = JSON.parse(editsRaw)
        
        // Extract validation status from suggested_additions
        if (edits.suggested_additions) {
          const flaggedSkills = edits.suggested_additions
            .filter(suggestion => suggestion.why && suggestion.why.includes('Skills validation:'))
            .map(suggestion => {
              const whyMatch = suggestion.why.match(/Skills validation: (.+?) \(confidence: (.+?)\)/)
              return {
                skill: suggestion.term,
                reason: whyMatch ? whyMatch[1] : suggestion.why,
                confidence: whyMatch ? whyMatch[2] : 'low'
              }
            })
          
          // Calculate confidence level
          let confidence = 'high'
          if (flaggedSkills.length > 2) {
            confidence = 'low'
          } else if (flaggedSkills.length > 0) {
            confidence = 'medium'
          }
          
          validationStatus = {
            confidence,
            flaggedCount: flaggedSkills.length,
            flaggedSkills
          }
        }
        
        // Filter suggested additions to exclude validation-related ones
        suggestedAdditions = (edits.suggested_additions || []).filter(
          suggestion => !suggestion.why || !suggestion.why.includes('Skills validation:')
        )
        
        // Process skills changes
        if (edits.skills) {
          skillsChanges = {}
          for (const [category, skillEdit] of Object.entries(edits.skills)) {
            if (skillEdit.replace) {
              const newSkills = skillEdit.replace.split(',').map(s => s.trim()).filter(s => s)
              skillsChanges[category] = {
                added: newSkills,
                removed: []
              }
            }
          }
        }
        
      } catch (error) {
        console.warn(`Could not load edits.json for job ${jobId}:`, error.message)
      }
      
      // Try to get review data with multiple fallback strategies
      let reviewSuccess = false
      
      // Strategy 1: Try review API without provider (auto-detect)
      try {
        console.log('Attempting to fetch review data (auto-detect provider)...')
        const reviewResponse = await fetch(`http://localhost:${PORT}/api/review?format=json&jobId=${jobId}`)
        if (reviewResponse.ok) {
          const reviewResult = await reviewResponse.json()
          if (reviewResult.success && reviewResult.data) {
            console.log('Review data fetched successfully via auto-detect')
            reviewData = reviewResult.data
            reviewSuccess = true
          }
        } else {
          console.warn(`Review API returned ${reviewResponse.status}: ${reviewResponse.statusText}`)
        }
      } catch (error) {
        console.warn('Failed to fetch review data via auto-detect:', error.message)
      }
      
      // Strategy 2: If review API failed, create minimal reviewData
      if (!reviewSuccess) {
        try {
          console.log('Creating minimal review data from edits...')
          
          // Create minimal reviewData with computed statistics
          const totalChunksModified = edits ? 
            Object.keys(edits).filter(key => 
              key !== 'suggested_additions' && 
              edits[key] && 
              (typeof edits[key] === 'object' ? Object.keys(edits[key]).length > 0 : edits[key].length > 0)
            ).length : 0
          
          const skillsSectionsUpdated = edits?.skills ? Object.keys(edits.skills).length : 0
          const coverLetterParagraphs = edits?.cover_letter?.paragraphs?.length || 0
          const suggestedAdditionsCount = suggestedAdditions.length
          
          reviewData = {
            overview: totalChunksModified > 0 
              ? `Successfully analyzed and customized your resume with ${totalChunksModified} modifications, ${skillsSectionsUpdated} skills updates, and ${coverLetterParagraphs} cover letter adjustments. Generated ${suggestedAdditionsCount} additional recommendations based on the job description.`
              : 'Resume analysis completed successfully. Your documents have been generated and are ready for review.',
            statistics: {
              total_chunks_modified: totalChunksModified,
              skills_sections_updated: skillsSectionsUpdated,
              cover_letter_paragraphs: coverLetterParagraphs,
              suggested_additions: suggestedAdditionsCount
            }
          }
          
          console.log('Fallback data generated from edits.json:', {
            suggestedAdditionsCount,
            totalChunksModified,
            skillsSectionsUpdated,
            coverLetterParagraphs
          })
          
        } catch (fallbackError) {
          console.warn('Failed to read edits.json fallback:', fallbackError.message)
          // Provide minimal default data to ensure UI sections still appear
          suggestedAdditions = []
          reviewData = {
            overview: 'Resume generation completed successfully. Your customized documents are ready for download.',
            statistics: {
              total_chunks_modified: 0,
              skills_sections_updated: 0,
              cover_letter_paragraphs: 0,
              suggested_additions: 0
            }
          }
        }
      }

      // Get skills changes by comparing original and new skills
      try {
        const baseTextPath = path.join(__dirname, '../../out/base_text.json')
        const editsPath = path.join(tempDir, 'edits.json')
        
        // Read original skills from base_text.json
        const baseTextRaw = await fs.readFile(baseTextPath, 'utf8')
        const baseText = JSON.parse(baseTextRaw)
        const originalSkills = baseText.resume?.skills || {}
        
        // Read new skills from edits.json
        const editsRaw = await fs.readFile(editsPath, 'utf8')
        const edits = JSON.parse(editsRaw)
        const newSkills = edits.skills || {}
        
        // Compare skills and generate changes
        skillsChanges = {}
        for (const [category, newSkillData] of Object.entries(newSkills)) {
          const originalSkill = originalSkills[category] || ''
          // Handle null/empty values properly - if replace is null/empty/"null", use original
          const newSkill = (newSkillData.replace && newSkillData.replace.trim() && newSkillData.replace !== "null") ? newSkillData.replace : originalSkill
          
          if (originalSkill !== newSkill) {
            // Parse skills into arrays for comparison
            const originalItems = originalSkill.split(',').map(s => s.trim()).filter(s => s)
            const newItems = newSkill.split(',').map(s => s.trim()).filter(s => s)
            
            const originalSet = new Set(originalItems)
            const newSet = new Set(newItems)
            
            const removed = originalItems.filter(item => !newSet.has(item))
            const added = newItems.filter(item => !originalSet.has(item))
            
            if (removed.length > 0 || added.length > 0) {
              skillsChanges[category] = {
                original: originalSkill,
                new: newSkill,
                removed: removed,
                added: added
              }
            }
          }
        }
      } catch (error) {
        console.warn('Failed to generate skills changes:', error.message)
        skillsChanges = {}
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
      skillsChanges,
      validationStatus,
      jobDescription,
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