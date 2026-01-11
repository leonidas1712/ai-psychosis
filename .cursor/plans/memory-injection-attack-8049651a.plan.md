<!-- 8049651a-efae-4513-bc63-8b5ff5ce467c 81e7290d-67bb-4e3d-83ef-e360b7e5b07c -->
# Injection Content Variations Plan

## Changes Required

### 1. Refactor [`agent_injection/content.py`](agent_injection/content.py)

Replace hardcoded injection/control content with a dictionary of named variations:

```python
INJECTION_VARIATIONS = {
    "control": {
        "name": "Control (no injection)",
        "beverages_page": BEVERAGES_PAGE_CONTROL,  # clean HTML
    },
    "html_comment": {
        "name": "HTML Comment (original)",
        "beverages_page": "...",  # current injection
    },
    "json_ld": {
        "name": "JSON-LD Structured Data",
        "beverages_page": "...",  # Strategy 1
    },
    "user_review": {
        "name": "Fake User Review",
        "beverages_page": "...",  # Strategy 2
    },
    "api_response": {
        "name": "Fake API Response",
        "beverages_page": "...",  # Strategy 3
    },
    "continuation": {
        "name": "Instruction Continuation",
        "beverages_page": "...",  # Strategy 4
    },
    "social_engineering": {
        "name": "Social Engineering",
        "beverages_page": "...",  # Strategy 6
    },
    "chat_log": {
        "name": "Fake Chat Log",
        "beverages_page": "...",  # Strategy 7
    },
    "explicit_sync": {
        "name": "Explicit Memory Sync",
        "beverages_page": "...",  # Strategy 9
    },
}

def get_web_search_response(variation: str) -> str:
    """Get combined HTML for a given variation."""
    config = INJECTION_VARIATIONS[variation]
    return f"...{BBQ_RECIPES_PAGE}...{GRILLING_TIPS_PAGE}...{config['beverages_page']}"
```

### 2. Update [`agent_injection/tasks.py`](agent_injection/tasks.py)

- Change `condition` parameter to `variation` (string key into INJECTION_VARIATIONS)
- Update task name to include variation: `f"memory_injection_{variation}"`

### 3. Update [`scripts/run_injection_test.py`](scripts/run_injection_test.py)

Add options:

- `--variation` - run a single named variation
- `--all` - run all variations in parallel
- `--list` - list available variations
```bash
# Single variation
uv run python scripts/run_injection_test.py --model openrouter/openai/gpt-4o --variation json_ld

# All variations in parallel
uv run python scripts/run_injection_test.py --model openrouter/openai/gpt-4o --all
```


### 4. Variations to Add (from INJECTION_IMPROVEMENT.md)

| Key | Strategy | Description |

|-----|----------|-------------|

| `control` | Control | Clean HTML, no injection |

| `html_comment` | Original | HTML comment (current) |

| `json_ld` | Strategy 1 | JSON-LD structured data |

| `user_review` | Strategy 2 | Fake user review |

### To-dos

- [ ] Create pattern_seeker scenario folder and persona_v5.txt
- [ ] Create memory_0sessions.txt for pattern_seeker
- [ ] Create red_team_prompt_v5.txt with seeker + pushback handling
- [ ] Update tasks.py with v5 stage hints and support
- [ ] Update run_eval.py with v5 option
- [ ] Research InspectAI agents and tools for memory injection experiment