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
    {"id": "COVER.SALUTATION", "editable": True, "type": "salutation"},
    {"id": "COVER.P1", "editable": True, "type": "paragraph"},
    {"id": "COVER.P2", "editable": True, "type": "paragraph"},
    {"id": "COVER.P3", "editable": True, "type": "paragraph"},
    {"id": "COVER.P4", "editable": True, "type": "paragraph"},
]

COVER_LOCKS = [
    {"id": "COVER.PREAMBLE", "editable": False, "type": "fixed"},
    {"id": "COVER.HEADER", "editable": False, "type": "fixed"},
    {"id": "COVER.DATE", "editable": False, "type": "fixed"},
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
    
    # Extract the preamble (everything before \begin{document})
    preamble_match = re.search(r'(.*?)(\\begin\{document\})', content, re.DOTALL)
    if not preamble_match:
        return content  # If we can't find the structure, return as-is
    
    preamble = preamble_match.group(1).strip()
    begin_doc = preamble_match.group(2)
    
    # Extract the header section (from \begin{document} to date)
    header_match = re.search(r'(\\begin\{document\}.*?)(?=\\vspace\{16pt\}.*?\\begin\{flushright\})', content, re.DOTALL)
    if not header_match:
        return content
    
    header_content = header_match.group(1)
    
    # Extract the date section
    date_match = re.search(r'(\\begin\{flushright\}.*?August.*?\\end\{flushright\})', content, re.DOTALL)
    if not date_match:
        return content
    
    date_content = date_match.group(1)
    
    # Extract the body content (everything after date until end)
    body_match = re.search(r'\\end\{flushright\}(.*?)\\end\{document\}', content, re.DOTALL)
    if not body_match:
        return content
    
    body_content = body_match.group(1).strip()
    
    # Split body into paragraphs and create salutation + paragraphs
    # Replace "Hiring Team," with template and make first paragraph without salutation
    body_lines = body_content.split('\n')
    
    # Build the new content
    result = []
    result.append(meta_header)
    result.append(wrap_chunk(preamble, "COVER.PREAMBLE", False))
    result.append("")
    result.append(header_content)
    result.append("")
    result.append("\\vspace{16pt}")
    result.append("")
    result.append(wrap_chunk(date_content, "COVER.DATE", False))
    result.append("")
    result.append(wrap_chunk("\\noindent\nHello [Company Name] team,", "COVER.SALUTATION", True))
    result.append("")
    result.append("\\vspace{16pt}")
    result.append("")
    
    # Add the main paragraphs
    result.append(wrap_chunk("I'm applying for the [Job Title] role at [Company Name]. I was drawn to your work in [Mention a specific area from the job description, e.g., building next-generation cloud infrastructure].\n\nMy core strengths are in Python and systems-level development, with a focus on building secure, observable, and scalable software solutions. I am adept at working across cloud environments like AWS, Azure, and GCP, containerizing with Docker/Kubernetes, provisioning with Terraform, and implementing CI/CD pipelines to ensure that all processes are testable, versioned, and easy to roll back.", "COVER.P1", True))
    result.append("")
    result.append("\\vspace{16pt}")
    result.append("")
    
    result.append(wrap_chunk("At a previous role, I engineered a solution that consolidated diverse enterprise systems—including Rapid7, Jamf, and BigFix—into a unified platform. I automated the end-to-end workflow from data aggregation to remediation, which reduced manual effort by over 100 hours per month and improved the organization's visibility and response capabilities across thousands of endpoints.", "COVER.P2", True))
    result.append("")
    result.append("\\vspace{16pt}")
    result.append("")
    
    result.append(wrap_chunk("Earlier, I developed custom automation and tooling to analyze system behavior, identify anomalies, and harden production environments. These projects leaned on the same foundations you need: robust system architecture, strong authentication and secrets management, and disciplined monitoring and alerting to maintain high availability and performance.\n\nI am comfortable owning the entire lifecycle of a solution, from design through deployment and operations. This includes architecting and implementing features, instrumenting pipelines, documenting APIs and system contracts, and collaborating closely with cross-functional teams. While my experience is broad, I can ramp quickly on any specific technology stack your team uses.", "COVER.P3", True))
    result.append("")
    result.append("\\vspace{16pt}")
    result.append("")
    
    result.append(wrap_chunk("If your mandate is to build reliable, secure, and scalable software that solves complex problems, I would like to help you ship that.", "COVER.P4", True))
    result.append("")
    result.append("\\vspace{16pt}")
    result.append("")
    
    result.append(wrap_chunk("Sincerely,  \nConner Jordan", "COVER.SIGNOFF", False))
    result.append("")
    result.append("\\end{document}")
    
    return '\n'.join(result)


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


def init_files(quiet: bool = False) -> None:
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
        if not quiet:
            print(f"Created: {resume_output}")
    else:
        if not quiet:
            print(f"Warning: Resume source file not found: {resume_input}")
    
    if cover_input.exists():
        process_cover_letter_file(str(cover_input), str(cover_output))
        if not quiet:
            print(f"Created: {cover_output}")
    else:
        if not quiet:
            print(f"Warning: Cover letter source file not found: {cover_input}")