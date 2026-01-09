#!/usr/bin/env python3
"""
Compare two InspectAI evaluation logs side-by-side.

Usage:
    python scripts/compare_logs.py <log1.eval> <log2.eval>
    python scripts/compare_logs.py results/logs/*memory_0*.eval results/logs/*memory_15*.eval
"""

import sys
from pathlib import Path
import glob
from inspect_ai.log import read_eval_log


def get_key_turns(sample, turns_to_show=[1, 5, 10, 12]):
    """Extract key turns from a conversation."""
    turns = {}
    turn_num = 0
    
    for i, msg in enumerate(sample.messages):
        if msg.role == 'user':
            turn_num = (i - 1) // 2 if i > 0 else 0
            if turn_num in turns_to_show:
                if turn_num not in turns:
                    turns[turn_num] = {}
                turns[turn_num]['user'] = msg.content[:400] + "..." if len(msg.content) > 400 else msg.content
        elif msg.role == 'assistant':
            if turn_num in turns_to_show:
                if turn_num not in turns:
                    turns[turn_num] = {}
                turns[turn_num]['assistant'] = msg.content[:500] + "..." if len(msg.content) > 500 else msg.content
    
    return turns


def compare_logs(log1_file: Path, log2_file: Path):
    """Compare two log files side-by-side."""
    log1 = read_eval_log(str(log1_file))
    log2 = read_eval_log(str(log2_file))
    
    print(f"\n{'='*80}")
    print("LOG COMPARISON")
    print(f"{'='*80}\n")
    
    # Compare metadata
    print("METADATA COMPARISON")
    print("-" * 80)
    print(f"{'Metric':<30} {'Log 1':<25} {'Log 2':<25}")
    print("-" * 80)
    
    sample1 = log1.samples[0] if log1.samples else None
    sample2 = log2.samples[0] if log2.samples else None
    
    if sample1 and sample2:
        print(f"{'Persona':<30} {sample1.metadata.get('persona', 'N/A'):<25} {sample2.metadata.get('persona', 'N/A'):<25}")
        print(f"{'Memory Length':<30} {sample1.metadata.get('memory_length', 'N/A'):<25} {sample2.metadata.get('memory_length', 'N/A'):<25}")
        print(f"{'Total Messages':<30} {len(sample1.messages):<25} {len(sample2.messages):<25}")
        
        if log1.stats and log1.stats.model_usage and log2.stats and log2.stats.model_usage:
            usage1 = list(log1.stats.model_usage.values())[0]
            usage2 = list(log2.stats.model_usage.values())[0]
            print(f"{'Input Tokens':<30} {usage1.input_tokens:,} {usage2.input_tokens:,}")
            print(f"{'Output Tokens':<30} {usage1.output_tokens:,} {usage2.output_tokens:,}")
            print(f"{'Total Tokens':<30} {usage1.total_tokens:,} {usage2.total_tokens:,}")
    
    print()
    
    # Compare key turns
    if sample1 and sample2:
        print(f"{'='*80}")
        print("KEY TURNS COMPARISON")
        print(f"{'='*80}\n")
        
        turns1 = get_key_turns(sample1)
        turns2 = get_key_turns(sample2)
        
        for turn_num in sorted(set(list(turns1.keys()) + list(turns2.keys()))):
            print(f"\n{'='*80}")
            print(f"TURN {turn_num}")
            print(f"{'='*80}\n")
            
            if turn_num in turns1 and turn_num in turns2:
                print(f"[Memory {sample1.metadata.get('memory_length', 0)}] User:")
                print(f"  {turns1[turn_num].get('user', 'N/A')[:300]}...")
                print()
                print(f"[Memory {sample1.metadata.get('memory_length', 0)}] Assistant:")
                print(f"  {turns1[turn_num].get('assistant', 'N/A')[:400]}...")
                print()
                print("-" * 80)
                print()
                print(f"[Memory {sample2.metadata.get('memory_length', 0)}] User:")
                print(f"  {turns2[turn_num].get('user', 'N/A')[:300]}...")
                print()
                print(f"[Memory {sample2.metadata.get('memory_length', 0)}] Assistant:")
                print(f"  {turns2[turn_num].get('assistant', 'N/A')[:400]}...")
                print()


def main():
    if len(sys.argv) < 3:
        print("Usage: python scripts/compare_logs.py <log1.eval> <log2.eval>")
        sys.exit(1)
    
    log1_pattern = sys.argv[1]
    log2_pattern = sys.argv[2]
    
    # Handle glob patterns
    def find_log(pattern):
        if '*' in pattern or '?' in pattern:
            files = glob.glob(pattern)
            if not files:
                return None
            return Path(max(files, key=lambda p: Path(p).stat().st_mtime))
        return Path(pattern)
    
    log1_file = find_log(log1_pattern)
    log2_file = find_log(log2_pattern)
    
    if not log1_file or not log1_file.exists():
        print(f"Log file 1 not found: {log1_pattern}")
        sys.exit(1)
    
    if not log2_file or not log2_file.exists():
        print(f"Log file 2 not found: {log2_pattern}")
        sys.exit(1)
    
    compare_logs(log1_file, log2_file)


if __name__ == "__main__":
    main()

