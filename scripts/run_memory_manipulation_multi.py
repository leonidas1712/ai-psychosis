#!/usr/bin/env python3
"""
Run multi-turn memory-enabled manipulation evaluation tasks directly from Python.
"""

import sys
import argparse
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from memory_manipulation.multi_turn_tasks import memory_manipulation_multi_turn_eval
from inspect_ai import eval


def main():
    parser = argparse.ArgumentParser(
        description="Run multi-turn memory-enabled manipulation evaluation tasks",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Test with vulnerable memory, 8 turns
  uv run python scripts/run_memory_manipulation_multi.py --memory-condition vulnerable --turns 8 --assistant-model openrouter/anthropic/claude-sonnet-4.5 --user-model openrouter/x-ai/grok-4.1-fast
  
  # Test with neutral memory, 6 turns
  uv run python scripts/run_memory_manipulation_multi.py --memory-condition neutral --turns 6 --assistant-model openrouter/openai/gpt-5-chat --user-model openrouter/x-ai/grok-4.1-fast

Memory Conditions:
  none: No memory context provided
  neutral: Factual information about user
  vulnerable: Detailed vulnerabilities and emotional state
        """
    )
    
    parser.add_argument("--memory-condition", type=str, default="vulnerable", 
                       choices=["none", "neutral", "vulnerable"],
                       help="Memory condition to test (default: vulnerable)")
    parser.add_argument("--turns", type=int, default=8,
                       help="Number of conversation turns (default: 8)")
    parser.add_argument("--assistant-model", required=True,
                       help="Assistant model identifier (e.g., openrouter/anthropic/claude-sonnet-4.5)")
    parser.add_argument("--user-model", type=str, default="openrouter/x-ai/grok-4.1-fast",
                       help="User simulator model (default: openrouter/x-ai/grok-4.1-fast)")
    
    args = parser.parse_args()
    
    print(f"\n{'='*60}")
    print(f"Running multi-turn memory-enabled manipulation test:")
    print(f"  Memory Condition: {args.memory_condition}")
    print(f"  Number of Turns: {args.turns}")
    print(f"  Assistant Model: {args.assistant_model}")
    print(f"  User Model: {args.user_model}")
    print(f"{'='*60}\n")
    
    # Create task
    task = memory_manipulation_multi_turn_eval(
        memory_condition=args.memory_condition,
        num_turns=args.turns,
        user_model=args.user_model,
        assistant_model=args.assistant_model
    )
    
    # Run evaluation
    try:
        log = eval(task, model=args.assistant_model)[0]
        print(f"\n{'='*60}")
        print(f"Evaluation complete!")
        print(f"Log file: {log.location}")
        print(f"{'='*60}\n")
    except Exception as e:
        print(f"\n{'='*60}")
        print(f"Evaluation failed with error:")
        print(f"{str(e)}")
        import traceback
        traceback.print_exc()
        print(f"{'='*60}\n")
        raise


if __name__ == "__main__":
    main()

