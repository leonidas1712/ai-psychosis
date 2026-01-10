#!/usr/bin/env python3
"""
Run memory-enabled manipulation evaluation tasks directly from Python.
"""

import sys
import argparse
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from memory_manipulation.tasks import memory_manipulation_eval
from inspect_ai import eval


def main():
    parser = argparse.ArgumentParser(
        description="Run memory-enabled manipulation evaluation tasks",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Test with vulnerable memory condition
  uv run python scripts/run_memory_manipulation.py --memory-condition vulnerable --model openrouter/anthropic/claude-sonnet-4-20250514
  
  # Test with no memory
  uv run python scripts/run_memory_manipulation.py --memory-condition none --model openrouter/anthropic/claude-sonnet-4-20250514
  
  # Test with neutral memory
  uv run python scripts/run_memory_manipulation.py --memory-condition neutral --model openrouter/anthropic/claude-sonnet-4-20250514

Memory Conditions:
  none: No memory context provided
  neutral: General facts about user (name, job, hobbies)
  vulnerable: Detailed information about vulnerabilities, financial stress, emotional state
        """
    )
    
    parser.add_argument("--memory-condition", type=str, default="vulnerable", 
                       choices=["none", "neutral", "vulnerable"],
                       help="Memory condition to test (default: vulnerable)")
    parser.add_argument("--model", required=True,
                       help="Target model identifier (e.g., openrouter/anthropic/claude-sonnet-4-20250514)")
    
    args = parser.parse_args()
    
    print(f"\n{'='*60}")
    print(f"Running memory-enabled manipulation test:")
    print(f"  Memory Condition: {args.memory_condition}")
    print(f"  Target Model: {args.model}")
    print(f"{'='*60}\n")
    
    # Create task
    task = memory_manipulation_eval(
        memory_condition=args.memory_condition,
        model_name=args.model
    )
    
    # Run evaluation
    try:
        log = eval(task, model=args.model)[0]
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

