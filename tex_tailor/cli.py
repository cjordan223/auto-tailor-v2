"""
Main CLI interface for tex-tailor.
"""
import click
import os
import sys
import subprocess
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
from .logger import WorkflowLogger, get_latest_log, show_latest_log
from .config import config, get_model_for_provider, get_default_paths


@click.group()
@click.version_option(version="1.0.0")
@click.option('--quiet', '-q', is_flag=True, help='Suppress verbose output')
@click.pass_context
def main(ctx, quiet):
    """Deterministic LaTeX Tailor - Tailor résumés and cover letters to job descriptions."""
    ctx.ensure_object(dict)
    ctx.obj['quiet'] = quiet


@main.command()
@click.pass_context
def init(ctx):
    """Initialize baseline files with LLM markers and reorder résumé sections."""
    try:
        quiet = ctx.obj.get('quiet', False) if ctx.obj else False
        init_files(quiet=quiet)
        click.echo("✓ Initialization complete")
        if not quiet:
            click.echo(
                "Files created with LOCK/CHUNK markers and résumé sections reordered.")
    except Exception as e:
        click.echo(f"Error during initialization: {e}", err=True)
        sys.exit(1)


@main.command()
@click.option("--resume", required=True, help="Path to résumé LLM-ready file")
@click.option("--cover", required=True, help="Path to cover letter LLM-ready file")
@click.option("--out", default=None, help="Output JSON file path")
@click.pass_context
def extract(ctx, resume: str, cover: str, out: Optional[str]):
    """Extract editable text from marked LaTeX files."""

    # Use default path if not specified
    if not out:
        out = get_default_paths()["base_text"]

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
        quiet = ctx.obj.get('quiet', False) if ctx.obj else False
        extract_to_json(resume, cover, out, quiet=quiet)
        click.echo("✓ Text extraction complete")
    except Exception as e:
        click.echo(f"Error during extraction: {e}", err=True)
        sys.exit(1)


@main.command()
@click.option("--jd", required=True, help="Path to job description file")
@click.option("--provider", type=click.Choice(["ollama", "gemini", "openai"]),
              help="LLM provider to use (optional, auto-detects if not specified)")
@click.option("--model", help="Model name (optional, uses env defaults)")
@click.option("--base-text", default=None, help="Path to base text JSON")
@click.option("--out", default=None, help="Output edits JSON file")
@click.pass_context
def propose(ctx, jd: str, provider: Optional[str], model: Optional[str], base_text: Optional[str], out: Optional[str]):
    """Propose edits based on job description using LLM."""

    # Use default paths if not specified
    if not base_text:
        base_text = get_default_paths()["base_text"]
    if not out:
        out = get_default_paths()["edits"]

    # Validate input files
    if not Path(jd).exists():
        click.echo(f"Error: Job description file not found: {jd}", err=True)
        sys.exit(1)

    if not Path(base_text).exists():
        click.echo(f"Error: Base text file not found: {base_text}", err=True)
        click.echo("Run 'tex-tailor extract' first.", err=True)
        sys.exit(1)

    # Determine provider if not specified
    if not provider:
        if os.getenv("OPENAI_API_KEY"):
            provider = "openai"
            click.echo("OPENAI_API_KEY found, using OpenAI provider.")
        elif os.getenv("GEMINI_API_KEY"):
            provider = "gemini"
            click.echo("GEMINI_API_KEY found, using Gemini provider.")
        else:
            provider = "ollama"
            click.echo("No API keys found, defaulting to Ollama provider.")

    # Get configuration for provider
    if provider == "ollama":
        api_config = config.apis
        default_model = get_model_for_provider("ollama")
        click.echo(f"Using Ollama: {api_config.ollama_base_url}")
        click.echo(f"Model: {model or default_model}")
    elif provider == "openai":
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            click.echo(
                "Error: OPENAI_API_KEY environment variable required for OpenAI", err=True)
            sys.exit(1)
        default_model = get_model_for_provider("openai")
        click.echo(f"Using OpenAI API")
        click.echo(f"Model: {model or default_model}")
    elif provider == "gemini":
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            click.echo(
                "Error: GEMINI_API_KEY environment variable required for Gemini", err=True)
            sys.exit(1)
        default_model = get_model_for_provider("gemini")
        click.echo(f"Using Gemini API")
        click.echo(f"Model: {model or default_model}")

    # Ensure output directory exists
    out_path = Path(out)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    try:
        quiet = ctx.obj.get('quiet', False) if ctx.obj else False
        propose_and_save_edits(jd, base_text, out, provider, model, quiet=quiet)
        click.echo("✓ Edit proposal complete")
    except Exception as e:
        click.echo(f"Error during proposal: {e}", err=True)
        sys.exit(1)


@main.command()
@click.option("--edits", default=None, help="Path to edits JSON file")
@click.option("--resume", default=None, help="Path to original résumé LLM-ready file")
@click.option("--cover", default=None, help="Path to original cover letter LLM-ready file")
@click.pass_context
def apply(ctx, edits: Optional[str], resume: Optional[str], cover: Optional[str]):
    """Validate and apply edits to create tuned LaTeX files."""

    # Use default paths if not specified
    default_paths = get_default_paths()
    if not edits:
        edits = default_paths["edits"]
    if not resume:
        resume = default_paths["baseline_resume"]
    if not cover:
        cover = default_paths["baseline_cover"]
    
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
    Path(config.paths.output_dir).mkdir(exist_ok=True)

    try:
        quiet = ctx.obj.get('quiet', False) if ctx.obj else False
        apply_edits_with_validation(resume, cover, edits, quiet=quiet)
        click.echo("✓ Edits applied successfully")
    except Exception as e:
        click.echo(f"Error applying edits: {e}", err=True)
        sys.exit(1)


@main.command()
@click.option("--original-resume", default=None, help="Path to original résumé file")
@click.option("--original-cover", default=None, help="Path to original cover letter file")
@click.option("--tuned-resume", help="Path to tuned résumé file (auto-detected if not specified)")
@click.option("--tuned-cover", help="Path to tuned cover letter file (auto-detected if not specified)")
@click.option("--export", help="Export diff report to file")
@click.pass_context
def diff(ctx, original_resume: Optional[str], original_cover: Optional[str],
         tuned_resume: Optional[str], tuned_cover: Optional[str],
         export: Optional[str]):
    """Show colorized word-diffs of chunk changes."""

    # Use default paths if not specified
    default_paths = get_default_paths()
    if not original_resume:
        original_resume = default_paths["baseline_resume"]
    if not original_cover:
        original_cover = default_paths["baseline_cover"]
    
    if tuned_resume and tuned_cover:
        # Use specified files
        if not Path(tuned_resume).exists():
            click.echo(
                f"Error: Tuned résumé file not found: {tuned_resume}", err=True)
            sys.exit(1)

        if not Path(tuned_cover).exists():
            click.echo(
                f"Error: Tuned cover letter file not found: {tuned_cover}", err=True)
            sys.exit(1)

        diff_specific_files(original_resume, original_cover,
                            tuned_resume, tuned_cover)
    else:
        # Use auto-detection
        quiet = ctx.obj.get('quiet', False) if ctx.obj else False
        show_diffs(quiet=quiet)

    # Export report if requested
    if export:
        try:
            export_diff_report(export)
        except Exception as e:
            click.echo(f"Error exporting diff report: {e}", err=True)


@main.command()
@click.option("--out-dir", default=None, help="Output directory for PDFs")
def render(out_dir: Optional[str]):
    """Render tuned LaTeX files to PDF using latexmk."""

    if not out_dir:
        out_dir = config.paths.output_dir
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
        subprocess.run(["latexmk", "--version"],
                       capture_output=True, check=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        click.echo(
            "Error: latexmk not found. Please install LaTeX distribution.", err=True)
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
    aux_patterns = ["*.aux", "*.log", "*.fls",
                    "*.fdb_latexmk", "*.out", "*.toc"]
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
    default_paths = get_default_paths()
    init_files = [
        default_paths["baseline_resume"],
        default_paths["baseline_cover"]
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
    base_text_file = default_paths["base_text"]
    click.echo("\n2. Text Extraction:")
    if Path(base_text_file).exists():
        click.echo(f"   ✓ {base_text_file}")
    else:
        click.echo(f"   ✗ {base_text_file}")
        click.echo("   → Run: tex-tailor extract --resume ... --cover ...")

    # Check proposal
    edits_file = default_paths["edits"]
    click.echo("\n3. Edit Proposal:")
    if Path(edits_file).exists():
        click.echo(f"   ✓ {edits_file}")
    else:
        click.echo(f"   ✗ {edits_file}")
        click.echo("   → Run: tex-tailor propose --jd job_description.txt")

    # Check application
    out_dir = Path(config.paths.output_dir)
    tuned_files = list(out_dir.glob("*.tuned.tex")) if out_dir.exists() else []
    click.echo("\n4. Edit Application:")
    if tuned_files:
        for file in tuned_files:
            click.echo(f"   ✓ {file}")
    else:
        click.echo("   ✗ No tuned .tex files found")
        click.echo(f"   → Run: tex-tailor apply --edits {default_paths['edits']}")

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
    click.echo(f"   Ollama URL: {config.apis.ollama_base_url}")
    click.echo(f"   Ollama Model: {get_model_for_provider('ollama')}")

    # Check OpenAI
    openai_key = os.getenv("OPENAI_API_KEY")
    if openai_key:
        click.echo(f"   OpenAI API Key: [SET]")
        click.echo(f"   OpenAI Model: {get_model_for_provider('openai')}")
    else:
        click.echo("   OpenAI API Key: [NOT SET]")

    # Check Gemini
    gemini_key = os.getenv("GEMINI_API_KEY")
    if gemini_key:
        click.echo(f"   Gemini API Key: [SET]")
        click.echo(f"   Gemini Model: {get_model_for_provider('gemini')}")
    else:
        click.echo("   Gemini API Key: [NOT SET]")

    click.echo()


@main.command()
@click.option("--out-dir", default=None, help="Directory containing the PDF files")
def open(out_dir: Optional[str]):
    """Open the generated PDF files in the default viewer."""

    if not out_dir:
        out_dir = config.paths.output_dir
    out_path = Path(out_dir)
    if not out_path.exists():
        click.echo(f"Error: Output directory not found: {out_dir}", err=True)
        sys.exit(1)

    pdf_files = list(out_path.glob("*.tuned.pdf"))

    if not pdf_files:
        click.echo("No tuned PDF files found in output directory.", err=True)
        click.echo("Run 'tex-tailor render' first.", err=True)
        sys.exit(1)

    click.echo(f"Opening {len(pdf_files)} PDF file(s) with Preview...")
    for pdf_file in pdf_files:
        try:
            if sys.platform == "darwin":
                # Force use of Preview on macOS to avoid Adobe Reader caching issues
                subprocess.run(["open", "-a", "Preview", str(pdf_file)], check=True)
            elif sys.platform == "linux":
                subprocess.run(["xdg-open", str(pdf_file)], check=True)
            elif sys.platform == "win32":
                subprocess.run(["start", str(pdf_file)], check=True, shell=True)
            else:
                click.echo(f"Unsupported platform: {sys.platform}")
                click.echo("Could not automatically open PDF files.")
                break
        except Exception as e:
            click.echo(f"Error opening {pdf_file}: {e}", err=True)


@main.command()
def log():
    """Show the most recent workflow log."""
    show_latest_log()


@main.command()
@click.option("--with-logging", is_flag=True, help="Run the workflow with logging enabled")
@click.argument("job_description", type=click.Path(exists=True))
def workflow(job_description: str, with_logging: bool):
    """Run the complete workflow with optional logging."""
    
    if with_logging:
        with WorkflowLogger():
            run_workflow_steps(job_description)
    else:
        run_workflow_steps(job_description)


def run_workflow_steps(job_description: str):
    """Run the complete workflow steps."""
    try:
        # Step 1: Initialize
        click.echo("🔄 Step 1: Initializing...")
        init_files()
        click.echo("✅ Initialization complete")
        
        # Step 2: Extract
        click.echo("🔄 Step 2: Extracting content...")
        default_paths = get_default_paths()
        resume_file = default_paths["baseline_resume"]
        cover_file = default_paths["baseline_cover"]
        extract_to_json(resume_file, cover_file, default_paths["base_text"])
        click.echo("✅ Text extraction complete")
        
        # Step 3: Propose edits
        click.echo("🔄 Step 3: Proposing edits...")
        propose_and_save_edits(job_description, default_paths["base_text"], default_paths["edits"], "auto")
        click.echo("✅ Edit proposal complete")
        
        # Step 4: Apply edits
        click.echo("🔄 Step 4: Applying edits...")
        apply_edits_with_validation(resume_file, cover_file, default_paths["edits"])
        click.echo("✅ Edits applied")
        
        # Step 5: Show diffs
        click.echo("🔄 Step 5: Showing differences...")
        show_diffs()
        
        # Step 6: Render PDFs
        click.echo("🔄 Step 6: Rendering PDFs...")
        render_pdfs(config.paths.output_dir)
        click.echo("✅ PDF rendering complete")
        
        click.echo("🎉 Workflow completed successfully!")
        
    except Exception as e:
        click.echo(f"❌ Workflow failed: {e}", err=True)
        sys.exit(1)


def render_pdfs(out_dir: str):
    """Render PDFs using latexmk."""
    out_path = Path(out_dir)
    if not out_path.exists():
        raise RuntimeError(f"Output directory not found: {out_dir}")
    
    tex_files = list(out_path.glob("*.tuned.tex"))
    if not tex_files:
        raise RuntimeError("No tuned .tex files found")
    
    for tex_file in tex_files:
        result = subprocess.run([
            "latexmk", "-pdf", tex_file.name
        ], capture_output=True, text=True, cwd=out_path)
        
        if result.returncode != 0:
            raise RuntimeError(f"PDF rendering failed for {tex_file.name}: {result.stderr}")


if __name__ == "__main__":
    main()
