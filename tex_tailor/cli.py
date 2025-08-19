"""
Main CLI interface for tex-tailor.
"""
import click
import os
import sys
from pathlib import Path
from typing import Optional

# Load .env file if it exists
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

from .markers import init_files
from .extractor import extract_to_json
from .proposer import propose_and_save_edits
from .patcher import apply_edits_with_validation
from .differ import show_diffs, diff_specific_files, export_diff_report


@click.group()
@click.version_option(version="1.0.0")
def main():
    """Deterministic LaTeX Tailor - Tailor résumés and cover letters to job descriptions."""
    pass


@main.command()
def init():
    """Initialize baseline files with LLM markers and reorder résumé sections."""
    try:
        init_files()
        click.echo("✓ Initialization complete")
        click.echo("Files created with LOCK/CHUNK markers and résumé sections reordered.")
    except Exception as e:
        click.echo(f"Error during initialization: {e}", err=True)
        sys.exit(1)


@main.command()
@click.option("--resume", required=True, help="Path to résumé LLM-ready file")
@click.option("--cover", required=True, help="Path to cover letter LLM-ready file")
@click.option("--out", default="out/base_text.json", help="Output JSON file path")
def extract(resume: str, cover: str, out: str):
    """Extract editable text from marked LaTeX files."""
    
    # Validate input files
    if not Path(resume).exists():
        click.echo(f"Error: Resume file not found: {resume}", err=True)
        sys.exit(1)
    
    if not Path(cover).exists():
        click.echo(f"Error: Cover letter file not found: {cover}", err=True)
        sys.exit(1)
    
    # Ensure output directory exists
    out_path = Path(out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    
    try:
        extract_to_json(resume, cover, out)
        click.echo("✓ Text extraction complete")
    except Exception as e:
        click.echo(f"Error during extraction: {e}", err=True)
        sys.exit(1)


@main.command()
@click.option("--jd", required=True, help="Path to job description file")
@click.option("--provider", default="ollama", type=click.Choice(["ollama", "gemini"]), 
              help="LLM provider to use")
@click.option("--model", help="Model name (optional, uses env defaults)")
@click.option("--base-text", default="out/base_text.json", help="Path to base text JSON")
@click.option("--out", default="out/edits.json", help="Output edits JSON file")
def propose(jd: str, provider: str, model: Optional[str], base_text: str, out: str):
    """Propose edits based on job description using LLM."""
    
    # Validate input files
    if not Path(jd).exists():
        click.echo(f"Error: Job description file not found: {jd}", err=True)
        sys.exit(1)
    
    if not Path(base_text).exists():
        click.echo(f"Error: Base text file not found: {base_text}", err=True)
        click.echo("Run 'tex-tailor extract' first.", err=True)
        sys.exit(1)
    
    # Check environment variables for provider
    if provider == "ollama":
        base_url = os.getenv("OLLAMA_BASE_URL", "http://127.0.0.1:11434")
        default_model = os.getenv("OLLAMA_MODEL", "qwen2.5:14b-instruct")
        click.echo(f"Using Ollama: {base_url}")
        click.echo(f"Model: {model or default_model}")
    elif provider == "gemini":
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            click.echo("Error: GEMINI_API_KEY environment variable required for Gemini", err=True)
            sys.exit(1)
        default_model = os.getenv("GEMINI_MODEL", "gemini-1.5-pro")
        click.echo(f"Using Gemini API")
        click.echo(f"Model: {model or default_model}")
    
    # Ensure output directory exists
    out_path = Path(out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    
    try:
        propose_and_save_edits(jd, base_text, out, provider, model)
        click.echo("✓ Edit proposal complete")
    except Exception as e:
        click.echo(f"Error during proposal: {e}", err=True)
        sys.exit(1)


@main.command()
@click.option("--edits", default="out/edits.json", help="Path to edits JSON file")
@click.option("--resume", default="Baseline_Resume/Conner_Jordan_Software_Engineer llm_ready.tex",
              help="Path to original résumé LLM-ready file")
@click.option("--cover", default="Basline_Cover_Letter/Conner_Jordan_Cover_Letter llm_ready.tex",
              help="Path to original cover letter LLM-ready file")
def apply(edits: str, resume: str, cover: str):
    """Validate and apply edits to create tuned LaTeX files."""
    
    # Validate input files
    if not Path(edits).exists():
        click.echo(f"Error: Edits file not found: {edits}", err=True)
        click.echo("Run 'tex-tailor propose' first.", err=True)
        sys.exit(1)
    
    if not Path(resume).exists():
        click.echo(f"Error: Resume file not found: {resume}", err=True)
        sys.exit(1)
    
    if not Path(cover).exists():
        click.echo(f"Error: Cover letter file not found: {cover}", err=True)
        sys.exit(1)
    
    # Ensure output directory exists
    Path("out").mkdir(exist_ok=True)
    
    try:
        apply_edits_with_validation(resume, cover, edits)
        click.echo("✓ Edits applied successfully")
    except Exception as e:
        click.echo(f"Error applying edits: {e}", err=True)
        sys.exit(1)


@main.command()
@click.option("--original-resume", 
              default="Baseline_Resume/Conner_Jordan_Software_Engineer llm_ready.tex",
              help="Path to original résumé file")
@click.option("--original-cover", 
              default="Basline_Cover_Letter/Conner_Jordan_Cover_Letter llm_ready.tex",
              help="Path to original cover letter file")
@click.option("--tuned-resume", help="Path to tuned résumé file (auto-detected if not specified)")
@click.option("--tuned-cover", help="Path to tuned cover letter file (auto-detected if not specified)")
@click.option("--export", help="Export diff report to file")
def diff(original_resume: str, original_cover: str, 
         tuned_resume: Optional[str], tuned_cover: Optional[str],
         export: Optional[str]):
    """Show colorized word-diffs of chunk changes."""
    
    if tuned_resume and tuned_cover:
        # Use specified files
        if not Path(tuned_resume).exists():
            click.echo(f"Error: Tuned résumé file not found: {tuned_resume}", err=True)
            sys.exit(1)
        
        if not Path(tuned_cover).exists():
            click.echo(f"Error: Tuned cover letter file not found: {tuned_cover}", err=True)
            sys.exit(1)
        
        diff_specific_files(original_resume, original_cover, tuned_resume, tuned_cover)
    else:
        # Use auto-detection
        show_diffs()
    
    # Export report if requested
    if export:
        try:
            export_diff_report(export)
        except Exception as e:
            click.echo(f"Error exporting diff report: {e}", err=True)


@main.command()
@click.option("--out-dir", default="out", help="Output directory for PDFs")
def render(out_dir: str):
    """Render tuned LaTeX files to PDF using latexmk."""
    
    out_path = Path(out_dir)
    if not out_path.exists():
        click.echo(f"Error: Output directory not found: {out_dir}", err=True)
        sys.exit(1)
    
    # Find tuned .tex files
    tex_files = list(out_path.glob("*.tuned.tex"))
    
    if not tex_files:
        click.echo("No tuned .tex files found in output directory.", err=True)
        click.echo("Run 'tex-tailor apply' first.", err=True)
        sys.exit(1)
    
    # Check if latexmk is available
    import subprocess
    
    try:
        subprocess.run(["latexmk", "--version"], capture_output=True, check=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        click.echo("Error: latexmk not found. Please install LaTeX distribution.", err=True)
        sys.exit(1)
    
    click.echo(f"Found {len(tex_files)} tuned LaTeX files")
    
    for tex_file in tex_files:
        click.echo(f"Rendering: {tex_file.name}")
        
        try:
            # Run latexmk to generate PDF in the same directory as the .tex file
            result = subprocess.run([
                "latexmk", "-pdf", tex_file.name
            ], capture_output=True, text=True, cwd=out_path)
            
            if result.returncode == 0:
                pdf_name = tex_file.stem + ".pdf"
                click.echo(f"✓ Generated: {pdf_name}")
            else:
                click.echo(f"✗ Error rendering {tex_file.name}:")
                click.echo(result.stderr, err=True)
                
        except Exception as e:
            click.echo(f"✗ Error rendering {tex_file.name}: {e}", err=True)
    
    # Clean up auxiliary files
    aux_patterns = ["*.aux", "*.log", "*.fls", "*.fdb_latexmk", "*.out", "*.toc"]
    for pattern in aux_patterns:
        for aux_file in out_path.glob(pattern):
            aux_file.unlink(missing_ok=True)
    
    click.echo("✓ Rendering complete")


@main.command()
def status():
    """Show status of tex-tailor workflow files."""
    
    click.echo("Tex-Tailor Status")
    click.echo("=" * 50)
    
    # Check initialization
    init_files = [
        "Baseline_Resume/Conner_Jordan_Software_Engineer llm_ready.tex",
        "Basline_Cover_Letter/Conner_Jordan_Cover_Letter llm_ready.tex"
    ]
    
    all_init = True
    click.echo("\n1. Initialization:")
    for file in init_files:
        if Path(file).exists():
            click.echo(f"   ✓ {file}")
        else:
            click.echo(f"   ✗ {file}")
            all_init = False
    
    if not all_init:
        click.echo("   → Run: tex-tailor init")
    
    # Check extraction
    base_text_file = "out/base_text.json"
    click.echo("\n2. Text Extraction:")
    if Path(base_text_file).exists():
        click.echo(f"   ✓ {base_text_file}")
    else:
        click.echo(f"   ✗ {base_text_file}")
        click.echo("   → Run: tex-tailor extract --resume ... --cover ...")
    
    # Check proposal
    edits_file = "out/edits.json"
    click.echo("\n3. Edit Proposal:")
    if Path(edits_file).exists():
        click.echo(f"   ✓ {edits_file}")
    else:
        click.echo(f"   ✗ {edits_file}")
        click.echo("   → Run: tex-tailor propose --jd job_description.txt")
    
    # Check application
    out_dir = Path("out")
    tuned_files = list(out_dir.glob("*.tuned.tex")) if out_dir.exists() else []
    click.echo("\n4. Edit Application:")
    if tuned_files:
        for file in tuned_files:
            click.echo(f"   ✓ {file}")
    else:
        click.echo("   ✗ No tuned .tex files found")
        click.echo("   → Run: tex-tailor apply --edits out/edits.json")
    
    # Check PDFs
    pdf_files = list(out_dir.glob("*.pdf")) if out_dir.exists() else []
    click.echo("\n5. PDF Rendering (Optional):")
    if pdf_files:
        for file in pdf_files:
            click.echo(f"   ✓ {file}")
    else:
        click.echo("   ✗ No PDF files found")
        click.echo("   → Run: tex-tailor render")
    
    # Environment check
    click.echo("\n6. Environment:")
    
    # Check Ollama
    ollama_url = os.getenv("OLLAMA_BASE_URL", "http://127.0.0.1:11434")
    ollama_model = os.getenv("OLLAMA_MODEL", "qwen2.5:14b-instruct")
    click.echo(f"   Ollama URL: {ollama_url}")
    click.echo(f"   Ollama Model: {ollama_model}")
    
    # Check Gemini
    gemini_key = os.getenv("GEMINI_API_KEY")
    gemini_model = os.getenv("GEMINI_MODEL", "gemini-1.5-pro")
    if gemini_key:
        click.echo(f"   Gemini API Key: [SET]")
        click.echo(f"   Gemini Model: {gemini_model}")
    else:
        click.echo("   Gemini API Key: [NOT SET]")
    
    click.echo()


if __name__ == "__main__":
    main()