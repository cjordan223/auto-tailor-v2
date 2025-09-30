import express from 'express'
import path from 'path'
import fs from 'fs/promises'
import { fileURLToPath } from 'url'

const __filename = fileURLToPath(import.meta.url)
const __dirname = path.dirname(__filename)

const router = express.Router()

// Check if PDF file has been updated after recompilation
router.get('/:jobId/:fileType', async (req, res) => {
  try {
    const { jobId, fileType } = req.params
    const { since } = req.query // Timestamp to check against

    if (!['resume', 'cover-letter'].includes(fileType)) {
      return res.status(400).json({
        success: false,
        error: 'Invalid file type'
      })
    }

    const tempDir = path.join(__dirname, '../../temp', jobId)

    // Check if job directory exists
    try {
      await fs.access(tempDir)
    } catch (error) {
      return res.status(404).json({
        success: false,
        error: 'Job directory not found'
      })
    }

    const fileMap = {
      'resume': 'Conner_Jordan_Software_Engineer.tuned.pdf',
      'cover-letter': 'Conner_Jordan_Cover_Letter.tuned.pdf'
    }

    const pdfPath = path.join(tempDir, fileMap[fileType])

    try {
      const stats = await fs.stat(pdfPath)
      const fileModifiedTime = stats.mtime.getTime()
      const currentTime = Date.now()
      const fileAge = currentTime - fileModifiedTime
      const sinceTime = since ? parseInt(since) : 0

      // Consider file updated if:
      // 1. File was modified after the 'since' timestamp
      // 2. File is less than 30 seconds old (fresh compilation)
      const isUpdated = fileModifiedTime > sinceTime && fileAge < 30000

      console.log(`PDF check for ${jobId}/${fileType}:`, {
        fileModifiedTime: new Date(fileModifiedTime).toISOString(),
        sinceTime: since ? new Date(sinceTime).toISOString() : 'not provided',
        fileAge: `${fileAge}ms`,
        isUpdated,
        fileSize: stats.size
      })

      res.json({
        success: true,
        exists: true,
        updated: isUpdated,
        size: stats.size,
        modified: fileModifiedTime,
        age: fileAge,
        since: sinceTime
      })

    } catch (statError) {
      console.error(`PDF file not found: ${pdfPath}`, statError.message)
      res.json({
        success: true,
        exists: false,
        updated: false,
        error: `PDF file not found: ${statError.message}`
      })
    }

  } catch (error) {
    console.error('PDF check error:', error)
    res.status(500).json({
      success: false,
      error: error.message
    })
  }
})

export default router