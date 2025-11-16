#!/usr/bin/env python3
"""
Test Kimi K2 APIs (normal and heavy mode).
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from src.evaluator import run_single_case
from rich.console import Console
import json

console = Console()

def test_kimi():
    """Test Kimi K2 normal and heavy mode."""
    console.print("[bold blue]Kimi K2 API Test[/bold blue]")

    # Reasoning test case (good for heavy mode comparison)
    case = {
        "prompt": "If all roses are flowers, and some flowers fade quickly, can we conclude that some roses fade quickly? Answer Yes or No and explain your reasoning step by step.",
        "expected_answer": "No",
        "benchmark_id": "test.logic.001"
    }

    console.print(f"Test: {case['prompt'][:100]}...")
    console.print(f"Expected: {case['expected_answer']}")
    console.print()

    # Test Kimi K2 Normal
    console.print("[cyan]Testing kimi_k2_normal...[/cyan]")
    try:
        result_normal = run_single_case("kimi_k2_normal", "test.logic", case)
        console.print(f"Response: {result_normal['output']['response'][:300]}...")
        console.print(f"Correctness: {result_normal['metrics']['correctness']}")
        console.print(f"Time: {result_normal['metrics']['total_time']:.3f}s")
        console.print(f"Tokens/s: {result_normal['metrics']['tokens_per_second']:.1f}")
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
    console.print()

    # Test Kimi K2 Heavy Mode
    console.print("[magenta]Testing kimi_k2_heavy...[/magenta]")
    try:
        result_heavy = run_single_case("kimi_k2_heavy", "test.logic", case)
        console.print(f"Response: {result_heavy['output']['response'][:300]}...")
        console.print(f"Correctness: {result_heavy['metrics']['correctness']}")
        console.print(f"Time: {result_heavy['metrics']['total_time']:.3f}s")
        console.print(f"Tokens/s: {result_heavy['metrics']['tokens_per_second']:.1f}")
        if result_heavy.get('heavy_mode_data'):
            console.print(f"Heavy mode data captured: {result_heavy['heavy_mode_data']}")
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")

if __name__ == "__main__":
    test_kimi()
