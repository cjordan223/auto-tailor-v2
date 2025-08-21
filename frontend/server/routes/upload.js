import express from 'express'
import multer from 'multer'
import path from 'path'
import fs from 'fs/promises'

const router = express.Router()

const storage = multer.diskStorage({
  destination: async (req, file, cb) => {
    const tempDir = path.join(process.cwd(), 'frontend/temp')
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

const upload = multer({ storage, limits: { fileSize: 10 * 1024 * 1024 } })

router.post('/', upload.single('file'), async (req, res) => {
  try {
    if (!req.file) {
      return res.status(400).json({ message: 'No file uploaded' })
    }

    res.json({
      message: 'File uploaded successfully',
      file: {
        filename: req.file.filename,
        originalname: req.file.originalname,
        size: req.file.size,
        path: req.file.path
      }
    })
  } catch (error) {
    res.status(500).json({ message: error.message })
  }
})

export default router