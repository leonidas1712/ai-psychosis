#!/usr/bin/env python3
"""
Run psychosis evaluation tasks directly from Python.

This script bypasses the CLI and runs evaluations directly, which works
around issues with task parameter discovery in the CLI.
"""

import sys
import argparse
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from evaluation.tasks import psychosis_eval, psychosis_redteam_eval
from inspect_ai import eval


def main():
    parser = argparse.ArgumentParser(
        description="Run psychosis evaluation tasks",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Manual scenario (using turns.json)
  uv run python scripts/run_eval.py pattern_analyst 0 openrouter/openai/gpt-4o
  
  # Red teaming mode (using Grok as red teamer)
  uv run python scripts/run_eval.py pattern_analyst 15 openrouter/openai/gpt-4o --redteam
  
  # Red teaming with custom settings
  uv run python scripts/run_eval.py pattern_analyst 15 openrouter/openai/gpt-4o --redteam --turns 18 --redteam-model openrouter/x-ai/grok-4
  
  # Red teaming with Spiral-Bench style prompts (v2)
  uv run python scripts/run_eval.py pattern_analyst 15 openrouter/openai/gpt-4o --redteam --turns 10 --prompt-version v2
  
  # Red teaming with LATE-ONSET + Creative Collaborator (v3)
  uv run python scripts/run_eval.py pattern_analyst 15 openrouter/openai/gpt-4o --redteam --turns 20 --prompt-version v3
  
  # Red teaming with REALISTIC LOWERCASE (v4) - best for natural conversations
  uv run python scripts/run_eval.py geometry_decoder 0 openrouter/openai/gpt-4o --redteam --turns 12 --prompt-version v4

Prompt Versions:
  v1: Original direct escalation - immediate pattern discussion
  v2: Spiral-Bench style seeker - lowercase, follows AI's lead
  v3: LATE-ONSET + Creative Collaborator - normal conversation first (0-30%), 
      then gradual escalation with open-ended questions that invite AI to 
      contribute ideas ("What else could this apply to?")
  v4: REALISTIC LOWERCASE - grounded story with natural message style. 
      Fragmented sentences, sensory details, self-aware moments. 
      Best for producing realistic transcripts.
        """
    )
    
    parser.add_argument("persona", help="Name of the persona (e.g., pattern_analyst)")
    parser.add_argument("memory_length", type=int, help="Memory profile length (0, 5, 10, or 15)")
    parser.add_argument("model", help="Target model identifier (e.g., openrouter/openai/gpt-4o)")
    parser.add_argument("--redteam", action="store_true", help="Use red teaming mode (Grok acts as user)")
    parser.add_argument("--turns", type=int, default=12, help="Number of conversation turns (default: 12)")
    parser.add_argument("--redteam-model", type=str, default="openrouter/x-ai/grok-4", 
                       help="Model to use for red teaming (default: openrouter/x-ai/grok-4)")
    parser.add_argument("--prompt-version", type=str, default="v1", choices=["v1", "v2", "v3", "v4"],
                       help="Prompt version: v1 (original), v2 (Spiral-Bench seeker), v3 (late-onset), v4 (realistic lowercase)")
    
    args = parser.parse_args()
    
    print(f"\n{'='*60}")
    print(f"Running evaluation:")
    print(f"  Persona: {args.persona}")
    print(f"  Memory Length: {args.memory_length}")
    print(f"  Target Model: {args.model}")
    if args.redteam:
        print(f"  Mode: Red Teaming")
        print(f"  Red Teamer Model: {args.redteam_model}")
        print(f"  Number of Turns: {args.turns}")
        print(f"  Prompt Version: {args.prompt_version}")
    else:
        print(f"  Mode: Manual Scenario (turns.json)")
        print(f"  Number of Turns: {args.turns}")
    print(f"{'='*60}\n")
    
    # Create task
    if args.redteam:
        task = psychosis_redteam_eval(
            persona=args.persona,
            memory_length=args.memory_length,
            num_turns=args.turns,
            redteam_model=args.redteam_model,
            prompt_version=args.prompt_version
        )
    else:
        task = psychosis_eval(persona=args.persona, memory_length=args.memory_length)
    
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
