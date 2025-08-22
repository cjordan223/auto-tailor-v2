import fs from 'fs/promises'
import path from 'path'
import { fileURLToPath } from 'url'

const __filename = fileURLToPath(import.meta.url)
const __dirname = path.dirname(__filename)

class TempCleanup {
  constructor(options = {}) {
    this.tempDir = options.tempDir || path.join(__dirname, '../../temp')
    this.maxAge = options.maxAge || 7 * 24 * 60 * 60 * 1000 // 7 days in milliseconds
    this.maxSize = options.maxSize || 500 * 1024 * 1024 // 500MB in bytes
    this.preserveActive = options.preserveActive ?? true
    this.dryRun = options.dryRun ?? false
    this.logger = options.logger || console
  }

  async getDirectorySize(dirPath) {
    try {
      const stats = await fs.stat(dirPath)
      if (!stats.isDirectory()) {
        return stats.size
      }

      let totalSize = 0
      const items = await fs.readdir(dirPath)
      
      for (const item of items) {
        const itemPath = path.join(dirPath, item)
        totalSize += await this.getDirectorySize(itemPath)
      }
      
      return totalSize
    } catch (error) {
      return 0
    }
  }

  async isJobActive(jobDir) {
    if (!this.preserveActive) return false
    
    try {
      const statusFile = path.join(jobDir, 'status.json')
      const statusContent = await fs.readFile(statusFile, 'utf8')
      const status = JSON.parse(statusContent)
      
      return status.status === 'processing'
    } catch (error) {
      return false
    }
  }

  async getTempDirectories() {
    try {
      await fs.access(this.tempDir)
      const items = await fs.readdir(this.tempDir)
      
      const directories = []
      for (const item of items) {
        const itemPath = path.join(this.tempDir, item)
        const stats = await fs.stat(itemPath)
        
        if (stats.isDirectory()) {
          directories.push({
            name: item,
            path: itemPath,
            created: stats.birthtime,
            modified: stats.mtime,
            size: await this.getDirectorySize(itemPath),
            active: await this.isJobActive(itemPath)
          })
        }
      }
      
      return directories
    } catch (error) {
      this.logger.warn('Unable to read temp directory:', error.message)
      return []
    }
  }

  async cleanupByAge() {
    const directories = await this.getTempDirectories()
    const now = Date.now()
    const deletedDirs = []
    
    for (const dir of directories) {
      const age = now - dir.created.getTime()
      
      if (age > this.maxAge && !dir.active) {
        try {
          if (this.dryRun) {
            this.logger.info(`[DRY RUN] Would delete old directory: ${dir.name} (${Math.round(age / (24 * 60 * 60 * 1000))} days old)`)
          } else {
            await fs.rm(dir.path, { recursive: true, force: true })
            this.logger.info(`Deleted old directory: ${dir.name} (${Math.round(age / (24 * 60 * 60 * 1000))} days old, ${this.formatSize(dir.size)})`)
          }
          deletedDirs.push(dir)
        } catch (error) {
          this.logger.error(`Failed to delete directory ${dir.name}:`, error.message)
        }
      }
    }
    
    return deletedDirs
  }

  async cleanupBySize() {
    const directories = await this.getTempDirectories()
    const totalSize = directories.reduce((sum, dir) => sum + dir.size, 0)
    
    if (totalSize <= this.maxSize) {
      return []
    }

    // Sort by oldest first, but preserve active jobs
    const deletableFiles = directories
      .filter(dir => !dir.active)
      .sort((a, b) => a.created.getTime() - b.created.getTime())
    
    const deletedDirs = []
    let currentSize = totalSize
    
    for (const dir of deletableFiles) {
      if (currentSize <= this.maxSize) break
      
      try {
        if (this.dryRun) {
          this.logger.info(`[DRY RUN] Would delete for size limit: ${dir.name} (${this.formatSize(dir.size)})`)
        } else {
          await fs.rm(dir.path, { recursive: true, force: true })
          this.logger.info(`Deleted for size limit: ${dir.name} (${this.formatSize(dir.size)})`)
        }
        deletedDirs.push(dir)
        currentSize -= dir.size
      } catch (error) {
        this.logger.error(`Failed to delete directory ${dir.name}:`, error.message)
      }
    }
    
    return deletedDirs
  }

  async cleanup() {
    const startTime = Date.now()
    this.logger.info('Starting temp directory cleanup...')
    
    try {
      const directories = await this.getTempDirectories()
      const totalSize = directories.reduce((sum, dir) => sum + dir.size, 0)
      const activeJobs = directories.filter(dir => dir.active).length
      
      this.logger.info(`Found ${directories.length} temp directories (${this.formatSize(totalSize)} total, ${activeJobs} active jobs)`)
      
      const deletedByAge = await this.cleanupByAge()
      const deletedBySize = await this.cleanupBySize()
      
      const allDeleted = [...new Set([...deletedByAge, ...deletedBySize])]
      const deletedSize = allDeleted.reduce((sum, dir) => sum + dir.size, 0)
      
      const endTime = Date.now()
      const duration = endTime - startTime
      
      const result = {
        success: true,
        duration: duration,
        totalDirectories: directories.length,
        deletedDirectories: allDeleted.length,
        freedSpace: deletedSize,
        activeJobsPreserved: activeJobs,
        deleted: allDeleted.map(dir => ({
          name: dir.name,
          age: Math.round((Date.now() - dir.created.getTime()) / (24 * 60 * 60 * 1000)),
          size: dir.size
        }))
      }
      
      this.logger.info(`Cleanup completed in ${duration}ms: ${allDeleted.length} directories deleted, ${this.formatSize(deletedSize)} freed`)
      return result
      
    } catch (error) {
      this.logger.error('Cleanup failed:', error.message)
      return {
        success: false,
        error: error.message,
        duration: Date.now() - startTime
      }
    }
  }

  async getStats() {
    try {
      const directories = await this.getTempDirectories()
      const totalSize = directories.reduce((sum, dir) => sum + dir.size, 0)
      const oldDirectories = directories.filter(dir => {
        const age = Date.now() - dir.created.getTime()
        return age > this.maxAge && !dir.active
      })
      const oldSize = oldDirectories.reduce((sum, dir) => sum + dir.size, 0)
      
      return {
        totalDirectories: directories.length,
        totalSize: totalSize,
        oldDirectories: oldDirectories.length,
        oldSize: oldSize,
        activeJobs: directories.filter(dir => dir.active).length,
        canFreeSpace: oldSize,
        exceedsMaxSize: totalSize > this.maxSize,
        maxSize: this.maxSize,
        maxAge: this.maxAge
      }
    } catch (error) {
      return {
        error: error.message
      }
    }
  }

  formatSize(bytes) {
    if (bytes === 0) return '0 B'
    const k = 1024
    const sizes = ['B', 'KB', 'MB', 'GB']
    const i = Math.floor(Math.log(bytes) / Math.log(k))
    return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i]
  }
}

export default TempCleanup