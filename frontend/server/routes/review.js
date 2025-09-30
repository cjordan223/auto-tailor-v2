import express from 'express'
import { spawn } from 'child_process'
import path from 'path'
import { fileURLToPath } from 'url'

const __filename = fileURLToPath(import.meta.url)
const __dirname = path.dirname(__filename)

const router = express.Router()

// Review endpoint - Generate LLM overview and structured diffs
router.get('/', async (req, res) => {
  try {
    const { format = 'json', provider } = req.query
    
    // Execute the Python CLI review command
    // In Docker production, Python is in PATH due to ENV PATH="/opt/venv/bin:$PATH"
    const pythonCmd = process.env.NODE_ENV === 'production' ? 'python' : '/opt/homebrew/opt/python@3.13/bin/python3.13'
    
    const args = ['-m', 'tex_tailor.cli', 'review', '--format', format]
    if (provider) {
      args.push('--provider', provider)
    }
    
    const child = spawn(pythonCmd, args, {
      cwd: path.join(__dirname, '../../..'), // Project root
      stdio: ['pipe', 'pipe', 'pipe'],
      env: {
        ...process.env,
        PYTHONPATH: path.join(__dirname, '../../..'), // Add project root to Python path
        ...(provider && { PROVIDER: provider })
      }
    })
    
    let stdout = ''
    let stderr = ''
    
    child.stdout.on('data', (data) => {
      stdout += data.toString()
    })
    
    child.stderr.on('data', (data) => {
      stderr += data.toString()
    })
    
    child.on('close', (code) => {
      try {
        if (code === 0) {
          // Successfully generated review
          if (format === 'json') {
            // Parse JSON output, skipping any non-JSON lines (like LLM generation messages)
            const lines = stdout.split('\n')
            let jsonStart = -1
            
            // Find where JSON starts (look for opening brace)
            for (let i = 0; i < lines.length; i++) {
              if (lines[i].trim().startsWith('{')) {
                jsonStart = i
                break
              }
            }
            
            if (jsonStart >= 0) {
              const jsonOutput = lines.slice(jsonStart).join('\n')
              try {
                const reviewData = JSON.parse(jsonOutput)
                res.json({
                  success: true,
                  data: reviewData
                })
              } catch (parseError) {
                // Fallback: return as text if JSON parsing fails
                res.json({
                  success: true,
                  data: {
                    overview: "Review generated successfully",
                    raw_output: stdout,
                    format: 'text'
                  }
                })
              }
            } else {
              // No JSON found, return as text
              res.json({
                success: true,
                data: {
                  overview: "Review generated successfully",
                  raw_output: stdout,
                  format: 'text'
                }
              })
            }
          } else {
            // Text format
            res.json({
              success: true,
              data: {
                overview: "Review generated successfully",
                raw_output: stdout,
                format: 'text'
              }
            })
          }
        } else {
          res.status(500).json({
            success: false,
            error: `Review generation failed with code ${code}`,
            stderr: stderr.slice(-500),
            stdout: stdout.slice(-500)
          })
        }
      } catch (error) {
        console.error('Error processing review response:', error)
        res.status(500).json({
          success: false,
          error: 'Failed to process review response',
          details: error.message
        })
      }
    })
    
    child.on('error', (error) => {
      console.error('Review process error:', error)
      res.status(500).json({
        success: false,
        error: 'Failed to start review process',
        details: error.message
      })
    })
    
  } catch (error) {
    console.error('Review endpoint error:', error)
    res.status(500).json({
      success: false,
      error: 'Review endpoint error',
      details: error.message
    })
  }
})

export default router