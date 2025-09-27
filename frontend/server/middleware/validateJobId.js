/**
 * Middleware to validate jobId parameters
 * Ensures jobIds are UUIDs to prevent directory traversal and other attacks
 */

const UUID_REGEX = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i

export const validateJobId = (paramName = 'jobId') => {
  return (req, res, next) => {
    const jobId = req.params[paramName]
    
    if (!jobId) {
      return res.status(400).json({
        success: false,
        error: `${paramName} parameter is required`
      })
    }
    
    // Validate that jobId is a proper UUID format
    if (!UUID_REGEX.test(jobId)) {
      return res.status(400).json({
        success: false,
        error: `Invalid ${paramName} format. Must be a valid UUID.`
      })
    }
    
    // Additional security: prevent excessively long IDs
    if (jobId.length > 36) {
      return res.status(400).json({
        success: false,
        error: `${paramName} is too long`
      })
    }
    
    next()
  }
}

export default validateJobId