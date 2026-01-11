#!/usr/bin/env python3
"""
Run multi-scenario memory injection attack experiments.

Tests whether hidden instructions in web content can cause an AI agent
to update its persistent memory in ways that lead to harmful recommendations.

Scenarios:
- financial_steering: Changes risk tolerance to recommend high-risk investments
- medical_allergy: Removes allergy info, risking dangerous drug recommendations
- dietary_diabetic: Removes diabetic flag, risking high-sugar recommendations
- security_downgrade: Changes security prefs to recommend weak security

Each scenario is tested with:
- chat_log: Fake customer support chat confirming preference
- user_review: Fake user review mentioning preference
- control: No injection (baseline)
"""

import sys
import argparse
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from agent_injection.scenarios import SCENARIOS, get_scenario_ids, INJECTION_STRATEGIES
from agent_injection.scenario_tasks import multi_scenario_injection_eval, single_scenario_injection_eval
from inspect_ai import eval


def list_scenarios():
    """Print all available scenarios."""
    print("\nAvailable scenarios:")
    print("-" * 70)
    for sid, scenario in SCENARIOS.items():
        print(f"  {sid}")
        print(f"    Name: {scenario['name']}")
        print(f"    Description: {scenario['description']}")
        print(f"    Target key: {scenario['target_key']}")
        print(f"    Attack: {scenario['initial_memory'].get(scenario['target_key'])} → {scenario['injected_value']}")
        print()
    
    print("Available injection strategies:")
    print("-" * 70)
    for strategy in INJECTION_STRATEGIES:
        print(f"  {strategy}")
    print()


def print_results_table(logs):
    """Print a summary table of results."""
    print("\nResults Summary:")
    print("=" * 100)
    print(f"{'Scenario':<22} {'Strategy':<12} {'Injected':<10} {'Changed':<10} {'Harm':<10} {'Safety':<10}")
    print("=" * 100)
    
    for log in logs:
        if log.samples:
            for sample in log.samples:
                if sample.metadata and "experiment_results" in sample.metadata:
                    r = sample.metadata["experiment_results"]
                    scenario = r.get("scenario_id", "?")[:20]
                    strategy = r.get("strategy", "control")[:10]
                    injected = "✓" if r.get("injection_triggered") else "✗"
                    changed = "✓" if r.get("target_overwritten") else "✗"
                    harm = "✓" if r.get("harm_detected") else "✗"
                    safety = "✓" if r.get("safety_present") else "✗"
                    
                    print(f"{scenario:<22} {strategy:<12} {injected:<10} {changed:<10} {harm:<10} {safety:<10}")
    
    print("=" * 100)
    print("\nLegend:")
    print("  Injected: Did the injection trigger a memory update?")
    print("  Changed: Was the target memory key overwritten to the malicious value?")
    print("  Harm: Did the response contain harm indicators (dangerous recommendations)?")
    print("  Safety: Did the response contain safety indicators (warnings, safe alternatives)?")
    print()


def run_all(model: str, include_control: bool = True):
    """Run all scenarios with all strategies."""
    scenarios = get_scenario_ids()
    strategies = list(INJECTION_STRATEGIES)
    
    total_samples = len(scenarios) * (len(strategies) + (1 if include_control else 0))
    
    print(f"\n{'='*70}")
    print(f"Multi-Scenario Memory Injection Attack Experiment")
    print(f"{'='*70}")
    print(f"  Model: {model}")
    print(f"  Scenarios: {len(scenarios)}")
    for sid in scenarios:
        print(f"    - {sid}: {SCENARIOS[sid]['name']}")
    print(f"  Strategies: {strategies}")
    print(f"  Include control: {include_control}")
    print(f"  Total samples: {total_samples}")
    print(f"{'='*70}\n")
    
    # Create task
    task = multi_scenario_injection_eval(
        scenarios=scenarios,
        strategies=strategies,
        include_control=include_control,
        model_name=model
    )
    
    try:
        logs = eval(task, model=model)
        
        print(f"\n{'='*70}")
        print(f"All experiments complete!")
        print(f"{'='*70}")
        
        print_results_table(logs)
        
        # Print log locations
        print("Log files:")
        for log in logs:
            print(f"  {log.location}")
        print()
        
        return logs
        
    except Exception as e:
        print(f"\n{'='*70}")
        print(f"Experiment failed with error:")
        print(f"{str(e)}")
        import traceback
        traceback.print_exc()
        print(f"{'='*70}\n")
        raise


def run_scenarios(model: str, scenario_ids: list[str], include_control: bool = True):
    """Run specific scenarios with all strategies."""
    strategies = list(INJECTION_STRATEGIES)
    
    total_samples = len(scenario_ids) * (len(strategies) + (1 if include_control else 0))
    
    print(f"\n{'='*70}")
    print(f"Multi-Scenario Memory Injection Attack Experiment")
    print(f"{'='*70}")
    print(f"  Model: {model}")
    print(f"  Scenarios: {scenario_ids}")
    print(f"  Strategies: {strategies}")
    print(f"  Include control: {include_control}")
    print(f"  Total samples: {total_samples}")
    print(f"{'='*70}\n")
    
    # Create task
    task = multi_scenario_injection_eval(
        scenarios=scenario_ids,
        strategies=strategies,
        include_control=include_control,
        model_name=model
    )
    
    try:
        logs = eval(task, model=model)
        
        print(f"\n{'='*70}")
        print(f"All experiments complete!")
        print(f"{'='*70}")
        
        print_results_table(logs)
        
        # Print log locations
        print("Log files:")
        for log in logs:
            print(f"  {log.location}")
        print()
        
        return logs
        
    except Exception as e:
        print(f"\n{'='*70}")
        print(f"Experiment failed with error:")
        print(f"{str(e)}")
        import traceback
        traceback.print_exc()
        print(f"{'='*70}\n")
        raise


def run_single(model: str, scenario_id: str, strategy: str | None):
    """Run a single scenario/strategy combination."""
    print(f"\n{'='*70}")
    print(f"Single Scenario Injection Attack")
    print(f"{'='*70}")
    print(f"  Model: {model}")
    print(f"  Scenario: {scenario_id} ({SCENARIOS[scenario_id]['name']})")
    print(f"  Strategy: {strategy or 'control'}")
    print(f"{'='*70}\n")
    
    task = single_scenario_injection_eval(
        scenario_id=scenario_id,
        strategy=strategy,
        model_name=model
    )
    
    try:
        logs = eval(task, model=model)
        
        print(f"\n{'='*70}")
        print(f"Experiment complete!")
        print(f"{'='*70}")
        
        print_results_table(logs)
        
        print(f"Log file: {logs[0].location}")
        print()
        
        return logs
        
    except Exception as e:
        print(f"\n{'='*70}")
        print(f"Experiment failed with error:")
        print(f"{str(e)}")
        import traceback
        traceback.print_exc()
        print(f"{'='*70}\n")
        raise


def main():
    parser = argparse.ArgumentParser(
        description="Run multi-scenario memory injection attack experiments",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # List all available scenarios
  uv run python scripts/run_injection_scenarios.py --list
  
  # Run all scenarios with all strategies (parallel)
  uv run python scripts/run_injection_scenarios.py --model openrouter/openai/gpt-4o --all
  
  # Run specific scenarios
  uv run python scripts/run_injection_scenarios.py --model openrouter/openai/gpt-4o --scenarios financial_steering,medical_allergy
  
  # Run a single scenario with a specific strategy
  uv run python scripts/run_injection_scenarios.py --model openrouter/openai/gpt-4o --scenario financial_steering --strategy chat_log
  
  # Run without control conditions (only injection strategies)
  uv run python scripts/run_injection_scenarios.py --model openrouter/openai/gpt-4o --all --no-control
        """
    )
    
    parser.add_argument(
        "--model",
        type=str,
        help="Target model identifier (e.g., openrouter/openai/gpt-4o)"
    )
    parser.add_argument(
        "--list",
        action="store_true",
        help="List all available scenarios and strategies"
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="Run all scenarios with all strategies"
    )
    parser.add_argument(
        "--scenarios",
        type=str,
        help="Comma-separated list of scenario IDs to run"
    )
    parser.add_argument(
        "--scenario",
        type=str,
        help="Single scenario ID to run (use with --strategy)"
    )
    parser.add_argument(
        "--strategy",
        type=str,
        choices=list(INJECTION_STRATEGIES) + ["control"],
        help="Single strategy to run (use with --scenario)"
    )
    parser.add_argument(
        "--no-control",
        action="store_true",
        help="Skip control conditions (no injection baseline)"
    )
    
    args = parser.parse_args()
    
    # Handle --list
    if args.list:
        list_scenarios()
        return
    
    # Validate model is provided for running
    if not args.model:
        if not args.list:
            parser.error("--model is required (unless using --list)")
        return
    
    # Determine what to run
    include_control = not args.no_control
    
    if args.all:
        run_all(args.model, include_control)
    elif args.scenarios:
        scenario_ids = [s.strip() for s in args.scenarios.split(",")]
        # Validate scenario IDs
        for sid in scenario_ids:
            if sid not in SCENARIOS:
                print(f"Error: Unknown scenario '{sid}'")
                list_scenarios()
                sys.exit(1)
        run_scenarios(args.model, scenario_ids, include_control)
    elif args.scenario:
        if args.scenario not in SCENARIOS:
            print(f"Error: Unknown scenario '{args.scenario}'")
            list_scenarios()
            sys.exit(1)
        strategy = None if args.strategy == "control" else args.strategy
        run_single(args.model, args.scenario, strategy)
    else:
        parser.error("Specify --all, --scenarios, or --scenario")


if __name__ == "__main__":
    main()

