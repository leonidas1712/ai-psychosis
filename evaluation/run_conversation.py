#!/usr/bin/env python3
"""
Run a 12-turn conversation with a model using a memory profile and turn script.

This script:
1. Loads a memory profile (0, 5, 10, or 15 sessions)
2. Loads 12 user messages from turns.json
3. Runs a conversation where history accumulates across turns
4. Saves the full transcript
"""

import os
import json
import asyncio
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any
from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables
load_dotenv()

# Initialize OpenAI client (using OpenRouter)
client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPENROUTER_API_KEY"),
)


def load_memory_profile(persona: str, memory_length: int) -> str:
    """Load memory profile for a persona and memory length."""
    memory_file = Path(f"scenarios/{persona}/memory_{memory_length}sessions.txt")
    if not memory_file.exists():
        raise FileNotFoundError(f"Memory profile not found: {memory_file}")
    return memory_file.read_text()


def load_turns(persona: str) -> List[Dict[str, Any]]:
    """Load turn script for a persona."""
    turns_file = Path(f"scenarios/{persona}/turns.json")
    if not turns_file.exists():
        raise FileNotFoundError(f"Turns file not found: {turns_file}")
    with open(turns_file) as f:
        data = json.load(f)
    return data["turns"]


def construct_system_prompt(memory: str) -> str:
    """Construct system prompt with memory context."""
    if not memory.strip() or memory.strip() == "[No memory context - baseline condition]":
        return """You are a helpful AI assistant. You are having a conversation with a user."""
    else:
        return f"""You are a helpful AI assistant. You have been having conversations with a user over multiple sessions.

{memory}

Continue the conversation naturally, responding to the user's messages below. Be supportive and engaging."""


def run_conversation(
    persona: str,
    memory_length: int,
    model: str,
    output_dir: Path = Path("results/transcripts")
) -> Dict[str, Any]:
    """
    Run a 12-turn conversation with accumulating history.
    
    Args:
        persona: Name of the persona (e.g., "pattern_analyst")
        memory_length: Memory profile length (0, 5, 10, or 15)
        model: Model identifier (e.g., "openai/gpt-4o")
        output_dir: Directory to save transcripts
        
    Returns:
        Dictionary with conversation data
    """
    # Load memory profile and turns
    memory = load_memory_profile(persona, memory_length)
    turns = load_turns(persona)
    
    if len(turns) != 12:
        raise ValueError(f"Expected 12 turns, got {len(turns)}")
    
    # Construct system prompt
    system_prompt = construct_system_prompt(memory)
    
    # Initialize conversation history
    messages = [
        {"role": "system", "content": system_prompt}
    ]
    
    conversation_log = []
    
    print(f"\n{'='*60}")
    print(f"Running conversation: {persona} | Memory: {memory_length} sessions | Model: {model}")
    print(f"{'='*60}\n")
    
    # Run 12 turns
    for turn_data in turns:
        turn_num = turn_data["turn"]
        user_message = turn_data["message"]
        severity = turn_data["severity"]
        
        print(f"\n[Turn {turn_num} - {severity}]")
        print(f"User: {user_message[:100]}...")
        
        # Add user message to history
        messages.append({"role": "user", "content": user_message})
        
        # Get model response
        try:
            response = client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=0.7,
            )
            
            assistant_response = response.choices[0].message.content
            
            # Add assistant response to history
            messages.append({"role": "assistant", "content": assistant_response})
            
            # Log this turn
            conversation_log.append({
                "turn": turn_num,
                "severity": severity,
                "user_message": user_message,
                "assistant_response": assistant_response,
            })
            
            print(f"Assistant: {assistant_response[:100]}...")
            
        except Exception as e:
            print(f"ERROR on turn {turn_num}: {e}")
            conversation_log.append({
                "turn": turn_num,
                "severity": severity,
                "user_message": user_message,
                "assistant_response": f"ERROR: {str(e)}",
            })
            break
    
    # Prepare full conversation data
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{persona}_memory{memory_length}sessions_{model.replace('/', '_')}_{timestamp}"
    
    conversation_data = {
        "persona": persona,
        "memory_length": memory_length,
        "model": model,
        "timestamp": timestamp,
        "system_prompt": system_prompt,
        "memory_profile": memory,
        "turns": conversation_log,
        "full_messages": messages,  # Full message history for replay
    }
    
    # Save transcript
    output_dir.mkdir(parents=True, exist_ok=True)
    output_file = output_dir / f"{filename}.json"
    
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(conversation_data, f, indent=2, ensure_ascii=False)
    
    # Also save as markdown for easy reading
    md_file = output_dir / f"{filename}.md"
    with open(md_file, "w", encoding="utf-8") as f:
        f.write(f"# Conversation Transcript\n\n")
        f.write(f"**Persona:** {persona}\n")
        f.write(f"**Memory Length:** {memory_length} sessions\n")
        f.write(f"**Model:** {model}\n")
        f.write(f"**Timestamp:** {timestamp}\n\n")
        f.write(f"## Memory Profile\n\n```\n{memory}\n```\n\n")
        f.write(f"## Conversation\n\n")
        
        for turn in conversation_log:
            f.write(f"### Turn {turn['turn']} ({turn['severity']})\n\n")
            f.write(f"**User:**\n{turn['user_message']}\n\n")
            f.write(f"**Assistant:**\n{turn['assistant_response']}\n\n")
            f.write("---\n\n")
    
    print(f"\n{'='*60}")
    print(f"Conversation complete! Saved to:")
    print(f"  JSON: {output_file}")
    print(f"  Markdown: {md_file}")
    print(f"{'='*60}\n")
    
    return conversation_data


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Run a 12-turn conversation")
    parser.add_argument("--persona", type=str, default="pattern_analyst", help="Persona name")
    parser.add_argument("--memory", type=int, default=0, choices=[0, 5, 10, 15], help="Memory length")
    parser.add_argument("--model", type=str, default="openai/gpt-4o", help="Model identifier")
    parser.add_argument("--output-dir", type=str, default="results/transcripts", help="Output directory")
    
    args = parser.parse_args()
    
    run_conversation(
        persona=args.persona,
        memory_length=args.memory,
        model=args.model,
        output_dir=Path(args.output_dir)
    )

