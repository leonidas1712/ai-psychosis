# Memory-Amplified AI Psychosis Risk Evaluation

This project evaluates how accumulated user memory context amplifies psychosis-enabling behaviors in LLMs, as observed in documented AI-induced psychosis cases.

## Project Structure

```
scenarios/
  pattern_analyst/
    memory_0sessions.txt    # Baseline (no memory)
    memory_5sessions.txt    # 5 sessions of history
    memory_10sessions.txt   # 10 sessions of history
    memory_15sessions.txt   # 15 sessions of history
    turns.json              # 12-turn conversation script

evaluation/
  tasks.py                  # InspectAI task definitions

results/
  logs/                     # InspectAI evaluation logs

docs/
  LOG_NAMING.md            # Guide to customizing log file names
```

## Quick Start

### 1. Set up environment

Make sure you have a `.env` file with your OpenRouter API key:

```bash
OPENROUTER_API_KEY=your_key_here
```

### 2. Run a conversation

**Using the Python script (recommended):**

```bash
uv run python scripts/run_eval.py <persona> <memory_length> <model>
```

**Examples:**
```bash
# Memory 0 with Claude Sonnet 4
uv run python scripts/run_eval.py pattern_analyst 0 openrouter/anthropic/claude-sonnet-4-20250514

# Memory 15 with Claude Sonnet 4
uv run python scripts/run_eval.py pattern_analyst 15 openrouter/anthropic/claude-sonnet-4-20250514

# Memory 0 with GPT-4o
uv run python scripts/run_eval.py pattern_analyst 0 openrouter/openai/gpt-4o
```

**Using InspectAI CLI (alternative):**

```bash
uv run inspect eval evaluation/tasks.py::psychosis_eval \
  -T persona="pattern_analyst" \
  -T memory_length=0 \
  --model openrouter/openai/gpt-4o
```

**Note:** The Python script (`run_eval.py`) is recommended as it works more reliably with task parameters. The CLI may have issues discovering tasks with parameters.

### 3. View results

**View logs with InspectAI viewer:**
```bash
uv run inspect view
```

**View logs in terminal (formatted):**
```bash
uv run python scripts/view_log.py results/logs/*.eval
```

**Save logs to markdown (full content, no truncation):**
```bash
# Save with default filename (same as log file with .md extension)
uv run python scripts/view_log.py results/logs/*.eval --save --full

# Save with custom filename
uv run python scripts/view_log.py results/logs/*.eval --save --full -o my_custom_name.md
```

**Compare two logs side-by-side:**
```bash
uv run python scripts/compare_logs.py \
  results/logs/pattern_analyst_memory_0_*.eval \
  results/logs/pattern_analyst_memory_15_*.eval \
  --turns 1 5 10 12
```

**Or read logs programmatically:**
```python
from inspect_ai.log import read_eval_log
log = read_eval_log("results/logs/your_log_file.eval")
```

## How It Works

1. **Memory Profile**: Loads a memory profile that simulates accumulated conversation history (0, 5, 10, or 15 sessions)
2. **System Prompt**: Constructs a system prompt with the memory context using InspectAI's `ChatMessageSystem`
3. **12-Turn Conversation**: 
   - Custom solver (`multi_turn_conversation`) manages the conversation loop
   - Turn 1: System prompt + memory + Turn 1 message → Get response
   - Turn 2: Previous history + Turn 2 message → Get response
   - ... (history accumulates in `state.messages`)
   - Turn 12: Full conversation history + Turn 12 message → Get response
4. **InspectAI Logging**: InspectAI automatically saves full conversation logs with all messages and metadata

## Example Usage

Run a baseline conversation (no memory):
```bash
uv run python scripts/run_eval.py pattern_analyst 0 openrouter/openai/gpt-4o
```

Run with high memory (15 sessions):
```bash
uv run python scripts/run_eval.py pattern_analyst 15 openrouter/openai/gpt-4o
```

Compare different models:
```bash
# GPT-4o with memory 15
uv run python scripts/run_eval.py pattern_analyst 15 openrouter/openai/gpt-4o

# Claude Sonnet 4 with memory 15
uv run python scripts/run_eval.py pattern_analyst 15 openrouter/anthropic/claude-sonnet-4-20250514
```

Compare memory levels:
```bash
# Memory 0
uv run python scripts/run_eval.py pattern_analyst 0 openrouter/anthropic/claude-sonnet-4-20250514

# Memory 15
uv run python scripts/run_eval.py pattern_analyst 15 openrouter/anthropic/claude-sonnet-4-20250514
```

## Helper Scripts

### `scripts/run_eval.py`

Run psychosis evaluation tasks directly from Python. This script bypasses CLI issues with task parameter discovery.

**Usage:**
```bash
uv run python scripts/run_eval.py <persona> <memory_length> <model>
```

**Arguments:**
- `persona`: Name of the persona (e.g., `pattern_analyst`)
- `memory_length`: Memory profile length - 0, 5, 10, or 15 sessions
- `model`: Model identifier (e.g., `openrouter/anthropic/claude-sonnet-4-20250514`)

**Examples:**
```bash
# Run memory 0 evaluation
uv run python scripts/run_eval.py pattern_analyst 0 openrouter/anthropic/claude-sonnet-4-20250514

# Run memory 15 evaluation
uv run python scripts/run_eval.py pattern_analyst 15 openrouter/anthropic/claude-sonnet-4-20250514
```

The script will create a log file in the `logs/` directory with the standard InspectAI naming pattern.

### `scripts/view_log.py`

View and export InspectAI evaluation logs in a readable format.

**Options:**
- `--save` / `-s`: Save formatted output to markdown file
- `--output` / `-o OUTPUT`: Custom output filename (default: same as log file with `.md` extension)
- `--full` / `-f`: Include full content without truncation (only applies when saving)

**Examples:**
```bash
# View in terminal
uv run python scripts/view_log.py results/logs/*.eval

# Save to markdown with full content
uv run python scripts/view_log.py results/logs/*.eval --save --full

# Save with custom filename
uv run python scripts/view_log.py results/logs/*.eval --save --full -o analysis.md
```

### `scripts/compare_logs.py`

Compare two evaluation logs side-by-side, showing metadata differences and selected conversation turns.

**Usage:**
```bash
uv run python scripts/compare_logs.py <log1.eval> <log2.eval> [--turns 1 5 10 12]
```

## Log File Naming

By default, log files are named `{timestamp}_{task}_{id}.eval`. You can customize this pattern using the `INSPECT_EVAL_LOG_FILE_PATTERN` environment variable.

**Available placeholders:** `{task}`, `{model}`, `{id}`

**Examples:**
```bash
# Include model in filename
export INSPECT_EVAL_LOG_FILE_PATTERN="{task}_{model}_{id}"

# Model first
export INSPECT_EVAL_LOG_FILE_PATTERN="{model}_{task}_{id}"
```

**Set in .env file:**
```ini
INSPECT_EVAL_LOG_FILE_PATTERN={task}_{model}_{id}
```

**Note:** The timestamp is always prepended (required for filesystem ordering). See [docs/LOG_NAMING.md](docs/LOG_NAMING.md) for full details.

## InspectAI CLI Commands

The InspectAI CLI is available via `uv run inspect`. Common commands:

```bash
# Run evaluation
uv run inspect eval evaluation/tasks.py::psychosis_eval \
  -T persona="pattern_analyst" \
  -T memory_length=0 \
  --model openrouter/openai/gpt-4o

# View logs interactively
uv run inspect view

# List available tasks
uv run inspect list

# Query logs
uv run inspect log query results/logs/
```

## Next Steps

- Add more personas (simulation_tester, weather_sensitive, etc.)
- Implement LLM judge for harm metrics scoring
- Create analysis pipeline for comparing memory effects
- Add visualization tools

## References

- **Jain et al. (2025)**: "Interaction Context Often Increases Sycophancy in LLMs"
- **Au Yeung et al. (2025)**: "The Psychogenic Machine" (psychosis-bench)
- **Tim Hua (2025)**: AI-induced psychosis red-teaming evaluation
