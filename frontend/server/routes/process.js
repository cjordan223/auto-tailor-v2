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

// Configure multer for file uploads
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
    // Allow tex, txt, pdf, doc, docx files
    const allowedTypes = ['.tex', '.txt', '.pdf', '.doc', '.docx']
    const ext = path.extname(file.originalname).toLowerCase()
    
    if (allowedTypes.includes(ext)) {
      cb(null, true)
    } else {
      cb(new Error(`File type ${ext} not allowed`))
    }
  }
})

// Process resume endpoint
router.post('/', upload.fields([
  { name: 'resume', maxCount: 1 },
  { name: 'jobDescription', maxCount: 1 }
]), async (req, res) => {
  try {
    const { provider = 'gemini', model = 'gemini-1.5-flash', jobDescriptionText } = req.body
    const resumeFile = req.files?.resume?.[0]
    const jobFile = req.files?.jobDescription?.[0]
    
    // Validate inputs
    if (!resumeFile) {
      return res.status(400).json({ message: 'Resume file is required' })
    }
    
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
    
    // Move resume file to job directory
    const resumePath = path.join(tempDir, 'resume' + path.extname(resumeFile.originalname))
    await fs.copyFile(resumeFile.path, resumePath)
    await fs.unlink(resumeFile.path) // Clean up original upload
    
    // If job file exists, move it too
    if (jobFile) {
      const jobPath = path.join(tempDir, 'job-description' + path.extname(jobFile.originalname))
      await fs.copyFile(jobFile.path, jobPath)
      await fs.unlink(jobFile.path) // Clean up original upload
      jobDescriptionPath = jobPath
    }
    
    // Start processing in background
    processResumeAsync(jobId, resumePath, jobDescriptionPath, provider, model)
    
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
async function processResumeAsync(jobId, resumePath, jobDescriptionPath, provider, model) {
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
    
    // Execute the Python workflow
    const child = spawn('bash', [cliPath, jobDescriptionPath], {
      cwd: path.join(__dirname, '../../..'), // Root project directory
      stdio: ['pipe', 'pipe', 'pipe'],
      env: {
        ...process.env,
        PROVIDER: provider,
        MODEL: model
      }
    })
    
    let stdout = ''
    let stderr = ''
    
    child.stdout.on('data', (data) => {
      stdout += data.toString()
      console.log(`[${jobId}] stdout:`, data.toString())
    })
    
    child.stderr.on('data', (data) => {
      stderr += data.toString()
      console.error(`[${jobId}] stderr:`, data.toString())
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
 * Update job status file
 */
async function updateStatus(statusFile, status) {
  try {
    await fs.writeFile(statusFile, JSON.stringify({
      ...status,
      updatedAt: new Date().toISOString()
    }, null, 2))
  } catch (error) {
    console.error('Error updating status file:', error)
  }
}

export default router