#!/usr/bin/env python3
"""
Extract a specific transcript from Spiral-Bench results.

Usage:
    python scripts/extract_spiral_transcript.py mp03
"""

import sys
import json
from pathlib import Path

def extract_transcript(prompt_id: str, output_file: str = None):
    """Extract transcript for a given prompt_id from Spiral-Bench results."""
    project_root = Path(__file__).parent.parent
    results_file = project_root / "resources" / "spiral-bench" / "res_v1.2" / "chatgpt-4o-latest.json"
    
    if not results_file.exists():
        print(f"Error: Results file not found: {results_file}")
        sys.exit(1)
    
    print(f"Loading results from: {results_file}")
    with open(results_file, 'r') as f:
        data = json.load(f)
    
    # Navigate to the prompt_id
    if '1' not in data:
        print("Error: Expected '1' key in results file")
        sys.exit(1)
    
    if 'eval_prompts_v0.2.json' not in data['1']:
        print("Error: Expected 'eval_prompts_v0.2.json' key")
        sys.exit(1)
    
    prompts = data['1']['eval_prompts_v0.2.json']
    
    if prompt_id not in prompts:
        print(f"Error: Prompt ID '{prompt_id}' not found")
        print(f"Available prompt IDs: {list(prompts.keys())[:10]}...")
        sys.exit(1)
    
    result = prompts[prompt_id]
    if not isinstance(result, list) or len(result) == 0:
        print(f"Error: No results found for {prompt_id}")
        sys.exit(1)
    
    # Get the first (and likely only) result
    result_item = result[0]
    transcript = result_item.get('transcript', [])
    
    print(f"\nFound transcript for {prompt_id}:")
    print(f"  Category: {result_item.get('category', 'N/A')}")
    print(f"  Initial prompt: {result_item.get('prompts', [''])[0][:100]}...")
    print(f"  Transcript length: {len(transcript)} messages")
    print(f"  User model: {result_item.get('user_model', 'N/A')}")
    print(f"  Evaluated model: {result_item.get('evaluated_model', 'N/A')}")
    
    # Prepare clean output
    output = {
        "prompt_id": prompt_id,
        "category": result_item.get('category'),
        "initial_prompt": result_item.get('prompts', [''])[0] if result_item.get('prompts') else '',
        "transcript": transcript,
        "metadata": {
            "user_model": result_item.get('user_model'),
            "evaluated_model": result_item.get('evaluated_model'),
            "total_messages": len(transcript),
            "turns": len([m for m in transcript if m.get('role') == 'assistant'])
        }
    }
    
    # Determine output file
    if output_file is None:
        output_file = project_root / "spiral_history" / "transcripts" / f"{prompt_id}_transcript.json"
    
    output_path = Path(output_file)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Write output
    with open(output_path, 'w') as f:
        json.dump(output, f, indent=2)
    
    print(f"\n✓ Saved transcript to: {output_path}")
    print(f"  Total messages: {len(transcript)}")
    print(f"  Turns (assistant responses): {output['metadata']['turns']}")
    
    return output_path


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python scripts/extract_spiral_transcript.py <prompt_id> [output_file]")
        print("Example: python scripts/extract_spiral_transcript.py mp03")
        sys.exit(1)
    
    prompt_id = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else None
    
    extract_transcript(prompt_id, output_file)

