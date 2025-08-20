"""
Module for extracting CHUNK regions from LaTeX files and building JSON payloads.
"""
import re
import json
from typing import Dict, List, Any, Optional


def extract_chunks_from_file(filepath: str) -> Dict[str, str]:
    """Extract all CHUNK regions from a LaTeX file."""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    chunks = {}
    
    # Regex pattern to match CHUNK blocks
    chunk_pattern = r'^% === LLM:CHUNK START (.+) ===\s*\n(.*?)\n% === LLM:CHUNK END \1 ===$'
    
    matches = re.finditer(chunk_pattern, content, re.MULTILINE | re.DOTALL)
    
    for match in matches:
        chunk_id = match.group(1)
        chunk_content = match.group(2).strip()
        chunks[chunk_id] = chunk_content
    
    return chunks


def extract_meta_info(filepath: str) -> Optional[Dict[str, Any]]:
    """Extract LLM-META information from a LaTeX file."""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Find meta block
    meta_pattern = r'% === LLM-META ===\s*\n(.*?)\n% === /LLM-META ==='
    meta_match = re.search(meta_pattern, content, re.DOTALL)
    
    if not meta_match:
        return None
    
    # Extract JSON from comment lines
    meta_lines = meta_match.group(1).split('\n')
    json_lines = []
    
    for line in meta_lines:
        line = line.strip()
        if line.startswith('% '):
            json_lines.append(line[2:])  # Remove '% ' prefix
    
    try:
        meta_json = '\n'.join(json_lines)
        return json.loads(meta_json)
    except json.JSONDecodeError:
        return None


def extract_skill_content(skill_text: str) -> str:
    """Extract just the content part from a skill line, removing LaTeX formatting."""
    if not skill_text:
        return ""
    
    # Pattern: \textbf{Skill Name:} content
    # We want to extract just the content part
    match = re.search(r'\\textbf\{[^}]+:\}\s*(.+)', skill_text)
    if match:
        return match.group(1).strip()
    
    # Fallback: if no textbf pattern, return as-is
    return skill_text


def build_base_text_json(resume_file: str, cover_file: str) -> Dict[str, Any]:
    """Build the base_text.json structure from résumé and cover letter files."""
    
    # Extract chunks from résumé
    resume_chunks = extract_chunks_from_file(resume_file)
    
    # Extract chunks from cover letter
    cover_chunks = extract_chunks_from_file(cover_file)
    
    # Build the base text structure
    base_text = {
        "resume": {
            "summary": resume_chunks.get("RESUME.SUMMARY", ""),
            "skills": {
                "Programming Languages": extract_skill_content(resume_chunks.get("SKILLS.Programming Languages", "")),
                "Frontend": extract_skill_content(resume_chunks.get("SKILLS.Frontend", "")),
                "Backend": extract_skill_content(resume_chunks.get("SKILLS.Backend", "")),
                "Cloud & DevOps": extract_skill_content(resume_chunks.get("SKILLS.Cloud & DevOps", "")),
                "AI & LLM Tools": extract_skill_content(resume_chunks.get("SKILLS.AI & LLM Tools", "")),
                "Automation & Productivity": extract_skill_content(resume_chunks.get("SKILLS.Automation & Productivity", "")),
                "Security & Operating Systems": extract_skill_content(resume_chunks.get("SKILLS.Security & Operating Systems", "")),
                "Databases": extract_skill_content(resume_chunks.get("SKILLS.Databases", ""))
            }
        },
        "cover_letter": {
            "salutation": cover_chunks.get("COVER.SALUTATION", ""),
            "paragraphs": [
                cover_chunks.get("COVER.P1", ""),
                cover_chunks.get("COVER.P2", ""),
                cover_chunks.get("COVER.P3", ""),
                cover_chunks.get("COVER.P4", "")
            ]
        },
        "meta": {
            "resume_chunks": len([k for k in resume_chunks.keys() if k.startswith(("RESUME.", "SKILLS."))]),
            "cover_chunks": len([k for k in cover_chunks.keys() if k.startswith("COVER.")]),
            "total_editable_chunks": len([k for k in list(resume_chunks.keys()) + list(cover_chunks.keys()) 
                                        if k.startswith(("RESUME.SUMMARY", "SKILLS.", "COVER.P", "COVER.SALUTATION"))])
        }
    }
    
    return base_text


def extract_to_json(resume_file: str, cover_file: str, output_file: str, quiet: bool = False) -> None:
    """Extract base text from files and save as JSON."""
    
    base_text = build_base_text_json(resume_file, cover_file)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(base_text, f, indent=2, ensure_ascii=False)
    
    if not quiet:
        print(f"Extracted base text to: {output_file}")
        print(f"Found {base_text['meta']['total_editable_chunks']} editable chunks")


def validate_chunk_structure(filepath: str) -> List[str]:
    """Validate that all CHUNK blocks are properly closed and structured."""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    errors = []
    
    # Find all CHUNK START markers
    start_pattern = r'% === LLM:CHUNK START (.+) ==='
    start_matches = re.finditer(start_pattern, content)
    
    for start_match in start_matches:
        chunk_id = start_match.group(1)
        
        # Look for corresponding END marker
        end_pattern = rf'% === LLM:CHUNK END {re.escape(chunk_id)} ==='
        end_match = re.search(end_pattern, content[start_match.end():])
        
        if not end_match:
            errors.append(f"Missing END marker for chunk: {chunk_id}")
    
    # Find all CHUNK END markers and check they have corresponding START
    end_pattern = r'% === LLM:CHUNK END (.+) ==='
    end_matches = re.finditer(end_pattern, content)
    
    for end_match in end_matches:
        chunk_id = end_match.group(1)
        
        # Look for corresponding START marker before this position
        start_pattern_specific = rf'% === LLM:CHUNK START {re.escape(chunk_id)} ==='
        start_match = re.search(start_pattern_specific, content[:end_match.start()])
        
        if not start_match:
            errors.append(f"Missing START marker for chunk: {chunk_id}")
    
    return errors


def list_available_chunks(filepath: str) -> Dict[str, Dict[str, str]]:
    """List all available chunks in a file with their metadata."""
    chunks = extract_chunks_from_file(filepath)
    meta = extract_meta_info(filepath)
    
    result = {}
    
    for chunk_id, content in chunks.items():
        chunk_meta = {}
        
        if meta and 'chunks' in meta:
            for chunk_def in meta['chunks']:
                if chunk_def['id'] == chunk_id:
                    chunk_meta = chunk_def
                    break
        
        result[chunk_id] = {
            'content': content,
            'editable': chunk_meta.get('editable', True),
            'type': chunk_meta.get('type', 'unknown'),
            'length': len(content)
        }
    
    return result