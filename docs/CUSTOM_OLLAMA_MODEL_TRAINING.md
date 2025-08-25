# Custom Ollama Model Training for Resume Tailoring

## Overview

Creating a custom Ollama model specifically for resume tailoring requires preparing training data, choosing a base model, and fine-tuning for your specific use case.

## Quick Start

### 1. Choose Base Model
Start with a proven model that already has good instruction-following:
```bash
# Recommended base models (in order of preference):
ollama pull qwen2.5:14b-instruct    # Best balance of capability/resources
ollama pull mistral:7b-instruct     # Good alternative, smaller
ollama pull llama3.1:8b-instruct    # Meta's latest, reliable
```

### 2. Prepare Training Data

Create training examples that match your exact use case. Structure: `instruction -> input -> output`

**Example training format (JSONL)**:
```json
{"instruction": "You are a resume expert. Tailor this resume for the job description. Output only valid JSON matching the schema.", "input": "Job Description: Software Engineer at TechCorp...\n\nResume: {base_text_json}", "output": "{\"summary\": {\"replace\": \"Software engineer with 5+ years at TechCorp-focused development...\"}, \"skills\": {...}}"}
```

### 3. Key Training Data Requirements

**Quality over Quantity**: 50-100 high-quality examples better than 1000 poor ones

**Essential examples to include**:
- Company name extraction and usage
- Skills matching and enhancement  
- Cover letter personalization
- JSON schema compliance
- Edge cases (missing company names, vague job descriptions)

**Data structure for each example**:
```
Input: Job description text + Base resume JSON
Output: Properly formatted JSON response with actual company names
```

## Training Methods

### Method 1: Ollama Modelfile (Recommended for beginners)

Create a `Modelfile`:
```dockerfile
FROM qwen2.5:14b-instruct

# Set parameters optimized for resume tasks
PARAMETER temperature 0.1
PARAMETER top_k 5  
PARAMETER top_p 0.9
PARAMETER repeat_penalty 1.1

# Core system prompt focused on resume tailoring
SYSTEM """You are a professional resume consultant with expertise in tailoring resumes and cover letters.

CRITICAL RULES:
1. Extract the EXACT company name from job descriptions
2. Output ONLY valid JSON matching the provided schema
3. Never use placeholders like [Company Name] or [Position]
4. Focus on skills alignment and narrative storytelling

Your responses must be professional, compelling, and technically accurate."""

# Add training examples as few-shot learning
SYSTEM """
EXAMPLE 1:
Input: Job at DataCorp for Senior Developer...
Output: {"summary": {"replace": "Senior developer experienced in DataCorp's tech stack..."}}

EXAMPLE 2: 
Input: Position at StartupXYZ for Full Stack Engineer...
Output: {"cover_letter": {"paragraphs": ["I'm excited to apply for the Full Stack Engineer role at StartupXYZ..."]}}
"""
```

Build the model:
```bash
ollama create resume-tailor-v2 -f Modelfile
```

### Method 2: Fine-tuning with Training Data

**For advanced users - requires more setup:**

1. **Prepare dataset** (`training_data.jsonl`):
```json
{"messages": [{"role": "system", "content": "You are a resume expert..."}, {"role": "user", "content": "Job: Engineer at TechCorp..."}, {"role": "assistant", "content": "{\"summary\": {...}}"}]}
{"messages": [{"role": "system", "content": "You are a resume expert..."}, {"role": "user", "content": "Job: Developer at StartupABC..."}, {"role": "assistant", "content": "{\"cover_letter\": {...}}"}]}
```

2. **Use tools like Unsloth or LoRA** to fine-tune:
```python
# Example with Unsloth (simplified)
from unsloth import FastLanguageModel

model, tokenizer = FastLanguageModel.from_pretrained(
    model_name="qwen2.5:14b-instruct",
    max_seq_length=4096,
    dtype=None,
    load_in_4bit=True,
)

model = FastLanguageModel.get_peft_model(
    model,
    r=16,
    target_modules=["q_proj", "k_proj", "v_proj", "o_proj"],
    lora_alpha=16,
    lora_dropout=0,
    bias="none",
)
```

## Testing Your Custom Model

### 1. Basic JSON Test
```bash
curl -X POST http://localhost:11434/api/generate \
  -H "Content-Type: application/json" \
  -d '{
    "model": "resume-tailor-v2:latest",
    "prompt": "Output only valid JSON: {\"test\": \"working\"}",
    "stream": false
  }'
```

### 2. Resume Task Test
```bash
# Test with actual resume content
tex-tailor propose-ollama --jd sample_job.txt --model resume-tailor-v2:latest
```

### 3. Evaluation Metrics

**Measure these qualities**:
- JSON parsing success rate (should be >95%)
- Company name extraction accuracy
- Skills relevance scoring
- Cover letter personalization quality
- Response consistency across runs

## Optimization Tips

### Model Parameters
```dockerfile
# In your Modelfile:
PARAMETER temperature 0.05    # Very low for consistency
PARAMETER top_k 3            # Focused responses
PARAMETER top_p 0.8          # Balanced creativity
PARAMETER repeat_penalty 1.15 # Avoid repetition
PARAMETER seed 42            # Deterministic for testing
```

### Training Data Quality Checklist
- ✅ Real job descriptions with actual company names
- ✅ Varied industries and roles
- ✅ Different resume formats and experience levels  
- ✅ Edge cases (startups, government, remote roles)
- ✅ Both successful and corrected examples
- ✅ Consistent JSON schema formatting

### Common Issues & Solutions

**Issue**: Model generates placeholders like "[Company Name]"
**Solution**: Add more examples with explicit company name extraction

**Issue**: JSON parsing failures
**Solution**: Include malformed JSON examples with corrections

**Issue**: Generic responses
**Solution**: Add industry-specific examples and terminology

## Integration with Resume Tailor

Once trained, update your config:

```python
# In tex_tailor/ollama_optimized.py
"specialized": [
    "resume-tailor-v2:latest",  # Your custom model
],
```

```python  
# In tex_tailor/config.py
ollama: LLMModelConfig = field(default_factory=lambda: LLMModelConfig(
    default_model="resume-tailor-v2:latest"  # Use your custom model as default
))
```

## Production Considerations

- **Model versioning**: Tag your models (v1, v2, etc.)
- **A/B testing**: Compare against qwen2.5:14b-instruct baseline
- **Monitoring**: Track JSON parsing success rates in production
- **Continuous improvement**: Regular retraining with new examples

## Resources

- [Ollama Model Creation Guide](https://github.com/ollama/ollama/blob/main/docs/modelfile.md)
- [Unsloth Fine-tuning](https://github.com/unslothai/unsloth)
- [LoRA Training Tutorial](https://huggingface.co/docs/peft/conceptual_guides/lora)