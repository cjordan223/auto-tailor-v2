# Configuration Management

Tex-tailor uses a centralized configuration system located in `tex_tailor/config.py`. This eliminates hardcoded values scattered throughout the codebase and makes the application easier to customize.

## ✅ Implementation Status: COMPLETE

All hardcoded values have been successfully centralized:
- ✅ Model names and API endpoints moved to config
- ✅ File paths and directory structures configurable  
- ✅ CLI commands use smart defaults with runtime path resolution
- ✅ Environment variable overrides preserved and enhanced
- ✅ Backward compatibility maintained

## Configuration Structure

### LLM Providers
```python
# Default models (can be overridden by environment variables)
providers:
  ollama:
    default_model: "qwen2.5:14b-instruct"
    timeout: 120
    temperature: 0
    top_k: 1
    max_tokens: 2048
    
  openai:
    default_model: "gpt-4o-mini"
    timeout: 120
    temperature: 0
    max_tokens: 2048
    
  gemini:
    default_model: "gemini-1.5-flash"
    timeout: 120
    temperature: 0
    top_k: 1
    max_tokens: 2048
```

### API Endpoints
```python
apis:
  ollama_base_url: "http://127.0.0.1:11434"
  openai_base_url: "https://api.openai.com/v1"
  gemini_base_url: "https://generativelanguage.googleapis.com/v1beta/models"
```

### File Paths
```python
paths:
  output_dir: "out"
  baseline_resume_dir: "Baseline_Resume"
  baseline_cover_dir: "Basline_Cover_Letter"
  base_text_file: "base_text.json"
  edits_file: "edits.json"
  resume_llm_ready: "Conner_Jordan_Software_Engineer llm_ready.tex"
  cover_llm_ready: "Conner_Jordan_Cover_Letter llm_ready.tex"
```

## Environment Variable Overrides

The following environment variables can override default configuration:

- `OLLAMA_BASE_URL` - Override Ollama server URL
- `OLLAMA_MODEL` - Override default Ollama model
- `OPENAI_MODEL` - Override default OpenAI model  
- `GEMINI_MODEL` - Override default Gemini model

Example:
```bash
# Override models
export OLLAMA_MODEL="llama3.1:8b"
export OPENAI_MODEL="gpt-4"
export GEMINI_MODEL="gemini-1.5-flash"

# Override API endpoints
export OLLAMA_BASE_URL="http://192.168.1.100:11434"

# Use with any provider
tex-tailor propose --jd job.txt --provider ollama
tex-tailor propose --jd job.txt --provider openai
tex-tailor propose --jd job.txt --provider gemini
```

## CLI Changes

All CLI commands now use sensible defaults from the configuration:

- ✅ **Smart Defaults**: Output paths automatically resolved at runtime
- ✅ **Optional Parameters**: Most file paths now optional in CLI
- ✅ **Backward Compatibility**: Existing scripts continue to work
- ✅ **Environment Variables**: Still work as before, now handled through config

### Before and After Examples

```bash
# BEFORE: Required explicit paths everywhere
tex-tailor extract --resume "Baseline_Resume/..." --cover "Basline_Cover_Letter/..." --out "out/base_text.json"
tex-tailor propose --jd job.txt --base-text "out/base_text.json" --out "out/edits.json"
tex-tailor apply --edits "out/edits.json" --resume "Baseline_Resume/..." --cover "Basline_Cover_Letter/..."

# AFTER: Uses intelligent defaults
tex-tailor extract --resume "Baseline_Resume/..." --cover "Basline_Cover_Letter/..."
tex-tailor propose --jd job.txt
tex-tailor apply

# Still works with explicit paths when needed
tex-tailor extract --resume custom.tex --cover custom_cover.tex --out custom/output.json
```

### CLI Help Text
All commands now show parameters as optional (no hardcoded defaults visible):
```bash
$ tex-tailor propose --help
Options:
  --base-text TEXT    Path to base text JSON        # No default shown
  --out TEXT          Output edits JSON file        # No default shown
```

## Programmatic Usage

```python
from tex_tailor.config import config, get_model_for_provider, get_default_paths

# Get default paths (used by CLI commands)
paths = get_default_paths()
print(paths["base_text"])     # "out/base_text.json"
print(paths["edits"])        # "out/edits.json" 
print(paths["baseline_resume"]) # "Baseline_Resume/Conner_Jordan_Software_Engineer llm_ready.tex"

# Get model for provider (respects env var overrides)
model = get_model_for_provider("ollama")  # "qwen2.5:14b-instruct" or OLLAMA_MODEL
model = get_model_for_provider("openai")  # "gpt-4o-mini" or OPENAI_MODEL

# Access configuration directly
timeout = config.providers.ollama.timeout        # 120
output_dir = config.paths.output_dir             # "out"
api_url = config.apis.ollama_base_url            # "http://127.0.0.1:11434"
max_changes = config.validation.max_skills_changes # 8

# Get API configuration for provider
api_config = get_api_config_for_provider("gemini")
print(api_config["base_url"])     # Gemini API endpoint
print(api_config["timeout"])      # 120
print(api_config["temperature"])  # 0
```

## Testing the Configuration

```bash
# Test basic configuration loading
source venv/bin/activate
python -c "from tex_tailor.config import config; print('Config loaded:', config.providers.ollama.default_model)"

# Test environment variable overrides
OLLAMA_MODEL=llama3.1:8b python -c "from tex_tailor.config import get_model_for_provider; print(get_model_for_provider('ollama'))"

# Test CLI with defaults
tex-tailor status  # Shows all current configuration values
```

## Implementation Details

### Configuration Structure
The config system uses Python dataclasses for type safety:

```python
@dataclass
class Config:
    providers: ProviderConfig     # LLM model settings
    apis: APIConfig              # API endpoints and timeouts
    paths: PathConfig            # File paths and directories  
    validation: ValidationConfig # Edit limits and constraints
```

### Runtime Default Resolution
CLI commands follow this pattern:

1. **Decorator**: `@click.option("--out", default=None, help="...")`
2. **Function Signature**: `def command(out: Optional[str]):`
3. **Runtime Logic**: 
   ```python
   if not out:
       out = get_default_paths()["edits"]
   ```

This provides smart defaults while preserving user override capability.

### Environment Variable Integration
Environment variables are processed during config initialization:

```python
def __post_init__(self):
    """Apply environment variable overrides."""
    if os.getenv("OLLAMA_MODEL"):
        self.providers.ollama.default_model = os.getenv("OLLAMA_MODEL")
    # ... other overrides
```

## Benefits

1. ✅ **Centralized Configuration**: All settings in one place (`config.py`)
2. ✅ **Environment Override Support**: Easy customization via env vars
3. ✅ **Type Safety**: Configuration is type-checked with dataclasses
4. ✅ **Smart Defaults**: CLI commands require fewer parameters
5. ✅ **Backward Compatibility**: Existing environment variables still work
6. ✅ **Easier Testing**: Configuration can be easily mocked for tests
7. ✅ **Better Maintainability**: No more scattered hardcoded values
8. ✅ **User Experience**: Simpler command line usage

## Migration

**✅ FULLY BACKWARD COMPATIBLE**: Existing scripts and environment variables continue to work without modification.

### What Changed
- Hardcoded defaults removed from CLI option decorators
- Runtime default resolution added to command functions
- Configuration centralized in `config.py`
- All existing functionality preserved

### What Stayed the Same
- Environment variable names and behavior
- CLI command syntax and options
- Output file formats and locations
- API integrations and provider support