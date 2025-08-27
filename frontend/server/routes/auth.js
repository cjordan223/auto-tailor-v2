import express from 'express'
import bcrypt from 'bcryptjs'
import { ObjectId } from 'mongodb'
import { generateToken, authenticateToken } from '../middleware/auth.js'
import databaseConnection from '../config/database.js'

const router = express.Router()

const validateEmail = (email) => {
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
  return emailRegex.test(email)
}

const validatePassword = (password) => {
  return password && password.length >= 8
}

// Registration is currently restricted to authorized users only
// General registration is commented out for security
router.post('/register', async (req, res) => {
  try {
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

    const db = databaseConnection.db
    if (!db) {
      return res.status(503).json({ 
        message: 'Database not available',
        code: 'DB_UNAVAILABLE'
      })
    }

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

    delete newUser.password
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
})

/* 
// GENERAL REGISTRATION (Currently disabled)
// Uncomment this section to enable open registration in the future
router.post('/register', async (req, res) => {
  try {
    const { email, password, name } = req.body

    if (!email || !password || !name) {
      return res.status(400).json({ 
        message: 'Email, password, and name are required',
        code: 'MISSING_FIELDS'
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

    const db = databaseConnection.db
    if (!db) {
      return res.status(503).json({ 
        message: 'Database not available',
        code: 'DB_UNAVAILABLE'
      })
    }

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

    delete newUser.password
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
})
*/

router.post('/login', async (req, res) => {
  try {
    const { email, password } = req.body

    if (!email || !password) {
      return res.status(400).json({ 
        message: 'Email and password are required',
        code: 'MISSING_CREDENTIALS'
      })
    }

    const db = databaseConnection.db
    if (!db) {
      return res.status(503).json({ 
        message: 'Database not available',
        code: 'DB_UNAVAILABLE'
      })
    }

    const users = db.collection('users')
    const user = await users.findOne({ email: email.toLowerCase() })

    if (!user) {
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

    const isValidPassword = await bcrypt.compare(password, user.password)
    if (!isValidPassword) {
      return res.status(401).json({ 
        message: 'Invalid credentials',
        code: 'INVALID_CREDENTIALS'
      })
    }

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
})

router.get('/me', authenticateToken, async (req, res) => {
  try {
    const db = databaseConnection.db
    if (!db) {
      return res.status(503).json({ 
        message: 'Database not available',
        code: 'DB_UNAVAILABLE'
      })
    }

    const users = db.collection('users')
    const user = await users.findOne(
      { _id: new ObjectId(req.user.userId) },
      { projection: { password: 0 } }
    )

    if (!user) {
      return res.status(404).json({ 
        message: 'User not found',
        code: 'USER_NOT_FOUND'
      })
    }

    res.json({
      user: {
        id: user._id,
        email: user.email,
        name: user.name,
        createdAt: user.createdAt,
        lastLoginAt: user.lastLoginAt
      }
    })

  } catch (error) {
    console.error('Get user error:', error)
    res.status(500).json({ 
      message: 'Internal server error',
      code: 'USER_FETCH_ERROR'
    })
  }
})

router.post('/logout', authenticateToken, (req, res) => {
  res.json({ message: 'Logout successful' })
})

export default router