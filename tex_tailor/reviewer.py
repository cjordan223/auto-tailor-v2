"""
Review module for tex-tailor - Generate LLM overviews and structured diffs.

This module provides functionality to:
1. Read edits.json and generate LLM-powered overviews of changes
2. Create structured, programmatic diffs
3. Output results in multiple formats (text, JSON)
"""
import json
import os
import sys
from pathlib import Path
from typing import Dict, List, Any, Optional
import click

from .config import get_default_paths, get_model_for_provider
from .proposer import get_provider
from .differ import get_all_chunk_diffs


def generate_review(format: str = 'text', provider: Optional[str] = None, job_description_path: Optional[str] = None):
    """Generate a comprehensive review of recent edits."""
    try:
        default_paths = get_default_paths()
        edits_path = Path(default_paths["edits"])

        if not edits_path.exists():
            click.echo("❌ No edits.json found. Run workflow first.", err=True)
            sys.exit(1)

        # Read edits data
        with open(edits_path, 'r', encoding='utf-8') as f:
            edits_data = json.load(f)

        # Read job description if available
        job_description = ""
        if job_description_path and Path(job_description_path).exists():
            try:
                with open(job_description_path, 'r', encoding='utf-8') as f:
                    job_description = f.read().strip()
            except Exception as e:
                click.echo(f"⚠️  Could not read job description: {e}")

        # Generate LLM overview
        overview = generate_llm_overview(edits_data, provider, job_description)

        # Get structured diffs
        structured_diffs = get_structured_diffs()

        # Output results
        if format == 'json':
            output_json_review(overview, structured_diffs, edits_data)
        else:
            output_text_review(overview, structured_diffs, edits_data)

    except Exception as e:
        click.echo(f"❌ Review generation failed: {e}", err=True)
        sys.exit(1)


def generate_llm_overview(edits_data: Dict[str, Any], provider: Optional[str] = None, job_description: str = "") -> str:
    """Generate an LLM-powered overview of the edits."""

    # Use provider from environment variable (set by backend) or fallback to auto-detection
    if not provider:
        provider = os.getenv("PROVIDER")
        if not provider:
            # Fallback to auto-detection if not set
            if os.getenv("GEMINI_API_KEY"):
                provider = "gemini"
            elif os.getenv("OPENAI_API_KEY"):
                provider = "openai"
            else:
                provider = "ollama"

    try:
        # Create LLM instance
        model = get_model_for_provider(provider)
        llm = get_provider(provider, model)

        # Prepare analysis prompt
        prompt = create_analysis_prompt(edits_data, job_description)

        # Generate overview
        click.echo("🧠 Generating LLM overview of changes...")
        overview = llm.generate(
            "You are a helpful assistant analyzing resume edits.", prompt)

        # Try to parse JSON response and extract text content
        try:
            parsed = json.loads(overview)
            if isinstance(parsed, list) and len(parsed) > 0:
                # Handle case where LLM returns a list
                return parsed[0]
            elif isinstance(parsed, dict):
                # Extract text from nested analysis structure
                analysis = parsed.get('analysis', parsed)
                if isinstance(analysis, dict):
                    # Combine job explanation and game plan sections
                    parts = []
                    if analysis.get('job_explanation'):
                        parts.append(analysis['job_explanation'])
                    if analysis.get('game_plan_and_strategic_changes'):
                        parts.append(
                            analysis['game_plan_and_strategic_changes'])
                    if parts:
                        return '\n\n'.join(parts)
                    # Fallback to old structure
                    if analysis.get('overall_strategy'):
                        return analysis['overall_strategy']
                    elif analysis.get('key_changes'):
                        return analysis['key_changes']
        except (json.JSONDecodeError, KeyError, TypeError):
            pass

        # Return original if parsing fails
        return overview

    except Exception as e:
        click.echo(f"⚠️  Could not generate LLM overview: {e}")
        return "LLM overview unavailable - using edits data only."


def create_analysis_prompt(edits_data: Dict[str, Any], job_description: str = "") -> str:
    """Create a prompt for LLM analysis of edits."""

    # Count edits by type
    summary_changes = 1 if edits_data.get("summary") else 0
    skill_changes = len(edits_data.get("skills", {}))
    cover_changes = len(edits_data.get(
        "cover_letter", {}).get("paragraphs", []))
    suggested_additions = len(edits_data.get("suggested_additions", []))

    # Extract key changes for context
    skills_modified = []
    if edits_data.get("skills"):
        for skill_name, skill_data in edits_data["skills"].items():
            if skill_data.get("replace") and skill_data["replace"] != "null":
                skills_modified.append(skill_name)

    cover_paragraphs_modified = []
    if edits_data.get("cover_letter", {}).get("paragraphs"):
        for i, paragraph in enumerate(edits_data["cover_letter"]["paragraphs"], 1):
            if paragraph and paragraph != "null":
                cover_paragraphs_modified.append(f"Paragraph {i}")

    prompt = f"""You are an expert resume and job application analyst. Analyze the following job description and resume customization changes to provide a comprehensive overview.

JOB DESCRIPTION:
{job_description if job_description else "Job description not available"}

RESUME CUSTOMIZATION CHANGES:
{json.dumps(edits_data, indent=2)}

ANALYSIS REQUEST:
Write a comprehensive overview (2-3 paragraphs) that includes:

1. **JOB EXPLANATION** (1 paragraph):
   - Explain what this job is about in simple, approachable terms
   - Describe what the role requires and what kind of person would be successful
   - Make it conversational and easy to understand

2. **GAME PLAN & STRATEGIC CHANGES** (1-2 paragraphs):
   - Explain the overall strategy used to customize the resume for this specific job
   - Describe the key changes made and WHY they were strategically chosen
   - Connect the changes to the job requirements
   - Explain how these changes improve the candidate's fit for the role

KEY CHANGES MADE:
- Summary updated: {'Yes' if summary_changes else 'No'}
- Skills sections modified: {', '.join(skills_modified) if skills_modified else 'None'}
- Cover letter paragraphs updated: {', '.join(cover_paragraphs_modified) if cover_paragraphs_modified else 'None'}
- Suggested additions: {suggested_additions} new skills/keywords

CRITICAL REQUIREMENTS:
- Write in a conversational, helpful tone
- Make the job explanation accessible to someone unfamiliar with the field
- Explain the "why" behind the changes, not just what was changed
- Keep it informative but not overly technical
- Write as plain text, NOT JSON
- Aim for 2-3 paragraphs total
"""

    return prompt


def get_structured_diffs() -> List[Dict[str, Any]]:
    """Get structured diff data for programmatic use."""
    try:
        # Use existing differ functionality but format for structured output
        default_paths = get_default_paths()
        original_resume = default_paths["baseline_resume"]
        original_cover = default_paths["baseline_cover"]

        # Get diffs using the available function
        diff_text = get_all_chunk_diffs(
            original_resume, original_cover, quiet=True)

        # Parse the diff text to extract structured data
        structured_diffs = []

        # Simple parsing of diff output - this is a basic implementation
        # In a production system, you'd want more robust parsing
        lines = diff_text.split('\n')
        current_chunk = None

        for line in lines:
            if line.startswith('🔧 CHUNK:'):
                # Extract chunk name
                chunk_name = line.split('CHUNK:')[1].strip()
                current_chunk = {
                    "chunk_name": chunk_name,
                    "type": get_chunk_type(chunk_name),
                    "changes": {
                        "words_removed": 0,
                        "words_added": 0,
                        "net_change": 0
                    },
                    "content": {
                        "before": "",
                        "after": "",
                        "diff_text": ""
                    }
                }
                structured_diffs.append(current_chunk)
            elif line.startswith('📊 CHANGES:') and current_chunk:
                # Extract change statistics
                try:
                    changes_part = line.split('CHANGES:')[1].strip()
                    # Parse "X words, +Y words" format
                    import re
                    match = re.search(
                        r'(\d+)\s+words,\s*\+(\d+)\s+words', changes_part)
                    if match:
                        words_removed = int(match.group(1))
                        words_added = int(match.group(2))
                        current_chunk["changes"]["words_removed"] = words_removed
                        current_chunk["changes"]["words_added"] = words_added
                        current_chunk["changes"]["net_change"] = words_added - \
                            words_removed
                except:
                    pass

        return structured_diffs

    except Exception as e:
        click.echo(f"⚠️  Could not generate structured diffs: {e}")
        return []


def get_chunk_type(chunk_name: str) -> str:
    """Classify chunk type for better organization."""
    chunk_lower = chunk_name.lower()

    if 'summary' in chunk_lower:
        return 'summary'
    elif 'skill' in chunk_lower:
        return 'skills'
    elif 'cover' in chunk_lower:
        return 'cover_letter'
    elif 'experience' in chunk_lower:
        return 'experience'
    elif 'education' in chunk_lower:
        return 'education'
    else:
        return 'other'


def output_json_review(overview: str, structured_diffs: List[Dict[str, Any]], edits_data: Dict[str, Any]):
    """Output review in JSON format."""

    review_data = {
        "overview": overview,
        "statistics": {
            "total_chunks_modified": len(structured_diffs),
            "summary_changes": 1 if edits_data.get("summary") else 0,
            "skills_sections_updated": len(edits_data.get("skills", {})),
            "cover_letter_paragraphs": len(edits_data.get("cover_letter", {}).get("paragraphs", [])),
            "suggested_additions": len(edits_data.get("suggested_additions", []))
        },
        "structured_diffs": structured_diffs,
        "raw_edits": edits_data,
        "generated_at": "2025-08-21T20:00:00Z"  # Would use actual timestamp
    }

    click.echo(json.dumps(review_data, indent=2, ensure_ascii=False))


def output_text_review(overview: str, structured_diffs: List[Dict[str, Any]], edits_data: Dict[str, Any]):
    """Output review in human-readable text format."""

    click.echo("=" * 60)
    click.echo("📋 TEX-TAILOR REVIEW SUMMARY")
    click.echo("=" * 60)

    # Statistics
    click.echo(f"\n📊 CHANGE STATISTICS")
    click.echo(f"• Total chunks modified: {len(structured_diffs)}")
    click.echo(f"• Summary changes: {1 if edits_data.get('summary') else 0}")
    click.echo(
        f"• Skills sections updated: {len(edits_data.get('skills', {}))}")
    click.echo(
        f"• Cover letter paragraphs: {len(edits_data.get('cover_letter', {}).get('paragraphs', []))}")
    click.echo(
        f"• Suggested additions: {len(edits_data.get('suggested_additions', []))}")

    # LLM Overview
    click.echo(f"\n🧠 LLM ANALYSIS OVERVIEW")
    click.echo("-" * 40)
    click.echo(overview)

    # Structured Diffs
    click.echo(f"\n🔍 DETAILED CHANGES")
    click.echo("-" * 40)

    if not structured_diffs:
        click.echo("No changes detected.")
        return

    # Group by type
    by_type = {}
    for diff in structured_diffs:
        chunk_type = diff['type']
        if chunk_type not in by_type:
            by_type[chunk_type] = []
        by_type[chunk_type].append(diff)

    for chunk_type, diffs in by_type.items():
        click.echo(f"\n🔧 {chunk_type.upper()} CHANGES:")

        for diff in diffs:
            changes = diff['changes']
            click.echo(f"   • {diff['chunk_name']}")
            click.echo(
                f"     Words: -{changes['words_removed']} +{changes['words_added']} (net: {changes['net_change']:+d})")

            # Show content preview
            if diff['content']['after']:
                preview = diff['content']['after'][:100]
                if len(preview) == 100:
                    preview += "..."
                click.echo(f"     Preview: {preview}")

    # Suggested Additions
    if edits_data.get('suggested_additions'):
        click.echo(f"\n💡 SUGGESTED ADDITIONS")
        click.echo("-" * 40)
        for addition in edits_data['suggested_additions']:
            click.echo(f"• {addition.get('term', 'Unknown')}")
            if addition.get('why'):
                click.echo(f"  Reason: {addition['why']}")

    click.echo("\n" + "=" * 60)
