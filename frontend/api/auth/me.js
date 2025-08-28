import jwt from 'jsonwebtoken'
import { ObjectId } from 'mongodb'
import databaseConnection from '../../server/config/database.js'
import dotenv from 'dotenv'

// Load environment variables
dotenv.config()

// Authentication middleware
const authenticate = (req) => {
  try {
    const authHeader = req.headers.authorization
    if (!authHeader || !authHeader.startsWith('Bearer ')) {
      throw new Error('No token provided')
    }

    const token = authHeader.substring(7)
    const jwtSecret = process.env.JWT_SECRET || 'your-super-secret-jwt-key-change-in-production'
    
    const decoded = jwt.verify(token, jwtSecret)
    return decoded
  } catch (error) {
    throw new Error('Invalid token')
  }
}

// Initialize database connection for serverless function
const initializeDatabase = async () => {
  try {
    if (!databaseConnection.isConnected) {
      console.log('🔗 Initializing database connection for auth serverless function...')
      await databaseConnection.connect()
    }
    return true
  } catch (error) {
    console.error('❌ Failed to initialize database:', error)
    return false
  }
}

export default async function handler(req, res) {
  // Set CORS headers
  res.setHeader('Access-Control-Allow-Origin', '*')
  res.setHeader('Access-Control-Allow-Methods', 'GET, OPTIONS')
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type, Authorization')

  if (req.method === 'OPTIONS') {
    res.status(200).end()
    return
  }

  if (req.method !== 'GET') {
    return res.status(405).json({ 
      message: 'Method not allowed',
      code: 'METHOD_NOT_ALLOWED' 
    })
  }

  try {
    // Initialize database connection
    const dbInitialized = await initializeDatabase()
    if (!dbInitialized) {
      return res.status(503).json({
        message: 'Database not available',
        code: 'DB_UNAVAILABLE'
      })
    }

    // Authenticate user
    const user = authenticate(req)
    const userId = user.userId

    const db = databaseConnection.getDb()
    const users = db.collection('users')
    const userData = await users.findOne(
      { _id: new ObjectId(userId) },
      { projection: { password: 0 } }
    )

    if (!userData) {
      return res.status(404).json({ 
        message: 'User not found',
        code: 'USER_NOT_FOUND'
      })
    }

    res.json({
      user: {
        id: userData._id,
        email: userData.email,
        name: userData.name,
        createdAt: userData.createdAt,
        lastLoginAt: userData.lastLoginAt
      }
    })

  } catch (error) {
    console.error('Get user error:', error)
    if (error.message === 'Invalid token' || error.message === 'No token provided') {
      res.status(401).json({
        message: 'Unauthorized',
        code: 'UNAUTHORIZED'
      })
    } else {
      res.status(500).json({ 
        message: 'Internal server error',
        code: 'USER_FETCH_ERROR'
      })
    }
  }
}