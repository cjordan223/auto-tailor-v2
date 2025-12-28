"""
Configuration management for tex-tailor.

⚙️ SETTINGS CONTROL CENTER - Modify values here to change defaults
📍 Model parameters (temperature, timeout, etc.) controlled here
📍 Provider settings and API URLs defined here
📍 Environment variable fallbacks configured here
"""
import os
from typing import Dict, Any, Optional
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class LLMModelConfig:
    """Configuration for LLM models."""
    default_model: str
    timeout: int = 120
    temperature: float = 0      # 🎛️ CREATIVITY: 0=deterministic, 1=creative
    top_k: int = 1             # 🎛️ DIVERSITY: Lower=focused, higher=diverse
    max_tokens: int = 2048     # 🎛️ LENGTH: Max response length


@dataclass
class ProviderConfig:
    """Configuration for LLM providers."""
    ollama: LLMModelConfig = field(default_factory=lambda: LLMModelConfig(
        default_model="qwen2.5:14b-instruct"  # Best general-purpose model with excellent JSON parsing
    ))
    openai: LLMModelConfig = field(default_factory=lambda: LLMModelConfig(
        default_model="gpt-4o-mini"
    ))
    gemini: LLMModelConfig = field(default_factory=lambda: LLMModelConfig(
        default_model="gemini-1.5-flash"
    ))
    mistral: LLMModelConfig = field(default_factory=lambda: LLMModelConfig(
        default_model="mistral-large-latest"
    ))
    groq: LLMModelConfig = field(default_factory=lambda: LLMModelConfig(
        default_model="llama-3.3-70b-versatile", temperature=0.2
    ))


@dataclass
class APIConfig:
    """Configuration for API endpoints."""
    ollama_base_url: str = "http://192.168.1.22:11434"
    openai_base_url: str = "https://api.openai.com/v1"
    gemini_base_url: str = "https://generativelanguage.googleapis.com/v1beta/models"
    mistral_base_url: str = "https://api.mistral.ai/v1"
    groq_base_url: str = "https://api.groq.com/openai/v1"


@dataclass
class PathConfig:
    """Configuration for file paths and directories."""
    # Default directories
    output_dir: str = "out"
    baseline_resume_dir: str = "templates/Baseline_Resume"
    baseline_cover_dir: str = "templates/Basline_Cover_Letter"

    # Default file names
    base_text_file: str = "base_text.json"
    edits_file: str = "edits.json"

    # Baseline file names
    resume_llm_ready: str = "Conner_Jordan_Software_Engineer llm_ready.tex"
    cover_llm_ready: str = "Conner_Jordan_Cover_Letter llm_ready.tex"

    def get_output_path(self, filename: str) -> str:
        """Get full path for output file."""
        return str(Path(self.output_dir) / filename)

    def get_baseline_resume_path(self) -> str:
        """Get full path for baseline resume."""
        return str(Path(self.baseline_resume_dir) / self.resume_llm_ready)

    def get_baseline_cover_path(self) -> str:
        """Get full path for baseline cover letter."""
        return str(Path(self.baseline_cover_dir) / self.cover_llm_ready)


@dataclass
class ValidationConfig:
    """Configuration for validation limits."""
    max_summary_changes: int = 5
    max_skills_changes: int = 8
    max_cover_letter_paragraphs: int = 4
    max_suggestion_why_length: int = 200
    max_cover_letter_words: int = 500  # Increased from 300 to allow richer content
    # Increased from 100 to ensure substantial letters
    min_cover_letter_words: int = 200
    # Increased from 120 to allow more elaboration per paragraph
    max_paragraph_words: int = 180


@dataclass
class Config:
    """Main configuration class."""
    providers: ProviderConfig = field(default_factory=ProviderConfig)
    apis: APIConfig = field(default_factory=APIConfig)
    paths: PathConfig = field(default_factory=PathConfig)
    validation: ValidationConfig = field(default_factory=ValidationConfig)

    # Environment variable overrides
    def __post_init__(self):
        """Apply environment variable overrides."""
        # Ollama overrides
        if os.getenv("OLLAMA_BASE_URL"):
            self.apis.ollama_base_url = os.getenv("OLLAMA_BASE_URL")
        if os.getenv("OLLAMA_MODEL"):
            self.providers.ollama.default_model = os.getenv("OLLAMA_MODEL")

        # OpenAI overrides
        if os.getenv("OPENAI_MODEL"):
            self.providers.openai.default_model = os.getenv("OPENAI_MODEL")

        # Gemini overrides
        if os.getenv("GEMINI_MODEL"):
            self.providers.gemini.default_model = os.getenv("GEMINI_MODEL")

        # Mistral overrides
        if os.getenv("MISTRAL_MODEL"):
            self.providers.mistral.default_model = os.getenv("MISTRAL_MODEL")

        # Groq overrides
        if os.getenv("GROQ_MODEL"):
            self.providers.groq.default_model = os.getenv("GROQ_MODEL")


# Global configuration instance
config = Config()


def get_model_for_provider(provider: str) -> str:
    """Get default model for a provider."""
    provider_map = {
        "ollama": config.providers.ollama.default_model,
        "openai": config.providers.openai.default_model,
        "gemini": config.providers.gemini.default_model,
    }
    return provider_map.get(provider.lower(), "qwen2.5:14b-instruct")


def get_api_config_for_provider(provider: str) -> Dict[str, Any]:
    """Get API configuration for a provider."""
    provider_configs = {
        "ollama": {
            "base_url": config.apis.ollama_base_url,
            "timeout": config.providers.ollama.timeout,
            "temperature": config.providers.ollama.temperature,
            "top_k": config.providers.ollama.top_k,
            "max_tokens": config.providers.ollama.max_tokens,
        },
        "openai": {
            "base_url": config.apis.openai_base_url,
            "timeout": config.providers.openai.timeout,
            "temperature": config.providers.openai.temperature,
            "max_tokens": config.providers.openai.max_tokens,
        },
        "gemini": {
            "base_url": config.apis.gemini_base_url,
            "timeout": config.providers.gemini.timeout,
            "temperature": config.providers.gemini.temperature,
            "top_k": config.providers.gemini.top_k,
            "max_tokens": config.providers.gemini.max_tokens,
        },
    }
    return provider_configs.get(provider.lower(), provider_configs["ollama"])


def get_default_paths() -> Dict[str, str]:
    """Get dictionary of default paths."""
    return {
        "output_dir": config.paths.output_dir,
        "base_text": config.paths.get_output_path(config.paths.base_text_file),
        "edits": config.paths.get_output_path(config.paths.edits_file),
        "baseline_resume": config.paths.get_baseline_resume_path(),
        "baseline_cover": config.paths.get_baseline_cover_path(),
    }


def update_config_from_env():
    """Manually trigger environment variable updates."""
    global config
    config = Config()
