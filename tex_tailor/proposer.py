"""
Module for LLM calls (Ollama, Gemini, OpenAI) to propose edits.

🧠 THIS IS THE MAIN AI BRAIN - PERSONALITY & BEHAVIOR CONTROLLED HERE
📍 To tune model behavior, modify SYSTEM_PROMPT below or load personality files
📍 To adjust creativity, modify temperature/top_k in provider classes (lines 175+)
"""
import os
import json
import requests
import time
from pathlib import Path
from typing import Dict, Any, Optional
from .schema import validate_edits, validate_skills_against_inventory
from .config import config, get_api_config_for_provider


def load_personality_prompt(personality_name: str) -> str:
    """Load personality prompt from file or return default."""
    try:
        # Get the project root directory (where personalities/ folder is located)
        current_file = Path(__file__)
        # tex_tailor/proposer.py -> project root
        project_root = current_file.parent.parent
        personality_file = project_root / \
            "personalities" / f"{personality_name}.txt"

        if personality_file.exists():
            with open(personality_file, 'r', encoding='utf-8') as f:
                personality_prompt = f.read().strip()
            print(f"🎭 Loaded personality: {personality_name}")
            return personality_prompt
        else:
            print(f"⚠️ Personality file not found: {personality_file}")
            return DEFAULT_PERSONALITY_PROMPT
    except Exception as e:
        print(f"❌ Error loading personality {personality_name}: {e}")
        return DEFAULT_PERSONALITY_PROMPT


# Default personality prompt (fallback)
DEFAULT_PERSONALITY_PROMPT = """You are a career storyteller and a savvy colleague. Your goal is to help craft a compelling narrative that makes the candidate's experience come alive.
Your tone is confident, competent, and professional, yet approachable. You communicate clearly and directly, avoiding jargon."""


def build_system_prompt(personality_name: str = 'career_savvy_colleague') -> str:
    """Build complete system prompt with personality and directives."""

    # Get personality-specific instructions
    personality_prompt = load_personality_prompt(personality_name)

    # Build the complete prompt using string concatenation to avoid f-string issues with JSON schema
    system_prompt = personality_prompt + """
You will output VALID JSON only, matching the provided schema.

CRITICAL DIRECTIVES:
1.  **COMPANY & ROLE EXTRACTION:** Extract the company name and job role from the job description. Look for patterns like "Company:", "Position:", "Title:", "at [Company]", "joining [Company]", etc. Use the actual company name and role in the cover letter, NOT generic placeholders like "[Company Name]".
2.  **NARRATIVE FOCUS:** Do not just list skills. Weave the candidate's experience into a story. For the cover letter, identify the 2-3 most critical requirements in the job description and build a narrative explaining how the candidate's accomplishments directly meet those needs.
3.  **EVIDENCE-BASED:** Every claim in the cover letter must be implicitly backed by evidence from the resume text. Connect projects and experiences to the job's requirements.
4.  **TONE & VOICE:** Write in a confident, competent, and enthusiastic first-person voice. Sound like a real person, not a robot.
5.  **FACTUAL INTEGRITY:** NEVER change employers, titles, dates, or quantified metrics. Preserve the core facts of the resume.
6.  **SKILLS VALIDATION:** Only add skills from the job description if they align with the candidate's existing experience. If a skill is mentioned in the JD but is not something the candidate can confidently discuss, add it to "suggested_additions" with a clear explanation.
7.  **JSON ONLY:** Never output prose or LaTeX. Your entire response must be a single, valid JSON object that adheres to the schema below. Use `null` for fields that do not require changes.

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
          "minItems": 3,
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
          "why": {"type": "string"}
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

# 📚 EXAMPLES OF NARRATIVE-DRIVEN EDITS:
-   **Company & Role Extraction:** If the job description says "Company: HealthMetric Analytics" and "Position: Data Scientist", use "HealthMetric Analytics" and "Data Scientist" in the cover letter, NOT "[Company Name]" or generic terms.
-   **Cover Letter Paragraph 1 (Introduction):** Instead of "I am writing to apply for the Software Engineer role," generate something like: "When I saw the opening for the Data Scientist position at HealthMetric Analytics, I was immediately drawn to your innovative work in healthcare analytics. My experience in developing machine learning models aligns perfectly with what you're building."
-   **Cover Letter Paragraph 2 (Body):** Connect a key job requirement to a specific achievement. "The job description emphasizes a need for expertise in healthcare data analysis. In my previous role at [Previous Company], I led the development of predictive models for patient outcomes, resulting in a 25% improvement in treatment recommendations. This experience has prepared me to contribute effectively to HealthMetric Analytics' clinical insights team."
-   **Skills:** Add skills that are both in the JD and supported by the resume content. For example, if the JD requires "Terraform" and the resume mentions "Infrastructure as Code (IaC) for AWS," it's safe to add "Terraform" to the skills list. If the resume has no IaC experience, add "Terraform" to `suggested_additions`.
-   **JSON `null`:** Use `null` (the JSON literal, not the string "null") for any field where the existing text is already excellent and requires no changes. NEVER use the string "null" as a skill term or suggested addition.
"""

    return system_prompt


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

        # Combine system and user prompts for Ollama's generate API
        combined_prompt = f"{system_prompt}\n\n{user_prompt}"

        payload = {
            "model": self.model,
            "prompt": combined_prompt,
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
                f"{self.base_url}/api/generate",
                json=payload,
                timeout=config.providers.ollama.timeout
            )
            response.raise_for_status()

            result = response.json()
            return result["response"].strip()

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


class MistralProvider:
    """Mistral LLM provider - High quality, good performance."""

    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        self.api_key = api_key or os.getenv("MISTRAL_API_KEY")
        self.model = model or config.providers.mistral.default_model

        if not self.api_key:
            raise ValueError(
                "MISTRAL_API_KEY environment variable is required")

    def generate(self, system_prompt: str, user_prompt: str) -> str:
        """Generate response using Mistral."""

        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            # 🎛️ CREATIVITY CONTROLS - Modify these in config.py
            "temperature": config.providers.mistral.temperature,  # 0=deterministic, 1=creative
            "max_tokens": config.providers.mistral.max_tokens,
            "response_format": {"type": "json_object"}
        }

        try:
            url = f"{config.apis.mistral_base_url}/chat/completions"
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}"
            }

            response = requests.post(
                url,
                json=payload,
                headers=headers,
                timeout=config.providers.mistral.timeout
            )
            response.raise_for_status()

            result = response.json()
            return result["choices"][0]["message"]["content"].strip()

        except requests.exceptions.RequestException as e:
            raise RuntimeError(f"Mistral API error: {e}")
        except KeyError as e:
            raise RuntimeError(f"Unexpected Mistral response format: {e}")


class GroqProvider:
    """Groq LLM provider - Very fast inference."""

    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        self.api_key = api_key or os.getenv("GROQ_API_KEY")
        self.model = model or config.providers.groq.default_model

        if not self.api_key:
            raise ValueError("GROQ_API_KEY environment variable is required")

    def generate(self, system_prompt: str, user_prompt: str) -> str:
        """Generate response using Groq."""

        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            # 🎛️ CREATIVITY CONTROLS - Modify these in config.py
            "temperature": config.providers.groq.temperature,  # 0=deterministic, 1=creative
            "max_tokens": config.providers.groq.max_tokens,
            "response_format": {"type": "json_object"}
        }

        try:
            url = f"{config.apis.groq_base_url}/chat/completions"
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}"
            }

            response = requests.post(
                url,
                json=payload,
                headers=headers,
                timeout=config.providers.groq.timeout
            )
            response.raise_for_status()

            result = response.json()
            return result["choices"][0]["message"]["content"].strip()

        except requests.exceptions.RequestException as e:
            raise RuntimeError(f"Groq API error: {e}")
        except KeyError as e:
            raise RuntimeError(f"Unexpected Groq response format: {e}")


def get_provider(provider_name: str, model: Optional[str] = None):
    """Get LLM provider instance."""
    if provider_name.lower() == "ollama":
        return OllamaProvider(model=model)
    elif provider_name.lower() == "gemini":
        return GeminiProvider(model=model)
    elif provider_name.lower() == "openai":
        return OpenAIProvider(model=model)
    elif provider_name.lower() == "mistral":
        return MistralProvider(model=model)
    elif provider_name.lower() == "groq":
        return GroqProvider(model=model)
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
                  model: Optional[str] = None, personality: str = 'career_savvy_colleague',
                  max_retries: int = 2) -> Dict[str, Any]:
    """Propose edits using LLM."""

    # Load inputs
    with open(jd_file, 'r', encoding='utf-8') as f:
        jd_content = f.read()

    with open(base_text_file, 'r', encoding='utf-8') as f:
        base_text = json.load(f)

    # Build prompts with personality
    system_prompt = build_system_prompt(personality)
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
                    # Exponential backoff: wait 2^attempt seconds (2, 4, 8...)
                    backoff_time = 2 ** attempt
                    print(
                        f"Retrying in {backoff_time} seconds to avoid rate limits...")
                    time.sleep(backoff_time)
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
                # Exponential backoff: wait 2^attempt seconds (2, 4, 8...)
                backoff_time = 2 ** attempt
                print(
                    f"Retrying in {backoff_time} seconds to avoid rate limits...")
                time.sleep(backoff_time)
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

        # Skip validation if new_skills is null or "null"
        if new_skills is None or new_skills == "null" or new_skills.strip() == "":
            continue

        # Validate skills against inventory
        validation_result = validate_skills_against_inventory(
            original_skills, new_skills)

        # Update the skills with validated version
        validated_edits["skills"][skill_category]["replace"] = validation_result["validated_skills"]

        # Add flagged skills to suggested_additions
        for flagged_skill in validation_result["flagged_skills"]:
            # Skip if the skill is null or "null"
            if flagged_skill["skill"] and flagged_skill["skill"] != "null":
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
                           provider: str, model: Optional[str] = None,
                           personality: str = 'career_savvy_colleague', quiet: bool = False) -> None:
    """Complete flow: propose edits and save to file."""

    edits = propose_edits(jd_file, base_text_file,
                          provider, model, personality)
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
