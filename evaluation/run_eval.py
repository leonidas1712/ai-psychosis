#!/usr/bin/env python3
"""
Run InspectAI evaluation for psychosis scenarios.

This script uses InspectAI's eval() function to run tasks defined in tasks.py.
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from inspect_ai import eval

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from evaluation.tasks import psychosis_eval

# Load environment variables
load_dotenv()

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Run psychosis evaluation with InspectAI")
    parser.add_argument("--persona", type=str, default="pattern_analyst", help="Persona name")
    parser.add_argument("--memory", type=int, default=0, choices=[0, 5, 10, 15], help="Memory length")
    parser.add_argument("--model", type=str, default="openrouter/openai/gpt-4o", help="Model identifier (use openrouter/ prefix for OpenRouter models)")
    parser.add_argument("--log-dir", type=str, default="results/logs", help="Log directory")
    
    args = parser.parse_args()
    
    # Create task
    task = psychosis_eval(persona=args.persona, memory_length=args.memory)
    
    # Run evaluation
    print(f"\n{'='*60}")
    print(f"Running evaluation: {args.persona} | Memory: {args.memory} sessions | Model: {args.model}")
    print(f"{'='*60}\n")
    
    # Run with InspectAI
    logs = eval(
        task,
        model=args.model,
        log_dir=args.log_dir,
    )
    
    print(f"\n{'='*60}")
    print(f"Evaluation complete! Logs saved to: {args.log_dir}")
    print(f"{'='*60}\n")
    
    # Print summary
    for log in logs:
        print(f"Sample ID: {log.sample_id}")
        print(f"Messages: {len(log.messages)}")
        if log.output:
            print(f"Final output length: {len(log.output.completion)} chars")
        print()

