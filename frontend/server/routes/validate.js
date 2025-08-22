import express from 'express'
import axios from 'axios'

const router = express.Router()

/**
 * Validate API keys for different providers
 */
router.post('/', async (req, res) => {
  try {
    const { provider, apiKey, ollamaUrl } = req.body

    if (!provider) {
      return res.status(400).json({ message: 'Provider is required' })
    }

    let validation = { valid: false, error: null }

    switch (provider) {
      case 'gemini':
        validation = await validateGeminiKey(apiKey)
        break
      case 'openai':
        validation = await validateOpenAIKey(apiKey)
        break
      case 'ollama':
        validation = await validateOllamaServer(ollamaUrl || 'http://localhost:11434')
        break
      default:
        return res.status(400).json({ message: `Unsupported provider: ${provider}` })
    }

    res.json({
      provider,
      valid: validation.valid,
      error: validation.error
    })

  } catch (error) {
    res.status(500).json({ 
      message: 'Validation failed',
      error: error.message 
    })
  }
})

/**
 * Validate Gemini API key
 */
async function validateGeminiKey(apiKey) {
  if (!apiKey || apiKey.trim().length === 0) {
    return { valid: false, error: 'API key is required' }
  }

  try {
    const response = await axios.get(
      `https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key=${apiKey}`,
      {
        timeout: 10000,
        validateStatus: (status) => status === 400 || status === 200 // 400 is expected for missing body
      }
    )

    // If we get a 400 with specific error about missing content, the key is valid
    if (response.status === 400 && response.data?.error?.message?.includes('content')) {
      return { valid: true, error: null }
    }

    // If we get 200, key is definitely valid
    if (response.status === 200) {
      return { valid: true, error: null }
    }

    return { 
      valid: false, 
      error: response.data?.error?.message || 'Invalid API key' 
    }

  } catch (error) {
    if (error.response?.status === 403) {
      return { valid: false, error: 'Invalid API key' }
    }
    if (error.response?.status === 429) {
      return { valid: false, error: 'API rate limit exceeded' }
    }
    return { 
      valid: false, 
      error: error.message || 'Failed to validate API key' 
    }
  }
}

/**
 * Validate OpenAI API key
 */
async function validateOpenAIKey(apiKey) {
  if (!apiKey || apiKey.trim().length === 0) {
    return { valid: false, error: 'API key is required' }
  }

  try {
    const response = await axios.get(
      'https://api.openai.com/v1/models',
      {
        headers: {
          'Authorization': `Bearer ${apiKey}`,
          'Content-Type': 'application/json'
        },
        timeout: 10000
      }
    )

    if (response.status === 200) {
      return { valid: true, error: null }
    }

    return { valid: false, error: 'Invalid API key' }

  } catch (error) {
    if (error.response?.status === 401) {
      return { valid: false, error: 'Invalid API key' }
    }
    if (error.response?.status === 429) {
      return { valid: false, error: 'API rate limit exceeded' }
    }
    return { 
      valid: false, 
      error: error.message || 'Failed to validate API key' 
    }
  }
}

/**
 * Validate Ollama server connection
 */
async function validateOllamaServer(serverUrl) {
  if (!serverUrl || serverUrl.trim().length === 0) {
    return { valid: false, error: 'Server URL is required' }
  }

  try {
    const response = await axios.get(`${serverUrl}/api/tags`, {
      timeout: 5000
    })

    if (response.status === 200) {
      const models = response.data?.models || []
      return { 
        valid: true, 
        error: null,
        info: `Found ${models.length} models` 
      }
    }

    return { valid: false, error: 'Ollama server not responding' }

  } catch (error) {
    if (error.code === 'ECONNREFUSED') {
      return { valid: false, error: 'Cannot connect to Ollama server. Is it running?' }
    }
    return { 
      valid: false, 
      error: error.message || 'Failed to connect to Ollama server' 
    }
  }
}

export default router