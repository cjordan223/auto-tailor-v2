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

const validatePassword = (password) => {
  return password && password.length >= 8
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

  try {
    // Initialize database connection
    const dbInitialized = await initializeDatabase()
    if (!dbInitialized) {
      return res.status(503).json({
        message: 'Database not available',
        code: 'DB_UNAVAILABLE'
      })
    }

    const { email, password, name } = req.body

    if (!email || !password || !name) {
      return res.status(400).json({ 
        message: 'Email, password, and name are required',
        code: 'MISSING_FIELDS'
      })
    }

    // RESTRICTED REGISTRATION - Only specific email allowed
    const allowedEmail = 'connercharlesjordan@gmail.com'
    if (email.toLowerCase() !== allowedEmail) {
      return res.status(403).json({
        message: 'Registration is currently restricted to authorized users only',
        code: 'REGISTRATION_RESTRICTED'
      })
    }

    if (!validateEmail(email)) {
      return res.status(400).json({ 
        message: 'Invalid email format',
        code: 'INVALID_EMAIL'
      })
    }

    if (!validatePassword(password)) {
      return res.status(400).json({ 
        message: 'Password must be at least 8 characters long',
        code: 'INVALID_PASSWORD'
      })
    }

    const db = databaseConnection.getDb()
    const users = db.collection('users')

    const existingUser = await users.findOne({ email: email.toLowerCase() })
    if (existingUser) {
      return res.status(409).json({ 
        message: 'User already exists with this email',
        code: 'USER_EXISTS'
      })
    }

    const saltRounds = 12
    const hashedPassword = await bcrypt.hash(password, saltRounds)

    const newUser = {
      email: email.toLowerCase(),
      name: name.trim(),
      password: hashedPassword,
      createdAt: new Date(),
      updatedAt: new Date(),
      emailVerified: false,
      isActive: true
    }

    const result = await users.insertOne(newUser)
    
    const token = generateToken({
      _id: result.insertedId,
      email: newUser.email
    })

    res.status(201).json({
      message: 'User registered successfully',
      user: {
        id: result.insertedId,
        email: newUser.email,
        name: newUser.name
      },
      token
    })

  } catch (error) {
    console.error('Registration error:', error)
    res.status(500).json({ 
      message: 'Internal server error during registration',
      code: 'REGISTRATION_ERROR'
    })
  }
}