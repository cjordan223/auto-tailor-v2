import express from 'express'
import path from 'path'
import fs from 'fs/promises'
import { fileURLToPath } from 'url'

const __filename = fileURLToPath(import.meta.url)
const __dirname = path.dirname(__filename)

const router = express.Router()

const SKILL_CHUNKS = {
  'Programming Languages': 'SKILLS.Programming Languages',
  'Frontend': 'SKILLS.Frontend',
  'Backend': 'SKILLS.Backend',
  'Cloud & DevOps': 'SKILLS.Cloud & DevOps',
  'AI & LLM Tools': 'SKILLS.AI & LLM Tools',
  'Automation & Productivity': 'SKILLS.Automation & Productivity',
  'Security & Operating Systems': 'SKILLS.Security & Operating Systems',
  'Databases': 'SKILLS.Databases'
}

const SKILL_CATEGORY_KEYWORDS = {
  'Programming Languages': [
    'python', 'java', 'javascript', 'typescript', 'c++', 'c#', 'go', 'rust', 'swift',
    'kotlin', 'sql', 'bash', 'powershell', 'shell', 'scripting'
  ],
  'Frontend': [
    'frontend', 'react', 'vue', 'angular', 'html', 'css', 'ui', 'ux', 'tailwind',
    'next', 'vite'
  ],
  'Backend': [
    'backend', 'node', 'express', 'django', 'flask', 'fastapi', 'spring', 'api',
    'microservices'
  ],
  'Cloud & DevOps': [
    'cloud', 'devops', 'aws', 'azure', 'gcp', 'kubernetes', 'docker', 'terraform',
    'ansible', 'ci/cd', 'jenkins', 'github actions', 'gitlab', 'prometheus',
    'grafana', 'observability', 'monitoring', 'sre', 'site reliability'
  ],
  'AI & LLM Tools': [
    'ai', 'ml', 'machine learning', 'llm', 'nlp', 'pytorch', 'tensorflow',
    'scikit', 'langchain'
  ],
  'Security & Operating Systems': [
    'security', 'cyber', 'infosec', 'linux', 'unix', 'windows', 'macos', 'os',
    'operating system', 'network', 'tcp', 'ip', 'ipv4', 'ipv6', 'incident',
    'siem', 'forensics', 'firewall'
  ],
  'Databases': [
    'database', 'postgres', 'postgresql', 'mysql', 'mongodb', 'redis', 'dynamodb',
    'snowflake', 'databricks', 'clickhouse', 'sql server'
  ],
  'Automation & Productivity': [
    'automation', 'workflow', 'pipeline', 'productivity'
  ]
}

const RESUME_CATEGORY_MAP = {
  programming: 'Programming Languages',
  frontend: 'Frontend',
  backend: 'Backend',
  databases: 'Databases',
  cloud: 'Cloud & DevOps',
  devops: 'Cloud & DevOps',
  ai_ml: 'AI & LLM Tools',
  security: 'Security & Operating Systems',
  tools: 'Automation & Productivity'
}

const escapeRegExp = (text) => text.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')

const splitSkillList = (text) => {
  if (!text) return []
  const items = []
  let current = ''
  let depth = 0

  for (const char of text) {
    if (char === '(') depth += 1
    if (char === ')') depth = Math.max(0, depth - 1)

    if (char === ',' && depth === 0) {
      if (current.trim()) items.push(current.trim())
      current = ''
      continue
    }

    current += char
  }

  if (current.trim()) items.push(current.trim())
  return items
}

const normalizeSkill = (text) => text.toLowerCase().replace(/\s+/g, ' ').trim()

const escapeLatex = (text) => {
  if (!text) return text
  return text
    .replace(/\\/g, '\\textbackslash{}')
    .replace(/&/g, '\\&')
    .replace(/%/g, '\\%')
    .replace(/\$/g, '\\$')
    .replace(/#/g, '\\#')
    .replace(/_/g, '\\_')
    .replace(/{/g, '\\{')
    .replace(/}/g, '\\}')
    .replace(/~/g, '\\textasciitilde{}')
    .replace(/\^/g, '\\textasciicircum{}')
}

const getChunkContent = (texContent, chunkId) => {
  const pattern = new RegExp(
    `(% === LLM:CHUNK START ${escapeRegExp(chunkId)} ===\\s*\\n)([\\s\\S]*?)(\\n% === LLM:CHUNK END ${escapeRegExp(chunkId)} ===)`
  )
  const match = texContent.match(pattern)
  if (!match) return null

  return {
    fullMatch: match[0],
    prefix: match[1],
    content: match[2],
    suffix: match[3]
  }
}

const replaceChunkContent = (texContent, chunkId, newContent) => {
  const chunk = getChunkContent(texContent, chunkId)
  if (!chunk) return null

  const lines = chunk.content.split('\n')
  const firstLine = lines.find((line) => line.trim()) || ''
  const indentation = firstLine.match(/^\s*/)?.[0] || ''

  const indentedContent = newContent
    .split('\n')
    .map((line, index) => (index === 0 ? `${indentation}${line}` : `${indentation}${line}`))
    .join('\n')

  return texContent.replace(chunk.fullMatch, `${chunk.prefix}${indentedContent}${chunk.suffix}`)
}

const extractSkillsFromChunk = (chunkContent) => {
  if (!chunkContent) return { label: null, list: [] }

  const labelMatch = chunkContent.match(/\\textbf\{([^}]+):\}/)
  const listMatch = chunkContent.match(/\\textbf\{[^}]+:\}\s*([\s\S]*)/)
  const listText = listMatch ? listMatch[1].trim() : ''

  return {
    label: labelMatch ? labelMatch[1].trim() : null,
    list: splitSkillList(listText)
  }
}

const resolveSkillCategory = (term, availableCategories, skillsInventory) => {
  const normalizedTerm = normalizeSkill(term)

  if (skillsInventory?.skill_categories) {
    for (const [categoryKey, skills] of Object.entries(skillsInventory.skill_categories)) {
      const resumeCategory = RESUME_CATEGORY_MAP[categoryKey]
      if (!resumeCategory || !availableCategories.includes(resumeCategory)) {
        continue
      }

      const matched = skills.some((skill) => {
        const normalizedSkill = normalizeSkill(skill)
        return normalizedTerm === normalizedSkill ||
          normalizedTerm.includes(normalizedSkill) ||
          normalizedSkill.includes(normalizedTerm)
      })

      if (matched) return resumeCategory
    }
  }

  let bestCategory = null
  let bestScore = 0

  for (const category of availableCategories) {
    const keywords = SKILL_CATEGORY_KEYWORDS[category] || []
    const score = keywords.reduce((total, keyword) => {
      return normalizedTerm.includes(keyword) ? total + 1 : total
    }, 0)

    if (score > bestScore) {
      bestScore = score
      bestCategory = category
    }
  }

  if (bestCategory) return bestCategory

  return availableCategories.includes('Cloud & DevOps')
    ? 'Cloud & DevOps'
    : availableCategories[0]
}

// Add skill to baseline skills JSON file
router.post('/:jobId/add-skill', async (req, res) => {
  try {
    const { skill, category = 'conversational_skills', confidenceLevel = null } = req.body
    
    if (!skill) {
      return res.status(400).json({ message: 'Skill is required' })
    }
    
    // Validate category
    const validCategories = ['confirmed_skills', 'conversational_skills']
    if (!validCategories.includes(category)) {
      return res.status(400).json({ message: 'Invalid category. Must be confirmed_skills or conversational_skills' })
    }
    
    // Validate confidence level if provided
    const validConfidenceLevels = ['expert', 'proficient', 'familiar', 'learning']
    if (confidenceLevel && !validConfidenceLevels.includes(confidenceLevel)) {
      return res.status(400).json({ message: 'Invalid confidence level. Must be expert, proficient, familiar, or learning' })
    }
    
    // Path to baseline skills file
    const skillsFilePath = path.join(__dirname, '../../../templates/baseline_skills.json')
    
    try {
      // Check if file exists
      await fs.access(skillsFilePath)
    } catch (error) {
      return res.status(404).json({ message: 'Baseline skills file not found' })
    }
    
    // Read current skills file
    const skillsContent = await fs.readFile(skillsFilePath, 'utf-8')
    const skillsData = JSON.parse(skillsContent)
    
    // Check if skill already exists in any category
    const allSkills = [
      ...(skillsData.confirmed_skills || []),
      ...(skillsData.conversational_skills || []),
      ...(skillsData.exclude_skills || [])
    ]
    
    if (allSkills.includes(skill)) {
      return res.status(409).json({ 
        message: `Skill "${skill}" already exists in the skills inventory`,
        skill,
        category
      })
    }
    
    // Add skill to the specified category
    if (!skillsData[category]) {
      skillsData[category] = []
    }
    
    skillsData[category].push(skill)
    
    // Also add to confidence level category if specified
    if (confidenceLevel) {
      if (!skillsData.skill_confidence_levels) {
        skillsData.skill_confidence_levels = {}
      }
      if (!skillsData.skill_confidence_levels[confidenceLevel]) {
        skillsData.skill_confidence_levels[confidenceLevel] = []
      }
      
      // Only add if not already in this confidence level
      if (!skillsData.skill_confidence_levels[confidenceLevel].includes(skill)) {
        skillsData.skill_confidence_levels[confidenceLevel].push(skill)
        skillsData.skill_confidence_levels[confidenceLevel].sort()
      }
    }
    
    // Sort the skills alphabetically
    skillsData[category].sort()
    
    // Write back to file
    await fs.writeFile(skillsFilePath, JSON.stringify(skillsData, null, 2), 'utf-8')
    
    res.json({ 
      success: true, 
      message: `Skill "${skill}" added to ${category}${confidenceLevel ? ` as ${confidenceLevel} level` : ''}`,
      skill,
      category,
      confidenceLevel,
      updatedSkills: skillsData[category]
    })
    
  } catch (error) {
    console.error('Error adding skill:', error)
    res.status(500).json({ message: error.message })
  }
})

// Apply suggested addition directly to resume skills
router.post('/:jobId/apply-suggested-skill', async (req, res) => {
  try {
    const { jobId } = req.params
    const { term } = req.body

    if (!term || !term.trim()) {
      return res.status(400).json({ message: 'Suggested skill term is required' })
    }

    const tempDir = path.join(__dirname, '../../temp', jobId)
    const editsPath = path.join(tempDir, 'edits.json')
    const baseTextPath = path.join(tempDir, 'base_text.json')
    const resumePath = path.join(tempDir, 'Conner_Jordan_Software_Engineer.tuned.tex')

    try {
      await fs.access(tempDir)
    } catch (error) {
      return res.status(404).json({ message: 'Job not found' })
    }

    const [editsContent, baseTextContent, resumeContent] = await Promise.all([
      fs.readFile(editsPath, 'utf-8'),
      fs.readFile(baseTextPath, 'utf-8'),
      fs.readFile(resumePath, 'utf-8')
    ])

    const edits = JSON.parse(editsContent)
    const baseText = JSON.parse(baseTextContent)
    const trimmedTerm = term.trim()

    let skillsInventory = null
    try {
      const inventoryPath = path.join(__dirname, '../../../templates/baseline_skills.json')
      const inventoryContent = await fs.readFile(inventoryPath, 'utf-8')
      skillsInventory = JSON.parse(inventoryContent)
    } catch (error) {
      console.warn('Could not load skills inventory for category matching:', error.message)
    }

    const availableCategories = Object.keys(SKILL_CHUNKS).filter((category) => {
      const chunkId = SKILL_CHUNKS[category]
      return getChunkContent(resumeContent, chunkId)
    })

    if (!availableCategories.length) {
      return res.status(400).json({ message: 'Resume skills sections were not found' })
    }

    const normalizedTerm = normalizeSkill(trimmedTerm)
    const categorySkillsMap = {}
    let existingCategory = null

    for (const category of availableCategories) {
      const chunkId = SKILL_CHUNKS[category]
      const chunk = getChunkContent(resumeContent, chunkId)
      if (!chunk) continue

      const { list } = extractSkillsFromChunk(chunk.content)
      categorySkillsMap[category] = list

      if (list.some((skill) => normalizeSkill(skill) === normalizedTerm)) {
        existingCategory = category
        break
      }
    }

    if (existingCategory) {
      if (edits.suggested_additions) {
        edits.suggested_additions = edits.suggested_additions.filter(
          (suggestion) => normalizeSkill(suggestion.term || '') !== normalizedTerm
        )
        await fs.writeFile(editsPath, JSON.stringify(edits, null, 2), 'utf-8')
      }

      return res.json({
        success: true,
        alreadyExists: true,
        category: existingCategory,
        message: `Skill "${trimmedTerm}" already exists in ${existingCategory}`
      })
    }

    const resolvedCategory = resolveSkillCategory(trimmedTerm, availableCategories, skillsInventory)
    const chunkId = SKILL_CHUNKS[resolvedCategory]
    const chunk = getChunkContent(resumeContent, chunkId)

    if (!chunk) {
      return res.status(400).json({ message: `Skills section "${resolvedCategory}" not found` })
    }

    const baseSkillsText = edits.skills?.[resolvedCategory]?.replace
      || baseText?.resume?.skills?.[resolvedCategory]
      || ''

    const updatedSkillsList = splitSkillList(baseSkillsText)
    if (!updatedSkillsList.some((skill) => normalizeSkill(skill) === normalizedTerm)) {
      updatedSkillsList.push(trimmedTerm)
    }

    const updatedSkillsText = updatedSkillsList.join(', ')

    if (!edits.skills) {
      edits.skills = {}
    }
    edits.skills[resolvedCategory] = { replace: updatedSkillsText }

    if (edits.suggested_additions) {
      edits.suggested_additions = edits.suggested_additions.filter(
        (suggestion) => normalizeSkill(suggestion.term || '') !== normalizedTerm
      )
    }

    await fs.writeFile(editsPath, JSON.stringify(edits, null, 2), 'utf-8')

    const { label } = extractSkillsFromChunk(chunk.content)
    const displayLabel = label || resolvedCategory
    const newChunkContent = `\\textbf{${escapeLatex(displayLabel)}:} ${escapeLatex(updatedSkillsText)}`
    const updatedResumeContent = replaceChunkContent(resumeContent, chunkId, newChunkContent)

    if (!updatedResumeContent) {
      return res.status(500).json({ message: `Failed to update ${resolvedCategory} skills section` })
    }

    await fs.writeFile(resumePath, updatedResumeContent, 'utf-8')

    res.json({
      success: true,
      alreadyExists: false,
      category: resolvedCategory,
      resumeContent: updatedResumeContent,
      updatedSkills: updatedSkillsList,
      message: `Added "${trimmedTerm}" to ${resolvedCategory}`
    })
  } catch (error) {
    console.error('Error applying suggested skill:', error)
    res.status(500).json({ message: error.message })
  }
})

// Get job results including validation status
router.get('/:jobId', async (req, res) => {
  try {
    const { jobId } = req.params
    const tempDir = path.join(__dirname, '../../temp', jobId)
    
    // Check if job directory exists
    try {
      await fs.access(tempDir)
    } catch (error) {
      return res.status(404).json({ message: 'Job not found' })
    }
    
    // Load edits.json to get validation status
    const editsPath = path.join(tempDir, 'edits.json')
    let edits = null
    let validationStatus = null
    
    try {
      const editsContent = await fs.readFile(editsPath, 'utf-8')
      edits = JSON.parse(editsContent)
      
      // Extract validation status from suggested_additions and recalculate based on current baseline
      if (edits.suggested_additions) {
        // Load current baseline skills to recalculate validation
        const baselineSkillsPath = path.join(__dirname, '../../../templates/baseline_skills.json')
        let currentBaselineSkills = null
        
        try {
          const baselineContent = await fs.readFile(baselineSkillsPath, 'utf-8')
          currentBaselineSkills = JSON.parse(baselineContent)
        } catch (error) {
          console.warn('Could not load baseline skills for validation recalculation:', error.message)
        }
        
        // Get all skills that were originally flagged
        const originallyFlaggedSkills = edits.suggested_additions
          .filter(suggestion => suggestion.why && suggestion.why.includes('Skills validation:'))
          .map(suggestion => suggestion.term)
        
        // Recalculate which skills are still flagged based on current baseline
        const flaggedSkills = []
        if (currentBaselineSkills) {
          const confirmedSkills = new Set(currentBaselineSkills.confirmed_skills || [])
          const conversationalSkills = new Set(currentBaselineSkills.conversational_skills || [])
          
          for (const skill of originallyFlaggedSkills) {
            if (!confirmedSkills.has(skill) && !conversationalSkills.has(skill)) {
              flaggedSkills.push({
                skill: skill,
                reason: "Not in confirmed or conversational skills inventory",
                confidence: "low"
              })
            }
          }
        } else {
          // Fallback to original validation if baseline can't be loaded
          flaggedSkills.push(...edits.suggested_additions
            .filter(suggestion => suggestion.why && suggestion.why.includes('Skills validation:'))
            .map(suggestion => {
              const whyMatch = suggestion.why.match(/Skills validation: (.+?) \(confidence: (.+?)\)/)
              return {
                skill: suggestion.term,
                reason: whyMatch ? whyMatch[1] : suggestion.why,
                confidence: whyMatch ? whyMatch[2] : 'low'
              }
            }))
        }
        
        // Calculate confidence level
        let confidence = 'high'
        if (flaggedSkills.length > 2) {
          confidence = 'low'
        } else if (flaggedSkills.length > 0) {
          confidence = 'medium'
        }
        
        validationStatus = {
          confidence,
          flaggedCount: flaggedSkills.length,
          flaggedSkills
        }
      }
    } catch (error) {
      console.warn(`Could not load edits.json for job ${jobId}:`, error.message)
    }
    
    // Load review data if available
    let reviewData = null
    try {
      const reviewPath = path.join(tempDir, 'review.json')
      const reviewContent = await fs.readFile(reviewPath, 'utf-8')
      reviewData = JSON.parse(reviewContent)
    } catch (error) {
      // Review data not available, that's okay
    }
    
    // Load original generation settings from status.json
    let originalSettings = null
    try {
      const statusPath = path.join(tempDir, 'status.json')
      const statusContent = await fs.readFile(statusPath, 'utf-8')
      const statusData = JSON.parse(statusContent)
      originalSettings = statusData.originalSettings || null
    } catch (error) {
      // Original settings not available, that's okay
    }
    
    // Load job description if available
    let jobDescription = null
    try {
      const jobDescPath = path.join(tempDir, 'job-description.txt')
      jobDescription = await fs.readFile(jobDescPath, 'utf-8')
    } catch (error) {
      // Job description not available, that's okay
    }
    
    // Check which files are available
    const files = await fs.readdir(tempDir)
    const availableFiles = {
      resume: files.includes('Conner_Jordan_Software_Engineer.tuned.pdf'),
      coverLetter: files.includes('Conner_Jordan_Cover_Letter.tuned.pdf'),
      resumeTex: files.includes('Conner_Jordan_Software_Engineer.tuned.tex'),
      coverLetterTex: files.includes('Conner_Jordan_Cover_Letter.tuned.tex'),
      edits: files.includes('edits.json'),
      review: files.includes('review.json')
    }
    
    // Process skills changes from edits
    let skillsChanges = null
    if (edits && edits.skills) {
      skillsChanges = {}

      // Load base_text.json to get original skills
      let baseText = null
      try {
        const baseTextPath = path.join(tempDir, 'base_text.json')
        const baseTextContent = await fs.readFile(baseTextPath, 'utf-8')
        baseText = JSON.parse(baseTextContent)
      } catch (error) {
        console.warn('Could not load base_text.json:', error.message)
      }

      for (const [category, skillEdit] of Object.entries(edits.skills)) {
        if (skillEdit.replace) {
          // Get the new skills from the edit
          const newSkills = skillEdit.replace.split(',').map(s => s.trim()).filter(s => s)
          const newSkillsSet = new Set(newSkills)

          // Get the original skills from base text
          let originalSkills = []
          if (baseText && baseText.resume && baseText.resume.skills) {
            const originalSkillsText = baseText.resume.skills[category]
            if (originalSkillsText) {
              originalSkills = originalSkillsText.split(',').map(s => s.trim()).filter(s => s)
            }
          }
          const originalSkillsSet = new Set(originalSkills)

          // Calculate what was actually added vs removed
          const added = newSkills.filter(skill => !originalSkillsSet.has(skill))
          const removed = originalSkills.filter(skill => !newSkillsSet.has(skill))

          // Only include this category if there are actual changes
          if (added.length > 0 || removed.length > 0) {
            skillsChanges[category] = {
              added,
              removed
            }
          }
        }
      }
    }
    
    // Filter suggested additions to exclude validation-related ones (they're shown in validation status)
    let suggestedAdditions = null
    if (edits && edits.suggested_additions) {
      suggestedAdditions = edits.suggested_additions.filter(
        suggestion => !suggestion.why || !suggestion.why.includes('Skills validation:')
      )
    }
    
    const results = {
      jobId,
      availableFiles,
      skillsChanges,
      suggestedAdditions,
      validationStatus,
      reviewData,
      originalSettings,
      jobDescription,
      createdAt: new Date().toISOString(),
      completedAt: new Date().toISOString()
    }
    
    res.json(results)
    
  } catch (error) {
    console.error('Results error:', error)
    res.status(500).json({ message: error.message })
  }
})

export default router
