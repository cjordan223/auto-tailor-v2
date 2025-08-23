"""
Module for JSON schema validation and edit limits enforcement.

✅ VALIDATION CONTROLS - Modify functions here to change what AI can/cannot do
📍 FORBIDDEN_LATEX_PATTERNS - Controls what text patterns are blocked
📍 validate_*_edits functions - Controls validation strictness
"""
import re
import json
import os
from typing import Dict, Any, List, Optional
from jsonschema import validate, ValidationError


# JSON schema for edits
EDITS_SCHEMA = {
    "type": "object",
    "properties": {
        "summary": {
            "type": "object",
            "properties": {
                "replace": {"type": ["string", "null"]}
            },
            "required": ["replace"],
            "additionalProperties": False
        },
        "skills": {
            "type": "object",
            "properties": {
                "Programming Languages": {"type": "object", "properties": {"replace": {"type": ["string", "null"]}}, "required": ["replace"], "additionalProperties": False},
                "Frontend": {"type": "object", "properties": {"replace": {"type": ["string", "null"]}}, "required": ["replace"], "additionalProperties": False},
                "Backend": {"type": "object", "properties": {"replace": {"type": ["string", "null"]}}, "required": ["replace"], "additionalProperties": False},
                "Cloud & DevOps": {"type": "object", "properties": {"replace": {"type": ["string", "null"]}}, "required": ["replace"], "additionalProperties": False},
                "AI & LLM Tools": {"type": "object", "properties": {"replace": {"type": ["string", "null"]}}, "required": ["replace"], "additionalProperties": False},
                "Automation & Productivity": {"type": "object", "properties": {"replace": {"type": ["string", "null"]}}, "required": ["replace"], "additionalProperties": False},
                "Security & Operating Systems": {"type": "object", "properties": {"replace": {"type": ["string", "null"]}}, "required": ["replace"], "additionalProperties": False},
                "Databases": {"type": "object", "properties": {"replace": {"type": ["string", "null"]}}, "required": ["replace"], "additionalProperties": False}
            },
            "additionalProperties": False
        },
        "cover_letter": {
            "type": "object",
            "properties": {
                "salutation": {"type": "object", "properties": {"replace": {"type": ["string", "null"]}}, "required": ["replace"], "additionalProperties": False},
                "paragraphs": {
                    "type": "array",
                    "items": {"type": ["string", "null"]},
                    "minItems": 4,
                    "maxItems": 4
                }
            },
            "required": ["salutation", "paragraphs"],
            "additionalProperties": False
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
                "additionalProperties": False
            }
        }
    },
    "required": ["summary", "skills", "cover_letter"],
    "additionalProperties": False
}


# 🚫 FORBIDDEN PATTERNS - Controls what text the AI cannot output
# Only reject actual LaTeX commands that would break the document structure
# Previously blocked: %, _, \, {, } - removed these for more natural content
FORBIDDEN_LATEX_PATTERNS = [
    r'\\begin\{',       # Environment start - would break LaTeX structure
    r'\\end\{',         # Environment end - would break LaTeX structure
    r'\\section',       # Section command - would break document hierarchy
    r'\\documentclass',  # Document class - would break document structure
    r'\\usepackage',    # Package import - would break document structure
]


class ValidationError(Exception):
    """Custom validation error."""
    pass


def validate_json_schema(edits: Dict[str, Any]) -> None:
    """Validate the edits JSON against the schema."""
    try:
        validate(instance=edits, schema=EDITS_SCHEMA)
    except ValidationError as e:
        raise ValidationError(f"JSON schema validation failed: {e.message}")


def check_forbidden_latex(text: str) -> List[str]:
    """Check if text contains forbidden LaTeX commands or characters."""
    violations = []

    if not text:
        return violations

    for pattern in FORBIDDEN_LATEX_PATTERNS:
        if re.search(pattern, text):
            violations.append(f"Contains forbidden pattern: {pattern}")

    return violations


def count_sentences(text: str) -> int:
    """Count sentences in text."""
    if not text:
        return 0

    # Simple sentence counting - split by periods, exclamation marks, question marks
    sentences = re.split(r'[.!?]+', text.strip())
    # Filter out empty strings
    sentences = [s.strip() for s in sentences if s.strip()]
    return len(sentences)


def count_replacements(original: str, new: str) -> int:
    """Count the number of logical replacements between two texts."""
    if not original or not new:
        return 0 if original == new else 1

    # For skills - count comma-separated changes
    if ',' in original and ',' in new:
        orig_items = [item.strip() for item in original.split(',')]
        new_items = [item.strip() for item in new.split(',')]

        # Count items that changed
        orig_set = set(orig_items)
        new_set = set(new_items)

        # Count items that were replaced (removed and added)
        removed = orig_set - new_set
        added = new_set - orig_set

        return max(len(removed), len(added))

    # For other text - count sentence-level changes
    orig_sentences = [s.strip() for s in original.split('.') if s.strip()]
    new_sentences = [s.strip() for s in new.split('.') if s.strip()]

    # Simple comparison - if significantly different, count as 1-2 changes
    if len(orig_sentences) != len(new_sentences):
        return min(2, abs(len(orig_sentences) - len(new_sentences)) + 1)

    changes = 0
    for orig, new in zip(orig_sentences, new_sentences):
        if orig != new:
            # Count significant word differences
            orig_words = set(orig.lower().split())
            new_words = set(new.lower().split())
            diff_ratio = len(orig_words.symmetric_difference(
                new_words)) / max(len(orig_words), len(new_words), 1)
            if diff_ratio > 0.3:  # More than 30% word difference
                changes += 1

    return changes


def validate_summary_edits(original: str, new: str) -> List[str]:
    """Validate summary edits against limits."""
    violations = []

    if not new:
        return violations

    # Check for forbidden LaTeX
    latex_violations = check_forbidden_latex(new)
    violations.extend(latex_violations)

    # 🎛️ CONSTRAINT REMOVED: Previously had sentence count limits
    # Allow reasonable changes for job relevance - focus on quality over arbitrary limits
    # To re-enable limits, uncomment and modify the validation logic below:
    # sentence_changes = count_replacements(original, new)
    # if sentence_changes > LIMIT: violations.append(f"Too many changes: {sentence_changes}")

    return violations


def load_skills_inventory() -> Dict[str, Any]:
    """Load the personal skills inventory from baseline_skills.json."""
    skills_file = "baseline_skills.json"

    # Try to find the skills file in the current directory or parent directories
    current_dir = os.getcwd()
    skills_path = None

    # Check current directory
    if os.path.exists(os.path.join(current_dir, skills_file)):
        skills_path = os.path.join(current_dir, skills_file)
    # Check parent directory
    elif os.path.exists(os.path.join(os.path.dirname(current_dir), skills_file)):
        skills_path = os.path.join(os.path.dirname(current_dir), skills_file)
    # Check workspace root
    else:
        # Try to find it in the workspace
        for root, dirs, files in os.walk(current_dir):
            if skills_file in files:
                skills_path = os.path.join(root, skills_file)
                break

    if not skills_path:
        print(
            f"Warning: {skills_file} not found. Skills validation will be disabled.")
        return {}

    try:
        with open(skills_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(
            f"Warning: Could not load {skills_file}: {e}. Skills validation will be disabled.")
        return {}


def validate_skills_edits(original: str, new: str) -> List[str]:
    """Validate skills edits against limits and personal skills inventory."""
    violations = []

    if not new:
        return violations

    # Check for forbidden LaTeX
    latex_violations = check_forbidden_latex(new)
    violations.extend(latex_violations)

    # Must be comma-separated list (no newlines allowed)
    if '\n' in new or not re.match(r'^[^,]+(,\s*[^,]+)*$', new.strip()):
        violations.append("Must be comma-separated list format")

    # Load skills inventory for validation
    skills_inventory = load_skills_inventory()
    if not skills_inventory:
        return violations  # Skip validation if inventory not available

    # Extract skills from the new text
    new_skills = [skill.strip() for skill in new.split(',') if skill.strip()]

    # Check for excluded skills
    excluded_skills = skills_inventory.get("exclude_skills", [])
    for skill in new_skills:
        if skill in excluded_skills:
            violations.append(
                f"Skill '{skill}' is in exclude list and cannot be added")

    return violations


def validate_skills_against_inventory(original_skills: str, new_skills: str) -> Dict[str, Any]:
    """
    Validate proposed skills against personal skills inventory.
    Returns validation results with flagged skills for suggested_additions.
    """
    skills_inventory = load_skills_inventory()
    if not skills_inventory:
        return {"validated_skills": new_skills, "flagged_skills": [], "confidence": "low"}

    confirmed_skills = set(skills_inventory.get("confirmed_skills", []))
    conversational_skills = set(
        skills_inventory.get("conversational_skills", []))
    excluded_skills = set(skills_inventory.get("exclude_skills", []))

    # Extract skills from both original and new
    original_skill_list = [skill.strip()
                           for skill in original_skills.split(',') if skill.strip()]
    new_skill_list = [skill.strip()
                      for skill in new_skills.split(',') if skill.strip()]

    # Find skills that were added
    original_set = set(original_skill_list)
    new_set = set(new_skill_list)
    added_skills = new_set - original_set

    # Categorize added skills
    validated_skills = []
    flagged_skills = []

    for skill in new_skill_list:
        if skill in excluded_skills:
            # Remove excluded skills entirely
            continue
        elif skill in confirmed_skills:
            validated_skills.append(skill)
        elif skill in conversational_skills:
            validated_skills.append(skill)
        elif skill in added_skills:
            # This is a new skill that's not in our inventory
            flagged_skills.append({
                "skill": skill,
                "reason": "Not in confirmed or conversational skills inventory",
                "confidence": "low"
            })
        else:
            # Keep existing skills even if not in inventory
            validated_skills.append(skill)

    # Determine confidence level
    if not flagged_skills:
        confidence = "high"
    elif len(flagged_skills) <= 2:
        confidence = "medium"
    else:
        confidence = "low"

    return {
        "validated_skills": ", ".join(validated_skills),
        "flagged_skills": flagged_skills,
        "confidence": confidence
    }


def validate_cover_letter_edits(original_paragraphs: List[str], new_paragraphs: List[str]) -> List[str]:
    """Validate cover letter edits against limits."""
    violations = []

    if len(new_paragraphs) != 4:
        violations.append(
            f"Must have exactly 4 paragraphs, got {len(new_paragraphs)}")
        return violations

    edited_count = 0

    for i, (original, new) in enumerate(zip(original_paragraphs, new_paragraphs)):
        if new and new != original:
            edited_count += 1

            # Check for forbidden LaTeX
            latex_violations = check_forbidden_latex(new)
            for violation in latex_violations:
                violations.append(f"Paragraph {i+1}: {violation}")

    # 🎛️ CONSTRAINT REMOVED: Previously had paragraph count limits
    # Allow editing all paragraphs as needed for job relevance - focus on quality over arbitrary limits
    # To re-enable limits, uncomment and modify the validation logic below:
    # if edited_count > LIMIT: violations.append(f"Too many paragraphs edited: {edited_count}")

    return violations


def truncate_why_explanation(text: str, max_length: int = 80) -> str:
    """Truncate 'why' explanation to fit within character limit while preserving meaning."""
    if len(text) <= max_length:
        return text

    # Try to truncate at word boundaries
    words = text.split()
    truncated = ""

    for word in words:
        if len(truncated + " " + word) <= max_length - 3:  # Leave room for "..."
            truncated += (" " + word) if truncated else word
        else:
            break

    # Add ellipsis if we truncated
    if truncated != text:
        truncated = truncated.rstrip() + "..."

    # If still too long, truncate at character level
    if len(truncated) > max_length:
        truncated = text[:max_length-3] + "..."

    return truncated


def validate_suggested_additions(suggestions: List[Dict[str, str]]) -> List[str]:
    """Validate suggested additions, with automatic truncation of long explanations."""
    violations = []

    for i, suggestion in enumerate(suggestions):
        if not suggestion.get("term"):
            violations.append(f"Suggestion {i+1}: Missing term")

        why = suggestion.get("why", "")
        if len(why) > 200:
            # Instead of rejecting, truncate the explanation
            original_why = why
            suggestion["why"] = truncate_why_explanation(why, 200)
            print(
                f"Warning: Truncated 'why' explanation for '{suggestion['term']}' from {len(original_why)} to {len(suggestion['why'])} characters")

    return violations


def validate_edits(edits: Dict[str, Any], base_text: Dict[str, Any]) -> List[str]:
    """Validate all edits against schema and business rules."""
    violations = []

    # First validate JSON schema
    try:
        validate_json_schema(edits)
    except ValidationError as e:
        violations.append(str(e))
        return violations  # Don't continue if schema is invalid

    # Validate summary
    if "summary" in edits and "replace" in edits["summary"] and edits["summary"]["replace"]:
        original_summary = base_text.get("resume", {}).get("summary", "")
        new_summary = edits["summary"]["replace"]
        summary_violations = validate_summary_edits(
            original_summary, new_summary)
        violations.extend([f"Summary: {v}" for v in summary_violations])

    # Validate skills
    if "skills" in edits:
        base_skills = base_text.get("resume", {}).get("skills", {})
        for skill_name, skill_edit in edits["skills"].items():
            if skill_edit.get("replace"):
                original = base_skills.get(skill_name, "")
                new = skill_edit["replace"]
                skill_violations = validate_skills_edits(original, new)
                violations.extend(
                    [f"Skills.{skill_name}: {v}" for v in skill_violations])

    # Validate cover letter
    if "cover_letter" in edits and "paragraphs" in edits["cover_letter"]:
        original_paragraphs = base_text.get(
            "cover_letter", {}).get("paragraphs", [])
        new_paragraphs = edits["cover_letter"]["paragraphs"]
        cover_violations = validate_cover_letter_edits(
            original_paragraphs, new_paragraphs)
        violations.extend([f"Cover letter: {v}" for v in cover_violations])

    # Validate suggested additions
    if "suggested_additions" in edits:
        suggestions = edits["suggested_additions"]
        suggestion_violations = validate_suggested_additions(suggestions)
        violations.extend([f"Suggestions: {v}" for v in suggestion_violations])

    return violations


def load_and_validate_edits(edits_file: str, base_text_file: str) -> Dict[str, Any]:
    """Load and validate edits file against base text."""

    # Load files
    with open(edits_file, 'r', encoding='utf-8') as f:
        edits = json.load(f)

    with open(base_text_file, 'r', encoding='utf-8') as f:
        base_text = json.load(f)

    # Validate
    violations = validate_edits(edits, base_text)

    if violations:
        error_msg = "Validation failed:\n" + \
            "\n".join(f"- {v}" for v in violations)
        raise ValidationError(error_msg)

    return edits


def clean_edits_json(edits: Dict[str, Any]) -> Dict[str, Any]:
    """Clean edits JSON by replacing null values and "null" strings with empty strings."""
    cleaned = json.loads(json.dumps(edits))  # Deep copy

    # Replace null summary with empty string
    if "summary" in cleaned and cleaned["summary"].get("replace") is None:
        cleaned["summary"]["replace"] = ""

    # Clean skills - replace null values and "null" strings with empty strings
    if "skills" in cleaned:
        for skill_name in list(cleaned["skills"].keys()):
            replace_value = cleaned["skills"][skill_name].get("replace")
            if replace_value is None or replace_value == "null":
                cleaned["skills"][skill_name]["replace"] = ""

    # Clean cover letter salutation
    if "cover_letter" in cleaned and "salutation" in cleaned["cover_letter"]:
        replace_value = cleaned["cover_letter"]["salutation"].get("replace")
        if replace_value is None or replace_value == "null":
            cleaned["cover_letter"]["salutation"]["replace"] = ""

    # Clean cover letter paragraphs
    if "cover_letter" in cleaned and "paragraphs" in cleaned["cover_letter"]:
        for i, paragraph in enumerate(cleaned["cover_letter"]["paragraphs"]):
            if paragraph is None or paragraph == "null":
                cleaned["cover_letter"]["paragraphs"][i] = ""

    return cleaned
