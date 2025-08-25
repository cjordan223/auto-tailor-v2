import express from 'express'
import { spawn } from 'child_process'
import path from 'path'
import fs from 'fs/promises'
import { fileURLToPath } from 'url'
import { workflowLogger } from '../utils/workflowLogger.js'

const __filename = fileURLToPath(import.meta.url)
const __dirname = path.dirname(__filename)

const router = express.Router()

/**
 * Regenerate just the cover letter for an existing job
 * POST /api/regenerate/:jobId/cover-letter
 */
router.post('/:jobId/cover-letter', async (req, res) => {
  const jobId = req.params.jobId
  const { provider, model, personality } = req.body

  try {
    // Validate job exists
    const tempDir = path.join(__dirname, '../../temp', jobId)
    const statusFile = path.join(tempDir, 'status.json')
    
    try {
      await fs.access(tempDir)
    } catch (error) {
      return res.status(404).json({
        success: false,
        error: 'Job not found'
      })
    }

    // Start regeneration process
    await regenerateCoverLetterAsync(jobId, provider, model, personality)
    
    res.json({
      success: true,
      jobId: jobId,
      message: 'Cover letter regeneration started'
    })

  } catch (error) {
    console.error(`Error starting cover letter regeneration for job ${jobId}:`, error)
    res.status(500).json({
      success: false,
      error: error.message
    })
  }
})

/**
 * Get regeneration status
 * GET /api/regenerate/:jobId/status  
 */
router.get('/:jobId/status', async (req, res) => {
  const jobId = req.params.jobId
  
  try {
    const tempDir = path.join(__dirname, '../../temp', jobId)
    const statusFile = path.join(tempDir, 'regen-status.json')
    
    try {
      const statusContent = await fs.readFile(statusFile, 'utf8')
      const status = JSON.parse(statusContent)
      res.json(status)
    } catch (error) {
      if (error.code === 'ENOENT') {
        res.json({
          status: 'not_started',
          progress: 0,
          step: 'Waiting to start regeneration'
        })
      } else {
        throw error
      }
    }
  } catch (error) {
    console.error(`Error getting regeneration status for job ${jobId}:`, error)
    res.status(500).json({
      success: false,
      error: error.message
    })
  }
})

/**
 * Regenerate cover letter asynchronously
 */
async function regenerateCoverLetterAsync(jobId, provider = 'gemini', model = 'gemini-2.5-flash-lite', personality = 'career_savvy_colleague') {
  const tempDir = path.join(__dirname, '../../temp', jobId)
  const statusFile = path.join(tempDir, 'regen-status.json')
  
  try {
    await workflowLogger.startWorkflow(`${jobId}-regen`)
    await workflowLogger.writeWorkflowLog(jobId, `Cover letter regeneration started - Provider: ${provider}, Model: ${model}`)
    
    // Update regeneration status
    await updateRegenStatus(statusFile, {
      status: 'processing',
      progress: 10,
      step: 'Starting cover letter regeneration...',
      startedAt: new Date().toISOString()
    })

    // Read existing job description
    const jobDescriptionPath = path.join(tempDir, 'job-description.txt')
    let jobDescription
    try {
      jobDescription = await fs.readFile(jobDescriptionPath, 'utf8')
    } catch (error) {
      throw new Error('Job description not found - cannot regenerate cover letter')
    }

    // Use the isolated cover letter regeneration script
    const cliPath = path.join(__dirname, '../../../scripts/run_cover_letter_only.sh')

    await updateRegenStatus(statusFile, {
      status: 'processing',
      progress: 30,
      step: 'Analyzing job requirements...'
    })

    // Set up environment for isolated execution
    const env = {
      ...process.env,
      PROVIDER: provider,
      MODEL: model,
      PERSONALITY: personality,
      JOB_ID: jobId,
      OUTPUT_DIR: tempDir
    }

    // Spawn isolated cover letter process
    const child = spawn('bash', [cliPath, tempDir], {
      cwd: path.join(__dirname, '../../../'),
      env: env,
      stdio: ['pipe', 'pipe', 'pipe']
    })

    let stdout = ''
    let stderr = ''

    // Handle stdout
    child.stdout.on('data', (output) => {
      const outputStr = output.toString()
      stdout += outputStr
      console.log(`[${jobId}-regen] stdout:`, outputStr)
      workflowLogger.logServerOutput(`${jobId}-regen`, outputStr, false)
      
      // Parse output for progress updates
      parseRegenOutputAndUpdateStatus(statusFile, outputStr, jobId)
    })

    // Handle stderr  
    child.stderr.on('data', (output) => {
      const outputStr = output.toString()
      stderr += outputStr
      console.error(`[${jobId}-regen] stderr:`, outputStr)
      workflowLogger.logServerOutput(`${jobId}-regen`, outputStr, true)
    })

    // Handle process completion
    child.on('close', async (code) => {
      try {
        if (code === 0) {
          await workflowLogger.writeWorkflowLog(jobId, 'Cover letter regeneration completed successfully')
          
          // Copy regenerated cover letter files
          await copyRegeneratedFiles(tempDir, jobId)
          
          await updateRegenStatus(statusFile, {
            status: 'completed',
            progress: 100,
            step: 'Cover letter regeneration complete!',
            completedAt: new Date().toISOString()
          })
          
        } else {
          await workflowLogger.writeWorkflowLog(jobId, `Cover letter regeneration failed with exit code ${code}`, 'error')
          
          await updateRegenStatus(statusFile, {
            status: 'error',
            progress: 0,
            step: 'Regeneration failed',
            error: `Process exited with code ${code}`,
            stderr: stderr.slice(-500),
            stdout: stdout.slice(-500)
          })
        }
      } catch (error) {
        console.error(`Error updating regeneration status for job ${jobId}:`, error)
      }
    })
    
  } catch (error) {
    console.error(`Regeneration error for job ${jobId}:`, error)
    await workflowLogger.writeWorkflowLog(jobId, `Regeneration error: ${error.message}`, 'error')
    
    await updateRegenStatus(statusFile, {
      status: 'error', 
      progress: 0,
      step: 'Regeneration failed',
      error: error.message
    })
  } finally {
    await workflowLogger.endWorkflow()
  }
}

// Script file already exists at scripts/run_cover_letter_only.sh

/**
 * Copy regenerated cover letter files to temp directory
 */
async function copyRegeneratedFiles(tempDir, jobId) {
  try {
    const outputDir = path.join(__dirname, '../../../out')
    
    // Cover letter files to copy
    const coverLetterFiles = [
      'Conner_Jordan_Cover_Letter.tuned.pdf',
      'Conner_Jordan_Cover_Letter.tuned.tex'
    ]
    
    for (const file of coverLetterFiles) {
      const sourcePath = path.join(outputDir, file)
      const destPath = path.join(tempDir, file)
      
      try {
        await fs.copyFile(sourcePath, destPath)
        console.log(`✅ Copied regenerated file: ${file}`)
      } catch (error) {
        console.warn(`⚠️ Could not copy ${file}:`, error.message)
      }
    }
    
  } catch (error) {
    console.error('Error copying regenerated files:', error)
    throw error
  }
}

/**
 * Update regeneration status file
 */
async function updateRegenStatus(statusFile, status) {
  try {
    const statusContent = JSON.stringify(status, null, 2)
    await fs.writeFile(statusFile, statusContent, 'utf8')
  } catch (error) {
    console.error('Failed to update regeneration status:', error)
  }
}

/**
 * Parse regeneration output for progress updates
 */
async function parseRegenOutputAndUpdateStatus(statusFile, output, jobId) {
  try {
    const lines = output.split('\n').filter(line => line.trim())
    
    for (const line of lines) {
      let statusUpdate = null
      
      // Parse different types of progress indicators
      if (line.includes('🔄 Starting') || line.includes('propose')) {
        statusUpdate = {
          status: 'processing',
          progress: 20,
          step: 'Initializing cover letter generation...'
        }
      } else if (line.includes('🎭 Loaded personality')) {
        statusUpdate = {
          status: 'processing',
          progress: 40,
          step: 'Personality loaded, analyzing job requirements...'
        }
      } else if (line.includes('Generating') || line.includes('attempt')) {
        statusUpdate = {
          status: 'processing',
          progress: 60,
          step: 'AI generating new cover letter content...'
        }
      } else if (line.includes('Applying') || line.includes('edits')) {
        statusUpdate = {
          status: 'processing',
          progress: 80,
          step: 'Applying edits to cover letter...'
        }
      } else if (line.includes('PDF') || line.includes('Rendering')) {
        statusUpdate = {
          status: 'processing',
          progress: 90,
          step: 'Generating new cover letter PDF...'
        }
      }
      
      if (statusUpdate) {
        await updateRegenStatus(statusFile, statusUpdate)
      }
    }
  } catch (error) {
    console.error('Error parsing regeneration output:', error)
  }
}

export default router