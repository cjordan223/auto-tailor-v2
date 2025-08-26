"""
Main CLI interface for tex-tailor.

🚪 ENTRY POINT - This orchestrates the entire workflow
📍 Main commands: propose, patch, extract
📍 Workflow: CLI → Extractor → Proposer → Schema → Patcher
"""
import click
import os
import sys
import subprocess
from subprocess import TimeoutExpired
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
from .reviewer import generate_review
from .ollama_optimized import propose_edits_ollama_optimized, get_recommended_ollama_models
from .ollama_validation import validate_ollama_response, get_ollama_validation_summary


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
@click.option("--provider", type=click.Choice(["ollama", "gemini", "openai", "mistral", "groq"]),
              help="LLM provider to use (optional, auto-detects if not specified)")
@click.option("--model", help="Model name (optional, uses env defaults)")
@click.option("--personality", default="career_savvy_colleague", 
              help="Writing personality to use (optional, defaults to career_savvy_colleague)")
@click.option("--base-text", default=None, help="Path to base text JSON")
@click.option("--out", default=None, help="Output edits JSON file")
@click.pass_context
def propose(ctx, jd: str, provider: Optional[str], model: Optional[str], personality: str, base_text: Optional[str], out: Optional[str]):
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
        # Check for PROVIDER environment variable first (set by backend)
        provider = os.getenv("PROVIDER")
        if not provider:
            # Fallback to auto-detection if not set
            if os.getenv("OPENAI_API_KEY"):
                provider = "openai"
                click.echo("OPENAI_API_KEY found, using OpenAI provider.")
            elif os.getenv("GEMINI_API_KEY"):
                provider = "gemini"
                click.echo("GEMINI_API_KEY found, using Gemini provider.")
            elif os.getenv("MISTRAL_API_KEY"):
                provider = "mistral"
                click.echo("MISTRAL_API_KEY found, using Mistral provider.")
            elif os.getenv("GROQ_API_KEY"):
                provider = "groq"
                click.echo("GROQ_API_KEY found, using Groq provider.")
            else:
                provider = "ollama"
                click.echo("No API keys found, defaulting to Ollama provider.")
        else:
            click.echo(f"Using provider from environment: {provider}")

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
    elif provider == "mistral":
        api_key = os.getenv("MISTRAL_API_KEY")
        if not api_key:
            click.echo(
                "Error: MISTRAL_API_KEY environment variable required for Mistral", err=True)
            sys.exit(1)
        default_model = get_model_for_provider("mistral")
        click.echo(f"Using Mistral API")
        click.echo(f"Model: {model or default_model}")
    elif provider == "groq":
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            click.echo(
                "Error: GROQ_API_KEY environment variable required for Groq", err=True)
            sys.exit(1)
        default_model = get_model_for_provider("groq")
        click.echo(f"Using Groq API")
        click.echo(f"Model: {model or default_model}")

    # Ensure output directory exists
    out_path = Path(out)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    try:
        quiet = ctx.obj.get('quiet', False) if ctx.obj else False
        propose_and_save_edits(
            jd, base_text, out, provider, model, personality, quiet=quiet)
        click.echo("✓ Edit proposal complete")
    except Exception as e:
        click.echo(f"Error during proposal: {e}", err=True)
        sys.exit(1)


@main.command("propose-ollama")
@click.option("--jd", required=True, help="Path to job description file")
@click.option("--model", help="Ollama model name (optional, uses configured default)")
@click.option("--base-text", default=None, help="Path to base text JSON")
@click.option("--out", default=None, help="Output edits JSON file")
@click.option("--list-models", is_flag=True, help="List recommended Ollama models and exit")
@click.pass_context
def propose_ollama(ctx, jd: str, model: Optional[str], base_text: Optional[str], out: Optional[str], list_models: bool):
    """
    Propose edits using Ollama with optimized prompts and validation.
    
    This command uses a specialized workflow for local Ollama models that:
    - Uses model-specific prompts with aggressive company name reminders
    - Provides immediate feedback without expensive retry logic
    - Auto-fixes common local model issues (placeholders, JSON formatting)
    - Blocks resource-intensive models that freeze the system
    """
    
    if list_models:
        click.echo("🔧 Recommended Ollama Models:")
        click.echo()
        
        # Sort by priority first, then by recommendation status
        models = sorted(get_recommended_ollama_models(), 
                       key=lambda x: (x.get("priority", 99), not x.get("recommended", False)))
        
        for model_info in models:
            if model_info.get("recommended"):
                marker = "⭐"
            elif model_info["tier"] == "specialized":
                marker = "🎯"
            else:
                marker = "  "
            
            click.echo(f"{marker} {model_info['model']} ({model_info['tier']})")
            click.echo(f"     {model_info['description']}")
            click.echo()
        
        click.echo("💡 Install models with: ollama pull <model-name>")
        click.echo("🎯 Specialized models are trained specifically for resume tailoring")
        click.echo("⚠️  Avoid models in the 'blocked' tier - they may freeze your system")
        return

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

    # Load JD content for validation
    try:
        with open(jd, 'r') as f:
            jd_content = f.read()
    except Exception as e:
        click.echo(f"Error reading job description: {e}", err=True)
        sys.exit(1)

    # Load base text for validation
    try:
        import json
        with open(base_text, 'r') as f:
            base_text_data = json.load(f)
    except Exception as e:
        click.echo(f"Error reading base text: {e}", err=True)
        sys.exit(1)

    # Show model selection
    selected_model = model or config.providers.ollama.default_model
    click.echo(f"🔧 Ollama Optimized Mode")
    click.echo(f"Model: {selected_model}")
    click.echo(f"URL: {config.apis.ollama_base_url}")
    click.echo()

    # Ensure output directory exists
    out_path = Path(out)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    try:
        # Use Ollama-optimized workflow
        edits = propose_edits_ollama_optimized(jd, base_text, selected_model)
        
        # Use Ollama-specific validation
        with open(jd, 'r', encoding='utf-8') as f:
            jd_content = f.read()
        
        # Get raw response for validation (we'll need to modify propose_edits_ollama_optimized to return this)
        # For now, we'll do a quick validation
        _, warnings = validate_ollama_response(json.dumps(edits), jd_content, base_text_data)
        
        # Save edits
        with open(out, 'w', encoding='utf-8') as f:
            json.dump(edits, f, indent=2, ensure_ascii=False)
        
        click.echo(f"✅ Ollama edits saved to: {out}")
        click.echo()
        
        # Show summary
        summary = get_ollama_validation_summary(edits, warnings)
        click.echo("📊 Generation Summary:")
        click.echo(summary)
        
        # Show warnings if any
        if warnings:
            click.echo()
            click.echo("⚠️  Warnings:")
            for warning in warnings:
                click.echo(f"  • {warning}")
            click.echo()
            click.echo("💡 Tips:")
            click.echo("  • Try a higher-tier model for better results")
            click.echo("  • Ensure company name is clearly stated in job description")
            click.echo("  • Use 'propose-ollama --list-models' to see recommendations")
        
    except Exception as e:
        click.echo(f"❌ Ollama generation failed: {e}", err=True)
        click.echo()
        click.echo("🔧 Troubleshooting:")
        click.echo("  1. Check if Ollama is running: ollama serve")
        click.echo("  2. Verify model is installed: ollama list")
        click.echo("  3. Try a different model: --model qwen2.5:14b-instruct")
        click.echo("  4. Check model recommendations: propose-ollama --list-models")
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
                "latexmk", "-pdf", "-interaction=nonstopmode", "-halt-on-error", tex_file.name
            ], capture_output=True, text=True, cwd=out_path, timeout=60)

            if result.returncode == 0:
                pdf_name = tex_file.stem + ".pdf"
                click.echo(f"✓ Generated: {pdf_name}")
            else:
                click.echo(f"✗ Error rendering {tex_file.name}:")
                click.echo(result.stderr, err=True)
        except TimeoutExpired:
            click.echo(f"✗ Timeout rendering {tex_file.name} (LaTeX compilation took >60s)", err=True)

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
        click.echo(
            f"   → Run: tex-tailor apply --edits {default_paths['edits']}")

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
                subprocess.run(
                    ["open", "-a", "Preview", str(pdf_file)], check=True)
            elif sys.platform == "linux":
                subprocess.run(["xdg-open", str(pdf_file)], check=True)
            elif sys.platform == "win32":
                subprocess.run(["start", str(pdf_file)],
                               check=True, shell=True)
            else:
                click.echo(f"Unsupported platform: {sys.platform}")
                click.echo("Could not automatically open PDF files.")
                break
        except Exception as e:
            click.echo(f"Error opening {pdf_file}: {e}", err=True)


@main.command()
@click.option("--job-id", required=True, help="Job ID for the files")
@click.option("--file-type", required=True, type=click.Choice(["resume", "cover-letter"]), help="Type of file to recompile")
@click.option("--content", required=True, help="LaTeX content to compile")
@click.option("--temp-dir", required=True, help="Temporary directory for job files")
def recompile(job_id: str, file_type: str, content: str, temp_dir: str):
    """Recompile LaTeX content to PDF for a specific job."""
    try:
        from pathlib import Path
        import subprocess

        # Create job directory if it doesn't exist
        job_dir = Path(temp_dir) / job_id
        job_dir.mkdir(parents=True, exist_ok=True)

        # Determine file names based on type
        if file_type == "resume":
            tex_filename = "Conner_Jordan_Software_Engineer.tuned.tex"
            pdf_filename = "Conner_Jordan_Software_Engineer.tuned.pdf"
        else:  # cover-letter
            tex_filename = "Conner_Jordan_Cover_Letter.tuned.tex"
            pdf_filename = "Conner_Jordan_Cover_Letter.tuned.pdf"

        # Write the LaTeX content to file
        tex_file = job_dir / tex_filename
        tex_file.write_text(content, encoding='utf-8')

        # Compile to PDF using latexmk
        try:
            result = subprocess.run([
                "latexmk", "-pdf", "-interaction=nonstopmode", "-halt-on-error", tex_filename
            ], capture_output=True, text=True, cwd=job_dir, timeout=60)

            if result.returncode == 0:
                click.echo(f"✓ Successfully compiled {file_type} to PDF")
                # Clean up auxiliary files
                aux_patterns = ["*.aux", "*.log", "*.fls",
                                "*.fdb_latexmk", "*.out", "*.toc"]
                for pattern in aux_patterns:
                    for aux_file in job_dir.glob(pattern):
                        aux_file.unlink(missing_ok=True)
            else:
                click.echo(f"✗ Compilation failed: {result.stderr}", err=True)
                sys.exit(1)
        except TimeoutExpired:
            click.echo(f"✗ PDF compilation timed out for {file_type} (LaTeX compilation took >60s)", err=True)
            sys.exit(1)

    except Exception as e:
        click.echo(f"Error during recompilation: {e}", err=True)
        sys.exit(1)


@main.command()
def log():
    """Show the most recent workflow log."""
    show_latest_log()


@main.command()
@click.option("--format", "-f", default="json", type=click.Choice(["text", "json"]), help="Output format")
@click.option("--provider", "-p", type=click.Choice(["ollama", "openai", "gemini"]), help="LLM provider")
@click.option("--job-description", "-jd", type=click.Path(exists=True), help="Path to job description file")
def review(format: str, provider: Optional[str], job_description: Optional[str]):
    """Generate a comprehensive review of recent edits."""
    generate_review(format, provider, job_description)


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
        # Use provider from environment variable (set by backend)
        provider = os.getenv("PROVIDER")
        model = os.getenv("MODEL")
        personality = os.getenv("PERSONALITY", "career_savvy_colleague")
        if not provider:
            # Fallback to auto-detection if not set
            if os.getenv("OPENAI_API_KEY"):
                provider = "openai"
                click.echo("OPENAI_API_KEY found, using OpenAI provider.")
            elif os.getenv("GEMINI_API_KEY"):
                provider = "gemini"
                click.echo("GEMINI_API_KEY found, using Gemini provider.")
            elif os.getenv("MISTRAL_API_KEY"):
                provider = "mistral"
                click.echo("MISTRAL_API_KEY found, using Mistral provider.")
            elif os.getenv("GROQ_API_KEY"):
                provider = "groq"
                click.echo("GROQ_API_KEY found, using Groq provider.")
            else:
                provider = "ollama"
                click.echo("No API keys found, defaulting to Ollama provider.")
        else:
            click.echo(f"Using provider: {provider}")
            if model:
                click.echo(f"Using model: {model}")

        # Use Ollama-optimized workflow for specific models
        if provider == "ollama" and model and model in ["resume-editor:latest", "qwen2.5:14b-instruct", "mixtral:latest"]:
            click.echo(f"🔧 Using Ollama-optimized workflow for {model}")
            try:
                from .ollama_optimized import propose_edits_ollama_optimized
                import json
                
                # Generate edits with Ollama optimization (simplified - no extra validation)
                edits = propose_edits_ollama_optimized(
                    job_description, default_paths["base_text"], model)
                
                # Save edits directly
                with open(default_paths["edits"], 'w') as f:
                    json.dump(edits, f, indent=2, ensure_ascii=False)
                
                click.echo("✅ Ollama-optimized edits generated")
                
            except Exception as e:
                click.echo(f"⚠️ Ollama optimization failed, falling back to standard workflow: {e}")
                # Fallback to standard workflow
                propose_and_save_edits(
                    job_description, default_paths["base_text"], default_paths["edits"], provider, model, personality)
        else:
            # Use standard workflow
            propose_and_save_edits(
                job_description, default_paths["base_text"], default_paths["edits"], provider, model, personality)
        
        click.echo("✅ Edit proposal complete")

        # Step 4: Apply edits
        click.echo("🔄 Step 4: Applying edits...")
        apply_edits_with_validation(
            resume_file, cover_file, default_paths["edits"])
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
        try:
            result = subprocess.run([
                "latexmk", "-pdf", "-interaction=nonstopmode", "-halt-on-error", tex_file.name
            ], capture_output=True, text=True, cwd=out_path, timeout=60)

            if result.returncode != 0:
                raise RuntimeError(
                    f"PDF rendering failed for {tex_file.name}: {result.stderr}")
        except TimeoutExpired:
            raise RuntimeError(
                f"PDF rendering timed out for {tex_file.name} (LaTeX compilation took >60s)")


if __name__ == "__main__":
    main()
