import express from 'express'
import path from 'path'
import fs from 'fs/promises'
import { fileURLToPath } from 'url'

const __filename = fileURLToPath(import.meta.url)
const __dirname = path.dirname(__filename)

const router = express.Router()

// Get job results including validation status
router.get('/:jobId', async (req, res) => {
  try {
    const { jobId } = req.params
    const tempDir = path.join(__dirname, '../../temp', jobId)
    
    // Check if job directory exists
    try {
      await fs.access(tempDir)
    } catch (error) {
      return res.status(404).json({ message: 'Job not found' })
    }
    
    // Load edits.json to get validation status
    const editsPath = path.join(tempDir, 'edits.json')
    let edits = null
    let validationStatus = null
    
    try {
      const editsContent = await fs.readFile(editsPath, 'utf-8')
      edits = JSON.parse(editsContent)
      
      // Extract validation status from suggested_additions
      if (edits.suggested_additions) {
        const flaggedSkills = edits.suggested_additions
          .filter(suggestion => suggestion.why && suggestion.why.includes('Skills validation:'))
          .map(suggestion => {
            const whyMatch = suggestion.why.match(/Skills validation: (.+?) \(confidence: (.+?)\)/)
            return {
              skill: suggestion.term,
              reason: whyMatch ? whyMatch[1] : suggestion.why,
              confidence: whyMatch ? whyMatch[2] : 'low'
            }
          })
        
        // Calculate confidence level
        let confidence = 'high'
        if (flaggedSkills.length > 2) {
          confidence = 'low'
        } else if (flaggedSkills.length > 0) {
          confidence = 'medium'
        }
        
        validationStatus = {
          confidence,
          flaggedCount: flaggedSkills.length,
          flaggedSkills
        }
      }
    } catch (error) {
      console.warn(`Could not load edits.json for job ${jobId}:`, error.message)
    }
    
    // Load review data if available
    let reviewData = null
    try {
      const reviewPath = path.join(tempDir, 'review.json')
      const reviewContent = await fs.readFile(reviewPath, 'utf-8')
      reviewData = JSON.parse(reviewContent)
    } catch (error) {
      // Review data not available, that's okay
    }
    
    // Load job description if available
    let jobDescription = null
    try {
      const jobDescPath = path.join(tempDir, 'job-description.txt')
      jobDescription = await fs.readFile(jobDescPath, 'utf-8')
    } catch (error) {
      // Job description not available, that's okay
    }
    
    // Check which files are available
    const files = await fs.readdir(tempDir)
    const availableFiles = {
      resume: files.includes('Conner_Jordan_Software_Engineer.tuned.pdf'),
      coverLetter: files.includes('Conner_Jordan_Cover_Letter.tuned.pdf'),
      resumeTex: files.includes('Conner_Jordan_Software_Engineer.tuned.tex'),
      coverLetterTex: files.includes('Conner_Jordan_Cover_Letter.tuned.tex'),
      edits: files.includes('edits.json'),
      review: files.includes('review.json')
    }
    
    // Process skills changes from edits
    let skillsChanges = null
    if (edits && edits.skills) {
      skillsChanges = {}
      
      for (const [category, skillEdit] of Object.entries(edits.skills)) {
        if (skillEdit.replace) {
          // This is a simplified version - in a real implementation,
          // you'd compare with the original base text
          const newSkills = skillEdit.replace.split(',').map(s => s.trim()).filter(s => s)
          skillsChanges[category] = {
            added: newSkills,
            removed: []
          }
        }
      }
    }
    
    // Filter suggested additions to exclude validation-related ones (they're shown in validation status)
    let suggestedAdditions = null
    if (edits && edits.suggested_additions) {
      suggestedAdditions = edits.suggested_additions.filter(
        suggestion => !suggestion.why || !suggestion.why.includes('Skills validation:')
      )
    }
    
    const results = {
      jobId,
      availableFiles,
      skillsChanges,
      suggestedAdditions,
      validationStatus,
      reviewData,
      jobDescription,
      createdAt: new Date().toISOString(),
      completedAt: new Date().toISOString()
    }
    
    res.json(results)
    
  } catch (error) {
    console.error('Results error:', error)
    res.status(500).json({ message: error.message })
  }
})

export default router
