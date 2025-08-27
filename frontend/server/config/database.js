import { MongoClient } from 'mongodb'
import dotenv from 'dotenv'

dotenv.config()

class DatabaseConnection {
  constructor() {
    this.client = null
    this.db = null
    this.isConnected = false
  }

  async connect() {
    try {
      const uri = process.env.MONGODB_ATLAS_URI
      if (!uri) {
        throw new Error('MONGODB_ATLAS_URI environment variable is not set')
      }

      console.log('🔗 Attempting MongoDB Atlas connection...')
      console.log('📍 Node.js version:', process.version)
      console.log('📦 MongoDB driver version: 6.19.0 (latest)')

      // MongoDB client options - Production-ready secure configuration
      const clientOptions = {
        maxPoolSize: 10,
        serverSelectionTimeoutMS: 15000,
        socketTimeoutMS: 45000,
        connectTimeoutMS: 15000,
        retryWrites: true,
        retryReads: true,
        
        // Secure TLS configuration for production
        tls: true,
        tlsAllowInvalidCertificates: false,
        tlsAllowInvalidHostnames: false,
        
        // Additional security hardening
        authSource: 'admin',
        compressors: ['zlib'],  // Enable compression for better performance
        zlibCompressionLevel: 6,
        
        // Connection monitoring and security
        monitorCommands: false,  // Disable command monitoring in production
        heartbeatFrequencyMS: 30000,
        
        // Security timeouts
        maxIdleTimeMS: 300000,   // 5 minutes max idle time
        waitQueueTimeoutMS: 10000,
      }
      
      console.log('⚙️  Client options:', JSON.stringify(clientOptions, null, 2))
      
      this.client = new MongoClient(uri, clientOptions)

      console.log('🔌 Connecting to MongoDB...')
      await this.client.connect()
      
      console.log('🏗️  Setting up database...')
      this.db = this.client.db(process.env.MONGODB_DATABASE_NAME || 'resume_tailor')
      this.isConnected = true

      // Test the connection with a ping
      console.log('🏓 Testing connection...')
      await this.db.admin().ping()

      // Set up collections with proper configuration
      await this.setupCollections()

      console.log('✅ Successfully connected to MongoDB Atlas')
      return this.db
    } catch (error) {
      console.error('❌ MongoDB connection failed:', error.message)
      
      // Production-safe error logging (avoid exposing sensitive connection details)
      const safeErrorDetails = {
        name: error.name,
        code: error.code,
        codeName: error.codeName,
        timestamp: new Date().toISOString()
      }
      console.error('🔍 Error details:', safeErrorDetails)
      
      // In production, log to monitoring service instead of console
      if (process.env.NODE_ENV === 'production') {
        // TODO: Integrate with monitoring service (e.g., CloudWatch, DataDog)
        console.error('🚨 Production MongoDB connection failure - alerting required')
      }
      
      // Graceful degradation - allow server to continue without database
      this.isConnected = false
      console.log('⚠️  Server will continue in degraded mode without database')
      return null
    }
  }

  async setupCollections() {
    try {
      // Create capped collection for temporary generated applications
      const generatedExists = await this.db.listCollections({ name: 'generated_applications' }).hasNext()
      if (!generatedExists) {
        await this.db.createCollection('generated_applications', {
          capped: true,
          size: 52428800, // 50MB
          max: 100 // Maximum 100 documents
        })
        console.log('📦 Created capped collection: generated_applications')
      }

      // Create indexes for performance
      await this.createIndexes()
      
      console.log('🔧 Database collections and indexes configured')
    } catch (error) {
      console.error('❌ Failed to setup collections:', error)
      throw error
    }
  }

  async createIndexes() {
    // Indexes for generated_applications (capped collection)
    await this.db.collection('generated_applications').createIndex(
      { "userId": 1, "createdAt": -1 }, 
      { background: true }
    )

    // Indexes for saved_applications (standard collection)
    await this.db.collection('saved_applications').createIndex(
      { "userId": 1, "status": 1, "isArchived": 1 }, 
      { background: true }
    )
    await this.db.collection('saved_applications').createIndex(
      { "userId": 1, "jobDetails.companyName": 1 }, 
      { background: true }
    )
    await this.db.collection('saved_applications').createIndex(
      { "userId": 1, "createdAt": -1 }, 
      { background: true }
    )
    await this.db.collection('saved_applications').createIndex(
      { "_id": 1, "userId": 1 }, 
      { background: true }
    )

    // Text search index for job descriptions
    await this.db.collection('saved_applications').createIndex(
      { 
        "jobDetails.jobDescription": "text",
        "jobDetails.jobTitle": "text",
        "jobDetails.companyName": "text"
      },
      { 
        name: "job_search_text",
        background: true,
        weights: {
          "jobDetails.jobTitle": 3,
          "jobDetails.companyName": 2,
          "jobDetails.jobDescription": 1
        }
      }
    )
  }

  getDb() {
    if (!this.isConnected || !this.db) {
      throw new Error('Database not connected. Call connect() first.')
    }
    return this.db
  }

  async close() {
    if (this.client) {
      await this.client.close()
      this.isConnected = false
      console.log('🔌 MongoDB connection closed')
    }
  }

  async healthCheck() {
    try {
      await this.db.admin().ping()
      return { status: 'healthy', connected: true }
    } catch (error) {
      return { status: 'unhealthy', connected: false, error: error.message }
    }
  }
}

// Singleton instance
const databaseConnection = new DatabaseConnection()

export default databaseConnection