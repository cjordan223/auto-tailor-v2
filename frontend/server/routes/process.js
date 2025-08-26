import express from 'express'
import multer from 'multer'
import { spawn } from 'child_process'
import path from 'path'
import fs from 'fs/promises'
import { v4 as uuidv4 } from 'uuid'
import { fileURLToPath } from 'url'
import { workflowLogger } from '../utils/workflowLogger.js'
import applicationService from '../services/ApplicationService.js'

const __filename = fileURLToPath(import.meta.url)
const __dirname = path.dirname(__filename)

const router = express.Router()

/**
 * Save completed application to MongoDB database
 */
async function saveApplicationToDatabase(jobId, tempDir, jobDescriptionPath, provider, model, outputFiles) {
  try {
    // Only save if application service is available
    if (!applicationService.db) {
      console.log('📚 Database not connected - skipping application save')
      return
    }

    // Read job description
    const jobDescription = await fs.readFile(jobDescriptionPath, 'utf8')
    
    // Read generated edits.json if available
    let edits = null
    const editsPath = path.join(tempDir, 'edits.json')
    try {
      const editsContent = await fs.readFile(editsPath, 'utf8')
      edits = JSON.parse(editsContent)
    } catch (error) {
      console.warn('Could not read edits.json:', error.message)
    }

    // Extract job details from description
    const jobTitle = extractJobTitle(jobDescription)
    const companyName = extractCompanyName(jobDescription)
    
    // Build file references
    const files = {
      resume: {
        url: outputFiles.includes('Conner_Jordan_Software_Engineer.tuned.pdf') 
          ? `/static/${jobId}/Conner_Jordan_Software_Engineer.tuned.pdf` 
          : null,
        storageKey: `${jobId}/Conner_Jordan_Software_Engineer.tuned.pdf`
      },
      coverLetter: {
        url: outputFiles.includes('Conner_Jordan_Cover_Letter.tuned.pdf')
          ? `/static/${jobId}/Conner_Jordan_Cover_Letter.tuned.pdf`
          : null,
        storageKey: `${jobId}/Conner_Jordan_Cover_Letter.tuned.pdf`
      }
    }

    // Build application data
    const applicationData = {
      jobTitle: jobTitle,
      companyName: companyName,
      jobDescription: jobDescription,
      location: null, // Could be extracted from JD in the future
      
      resume: {
        fileName: 'Conner_Jordan_Software_Engineer.tuned.pdf',
        summary: edits?.summary?.replace || null,
        skills: edits?.skills || {}
      },
      
      coverLetter: {
        fileName: 'Conner_Jordan_Cover_Letter.tuned.pdf',
        paragraphs: edits?.cover_letter?.paragraphs || []
      },

      generationMeta: {
        provider: provider,
        model: model,
        processingTime: 0, // Could be calculated
        validationPassed: true
      },

      files: files,

      searchMeta: {
        keywords: extractKeywords(jobDescription),
        jobType: extractJobType(jobDescription)
      }
    }

    // Save to database
    const result = await applicationService.createApplication('temp_user', applicationData)
    
    if (result.success) {
      console.log(`💾 Saved application to database: ${result.applicationId}`)
      console.log(`📄 Company: ${companyName}, Position: ${jobTitle}`)
    } else {
      console.error('Failed to save application:', result.error)
    }

  } catch (error) {
    console.error('Database save error:', error)
    throw error
  }
}

/**
 * Simple extraction functions for job details
 */
function extractJobTitle(jobDescription) {
  // Look for common patterns
  const patterns = [
    /Position:\s*([^\n\r]+)/i,
    /Role:\s*([^\n\r]+)/i,
    /Job Title:\s*([^\n\r]+)/i,
    /seeking\s+(?:a\s+)?([A-Z][a-zA-Z\s]+?)(?:\s+at|\s*,|\s*\.)/i,
    /hiring\s+(?:a\s+)?([A-Z][a-zA-Z\s]+?)(?:\s+to|\s*,|\s*\.)/i
  ]
  
  for (const pattern of patterns) {
    const match = jobDescription.match(pattern)
    if (match) {
      return match[1].trim()
    }
  }
  
  return 'Software Engineer' // Default fallback
}

function extractCompanyName(jobDescription) {
  // Look for common patterns
  const patterns = [
    /Company:\s*([^\n\r,]+)/i,
    /at\s+([A-Z][a-zA-Z\s&.,]+?)(?:\s+is\s|\s*,|\s*\.|$)/i,
    /join\s+([A-Z][a-zA-Z\s&.,]+?)(?:\s+as\s|\s*,|\s*\.|$)/i,
    /([A-Z][a-zA-Z\s&.,]+?)\s+is\s+(?:seeking|hiring|looking)/i
  ]
  
  for (const pattern of patterns) {
    const match = jobDescription.match(pattern)
    if (match) {
      let company = match[1].trim()
      // Clean up common suffixes
      company = company.replace(/\s+(Inc\.?|LLC\.?|Ltd\.?|Corp\.?|Corporation)\.?$/i, '')
      return company
    }
  }
  
  return 'Unknown Company' // Default fallback
}

function extractKeywords(jobDescription) {
  // Extract technical terms and skills
  const techKeywords = [
    'python', 'javascript', 'typescript', 'java', 'go', 'rust', 'c++',
    'react', 'vue', 'angular', 'node', 'express',
    'aws', 'azure', 'gcp', 'docker', 'kubernetes',
    'mongodb', 'postgresql', 'mysql', 'redis',
    'git', 'ci/cd', 'jenkins', 'github actions',
    'security', 'authentication', 'oauth', 'saml'
  ]
  
  const foundKeywords = []
  const lowerDescription = jobDescription.toLowerCase()
  
  for (const keyword of techKeywords) {
    if (lowerDescription.includes(keyword)) {
      foundKeywords.push(keyword)
    }
  }
  
  return foundKeywords.slice(0, 10) // Limit to 10 keywords
}

function extractJobType(jobDescription) {
  const lowerDescription = jobDescription.toLowerCase()
  
  if (lowerDescription.includes('remote') || lowerDescription.includes('work from home')) {
    return 'remote'
  } else if (lowerDescription.includes('contract') || lowerDescription.includes('contractor')) {
    return 'contract'
  } else if (lowerDescription.includes('part-time')) {
    return 'part-time'
  } else {
    return 'full-time'
  }
}

// Configure multer for file uploads (job description only)
const storage = multer.diskStorage({
  destination: async (req, file, cb) => {
    const tempDir = path.join(__dirname, '../../temp')
    try {
      await fs.mkdir(tempDir, { recursive: true })
      cb(null, tempDir)
    } catch (error) {
      cb(error)
    }
  },
  filename: (req, file, cb) => {
    const uniqueSuffix = Date.now() + '-' + Math.round(Math.random() * 1E9)
    cb(null, file.fieldname + '-' + uniqueSuffix + path.extname(file.originalname))
  }
})

const upload = multer({ 
  storage,
  limits: {
    fileSize: 10 * 1024 * 1024 // 10MB limit
  },
  fileFilter: (req, file, cb) => {
    // Allow txt, pdf, doc, docx files for job descriptions
    const allowedTypes = ['.txt', '.pdf', '.doc', '.docx']
    const ext = path.extname(file.originalname).toLowerCase()
    
    if (allowedTypes.includes(ext)) {
      cb(null, true)
    } else {
      cb(new Error(`File type ${ext} not allowed`))
    }
  }
})

// TODO: Custom LaTeX upload support
// Currently uses pre-configured baseline resume with LLM markers
// Future: Allow users to upload custom LaTeX templates
// Requires: Marker detection, template validation, chunk extraction

// Process resume endpoint
router.post('/', upload.single('jobDescription'), async (req, res) => {
  try {
    const { 
      provider = 'gemini', 
      model = 'gemini-1.5-flash', 
      personality = 'career_savvy_colleague',
      jobDescriptionText,
      apiKeys: apiKeysString = '{}' // API keys from frontend as JSON string
    } = req.body
    
    // Parse API keys JSON
    let apiKeys = {}
    try {
      apiKeys = JSON.parse(apiKeysString)
    } catch (error) {
      console.warn('Failed to parse API keys:', error.message)
      apiKeys = {}
    }
    const jobFile = req.file
    
    // Validate inputs
    if (!jobFile && !jobDescriptionText) {
      return res.status(400).json({ message: 'Job description (file or text) is required' })
    }
    
    // Generate unique job ID
    const jobId = uuidv4()
    const tempDir = path.join(__dirname, '../../temp', jobId)
    await fs.mkdir(tempDir, { recursive: true })
    
    // Save job description text if provided
    let jobDescriptionPath = jobFile?.path
    if (jobDescriptionText) {
      jobDescriptionPath = path.join(tempDir, 'job-description.txt')
      await fs.writeFile(jobDescriptionPath, jobDescriptionText, 'utf8')
    }
    
    // Use hardcoded baseline resume path
    const baselineResumePath = path.join(__dirname, '../../../templates/Baseline_Resume/Conner_Jordan_Software_Engineer llm_ready.tex')
    
    // Verify baseline resume exists
    try {
      await fs.access(baselineResumePath)
    } catch (error) {
      return res.status(500).json({ 
        message: 'Baseline resume template not found. Please ensure the template file exists.' 
      })
    }
    
    // If job file exists, move it to job directory
    if (jobFile) {
      const jobPath = path.join(tempDir, 'job-description' + path.extname(jobFile.originalname))
      await fs.copyFile(jobFile.path, jobPath)
      await fs.unlink(jobFile.path) // Clean up original upload
      jobDescriptionPath = jobPath
    }
    
    // Start processing in background
    processResumeAsync(jobId, baselineResumePath, jobDescriptionPath, provider, model, personality, apiKeys)
    
    // Return job ID immediately
    res.json({
      jobId,
      status: 'processing',
      message: 'Resume processing started'
    })
    
  } catch (error) {
    console.error('Process error:', error)
    res.status(500).json({ message: error.message })
  }
})

/**
 * Process resume asynchronously using the Python CLI
 */
async function processResumeAsync(jobId, resumePath, jobDescriptionPath, provider, model, personality, apiKeys = {}) {
  const tempDir = path.join(__dirname, '../../temp', jobId)
  const statusFile = path.join(tempDir, 'status.json')
  
  try {
    // Start workflow logging
    await workflowLogger.startWorkflow(jobId)
    
    // Log workflow start
    await workflowLogger.writeWorkflowLog(jobId, `Workflow started - Provider: ${provider}, Model: ${model}, Personality: ${personality}`)
    
    // Update status with original generation settings
    await updateStatus(statusFile, { 
      status: 'processing', 
      progress: 10,
      step: 'Initializing...',
      originalSettings: {
        provider,
        model,
        personality
      }
    })
    
    // Find the Python CLI script
    const cliPath = path.join(__dirname, '../../../scripts/run_workflow_clean.sh')
    
    // Debug path resolution
    console.log(`[${jobId}] __dirname: ${__dirname}`)
    console.log(`[${jobId}] CLI path: ${cliPath}`)
    console.log(`[${jobId}] Working directory: ${path.join(__dirname, '../..')}`)
    
    // Check if CLI exists
    try {
      await fs.access(cliPath)
      console.log(`[${jobId}] CLI script found and accessible`)
    } catch (error) {
      console.error(`[${jobId}] CLI script not found: ${error.message}`)
      throw new Error(`Python CLI not found at ${cliPath}`)
    }
    
    await updateStatus(statusFile, { 
      status: 'processing', 
      progress: 30,
      step: 'Running AI analysis...'
    })
    
    // Merge frontend API keys with environment variables (frontend takes precedence only if provided)
    const mergedEnv = {
      ...process.env,
      PROVIDER: provider,
      MODEL: model,
      PERSONALITY: personality,
      // Override with frontend API keys only if they have actual values
      ...(apiKeys.GEMINI_API_KEY && apiKeys.GEMINI_API_KEY.trim() && { GEMINI_API_KEY: apiKeys.GEMINI_API_KEY }),
      ...(apiKeys.OPENAI_API_KEY && apiKeys.OPENAI_API_KEY.trim() && { OPENAI_API_KEY: apiKeys.OPENAI_API_KEY }),
      ...(apiKeys.MISTRAL_API_KEY && apiKeys.MISTRAL_API_KEY.trim() && { MISTRAL_API_KEY: apiKeys.MISTRAL_API_KEY }),
      ...(apiKeys.GROQ_API_KEY && apiKeys.GROQ_API_KEY.trim() && { GROQ_API_KEY: apiKeys.GROQ_API_KEY }),
      ...(apiKeys.OLLAMA_BASE_URL && apiKeys.OLLAMA_BASE_URL.trim() && { OLLAMA_BASE_URL: apiKeys.OLLAMA_BASE_URL })
    }
    
    // Debug logging
    console.log(`[${jobId}] Environment check:`)
    console.log(`[${jobId}] - GEMINI_API_KEY from env: ${process.env.GEMINI_API_KEY ? 'SET' : 'NOT SET'}`)
    console.log(`[${jobId}] - OPENAI_API_KEY from env: ${process.env.OPENAI_API_KEY ? 'SET' : 'NOT SET'}`)
    console.log(`[${jobId}] - Frontend apiKeys:`, Object.keys(apiKeys))
    console.log(`[${jobId}] - Merged GEMINI_API_KEY: ${mergedEnv.GEMINI_API_KEY ? 'SET' : 'NOT SET'}`)
    console.log(`[${jobId}] - Merged OPENAI_API_KEY: ${mergedEnv.OPENAI_API_KEY ? 'SET' : 'NOT SET'}`)
    console.log(`[${jobId}] - Provider: ${provider}, Model: ${model}, Personality: ${personality}`)

    // Execute the Python workflow directly using venv Python
    // In Docker production, Python is in PATH due to ENV PATH="/opt/venv/bin:$PATH"
    const venvPython = process.env.NODE_ENV === 'production' ? 'python' : path.join(__dirname, '../../../venv/bin/python')
    
    // Ensure output directory exists before running workflow
    const projectRoot = path.join(__dirname, '../../..')
    const outDir = path.join(projectRoot, 'out')
    try {
      await fs.mkdir(outDir, { recursive: true })
      console.log(`[${jobId}] Created output directory: ${outDir}`)
    } catch (error) {
      console.log(`[${jobId}] Output directory already exists or error:`, error.message)
    }
    
    // Run the complete workflow using Python CLI directly
    const child = spawn(venvPython, ['-m', 'tex_tailor.cli', 'workflow', jobDescriptionPath], {
      cwd: projectRoot, // Project root for venv and paths
      stdio: ['pipe', 'pipe', 'pipe'],
      env: mergedEnv,
      timeout: 600000 // 10 minute timeout
    })
    
    let stdout = ''
    let stderr = ''
    
    child.stdout.on('data', (data) => {
      const output = data.toString()
      stdout += output
      console.log(`[${jobId}] stdout:`, output)
      
      // Use workflow logger to filter and log meaningful output
      workflowLogger.logServerOutput(jobId, output, false)
      
      // Parse output for meaningful progress updates
      try {
        parseOutputAndUpdateStatus(statusFile, output, jobId)
      } catch (parseError) {
        console.error(`[${jobId}] Error parsing stdout:`, parseError)
        // Ensure job status is preserved even if parsing fails
        try {
          await updateStatus(statusFile, { 
            status: 'processing',
            step: 'Processing...',
            detail: 'Workflow in progress'
          })
        } catch (statusError) {
          console.error(`[${jobId}] Failed to preserve status:`, statusError)
        }
      }
    })
    
    child.stderr.on('data', (data) => {
      const output = data.toString()
      stderr += output
      console.error(`[${jobId}] stderr:`, output)
      
      // Use workflow logger to filter and log meaningful errors
      workflowLogger.logServerOutput(jobId, output, true)
      
      // Parse stderr for errors and progress
      try {
        parseOutputAndUpdateStatus(statusFile, output, jobId, true)
      } catch (parseError) {
        console.error(`[${jobId}] Error parsing stderr:`, parseError)
        // Ensure job status is preserved even if parsing fails
        try {
          await updateStatus(statusFile, { 
            status: 'processing',
            step: 'Processing...',
            detail: 'Workflow in progress'
          })
        } catch (statusError) {
          console.error(`[${jobId}] Failed to preserve status:`, statusError)
        }
      }
    })
    
    child.on('error', async (error) => {
      console.error(`[${jobId}] Process error:`, error)
      await workflowLogger.writeWorkflowLog(jobId, `Process spawn error: ${error.message}`, 'error')
      
      await updateStatus(statusFile, { 
        status: 'error', 
        progress: 0,
        step: 'Failed to start processing',
        error: `Failed to spawn Python process: ${error.message}`
      })
    })
    
    child.on('close', async (code) => {
      try {
        if (code === 0) {
          await workflowLogger.writeWorkflowLog(jobId, 'Workflow completed successfully', 'success')
          
          await updateStatus(statusFile, { 
            status: 'processing', 
            progress: 80,
            step: 'Copying output files...'
          })
          
          // Copy generated files to temp directory
          const outputDir = path.join(__dirname, '../../../out')
          
          // List of expected output files
          const outputFiles = [
            'Conner_Jordan_Software_Engineer.tuned.pdf',
            'Conner_Jordan_Cover_Letter.tuned.pdf',
            'Conner_Jordan_Software_Engineer.tuned.tex',
            'Conner_Jordan_Cover_Letter.tuned.tex',
            'edits.json'
          ]
          
          for (const file of outputFiles) {
            const sourcePath = path.join(outputDir, file)
            const destPath = path.join(tempDir, file)
            
            try {
              await fs.copyFile(sourcePath, destPath)
            } catch (error) {
              console.warn(`Could not copy ${file}:`, error.message)
            }
          }
          
          // Save to database if MongoDB is connected
          try {
            await saveApplicationToDatabase(jobId, tempDir, jobDescriptionPath, provider, model, outputFiles)
          } catch (dbError) {
            console.warn(`Database save failed for job ${jobId}:`, dbError.message)
            // Don't fail the entire workflow if database save fails
          }
          
          await updateStatus(statusFile, { 
            status: 'completed', 
            progress: 100,
            step: 'Processing complete!',
            files: outputFiles,
            completedAt: new Date().toISOString()
          })
          
        } else {
          await workflowLogger.writeWorkflowLog(jobId, `Workflow failed with exit code ${code}`, 'error')
          
          await updateStatus(statusFile, { 
            status: 'error', 
            progress: 0,
            step: 'Processing failed',
            error: `Process exited with code ${code}`,
            stderr: stderr.slice(-500), // Last 500 chars of stderr
            stdout: stdout.slice(-500)  // Last 500 chars of stdout
          })
        }
      } catch (error) {
        console.error(`Error updating status for job ${jobId}:`, error)
      }
    })
    
  } catch (error) {
    console.error(`Processing error for job ${jobId}:`, error)
    await workflowLogger.writeWorkflowLog(jobId, `Processing error: ${error.message}`, 'error')
    
    await updateStatus(statusFile, { 
      status: 'error', 
      progress: 0,
      step: 'Processing failed',
      error: error.message
    })
  } finally {
    // End workflow logging
    await workflowLogger.endWorkflow()
  }
}

/**
 * Parse CLI output and update status with detailed progress
 */
async function parseOutputAndUpdateStatus(statusFile, output, jobId, isStderr = false) {
  try {
    const lines = output.split('\n').filter(line => line.trim())
    
    for (const line of lines) {
      let statusUpdate = null
      
      // Parse different types of progress indicators
      if (line.includes('🔄 Processing job description') || line.includes('🔄 Step 1: Initializing')) {
        statusUpdate = { 
          status: 'processing', 
          progress: 10, 
          step: 'Processing job description...',
          detail: 'Initializing workflow and reading job requirements'
        }
      } else if (line.includes('✓ Initialization complete') || line.includes('✅ Initialization complete')) {
        statusUpdate = { 
          status: 'processing', 
          progress: 20, 
          step: 'Initialization complete',
          detail: 'Baseline files prepared with LLM markers'
        }
      } else if (line.includes('Extracted base text to') || line.includes('✅ Text extraction complete')) {
        const match = line.match(/Found (\d+) editable chunks/)
        const chunks = match ? match[1] : 'multiple'
        statusUpdate = { 
          status: 'processing', 
          progress: 30, 
          step: 'Text extraction complete',
          detail: `Extracted ${chunks} editable chunks from LaTeX files`
        }
      } else if (line.includes('🧠') || line.includes('Sending to') || line.includes('API')) {
        statusUpdate = { 
          status: 'processing', 
          progress: 40, 
          step: 'AI analysis in progress...',
          detail: 'Sending content to AI provider for analysis'
        }
      } else if (line.includes('Generated') && line.includes('edits')) {
        const match = line.match(/Generated (\d+) edits/)
        const edits = match ? match[1] : 'multiple'
        statusUpdate = { 
          status: 'processing', 
          progress: 60, 
          step: 'AI analysis complete',
          detail: `Generated ${edits} targeted edits based on job requirements`
        }
      } else if (line.includes('✓') && line.includes('edits applied') || line.includes('✅ Edits applied')) {
        statusUpdate = { 
          status: 'processing', 
          progress: 70, 
          step: 'Applying edits to documents',
          detail: 'Updating resume and cover letter with AI-generated content'
        }
      } else if (line.includes('📄 Generating PDFs') || line.includes('render') || line.includes('🔄 Step 6: Rendering PDFs')) {
        statusUpdate = { 
          status: 'processing', 
          progress: 80, 
          step: 'Generating PDF files...',
          detail: 'Compiling LaTeX to PDF using latexmk'
        }
      } else if (line.includes('✅ Workflow complete') || line.includes('🎉 Workflow completed successfully')) {
        statusUpdate = { 
          status: 'processing', 
          progress: 90, 
          step: 'Workflow complete',
          detail: 'Finalizing output files and cleaning up'
        }
      }
      
      // Handle errors
      if (isStderr || line.includes('Error') || line.includes('error') || line.includes('Failed')) {
        if (line.includes('API') || line.includes('authentication') || line.includes('key')) {
          statusUpdate = { 
            status: 'error', 
            progress: 0, 
            step: 'API Authentication Error',
            detail: 'Invalid or missing API key. Please check your credentials.',
            error: line.trim()
          }
        } else if (line.includes('timeout') || line.includes('Timeout')) {
          statusUpdate = { 
            status: 'error', 
            progress: 0, 
            step: 'Request Timeout',
            detail: 'AI provider request timed out. Please try again.',
            error: line.trim()
          }
        } else if (line.includes('rate limit') || line.includes('quota')) {
          statusUpdate = { 
            status: 'error', 
            progress: 0, 
            step: 'Rate Limit Exceeded',
            detail: 'API rate limit reached. Please wait before trying again.',
            error: line.trim()
          }
        } else {
          statusUpdate = { 
            status: 'error', 
            progress: 0, 
            step: 'Processing Error',
            detail: 'An error occurred during processing. Check logs for details.',
            error: line.trim()
          }
        }
      }
      
      // Provider detection
      if (line.includes('gemini') || line.includes('Gemini')) {
        statusUpdate = { ...statusUpdate, provider: 'Gemini' }
      } else if (line.includes('openai') || line.includes('OpenAI') || line.includes('gpt')) {
        statusUpdate = { ...statusUpdate, provider: 'OpenAI' }
      } else if (line.includes('ollama') || line.includes('Ollama')) {
        statusUpdate = { ...statusUpdate, provider: 'Ollama' }
      }
      
      // Update status if we found meaningful information
      if (statusUpdate) {
        console.log(`[${jobId}] Status update:`, statusUpdate)
        await updateStatus(statusFile, statusUpdate)
      }
    }
  } catch (error) {
    console.error(`[${jobId}] Error parsing output:`, error)
  }
}

/**
 * Update job status file
 */
async function updateStatus(statusFile, status) {
  try {
    // Read existing status to preserve fields
    let existingStatus = {}
    try {
      const existing = await fs.readFile(statusFile, 'utf8')
      existingStatus = JSON.parse(existing)
    } catch (_) {
      // File doesn't exist yet, use empty object
    }
    
    const updatedStatus = {
      ...existingStatus,
      ...status,
      updatedAt: new Date().toISOString()
    }
    
    await fs.writeFile(statusFile, JSON.stringify(updatedStatus, null, 2))
  } catch (error) {
    console.error('Error updating status file:', error)
  }
}

// Endpoint to get workflow log (now returns temp log for current run)
router.get('/log', async (req, res) => {
  try {
    const result = await workflowLogger.getTempLog()
    res.json(result)
  } catch (error) {
    res.status(500).json({
      success: false,
      error: error.message
    })
  }
})

// Endpoint to clear workflow log
router.delete('/log', async (req, res) => {
  try {
    const result = await workflowLogger.clearTempLog()
    res.json({
      success: result.success,
      message: result.success ? 'Workflow log cleared' : 'Failed to clear log',
      error: result.error
    })
  } catch (error) {
    res.status(500).json({
      success: false,
      error: error.message
    })
  }
})

export default router