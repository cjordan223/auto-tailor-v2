"""
Ollama-specific validation with relaxed rules for local model limitations.

🎯 OLLAMA VALIDATION STRATEGY:
📍 More lenient parsing - accept partial JSON
📍 Automatic fix common local model issues
📍 Graceful degradation rather than hard failures
📍 Company name validation with smart fallbacks
"""

import json
import re
from typing import Dict, Any, List, Tuple
from .schema import validate_edits as standard_validate_edits
from .config import config


def fix_ollama_json_issues(response_text: str) -> str:
    """Fix common JSON issues that Ollama models produce."""
    
    text = response_text.strip()
    
    # Remove markdown formatting
    text = re.sub(r'^```(?:json)?\s*', '', text)
    text = re.sub(r'\s*```$', '', text)
    
    # Fix common string escaping issues
    text = re.sub(r'(?<!\\)"(?=\w)', r'\\"', text)  # Fix unescaped quotes in strings
    
    # Fix trailing commas
    text = re.sub(r',(\s*[}\]])', r'\1', text)
    
    # Fix missing commas
    text = re.sub(r'(["\]}])(\s+")([^:]*":)', r'\1,\2\3', text)
    
    # Fix null handling (convert "null" strings to null literals where appropriate)
    text = re.sub(r':\s*"null"(?=\s*[,}])', ': null', text)
    
    # Ensure proper JSON structure for missing fields
    if '"summary"' not in text:
        text = text.replace('{', '{"summary":{"replace":null},', 1)
    
    if '"skills"' not in text:
        # Add minimal skills structure
        skills_template = '''
        "skills": {
            "Programming Languages": {"replace": null},
            "Frontend": {"replace": null},
            "Backend": {"replace": null},
            "Cloud & DevOps": {"replace": null},
            "AI & LLM Tools": {"replace": null},
            "Automation & Productivity": {"replace": null},
            "Security & Operating Systems": {"replace": null},
            "Databases": {"replace": null}
        },'''
        text = text.replace('"cover_letter"', skills_template + '"cover_letter"')
    
    return text


def validate_company_name_extraction(edits: Dict[str, Any], jd_content: str) -> List[str]:
    """Validate that company names were properly extracted and used."""
    
    issues = []
    
    # Extract company name from JD
    company_patterns = [
        r'Company:\s*([^\n\r,]+)',
        r'at\s+([A-Z][a-zA-Z\s&.,]+?)(?:\s+is\s|\s*,|\s*\.|$)',
        r'join\s+([A-Z][a-zA-Z\s&.,]+?)(?:\s+as\s|\s*,|\s*\.|$)',
        r'([A-Z][a-zA-Z\s&.,]+?)\s+is\s+(?:seeking|hiring|looking)',
    ]
    
    extracted_company = None
    for pattern in company_patterns:
        match = re.search(pattern, jd_content, re.IGNORECASE | re.MULTILINE)
        if match:
            extracted_company = match.group(1).strip()
            break
    
    if not extracted_company:
        return issues  # Can't validate if we can't extract
    
    # Check cover letter paragraphs for placeholder usage
    cover_letter = edits.get("cover_letter", {})
    paragraphs = cover_letter.get("paragraphs", [])
    
    for i, paragraph in enumerate(paragraphs):
        if paragraph and isinstance(paragraph, str):
            # Check for common placeholder patterns
            if re.search(r'\[Company\s*Name\]|\[Position\]|\[Role\]', paragraph, re.IGNORECASE):
                issues.append(f"Paragraph {i+1}: Contains placeholders like [Company Name] - should use '{extracted_company}'")
            
            # Check for generic references
            if re.search(r'\bthe\s+company\b|\byour\s+organization\b', paragraph, re.IGNORECASE):
                if extracted_company.lower() not in paragraph.lower():
                    issues.append(f"Paragraph {i+1}: Uses generic 'the company' instead of '{extracted_company}'")
    
    return issues


def auto_fix_placeholders(edits: Dict[str, Any], jd_content: str) -> Dict[str, Any]:
    """Automatically fix placeholder issues in Ollama responses."""
    
    # Extract company and role
    company_patterns = [
        r'Company:\s*([^\n\r,]+)',
        r'at\s+([A-Z][a-zA-Z\s&.,]+?)(?:\s+is\s|\s*,|\s*\.|$)',
        r'join\s+([A-Z][a-zA-Z\s&.,]+?)(?:\s+as\s|\s*,|\s*\.|$)',
        r'([A-Z][a-zA-Z\s&.,]+?)\s+is\s+(?:seeking|hiring|looking)',
    ]
    
    role_patterns = [
        r'Position:\s*([^\n\r,]+)',
        r'Role:\s*([^\n\r,]+)',
        r'Title:\s*([^\n\r,]+)',
        r'hiring\s+(?:a\s+)?([A-Z][a-zA-Z\s]+?)(?:\s+at\s|\s*,|\s*\.|$)',
        r'seeking\s+(?:a\s+)?([A-Z][a-zA-Z\s]+?)(?:\s+to\s|\s*,|\s*\.|$)',
    ]
    
    company = None
    role = None
    
    for pattern in company_patterns:
        match = re.search(pattern, jd_content, re.IGNORECASE | re.MULTILINE)
        if match:
            company = match.group(1).strip()
            break
    
    for pattern in role_patterns:
        match = re.search(pattern, jd_content, re.IGNORECASE | re.MULTILINE)
        if match:
            role = match.group(1).strip()
            break
    
    if not company and not role:
        return edits
    
    # Fix placeholders in cover letter
    fixed_edits = json.loads(json.dumps(edits))  # Deep copy
    
    cover_letter = fixed_edits.get("cover_letter", {})
    paragraphs = cover_letter.get("paragraphs", [])
    
    for i, paragraph in enumerate(paragraphs):
        if paragraph and isinstance(paragraph, str):
            fixed_paragraph = paragraph
            
            # Replace placeholders
            if company:
                fixed_paragraph = re.sub(r'\[Company\s*Name\]', company, fixed_paragraph, flags=re.IGNORECASE)
                fixed_paragraph = re.sub(r'\bthe\s+company\b', company, fixed_paragraph, flags=re.IGNORECASE)
                fixed_paragraph = re.sub(r'\byour\s+organization\b', company, fixed_paragraph, flags=re.IGNORECASE)
            
            if role:
                fixed_paragraph = re.sub(r'\[Position\]|\[Role\]', role, fixed_paragraph, flags=re.IGNORECASE)
                fixed_paragraph = re.sub(r'\bthe\s+position\b', f'the {role} position', fixed_paragraph, flags=re.IGNORECASE)
            
            paragraphs[i] = fixed_paragraph
    
    return fixed_edits


def validate_ollama_response(response_text: str, jd_content: str, base_text: Dict[str, Any]) -> Tuple[Dict[str, Any], List[str]]:
    """
    Validate and fix Ollama response with specialized handling.
    
    Returns:
        Tuple of (fixed_edits, warning_list)
    """
    
    warnings = []
    
    try:
        # Step 1: Fix common JSON issues
        fixed_json_text = fix_ollama_json_issues(response_text)
        
        # Step 2: Parse JSON
        try:
            edits = json.loads(fixed_json_text)
        except json.JSONDecodeError as e:
            # Try to extract partial JSON
            json_match = re.search(r'(\{.*\})', fixed_json_text, re.DOTALL)
            if json_match:
                try:
                    edits = json.loads(json_match.group(1))
                except json.JSONDecodeError:
                    raise ValueError(f"Could not parse JSON from Ollama response: {e}")
            else:
                raise ValueError(f"No JSON found in Ollama response: {e}")
        
        # Step 3: Auto-fix placeholders
        original_edits = json.loads(json.dumps(edits))  # Keep original for comparison
        edits = auto_fix_placeholders(edits, jd_content)
        
        if edits != original_edits:
            warnings.append("Auto-fixed placeholder issues (e.g., [Company Name] → actual company name)")
        
        # Step 4: Validate company name usage
        company_issues = validate_company_name_extraction(edits, jd_content)
        if company_issues:
            warnings.extend(company_issues)
        
        # Step 5: Use more lenient validation
        validation_issues = validate_ollama_edits_lenient(edits, base_text)
        if validation_issues:
            warnings.extend([f"Validation: {issue}" for issue in validation_issues])
        
        return edits, warnings
        
    except Exception as e:
        raise ValueError(f"Ollama response validation failed: {e}")


def validate_ollama_edits_lenient(edits: Dict[str, Any], base_text: Dict[str, Any]) -> List[str]:
    """
    Lenient validation specifically for Ollama models.
    
    This accepts responses that would fail standard validation but are
    good enough for local model capabilities.
    """
    
    warnings = []
    
    # Use standard validation but collect warnings instead of failing
    try:
        standard_violations = standard_validate_edits(edits, base_text)
        
        # Convert some violations to warnings for Ollama
        for violation in standard_violations:
            if "too long" in violation.lower():
                # Allow longer content for Ollama - just warn
                warnings.append(f"Length warning: {violation}")
            elif "forbidden pattern" in violation.lower():
                # More strict about LaTeX patterns
                warnings.append(violation)
            else:
                # Other issues are warnings for Ollama
                warnings.append(violation)
                
    except Exception as e:
        warnings.append(f"Validation error: {e}")
    
    # Ollama-specific validations
    
    # Check for essential structure
    if "cover_letter" not in edits:
        warnings.append("Missing cover_letter section")
    elif "paragraphs" not in edits.get("cover_letter", {}):
        warnings.append("Missing paragraphs in cover_letter")
    
    if "skills" not in edits:
        warnings.append("Missing skills section")
    
    if "summary" not in edits:
        warnings.append("Missing summary section")
    
    # Check cover letter has content
    paragraphs = edits.get("cover_letter", {}).get("paragraphs", [])
    if not paragraphs or all(not p for p in paragraphs):
        warnings.append("Cover letter has no content")
    
    # Check for reasonable length (more lenient than standard)
    total_chars = sum(len(str(p)) for p in paragraphs if p)
    if total_chars < 200:
        warnings.append("Cover letter seems too short (less than 200 characters)")
    elif total_chars > 5000:
        warnings.append("Cover letter seems too long (over 5000 characters)")
    
    return warnings


def get_ollama_validation_summary(edits: Dict[str, Any], warnings: List[str]) -> str:
    """Generate a summary of the Ollama validation results."""
    
    summary_lines = []
    
    # Count what was generated
    if edits.get("summary", {}).get("replace"):
        summary_lines.append("✓ Summary updated")
    
    skills_count = sum(1 for skill in edits.get("skills", {}).values() 
                      if skill and skill.get("replace"))
    if skills_count:
        summary_lines.append(f"✓ {skills_count} skill sections updated")
    
    paragraphs = edits.get("cover_letter", {}).get("paragraphs", [])
    paragraph_count = sum(1 for p in paragraphs if p)
    if paragraph_count:
        summary_lines.append(f"✓ {paragraph_count} cover letter paragraphs")
    
    suggestions = len(edits.get("suggested_additions", []))
    if suggestions:
        summary_lines.append(f"✓ {suggestions} suggested additions")
    
    # Add warnings summary
    if warnings:
        summary_lines.append(f"⚠️ {len(warnings)} warnings (see above)")
    else:
        summary_lines.append("✅ No validation warnings")
    
    return "\n".join(f"  {line}" for line in summary_lines)