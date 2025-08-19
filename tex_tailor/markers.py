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
    
    # First reorder sections
    content = reorder_resume_sections(content)
    
    # Create meta header
    all_chunks = RESUME_LOCKS + RESUME_CHUNKS
    meta_header = create_meta_header("RESUME", all_chunks)
    
    # Wrap preamble (everything before \begin{document})
    preamble_match = re.search(r'(.*?)(\\begin\{document\})', content, re.DOTALL)
    if preamble_match:
        preamble = preamble_match.group(1)
        begin_doc = preamble_match.group(2)
        wrapped_preamble = wrap_chunk(preamble.strip(), "RESUME.PREAMBLE", False)
        content = content.replace(preamble + begin_doc, wrapped_preamble + "\n\n" + begin_doc)
    
    # Extract and wrap summary
    summary_pattern = r'(\\section\*?\{.*?(?:Summary|Professional Summary).*?\}\s*)(.*?)(?=\\section|\Z)'
    summary_match = re.search(summary_pattern, content, re.DOTALL | re.IGNORECASE)
    if summary_match:
        summary_header = summary_match.group(1)
        summary_content = summary_match.group(2).strip()
        wrapped_header = wrap_chunk(summary_header.strip(), "RESUME.HEADER", False)
        wrapped_content = wrap_chunk(summary_content, "RESUME.SUMMARY", True)
        content = content.replace(summary_match.group(0), wrapped_header + "\n\n" + wrapped_content)
    
    # Extract and wrap experience section
    exp_pattern = r'(\\section\*?\{.*?(?:Experience|Work Experience|Professional Experience).*?\}\s*)(.*?)(?=\\section|\Z)'
    exp_match = re.search(exp_pattern, content, re.DOTALL | re.IGNORECASE)
    if exp_match:
        exp_content = exp_match.group(0)
        wrapped_exp = wrap_chunk(exp_content.strip(), "RESUME.EXPERIENCE", False)
        content = content.replace(exp_content, wrapped_exp)
    
    # Extract and wrap skills section
    skills_pattern = r'(\\section\*?\{.*?(?:Skills|Technical Skills).*?\})(.*?)(?=\\section|\Z)'
    skills_match = re.search(skills_pattern, content, re.DOTALL | re.IGNORECASE)
    if skills_match:
        skills_header = skills_match.group(1)
        skills_body = skills_match.group(2)
        
        # Parse individual skill lines
        skill_lines = []
        for line in skills_body.split('\n'):
            line = line.strip()
            if line and not line.startswith('%'):
                skill_lines.append(line)
        
        # Map skill lines to chunk IDs
        skill_mapping = {
            'Programming Languages': 'SKILLS.Programming Languages',
            'Frontend': 'SKILLS.Frontend', 
            'Backend': 'SKILLS.Backend',
            'Cloud & DevOps': 'SKILLS.Cloud & DevOps',
            'AI & LLM Tools': 'SKILLS.AI & LLM Tools',
            'Automation & Productivity': 'SKILLS.Automation & Productivity',
            'Security & Operating Systems': 'SKILLS.Security & Operating Systems',
            'Databases': 'SKILLS.Databases'
        }
        
        # Rebuild skills section with markers
        new_skills = [skills_header.strip()]
        
        for skill_name, chunk_id in skill_mapping.items():
            # Find matching line
            matching_line = None
            for line in skill_lines:
                if skill_name.lower() in line.lower():
                    matching_line = line
                    break
            
            if matching_line:
                # Extract just the content after the skill name
                content_match = re.search(rf'{re.escape(skill_name)}:\s*(.*)', matching_line, re.IGNORECASE)
                if content_match:
                    skill_content = content_match.group(1)
                    wrapped_skill = wrap_chunk(skill_content.strip(), chunk_id, True)
                    new_skills.append(f"\\textbf{{{skill_name}:}} {wrapped_skill}")
        
        new_skills_content = '\n'.join(new_skills)
        content = content.replace(skills_match.group(0), new_skills_content)
    
    # Wrap education
    edu_pattern = r'(\\section\*?\{.*?(?:Education).*?\}.*?)(?=\\section|\Z)'
    edu_match = re.search(edu_pattern, content, re.DOTALL | re.IGNORECASE)
    if edu_match:
        edu_content = edu_match.group(0)
        wrapped_edu = wrap_chunk(edu_content.strip(), "RESUME.EDUCATION", False)
        content = content.replace(edu_content, wrapped_edu)
    
    # Wrap certifications
    cert_pattern = r'(\\section\*?\{.*?(?:Certifications?).*?\}.*?)(?=\\section|\Z)'
    cert_match = re.search(cert_pattern, content, re.DOTALL | re.IGNORECASE)
    if cert_match:
        cert_content = cert_match.group(0)
        wrapped_cert = wrap_chunk(cert_content.strip(), "RESUME.CERTS", False)
        content = content.replace(cert_content, wrapped_cert)
    
    return meta_header + content


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