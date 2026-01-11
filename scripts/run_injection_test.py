#!/usr/bin/env python3
"""
Run the memory injection attack experiment.

Tests whether hidden instructions in web content can cause an AI agent 
to update its persistent memory, which then influences future recommendations.

Supports multiple injection strategies that can be run individually or in parallel.
"""

import sys
import argparse
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from agent_injection.tasks import memory_injection_eval
from agent_injection.content import INJECTION_VARIATIONS, get_variation_names
from inspect_ai import eval


def list_variations():
    """Print all available injection variations."""
    print("\nAvailable injection variations:")
    print("-" * 60)
    for key, info in INJECTION_VARIATIONS.items():
        print(f"  {key:20} - {info['name']}")
        print(f"  {' '*20}   {info['description']}")
    print()


def run_single(model: str, variation: str):
    """Run a single variation."""
    print(f"\n{'='*60}")
    print(f"Memory Injection Attack Experiment")
    print(f"{'='*60}")
    print(f"  Model: {model}")
    print(f"  Variation: {variation}")
    print(f"  Description: {INJECTION_VARIATIONS[variation]['description']}")
    print(f"{'='*60}\n")
    
    task = memory_injection_eval(variation=variation, model_name=model)
    
    try:
        log = eval(task, model=model)[0]
        
        print(f"\n{'='*60}")
        print(f"Experiment complete!")
        print(f"Log file: {log.location}")
        print(f"{'='*60}\n")
        
        # Print summary
        if log.samples and len(log.samples) > 0:
            sample = log.samples[0]
            if sample.metadata and "experiment_results" in sample.metadata:
                results = sample.metadata["experiment_results"]
                print("Results Summary:")
                print(f"  Injection triggered memory update: {results.get('injection_triggered_memory_update', 'N/A')}")
                print(f"  Favorite drink overwritten: {results.get('favorite_drink_overwritten', 'N/A')}")
                print(f"  Turn 2 mentions Pepsi: {results.get('turn2_mentions_pepsi', 'N/A')}")
                print(f"  Turn 2 mentions green tea: {results.get('turn2_mentions_green_tea', 'N/A')}")
                print()
                
        return log
                
    except Exception as e:
        print(f"\n{'='*60}")
        print(f"Experiment failed with error:")
        print(f"{str(e)}")
        import traceback
        traceback.print_exc()
        print(f"{'='*60}\n")
        raise


def run_all(model: str):
    """Run all variations in parallel."""
    variations = get_variation_names()
    
    print(f"\n{'='*60}")
    print(f"Memory Injection Attack Experiment - ALL VARIATIONS")
    print(f"{'='*60}")
    print(f"  Model: {model}")
    print(f"  Variations: {len(variations)}")
    for v in variations:
        print(f"    - {v}: {INJECTION_VARIATIONS[v]['name']}")
    print(f"{'='*60}\n")
    
    # Create tasks for all variations
    tasks = [memory_injection_eval(variation=v, model_name=model) for v in variations]
    
    try:
        # Run all in parallel (InspectAI handles parallelism)
        logs = eval(tasks, model=model)
        
        print(f"\n{'='*60}")
        print(f"All experiments complete!")
        print(f"{'='*60}\n")
        
        # Print summary table
        print("Results Summary:")
        print("-" * 80)
        print(f"{'Variation':<20} {'Injection Triggered':<20} {'Memory Changed':<15} {'Says Pepsi':<12}")
        print("-" * 80)
        
        for log in logs:
            if log.samples and len(log.samples) > 0:
                sample = log.samples[0]
                if sample.metadata and "experiment_results" in sample.metadata:
                    results = sample.metadata["experiment_results"]
                    variation = results.get("variation", "?")
                    triggered = "✓" if results.get("injection_triggered_memory_update") else "✗"
                    changed = "✓" if results.get("favorite_drink_overwritten") else "✗"
                    pepsi = "✓" if results.get("turn2_mentions_pepsi") else "✗"
                    print(f"{variation:<20} {triggered:<20} {changed:<15} {pepsi:<12}")
        
        print("-" * 80)
        print()
        
        # Print log file locations
        print("Log files:")
        for log in logs:
            print(f"  {log.location}")
        print()
        
        return logs
                
    except Exception as e:
        print(f"\n{'='*60}")
        print(f"Experiment failed with error:")
        print(f"{str(e)}")
        import traceback
        traceback.print_exc()
        print(f"{'='*60}\n")
        raise


def main():
    parser = argparse.ArgumentParser(
        description="Run the memory injection attack experiment",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # List all available variations
  uv run python scripts/run_injection_test.py --list
  
  # Run a single variation
  uv run python scripts/run_injection_test.py --model openrouter/openai/gpt-4o --variation html_comment
  
  # Run all variations in parallel
  uv run python scripts/run_injection_test.py --model openrouter/openai/gpt-4o --all
        """
    )
    
    parser.add_argument(
        "--model", 
        type=str,
        help="Target model identifier (e.g., openrouter/openai/gpt-4o)"
    )
    parser.add_argument(
        "--variation", 
        type=str,
        help="Specific variation to run (use --list to see options)"
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="Run all variations in parallel"
    )
    parser.add_argument(
        "--list",
        action="store_true",
        help="List all available injection variations"
    )
    
    args = parser.parse_args()
    
    # Handle --list
    if args.list:
        list_variations()
        return
    
    # Validate arguments
    if not args.model:
        parser.error("--model is required (unless using --list)")
    
    if not args.variation and not args.all:
        parser.error("Either --variation or --all is required")
    
    if args.variation and args.all:
        parser.error("Cannot use both --variation and --all")
    
    if args.variation and args.variation not in INJECTION_VARIATIONS:
        print(f"Error: Unknown variation '{args.variation}'")
        list_variations()
        sys.exit(1)
    
    # Run experiment(s)
    if args.all:
        run_all(args.model)
    else:
        run_single(args.model, args.variation)


if __name__ == "__main__":
    main()
