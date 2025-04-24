# Plan: Model Alias Resolution

**Goal:** Implement a feature to resolve short model aliases (e.g., `claude35`) provided via the `--model` option into their full identifiers (e.g., `openrouter/anthropic/claude-3.5-sonnet`) using a configuration file.

**Configuration File:** `config/model-aliases.yaml`

```yaml
# Model aliases configuration
# Format: alias: full_model_identifier

# OpenAI examples
gpt4o: openai/gpt-4o-2024-05-13

# OpenRouter examples
claude35: openrouter/anthropic/claude-3.5-sonnet
claude37: openrouter/anthropic/claude-3.7-sonnet
geminiflash20-free: openrouter/google/gemini-2.0-flash-exp:free
geminiflash25: google/gemini-2.5-flash-preview
gemini25pro-free: openrouter/google/gemini-2.5-pro-exp-03-25:free
qwen32b: openrouter/qwen/qwen-2.5-coder-32b-instruct
qwenmax: openrouter/qwen/qwen-max
deepseekr1: openrouter/deepseek/deepseek-r1-distill-qwen-32b
deepseekr1free: openrouter/deepseek/deepseek-r1:free
deepseekchatfree: openrouter/deepseek/deepseek-chat:free
qwq32b: openrouter/qwen/qwq-32b
```

**Implementation Steps:**

1.  **Create Configuration File:**
    *   Establish the `config/` directory at the project root.
    *   Create `model-aliases.yaml` within `config/` with the content above.

2.  **Implement Alias Resolution Logic:**
    *   Create a new utility file: `ai_git/config_utils.py`.
    *   Define a function `resolve_model_alias(model_name: str) -> str`.
    *   **Logic:**
        *   If `/` in `model_name`, return it directly.
        *   Load `config/model-aliases.yaml` using `pathlib` and `yaml.safe_load`.
        *   Handle errors gracefully (FileNotFoundError, YAMLError, KeyError for missing alias), logging warnings and returning the original `model_name`.
        *   If alias found, return the corresponding full identifier.

3.  **Integrate into `AISummarizer`:**
    *   Modify `_prepare_api_kwargs` in `ai_git/ai_summarizer.py`.
    *   Import the `resolve_model_alias` function.
    *   Call `resolved_model = resolve_model_alias(model)` at the start.
    *   Use `resolved_model` throughout the method for checks and setting the API call parameters.

4.  **Update Help Text (Optional):**
    *   Modify the help string for the `--model` option in `ai_git/commands/git_summary.py` to mention the alias feature and the config file.

**Workflow Diagram:**

```mermaid
sequenceDiagram
    participant User
    participant CLI (git_summary.py)
    participant AISummarizer (ai_summarizer.py)
    participant AliasResolver (config_utils.py)
    participant ConfigFile (config/model-aliases.yaml)
    participant AI_API

    User->>CLI: Executes command with --model <alias> (e.g., "claude35")
    CLI->>AISummarizer: Calls method(..., model="claude35")
    AISummarizer->>AISummarizer: Enters _prepare_api_kwargs(model="claude35")
    AISummarizer->>AliasResolver: resolve_model_alias(model="claude35")
    AliasResolver->>ConfigFile: Reads config/model-aliases.yaml
    ConfigFile-->>AliasResolver: Returns {..., "claude35": "openrouter/...", ...}
    AliasResolver-->>AISummarizer: Returns resolved_model="openrouter/..."
    AISummarizer->>AISummarizer: Uses "openrouter/..." to prepare API kwargs (strips prefix, sets model in payload)
    AISummarizer->>AI_API: Makes API call with model="anthropic/claude-3.5-sonnet"
    AI_API-->>AISummarizer: Returns API response
    AISummarizer-->>CLI: Returns result
    CLI-->>User: Displays result