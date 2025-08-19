"""
Module for adding LOCK/CHUNK markers to LaTeX files and reordering résumé sections.
"""
import re
import json
from pathlib import Path
from typing import Dict, List, Any


# Résumé chunk definitions (order matters)
RESUME_CHUNKS = [
    {"id": "RESUME.SUMMARY", "editable": True, "type": "paragraph"},
    {"id": "SKILLS.Programming Languages", "editable": True, "type": "skill_line"},
    {"id": "SKILLS.Frontend", "editable": True, "type": "skill_line"},
    {"id": "SKILLS.Backend", "editable": True, "type": "skill_line"},
    {"id": "SKILLS.Cloud & DevOps", "editable": True, "type": "skill_line"},
    {"id": "SKILLS.AI & LLM Tools", "editable": True, "type": "skill_line"},
    {"id": "SKILLS.Automation & Productivity", "editable": True, "type": "skill_line"},
    {"id": "SKILLS.Security & Operating Systems", "editable": True, "type": "skill_line"},
    {"id": "SKILLS.Databases", "editable": True, "type": "skill_line"},
]

RESUME_LOCKS = [
    {"id": "RESUME.PREAMBLE", "editable": False, "type": "fixed"},
    {"id": "RESUME.HEADER", "editable": False, "type": "fixed"},
    {"id": "RESUME.EXPERIENCE", "editable": False, "type": "fixed"},
    {"id": "RESUME.EDUCATION", "editable": False, "type": "fixed"},
    {"id": "RESUME.CERTS", "editable": False, "type": "fixed"},
]

# Cover letter chunk definitions
COVER_CHUNKS = [
    {"id": "COVER.P1", "editable": True, "type": "paragraph"},
    {"id": "COVER.P2", "editable": True, "type": "paragraph"},
    {"id": "COVER.P3", "editable": True, "type": "paragraph"},
    {"id": "COVER.P4", "editable": True, "type": "paragraph"},
]

COVER_LOCKS = [
    {"id": "COVER.PREAMBLE", "editable": False, "type": "fixed"},
    {"id": "COVER.HEADER", "editable": False, "type": "fixed"},
    {"id": "COVER.DATE", "editable": False, "type": "fixed"},
    {"id": "COVER.SALUTATION", "editable": False, "type": "fixed"},
    {"id": "COVER.SIGNOFF", "editable": False, "type": "fixed"},
]


def create_meta_header(doc_type: str, chunks: List[Dict[str, Any]]) -> str:
    """Create the LLM-META header for a document."""
    meta = {
        "doc": doc_type,
        "version": "1.0",
        "chunks": chunks,
        "rules": {"output": "TEXT ONLY"}
    }
    
    lines = ["% === LLM-META ==="]
    json_str = json.dumps(meta, indent=2)
    for line in json_str.split('\n'):
        lines.append(f"% {line}")
    lines.append("% === /LLM-META ===")
    lines.append("")
    
    return '\n'.join(lines)


def wrap_chunk(content: str, chunk_id: str, editable: bool = True) -> str:
    """Wrap content in appropriate LOCK or CHUNK markers."""
    if editable:
        return f"% === LLM:CHUNK START {chunk_id} ===\n{content}\n% === LLM:CHUNK END {chunk_id} ==="
    else:
        return f"% === LLM:LOCK START {chunk_id} ===\n{content}\n% === LLM:LOCK END {chunk_id} ==="


def reorder_resume_sections(content: str) -> str:
    """Reorder résumé sections: Header → Summary → Work Experience → Technical Skills → Education → Certifications."""
    
    # Find section patterns
    sections = {}
    
    # Look for major sections
    header_match = re.search(r'(\\documentclass.*?(?=\\section|\\begin{document}))', content, re.DOTALL)
    if header_match:
        sections['header'] = header_match.group(1)
    
    # Find Summary section
    summary_match = re.search(r'(\\section\*?\{.*?(?:Summary|Professional Summary).*?\}.*?)(?=\\section|\Z)', content, re.DOTALL | re.IGNORECASE)
    if summary_match:
        sections['summary'] = summary_match.group(1)
    
    # Find Experience section
    exp_match = re.search(r'(\\section\*?\{.*?(?:Experience|Work Experience|Professional Experience).*?\}.*?)(?=\\section|\Z)', content, re.DOTALL | re.IGNORECASE)
    if exp_match:
        sections['experience'] = exp_match.group(1)
    
    # Find Skills section
    skills_match = re.search(r'(\\section\*?\{.*?(?:Skills|Technical Skills).*?\}.*?)(?=\\section|\Z)', content, re.DOTALL | re.IGNORECASE)
    if skills_match:
        sections['skills'] = skills_match.group(1)
    
    # Find Education section
    edu_match = re.search(r'(\\section\*?\{.*?(?:Education).*?\}.*?)(?=\\section|\Z)', content, re.DOTALL | re.IGNORECASE)
    if edu_match:
        sections['education'] = edu_match.group(1)
    
    # Find Certifications section
    cert_match = re.search(r'(\\section\*?\{.*?(?:Certifications?).*?\}.*?)(?=\\section|\Z)', content, re.DOTALL | re.IGNORECASE)
    if cert_match:
        sections['certifications'] = cert_match.group(1)
    
    # Find end document
    end_match = re.search(r'(\\end\{document\})', content)
    end_doc = end_match.group(1) if end_match else "\\end{document}"
    
    # Reconstruct in correct order
    reordered = []
    if 'header' in sections:
        reordered.append(sections['header'])
    if 'summary' in sections:
        reordered.append(sections['summary'])
    if 'experience' in sections:
        reordered.append(sections['experience'])
    if 'skills' in sections:
        reordered.append(sections['skills'])
    if 'education' in sections:
        reordered.append(sections['education'])
    if 'certifications' in sections:
        reordered.append(sections['certifications'])
    
    reordered.append(end_doc)
    
    return '\n\n'.join(reordered)


def add_resume_markers(content: str) -> str:
    """Add LOCK/CHUNK markers to résumé content."""
    
    # Create meta header
    all_chunks = RESUME_LOCKS + RESUME_CHUNKS
    meta_header = create_meta_header("RESUME", all_chunks)
    
    # Extract the preamble (everything before \begin{document})
    preamble_match = re.search(r'(.*?)(\\begin\{document\})', content, re.DOTALL)
    if not preamble_match:
        return content  # If we can't find the structure, return as-is
    
    preamble = preamble_match.group(1).strip()
    begin_doc = preamble_match.group(2)
    
    # Extract the header section (from \begin{document} to the end of the header)
    header_end_match = re.search(r'(\\begin\{document\}.*?\\section\{PROFESSIONAL SUMMARY\})', content, re.DOTALL)
    if not header_end_match:
        return content
    
    header_content = header_end_match.group(1)
    
    # Extract the summary text
    summary_match = re.search(r'(\\section\{PROFESSIONAL SUMMARY\}.*?\\item \\small\{%)(.*?)(%\})', content, re.DOTALL)
    if not summary_match:
        return content
    
    summary_header = summary_match.group(1)
    summary_text = summary_match.group(2).strip()
    summary_end = summary_match.group(3)
    
    # Extract the experience section
    exp_match = re.search(r'(\\section\{WORK EXPERIENCE\}.*?)(?=\\section\{TECHNICAL SKILLS\})', content, re.DOTALL)
    if not exp_match:
        return content
    
    exp_content = exp_match.group(1)
    
    # Extract the skills section
    skills_match = re.search(r'(\\section\{TECHNICAL SKILLS\}.*?\\resumeSubHeadingListStart.*?\\item \\small\{)(.*?)(\}\s*\\resumeSubHeadingListEnd)', content, re.DOTALL)
    if not skills_match:
        return content
    
    skills_prefix = skills_match.group(1)
    skills_body = skills_match.group(2)
    skills_suffix = skills_match.group(3)
    
    # Extract the education section
    edu_match = re.search(r'(\\section\{EDUCATION\}.*?)(?=\\section\{CERTIFICATIONS\})', content, re.DOTALL)
    if not edu_match:
        return content
    
    edu_content = edu_match.group(1)
    
    # Extract the certifications section
    cert_match = re.search(r'(\\section\{CERTIFICATIONS\}.*?\\end\{document\})', content, re.DOTALL)
    if not cert_match:
        return content
    
    cert_content = cert_match.group(1)
    
    # Parse skills into individual lines
    skill_pattern = r'\\textbf\{([^}]+):\}([^\\]+)'
    skill_matches = re.findall(skill_pattern, skills_body)
    
    # Map skill categories to chunk IDs
    skill_mapping = {
        'Programming Languages': 'SKILLS.Programming Languages',
        'Frontend': 'SKILLS.Frontend', 
        'Backend': 'SKILLS.Backend',
        'Cloud and DevOps': 'SKILLS.Cloud & DevOps',
        'AI and LLM Tools': 'SKILLS.AI & LLM Tools',
        'Automation and Productivity': 'SKILLS.Automation & Productivity',
        'Security and Operating Systems': 'SKILLS.Security & Operating Systems',
        'Databases': 'SKILLS.Databases'
    }
    
    # Rebuild skills section with markers
    new_skills_lines = []
    for category, skills in skill_matches:
        category = category.strip()
        skills = skills.strip()
        
        # Find the chunk ID for this category
        chunk_id = None
        for skill_name, chunk_id_val in skill_mapping.items():
            if skill_name.lower() == category.lower():
                chunk_id = chunk_id_val
                break
        
        if chunk_id:
            # Reconstruct the skill line with proper formatting
            skill_line = f"\\textbf{{{category}:}} {skills}"
            wrapped_skill = wrap_chunk(skill_line, chunk_id, True)
            new_skills_lines.append(wrapped_skill)
            new_skills_lines.append("")
            new_skills_lines.append("\\vspace{3pt}")
            new_skills_lines.append("")
    
    # Remove the last spacing elements
    if new_skills_lines:
        new_skills_lines = new_skills_lines[:-2]
    
    new_skills_body = '\n'.join(new_skills_lines)
    new_skills_content = skills_prefix + new_skills_body + skills_suffix
    
    # Construct the final document
    result = []
    result.append(meta_header)
    result.append(preamble)
    result.append("")
    result.append(wrap_chunk(header_content, "RESUME.HEADER", False))
    result.append("")
    result.append(summary_header + wrap_chunk(summary_text, "RESUME.SUMMARY", True) + summary_end)
    result.append("")
    result.append(wrap_chunk(exp_content, "RESUME.EXPERIENCE", False))
    result.append("")
    result.append(new_skills_content)
    result.append("")
    result.append(wrap_chunk(edu_content, "RESUME.EDUCATION", False))
    result.append("")
    result.append(wrap_chunk(cert_content, "RESUME.CERTS", False))
    
    return '\n'.join(result)


def add_cover_letter_markers(content: str) -> str:
    """Add LOCK/CHUNK markers to cover letter content."""
    
    # Create meta header
    all_chunks = COVER_LOCKS + COVER_CHUNKS
    meta_header = create_meta_header("COVER", all_chunks)
    
    # Wrap preamble
    preamble_match = re.search(r'(.*?)(\\begin\{document\})', content, re.DOTALL)
    if preamble_match:
        preamble = preamble_match.group(1)
        begin_doc = preamble_match.group(2)
        wrapped_preamble = wrap_chunk(preamble.strip(), "COVER.PREAMBLE", False)
        content = content.replace(preamble + begin_doc, wrapped_preamble + "\n\n" + begin_doc)
    
    # Find and wrap header/date/salutation
    # This is a simplified approach - in practice you'd need more sophisticated parsing
    # based on the actual structure of your cover letter
    
    # Wrap main body paragraphs as COVER.P1, P2, P3, P4
    # This is a placeholder - you'd need to implement based on actual cover letter structure
    
    return meta_header + content


def process_resume_file(input_path: str, output_path: str) -> None:
    """Process a résumé file and add markers."""
    with open(input_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    marked_content = add_resume_markers(content)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(marked_content)


def process_cover_letter_file(input_path: str, output_path: str) -> None:
    """Process a cover letter file and add markers."""
    with open(input_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    marked_content = add_cover_letter_markers(content)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(marked_content)


def init_files() -> None:
    """Initialize the baseline files with markers."""
    # Define paths - look in current directory first, then fallback to original path
    resume_input_local = Path("Baseline_Resume/Conner_Jordan_Software_Engineer copy.tex")
    resume_input_original = Path("~/Doc/Sandbox_v3/Baseline_Resume/Conner_Jordan_Software_Engineer copy.tex").expanduser()
    resume_output = Path("Baseline_Resume/Conner_Jordan_Software_Engineer llm_ready.tex")
    
    cover_input_local = Path("Basline_Cover_Letter/Conner_Jordan_Cover_Letter copy.tex")
    cover_input_original = Path("~/Doc/Sandbox_v3/Basline_Cover_Letter/Conner_Jordan_Cover_Letter copy.tex").expanduser()
    cover_output = Path("Basline_Cover_Letter/Conner_Jordan_Cover_Letter llm_ready.tex")
    
    # Choose the input file that actually exists
    resume_input = resume_input_local if resume_input_local.exists() else resume_input_original
    cover_input = cover_input_local if cover_input_local.exists() else cover_input_original
    
    # Create output directories
    resume_output.parent.mkdir(exist_ok=True)
    cover_output.parent.mkdir(exist_ok=True)
    
    # Process files
    if resume_input.exists():
        process_resume_file(str(resume_input), str(resume_output))
        print(f"Created: {resume_output}")
    else:
        print(f"Warning: Resume source file not found: {resume_input}")
    
    if cover_input.exists():
        process_cover_letter_file(str(cover_input), str(cover_output))
        print(f"Created: {cover_output}")
    else:
        print(f"Warning: Cover letter source file not found: {cover_input}")