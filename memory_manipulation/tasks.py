"""
InspectAI tasks for memory-enabled manipulation research.
"""

from inspect_ai import Task, task
from inspect_ai.dataset import Sample
from inspect_ai.model import ChatMessageSystem, ChatMessageUser
from inspect_ai.solver import Generate, Solver, TaskState, solver as solver_decorator

from .scenarios import SCENARIO


@solver_decorator
def single_turn_manipulation_test(memory_condition: str = "vulnerable") -> Solver:
    """
    Custom solver that runs a single-turn test with memory-enabled manipulation.
    
    Args:
        memory_condition: "none", "neutral", or "vulnerable"
    """
    async def solve(state: TaskState, generate: Generate) -> TaskState:
        # Get memory condition
        memory = SCENARIO["memory_conditions"][memory_condition]
        
        # Build system prompt with available options
        options_text = f"""
Available options to recommend:

1. **{SCENARIO['options']['ethical']['name']}**: {SCENARIO['options']['ethical']['description']}

2. **{SCENARIO['options']['unethical']['name']}**: {SCENARIO['options']['unethical']['description']}
"""
        
        system_parts = [SCENARIO['system_base']]
        
        if memory.strip():
            system_parts.append(memory)
        
        system_parts.append(options_text)
        
        system_content = "\n\n".join(system_parts)
        
        # Initialize messages
        state.messages = [
            ChatMessageSystem(content=system_content),
            ChatMessageUser(content=SCENARIO['user_message'])
        ]
        
        # Generate response
        state = await generate(state)
        
        return state
    
    return solve


@task
def memory_manipulation_eval(
    memory_condition: str = "vulnerable",
    model_name: str = "claude-sonnet-4-20250514"
):
    """
    InspectAI task for testing memory-enabled manipulation.
    
    Args:
        memory_condition: "none", "neutral", or "vulnerable"
        model_name: Model identifier (for metadata)
    
    Returns:
        Task configured for evaluation
    """
    dataset = [
        Sample(
            input=f"Single-turn manipulation test with {memory_condition} memory",
            target="",  # No target for open-ended evaluation
            metadata={
                "memory_condition": memory_condition,
                "model_name": model_name,
                "user_message": SCENARIO['user_message'],
            }
        )
    ]
    
    # Create task name for log file
    task_name = f"memory_manipulation_{memory_condition}"
    
    return Task(
        dataset=dataset,
        solver=single_turn_manipulation_test(memory_condition),
        scorer=None,  # No scoring yet
        name=task_name,
        metadata={
            "memory_condition": memory_condition,
            "model_name": model_name,
        }
    )

