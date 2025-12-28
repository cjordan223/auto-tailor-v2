"""
Workflow helpers for running the full tex-tailor pipeline without Click.
"""
from __future__ import annotations

import os
import shutil
import subprocess
from pathlib import Path
from subprocess import TimeoutExpired
from typing import Callable

from .config import config, get_default_paths
from .differ import show_diffs
from .extractor import extract_to_json
from .markers import init_files
from .ollama_optimized import propose_edits_ollama_optimized
from .patcher import apply_edits_with_validation
from .proposer import propose_and_save_edits


def run_workflow_steps(job_description: str, emit: Callable[[str], None] = print) -> None:
    """Run the complete workflow steps.

    The emit callback is used for progress output.
    """
    try:
        # Step 1: Initialize
        emit("🔄 Step 1: Initializing...")
        init_files()
        emit("✅ Initialization complete")

        # Step 2: Extract
        emit("🔄 Step 2: Extracting content...")
        Path(config.paths.output_dir).mkdir(parents=True, exist_ok=True)
        default_paths = get_default_paths()
        resume_file = default_paths["baseline_resume"]
        cover_file = default_paths["baseline_cover"]
        extract_to_json(resume_file, cover_file, default_paths["base_text"])
        emit("✅ Text extraction complete")

        # Step 3: Propose edits
        emit("🔄 Step 3: Proposing edits...")
        provider = os.getenv("PROVIDER")
        model = os.getenv("MODEL")
        personality = os.getenv("PERSONALITY", "career_savvy_colleague")
        if not provider:
            if os.getenv("OPENAI_API_KEY"):
                provider = "openai"
                emit("OPENAI_API_KEY found, using OpenAI provider.")
            elif os.getenv("GEMINI_API_KEY"):
                provider = "gemini"
                emit("GEMINI_API_KEY found, using Gemini provider.")
            elif os.getenv("MISTRAL_API_KEY"):
                provider = "mistral"
                emit("MISTRAL_API_KEY found, using Mistral provider.")
            elif os.getenv("GROQ_API_KEY"):
                provider = "groq"
                emit("GROQ_API_KEY found, using Groq provider.")
            else:
                provider = "ollama"
                emit("No API keys found, defaulting to Ollama provider.")
        else:
            emit(f"Using provider: {provider}")
            if model:
                emit(f"Using model: {model}")

        if provider == "ollama" and model and model in [
            "resume-editor:latest",
            "qwen2.5:14b-instruct",
            "mixtral:latest",
        ]:
            emit(f"🔧 Using Ollama-optimized workflow for {model}")
            try:
                edits = propose_edits_ollama_optimized(
                    job_description, default_paths["base_text"], model
                )

                with open(default_paths["edits"], "w", encoding="utf-8") as f:
                    import json

                    json.dump(edits, f, indent=2, ensure_ascii=False)

                emit("✅ Ollama-optimized edits generated")

            except Exception as exc:
                emit(
                    "⚠️ Ollama optimization failed, falling back to standard workflow: "
                    f"{exc}"
                )
                propose_and_save_edits(
                    job_description,
                    default_paths["base_text"],
                    default_paths["edits"],
                    provider,
                    model,
                    personality,
                )
        else:
            propose_and_save_edits(
                job_description,
                default_paths["base_text"],
                default_paths["edits"],
                provider,
                model,
                personality,
            )

        emit("✅ Edit proposal complete")

        # Step 4: Apply edits
        emit("🔄 Step 4: Applying edits...")
        apply_edits_with_validation(resume_file, cover_file, default_paths["edits"])
        emit("✅ Edits applied")

        # Step 5: Show diffs
        emit("🔄 Step 5: Showing differences...")
        show_diffs()

        # Step 6: Render PDFs
        emit("🔄 Step 6: Rendering PDFs...")
        render_pdfs(config.paths.output_dir, emit=emit)
        emit("✅ PDF rendering complete")

        emit("🎉 Workflow completed successfully!")

    except Exception as exc:
        emit(f"❌ Workflow failed: {exc}")
        raise


def render_pdfs(out_dir: str, emit: Callable[[str], None] = print) -> None:
    """Render PDFs using latexmk."""
    out_path = Path(out_dir)
    if not out_path.exists():
        raise RuntimeError(f"Output directory not found: {out_dir}")

    if not shutil.which("latexmk"):
        emit("⚠️ latexmk not found; skipping PDF rendering.")
        return

    tex_files = list(out_path.glob("*.tuned.tex"))
    if not tex_files:
        raise RuntimeError("No tuned .tex files found")

    for tex_file in tex_files:
        try:
            result = subprocess.run(
                [
                    "latexmk",
                    "-pdf",
                    "-interaction=nonstopmode",
                    "-halt-on-error",
                    tex_file.name,
                ],
                capture_output=True,
                text=True,
                cwd=out_path,
                timeout=300,
            )

            if result.returncode != 0:
                subprocess.run(
                    ["latexmk", "-C", tex_file.name],
                    capture_output=True,
                    text=True,
                    cwd=out_path,
                    timeout=300,
                )
                result = subprocess.run(
                    [
                        "latexmk",
                        "-pdf",
                        "-interaction=nonstopmode",
                        "-halt-on-error",
                        tex_file.name,
                    ],
                    capture_output=True,
                    text=True,
                    cwd=out_path,
                    timeout=300,
                )

            if result.returncode != 0:
                raise RuntimeError(
                    f"PDF rendering failed for {tex_file.name}: {result.stderr}"
                )
        except TimeoutExpired:
            raise RuntimeError(
                f"PDF rendering timed out for {tex_file.name} (LaTeX compilation took >60s)"
            )
