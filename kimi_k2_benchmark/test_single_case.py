#!/usr/bin/env python3
"""
Test a single benchmark case to validate the framework.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from src.evaluator import run_single_case, load_configs
from rich.console import Console
from rich import print_json
import json

console = Console()

def test_single():
    """Test single case against Qwen local."""
    console.print("[bold blue]Single Case Test[/bold blue]")

    # Simple test case
    case = {
        "prompt": "What is 2 + 2? Answer with just the number.",
        "expected_answer": "4",
        "benchmark_id": "test.arithmetic.001"
    }

    console.print(f"Testing: {case['prompt']}")
    console.print(f"Expected: {case['expected_answer']}")
    console.print()

    # Test Qwen local first (no API cost)
    console.print("[cyan]Testing qwen3_coder_30b (local)...[/cyan]")
    result = run_single_case("qwen3_coder_30b", "test.arithmetic", case)

    console.print(f"Response: {result['output']['response'][:200]}...")
    console.print(f"Correctness: {result['metrics']['correctness']}")
    console.print(f"Time: {result['metrics']['total_time']:.3f}s")
    console.print(f"Tokens/s: {result['metrics']['tokens_per_second']:.1f}")
    console.print()

    # Save full result
    console.print("Full result:")
    print_json(json.dumps(result, indent=2, default=str))

if __name__ == "__main__":
    test_single()
