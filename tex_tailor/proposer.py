"""
Module for LLM calls (Ollama and Gemini) to propose edits.
"""
import os
import json
import requests
from typing import Dict, Any, Optional
from .schema import validate_edits


# LLM prompt templates
SYSTEM_PROMPT = """You are a deterministic résumé/cover-letter tailor.
Never output LaTeX or prose. Output VALID JSON only matching the provided schema.
Preserve factual integrity (employers, titles, dates, metrics). Prefer minimal substitutions for keyword alignment with the JD.
If a needed JD term is not present in the base text and cannot be inferred, list it under "suggested_additions" only.
Keep "why" explanations very brief (max 30 chars).

CRITICAL CONSTRAINTS:
- Summary: Maximum 2 sentence-level changes only
- Skills: Maximum 2 word replacements per category 
- Cover letter: Edit maximum 2 paragraphs only
- Suggested additions: "why" field maximum 30 characters
- Use null for unchanged fields
- Make minimal, targeted edits that preserve original meaning

REQUIRED JSON SCHEMA:
{
  "type": "object",
  "properties": {
    "summary": {
      "type": "object",
      "properties": {"replace": {"type": ["string", "null"]}},
      "required": ["replace"],
      "additionalProperties": false
    },
    "skills": {
      "type": "object",
      "properties": {
        "Programming Languages": {"type": "object", "properties": {"replace": {"type": ["string", "null"]}}, "required": ["replace"], "additionalProperties": false},
        "Frontend": {"type": "object", "properties": {"replace": {"type": ["string", "null"]}}, "required": ["replace"], "additionalProperties": false},
        "Backend": {"type": "object", "properties": {"replace": {"type": ["string", "null"]}}, "required": ["replace"], "additionalProperties": false},
        "Cloud & DevOps": {"type": "object", "properties": {"replace": {"type": ["string", "null"]}}, "required": ["replace"], "additionalProperties": false},
        "AI & LLM Tools": {"type": "object", "properties": {"replace": {"type": ["string", "null"]}}, "required": ["replace"], "additionalProperties": false},
        "Automation & Productivity": {"type": "object", "properties": {"replace": {"type": ["string", "null"]}}, "required": ["replace"], "additionalProperties": false},
        "Security & Operating Systems": {"type": "object", "properties": {"replace": {"type": ["string", "null"]}}, "required": ["replace"], "additionalProperties": false},
        "Databases": {"type": "object", "properties": {"replace": {"type": ["string", "null"]}}, "required": ["replace"], "additionalProperties": false}
      },
      "additionalProperties": false
    },
    "cover_letter": {
      "type": "object",
      "properties": {
        "paragraphs": {
          "type": "array",
          "items": {"type": ["string", "null"]},
          "minItems": 4,
          "maxItems": 4
        }
      },
      "required": ["paragraphs"],
      "additionalProperties": false
    },
    "suggested_additions": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "term": {"type": "string"},
          "why": {"type": "string", "maxLength": 30}
        },
        "required": ["term", "why"],
        "additionalProperties": false
      }
    }
  },
  "required": ["summary", "skills", "cover_letter"],
  "additionalProperties": false
}

YOU MUST include all required fields: summary, skills, cover_letter.

EXAMPLES OF VALID EDITS:
- Summary: Change 1-2 key terms only, keep structure intact
- Skills: Replace 1-2 words per category (e.g., "React" → "React/Vue", "AWS" → "AWS/GCP")
  IMPORTANT: For skills, only provide the content after the colon, NOT the category name
  Example: For "Frontend", return "React, Vue.js, Angular" NOT "Frontend: React, Vue.js, Angular"  
- Cover letter: Edit only 2 paragraphs maximum, use null for unchanged paragraphs
- Be conservative - when in doubt, use null to indicate no change"""


def build_user_prompt(jd_content: str, base_text: Dict[str, Any]) -> str:
    """Build the user prompt from JD content and base text."""
    
    resume = base_text.get("resume", {})
    cover_letter = base_text.get("cover_letter", {})
    
    prompt_parts = [
        "[JD]",
        "<<<JD_START",
        jd_content.strip(),
        "<<<JD_END",
        "",
        "[BASE TEXT]",
        "Summary:",
        "<<<SUMMARY_START",
        resume.get("summary", ""),
        "<<<SUMMARY_END",
        "",
        "Skills:"
    ]
    
    # Add skills
    skills = resume.get("skills", {})
    for skill_name in [
        "Programming Languages", "Frontend", "Backend", "Cloud & DevOps",
        "AI & LLM Tools", "Automation & Productivity", 
        "Security & Operating Systems", "Databases"
    ]:
        skill_content = skills.get(skill_name, "")
        prompt_parts.append(f"{skill_name}: {skill_content}")
    
    prompt_parts.extend([
        "",
        "Cover Letter Paragraphs:"
    ])
    
    # Add cover letter paragraphs
    paragraphs = cover_letter.get("paragraphs", [])
    for i, paragraph in enumerate(paragraphs, 1):
        prompt_parts.extend([
            f"<<<CL_P{i}",
            paragraph,
            f"<<<CL_P{i}_END"
        ])
    
    prompt_parts.extend([
        "",
        "Return JSON only."
    ])
    
    return "\n".join(prompt_parts)


class OllamaProvider:
    """Ollama LLM provider."""
    
    def __init__(self, base_url: Optional[str] = None, model: Optional[str] = None):
        self.base_url = base_url or os.getenv("OLLAMA_BASE_URL", "http://127.0.0.1:11434")
        self.model = model or os.getenv("OLLAMA_MODEL", "qwen2.5:14b-instruct")
    
    def generate(self, system_prompt: str, user_prompt: str) -> str:
        """Generate response using Ollama."""
        
        # Use chat API format
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            "stream": False,
            "options": {
                "temperature": 0,
                "top_k": 1,
                "num_predict": 2048
            }
        }
        
        try:
            response = requests.post(
                f"{self.base_url}/api/chat",
                json=payload,
                timeout=120
            )
            response.raise_for_status()
            
            result = response.json()
            return result["message"]["content"].strip()
            
        except requests.exceptions.RequestException as e:
            raise RuntimeError(f"Ollama API error: {e}")
        except KeyError as e:
            raise RuntimeError(f"Unexpected Ollama response format: {e}")


class GeminiProvider:
    """Gemini LLM provider."""
    
    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        self.model = model or os.getenv("GEMINI_MODEL", "gemini-1.5-pro")
        
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY environment variable is required")
    
    def generate(self, system_prompt: str, user_prompt: str) -> str:
        """Generate response using Gemini."""
        
        # Combine system and user prompts for Gemini
        combined_prompt = f"{system_prompt}\n\n{user_prompt}"
        
        payload = {
            "contents": [
                {
                    "parts": [
                        {"text": combined_prompt}
                    ]
                }
            ],
            "generationConfig": {
                "temperature": 0,
                "topK": 1,
                "maxOutputTokens": 2048,
                "responseMimeType": "application/json"
            }
        }
        
        try:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent"
            headers = {"Content-Type": "application/json"}
            params = {"key": self.api_key}
            
            response = requests.post(
                url,
                json=payload,
                headers=headers,
                params=params,
                timeout=120
            )
            response.raise_for_status()
            
            result = response.json()
            
            # Extract text from Gemini response
            candidates = result.get("candidates", [])
            if not candidates:
                raise RuntimeError("No candidates in Gemini response")
            
            content = candidates[0].get("content", {})
            parts = content.get("parts", [])
            if not parts:
                raise RuntimeError("No parts in Gemini response")
            
            return parts[0].get("text", "").strip()
            
        except requests.exceptions.RequestException as e:
            raise RuntimeError(f"Gemini API error: {e}")
        except KeyError as e:
            raise RuntimeError(f"Unexpected Gemini response format: {e}")


def get_provider(provider_name: str, model: Optional[str] = None):
    """Get LLM provider instance."""
    if provider_name.lower() == "ollama":
        return OllamaProvider(model=model)
    elif provider_name.lower() == "gemini":
        return GeminiProvider(model=model)
    else:
        raise ValueError(f"Unknown provider: {provider_name}")


def parse_json_response(response: str) -> Dict[str, Any]:
    """Parse JSON from LLM response, handling potential formatting issues."""
    
    # Try to parse as-is first
    try:
        return json.loads(response)
    except json.JSONDecodeError:
        pass
    
    # Try to extract JSON from markdown code blocks
    import re
    json_match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', response, re.DOTALL)
    if json_match:
        try:
            return json.loads(json_match.group(1))
        except json.JSONDecodeError:
            pass
    
    # Try to find JSON-like content
    json_match = re.search(r'(\{.*\})', response, re.DOTALL)
    if json_match:
        try:
            return json.loads(json_match.group(1))
        except json.JSONDecodeError:
            pass
    
    raise ValueError(f"Could not parse JSON from response: {response}")


def propose_edits(jd_file: str, base_text_file: str, provider: str, 
                 model: Optional[str] = None, max_retries: int = 2) -> Dict[str, Any]:
    """Propose edits using LLM."""
    
    # Load inputs
    with open(jd_file, 'r', encoding='utf-8') as f:
        jd_content = f.read()
    
    with open(base_text_file, 'r', encoding='utf-8') as f:
        base_text = json.load(f)
    
    # Build prompts
    system_prompt = SYSTEM_PROMPT
    user_prompt = build_user_prompt(jd_content, base_text)
    
    # Get provider
    llm = get_provider(provider, model)
    
    # Generate with retries
    for attempt in range(max_retries + 1):
        try:
            print(f"Generating edits (attempt {attempt + 1}/{max_retries + 1})...")
            
            if attempt > 0:
                # Add retry instruction
                user_prompt += "\n\nRespond with valid JSON matching schema. No extra keys."
            
            response = llm.generate(system_prompt, user_prompt)
            
            # Parse JSON
            edits = parse_json_response(response)
            
            # Validate against schema and business rules
            violations = validate_edits(edits, base_text)
            
            if violations:
                if attempt < max_retries:
                    print(f"Validation failed (attempt {attempt + 1}): {violations}")
                    continue
                else:
                    raise ValueError(f"Validation failed after {max_retries + 1} attempts: {violations}")
            
            return edits
            
        except (json.JSONDecodeError, ValueError) as e:
            if attempt < max_retries:
                print(f"Error on attempt {attempt + 1}: {e}")
                continue
            else:
                raise RuntimeError(f"Failed to generate valid edits after {max_retries + 1} attempts: {e}")
    
    raise RuntimeError("Unexpected error in propose_edits")


def save_edits(edits: Dict[str, Any], output_file: str) -> None:
    """Save edits to JSON file."""
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(edits, f, indent=2, ensure_ascii=False)
    
    print(f"Saved edits to: {output_file}")


def propose_and_save_edits(jd_file: str, base_text_file: str, output_file: str,
                          provider: str, model: Optional[str] = None) -> None:
    """Complete flow: propose edits and save to file."""
    
    edits = propose_edits(jd_file, base_text_file, provider, model)
    save_edits(edits, output_file)
    
    # Print summary
    summary_lines = []
    
    if edits.get("summary", {}).get("replace"):
        summary_lines.append("✓ Summary edit proposed")
    
    skills_edits = sum(1 for skill in edits.get("skills", {}).values() 
                      if skill.get("replace"))
    if skills_edits:
        summary_lines.append(f"✓ {skills_edits} skills edits proposed")
    
    cover_edits = sum(1 for p in edits.get("cover_letter", {}).get("paragraphs", []) 
                     if p is not None)
    if cover_edits:
        summary_lines.append(f"✓ {cover_edits} cover letter paragraph edits proposed")
    
    suggestions = len(edits.get("suggested_additions", []))
    if suggestions:
        summary_lines.append(f"✓ {suggestions} suggested additions")
    
    if summary_lines:
        print("\nEdit Summary:")
        for line in summary_lines:
            print(f"  {line}")
    else:
        print("\nNo edits proposed.")