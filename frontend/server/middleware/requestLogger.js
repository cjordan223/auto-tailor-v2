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

/**
 * Check if a request should be logged (filter out noise)
 */
function shouldLogRequest(req) {
  const url = req.url
  const method = req.method
  
  // Skip noise patterns
  return !NOISE_PATTERNS.some(pattern => pattern.test(`${method} ${url}`))
}

export const requestLogger = (req, res, next) => {
  const start = Date.now()
  
  // Only log meaningful requests
  if (shouldLogRequest(req)) {
    console.log(`${new Date().toISOString()} ${req.method} ${req.url}`)
  }
  
  // Log response when finished (only for meaningful requests)
  res.on('finish', () => {
    if (shouldLogRequest(req)) {
      const duration = Date.now() - start
      console.log(`${new Date().toISOString()} ${req.method} ${req.url} ${res.statusCode} ${duration}ms`)
    }
  })
  
  next()
}