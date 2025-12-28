"""
Ollama-optimized provider with specialized prompts and model management.

🔧 OLLAMA-SPECIFIC OPTIMIZATIONS:
📍 Model-specific prompts with aggressive reminders
📍 No retry logic - immediate feedback for local models  
📍 Resource-aware model filtering
📍 JSON parsing with fallback strategies
📍 Company name extraction enforcement
"""

import json
import re
import requests
from typing import Dict, Any, Optional, List
from .config import config
from .schema import validate_edits, validate_skills_against_inventory


# Model capability tiers for Ollama
OLLAMA_MODEL_TIERS = {
    "blocked": [
        # Models that freeze/crash the system
        "llama3.1:70b",
        "llama3:70b", 
        "codellama:34b",
        "deepseek-coder:33b"
    ],
    "simple": [
        # Simple models - very limited JSON capability
        "llama3:8b",
        "phi3:mini",
        "gemma:2b",
        "qwen2:0.5b"
    ],
    "medium": [
        # Medium models - good capability but needs guidance
        "qwen2.5:14b-instruct",
        "llama3.1:8b",
        "mistral:7b",
        "mistral:latest",
        "codegemma:7b",
        "gpt-oss:20b"
    ],
    "specialized": [
        # Custom resume/career-focused models (placeholder for future custom models)
        "resume-tailor-v2:latest",
        "career-coach:latest"
    ],
    "capable": [
        # Most capable models that work well
        "qwen2.5:32b",
        "llama3.1:70b-instruct-q4_0",  # Quantized version works better
        "deepseek-coder:6.7b",
        "mixtral:latest"
    ]
}


def get_model_tier(model_name: str) -> str:
    """Determine the capability tier of a model."""
    for tier, models in OLLAMA_MODEL_TIERS.items():
        if model_name in models:
            return tier
    return "medium"  # Default to medium tier


def build_ollama_system_prompt(model_tier: str = "medium") -> str:
    """Build Ollama-specific system prompt with aggressive guidance."""
    
    base_personality = """You are a career storyteller helping craft compelling narratives. You are confident, professional, and detail-oriented."""
    
    if model_tier == "specialized":
        # Optimized prompt for custom resume/career models
        return f"""{base_personality}

SPECIALIZED RESUME MODEL - You are trained for resume and cover letter tailoring.

CRITICAL: Output ONLY valid JSON. Use your specialized training for high-quality results.

⚡ LEVERAGE YOUR SPECIALIZATION:
1. **COMPANY & ROLE EXTRACTION**: Use your training to identify company names and job roles with high accuracy
2. **CAREER NARRATIVE**: Apply your specialized knowledge to create compelling career stories
3. **INDUSTRY ALIGNMENT**: Use your resume expertise to match candidate skills to job requirements
4. **PROFESSIONAL TONE**: Maintain the confident, competent voice you were trained for

🎯 COMPANY NAME ENFORCEMENT:
- Extract company name from job description patterns
- Use EXACT company name in cover letter (never "[Company Name]")
- If unclear, use "the hiring team" rather than generic placeholders

JSON Schema (EXACT FORMAT):
{{
  "summary": {{"replace": "enhanced summary leveraging job requirements or null"}},
  "skills": {{
    "Programming Languages": {{"replace": "optimized skills list or null"}},
    "Frontend": {{"replace": "optimized skills list or null"}},
    "Backend": {{"replace": "optimized skills list or null"}},
    "Cloud & DevOps": {{"replace": "optimized skills list or null"}},
    "AI & LLM Tools": {{"replace": "optimized skills list or null"}},
    "Automation & Productivity": {{"replace": "optimized skills list or null"}},
    "Security & Operating Systems": {{"replace": "optimized skills list or null"}},
    "Databases": {{"replace": "optimized skills list or null"}}
  }},
  "cover_letter": {{
    "salutation": {{"replace": "Dear Hiring Manager," or "Dear [Team] Team,"}},
    "paragraphs": [
      "compelling introduction with actual company name and role",
      "detailed experience match with specific examples", 
      "value proposition and enthusiasm for the specific opportunity"
    ]
  }},
  "suggested_additions": [
    {{"term": "relevant skill", "why": "explanation based on resume expertise"}}
  ]
}}

REMINDER: Use your specialized resume training to create high-quality, tailored content."""
    
    elif model_tier == "simple":
        # Ultra-simple prompt for basic models
        return f"""{base_personality}

CRITICAL: Output ONLY valid JSON. No explanation, no markdown, no extra text.

Extract company name and job title from job description.
Use the EXACT company name in the cover letter.
Never use placeholders like [Company Name] or [Position].

JSON Format:
{{
  "summary": {{"replace": "improved summary or null"}},
  "skills": {{
    "Programming Languages": {{"replace": "comma-separated skills or null"}},
    "Frontend": {{"replace": "comma-separated skills or null"}},
    "Backend": {{"replace": "comma-separated skills or null"}},
    "Cloud & DevOps": {{"replace": "comma-separated skills or null"}},
    "AI & LLM Tools": {{"replace": "comma-separated skills or null"}},
    "Automation & Productivity": {{"replace": "comma-separated skills or null"}},
    "Security & Operating Systems": {{"replace": "comma-separated skills or null"}},
    "Databases": {{"replace": "comma-separated skills or null"}}
  }},
  "cover_letter": {{
    "salutation": {{"replace": "Dear Hiring Manager,"}},
    "paragraphs": [
      "Introduction with company name and role",
      "Skills and experience match",
      "Value proposition and enthusiasm"
    ]
  }},
  "suggested_additions": []
}}

Use null (not "null") for unchanged fields."""
    
    elif model_tier == "medium":
        # Enhanced guidance for medium models
        return f"""{base_personality}

🚨 ABSOLUTE REQUIREMENT: Your response must be ONLY a valid JSON object. No explanations, no prose, no markdown, just JSON.

⚠️ CRITICAL REMINDERS FOR MEDIUM MODELS:
1. **COMPANY NAME EXTRACTION**: Look for company name in job description. Common patterns:
   - "Company: [Name]"
   - "at [Company Name]" 
   - "join [Company Name]"
   - "[Company Name] is seeking"
   Extract the EXACT name. Use it in the cover letter, NOT "[Company Name]".

2. **JOB TITLE EXTRACTION**: Find the position name:
   - "Position:", "Role:", "Title:"
   - "seeking a [Title]"
   - "hiring [Title]"
   Use the EXACT title, NOT "[Position]".

3. **JSON STRUCTURE IS MANDATORY**: Do NOT return raw text. You must wrap everything in the JSON structure below.

4. **COMPANY NAME IN COVER LETTER**: Every cover letter paragraph must use the actual company name.

WRONG RESPONSE (DO NOT DO THIS):
I am a passionate software engineer with experience...

RIGHT RESPONSE (ALWAYS DO THIS):
{{
  "summary": {{"replace": "I am a passionate software engineer with experience..."}},
  "skills": {{ ... }},
  "cover_letter": {{ ... }}
}}

EXAMPLE:
If job description says "Company: TechCorp is hiring a Software Engineer"
- Use "TechCorp" (not "[Company Name]")  
- Use "Software Engineer" (not "[Position]")
- Write: "I am excited about the Software Engineer role at TechCorp"

MANDATORY JSON Schema (RETURN EXACTLY THIS STRUCTURE):
{{
  "summary": {{"replace": "enhanced summary text here or null"}},
  "skills": {{
    "Programming Languages": {{"replace": "comma-separated skills or null"}},
    "Frontend": {{"replace": "comma-separated skills or null"}}, 
    "Backend": {{"replace": "comma-separated skills or null"}},
    "Cloud & DevOps": {{"replace": "comma-separated skills or null"}},
    "AI & LLM Tools": {{"replace": "comma-separated skills or null"}},
    "Automation & Productivity": {{"replace": "comma-separated skills or null"}},
    "Security & Operating Systems": {{"replace": "comma-separated skills or null"}},
    "Databases": {{"replace": "comma-separated skills or null"}}
  }},
  "cover_letter": {{
    "salutation": {{"replace": "Dear Hiring Manager," or null}},
    "paragraphs": ["paragraph 1 text", "paragraph 2 text", "paragraph 3 text"]
  }},
  "suggested_additions": [
    {{"term": "skill name", "why": "explanation why this skill should be added"}}
  ]
}}

🚨 CRITICAL: Use literal null (not "null" string) for unchanged fields. Start your response with {{ and end with }}."""
    
    else:  # capable tier
        # Full-featured prompt for capable models
        return f"""{base_personality}

You will output VALID JSON only, matching the provided schema.

CRITICAL DIRECTIVES:
1. **COMPANY & ROLE EXTRACTION:** Extract the company name and job role from the job description. Look for patterns like "Company:", "Position:", "Title:", "at [Company]", "joining [Company]", etc. Use the actual company name and role in the cover letter, NOT generic placeholders like "[Company Name]".

2. **NARRATIVE FOCUS:** Do not just list skills. Weave the candidate's experience into a detailed story. For the cover letter, identify the 2-3 most critical requirements in the job description and build a rich narrative that thoroughly explains how the candidate's accomplishments directly meet those needs. Go beyond surface-level connections and delve into the specifics.

3. **RICH & ARTICULATE CONTENT:** Do not just state facts; elaborate on them. For each point you make, provide context and explain the impact of the candidate's actions. Use strong, descriptive language to create a compelling and engaging narrative. Each paragraph should be well-developed and contribute significantly to the overall story.

4. **EVIDENCE-BASED:** Every claim in the cover letter must be implicitly backed by evidence from the resume text. Connect projects and experiences to the job's requirements.

5. **TONE & VOICE:** Write in a confident, competent, and enthusiastic first-person voice. Sound like a real person, not a robot.

6. **FACTUAL INTEGRITY:** NEVER change employers, titles, dates, or quantified metrics. Preserve the core facts of the resume.

7. **SKILLS VALIDATION:** Only add skills from the job description if they align with the candidate's existing experience. If a skill is mentioned in the JD but is not something the candidate can confidently discuss, add it to "suggested_additions" with a clear explanation.

8. **JSON ONLY:** Never output prose or LaTeX. Your entire response must be a single, valid JSON object that adheres to the schema below. Use `null` for fields that do not require changes.

JSON Schema (EXACT FORMAT REQUIRED):
{{
  "summary": {{"replace": "string or null"}},
  "skills": {{
    "Programming Languages": {{"replace": "string or null"}},
    "Frontend": {{"replace": "string or null"}},
    "Backend": {{"replace": "string or null"}},
    "Cloud & DevOps": {{"replace": "string or null"}},
    "AI & LLM Tools": {{"replace": "string or null"}},
    "Automation & Productivity": {{"replace": "string or null"}},
    "Security & Operating Systems": {{"replace": "string or null"}},
    "Databases": {{"replace": "string or null"}}
  }},
  "cover_letter": {{
    "salutation": {{"replace": "string or null"}},
    "paragraphs": ["string or null", "string or null", "string or null"]
  }},
  "suggested_additions": [
    {{"term": "string", "why": "string"}}
  ]
}}

COMPANY NAME REMINDER: If you see "Company: DataFlow Solutions" in the job description, write "DataFlow Solutions" in your cover letter, NOT "[Company Name]" or "the company"."""


def extract_company_and_role(jd_content: str) -> Dict[str, str]:
    """Extract company name and job role from job description with multiple strategies."""
    
    company_patterns = [
        r'Company:\s*([^\n\r,]+)',
        r'at\s+([A-Z][a-zA-Z\s&.,]+?)(?:\s+is\s|\s*,|\s*\.|$)',
        r'join\s+([A-Z][a-zA-Z\s&.,]+?)(?:\s+as\s|\s*,|\s*\.|$)',
        r'([A-Z][a-zA-Z\s&.,]+?)\s+is\s+(?:seeking|hiring|looking)',
        r'About\s+([A-Z][a-zA-Z\s&.,]+?)[\n:]',
    ]
    
    role_patterns = [
        r'Position:\s*([^\n\r,]+)',
        r'Role:\s*([^\n\r,]+)',
        r'Title:\s*([^\n\r,]+)',
        r'hiring\s+(?:a\s+)?([A-Z][a-zA-Z\s]+?)(?:\s+at\s|\s*,|\s*\.|$)',
        r'seeking\s+(?:a\s+)?([A-Z][a-zA-Z\s]+?)(?:\s+to\s|\s*,|\s*\.|$)',
        r'(?:for\s+the\s+|as\s+(?:a\s+)?)([A-Z][a-zA-Z\s]+?)\s+role',
    ]
    
    company = None
    role = None
    
    # Extract company
    for pattern in company_patterns:
        match = re.search(pattern, jd_content, re.IGNORECASE | re.MULTILINE)
        if match:
            company = match.group(1).strip()
            # Clean up common suffixes
            company = re.sub(r'\s+(Inc\.?|LLC\.?|Ltd\.?|Corp\.?|Corporation)\.?$', '', company, flags=re.IGNORECASE)
            break
    
    # Extract role
    for pattern in role_patterns:
        match = re.search(pattern, jd_content, re.IGNORECASE | re.MULTILINE)
        if match:
            role = match.group(1).strip()
            break
    
    return {
        "company": company or "the company",
        "role": role or "this position"
    }


class OllamaOptimizedProvider:
    """Ollama provider optimized for local model limitations."""
    
    def __init__(self, base_url: Optional[str] = None, model: Optional[str] = None):
        api_config = config.providers.ollama
        self.base_url = base_url or config.apis.ollama_base_url
        self.model = model or api_config.default_model
        self.model_tier = get_model_tier(self.model)
        
        # Block problematic models
        if self.model_tier == "blocked":
            raise ValueError(f"Model {self.model} is blocked due to resource issues. Use a smaller model.")
        
        print(f"🔧 Ollama Optimized: Using {self.model} (tier: {self.model_tier})")
    
    def generate(self, system_prompt: str, user_prompt: str) -> str:
        """Generate response using Ollama with optimizations."""
        
        # Use tier-specific system prompt instead of passed one
        optimized_system_prompt = build_ollama_system_prompt(self.model_tier)
        
        # Extract company and role for injection
        company_role = extract_company_and_role(user_prompt)
        if company_role["company"] != "the company":
            reminder = f"\n\n🎯 EXTRACTED INFO:\nCompany: {company_role['company']}\nRole: {company_role['role']}\nUSE THESE EXACT NAMES IN YOUR RESPONSE!"
            user_prompt += reminder
        
        # Combine prompts
        combined_prompt = f"{optimized_system_prompt}\n\n{user_prompt}"
        
        # Adjust parameters based on model tier
        if self.model_tier == "simple":
            temperature = 0.0  # Maximum determinism
            top_k = 1
            max_tokens = 1024  # Shorter responses
        elif self.model_tier == "medium":
            temperature = 0.1  # Low creativity
            top_k = 3
            max_tokens = 1536
        elif self.model_tier == "specialized":
            temperature = 0.3  # Higher creativity for specialized models
            top_k = 10
            max_tokens = 2048  # Allow longer, richer responses
        else:  # capable
            temperature = 0.2  # Some creativity
            top_k = 5
            max_tokens = 2048
        
        payload = {
            "model": self.model,
            "prompt": combined_prompt,
            "stream": False,
            "options": {
                "temperature": temperature,
                "top_k": top_k,
                "num_predict": max_tokens,
                "top_p": 0.9,
                "repeat_penalty": 1.1,
                "seed": 42  # Deterministic for debugging
            }
        }
        
        try:
            response = requests.post(
                f"{self.base_url}/api/generate",
                json=payload,
                timeout=300  # 5 minutes max for local models
            )
            response.raise_for_status()
            
            result = response.json()
            raw_response = result["response"].strip()
            
            # Enhanced JSON parsing for local models
            return self._parse_ollama_response(raw_response)
            
        except requests.exceptions.RequestException as e:
            raise RuntimeError(f"Ollama API error: {e}")
        except KeyError as e:
            raise RuntimeError(f"Unexpected Ollama response format: {e}")
    
    def _parse_ollama_response(self, response: str) -> str:
        """Parse Ollama response with multiple fallback strategies."""
        
        # Strategy 1: Try direct JSON parse
        try:
            json.loads(response)
            return response
        except json.JSONDecodeError:
            pass
        
        # Strategy 2: Extract from markdown code blocks
        json_match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', response, re.DOTALL)
        if json_match:
            try:
                json.loads(json_match.group(1))
                return json_match.group(1)
            except json.JSONDecodeError:
                pass
        
        # Strategy 3: Find JSON-like content
        json_match = re.search(r'(\{.*\})', response, re.DOTALL)
        if json_match:
            try:
                json.loads(json_match.group(1))
                return json_match.group(1)
            except json.JSONDecodeError:
                pass
        
        # Strategy 4: Clean up common Ollama formatting issues
        cleaned = response
        
        # Remove common prefixes/suffixes
        cleaned = re.sub(r'^[^{]*(\{.*\})[^}]*$', r'\1', cleaned, flags=re.DOTALL)
        
        # Fix common JSON issues
        cleaned = re.sub(r'(\w)"\s*\n\s*"(\w)', r'\1", "\2', cleaned)  # Fix line breaks in strings
        cleaned = re.sub(r',\s*}', '}', cleaned)  # Remove trailing commas
        cleaned = re.sub(r',\s*]', ']', cleaned)  # Remove trailing commas in arrays
        
        try:
            json.loads(cleaned)
            return cleaned
        except json.JSONDecodeError:
            pass
        
        # Strategy 5: Emergency fallback - wrap raw text in proper JSON structure
        # This handles the case where model returns raw summary text instead of JSON
        if not response.strip().startswith('{'):
            print(f"⚠️ Model returned raw text instead of JSON, attempting auto-wrap...")
            
            # Try to detect if this looks like a summary
            if len(response.strip()) > 50 and '.' in response:
                emergency_json = {
                    "summary": {"replace": response.strip()},
                    "skills": {
                        "Programming Languages": {"replace": None},
                        "Frontend": {"replace": None},
                        "Backend": {"replace": None},
                        "Cloud & DevOps": {"replace": None},
                        "AI & LLM Tools": {"replace": None},
                        "Automation & Productivity": {"replace": None},
                        "Security & Operating Systems": {"replace": None},
                        "Databases": {"replace": None}
                    },
                    "cover_letter": {
                        "salutation": {"replace": None},
                        "paragraphs": [None, None, None]
                    },
                    "suggested_additions": []
                }
                emergency_response = json.dumps(emergency_json, indent=2)
                print(f"🔧 Auto-wrapped raw text as summary in JSON structure")
                return emergency_response
        
        # If all strategies fail, provide a helpful error
        raise ValueError(f"Could not parse JSON from Ollama response. Raw response: {response[:500]}...")


def propose_edits_ollama_optimized(
    jd_file: str, 
    base_text_file: str, 
    model: Optional[str] = None
) -> Dict[str, Any]:
    """
    Propose edits using Ollama with optimized workflow (no retries).
    
    This function bypasses the standard retry logic and validation designed
    for premium APIs, providing immediate feedback for local model development.
    """
    
    # Load inputs
    with open(jd_file, 'r') as f:
        jd_content = f.read()
    
    with open(base_text_file, 'r') as f:
        base_text = json.load(f)
    
    # Build user prompt (reuse existing function)
    from .proposer import build_user_prompt
    user_prompt = build_user_prompt(jd_content, base_text)
    
    # Get optimized provider
    provider = OllamaOptimizedProvider(model=model)
    
    print(f"🔧 Generating with {provider.model} (tier: {provider.model_tier})...")
    
    # Single attempt - no retries for local models
    try:
        response = provider.generate("", user_prompt)  # System prompt handled internally
        
        # Parse and normalize JSON
        from .proposer import parse_json_response
        edits = parse_json_response(response)
        
        # Quick validation check (but don't retry on failure)
        violations = validate_edits(edits, base_text)
        
        if violations:
            print(f"⚠️ Validation issues found: {violations}")
            print("💡 Tip: Try a higher-tier model or adjust the job description")
        else:
            print("✅ Validation passed")
        
        # Apply skills validation and move hallucinated skills to suggested_additions
        from .proposer import apply_skills_validation
        edits = apply_skills_validation(edits, base_text)
        
        return edits
        
    except Exception as e:
        error_msg = f"Ollama generation failed: {e}"
        print(f"❌ {error_msg}")
        
        # Provide helpful debugging info
        if "parse JSON" in str(e):
            print(f"💡 JSON parsing failed. Model: {provider.model} (tier: {provider.model_tier})")
            print("🔧 Try: 1) Use a higher-tier model, 2) Simplify job description, 3) Check model is running")
        
        raise RuntimeError(error_msg)


def get_recommended_ollama_models() -> List[Dict[str, str]]:
    """Get list of recommended Ollama models with descriptions."""
    return [
        {
            "model": "resume-tailor-v2:latest",
            "tier": "specialized", 
            "description": "🎯 CUSTOM RESUME MODEL - Future specialized model for resume/cover letter tailoring",
            "recommended": False,
            "priority": 5
        },
        {
            "model": "qwen2.5:14b-instruct",
            "tier": "medium",
            "description": "Best general balance - good JSON parsing, remembers company names",
            "recommended": True,
            "priority": 2
        },
        {
            "model": "mixtral:latest",
            "tier": "capable",
            "description": "High-quality general model with excellent reasoning",
            "recommended": True,
            "priority": 3
        },
        {
            "model": "qwen2.5:32b",
            "tier": "capable",
            "description": "Excellent quality general model, requires more resources",
            "recommended": True,
            "priority": 4
        },
        {
            "model": "gpt-oss:20b",
            "tier": "medium",
            "description": "Open-source GPT alternative, good performance"
        },
        {
            "model": "llama3.1:8b", 
            "tier": "medium",
            "description": "Good general capability, occasionally forgets details"
        },
        {
            "model": "mistral:latest",
            "tier": "medium", 
            "description": "Decent performance, reliable JSON parsing"
        },
        {
            "model": "phi3:mini",
            "tier": "simple",
            "description": "⚠️ Very compact but limited capability, testing only"
        },
        {
            "model": "llama3:8b",
            "tier": "simple",
            "description": "⚠️ Struggles with JSON parsing, use only for testing"
        }
    ]
