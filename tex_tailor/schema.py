"""
Module for JSON schema validation and edit limits enforcement.
"""
import re
import json
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
                "paragraphs": {
                    "type": "array",
                    "items": {"type": ["string", "null"]},
                    "minItems": 4,
                    "maxItems": 4
                }
            },
            "required": ["paragraphs"],
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


# LaTeX commands and characters that should be rejected
FORBIDDEN_LATEX_PATTERNS = [
    r'\\',          # Backslash (LaTeX commands)
    r'\{',          # Opening brace
    r'\}',          # Closing brace
    r'%',           # Comment character
    r'_',           # Subscript
    r'\^',          # Superscript
    r'~',           # Non-breaking space
    r'\\begin',     # Environment start
    r'\\section',   # Section command
    r'\\textbf',    # Bold command
    r'\\item',      # List item
    r'\\\\',        # Line break
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
            diff_ratio = len(orig_words.symmetric_difference(new_words)) / max(len(orig_words), len(new_words), 1)
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
    
    # Check sentence limit (≤ 5 sentence-level edits)
    sentence_changes = count_replacements(original, new)
    if sentence_changes > 5:
        violations.append(f"Too many sentence-level changes: {sentence_changes} (max: 5)")
    
    return violations


def validate_skills_edits(original: str, new: str) -> List[str]:
    """Validate skills edits against limits."""
    violations = []
    
    if not new:
        return violations
    
    # Check for forbidden LaTeX
    latex_violations = check_forbidden_latex(new)
    violations.extend(latex_violations)
    
    # Check replacement limit (≤ 4 replacements)
    replacements = count_replacements(original, new)
    if replacements > 4:
        violations.append(f"Too many replacements: {replacements} (max: 4)")
    
    # Must be comma-separated list (no newlines allowed)
    if '\n' in new or not re.match(r'^[^,]+(,\s*[^,]+)*$', new.strip()):
        violations.append("Must be comma-separated list format")
    
    return violations


def validate_cover_letter_edits(original_paragraphs: List[str], new_paragraphs: List[str]) -> List[str]:
    """Validate cover letter edits against limits."""
    violations = []
    
    if len(new_paragraphs) != 4:
        violations.append(f"Must have exactly 4 paragraphs, got {len(new_paragraphs)}")
        return violations
    
    edited_count = 0
    
    for i, (original, new) in enumerate(zip(original_paragraphs, new_paragraphs)):
        if new and new != original:
            edited_count += 1
            
            # Check for forbidden LaTeX
            latex_violations = check_forbidden_latex(new)
            for violation in latex_violations:
                violations.append(f"Paragraph {i+1}: {violation}")
    
    # Check edit limit (≤ 1 edit per paragraph, ≤ 4 paragraphs edited total)
    if edited_count > 4:
        violations.append(f"Too many paragraphs edited: {edited_count} (max: 4)")
    
    return violations


def validate_suggested_additions(suggestions: List[Dict[str, str]]) -> List[str]:
    """Validate suggested additions."""
    violations = []
    
    for i, suggestion in enumerate(suggestions):
        if not suggestion.get("term"):
            violations.append(f"Suggestion {i+1}: Missing term")
        
        why = suggestion.get("why", "")
        if len(why) > 30:
            violations.append(f"Suggestion {i+1}: 'why' too long ({len(why)} chars, max: 30)")
    
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
        summary_violations = validate_summary_edits(original_summary, new_summary)
        violations.extend([f"Summary: {v}" for v in summary_violations])
    
    # Validate skills
    if "skills" in edits:
        base_skills = base_text.get("resume", {}).get("skills", {})
        for skill_name, skill_edit in edits["skills"].items():
            if skill_edit.get("replace"):
                original = base_skills.get(skill_name, "")
                new = skill_edit["replace"]
                skill_violations = validate_skills_edits(original, new)
                violations.extend([f"Skills.{skill_name}: {v}" for v in skill_violations])
    
    # Validate cover letter
    if "cover_letter" in edits and "paragraphs" in edits["cover_letter"]:
        original_paragraphs = base_text.get("cover_letter", {}).get("paragraphs", [])
        new_paragraphs = edits["cover_letter"]["paragraphs"]
        cover_violations = validate_cover_letter_edits(original_paragraphs, new_paragraphs)
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
        error_msg = "Validation failed:\n" + "\n".join(f"- {v}" for v in violations)
        raise ValidationError(error_msg)
    
    return edits


def clean_edits_json(edits: Dict[str, Any]) -> Dict[str, Any]:
    """Clean edits JSON by removing null values and empty strings."""
    cleaned = json.loads(json.dumps(edits))  # Deep copy
    
    # Remove null summary
    if "summary" in cleaned and cleaned["summary"].get("replace") is None:
        cleaned["summary"]["replace"] = None
    
    # Clean skills
    if "skills" in cleaned:
        for skill_name in list(cleaned["skills"].keys()):
            if cleaned["skills"][skill_name].get("replace") is None:
                cleaned["skills"][skill_name]["replace"] = None
    
    # Clean cover letter paragraphs
    if "cover_letter" in cleaned and "paragraphs" in cleaned["cover_letter"]:
        for i, paragraph in enumerate(cleaned["cover_letter"]["paragraphs"]):
            if paragraph is None:
                cleaned["cover_letter"]["paragraphs"][i] = None
    
    return cleaned