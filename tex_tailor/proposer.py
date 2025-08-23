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
from .schema import validate_edits, validate_skills_against_inventory
from .config import config, get_api_config_for_provider


# 🎯 MAIN AI PROMPT - MODIFY HERE TO CHANGE PERSONALITY & BEHAVIOR
# This controls how the AI behaves, what it prioritizes, and its "personality"
SYSTEM_PROMPT = """You are a deterministic résumé/cover-letter tailor.
Never output LaTeX or prose. Output VALID JSON only matching the provided schema.
Preserve factual integrity (employers, titles, dates, metrics). Optimize skills and content to align with job description requirements.
If a needed JD term is not present in the base text and cannot be inferred, list it under "suggested_additions" only.

CRITICAL CONSTRAINTS:
# 🎛️ TUNE THESE TO CHANGE AI BEHAVIOR - More restrictive = safer, less restrictive = more creative
- Summary: Preserve personal voice while optimizing for job relevance. Focus on key terminology alignment.
- Skills: ONLY add skills from job description if they align with existing confirmed or conversational skills. NEVER add skills in exclude_skills list or unrelated technical domains. Use suggested_additions for skills outside your confirmed expertise.
- Cover letter: Tailor content to job requirements while maintaining authentic tone and factual accuracy.
- Suggested additions: "why" field should be concise and under 200 characters.
- Use null (not the string "null") for unchanged fields when no improvement is needed.
- Focus on strategic job-relevant modifications that improve keyword alignment.
- PRESERVE FACTUAL INTEGRITY: Never change employers, titles, dates, or quantified metrics.
- SKILLS VALIDATION: Only add skills you can confidently discuss. If uncertain about a skill, add it to suggested_additions instead of directly to skills sections.

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
- Summary: Modify to highlight relevant experience for the target role.
- Skills: ONLY add skills you can confidently discuss. If a skill from the job description is not in your confirmed expertise, add it to suggested_additions instead.
  IMPORTANT: For skills, only provide the content after the colon, NOT the category name.
  Example: For "Frontend", return "React, Vue.js, Angular" NOT "Frontend: React, Vue.js, Angular".
  PREFERRED approach: "Python, Java, C++" → "Python, Java, C++, Go" (ADD Go if you can discuss it, keep existing).
  AVOID: "Python, Java, C++" → "Go, Rust" (removes valuable existing skills).
  SKILLS VALIDATION EXAMPLES:
  - If JD mentions "SCADA" but you don't have SCADA experience → add to suggested_additions with reason "Not in confirmed skills"
  - If JD mentions "React" and you have React experience → add to Frontend skills
  - If JD mentions "CAD software" but you don't have CAD experience → add to suggested_additions with reason "Not in confirmed skills"
- Cover letter salutation: Replace [Company Name] with the actual company name from the job description.
- Cover letter paragraphs: Tailor content to emphasize job-relevant experience and match company needs.
- Make strategic edits that improve job relevance - use null (not "null") only when no improvements are needed.
- PRESERVE foundational skills unless they conflict with job requirements.
- IMPORTANT: Return actual null values, not the string "null". Example: "replace": null is correct, "replace": "null" is wrong.
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
                # Lower=focused, higher=diverse
                "top_k": config.providers.ollama.top_k,
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
                # Lower=focused, higher=diverse
                "topK": config.providers.gemini.top_k,
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

            # Apply skills validation and move hallucinated skills to suggested_additions
            edits = apply_skills_validation(edits, base_text)

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


def apply_skills_validation(edits: Dict[str, Any], base_text: Dict[str, Any]) -> Dict[str, Any]:
    """
    Apply skills validation and move hallucinated skills to suggested_additions.
    This prevents AI from adding skills that aren't in the personal skills inventory.
    """
    if "skills" not in edits:
        return edits

    base_skills = base_text.get("resume", {}).get("skills", {})
    validated_edits = edits.copy()

    # Initialize suggested_additions if not present
    if "suggested_additions" not in validated_edits:
        validated_edits["suggested_additions"] = []

    # Process each skills section
    for skill_category, skill_edit in edits["skills"].items():
        if not skill_edit.get("replace"):
            continue

        original_skills = base_skills.get(skill_category, "")
        new_skills = skill_edit["replace"]

        # Validate skills against inventory
        validation_result = validate_skills_against_inventory(
            original_skills, new_skills)

        # Update the skills with validated version
        validated_edits["skills"][skill_category]["replace"] = validation_result["validated_skills"]

        # Add flagged skills to suggested_additions
        for flagged_skill in validation_result["flagged_skills"]:
            validated_edits["suggested_additions"].append({
                "term": flagged_skill["skill"],
                "why": f"Skills validation: {flagged_skill['reason']} (confidence: {flagged_skill['confidence']})"
            })

    return validated_edits


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
