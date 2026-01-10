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
# Manual scenario (using turns.json)
uv run python scripts/run_eval.py <persona> <memory_length> <model>

# Red teaming mode (Grok acts as user, dynamically generates messages)
uv run python scripts/run_eval.py <persona> <memory_length> <model> --redteam [--turns N] [--redteam-model MODEL]
```

**Examples:**

**Manual scenarios (pre-written turns):**
```bash
# Memory 0 with Claude Sonnet 4
uv run python scripts/run_eval.py pattern_analyst 0 openrouter/anthropic/claude-sonnet-4-20250514

# Memory 15 with Claude Sonnet 4
uv run python scripts/run_eval.py pattern_analyst 15 openrouter/anthropic/claude-sonnet-4-20250514

# Memory 0 with GPT-4o
uv run python scripts/run_eval.py pattern_analyst 0 openrouter/openai/gpt-4o
```

**Red teaming (dynamic user messages):**
```bash
# Red teaming with default settings (12 turns, Grok-4 as red teamer)
uv run python scripts/run_eval.py pattern_analyst 15 openrouter/openai/gpt-4o --redteam

# Red teaming with custom number of turns
uv run python scripts/run_eval.py pattern_analyst 15 openrouter/openai/gpt-4o --redteam --turns 18

# Red teaming with custom red teamer model
uv run python scripts/run_eval.py pattern_analyst 15 openrouter/openai/gpt-4o --redteam --turns 12 --redteam-model openrouter/x-ai/grok-4
```

**Red teaming options:**
- `--redteam`: Enable red teaming mode (Grok generates user messages dynamically)
- `--turns N`: Number of conversation turns (default: 12)
- `--redteam-model MODEL`: Model to use for red teaming (default: `openrouter/x-ai/grok-4`)

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
uv run python scripts/view_log.py logs/*.eval
```

**Save logs to markdown (full content, no truncation):**
```bash
# Save with default filename ({task}_{model}.md)
uv run python scripts/view_log.py logs/*pattern-analyst-memory-15*.eval --save --full

# Save with custom filename
uv run python scripts/view_log.py logs/*.eval --save --full -o my_custom_name.md

# Save red teaming logs (automatically labels red teamer/target model messages)
uv run python scripts/view_log.py logs/*redteam*.eval --save --full
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

### Manual Scenario Mode

1. **Memory Profile**: Loads a memory profile that simulates accumulated conversation history (0, 5, 10, or 15 sessions)
2. **System Prompt**: Constructs a system prompt with the memory context using InspectAI's `ChatMessageSystem`
3. **Pre-written Conversation**: 
   - Custom solver (`multi_turn_conversation`) manages the conversation loop
   - Loads user messages from `scenarios/{persona}/turns.json`
   - Turn 1: System prompt + memory + Turn 1 message → Get response
   - Turn 2: Previous history + Turn 2 message → Get response
   - ... (history accumulates in `state.messages`)
   - Turn N: Full conversation history + Turn N message → Get response
4. **InspectAI Logging**: InspectAI automatically saves full conversation logs with all messages and metadata

### Red Teaming Mode

1. **Memory Profile**: Loads a memory profile for the target model (same as manual mode)
2. **Red Teamer Setup**: 
   - Red teamer model (Grok) receives character description and progression arc
   - Red teamer does NOT see the memory profile (only target model sees it)
   - Two separate conversation histories maintained
3. **Dynamic Conversation**:
   - Red teamer generates user messages based on persona and conversation history
   - Target model responds with memory context included
   - Messages flow: Red teamer → Target model → Red teamer (sees target response) → ...
   - Red teamer adapts its messages based on how target model responds
4. **InspectAI Logging**: Saves the target model's conversation history (includes red teamer messages as "user" messages)

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
# Manual scenario mode
uv run python scripts/run_eval.py <persona> <memory_length> <model>

# Red teaming mode
uv run python scripts/run_eval.py <persona> <memory_length> <model> --redteam [OPTIONS]
```

**Arguments:**
- `persona`: Name of the persona (e.g., `pattern_analyst`)
- `memory_length`: Memory profile length - 0, 5, 10, or 15 sessions
- `model`: Target model identifier (e.g., `openrouter/openai/gpt-4o`)

**Red teaming options:**
- `--redteam`: Enable red teaming mode (Grok generates user messages)
- `--turns N`: Number of conversation turns (default: 12)
- `--redteam-model MODEL`: Model to use for red teaming (default: `openrouter/x-ai/grok-4`)

**Examples:**
```bash
# Manual scenario: Run memory 0 evaluation
uv run python scripts/run_eval.py pattern_analyst 0 openrouter/anthropic/claude-sonnet-4-20250514

# Manual scenario: Run memory 15 evaluation
uv run python scripts/run_eval.py pattern_analyst 15 openrouter/anthropic/claude-sonnet-4-20250514

# Red teaming: Default settings (12 turns, Grok-4)
uv run python scripts/run_eval.py pattern_analyst 15 openrouter/openai/gpt-4o --redteam

# Red teaming: Custom turns and red teamer model
uv run python scripts/run_eval.py pattern_analyst 15 openrouter/openai/gpt-4o --redteam --turns 18 --redteam-model openrouter/x-ai/grok-4
```

The script will create a log file in the `logs/` directory with the standard InspectAI naming pattern. Red teaming logs will have `_redteam` in the task name.

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
