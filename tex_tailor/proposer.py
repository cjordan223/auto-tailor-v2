"""
Module for LLM calls (Ollama, Gemini, OpenAI) to propose edits.

🧠 THIS IS THE MAIN AI BRAIN - PERSONALITY & BEHAVIOR CONTROLLED HERE
📍 To tune model behavior, modify SYSTEM_PROMPT below (lines 15-95)
📍 To adjust creativity, modify temperature/top_k in provider classes (lines 175+)
"""
import os
import json
import requests
from typing import Dict, Any, Optional
from .schema import validate_edits
from .config import config, get_api_config_for_provider


# 🎯 MAIN AI PROMPT - MODIFY HERE TO CHANGE PERSONALITY & BEHAVIOR
# This controls how the AI behaves, what it prioritizes, and its "personality"
SYSTEM_PROMPT = """You are a deterministic résumé/cover-letter tailor.
Never output LaTeX or prose. Output VALID JSON only matching the provided schema.
Preserve factual integrity (employers, titles, dates, metrics). Optimize skills and content to align with job description requirements.
If a needed JD term is not present in the base text and cannot be inferred, list it under "suggested_additions" only.

CRITICAL CONSTRAINTS:
# 🎛️ TUNE THESE TO CHANGE AI BEHAVIOR - More restrictive = safer, less restrictive = more creative
- Summary: Create a COMPELLING, DETAILED summary that showcases specific expertise and achievements. Be verbose and impactful - avoid bland generic statements. Highlight concrete technical capabilities, years of experience, quantified achievements, and unique value proposition. Write with confidence and substance.
- Skills: PREFER ADDITIONS over deletions. Add job-relevant technologies while preserving core competencies.
- Cover letter: Write with a NATURAL, CONVERSATIONAL tone that flows like genuine human communication. Avoid corporate jargon and stiff formal language. Be authentic, engaging, and personable while remaining professional. Use varied sentence structures and natural transitions between ideas.
- Suggested additions: "why" field should be concise and under 200 characters.
- Use null for unchanged fields when no improvement is needed.
- Focus on strategic job-relevant modifications that improve keyword alignment.
- PRESERVE FACTUAL INTEGRITY: Never change employers, titles, dates, or quantified metrics.

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
        "salutation": {"type": "object", "properties": {"replace": {"type": ["string", "null"]}}, "required": ["replace"], "additionalProperties": false},
        "paragraphs": {
          "type": "array",
          "items": {"type": ["string", "null"]},
          "minItems": 4,
          "maxItems": 4
        }
      },
      "required": ["salutation", "paragraphs"],
      "additionalProperties": false
    },
    "suggested_additions": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "term": {"type": "string"},
          "why": {"type": "string", "maxLength": 200}
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

# 📚 EXAMPLES SECTION - ADD MORE EXAMPLES HERE TO TEACH AI NEW BEHAVIORS
EXAMPLES OF VALID EDITS:

- Summary: Transform bland summaries into compelling narratives:
  AVOID: "I am a software engineer with experience in Python."
  PREFER: "I am a passionate Software Engineer with over three years of hands-on experience building scalable backend systems using Python, FastAPI, and PostgreSQL. I've successfully architected microservices handling 10M+ daily requests, reduced system latency by 40% through database optimization, and mentored junior developers while maintaining 99.9% uptime across production environments."

- Skills: ADD job-relevant technologies while preserving existing core skills. Only remove if truly irrelevant.
  IMPORTANT: For skills, only provide the content after the colon, NOT the category name.
  Example: For "Frontend", return "React, Vue.js, Angular" NOT "Frontend: React, Vue.js, Angular".
  PREFERRED approach: "Python, Java, C++" → "Python, Java, C++, Go, Rust" (ADD Go and Rust, keep existing).
  AVOID: "Python, Java, C++" → "Go, Rust" (removes valuable existing skills).

- Cover letter salutation: Replace [Company Name] with the actual company name from the job description.

- Cover letter tone: Write naturally and conversationally:
  AVOID: "I am writing to express my interest in the Software Engineer position at your esteemed organization."
  PREFER: "I'm excited to apply for the Software Engineer role at [Company]. Your work in [specific area] really caught my attention, especially [specific detail from JD]."
  
  AVOID: "I possess the requisite qualifications for this role."
  PREFER: "I think I'd be a great fit for this role because of my background in [specific relevant area]."

- Cover letter flow: Use natural transitions and varied sentence structures:
  AVOID: Stiff, formal corporate speak
  PREFER: Authentic, engaging language that sounds like a real conversation

- Make strategic edits that improve job relevance - use null only when no improvements are needed.
- PRESERVE foundational skills unless they conflict with job requirements.
"""


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
        "Cover Letter Salutation:",
        "<<<SALUTATION",
        cover_letter.get("salutation", ""),
        "<<<SALUTATION_END",
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
    """Ollama LLM provider - Free local models."""

    def __init__(self, base_url: Optional[str] = None, model: Optional[str] = None):
        api_config = get_api_config_for_provider("ollama")
        self.base_url = base_url or api_config["base_url"]
        self.model = model or config.providers.ollama.default_model

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
                # 🎛️ CREATIVITY CONTROLS - Modify these in config.py
                "temperature": config.providers.ollama.temperature,  # 0=deterministic, 1=creative
                "top_k": config.providers.ollama.top_k,              # Lower=focused, higher=diverse
                "num_predict": config.providers.ollama.max_tokens
            }
        }

        try:
            response = requests.post(
                f"{self.base_url}/api/chat",
                json=payload,
                timeout=config.providers.ollama.timeout
            )
            response.raise_for_status()

            result = response.json()
            return result["message"]["content"].strip()

        except requests.exceptions.RequestException as e:
            raise RuntimeError(f"Ollama API error: {e}")
        except KeyError as e:
            raise RuntimeError(f"Unexpected Ollama response format: {e}")


class GeminiProvider:
    """Gemini LLM provider - Best balance of speed, quality, and cost (RECOMMENDED)."""

    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        self.model = model or config.providers.gemini.default_model

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
                # 🎛️ CREATIVITY CONTROLS - Modify these in config.py
                "temperature": config.providers.gemini.temperature,   # 0=deterministic, 1=creative
                "topK": config.providers.gemini.top_k,               # Lower=focused, higher=diverse
                "maxOutputTokens": config.providers.gemini.max_tokens,
                "responseMimeType": "application/json"
            }
        }

        try:
            url = f"{config.apis.gemini_base_url}/{self.model}:generateContent"
            headers = {"Content-Type": "application/json"}
            params = {"key": self.api_key}

            response = requests.post(
                url,
                json=payload,
                headers=headers,
                params=params,
                timeout=config.providers.gemini.timeout
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


class OpenAIProvider:
    """OpenAI LLM provider - Highest quality, most expensive."""

    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.model = model or config.providers.openai.default_model

        if not self.api_key:
            raise ValueError("OPENAI_API_KEY environment variable is required")

    def generate(self, system_prompt: str, user_prompt: str) -> str:
        """Generate response using OpenAI."""

        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            # 🎛️ CREATIVITY CONTROLS - Modify these in config.py
            "temperature": config.providers.openai.temperature,  # 0=deterministic, 1=creative
            "max_tokens": config.providers.openai.max_tokens,
            "response_format": {"type": "json_object"}
        }

        try:
            url = f"{config.apis.openai_base_url}/chat/completions"
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}"
            }

            response = requests.post(
                url,
                json=payload,
                headers=headers,
                timeout=config.providers.openai.timeout
            )
            response.raise_for_status()

            result = response.json()
            return result["choices"][0]["message"]["content"].strip()

        except requests.exceptions.RequestException as e:
            raise RuntimeError(f"OpenAI API error: {e}")
        except KeyError as e:
            raise RuntimeError(f"Unexpected OpenAI response format: {e}")


def get_provider(provider_name: str, model: Optional[str] = None):
    """Get LLM provider instance."""
    if provider_name.lower() == "ollama":
        return OllamaProvider(model=model)
    elif provider_name.lower() == "gemini":
        return GeminiProvider(model=model)
    elif provider_name.lower() == "openai":
        return OpenAIProvider(model=model)
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
    json_match = re.search(
        r'```(?:json)?\s*(\{.*?\})\s*```', response, re.DOTALL)
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
    last_error = None
    for attempt in range(max_retries + 1):
        try:
            print(
                f"Generating edits (attempt {attempt + 1}/{max_retries + 1})...")

            current_prompt = user_prompt
            if attempt > 0 and last_error:
                # Add retry instruction with details of the last error
                current_prompt += f"\n\nYou failed the last attempt. Review the validation errors: {last_error}. Pay close attention to the replacement limits and field lengths. Respond with valid JSON matching the schema."

            response = llm.generate(system_prompt, current_prompt)

            # Parse JSON
            edits = parse_json_response(response)

            # Validate against schema and business rules
            violations = validate_edits(edits, base_text)

            if violations:
                last_error = f"Validation failed: {violations}"
                if attempt < max_retries:
                    print(
                        f"Validation failed (attempt {attempt + 1}): {violations}")
                    continue
                else:
                    raise ValueError(
                        f"Validation failed after {max_retries + 1} attempts: {violations}")

            return edits

        except (json.JSONDecodeError, ValueError) as e:
            last_error = f"Error: {e}"
            if attempt < max_retries:
                print(f"Error on attempt {attempt + 1}: {e}")
                continue
            else:
                raise RuntimeError(
                    f"Failed to generate valid edits after {max_retries + 1} attempts: {e}")

    raise RuntimeError("Unexpected error in propose_edits")


def save_edits(edits: Dict[str, Any], output_file: str, quiet: bool = False) -> None:
    """Save edits to JSON file."""
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(edits, f, indent=2, ensure_ascii=False)

    if not quiet:
        print(f"Saved edits to: {output_file}")


def propose_and_save_edits(jd_file: str, base_text_file: str, output_file: str,
                           provider: str, model: Optional[str] = None, quiet: bool = False) -> None:
    """Complete flow: propose edits and save to file."""

    edits = propose_edits(jd_file, base_text_file, provider, model)
    save_edits(edits, output_file, quiet=quiet)

    if not quiet:
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
            summary_lines.append(
                f"✓ {cover_edits} cover letter paragraph edits proposed")

        suggestions = len(edits.get("suggested_additions", []))
        if suggestions:
            summary_lines.append(f"✓ {suggestions} suggested additions")

        if summary_lines:
            print("\nEdit Summary:")
            for line in summary_lines:
                print(f"  {line}")
        else:
            print("\nNo edits proposed.")
