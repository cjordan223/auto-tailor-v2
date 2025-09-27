import { getApiUrl } from '../config/api.js'

/**
 * Poll for PDF file updates after recompilation
 * @param {string} jobId - The job ID
 * @param {string} fileType - The file type ('resume' or 'cover-letter')
 * @param {number} sinceTimestamp - Timestamp to check for updates since
 * @param {number} maxAttempts - Maximum number of polling attempts
 * @param {number} pollInterval - Interval between polls in milliseconds
 * @returns {Promise<boolean>} - True if PDF was updated, false if timed out
 */
export const waitForPdfUpdate = async (
  jobId,
  fileType,
  sinceTimestamp = Date.now(),
  maxAttempts = 15,
  pollInterval = 500
) => {
  console.log(`Starting PDF update polling for ${jobId}/${fileType}`, {
    sinceTimestamp: new Date(sinceTimestamp).toISOString(),
    maxAttempts,
    pollInterval
  })

  for (let attempt = 1; attempt <= maxAttempts; attempt++) {
    try {
      const response = await fetch(
        getApiUrl(`/check-pdf/${jobId}/${fileType}?since=${sinceTimestamp}`)
      )

      if (!response.ok) {
        console.warn(`PDF check attempt ${attempt} failed: ${response.statusText}`)
        await new Promise(resolve => setTimeout(resolve, pollInterval))
        continue
      }

      const data = await response.json()

      console.log(`PDF check attempt ${attempt}:`, {
        exists: data.exists,
        updated: data.updated,
        size: data.size,
        age: data.age ? `${data.age}ms` : 'unknown',
        modified: data.modified ? new Date(data.modified).toISOString() : 'unknown'
      })

      if (data.success && data.exists && data.updated) {
        console.log(`✅ PDF update confirmed for ${jobId}/${fileType} after ${attempt} attempts`)
        return true
      }

      // If PDF doesn't exist, keep trying (compilation might still be in progress)
      if (!data.exists) {
        console.log(`PDF file not found yet, continuing to poll...`)
      }

    } catch (error) {
      console.warn(`PDF check attempt ${attempt} error:`, error.message)
    }

    // Wait before next attempt (except on last attempt)
    if (attempt < maxAttempts) {
      await new Promise(resolve => setTimeout(resolve, pollInterval))
    }
  }

  console.warn(`❌ PDF update polling timed out for ${jobId}/${fileType} after ${maxAttempts} attempts`)
  return false
}

/**
 * Enhanced recompile function with polling-based verification
 * @param {string} jobId - The job ID
 * @param {string} fileType - The file type ('resume' or 'cover-letter')
 * @param {string} content - The LaTeX content to compile
 * @returns {Promise<{success: boolean, updated: boolean, error?: string}>}
 */
export const recompileWithVerification = async (jobId, fileType, content) => {
  const startTime = Date.now()

  try {
    console.log(`Starting recompilation for ${jobId}/${fileType}`)

    // Make the recompile API call
    const response = await fetch(getApiUrl(`/recompile/${jobId}/${fileType}`), {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ content })
    })

    if (!response.ok) {
      throw new Error(`Recompilation failed: ${response.statusText}`)
    }

    const result = await response.json()

    if (!result.success) {
      throw new Error(result.error || 'Recompilation failed')
    }

    console.log(`Recompilation API call successful for ${jobId}/${fileType}`, {
      fileSize: result.fileSize,
      lastModified: result.lastModified ? new Date(result.lastModified).toISOString() : 'unknown'
    })

    // Wait for PDF file to be updated using polling
    const pdfUpdated = await waitForPdfUpdate(jobId, fileType, startTime)

    return {
      success: true,
      updated: pdfUpdated,
      fileSize: result.fileSize,
      lastModified: result.lastModified
    }

  } catch (error) {
    console.error(`Recompilation with verification failed for ${jobId}/${fileType}:`, error)
    return {
      success: false,
      updated: false,
      error: error.message
    }
  }
}

/**
 * Generate a cache-busting PDF URL with aggressive parameters
 * @param {string} jobId - The job ID
 * @param {string} fileType - The file type ('resume' or 'cover-letter')
 * @param {number} cacheBuster - Cache busting timestamp
 * @param {number} refreshId - Additional refresh identifier
 * @returns {string} - The cache-busted URL
 */
export const generatePdfUrl = (jobId, fileType, cacheBuster = Date.now(), refreshId = 0) => {
  const baseUrl = getApiUrl(`/view/${jobId}/${fileType}`)
  const random = Math.random().toString(36).substring(7)
  const timestamp = Date.now()

  // Use multiple cache-busting strategies
  const params = new URLSearchParams({
    t: cacheBuster.toString(),
    v: timestamp.toString(),
    r: refreshId.toString(),
    cb: random,
    _: Math.random().toString(36).substring(7) // Additional randomness
  })

  // PDF viewer parameters to control display
  const pdfParams = [
    'toolbar=1',
    'navpanes=0',
    'scrollbar=1',
    'view=FitH',
    'pagemode=none',
    'statusbar=0',
    'messages=0',
    'viewrect=0,0,800,600'
  ].join('&')

  return `${baseUrl}?${params.toString()}#${pdfParams}`
}