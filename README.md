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
```

## Quick Start

### 1. Set up environment

Make sure you have a `.env` file with your OpenRouter API key:

```bash
OPENROUTER_API_KEY=your_key_here
```

### 2. Run a conversation

Run a 12-turn conversation with a specific memory profile using InspectAI CLI:

```bash
uv run inspect eval evaluation/tasks.py::psychosis_eval \
  -T persona="pattern_analyst" \
  -T memory_length=0 \
  --model openrouter/openai/gpt-4o
```

**Note:** You must use `uv run inspect` (not just `inspect`) because the CLI tool is installed in the virtual environment managed by `uv`.

### 3. View results

**View logs with InspectAI viewer:**
```bash
uv run inspect view
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
uv run inspect eval evaluation/tasks.py::psychosis_eval \
  -T persona="pattern_analyst" \
  -T memory_length=0 \
  --model openrouter/openai/gpt-4o
```

Run with high memory (15 sessions):
```bash
uv run inspect eval evaluation/tasks.py::psychosis_eval \
  -T persona="pattern_analyst" \
  -T memory_length=15 \
  --model openrouter/openai/gpt-4o
```

Compare different models:
```bash
uv run inspect eval evaluation/tasks.py::psychosis_eval \
  -T persona="pattern_analyst" \
  -T memory_length=15 \
  --model openrouter/openai/gpt-4o

uv run inspect eval evaluation/tasks.py::psychosis_eval \
  -T persona="pattern_analyst" \
  -T memory_length=15 \
  --model openrouter/anthropic/claude-sonnet-4-20250514
```

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
