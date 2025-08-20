"""
Module for creating colorized word-level diffs of chunk changes.
"""
import re
import json
from typing import List, Tuple, Dict, Any
from pathlib import Path

try:
    from colorama import init, Fore, Back, Style
    init(autoreset=True)
    COLORS_AVAILABLE = True
except ImportError:
    COLORS_AVAILABLE = False
    # Fallback for when colorama is not available
    class Fore:
        RED = ""
        GREEN = ""
        YELLOW = ""
        BLUE = ""
        CYAN = ""
        RESET = ""
    
    class Back:
        RED = ""
        GREEN = ""
        RESET = ""
    
    class Style:
        BRIGHT = ""
        RESET_ALL = ""


def get_chunk_content(filepath: str, chunk_id: str) -> str:
    """Extract content from a specific chunk."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Find chunk boundaries
        start_pattern = rf'^% === LLM:CHUNK START {re.escape(chunk_id)} ===\s*\n'
        end_pattern = rf'\n% === LLM:CHUNK END {re.escape(chunk_id)} ===$'
        
        start_match = re.search(start_pattern, content, re.MULTILINE)
        if not start_match:
            return ""
        
        end_match = re.search(end_pattern, content[start_match.end():], re.MULTILINE)
        if not end_match:
            return ""
        
        chunk_content = content[start_match.end():start_match.end() + end_match.start()]
        return chunk_content.strip()
        
    except FileNotFoundError:
        return ""


def tokenize_text(text: str) -> List[str]:
    """Tokenize text into words and whitespace for word-level diffing."""
    if not text:
        return []
    
    # Split on word boundaries, keeping delimiters
    tokens = re.split(r'(\s+)', text)
    return [token for token in tokens if token]


def compute_word_diff(old_tokens: List[str], new_tokens: List[str]) -> List[Tuple[str, str]]:
    """Compute word-level diff between two token lists.
    
    Returns list of (status, token) tuples where status is:
    - 'equal': token unchanged
    - 'delete': token removed
    - 'insert': token added
    """
    
    # Simple word-level diff using dynamic programming
    old_len, new_len = len(old_tokens), len(new_tokens)
    
    # DP table: dp[i][j] = length of LCS of old_tokens[:i] and new_tokens[:j]
    dp = [[0] * (new_len + 1) for _ in range(old_len + 1)]
    
    for i in range(1, old_len + 1):
        for j in range(1, new_len + 1):
            if old_tokens[i-1] == new_tokens[j-1]:
                dp[i][j] = dp[i-1][j-1] + 1
            else:
                dp[i][j] = max(dp[i-1][j], dp[i][j-1])
    
    # Backtrack to find the diff
    result = []
    i, j = old_len, new_len
    
    while i > 0 or j > 0:
        if i > 0 and j > 0 and old_tokens[i-1] == new_tokens[j-1]:
            result.append(('equal', old_tokens[i-1]))
            i -= 1
            j -= 1
        elif j > 0 and (i == 0 or dp[i][j-1] >= dp[i-1][j]):
            result.append(('insert', new_tokens[j-1]))
            j -= 1
        else:
            result.append(('delete', old_tokens[i-1]))
            i -= 1
    
    return list(reversed(result))


def format_diff_line(diff_ops: List[Tuple[str, str]]) -> str:
    """Format a diff line with enhanced colors and readability."""
    formatted_parts = []
    
    for status, token in diff_ops:
        if status == 'equal':
            formatted_parts.append(token)
        elif status == 'delete':
            if COLORS_AVAILABLE:
                formatted_parts.append(f"{Fore.RED}{Style.BRIGHT} -{token}- {Style.RESET_ALL}")
            else:
                formatted_parts.append(f" -{token}- ")
        elif status == 'insert':
            if COLORS_AVAILABLE:
                formatted_parts.append(f"{Fore.BLUE}{Style.BRIGHT} +{token}+ {Style.RESET_ALL}")
            else:
                formatted_parts.append(f" +{token}+ ")
    
    return ''.join(formatted_parts)


def create_chunk_diff(old_content: str, new_content: str, chunk_id: str) -> str:
    """Create a formatted diff for a single chunk."""
    
    old_tokens = tokenize_text(old_content)
    new_tokens = tokenize_text(new_content)
    
    diff_ops = compute_word_diff(old_tokens, new_tokens)
    
    # Format the diff with enhanced header
    if COLORS_AVAILABLE:
        header = f"\n{Fore.WHITE}{Back.MAGENTA}{Style.BRIGHT} 🔧 CHUNK: {chunk_id} {Style.RESET_ALL}\n"
    else:
        header = f"\n🔧 CHUNK: {chunk_id}\n"
    
    diff_line = format_diff_line(diff_ops)
    
    # Add statistics with enhanced formatting
    deletions = sum(1 for op, _ in diff_ops if op == 'delete')
    insertions = sum(1 for op, _ in diff_ops if op == 'insert')
    
    if COLORS_AVAILABLE:
        stats = f"\n{Fore.WHITE}{Back.BLUE}{Style.BRIGHT} 📊 CHANGES: -{deletions} words, +{insertions} words {Style.RESET_ALL}\n"
    else:
        stats = f"\n📊 CHANGES: -{deletions} words, +{insertions} words\n"
    
    return header + diff_line + stats


def get_all_chunk_diffs(original_resume: str, original_cover: str,
                       tuned_resume: str, tuned_cover: str) -> List[str]:
    """Get diffs for all changed chunks."""
    
    diffs = []
    
    # Resume chunks to check
    resume_chunks = [
        "RESUME.SUMMARY",
        "SKILLS.Programming Languages",
        "SKILLS.Frontend", 
        "SKILLS.Backend",
        "SKILLS.Cloud & DevOps",
        "SKILLS.AI & LLM Tools",
        "SKILLS.Automation & Productivity",
        "SKILLS.Security & Operating Systems",
        "SKILLS.Databases"
    ]
    
    for chunk_id in resume_chunks:
        old_content = get_chunk_content(original_resume, chunk_id)
        new_content = get_chunk_content(tuned_resume, chunk_id)
        
        if old_content != new_content and new_content:
            diff = create_chunk_diff(old_content, new_content, chunk_id)
            diffs.append(diff)
    
    # Cover letter chunks
    cover_chunks = ["COVER.P1", "COVER.P2", "COVER.P3", "COVER.P4"]
    
    for chunk_id in cover_chunks:
        old_content = get_chunk_content(original_cover, chunk_id)
        new_content = get_chunk_content(tuned_cover, chunk_id)
        
        if old_content != new_content and new_content:
            diff = create_chunk_diff(old_content, new_content, chunk_id)
            diffs.append(diff)
    
    return diffs


def create_diff_summary(diffs: List[str]) -> str:
    """Create a summary of all changes."""
    
    if not diffs:
        return "No changes detected."
    
    # Extract changed chunk IDs from diffs
    changed_chunks = []
    for diff in diffs:
        chunk_match = re.search(r'=== CHUNK: (.+) ===', diff)
        if chunk_match:
            changed_chunks.append(chunk_match.group(1))
    
    # Categorize changes
    resume_changes = [c for c in changed_chunks if c.startswith(('RESUME.', 'SKILLS.'))]
    cover_changes = [c for c in changed_chunks if c.startswith('COVER.')]
    
    if COLORS_AVAILABLE:
        summary = f"\n{Fore.WHITE}{Back.CYAN}{Style.BRIGHT} 📋 DIFF SUMMARY {Style.RESET_ALL}\n"
        summary += f"{Fore.CYAN}{'='*60}{Style.RESET_ALL}\n"
    else:
        summary = f"\n📋 DIFF SUMMARY\n"
        summary += f"{'='*60}\n"
    
    if resume_changes:
        if COLORS_AVAILABLE:
            summary += f"\n{Fore.GREEN}{Style.BRIGHT}📄 Résumé Changes ({len(resume_changes)}):{Style.RESET_ALL}\n"
        else:
            summary += f"\n📄 Résumé Changes ({len(resume_changes)}):\n"
        for chunk in resume_changes:
            summary += f"  🔹 {chunk}\n"
    
    if cover_changes:
        if COLORS_AVAILABLE:
            summary += f"\n{Fore.YELLOW}{Style.BRIGHT}📝 Cover Letter Changes ({len(cover_changes)}):{Style.RESET_ALL}\n"
        else:
            summary += f"\n📝 Cover Letter Changes ({len(cover_changes)}):\n"
        for chunk in cover_changes:
            summary += f"  🔹 {chunk}\n"
    
    if COLORS_AVAILABLE:
        summary += f"\n{Fore.WHITE}{Back.GREEN}{Style.BRIGHT} ✅ Total chunks modified: {len(changed_chunks)} {Style.RESET_ALL}\n"
    else:
        summary += f"\n✅ Total chunks modified: {len(changed_chunks)}\n"
    
    return summary


def show_diffs(quiet: bool = False) -> None:
    """Show diffs for the standard file locations."""
    
    # Standard file paths
    original_resume = "Baseline_Resume/Conner_Jordan_Software_Engineer llm_ready.tex"
    original_cover = "Basline_Cover_Letter/Conner_Jordan_Cover_Letter llm_ready.tex"
    
    # Look for tuned files in out/
    tuned_resume = None
    tuned_cover = None
    
    out_dir = Path("out")
    if out_dir.exists():
        for file in out_dir.glob("*.tuned.tex"):
            if "Software_Engineer" in file.name:
                tuned_resume = str(file)
            elif "Cover_Letter" in file.name:
                tuned_cover = str(file)
    
    if not tuned_resume or not tuned_cover:
        print("No tuned files found in out/. Run 'tex-tailor apply' first.")
        return
    
    # Check if original files exist
    if not Path(original_resume).exists() or not Path(original_cover).exists():
        print("Original files not found. Run 'tex-tailor init' first.")
        return
    
    if not quiet:
        print(f"Comparing:")
        print(f"  Original résumé: {original_resume}")
        print(f"  Tuned résumé: {tuned_resume}")
        print(f"  Original cover: {original_cover}")
        print(f"  Tuned cover: {tuned_cover}")
    
    # Generate diffs
    diffs = get_all_chunk_diffs(original_resume, original_cover, tuned_resume, tuned_cover)
    
    # Show summary first
    summary = create_diff_summary(diffs)
    print(summary)
    
    # Show detailed diffs only if not quiet
    if not quiet and diffs:
        if COLORS_AVAILABLE:
            print(f"\n{Fore.WHITE}{Back.BLUE}{Style.BRIGHT} 🔍 DETAILED DIFFS {Style.RESET_ALL}\n")
        else:
            print(f"\n🔍 DETAILED DIFFS\n")
        
        for diff in diffs:
            print(diff)
    
    print()  # Final newline


def diff_specific_files(original_resume: str, original_cover: str,
                       tuned_resume: str, tuned_cover: str) -> None:
    """Show diffs for specific file paths."""
    
    print(f"Comparing:")
    print(f"  Original résumé: {original_resume}")
    print(f"  Tuned résumé: {tuned_resume}")
    print(f"  Original cover: {original_cover}")
    print(f"  Tuned cover: {tuned_cover}")
    
    # Generate diffs
    diffs = get_all_chunk_diffs(original_resume, original_cover, tuned_resume, tuned_cover)
    
    # Show summary first
    summary = create_diff_summary(diffs)
    print(summary)
    
    # Show detailed diffs
    if diffs:
        if COLORS_AVAILABLE:
            print(f"\n{Fore.BLUE}{Style.BRIGHT}DETAILED DIFFS{Style.RESET_ALL}\n")
        else:
            print(f"\nDETAILED DIFFS\n")
        
        for diff in diffs:
            print(diff)
    
    print()  # Final newline


def export_diff_report(output_file: str) -> None:
    """Export diff report to a file (without colors)."""
    
    # Temporarily disable colors for file output
    global COLORS_AVAILABLE
    colors_backup = COLORS_AVAILABLE
    COLORS_AVAILABLE = False
    
    try:
        # Standard file paths
        original_resume = "Baseline_Resume/Conner_Jordan_Software_Engineer llm_ready.tex"
        original_cover = "Basline_Cover_Letter/Conner_Jordan_Cover_Letter llm_ready.tex"
        
        # Look for tuned files in out/
        tuned_resume = None
        tuned_cover = None
        
        out_dir = Path("out")
        if out_dir.exists():
            for file in out_dir.glob("*.tuned.tex"):
                if "Software_Engineer" in file.name:
                    tuned_resume = str(file)
                elif "Cover_Letter" in file.name:
                    tuned_cover = str(file)
        
        if not tuned_resume or not tuned_cover:
            raise RuntimeError("No tuned files found in out/. Run 'tex-tailor apply' first.")
        
        # Generate diffs
        diffs = get_all_chunk_diffs(original_resume, original_cover, tuned_resume, tuned_cover)
        
        # Create report
        report_lines = [
            "LaTeX Tailor Diff Report",
            "=" * 50,
            "",
            f"Generated: {Path().cwd()}",
            f"Original résumé: {original_resume}",
            f"Tuned résumé: {tuned_resume}",
            f"Original cover: {original_cover}",
            f"Tuned cover: {tuned_cover}",
            ""
        ]
        
        # Add summary
        summary = create_diff_summary(diffs)
        report_lines.append(summary)
        
        # Add detailed diffs
        if diffs:
            report_lines.extend(["", "DETAILED DIFFS", ""])
            for diff in diffs:
                report_lines.append(diff)
        
        # Write to file
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write('\n'.join(report_lines))
        
        print(f"Diff report exported to: {output_file}")
    
    finally:
        # Restore color setting
        COLORS_AVAILABLE = colors_backup