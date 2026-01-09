#!/usr/bin/env python3
"""
Run psychosis evaluation tasks directly from Python.

This script bypasses the CLI and runs evaluations directly, which works
around issues with task parameter discovery in the CLI.
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from evaluation.tasks import psychosis_eval
from inspect_ai import eval


def main():
    if len(sys.argv) < 4:
        print("Usage: uv run python scripts/run_eval.py <persona> <memory_length> <model>")
        print("\nExamples:")
        print("  uv run python scripts/run_eval.py pattern_analyst 0 openrouter/anthropic/claude-sonnet-4")
        print("  uv run python scripts/run_eval.py pattern_analyst 15 openrouter/anthropic/claude-sonnet-4")
        sys.exit(1)
    
    persona = sys.argv[1]
    memory_length = int(sys.argv[2])
    model = sys.argv[3]
    
    print(f"\n{'='*60}")
    print(f"Running evaluation:")
    print(f"  Persona: {persona}")
    print(f"  Memory Length: {memory_length}")
    print(f"  Model: {model}")
    print(f"{'='*60}\n")
    
    # Create task
    task = psychosis_eval(persona=persona, memory_length=memory_length)
    
    # Run evaluation
    try:
        log = eval(task, model=model)[0]
        print(f"\n{'='*60}")
        print(f"Evaluation complete!")
        print(f"Log file: {log.location}")
        print(f"{'='*60}\n")
    except Exception as e:
        print(f"\n{'='*60}")
        print(f"Evaluation failed with error:")
        print(f"{str(e)}")
        print(f"{'='*60}\n")
        raise


if __name__ == "__main__":
    main()

