import { ObjectId } from 'mongodb'
import databaseConnection from '../config/database.js'

class ApplicationService {
  constructor() {
    this.db = null
  }

  async initialize() {
    console.log('🔗 Initializing ApplicationService...')
    this.db = databaseConnection.getDb()
    console.log('✅ ApplicationService initialized, database:', this.db ? 'connected' : 'not connected')
  }

  /**
   * Create a new application from generated content
   */
  async createApplication(userId, applicationData) {
    try {
      // Check if database is connected
      if (!this.db) {
        console.error('❌ Database not initialized in ApplicationService')
        return {
          success: false,
          error: 'Database not connected'
        }
      }
      const application = {
        _id: new ObjectId(),
        userId: userId,
        jobId: applicationData.jobId || null, // UUID from workflow for file retrieval
        createdAt: new Date(),
        updatedAt: new Date(),
        status: 'draft',
        source: 'generated',

        jobDetails: {
          jobTitle: applicationData.jobTitle || 'Unknown Position',
          companyName: applicationData.companyName || 'Unknown Company',
          jobUrl: applicationData.jobUrl || null,
          jobDescription: applicationData.jobDescription,
          location: applicationData.location || null,
          extractedOn: new Date()
        },

        generatedContent: {
          resume: {
            fileName: applicationData.resume?.fileName || null,
            summary: applicationData.resume?.summary || null,
            experience: applicationData.resume?.experience || [],
            education: applicationData.resume?.education || [],
            skills: applicationData.resume?.skills || {}
          },
          coverLetter: {
            fileName: applicationData.coverLetter?.fileName || null,
            paragraphs: applicationData.coverLetter?.paragraphs || []
          }
        },

        generationMeta: {
          provider: applicationData.generationMeta?.provider || 'unknown',
          model: applicationData.generationMeta?.model || 'unknown',
          processingTime: applicationData.generationMeta?.processingTime || 0,
          tokensUsed: applicationData.generationMeta?.tokensUsed || 0,
          validationPassed: applicationData.generationMeta?.validationPassed || false
        },

        baseResume: {
          resumeId: applicationData.baseResume?.resumeId || null,
          version: applicationData.baseResume?.version || 'v1.0',
          extractedAt: new Date()
        },

        files: {
          resume: {
            url: applicationData.files?.resume?.url || null,
            storageKey: applicationData.files?.resume?.storageKey || null,
            generatedAt: new Date()
          },
          coverLetter: {
            url: applicationData.files?.coverLetter?.url || null,
            storageKey: applicationData.files?.coverLetter?.storageKey || null,
            generatedAt: new Date()
          }
        },

        trackingInfo: {
          appliedAt: null,
          notes: '',
          nextSteps: []
        },

        searchMeta: {
          keywords: applicationData.searchMeta?.keywords || [],
          jobType: applicationData.searchMeta?.jobType || null,
          salaryRange: applicationData.searchMeta?.salaryRange || null,
          requiredYears: applicationData.searchMeta?.requiredYears || null
        },

        isArchived: false
      }

      console.log(`💾 Creating application for userId: ${userId} (type: ${typeof userId})`)

      // Insert into both collections:
      // 1. generated_applications (temporary/capped collection for recent items)
      const result = await this.db.collection('generated_applications').insertOne(application)

      // 2. saved_applications (permanent storage for dashboard)
      // Mark as 'draft' status since it's newly generated
      const savedApp = { ...application, status: 'draft' }
      await this.db.collection('saved_applications').insertOne(savedApp)

      console.log(`✅ Application saved to both collections: ${result.insertedId}`)

      return {
        success: true,
        applicationId: result.insertedId,
        application: application
      }
    } catch (error) {
      console.error('Error creating application:', error)
      return {
        success: false,
        error: error.message
      }
    }
  }

  /**
   * Save application permanently (move from generated to saved)
   */
  async saveApplication(applicationId, userId) {
    try {
      // Check if database is connected
      if (!this.db) {
        console.error('❌ Database not initialized in ApplicationService')
        return {
          success: false,
          error: 'Database not connected'
        }
      }
      // Find in generated applications
      const application = await this.db.collection('generated_applications').findOne({
        _id: new ObjectId(applicationId),
        userId: userId
      })

      if (!application) {
        return {
          success: false,
          error: 'Application not found in generated applications'
        }
      }

      // Update status and timestamp
      application.status = 'saved'
      application.updatedAt = new Date()

      // Upsert into saved_applications
      const result = await this.db.collection('saved_applications').replaceOne(
        { _id: application._id },
        application,
        { upsert: true }
      )

      return {
        success: true,
        applicationId: application._id,
        upserted: result.upsertedCount > 0,
        modified: result.modifiedCount > 0
      }
    } catch (error) {
      console.error('Error saving application:', error)
      return {
        success: false,
        error: error.message
      }
    }
  }

  /**
   * Get recent generated applications for a user
   */
  async getRecentGeneratedApplications(userId, limit = 10) {
    try {
      const applications = await this.db.collection('generated_applications')
        .find({ userId: userId })
        .sort({ createdAt: -1 })
        .limit(limit)
        .toArray()

      return {
        success: true,
        applications: applications
      }
    } catch (error) {
      console.error('Error fetching recent applications:', error)
      return {
        success: false,
        error: error.message
      }
    }
  }

  /**
   * Get saved applications for a user
   */
  async getSavedApplications(userId, options = {}) {
    try {
      const {
        status = null,
        includeArchived = false,
        limit = 50,
        skip = 0,
        sortBy = 'createdAt',
        sortOrder = -1
      } = options

      console.log(`🔍 Fetching saved applications for userId: ${userId} (type: ${typeof userId})`)

      const query = { userId: userId }
      
      if (!includeArchived) {
        query.isArchived = false
      }
      
      if (status) {
        query.status = status
      }

      // Handle nested field sorting
      let sortField = sortBy
      if (sortBy === 'jobTitle') {
        sortField = 'jobDetails.jobTitle'
      } else if (sortBy === 'companyName') {
        sortField = 'jobDetails.companyName'
      }

      const applications = await this.db.collection('saved_applications')
        .find(query)
        .sort({ [sortField]: sortOrder })
        .skip(skip)
        .limit(limit)
        .toArray()

      const totalCount = await this.db.collection('saved_applications').countDocuments(query)

      console.log(`📊 Query results: Found ${applications.length} applications (total: ${totalCount})`)
      console.log(`📊 Query used: ${JSON.stringify(query)}`)

      return {
        success: true,
        applications: applications,
        totalCount: totalCount,
        hasMore: (skip + applications.length) < totalCount
      }
    } catch (error) {
      console.error('Error fetching saved applications:', error)
      return {
        success: false,
        error: error.message
      }
    }
  }

  /**
   * Update application status (e.g., draft -> applied)
   */
  async updateApplicationStatus(applicationId, userId, newStatus, additionalData = {}) {
    try {
      const updateData = {
        status: newStatus,
        updatedAt: new Date(),
        ...additionalData
      }

      // If marking as applied, set appliedAt timestamp
      if (newStatus === 'applied') {
        updateData['trackingInfo.appliedAt'] = new Date()
      }

      const result = await this.db.collection('saved_applications').updateOne(
        { _id: new ObjectId(applicationId), userId: userId },
        { $set: updateData }
      )

      return {
        success: result.matchedCount > 0,
        modified: result.modifiedCount > 0,
        applicationId: applicationId
      }
    } catch (error) {
      console.error('Error updating application status:', error)
      return {
        success: false,
        error: error.message
      }
    }
  }

  /**
   * Add notes to application
   */
  async addNotes(applicationId, userId, notes) {
    try {
      const result = await this.db.collection('saved_applications').updateOne(
        { _id: new ObjectId(applicationId), userId: userId },
        { 
          $set: { 
            'trackingInfo.notes': notes,
            updatedAt: new Date()
          }
        }
      )

      return {
        success: result.matchedCount > 0,
        modified: result.modifiedCount > 0
      }
    } catch (error) {
      console.error('Error adding notes:', error)
      return {
        success: false,
        error: error.message
      }
    }
  }

  /**
   * Archive/unarchive application (soft delete)
   */
  async archiveApplication(applicationId, userId, archived = true) {
    try {
      const result = await this.db.collection('saved_applications').updateOne(
        { _id: new ObjectId(applicationId), userId: userId },
        { 
          $set: { 
            isArchived: archived,
            updatedAt: new Date()
          }
        }
      )

      return {
        success: result.matchedCount > 0,
        modified: result.modifiedCount > 0,
        archived: archived
      }
    } catch (error) {
      console.error('Error archiving application:', error)
      return {
        success: false,
        error: error.message
      }
    }
  }

  /**
   * Search applications by text
   */
  async searchApplications(userId, searchTerm, options = {}) {
    try {
      const {
        limit = 20,
        skip = 0,
        includeArchived = false
      } = options

      const query = {
        userId: userId,
        $text: { $search: searchTerm }
      }

      if (!includeArchived) {
        query.isArchived = false
      }

      const applications = await this.db.collection('saved_applications')
        .find(query)
        .sort({ score: { $meta: 'textScore' } })
        .skip(skip)
        .limit(limit)
        .toArray()

      return {
        success: true,
        applications: applications,
        searchTerm: searchTerm
      }
    } catch (error) {
      console.error('Error searching applications:', error)
      return {
        success: false,
        error: error.message
      }
    }
  }

  /**
   * Get application statistics for a user
   */
  async getApplicationStats(userId) {
    try {
      const pipeline = [
        { $match: { userId: userId, isArchived: false } },
        {
          $group: {
            _id: '$status',
            count: { $sum: 1 }
          }
        }
      ]

      const stats = await this.db.collection('saved_applications').aggregate(pipeline).toArray()
      
      const recentCount = await this.db.collection('generated_applications').countDocuments({ userId: userId })

      const statsObj = {
        draft: 0,
        saved: 0,
        applied: 0,
        interview: 0,
        rejected: 0,
        recent_generated: recentCount
      }

      stats.forEach(stat => {
        if (statsObj.hasOwnProperty(stat._id)) {
          statsObj[stat._id] = stat.count
        }
      })

      return {
        success: true,
        stats: statsObj
      }
    } catch (error) {
      console.error('Error getting application stats:', error)
      return {
        success: false,
        error: error.message
      }
    }
  }

  /**
   * Get single application by ID
   */
  async getApplication(applicationId, userId) {
    try {
      // Try saved applications first
      let application = await this.db.collection('saved_applications').findOne({
        _id: new ObjectId(applicationId),
        userId: userId
      })

      // If not found, try generated applications
      if (!application) {
        application = await this.db.collection('generated_applications').findOne({
          _id: new ObjectId(applicationId),
          userId: userId
        })
      }

      return {
        success: !!application,
        application: application
      }
    } catch (error) {
      console.error('Error getting application:', error)
      return {
        success: false,
        error: error.message
      }
    }
  }

  /**
   * Delete application permanently (hard delete)
   */
  async deleteApplication(applicationId, userId) {
    try {
      // Delete from saved_applications
      const savedResult = await this.db.collection('saved_applications').deleteOne({
        _id: new ObjectId(applicationId),
        userId: userId
      })

      // Also delete from generated_applications if exists
      const generatedResult = await this.db.collection('generated_applications').deleteOne({
        _id: new ObjectId(applicationId),
        userId: userId
      })

      const deleted = savedResult.deletedCount > 0 || generatedResult.deletedCount > 0

      return {
        success: deleted,
        deletedCount: savedResult.deletedCount + generatedResult.deletedCount
      }
    } catch (error) {
      console.error('Error deleting application:', error)
      return {
        success: false,
        error: error.message
      }
    }
  }
}

const applicationService = new ApplicationService()

export default applicationService