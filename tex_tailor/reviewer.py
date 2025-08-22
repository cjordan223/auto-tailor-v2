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
from .differ import get_diff_data


def generate_review(format: str = 'text', provider: Optional[str] = None):
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

        # Generate LLM overview
        overview = generate_llm_overview(edits_data, provider)

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


def generate_llm_overview(edits_data: Dict[str, Any], provider: Optional[str] = None) -> str:
    """Generate an LLM-powered overview of the edits."""

    # Auto-detect provider if not specified
    if not provider:
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
        prompt = create_analysis_prompt(edits_data)

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
                    # Just return the overall strategy if available, otherwise combine key points
                    if analysis.get('overall_strategy'):
                        return analysis['overall_strategy']
                    elif analysis.get('key_changes'):
                        return analysis['key_changes']
                    else:
                        # Combine multiple sections into one concise summary
                        parts = []
                        if analysis.get('overall_strategy'):
                            parts.append(analysis['overall_strategy'])
                        if analysis.get('key_changes'):
                            parts.append(analysis['key_changes'])
                        if parts:
                            return ' '.join(parts)
        except (json.JSONDecodeError, KeyError, TypeError):
            pass

        # Return original if parsing fails
        return overview

    except Exception as e:
        click.echo(f"⚠️  Could not generate LLM overview: {e}")
        return "LLM overview unavailable - using edits data only."


def create_analysis_prompt(edits_data: Dict[str, Any]) -> str:
    """Create a prompt for LLM analysis of edits."""

    # Count edits by type
    summary_changes = 1 if edits_data.get("summary") else 0
    skill_changes = len(edits_data.get("skills", {}))
    cover_changes = len(edits_data.get(
        "cover_letter", {}).get("paragraphs", []))
    suggested_additions = len(edits_data.get("suggested_additions", []))

    prompt = f"""Analyze the following resume/cover letter edits and provide a very brief, concise summary.

EDIT DATA:
{json.dumps(edits_data, indent=2)}

ANALYSIS REQUEST:
Write a very short summary (max 2-3 sentences total) covering:

1. Overall approach (1 sentence)
2. Key changes made (1-2 sentences)

STATISTICS:
- Summary changes: {summary_changes}
- Skills sections updated: {skill_changes}
- Cover letter paragraphs modified: {cover_changes}
- Suggested additions: {suggested_additions}

CRITICAL: 
- Write as plain text, NOT JSON
- Keep it extremely concise (max 3 sentences total)
- Focus only on the most important changes
- Use simple, clear language
"""

    return prompt


def get_structured_diffs() -> List[Dict[str, Any]]:
    """Get structured diff data for programmatic use."""
    try:
        # Use existing differ functionality but format for structured output
        diff_data = get_diff_data()

        structured_diffs = []

        for chunk_name, changes in diff_data.items():
            if changes['modified']:
                diff_entry = {
                    "chunk_name": chunk_name,
                    "type": get_chunk_type(chunk_name),
                    "changes": {
                        "words_removed": changes.get('words_removed', 0),
                        "words_added": changes.get('words_added', 0),
                        "net_change": changes.get('words_added', 0) - changes.get('words_removed', 0)
                    },
                    "content": {
                        "before": changes.get('before', ''),
                        "after": changes.get('after', ''),
                        "diff_text": changes.get('diff_display', '')
                    }
                }
                structured_diffs.append(diff_entry)

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
