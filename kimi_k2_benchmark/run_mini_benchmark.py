#!/usr/bin/env python3
"""
Mini Benchmark Runner
Executes a subset of benchmarks to validate the framework and compare models.
"""
import json
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.evaluator import run_single_case, save_raw_result, load_configs
from src.comparator import compute_metrics, compute_heavy_mode_advantage, generate_comparison_table
from src.reporter import generate_markdown_report, generate_plots, generate_recommendations

from rich.console import Console
from rich.table import Table
from rich.progress import track

console = Console()


def load_benchmark_cases():
    """Load mini benchmark cases from JSON."""
    cases_file = Path(__file__).parent / "benchmarks" / "mini_benchmark_cases.json"
    with open(cases_file) as f:
        return json.load(f)


def run_mini_benchmark():
    """Execute mini benchmark across all models."""
    console.print("[bold blue]Kimi K2 Benchmark Framework[/bold blue]")
    console.print("=" * 50)

    # Load configurations
    configs = load_configs()
    console.print(f"[green]✓[/green] Loaded configurations")

    # Models to test
    models = ["kimi_k2_normal", "kimi_k2_heavy", "qwen3_coder_30b"]
    console.print(f"[green]✓[/green] Models: {', '.join(models)}")

    # Load benchmark cases
    cases = load_benchmark_cases()
    console.print(f"[green]✓[/green] Loaded benchmark cases")

    # Count total cases
    total_cases = sum(len(cases[cat]) for cat in cases)
    console.print(f"[green]✓[/green] Total cases: {total_cases}")
    console.print()

    # Execute benchmarks
    all_results = []

    for model_id in models:
        console.print(f"\n[bold cyan]Testing {model_id}[/bold cyan]")

        model_results = []

        for category, category_cases in cases.items():
            for case in track(category_cases, description=f"  {category}"):
                try:
                    result = run_single_case(model_id, category, case)
                    model_results.append(result)

                    # Save raw result
                    save_raw_result(result)

                    # Show quick status
                    status = "✓" if result["metrics"]["correctness"] else "✗"
                    time_taken = result["metrics"]["total_time"]
                    console.print(f"    {status} {case['id']} ({time_taken:.2f}s)")

                except Exception as e:
                    console.print(f"    [red]✗ {case['id']}: {e}[/red]")

        all_results.extend(model_results)
        console.print(f"  [green]Completed {len(model_results)} cases[/green]")

    # Compute metrics
    console.print("\n[bold yellow]Computing Metrics...[/bold yellow]")
    metrics = compute_metrics(all_results)

    # Display results table
    table = Table(title="Benchmark Results")
    table.add_column("Model", style="cyan")
    table.add_column("Accuracy", style="green")
    table.add_column("Mean Latency", style="yellow")
    table.add_column("Tokens/s", style="magenta")

    for model_id in sorted(metrics.keys()):
        m = metrics[model_id]
        table.add_row(
            model_id,
            f"{m.get('accuracy', 0):.2f}%",
            f"{m.get('mean_latency', 0):.3f}s",
            f"{m.get('mean_tokens_per_second', 0):.1f}"
        )

    console.print(table)

    # Heavy mode advantage
    if "kimi_k2_normal" in metrics and "kimi_k2_heavy" in metrics:
        advantage = compute_heavy_mode_advantage(metrics)
        console.print(f"\n[bold]Heavy Mode Advantage:[/bold]")
        console.print(f"  Accuracy: {advantage['accuracy_advantage']:.2f}%")
        console.print(f"  Latency: {advantage['latency_advantage']:.2f}%")

    # Generate report
    console.print("\n[bold yellow]Generating Report...[/bold yellow]")
    report_path = Path(__file__).parent / "results" / "visualizations" / "mini_benchmark_report.md"
    generate_markdown_report(metrics, report_path)
    console.print(f"[green]✓[/green] Report: {report_path}")

    # Generate plots
    plots_dir = Path(__file__).parent / "results" / "visualizations"
    generate_plots(metrics, plots_dir)
    console.print(f"[green]✓[/green] Plots generated in: {plots_dir}")

    # Recommendations
    console.print("\n[bold]Recommendations:[/bold]")
    recs = generate_recommendations(metrics)
    for rec in recs:
        console.print(f"  • {rec}")

    console.print("\n[bold green]Benchmark Complete![/bold green]")


if __name__ == "__main__":
    run_mini_benchmark()
