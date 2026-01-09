# InspectAI Log File Naming

## Overview

InspectAI log files are automatically named using a pattern that includes a timestamp and customizable components. The timestamp is **always first** (required for filesystem ordering), but you can customize the rest of the filename.

## Default Pattern

By default, log files are named:
```
{timestamp}_{task}_{id}.eval
```

Example:
```
2026-01-09T15-34-18+00-00_pattern-analyst-memory-15_ESs7P9N8xstqp6x4JXuAzg.eval
```

Where:
- `{timestamp}` - ISO 8601 timestamp (always first, cannot be changed)
- `{task}` - Task name (from `Task.name` parameter)
- `{id}` - Unique task ID

## Customizing the Pattern

You can customize the filename pattern using the `INSPECT_EVAL_LOG_FILE_PATTERN` environment variable.

### Available Placeholders

- `{task}` - Task name (from `Task.name` parameter)
- `{model}` - Model name (e.g., `openrouter/openai/gpt-4o`)
- `{id}` - Unique task ID

### Examples

**Include model in filename:**
```bash
export INSPECT_EVAL_LOG_FILE_PATTERN="{task}_{model}_{id}"
```

Result:
```
2026-01-09T15-34-19+00-00_pattern-analyst-memory-15_openrouter-openai-gpt-4o-mini_9mFk3rkf4uEcynTBbvvkTj.eval
```

**Model first:**
```bash
export INSPECT_EVAL_LOG_FILE_PATTERN="{model}_{task}_{id}"
```

Result:
```
2026-01-09T15-34-21+00-00_openrouter-openai-gpt-4o-mini_pattern-analyst-memory-0_aDgnCcZkXf4iZnsK6cTQix.eval
```

**Task only (no ID):**
```bash
export INSPECT_EVAL_LOG_FILE_PATTERN="{task}_{model}"
```

Result:
```
2026-01-09T15-34-21+00-00_pattern-analyst-memory-15_openrouter-openai-gpt-4o-mini.eval
```

## Setting in .env File

For persistent configuration, add to your `.env` file:

```ini
INSPECT_EVAL_LOG_FILE_PATTERN={task}_{model}_{id}
```

This will apply to all evaluations run from that directory.

## Task Name

The task name comes from the `Task.name` parameter in your task definition. In our `psychosis_eval` task, we set:

```python
task_name = f"{persona}_memory_{memory_length}"
return Task(
    name=task_name,  # This becomes {task} in the filename
    ...
)
```

So for `persona="pattern_analyst"` and `memory_length=15`, the task name is `pattern_analyst_memory_15`, which becomes `pattern-analyst-memory-15` in the filename (underscores converted to hyphens).

## Important Notes

1. **Timestamp is always first** - This cannot be changed. It's required for filesystem ordering.

2. **Underscores become hyphens** - Task names and model names have underscores converted to hyphens in filenames for filesystem compatibility.

3. **Pattern is applied after timestamp** - The pattern you specify is appended after the timestamp prefix.

4. **Environment variable takes precedence** - If `INSPECT_EVAL_LOG_FILE_PATTERN` is set, it overrides the default `{task}_{id}` pattern.

## Testing

You can test different naming patterns using the test script:

```bash
uv run python scripts/test_log_naming.py
```

This will run three tests showing different naming patterns and their results.

