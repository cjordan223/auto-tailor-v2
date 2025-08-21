import express from 'express'
import path from 'path'
import fs from 'fs/promises'
import { fileURLToPath } from 'url'

const __filename = fileURLToPath(import.meta.url)
const __dirname = path.dirname(__filename)

const router = express.Router()

// Download generated files
router.get('/:jobId/:fileType', async (req, res) => {
  try {
    const { jobId, fileType } = req.params
    const tempDir = path.join(__dirname, '../../temp', jobId)
    
    // Map file types to actual filenames
    const fileMap = {
      'resume': 'Conner_Jordan_Software_Engineer.tuned.pdf',
      'cover-letter': 'Conner_Jordan_Cover_Letter.tuned.pdf',
      'edits': 'edits.json'
    }
    
    const filename = fileMap[fileType]
    if (!filename) {
      return res.status(400).json({ message: 'Invalid file type' })
    }
    
    const filePath = path.join(tempDir, filename)
    
    try {
      await fs.access(filePath)
      
      // Set appropriate headers
      const contentType = filename.endsWith('.pdf') ? 'application/pdf' : 'application/json'
      res.setHeader('Content-Type', contentType)
      res.setHeader('Content-Disposition', `attachment; filename="${filename}"`)
      
      // Stream the file
      const fileStream = await fs.readFile(filePath)
      res.send(fileStream)
      
    } catch (error) {
      res.status(404).json({ message: 'File not found' })
    }
    
  } catch (error) {
    console.error('Download error:', error)
    res.status(500).json({ message: error.message })
  }
})

export default router