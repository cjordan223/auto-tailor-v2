import express from 'express'
import multer from 'multer'
import { spawn } from 'child_process'
import path from 'path'
import fs from 'fs/promises'
import { v4 as uuidv4 } from 'uuid'
import { fileURLToPath } from 'url'

const __filename = fileURLToPath(import.meta.url)
const __dirname = path.dirname(__filename)

const router = express.Router()

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
    const baselineResumePath = path.join(__dirname, '../../../Baseline_Resume/Conner_Jordan_Software_Engineer llm_ready.tex')
    
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
    processResumeAsync(jobId, baselineResumePath, jobDescriptionPath, provider, model, apiKeys)
    
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
async function processResumeAsync(jobId, resumePath, jobDescriptionPath, provider, model, apiKeys = {}) {
  const tempDir = path.join(__dirname, '../../temp', jobId)
  const statusFile = path.join(tempDir, 'status.json')
  
  try {
    // Update status
    await updateStatus(statusFile, { 
      status: 'processing', 
      progress: 10,
      step: 'Initializing...'
    })
    
    // Find the Python CLI script
    const cliPath = path.join(__dirname, '../../../run_workflow_clean.sh')
    
    // Check if CLI exists
    try {
      await fs.access(cliPath)
    } catch (error) {
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
      // Override with frontend API keys only if they have actual values
      ...(apiKeys.GEMINI_API_KEY && apiKeys.GEMINI_API_KEY.trim() && { GEMINI_API_KEY: apiKeys.GEMINI_API_KEY }),
      ...(apiKeys.OPENAI_API_KEY && apiKeys.OPENAI_API_KEY.trim() && { OPENAI_API_KEY: apiKeys.OPENAI_API_KEY }),
      ...(apiKeys.OLLAMA_BASE_URL && apiKeys.OLLAMA_BASE_URL.trim() && { OLLAMA_BASE_URL: apiKeys.OLLAMA_BASE_URL })
    }
    
    // Debug logging
    console.log(`[${jobId}] Environment check:`)
    console.log(`[${jobId}] - GEMINI_API_KEY from env: ${process.env.GEMINI_API_KEY ? 'SET' : 'NOT SET'}`)
    console.log(`[${jobId}] - OPENAI_API_KEY from env: ${process.env.OPENAI_API_KEY ? 'SET' : 'NOT SET'}`)
    console.log(`[${jobId}] - Frontend apiKeys:`, Object.keys(apiKeys))

    // Execute the Python workflow
    const child = spawn('bash', [cliPath, jobDescriptionPath], {
      cwd: path.join(__dirname, '../../..'), // Root project directory
      stdio: ['pipe', 'pipe', 'pipe'],
      env: mergedEnv
    })
    
    let stdout = ''
    let stderr = ''
    
    child.stdout.on('data', (data) => {
      const output = data.toString()
      stdout += output
      console.log(`[${jobId}] stdout:`, output)
      
      // Parse output for meaningful progress updates
      parseOutputAndUpdateStatus(statusFile, output, jobId)
    })
    
    child.stderr.on('data', (data) => {
      const output = data.toString()
      stderr += output
      console.error(`[${jobId}] stderr:`, output)
      
      // Parse stderr for errors and progress
      parseOutputAndUpdateStatus(statusFile, output, jobId, true)
    })
    
    child.on('close', async (code) => {
      try {
        if (code === 0) {
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
          
          await updateStatus(statusFile, { 
            status: 'completed', 
            progress: 100,
            step: 'Processing complete!',
            files: outputFiles,
            completedAt: new Date().toISOString()
          })
          
        } else {
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
    await updateStatus(statusFile, { 
      status: 'error', 
      progress: 0,
      step: 'Processing failed',
      error: error.message
    })
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
      if (line.includes('🔄 Processing job description')) {
        statusUpdate = { 
          status: 'processing', 
          progress: 10, 
          step: 'Processing job description...',
          detail: 'Initializing workflow and reading job requirements'
        }
      } else if (line.includes('✓ Initialization complete')) {
        statusUpdate = { 
          status: 'processing', 
          progress: 20, 
          step: 'Initialization complete',
          detail: 'Baseline files prepared with LLM markers'
        }
      } else if (line.includes('Extracted base text to')) {
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
      } else if (line.includes('✓') && line.includes('edits applied')) {
        statusUpdate = { 
          status: 'processing', 
          progress: 70, 
          step: 'Applying edits to documents',
          detail: 'Updating resume and cover letter with AI-generated content'
        }
      } else if (line.includes('📄 Generating PDFs') || line.includes('render')) {
        statusUpdate = { 
          status: 'processing', 
          progress: 80, 
          step: 'Generating PDF files...',
          detail: 'Compiling LaTeX to PDF using latexmk'
        }
      } else if (line.includes('✅ Workflow complete')) {
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

export default router