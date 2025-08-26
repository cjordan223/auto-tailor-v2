import express from 'express'
import path from 'path'
import fs from 'fs/promises'
import { fileURLToPath } from 'url'

const __filename = fileURLToPath(import.meta.url)
const __dirname = path.dirname(__filename)

const router = express.Router()

// View generated PDFs inline (for embedding)
router.get('/:jobId/:fileType', async (req, res) => {
  try {
    const { jobId, fileType } = req.params
    const tempDir = path.join(__dirname, '../../temp', jobId)
    
    // Only allow PDF file types for viewing
    const fileMap = {
      'resume': 'Conner_Jordan_Software_Engineer.tuned.pdf',
      'cover-letter': 'Conner_Jordan_Cover_Letter.tuned.pdf'
    }
    
    const filename = fileMap[fileType]
    if (!filename) {
      return res.status(400).json({ message: 'Invalid file type for viewing' })
    }
    
    const filePath = path.join(tempDir, filename)
    
    try {
      const stats = await fs.stat(filePath)
      const lastModified = stats.mtime.toUTCString()
      const etag = `"${stats.size}-${stats.mtime.getTime()}"`
      
      // Check if client has current version
      const clientETag = req.headers['if-none-match']
      if (clientETag === etag) {
        return res.status(304).send() // Not Modified
      }
      
      // Set headers for inline PDF viewing with proper cache control
      res.setHeader('Content-Type', 'application/pdf')
      res.setHeader('Content-Disposition', `inline; filename="${filename}"`)
      res.setHeader('Cache-Control', 'no-cache, no-store, must-revalidate')
      res.setHeader('Pragma', 'no-cache')
      res.setHeader('Expires', '0')
      res.setHeader('ETag', etag)
      res.setHeader('Last-Modified', lastModified)
      res.setHeader('X-Content-Type-Options', 'nosniff')

      // Allow embedding the PDF in iframes from trusted origins only
      // Prefer Content-Security-Policy frame-ancestors over deprecated X-Frame-Options
      const allowedAncestors = [
        'http://localhost:3000',
        'https://auto-tailor-v2.vercel.app',
        process.env.FRONTEND_URL
      ].filter(Boolean)

      if (allowedAncestors.length > 0) {
        res.setHeader('Content-Security-Policy', `frame-ancestors ${allowedAncestors.join(' ')};`)
      }
      
      // Stream the file
      const fileStream = await fs.readFile(filePath)
      res.send(fileStream)
      
    } catch (error) {
      res.status(404).json({ message: 'File not found' })
    }
    
  } catch (error) {
    console.error('View error:', error)
    res.status(500).json({ message: error.message })
  }
})

// View generated LaTeX source files (for text display)
router.get('/:jobId/:fileType/tex', async (req, res) => {
  try {
    const { jobId, fileType } = req.params
    const tempDir = path.join(__dirname, '../../temp', jobId)
    
    // Map file types to LaTeX file names
    const fileMap = {
      'resume': 'Conner_Jordan_Software_Engineer.tuned.tex',
      'cover-letter': 'Conner_Jordan_Cover_Letter.tuned.tex'
    }
    
    const filename = fileMap[fileType]
    if (!filename) {
      return res.status(400).json({ message: 'Invalid file type for LaTeX viewing' })
    }
    
    const filePath = path.join(tempDir, filename)
    
    try {
      await fs.access(filePath)
      
      // Set headers for text file viewing
      res.setHeader('Content-Type', 'text/plain; charset=utf-8')
      res.setHeader('Content-Disposition', `inline; filename="${filename}"`)
      res.setHeader('Cache-Control', 'no-cache')
      res.setHeader('X-Content-Type-Options', 'nosniff')
      
      // Read and send the LaTeX source
      const fileContent = await fs.readFile(filePath, 'utf-8')
      res.send(fileContent)
      
    } catch (error) {
      res.status(404).json({ message: 'LaTeX file not found' })
    }
    
  } catch (error) {
    console.error('LaTeX view error:', error)
    res.status(500).json({ message: error.message })
  }
})

// View original tailored LaTeX source files (for reset functionality)
router.get('/:jobId/:fileType/original', async (req, res) => {
  try {
    const { jobId, fileType } = req.params
    const tempDir = path.join(__dirname, '../../temp', jobId)
    
    // Map file types to original LaTeX file names
    const fileMap = {
      'resume': 'Conner_Jordan_Software_Engineer.tuned.tex.original',
      'cover-letter': 'Conner_Jordan_Cover_Letter.tuned.tex.original'
    }
    
    const filename = fileMap[fileType]
    if (!filename) {
      return res.status(400).json({ message: 'Invalid file type for original LaTeX viewing' })
    }
    
    const filePath = path.join(tempDir, filename)
    
    try {
      await fs.access(filePath)
      
      // Set headers for text file viewing
      res.setHeader('Content-Type', 'text/plain; charset=utf-8')
      res.setHeader('Content-Disposition', `inline; filename="${filename}"`)
      res.setHeader('Cache-Control', 'no-cache')
      res.setHeader('X-Content-Type-Options', 'nosniff')
      
      // Read and send the original LaTeX source
      const fileContent = await fs.readFile(filePath, 'utf-8')
      res.send(fileContent)
      
    } catch (error) {
      // Fallback: try to serve current version if no original backup exists
      const currentFileMap = {
        'resume': 'Conner_Jordan_Software_Engineer.tuned.tex',
        'cover-letter': 'Conner_Jordan_Cover_Letter.tuned.tex'
      }
      
      const currentFilePath = path.join(tempDir, currentFileMap[fileType])
      try {
        await fs.access(currentFilePath)
        const fileContent = await fs.readFile(currentFilePath, 'utf-8')
        res.send(fileContent)
      } catch (fallbackError) {
        res.status(404).json({ message: 'Original LaTeX file not found' })
      }
    }
    
  } catch (error) {
    console.error('Original LaTeX view error:', error)
    res.status(500).json({ message: error.message })
  }
})

export default router