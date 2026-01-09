#!/usr/bin/env python3
"""
View InspectAI evaluation logs in a clear, readable format.

Usage:
    python scripts/view_log.py <log_file.eval>
    python scripts/view_log.py results/logs/pattern_analyst_memory_15_*.eval
"""

import sys
from pathlib import Path
import glob
from inspect_ai.log import read_eval_log


def format_message(msg, max_length=None):
    """Format a message for display."""
    content = msg.content if hasattr(msg, 'content') else str(msg)
    if max_length and len(content) > max_length:
        return content[:max_length] + "..."
    return content


def view_log(log_file: Path, save_md: bool = False, output_file: str = None, full_content: bool = False):
    """Display a log file in a readable format.
    
    Args:
        log_file: Path to the log file
        save_md: If True, save formatted output to markdown file
        output_file: Custom output filename (if None, uses log_file name with .md extension)
        full_content: If True, don't truncate message content
    """
    log = read_eval_log(str(log_file))
    
    # Prepare output (either print or collect for markdown)
    output_lines = []
    
    def add_line(text=""):
        """Add a line to output."""
        if save_md:
            output_lines.append(text)
        else:
            print(text)
    
    add_line(f"\n{'='*80}")
    add_line(f"EVALUATION LOG: {log_file.name}")
    add_line(f"{'='*80}\n")
    
    # Print evaluation metadata
    add_line(f"Task: {log.eval.task}")
    add_line(f"Model: {log.eval.model}")
    add_line(f"Status: {log.status}")
    add_line(f"Timestamp: {log.eval.created}")
    if log.stats and log.stats.model_usage:
        for model, usage in log.stats.model_usage.items():
            add_line(f"Tokens: {usage.input_tokens:,} input, {usage.output_tokens:,} output, {usage.total_tokens:,} total")
            if usage.input_tokens_cache_read:
                add_line(f"  Cache: {usage.input_tokens_cache_read:,} tokens read from cache")
    add_line()
    
    # Print sample metadata
    if log.samples:
        sample = log.samples[0]
        add_line(f"Persona: {sample.metadata.get('persona', 'N/A')}")
        add_line(f"Memory Length: {sample.metadata.get('memory_length', 'N/A')} sessions")
        add_line(f"Total Messages: {len(sample.messages)}")
        add_line()
        
        add_line(f"{'='*80}")
        add_line("CONVERSATION TRANSCRIPT")
        add_line(f"{'='*80}\n")
        
        # Display conversation
        turn_num = 0
        for i, msg in enumerate(sample.messages):
            if msg.role == 'system':
                add_line(f"## System Message")
                add_line()
                add_line("```")
                content = format_message(msg) if full_content else format_message(msg, max_length=800)
                add_line(content)
                add_line("```")
                add_line()
            elif msg.role == 'user':
                # Extract turn number from metadata if available, otherwise estimate
                turn_num = (i - 1) // 2 if i > 0 else 0
                add_line(f"### Turn {turn_num} - User")
                add_line()
                content = format_message(msg) if full_content else format_message(msg, max_length=600)
                add_line(content)
                add_line()
            elif msg.role == 'assistant':
                add_line(f"### Turn {turn_num} - Assistant")
                add_line()
                content = format_message(msg) if full_content else format_message(msg, max_length=800)
                add_line(content)
                add_line()
                add_line("---")
                add_line()
        
        # Print final output summary
        if sample.output:
            add_line()
            add_line(f"**Final Output Length:** {len(sample.output.completion):,} characters")
            add_line(f"**Stop Reason:** {sample.output.stop_reason}")
    
    # Save to markdown file if requested
    if save_md:
        if output_file is None:
            # Default: same name as log file but with .md extension
            output_file = log_file.with_suffix('.md')
        else:
            output_file = Path(output_file)
        
        # Ensure .md extension
        if not output_file.suffix == '.md':
            output_file = output_file.with_suffix('.md')
        
        # Build markdown content
        md_lines = []
        
        # Add markdown header
        md_lines.append(f"# Evaluation Log: {log_file.name}")
        md_lines.append("")
        md_lines.append(f"**Task:** `{log.eval.task}`  ")
        md_lines.append(f"**Model:** `{log.eval.model}`  ")
        md_lines.append(f"**Status:** {log.status}  ")
        md_lines.append(f"**Timestamp:** {log.eval.created}  ")
        md_lines.append("")
        
        if log.stats and log.stats.model_usage:
            for model, usage in log.stats.model_usage.items():
                md_lines.append(f"**Tokens:** {usage.input_tokens:,} input, {usage.output_tokens:,} output, {usage.total_tokens:,} total  ")
                if usage.input_tokens_cache_read:
                    md_lines.append(f"**Cache:** {usage.input_tokens_cache_read:,} tokens read from cache  ")
            md_lines.append("")
        
        if log.samples:
            sample = log.samples[0]
            md_lines.append(f"**Persona:** {sample.metadata.get('persona', 'N/A')}  ")
            md_lines.append(f"**Memory Length:** {sample.metadata.get('memory_length', 'N/A')} sessions  ")
            md_lines.append(f"**Total Messages:** {len(sample.messages)}  ")
            md_lines.append("")
            md_lines.append("---")
            md_lines.append("")
            md_lines.append("## Conversation Transcript")
            md_lines.append("")
            
            # Add conversation messages
            turn_num = 0
            for i, msg in enumerate(sample.messages):
                if msg.role == 'system':
                    md_lines.append("### System Message")
                    md_lines.append("")
                    md_lines.append("```")
                    content = format_message(msg) if full_content else format_message(msg, max_length=None)
                    md_lines.append(content)
                    md_lines.append("```")
                    md_lines.append("")
                elif msg.role == 'user':
                    turn_num = (i - 1) // 2 if i > 0 else 0
                    md_lines.append(f"### Turn {turn_num} - User")
                    md_lines.append("")
                    content = format_message(msg) if full_content else format_message(msg, max_length=None)
                    md_lines.append(content)
                    md_lines.append("")
                elif msg.role == 'assistant':
                    md_lines.append(f"### Turn {turn_num} - Assistant")
                    md_lines.append("")
                    content = format_message(msg) if full_content else format_message(msg, max_length=None)
                    md_lines.append(content)
                    md_lines.append("")
                    md_lines.append("---")
                    md_lines.append("")
            
            # Add final output summary
            if sample.output:
                md_lines.append("")
                md_lines.append(f"**Final Output Length:** {len(sample.output.completion):,} characters  ")
                md_lines.append(f"**Stop Reason:** {sample.output.stop_reason}  ")
        
        # Write markdown file
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write("\n".join(md_lines))
        
        print(f"\n✓ Saved formatted log to: {output_file}")
        print(f"  Full content: {'Yes' if full_content else 'No (truncated for display)'}")


def main():
    import argparse
    
    parser = argparse.ArgumentParser(
        description="View InspectAI evaluation logs in a clear, readable format"
    )
    parser.add_argument(
        "log_file",
        help="Path to log file (supports glob patterns like *.eval)"
    )
    parser.add_argument(
        "--save",
        "-s",
        action="store_true",
        help="Save formatted output to markdown file"
    )
    parser.add_argument(
        "--output",
        "-o",
        type=str,
        default=None,
        help="Output filename for markdown (default: same as log file with .md extension)"
    )
    parser.add_argument(
        "--full",
        "-f",
        action="store_true",
        help="Show full content without truncation (only applies when saving)"
    )
    
    args = parser.parse_args()
    
    # Handle glob patterns
    if '*' in args.log_file or '?' in args.log_file:
        log_files = glob.glob(args.log_file)
        if not log_files:
            print(f"No log files found matching: {args.log_file}")
            sys.exit(1)
        # Use most recent if multiple matches
        log_file = Path(max(log_files, key=lambda p: Path(p).stat().st_mtime))
    else:
        log_file = Path(args.log_file)
    
    if not log_file.exists():
        print(f"Log file not found: {log_file}")
        sys.exit(1)
    
    view_log(log_file, save_md=args.save, output_file=args.output, full_content=args.full)


if __name__ == "__main__":
    main()

