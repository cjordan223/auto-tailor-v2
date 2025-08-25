import fs from 'fs/promises'
import path from 'path'
import { fileURLToPath } from 'url'

const __filename = fileURLToPath(import.meta.url)
const __dirname = path.dirname(__filename)

// Create logs directory if it doesn't exist
const logsDir = path.join(__dirname, '../../logs')
const tempLogFile = path.join(logsDir, 'temp_workflow.txt')

// Noise patterns to filter out
const NOISE_PATTERNS = [
  /health check/i,
  /status check/i,
  /GET \/health/i,
  /GET \/api\/status/i,
  /GET \/api\/providers/i,
  /GET \/api\/process\/log/i,
  /POST \/api\/validate/i,
  /OPTIONS/i,
  /favicon\.ico/i,
  /static\//i,
  /\.css$/i,
  /\.js$/i,
  /\.png$/i,
  /\.jpg$/i,
  /\.ico$/i,
  /CORS/i,
  /preflight/i
]

class WorkflowLogger {
  constructor() {
    this.currentJobId = null
    this.isWorkflowActive = false
  }

  /**
   * Start a new workflow run
   */
  async startWorkflow(jobId) {
    this.currentJobId = jobId
    this.isWorkflowActive = true
    
    // Clear the temporary log file
    try {
      await fs.writeFile(tempLogFile, '', 'utf8')
    } catch (error) {
      console.error('Failed to clear temp log file:', error)
    }
    
    // Write workflow header
    const timestamp = new Date().toISOString()
    const header = `=== Workflow Run Started ===
Job ID: ${jobId}
Started: ${timestamp}
${'='.repeat(50)}

`
    await this.writeToTempLog(header)
  }

  /**
   * End the current workflow run
   */
  async endWorkflow() {
    if (!this.isWorkflowActive) return
    
    const timestamp = new Date().toISOString()
    const footer = `
${'='.repeat(50)}
=== Workflow Run Completed ===
Job ID: ${this.currentJobId}
Completed: ${timestamp}
`
    await this.writeToTempLog(footer)
    
    this.currentJobId = null
    this.isWorkflowActive = false
  }

  /**
   * Write workflow log entry
   */
  async writeWorkflowLog(jobId, message, type = 'info') {
    try {
      const timestamp = new Date().toISOString()
      const logEntry = `[${timestamp}] [${jobId}] [${type.toUpperCase()}] ${message}\n`
      
      // Write to persistent workflow log
      const logFile = path.join(logsDir, 'workflow.log')
      await fs.appendFile(logFile, logEntry, 'utf8')
      
      // Write to temporary run log if workflow is active
      if (this.isWorkflowActive && this.currentJobId === jobId) {
        await this.writeToTempLog(`[${type.toUpperCase()}] ${message}\n`)
      }
    } catch (error) {
      console.error('Failed to write workflow log:', error)
    }
  }

  /**
   * Write to temporary log file
   */
  async writeToTempLog(content) {
    try {
      await fs.appendFile(tempLogFile, content, 'utf8')
    } catch (error) {
      console.error('Failed to write to temp log:', error)
    }
  }

  /**
   * Filter and log server output
   */
  async logServerOutput(jobId, output, isError = false) {
    if (!this.isWorkflowActive || this.currentJobId !== jobId) {
      return
    }

    const lines = output.split('\n').filter(line => line.trim())
    
    for (const line of lines) {
      // Skip noise patterns
      if (this.isNoise(line)) {
        continue
      }
      
      // Only log meaningful workflow output
      if (this.isWorkflowOutput(line)) {
        const type = isError ? 'error' : 'workflow'
        // Only write to temp log, not to persistent log (to avoid duplication)
        await this.writeToTempLog(`${isError ? '[ERROR]' : '[WORKFLOW]'} ${line.trim()}\n`)
      }
    }
  }

  /**
   * Check if a line is noise (should be filtered out)
   */
  isNoise(line) {
    return NOISE_PATTERNS.some(pattern => pattern.test(line))
  }

  /**
   * Check if a line contains meaningful workflow output
   */
  isWorkflowOutput(line) {
    // Skip lines that already have timestamps (they're already formatted)
    if (line.match(/^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}/)) {
      return false
    }
    
    return line.includes('🔄') || 
           line.includes('✅') || 
           line.includes('❌') || 
           line.includes('📋') || 
           line.includes('🔍') || 
           line.includes('🔧') ||
           line.includes('📊') || 
           line.includes('🎉') || 
           line.includes('Step') ||
           line.includes('Created:') || 
           line.includes('Extracted') || 
           line.includes('Saved') ||
           line.includes('Applied') || 
           line.includes('Comparing') || 
           line.includes('Rendering') ||
           line.includes('Workflow') ||
           line.includes('Processing') ||
           line.includes('Error') ||
           line.includes('Failed') ||
           line.includes('Warning') ||
           line.includes('Completed')
  }

  /**
   * Get the current temporary log content
   */
  async getTempLog() {
    try {
      const content = await fs.readFile(tempLogFile, 'utf8')
      return {
        success: true,
        log: content,
        lastModified: new Date().toISOString()
      }
    } catch (error) {
      if (error.code === 'ENOENT') {
        return {
          success: true,
          log: 'No workflow log found yet.',
          lastModified: null
        }
      }
      throw error
    }
  }

  /**
   * Clear the temporary log
   */
  async clearTempLog() {
    try {
      await fs.writeFile(tempLogFile, '', 'utf8')
      return { success: true }
    } catch (error) {
      console.error('Failed to clear temp log:', error)
      return { success: false, error: error.message }
    }
  }
}

// Export singleton instance
export const workflowLogger = new WorkflowLogger()
