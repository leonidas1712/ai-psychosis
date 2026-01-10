# Memory-Amplified AI Psychosis Risk Evaluation

This project evaluates how accumulated user memory context amplifies psychosis-enabling behaviors in LLMs, as observed in documented AI-induced psychosis cases.

## Overview

The evaluation uses two modes:
1. **Manual Scenarios**: Pre-written conversation turns from `turns.json` are sent to the target model
2. **Red Teaming**: A red teamer model (Grok) dynamically generates user messages based on a persona, while the target model responds with memory context

## Project Structure

```
scenarios/
  {persona}/
    memory_{N}sessions.txt  # Memory profiles (0, 5, 10, 15 sessions)
    persona.txt             # Character description for red teaming
    turns.json              # Pre-written conversation turns (manual mode)

evaluation/
  tasks.py                  # InspectAI tasks and custom solvers

prompts/
  red_team_prompt.txt       # Prompt for red teamer model (Grok)

scripts/
  run_eval.py              # Run evaluations (manual or red teaming)
  view_log.py              # View/save evaluation logs with red teamer context
  compare_logs.py          # Compare two evaluation logs

logs/                      # InspectAI evaluation logs (.eval files)
logs_md/                   # Formatted markdown logs (saved via view_log.py)
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

### Architecture Overview

- **`evaluation/tasks.py`**: InspectAI tasks (`psychosis_eval`, `psychosis_redteam_eval`) and custom solvers
- **Memory Profiles**: `scenarios/{persona}/memory_{N}sessions.txt` - Simulated conversation history (0/5/10/15 sessions)
- **Personas**: `scenarios/{persona}/persona.txt` - Character description for red teaming
- **Manual Turns**: `scenarios/{persona}/turns.json` - Pre-written conversation script
- **Red Team Prompt**: `prompts/red_team_prompt.txt` - Framed as "synthetic data generation" to avoid safety filters

### Manual Scenario Mode

**Process:**
1. Load memory profile → inject into target model's system prompt
2. Load pre-written turns from `turns.json`
3. Loop: For each turn, send accumulated history + turn message → get response
4. History accumulates in `state.messages` across turns

**Key:** Target model sees memory + all previous turns. User messages are static from JSON.

### Red Teaming Mode

**Process:**
1. **Two conversation histories maintained:**
   - `redteam_messages`: Grok's context (persona prompt, no memory, sees conversation)
   - `state.messages`: Target model's context (memory profile + conversation)

2. **Per turn loop:**
   - Grok generates message based on persona + conversation (no memory context)
   - Extract message from `<message>` tags in Grok's response
   - Send extracted message to target model (which has memory)
   - Target responds → add response to Grok's history for next turn
   - Store Grok's input/output in metadata for detailed logging

3. **Logging:**
   - Target conversation saved normally (Grok's messages appear as "user")
   - Grok metadata (full prompt, response, extracted message) stored in sample metadata
   - `view_log.py` displays both conversations side-by-side

**Key:** Grok dynamically adapts based on target's responses. Only target model sees memory profile.

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
