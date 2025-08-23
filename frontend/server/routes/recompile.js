import express from 'express'
import path from 'path'
import fs from 'fs/promises'
import { spawn } from 'child_process'
import { fileURLToPath } from 'url'

const __filename = fileURLToPath(import.meta.url)
const __dirname = path.dirname(__filename)

const router = express.Router()

// Recompile LaTeX content to PDF
router.post('/:jobId/:fileType', async (req, res) => {
  try {
    const { jobId, fileType } = req.params
    const { content } = req.body
    
    if (!content) {
      return res.status(400).json({ message: 'LaTeX content is required' })
    }
    
    if (!['resume', 'cover-letter'].includes(fileType)) {
      return res.status(400).json({ message: 'Invalid file type' })
    }
    
    const tempDir = path.join(__dirname, '../../temp', jobId)
    
    // Check if job directory exists
    try {
      await fs.access(tempDir)
    } catch (error) {
      return res.status(404).json({ message: 'Job directory not found' })
    }
    
    // Prepare Python CLI command
    const pythonScriptPath = path.join(__dirname, '../../../venv/bin/python3')
    const workingDir = path.join(__dirname, '../../..')
    
    const args = [
      '-m', 'tex_tailor.cli',
      'recompile',
      '--job-id', jobId,
      '--file-type', fileType,
      '--content', content,
      '--temp-dir', path.join(__dirname, '../../temp')
    ]
    
    // Execute recompile command
    const process = spawn(pythonScriptPath, args, {
      cwd: workingDir,
      stdio: ['pipe', 'pipe', 'pipe']
    })
    
    let stdout = ''
    let stderr = ''
    
    process.stdout.on('data', (data) => {
      stdout += data.toString()
    })
    
    process.stderr.on('data', (data) => {
      stderr += data.toString()
    })
    
    process.on('close', async (code) => {
      if (code === 0) {
        console.log('Recompilation successful:', stdout)
        
        // Verify the PDF file exists and was recently modified
        const fileMap = {
          'resume': 'Conner_Jordan_Software_Engineer.tuned.pdf',
          'cover-letter': 'Conner_Jordan_Cover_Letter.tuned.pdf'
        }
        
        const expectedFile = path.join(tempDir, fileMap[fileType])
        
        try {
          const stats = await fs.stat(expectedFile)
          const fileAge = Date.now() - stats.mtime.getTime()
          
          if (fileAge > 30000) { // File older than 30 seconds
            console.warn(`PDF file seems outdated: ${expectedFile}, age: ${fileAge}ms`)
          }
          
          console.log(`PDF verified: ${expectedFile}, size: ${stats.size} bytes, modified: ${stats.mtime}`)
          
          res.json({
            success: true,
            message: 'LaTeX content recompiled successfully',
            output: stdout,
            fileSize: stats.size,
            lastModified: stats.mtime.getTime()
          })
        } catch (verifyError) {
          console.error('PDF file verification failed:', verifyError)
          res.status(500).json({
            success: false,
            message: 'PDF file not found after compilation',
            error: verifyError.message
          })
        }
      } else {
        console.error('Recompilation failed:', stderr)
        res.status(500).json({
          success: false,
          message: 'LaTeX compilation failed',
          error: stderr
        })
      }
    })
    
    process.on('error', (err) => {
      console.error('Process error:', err)
      res.status(500).json({
        success: false,
        message: 'Failed to execute recompilation',
        error: err.message
      })
    })
    
  } catch (error) {
    console.error('Recompile error:', error)
    res.status(500).json({ message: error.message })
  }
})

export default router