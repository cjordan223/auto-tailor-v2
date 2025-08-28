import bcrypt from 'bcryptjs'
import jwt from 'jsonwebtoken'
import databaseConnection from '../../server/config/database.js'
import dotenv from 'dotenv'

// Load environment variables
dotenv.config()

const validateEmail = (email) => {
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
  return emailRegex.test(email)
}

const generateToken = (user) => {
  const payload = {
    userId: user._id || user.userId,
    email: user.email
  }
  
  const jwtSecret = process.env.JWT_SECRET || 'your-super-secret-jwt-key-change-in-production'
  const jwtExpiresIn = process.env.JWT_EXPIRES_IN || '24h'
  
  return jwt.sign(payload, jwtSecret, { expiresIn: jwtExpiresIn })
}

// Initialize database connection for serverless function
const initializeDatabase = async () => {
  try {
    console.log('🔧 Checking database connection status...')
    console.log('📍 Current connection status:', {
      isConnected: databaseConnection.isConnected,
      hasDb: !!databaseConnection.db
    })

    if (!databaseConnection.isConnected) {
      console.log('🔗 Initializing database connection for auth serverless function...')
      await databaseConnection.connect()
      console.log('✅ Database connection established')
    }
    
    // Double check we have a database instance
    if (!databaseConnection.db) {
      console.error('❌ Database instance is null after connection attempt')
      return false
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
  res.setHeader('Access-Control-Allow-Methods', 'POST, OPTIONS')
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type, Authorization')

  if (req.method === 'OPTIONS') {
    res.status(200).end()
    return
  }

  if (req.method !== 'POST') {
    return res.status(405).json({ 
      message: 'Method not allowed',
      code: 'METHOD_NOT_ALLOWED' 
    })
  }

  // Debug environment variables
  console.log('🔍 Environment check:', {
    hasJwtSecret: !!process.env.JWT_SECRET,
    hasMongoUri: !!process.env.MONGODB_ATLAS_URI,
    nodeEnv: process.env.NODE_ENV
  })

  try {
    // Initialize database connection
    const dbInitialized = await initializeDatabase()
    if (!dbInitialized) {
      return res.status(503).json({
        message: 'Database not available',
        code: 'DB_UNAVAILABLE'
      })
    }

    const { email, password } = req.body

    if (!email || !password) {
      return res.status(400).json({ 
        message: 'Email and password are required',
        code: 'MISSING_CREDENTIALS'
      })
    }

    if (!validateEmail(email)) {
      return res.status(400).json({ 
        message: 'Invalid email format',
        code: 'INVALID_EMAIL'
      })
    }

    const db = databaseConnection.getDb()
    const users = db.collection('users')
    const user = await users.findOne({ email: email.toLowerCase() })

    console.log('🔍 Login attempt for:', email.toLowerCase())
    console.log('👤 User found:', !!user)

    if (!user) {
      console.log('❌ No user found with email:', email.toLowerCase())
      return res.status(401).json({ 
        message: 'Invalid credentials',
        code: 'INVALID_CREDENTIALS'
      })
    }

    if (!user.isActive) {
      return res.status(401).json({ 
        message: 'Account is deactivated',
        code: 'ACCOUNT_DEACTIVATED'
      })
    }

    console.log('🔐 Comparing password for user:', user.email)
    console.log('🔑 Stored hash exists:', !!user.password)
    const isValidPassword = await bcrypt.compare(password, user.password)
    console.log('✅ Password valid:', isValidPassword)
    
    if (!isValidPassword) {
      console.log('❌ Password comparison failed for user:', user.email)
      return res.status(401).json({ 
        message: 'Invalid credentials',
        code: 'INVALID_CREDENTIALS'
      })
    }

    // Update last login
    await users.updateOne(
      { _id: user._id },
      { 
        $set: { 
          lastLoginAt: new Date(),
          updatedAt: new Date()
        }
      }
    )

    const token = generateToken({
      _id: user._id,
      email: user.email
    })

    res.json({
      message: 'Login successful',
      user: {
        id: user._id,
        email: user.email,
        name: user.name
      },
      token
    })

  } catch (error) {
    console.error('Login error:', error)
    res.status(500).json({ 
      message: 'Internal server error during login',
      code: 'LOGIN_ERROR'
    })
  }
}