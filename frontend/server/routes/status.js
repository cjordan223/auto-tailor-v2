import express from 'express'
import path from 'path'
import fs from 'fs/promises'
import { fileURLToPath } from 'url'

const __filename = fileURLToPath(import.meta.url)
const __dirname = path.dirname(__filename)

const router = express.Router()

// Get job status
router.get('/:jobId', async (req, res) => {
  try {
    const { jobId } = req.params
    const statusFile = path.join(__dirname, '../../temp', jobId, 'status.json')
    
    try {
      const statusData = await fs.readFile(statusFile, 'utf8')
      const status = JSON.parse(statusData)
      
      res.json({
        jobId,
        ...status
      })
    } catch (error) {
      // If status file doesn't exist, job might not exist or be very new
      res.status(404).json({
        jobId,
        status: 'not_found',
        message: 'Job not found or status not available'
      })
    }
  } catch (error) {
    console.error('Status check error:', error)
    res.status(500).json({ message: error.message })
  }
})

export default router