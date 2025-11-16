#!/usr/bin/env python3
"""
Controlled Benchmark Runner
Executes a subset of benchmarks to compare models while managing costs.
"""
import json
import sys
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent))

from src.evaluator import run_single_case, save_raw_result
from src.comparator import compute_metrics, compute_heavy_mode_advantage
from src.reporter import generate_markdown_report, generate_plots, generate_recommendations, export_to_json

from rich.console import Console
from rich.table import Table

console = Console()


def run_controlled_benchmark():
    """Execute controlled benchmark across all models."""
    console.print("[bold blue]═══ Kimi K2 Controlled Benchmark ═══[/bold blue]")
    console.print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    console.print()

    # Carefully selected test cases for maximum insight
    test_cases = [
        # Reasoning - where heavy mode should shine
        {
            "id": "reasoning.logic.001",
            "prompt": "If A is taller than B, B is taller than C, and D is shorter than A but taller than C, who is the third tallest? Think step by step.",
            "expected_answer": "B",
            "category": "reasoning"
        },
        {
            "id": "reasoning.constraint.001",
            "prompt": "A baker has eggs, flour, and sugar. He can make: Cake (needs all 3), Bread (needs flour only), Cookies (needs eggs and sugar). He wants to make exactly 2 different items. What are his options? List all possibilities.",
            "expected_answer": "Bread and Cookies",
            "category": "reasoning"
        },
        # Coding - optimization challenge
        {
            "id": "coding.optimization.001",
            "prompt": "Write a Python function find_two_sum(arr, target) that finds two indices i and j where i < j and arr[i] + arr[j] = target. Use O(n) time complexity with a hash map. Return (i, j) tuple or None.",
            "expected_answer": "def find_two_sum",
            "category": "coding"
        },
        # Math - competition style
        {
            "id": "math.competition.001",
            "prompt": "What is the sum of all positive divisors of 360? Show your work step by step.",
            "expected_answer": "1170",
            "category": "math"
        },
        # Creative task
        {
            "id": "creative.style.001",
            "prompt": "Rewrite this sentence in the style of Shakespeare: 'The computer crashed and I lost all my work.'",
            "expected_answer": "computer",
            "category": "creative"
        }
    ]

    models = ["kimi_k2_normal", "kimi_k2_heavy", "qwen3_coder_30b"]
    all_results = []

    for model_id in models:
        console.print(f"\n[bold cyan]Testing: {model_id}[/bold cyan]")
        console.print("-" * 40)

        for case in test_cases:
            console.print(f"  Case: {case['id']}")
            try:
                result = run_single_case(model_id, case["category"], case)
                all_results.append(result)

                # Save raw result
                save_raw_result(result)

                # Quick summary
                status = "[green]✓[/green]" if result["metrics"]["correctness"] else "[red]✗[/red]"
                time_taken = result["metrics"]["total_time"]
                tps = result["metrics"]["tokens_per_second"]
                console.print(f"    {status} {time_taken:.2f}s | {tps:.1f} tok/s")

            except Exception as e:
                console.print(f"    [red]ERROR: {e}[/red]")

    # Compute and display metrics
    console.print("\n[bold yellow]═══ Results Analysis ═══[/bold yellow]")
    metrics = compute_metrics(all_results)

    # Results table
    table = Table(title="Model Performance Summary")
    table.add_column("Model", style="cyan", width=20)
    table.add_column("Accuracy", style="green", justify="right")
    table.add_column("Mean Latency", style="yellow", justify="right")
    table.add_column("Tokens/s", style="magenta", justify="right")

    for model_id in sorted(metrics.keys()):
        m = metrics[model_id]
        table.add_row(
            model_id,
            f"{m.get('accuracy', 0):.1f}%",
            f"{m.get('mean_latency', 0):.2f}s",
            f"{m.get('mean_tokens_per_second', 0):.1f}"
        )

    console.print(table)

    # Heavy mode advantage
    if "kimi_k2_normal" in metrics and "kimi_k2_heavy" in metrics:
        console.print("\n[bold]Heavy Mode Analysis:[/bold]")
        advantage = compute_heavy_mode_advantage(metrics)
        console.print(f"  Accuracy Advantage: {advantage['accuracy_advantage']:+.2f}%")
        console.print(f"  Latency Advantage: {advantage['latency_advantage']:+.2f}% (negative = slower)")

        normal_acc = metrics["kimi_k2_normal"]["accuracy"]
        heavy_acc = metrics["kimi_k2_heavy"]["accuracy"]
        if heavy_acc > normal_acc:
            console.print(f"  [green]✓ Heavy mode improves accuracy[/green]")
        elif heavy_acc < normal_acc:
            console.print(f"  [yellow]⚠ Normal mode has better accuracy[/yellow]")
        else:
            console.print(f"  [blue]= Same accuracy[/blue]")

    # Qwen comparison
    if "qwen3_coder_30b" in metrics:
        console.print("\n[bold]Qwen3-Coder:30B Comparison:[/bold]")
        qwen_acc = metrics["qwen3_coder_30b"]["accuracy"]
        qwen_lat = metrics["qwen3_coder_30b"]["mean_latency"]

        kimi_normal_acc = metrics.get("kimi_k2_normal", {}).get("accuracy", 0)
        kimi_heavy_acc = metrics.get("kimi_k2_heavy", {}).get("accuracy", 0)

        if qwen_acc > kimi_normal_acc:
            console.print(f"  [green]✓ Qwen beats Kimi Normal on accuracy ({qwen_acc:.1f}% vs {kimi_normal_acc:.1f}%)[/green]")
        else:
            console.print(f"  [yellow]✗ Kimi Normal beats Qwen on accuracy ({kimi_normal_acc:.1f}% vs {qwen_acc:.1f}%)[/yellow]")

        if qwen_acc > kimi_heavy_acc:
            console.print(f"  [green]✓ Qwen beats Kimi Heavy on accuracy ({qwen_acc:.1f}% vs {kimi_heavy_acc:.1f}%)[/green]")
        else:
            console.print(f"  [yellow]✗ Kimi Heavy beats Qwen on accuracy ({kimi_heavy_acc:.1f}% vs {qwen_acc:.1f}%)[/yellow]")

        console.print(f"  Local inference: {qwen_lat:.2f}s mean latency")

    # Generate reports
    console.print("\n[bold yellow]═══ Generating Reports ═══[/bold yellow]")

    results_dir = Path(__file__).parent / "results"

    # Save metrics to JSON
    metrics_path = results_dir / "analysis" / "controlled_benchmark_metrics.json"
    export_to_json(metrics, metrics_path)
    console.print(f"  [green]✓[/green] Metrics: {metrics_path}")

    # Generate Markdown report
    report_path = results_dir / "visualizations" / "controlled_benchmark_report.md"
    generate_markdown_report(metrics, report_path)
    console.print(f"  [green]✓[/green] Report: {report_path}")

    # Generate plots
    plots_dir = results_dir / "visualizations"
    generate_plots(metrics, plots_dir)
    console.print(f"  [green]✓[/green] Plots: {plots_dir}")

    # Recommendations
    console.print("\n[bold]Recommendations:[/bold]")
    recs = generate_recommendations(metrics)
    for rec in recs:
        console.print(f"  • {rec}")

    console.print(f"\n[bold green]Benchmark Complete![/bold green]")
    console.print(f"Finished: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")


if __name__ == "__main__":
    run_controlled_benchmark()
