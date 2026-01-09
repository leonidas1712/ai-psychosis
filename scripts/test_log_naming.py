#!/usr/bin/env python3
"""
Test script to demonstrate InspectAI log file naming patterns.

This script shows how to customize log file names using:
1. Task name (via Task.name parameter)
2. INSPECT_EVAL_LOG_FILE_PATTERN environment variable

The log file format is always: {timestamp}_{pattern}.eval
Where pattern can include: {task}, {model}, {id}
"""

import os
from pathlib import Path
from inspect_ai import Task, eval
from inspect_ai.dataset import Sample
from inspect_ai._util.environ import environ_var


def test_default_naming():
    """Test with default naming pattern: {task}_{id}"""
    print("\n" + "="*60)
    print("Test 1: Default naming pattern ({task}_{id})")
    print("="*60)
    
    task = Task(
        dataset=[Sample(input="Hello", target="World")],
        name="my_custom_task_name"
    )
    
    # Run eval (this will create a log file)
    log = eval(task, model="openrouter/openai/gpt-4o-mini")[0]
    
    print(f"Log location: {log.location}")
    print(f"Expected pattern: {{timestamp}}_my-custom-task-name_{{id}}.eval")
    print(f"Actual filename: {Path(log.location).name}")


def test_custom_pattern_with_model():
    """Test with custom pattern including model: {task}_{model}_{id}"""
    print("\n" + "="*60)
    print("Test 2: Custom pattern with model ({task}_{model}_{id})")
    print("="*60)
    
    with environ_var("INSPECT_EVAL_LOG_FILE_PATTERN", "{task}_{model}_{id}"):
        task = Task(
            dataset=[Sample(input="Hello", target="World")],
            name="pattern_analyst_memory_15"
        )
        
        log = eval(task, model="openrouter/openai/gpt-4o-mini")[0]
        
        print(f"Log location: {log.location}")
        print(f"Expected pattern: {{timestamp}}_pattern-analyst-memory-15_{{model}}_{{id}}.eval")
        print(f"Actual filename: {Path(log.location).name}")


def test_custom_pattern_model_first():
    """Test with model first: {model}_{task}_{id}"""
    print("\n" + "="*60)
    print("Test 3: Model first pattern ({model}_{task}_{id})")
    print("="*60)
    
    with environ_var("INSPECT_EVAL_LOG_FILE_PATTERN", "{model}_{task}_{id}"):
        task = Task(
            dataset=[Sample(input="Hello", target="World")],
            name="pattern_analyst_memory_0"
        )
        
        log = eval(task, model="openrouter/openai/gpt-4o-mini")[0]
        
        print(f"Log location: {log.location}")
        print(f"Expected pattern: {{timestamp}}_{{model}}_pattern-analyst-memory-0_{{id}}.eval")
        print(f"Actual filename: {Path(log.location).name}")


if __name__ == "__main__":
    print("\n" + "="*60)
    print("InspectAI Log File Naming Test")
    print("="*60)
    print("\nNote: Timestamp is ALWAYS prepended to the filename.")
    print("You can customize the pattern after the timestamp using")
    print("INSPECT_EVAL_LOG_FILE_PATTERN environment variable.")
    print("\nAvailable placeholders: {task}, {model}, {id}")
    print("Default pattern: {task}_{id}")
    
    # Run tests
    test_default_naming()
    test_custom_pattern_with_model()
    test_custom_pattern_model_first()
    
    print("\n" + "="*60)
    print("Summary:")
    print("="*60)
    print("1. Timestamp is always first (required for filesystem ordering)")
    print("2. Task name comes from Task.name parameter")
    print("3. Use INSPECT_EVAL_LOG_FILE_PATTERN to customize the pattern")
    print("4. Available fields: {task}, {model}, {id}")
    print("5. You can set this in .env file for persistent configuration")
    print("\nExample .env entry:")
    print("  INSPECT_EVAL_LOG_FILE_PATTERN={task}_{model}_{id}")
    print("="*60 + "\n")

