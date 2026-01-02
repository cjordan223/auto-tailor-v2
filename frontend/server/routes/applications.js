import express from 'express'
import applicationService from '../services/ApplicationService.js'
import { ObjectId } from 'mongodb'

const router = express.Router()

/**
 * Create a new application from generated content
 * POST /api/applications
 */
router.post('/', async (req, res) => {
  try {
    console.log('📝 Creating application...')
    const userId = req.user.userId
    const applicationData = req.body

    console.log('📋 Application data received:', {
      jobTitle: applicationData.jobTitle,
      companyName: applicationData.companyName,
      hasJobDescription: !!applicationData.jobDescription,
      provider: applicationData.generationMeta?.provider,
      model: applicationData.generationMeta?.model
    })

    if (!applicationData.jobDescription) {
      return res.status(400).json({
        success: false,
        error: 'Job description is required'
      })
    }

    const result = await applicationService.createApplication(userId, applicationData)
    
    console.log('💾 Create application result:', {
      success: result.success,
      applicationId: result.applicationId,
      error: result.error
    })
    
    if (result.success) {
      res.status(201).json(result)
    } else {
      res.status(500).json(result)
    }
  } catch (error) {
    console.error('Error creating application:', error)
    res.status(500).json({
      success: false,
      error: 'Internal server error'
    })
  }
})

/**
 * Get recent generated applications
 * GET /api/applications/recent
 */
router.get('/recent', async (req, res) => {
  try {
    const userId = req.user.userId
    const limit = parseInt(req.query.limit) || 10

    const result = await applicationService.getRecentGeneratedApplications(userId, limit)
    res.json(result)
  } catch (error) {
    console.error('Error fetching recent applications:', error)
    res.status(500).json({
      success: false,
      error: 'Internal server error'
    })
  }
})

/**
 * Get saved applications with filtering and pagination
 * GET /api/applications/saved
 */
router.get('/saved', async (req, res) => {
  try {
    const userId = req.user.userId
    
    const options = {
      status: req.query.status || null,
      includeArchived: req.query.includeArchived === 'true',
      limit: parseInt(req.query.limit) || 50,
      skip: parseInt(req.query.skip) || 0,
      sortBy: req.query.sortBy || 'createdAt',
      sortOrder: req.query.sortOrder === 'asc' ? 1 : -1
    }

    const result = await applicationService.getSavedApplications(userId, options)
    res.json(result)
  } catch (error) {
    console.error('Error fetching saved applications:', error)
    res.status(500).json({
      success: false,
      error: 'Internal server error'
    })
  }
})

/**
 * Save an application (move from generated to saved)
 * POST /api/applications/:id/save
 */
router.post('/:id/save', async (req, res) => {
  try {
    console.log('💾 Saving application...')
    const applicationId = req.params.id
    const userId = req.user.userId

    console.log('📋 Save request:', { applicationId, userId })

    if (!ObjectId.isValid(applicationId)) {
      return res.status(400).json({
        success: false,
        error: 'Invalid application ID'
      })
    }

    const result = await applicationService.saveApplication(applicationId, userId)
    
    console.log('💾 Save application result:', {
      success: result.success,
      applicationId: result.applicationId,
      upserted: result.upserted,
      modified: result.modified,
      error: result.error
    })
    
    if (result.success) {
      res.json(result)
    } else {
      res.status(404).json(result)
    }
  } catch (error) {
    console.error('Error saving application:', error)
    res.status(500).json({
      success: false,
      error: 'Internal server error'
    })
  }
})

/**
 * Update application status
 * PATCH /api/applications/:id/status
 */
router.patch('/:id/status', async (req, res) => {
  try {
    const applicationId = req.params.id
    const userId = req.user.userId
    const { status, ...additionalData } = req.body

    if (!ObjectId.isValid(applicationId)) {
      return res.status(400).json({
        success: false,
        error: 'Invalid application ID'
      })
    }

    if (!status) {
      return res.status(400).json({
        success: false,
        error: 'Status is required'
      })
    }

    const validStatuses = ['draft', 'saved', 'applied', 'interview', 'rejected', 'archived']
    if (!validStatuses.includes(status)) {
      return res.status(400).json({
        success: false,
        error: `Invalid status. Must be one of: ${validStatuses.join(', ')}`
      })
    }

    const result = await applicationService.updateApplicationStatus(
      applicationId, 
      userId, 
      status, 
      additionalData
    )
    
    if (result.success) {
      res.json(result)
    } else {
      res.status(404).json(result)
    }
  } catch (error) {
    console.error('Error updating application status:', error)
    res.status(500).json({
      success: false,
      error: 'Internal server error'
    })
  }
})

/**
 * Add notes to application
 * PATCH /api/applications/:id/notes
 */
router.patch('/:id/notes', async (req, res) => {
  try {
    const applicationId = req.params.id
    const userId = req.user.userId
    const { notes } = req.body

    if (!ObjectId.isValid(applicationId)) {
      return res.status(400).json({
        success: false,
        error: 'Invalid application ID'
      })
    }

    if (typeof notes !== 'string') {
      return res.status(400).json({
        success: false,
        error: 'Notes must be a string'
      })
    }

    const result = await applicationService.addNotes(applicationId, userId, notes)
    
    if (result.success) {
      res.json(result)
    } else {
      res.status(404).json(result)
    }
  } catch (error) {
    console.error('Error adding notes:', error)
    res.status(500).json({
      success: false,
      error: 'Internal server error'
    })
  }
})

/**
 * Archive/unarchive application
 * PATCH /api/applications/:id/archive
 */
router.patch('/:id/archive', async (req, res) => {
  try {
    const applicationId = req.params.id
    const userId = req.user.userId
    const { archived = true } = req.body

    if (!ObjectId.isValid(applicationId)) {
      return res.status(400).json({
        success: false,
        error: 'Invalid application ID'
      })
    }

    const result = await applicationService.archiveApplication(applicationId, userId, archived)
    
    if (result.success) {
      res.json(result)
    } else {
      res.status(404).json(result)
    }
  } catch (error) {
    console.error('Error archiving application:', error)
    res.status(500).json({
      success: false,
      error: 'Internal server error'
    })
  }
})

/**
 * Search applications by text
 * GET /api/applications/search
 */
router.get('/search', async (req, res) => {
  try {
    const userId = req.user.userId
    const searchTerm = req.query.q

    if (!searchTerm) {
      return res.status(400).json({
        success: false,
        error: 'Search term (q) is required'
      })
    }

    const options = {
      limit: parseInt(req.query.limit) || 20,
      skip: parseInt(req.query.skip) || 0,
      includeArchived: req.query.includeArchived === 'true'
    }

    const result = await applicationService.searchApplications(userId, searchTerm, options)
    res.json(result)
  } catch (error) {
    console.error('Error searching applications:', error)
    res.status(500).json({
      success: false,
      error: 'Internal server error'
    })
  }
})

/**
 * Get application statistics
 * GET /api/applications/stats
 */
router.get('/stats', async (req, res) => {
  try {
    const userId = req.user.userId

    const result = await applicationService.getApplicationStats(userId)
    res.json(result)
  } catch (error) {
    console.error('Error fetching application stats:', error)
    res.status(500).json({
      success: false,
      error: 'Internal server error'
    })
  }
})

/**
 * Get single application by ID
 * GET /api/applications/:id
 */
router.get('/:id', async (req, res) => {
  try {
    const applicationId = req.params.id
    const userId = req.user.userId

    if (!ObjectId.isValid(applicationId)) {
      return res.status(400).json({
        success: false,
        error: 'Invalid application ID'
      })
    }

    const result = await applicationService.getApplication(applicationId, userId)
    
    if (result.success) {
      res.json(result)
    } else {
      res.status(404).json({
        success: false,
        error: 'Application not found'
      })
    }
  } catch (error) {
    console.error('Error fetching application:', error)
    res.status(500).json({
      success: false,
      error: 'Internal server error'
    })
  }
})

/**
 * Download application files
 * GET /api/applications/:id/download
 */
router.get('/:id/download', async (req, res) => {
  try {
    const applicationId = req.params.id
    const userId = req.user.userId

    if (!ObjectId.isValid(applicationId)) {
      return res.status(400).json({
        success: false,
        error: 'Invalid application ID'
      })
    }

    const result = await applicationService.getApplication(applicationId, userId)
    
    if (!result.success) {
      return res.status(404).json({
        success: false,
        error: 'Application not found'
      })
    }

    const application = result.application
    
    // Check if files exist
    const resumeUrl = application.files?.resume?.url
    const coverLetterUrl = application.files?.coverLetter?.url
    
    if (!resumeUrl && !coverLetterUrl) {
      return res.status(404).json({
        success: false,
        error: 'No files found for this application'
      })
    }

    // For now, redirect to the existing download endpoint
    // In the future, this could be enhanced to create a proper zip with application metadata
    const jobId = applicationId // Use application ID as job ID for now
    
    res.redirect(`/api/download/${jobId}/zip/all`)
    
  } catch (error) {
    console.error('Error downloading application:', error)
    res.status(500).json({
      success: false,
      error: 'Internal server error'
    })
  }
})

/**
 * Add notes to application
 * PATCH /api/applications/:id/notes
 */
router.patch('/:id/notes', async (req, res) => {
  try {
    const applicationId = req.params.id
    const userId = req.user.userId
    const { notes } = req.body

    if (!ObjectId.isValid(applicationId)) {
      return res.status(400).json({
        success: false,
        error: 'Invalid application ID'
      })
    }

    if (!notes) {
      return res.status(400).json({
        success: false,
        error: 'Notes are required'
      })
    }

    const result = await applicationService.addNotes(applicationId, userId, notes)

    if (result.success) {
      res.json(result)
    } else {
      res.status(404).json({
        success: false,
        error: 'Application not found'
      })
    }
  } catch (error) {
    console.error('Error adding notes:', error)
    res.status(500).json({
      success: false,
      error: 'Internal server error'
    })
  }
})

/**
 * Delete application permanently
 * DELETE /api/applications/:id
 */
router.delete('/:id', async (req, res) => {
  try {
    const applicationId = req.params.id
    const userId = req.user.userId

    if (!ObjectId.isValid(applicationId)) {
      return res.status(400).json({
        success: false,
        error: 'Invalid application ID'
      })
    }

    const result = await applicationService.deleteApplication(applicationId, userId)

    if (result.success) {
      res.json(result)
    } else {
      res.status(404).json({
        success: false,
        error: 'Application not found'
      })
    }
  } catch (error) {
    console.error('Error deleting application:', error)
    res.status(500).json({
      success: false,
      error: 'Internal server error'
    })
  }
})


export default router