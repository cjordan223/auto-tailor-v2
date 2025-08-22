import express from 'express'
import path from 'path'
import fs from 'fs/promises'
import { exec } from 'child_process'
import { promisify } from 'util'
import { fileURLToPath } from 'url'

const __filename = fileURLToPath(import.meta.url)
const __dirname = path.dirname(__filename)
const execAsync = promisify(exec)

const router = express.Router()

// Generate PDF preview as image (fallback option)
router.get('/:jobId/:fileType', async (req, res) => {
  try {
    const { jobId, fileType } = req.params
    const tempDir = path.join(__dirname, '../../temp', jobId)
    
    // Only allow PDF file types for preview
    const fileMap = {
      'resume': 'Conner_Jordan_Software_Engineer.tuned.pdf',
      'cover-letter': 'Conner_Jordan_Cover_Letter.tuned.pdf'
    }
    
    const filename = fileMap[fileType]
    if (!filename) {
      return res.status(400).json({ message: 'Invalid file type for preview' })
    }
    
    const pdfPath = path.join(tempDir, filename)
    const previewDir = path.join(tempDir, 'previews')
    const imagePath = path.join(previewDir, `${fileType}-preview.png`)
    
    try {
      await fs.access(pdfPath)
      
      // Check if preview already exists
      try {
        await fs.access(imagePath)
        // Preview exists, serve it
        const imageData = await fs.readFile(imagePath)
        res.setHeader('Content-Type', 'image/png')
        res.setHeader('Cache-Control', 'public, max-age=3600') // Cache for 1 hour
        res.send(imageData)
        return
      } catch (err) {
        // Preview doesn't exist, generate it
      }
      
      // Create preview directory if it doesn't exist
      await fs.mkdir(previewDir, { recursive: true })
      
      // Convert first page of PDF to PNG using ImageMagick (if available)
      // This is optional and requires ImageMagick to be installed
      try {
        // Convert PDF first page to PNG at 150 DPI
        await execAsync(`convert -density 150 "${pdfPath}[0]" -quality 90 "${imagePath}"`)
        
        const imageData = await fs.readFile(imagePath)
        res.setHeader('Content-Type', 'image/png')
        res.setHeader('Cache-Control', 'public, max-age=3600')
        res.send(imageData)
        
      } catch (convertError) {
        // ImageMagick not available or conversion failed
        console.warn('PDF to image conversion failed:', convertError.message)
        res.status(501).json({ 
          message: 'PDF preview generation not available',
          fallback: `/api/view/${jobId}/${fileType}`
        })
      }
      
    } catch (error) {
      res.status(404).json({ message: 'PDF file not found' })
    }
    
  } catch (error) {
    console.error('Preview generation error:', error)
    res.status(500).json({ message: error.message })
  }
})

export default router