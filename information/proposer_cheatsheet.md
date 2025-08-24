# Troubleshooting and Navigation Guide for `proposer.py`

This document provides a guide to understanding, troubleshooting, and fine-tuning the behavior of the AI in `tex_tailor/proposer.py`. This file is the "brain" of the application, controlling how the LLM generates edits for your resume and cover letter.

## Key Sections of the File

### 1. `SYSTEM_PROMPT` (Lines 15-95)

*   **What it is:** This is the main instruction set for the LLM. It defines the AI's personality, its constraints, and the JSON schema it must follow.
*   **When to modify it:** You should modify this section to make high-level changes to the AI's behavior, such as:
    *   Changing the tone or style of the generated text.
    *   Adding or removing constraints on what the AI can or cannot do.
    *   Providing new examples to guide the AI's output.

### 2. `build_user_prompt()` (Lines 123-171)

*   **What it is:** This function gathers the raw text from your job description and base files and formats it into a prompt for the LLM.
*   **When to modify it:** You should only modify this section if you want to change the structure of the input to the LLM. For example, if you wanted to add a new section from your resume to the prompt.

### 3. Provider Classes (`OllamaProvider`, `GeminiProvider`, `OpenAIProvider`)

*   **What they are:** These classes handle the technical details of communicating with the different LLM APIs.
*   **When to modify them:** You generally shouldn't need to modify these classes. However, they are where the creativity controls (`temperature`, `top_k`) are set. These values are read from `config.py`.

## How to Fine-Tune the AI's Behavior

The most effective way to fine-tune the AI is by modifying the `SYSTEM_PROMPT`.

*   **To make the AI more creative:**
    *   Make the constraints in the `SYSTEM_PROMPT` less restrictive.
    *   Increase the `temperature` and `top_k` values in `config.py` for your chosen provider.
*   **To make the AI more deterministic and predictable:**
    *   Make the constraints in the `SYSTEM_PROMPT` more restrictive.
    *   Add more specific examples to the "EXAMPLES" section.
    *   Decrease the `temperature` and `top_k` values in `config.py`.

## Troubleshooting Common Issues

### Issue: The AI's output is not what I expect.

*   **Solution:**
    1.  Start by modifying the `SYSTEM_PROMPT` to be more specific about what you want.
    2.  Add more examples to the "EXAMPLES" section that show the AI the desired output.
    3.  If the issue persists, consider adjusting the `temperature` in `config.py`. A lower temperature will produce more predictable results.

### Issue: The script fails with a JSON parsing error.

*   **Solution:** This usually means the LLM has returned a response that is not valid JSON.
    1.  Make sure the `SYSTEM_PROMPT` is very clear that the AI must return valid JSON.
    2.  Check the "EXAMPLES" section to ensure all the examples are valid JSON.
    3.  If you are using a less powerful model, you may need to be more explicit in your instructions.

### Issue: The script is slow or timing out.

*   **Solution:**
    1.  The `timeout` for each provider is set in `config.py`. You can increase this value if you are using a model that takes a long time to respond.
    2.  Consider using a faster LLM provider or a smaller model.

By understanding these key sections and following these troubleshooting steps, you can effectively control and fine-tune the behavior of the AI to meet your needs.
