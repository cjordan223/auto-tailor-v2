"""
Module for LaTeX escaping and chunk replacement.
"""
import re
import json
from typing import Dict, Any, Tuple


# LaTeX escape mappings
LATEX_ESCAPE_MAP = {
    '\\': r'\textbackslash{}',
    '{': r'\{',
    '}': r'\}',
    '#': r'\#',
    '$': r'\$',
    '%': r'\%',
    '&': r'\&',
    '_': r'\_',
    '~': r'\textasciitilde{}',
    '^': r'\textasciicircum{}'
}


def latex_escape(text: str) -> str:
    """Escape special LaTeX characters in text."""
    if not text:
        return text
    
    escaped = text
    for char, replacement in LATEX_ESCAPE_MAP.items():
        escaped = escaped.replace(char, replacement)
    
    return escaped


def find_chunk_boundaries(content: str, chunk_id: str) -> Tuple[int, int]:
    """Find the start and end positions of a chunk in content."""
    
    start_pattern = rf'^% === LLM:CHUNK START {re.escape(chunk_id)} ===\s*\n'
    end_pattern = rf'\n% === LLM:CHUNK END {re.escape(chunk_id)} ===$'
    
    start_match = re.search(start_pattern, content, re.MULTILINE)
    if not start_match:
        raise ValueError(f"Could not find start marker for chunk: {chunk_id}")
    
    end_match = re.search(end_pattern, content[start_match.end():], re.MULTILINE)
    if not end_match:
        raise ValueError(f"Could not find end marker for chunk: {chunk_id}")
    
    content_start = start_match.end()
    content_end = start_match.end() + end_match.start()
    
    return content_start, content_end


def replace_chunk_content(content: str, chunk_id: str, new_content: str) -> str:
    """Replace the content of a specific chunk."""
    
    try:
        content_start, content_end = find_chunk_boundaries(content, chunk_id)
    except ValueError as e:
        print(f"Warning: {e}")
        return content
    
    # Escape the new content for LaTeX
    escaped_content = latex_escape(new_content)
    
    # Replace the content, preserving whitespace structure
    original_content = content[content_start:content_end]
    
    # Try to preserve indentation from original
    lines = original_content.split('\n')
    if lines:
        # Get indentation from first non-empty line
        first_line = next((line for line in lines if line.strip()), '')
        indent = ''
        for char in first_line:
            if char in ' \t':
                indent += char
            else:
                break
        
        # Apply same indentation to new content
        new_lines = escaped_content.split('\n')
        if len(new_lines) > 1:
            indented_lines = [new_lines[0]] + [indent + line if line.strip() else line 
                                             for line in new_lines[1:]]
            escaped_content = '\n'.join(indented_lines)
    
    return content[:content_start] + escaped_content + content[content_end:]


def replace_chunk_content_raw(content: str, chunk_id: str, new_content: str) -> str:
    """Replace the content of a specific chunk without LaTeX escaping."""
    
    try:
        content_start, content_end = find_chunk_boundaries(content, chunk_id)
    except ValueError as e:
        print(f"Warning: {e}")
        return content
    
    # Use content directly without escaping (for pre-formatted LaTeX like skills)
    return content[:content_start] + new_content + content[content_end:]


def apply_resume_edits(content: str, edits: Dict[str, Any]) -> str:
    """Apply résumé edits to content."""
    
    modified_content = content
    
    # Apply summary edit
    if "summary" in edits and "replace" in edits["summary"]:
        new_summary = edits["summary"]["replace"]
        if new_summary:
            modified_content = replace_chunk_content(modified_content, "RESUME.SUMMARY", new_summary)
    
    # Apply skills edits
    if "skills" in edits:
        skill_mapping = {
            'Programming Languages': 'SKILLS.Programming Languages',
            'Frontend': 'SKILLS.Frontend', 
            'Backend': 'SKILLS.Backend',
            'Cloud & DevOps': 'SKILLS.Cloud and DevOps',
            'AI & LLM Tools': 'SKILLS.AI and LLM Tools',
            'Automation & Productivity': 'SKILLS.Automation and Productivity',
            'Security & Operating Systems': 'SKILLS.Security and Operating Systems',
            'Databases': 'SKILLS.Databases'
        }
        
        for skill_name, chunk_id in skill_mapping.items():
            if skill_name in edits["skills"] and "replace" in edits["skills"][skill_name]:
                new_skill = edits["skills"][skill_name]["replace"]
                if new_skill:
                    # Clean up skill content if it accidentally includes the category name
                    if new_skill.startswith(f"{skill_name}:"):
                        new_skill = new_skill[len(f"{skill_name}:"):].strip()
                    
                    # Escape only the content part, not the LaTeX formatting
                    escaped_skill_content = latex_escape(new_skill)
                    
                    # Reconstruct the full LaTeX formatting
                    formatted_skill = f"\\textbf{{{skill_name}:}} {escaped_skill_content}"
                    
                    # Replace content directly without going through normal escaping
                    modified_content = replace_chunk_content_raw(modified_content, chunk_id, formatted_skill)
    
    return modified_content


def apply_cover_letter_edits(content: str, edits: Dict[str, Any]) -> str:
    """Apply cover letter edits to content."""
    
    modified_content = content
    
    # Apply paragraph edits
    if "cover_letter" in edits and "paragraphs" in edits["cover_letter"]:
        paragraphs = edits["cover_letter"]["paragraphs"]
        
        for i, new_paragraph in enumerate(paragraphs, 1):
            if new_paragraph:
                chunk_id = f"COVER.P{i}"
                modified_content = replace_chunk_content(modified_content, chunk_id, new_paragraph)
    
    return modified_content


def apply_edits_to_files(resume_file: str, cover_file: str, edits_file: str) -> Tuple[str, str]:
    """Apply edits to résumé and cover letter files, return output paths."""
    
    # Load edits
    with open(edits_file, 'r', encoding='utf-8') as f:
        edits = json.load(f)
    
    # Process résumé
    with open(resume_file, 'r', encoding='utf-8') as f:
        resume_content = f.read()
    
    modified_resume = apply_resume_edits(resume_content, edits)
    
    # Generate output filename with .tuned.tex pattern
    base_name = resume_file.split('/')[-1].replace(' llm_ready.tex', '').replace('llm_ready.tex', '')
    resume_output = f"out/{base_name}.tuned.tex"
    
    with open(resume_output, 'w', encoding='utf-8') as f:
        f.write(modified_resume)
    
    # Process cover letter
    with open(cover_file, 'r', encoding='utf-8') as f:
        cover_content = f.read()
    
    modified_cover = apply_cover_letter_edits(cover_content, edits)
    
    # Generate output filename with .tuned.tex pattern  
    base_name = cover_file.split('/')[-1].replace(' llm_ready.tex', '').replace('llm_ready.tex', '')
    cover_output = f"out/{base_name}.tuned.tex"
    
    with open(cover_output, 'w', encoding='utf-8') as f:
        f.write(modified_cover)
    
    return resume_output, cover_output


def validate_latex_compilation(tex_file: str) -> bool:
    """Validate that a LaTeX file can be compiled (basic check)."""
    
    with open(tex_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Basic checks for common issues
    issues = []
    
    # Check for unmatched braces
    open_braces = content.count('{')
    close_braces = content.count('}')
    if open_braces != close_braces:
        issues.append(f"Unmatched braces: {open_braces} open, {close_braces} close")
    
    # Check for required document structure
    if '\\documentclass' not in content:
        issues.append("Missing \\documentclass")
    
    if '\\begin{document}' not in content:
        issues.append("Missing \\begin{document}")
    
    if '\\end{document}' not in content:
        issues.append("Missing \\end{document}")
    
    # Check for problematic patterns that might have been introduced
    problematic_patterns = [
        (r'[^\\]\\[^a-zA-Z\\{}]', "Unescaped backslash"),
        (r'(?<!\\)%(?![^%]*%)', "Unescaped percent sign in content"),
        (r'(?<!\\)&(?![^&]*&)', "Unescaped ampersand in content"),
    ]
    
    for pattern, description in problematic_patterns:
        if re.search(pattern, content):
            issues.append(description)
    
    if issues:
        print("LaTeX validation warnings:")
        for issue in issues:
            print(f"  - {issue}")
        return False
    
    return True


def create_summary_report(resume_file: str, cover_file: str, edits_file: str) -> str:
    """Create a summary report of applied changes."""
    
    with open(edits_file, 'r', encoding='utf-8') as f:
        edits = json.load(f)
    
    report_lines = ["Edit Application Summary", "=" * 25, ""]
    
    # Summary changes
    if edits.get("summary", {}).get("replace"):
        report_lines.append("✓ Summary updated")
    
    # Skills changes
    skills_changed = []
    if "skills" in edits:
        for skill_name, skill_edit in edits["skills"].items():
            if skill_edit.get("replace"):
                skills_changed.append(skill_name)
    
    if skills_changed:
        report_lines.append(f"✓ Skills updated: {', '.join(skills_changed)}")
    
    # Cover letter changes
    cover_changes = 0
    if "cover_letter" in edits and "paragraphs" in edits["cover_letter"]:
        paragraphs = edits["cover_letter"]["paragraphs"]
        cover_changes = sum(1 for p in paragraphs if p is not None)
    
    if cover_changes:
        report_lines.append(f"✓ Cover letter: {cover_changes} paragraph(s) updated")
    
    # Suggested additions
    suggestions = edits.get("suggested_additions", [])
    if suggestions:
        report_lines.extend(["", "Suggested Additions:"])
        for suggestion in suggestions:
            term = suggestion.get("term", "")
            why = suggestion.get("why", "")
            report_lines.append(f"  • {term}: {why}")
    
    # Output files
    report_lines.extend([
        "",
        "Output Files:",
        f"  • Résumé: {resume_file}",
        f"  • Cover Letter: {cover_file}"
    ])
    
    return "\n".join(report_lines)


def apply_edits_with_validation(resume_file: str, cover_file: str, edits_file: str) -> None:
    """Apply edits with validation and reporting."""
    
    print("Applying edits...")
    
    try:
        resume_output, cover_output = apply_edits_to_files(resume_file, cover_file, edits_file)
        
        print(f"✓ Applied edits to résumé: {resume_output}")
        print(f"✓ Applied edits to cover letter: {cover_output}")
        
        # Validate LaTeX
        resume_valid = validate_latex_compilation(resume_output)
        cover_valid = validate_latex_compilation(cover_output)
        
        if resume_valid:
            print("✓ Résumé LaTeX validation passed")
        else:
            print("⚠ Résumé LaTeX validation warnings (see above)")
        
        if cover_valid:
            print("✓ Cover letter LaTeX validation passed")
        else:
            print("⚠ Cover letter LaTeX validation warnings (see above)")
        
        # Create and display summary
        summary = create_summary_report(resume_output, cover_output, edits_file)
        print(f"\n{summary}")
        
    except Exception as e:
        print(f"Error applying edits: {e}")
        raise


def get_chunk_diff_preview(original_file: str, chunk_id: str, new_content: str) -> str:
    """Preview what a chunk replacement would look like."""
    
    with open(original_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    try:
        content_start, content_end = find_chunk_boundaries(content, chunk_id)
        original_content = content[content_start:content_end].strip()
        escaped_new_content = latex_escape(new_content)
        
        return f"""Chunk: {chunk_id}
Original:
{original_content}

New:
{escaped_new_content}
"""
    
    except ValueError:
        return f"Chunk {chunk_id} not found in file"