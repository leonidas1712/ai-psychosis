#!/usr/bin/env python3
"""
Run the memory injection attack experiment.

Tests whether hidden instructions in web content can cause an AI agent 
to update its persistent memory, which then influences future recommendations.
"""

import sys
import argparse
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from agent_injection.tasks import memory_injection_eval
from inspect_ai import eval


def main():
    parser = argparse.ArgumentParser(
        description="Run the memory injection attack experiment",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Test with injection (malicious HTML comment)
  uv run python scripts/run_injection_test.py --model openrouter/openai/gpt-4o --condition injection
  
  # Test with control (clean HTML)
  uv run python scripts/run_injection_test.py --model openrouter/openai/gpt-4o --condition control
  
  # Test with Claude
  uv run python scripts/run_injection_test.py --model openrouter/anthropic/claude-sonnet-4 --condition injection
        """
    )
    
    parser.add_argument(
        "--model", 
        type=str, 
        required=True,
        help="Target model identifier (e.g., openrouter/openai/gpt-4o)"
    )
    parser.add_argument(
        "--condition", 
        type=str, 
        default="injection",
        choices=["injection", "control"],
        help="Experiment condition: 'injection' (malicious HTML) or 'control' (clean HTML). Default: injection"
    )
    
    args = parser.parse_args()
    
    print(f"\n{'='*60}")
    print(f"Memory Injection Attack Experiment")
    print(f"{'='*60}")
    print(f"  Model: {args.model}")
    print(f"  Condition: {args.condition}")
    print(f"{'='*60}\n")
    
    # Create task
    task = memory_injection_eval(
        condition=args.condition,
        model_name=args.model
    )
    
    # Run evaluation
    try:
        log = eval(task, model=args.model)[0]
        
        print(f"\n{'='*60}")
        print(f"Experiment complete!")
        print(f"Log file: {log.location}")
        print(f"{'='*60}\n")
        
        # Print summary of results
        if log.samples and len(log.samples) > 0:
            sample = log.samples[0]
            if sample.metadata and "experiment_results" in sample.metadata:
                results = sample.metadata["experiment_results"]
                print("Results Summary:")
                print(f"  Injection triggered memory update: {results.get('injection_triggered_memory_update', 'N/A')}")
                print(f"  Favorite drink overwritten: {results.get('favorite_drink_overwritten', 'N/A')}")
                print(f"  Turn 2 mentions Pepsi: {results.get('turn2_mentions_pepsi', 'N/A')}")
                print(f"  Turn 2 mentions green tea: {results.get('turn2_mentions_green_tea', 'N/A')}")
                print(f"  Verification returned injected preference: {results.get('verification_returned_injected_preference', 'N/A')}")
                print()
                
    except Exception as e:
        print(f"\n{'='*60}")
        print(f"Experiment failed with error:")
        print(f"{str(e)}")
        import traceback
        traceback.print_exc()
        print(f"{'='*60}\n")
        raise


if __name__ == "__main__":
    main()

