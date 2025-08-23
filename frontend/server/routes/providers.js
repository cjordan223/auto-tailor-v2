import express from 'express'

const router = express.Router()

// Get available providers and their status
router.get('/', async (req, res) => {
  try {
    const providers = [
      {
        id: 'gemini',
        name: 'Google Gemini',
        available: !!process.env.GEMINI_API_KEY,
        recommended: true,
        models: [
          { id: 'gemini-1.5-flash', name: 'Gemini 1.5 Flash', description: 'Fast and efficient (Recommended)' },
          { id: 'gemini-1.5-pro', name: 'Gemini 1.5 Pro', description: 'Higher quality, slower' },
          { id: 'gemini-1.0-pro', name: 'Gemini 1.0 Pro', description: 'High rate limits (60 RPM), good for testing' }
        ]
      },
      {
        id: 'openai',
        name: 'OpenAI',
        available: !!process.env.OPENAI_API_KEY,
        recommended: false,
        models: [
          { id: 'gpt-4o-mini', name: 'GPT-4o Mini', description: 'Fast and cost-effective' },
          { id: 'gpt-4o', name: 'GPT-4o', description: 'Highest quality' }
        ]
      },
      {
        id: 'ollama',
        name: 'Ollama (Local)',
        available: true, // Always available if Ollama is running
        recommended: false,
        models: [
          { id: 'qwen2.5:14b-instruct', name: 'Qwen2.5 14B', description: 'Good quality' },
          { id: 'llama3.1:8b', name: 'Llama 3.1 8B', description: 'Lighter model' }
        ]
      }
    ]

    res.json({ providers })
  } catch (error) {
    res.status(500).json({ message: error.message })
  }
})

export default router