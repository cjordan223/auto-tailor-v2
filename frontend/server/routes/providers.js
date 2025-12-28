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
          { 
            id: 'gemini-2.5-flash-lite', 
            name: 'Gemini 2.5 Flash-Lite', 
            description: 'Fast and efficient - perfect balance of speed and quality for everyday use',
            recommended: true,
            quality: 'Good',
            speed: 'Very Fast',
            rateLimits: '15 RPM, 1,000 RPD (Free) / 4,000 RPM (Paid)'
          },
          { 
            id: 'gemini-2.5-flash', 
            name: 'Gemini 2.5 Flash', 
            description: 'Standard production model with excellent performance',
            recommended: false,
            quality: 'High',
            speed: 'Fast',
            rateLimits: '10 RPM, 250 RPD (Free) / 1,000+ RPM (Paid)'
          },
          { 
            id: 'gemini-2.5-pro', 
            name: 'Gemini 2.5 Pro', 
            description: 'Highest quality analysis - best for final review before submitting',
            recommended: false,
            quality: 'Highest',
            speed: 'Medium',
            rateLimits: '5 RPM, 100 RPD (Free) / 150+ RPM (Paid)'
          },
          { 
            id: 'gemini-1.5-flash', 
            name: 'Gemini 1.5 Flash', 
            description: 'Proven stable model - current default choice',
            recommended: false,
            quality: 'High',
            speed: 'Fast',
            rateLimits: '15 RPM, 1,500 RPD (Free) / 1,000+ RPM (Paid)'
          },
          { 
            id: 'gemini-1.5-pro-latest', 
            name: 'Gemini 1.5 Pro', 
            description: 'High-quality tasks with detailed analysis',
            recommended: false,
            quality: 'Highest',
            speed: 'Medium',
            rateLimits: '2 RPM, 50 RPD (Free) / 150+ RPM (Paid)'
          }
        ]
      },
      {
        id: 'openai',
        name: 'OpenAI',
        available: !!process.env.OPENAI_API_KEY,
        recommended: false,
        models: [
          { 
            id: 'gpt-4o-mini', 
            name: 'GPT-4o Mini', 
            description: 'Fast and cost-effective',
            recommended: true,
            quality: 'High',
            speed: 'Fast',
            rateLimits: '3,000 RPM (Paid)'
          },
          { 
            id: 'gpt-4o', 
            name: 'GPT-4o', 
            description: 'Highest quality with advanced reasoning',
            recommended: false,
            quality: 'Highest',
            speed: 'Medium',
            rateLimits: '500 RPM (Paid)'
          }
        ]
      },
      {
        id: 'ollama',
        name: 'Ollama (Local)',
        available: !!process.env.OLLAMA_BASE_URL,
        recommended: false,
        models: [
          { 
            id: 'resume-editor:latest',
            name: 'Resume Editor (Custom)',
            description: 'Custom model tuned for resume and cover letter tailoring.',
            recommended: true,
            quality: 'Excellent',
            speed: 'Medium',
            rateLimits: 'No limits (local)'
          },
          { 
            id: 'llama3.2:3b', 
            name: 'Llama 3.2 3B', 
            description: 'Fast and lightweight - excellent for quick resume customization',
            recommended: false,
            quality: 'Good',
            speed: 'Very Fast',
            rateLimits: 'No limits (local)'
          },
          { 
            id: 'qwen2.5:14b-instruct', 
            name: 'Qwen2.5 14B', 
            description: 'Good quality, requires powerful hardware',
            recommended: false,
            quality: 'Good',
            speed: 'Medium',
            rateLimits: 'No limits (local)'
          },
          { 
            id: 'llama3:8b', 
            name: 'Llama 3 8B', 
            description: 'Lighter model, faster inference',
            recommended: false,
            quality: 'Good',
            speed: 'Fast',
            rateLimits: 'No limits (local)'
          },
          { 
            id: 'phi3:mini', 
            name: 'Phi-3 Mini (3.8B)', 
            description: 'Fastest and most lightweight model, suitable for simple tasks',
            recommended: false,
            quality: 'Good',
            speed: 'Very Fast',
            rateLimits: 'No limits (local)'
          },
          { 
            id: 'llama3.1:70b', 
            name: 'Llama 3.1 (70B)', 
            description: 'Highest quality local model, requires significant resources',
            recommended: false,
            quality: 'Highest',
            speed: 'Slow',
            rateLimits: 'No limits (local)'
          }
        ]
      }
    ]

    res.json({ providers })
  } catch (error) {
    res.status(500).json({ message: error.message })
  }
})

export default router
