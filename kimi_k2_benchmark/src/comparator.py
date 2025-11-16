"""
Kimi K2 Benchmark Comparator
Model comparison logic and metrics computation.
"""
from typing import Any
from collections import defaultdict


def compute_metrics(raw_results: list[dict[str, Any]]) -> dict[str, Any]:
    """
    Compute aggregated metrics from raw benchmark results.

    Args:
        raw_results: List of result dictionaries

    Returns:
        Dictionary with metrics per model
    """
    # Group results by model
    model_results = defaultdict(list)
    for result in raw_results:
        model_id = result.get("model_id", "unknown")
        model_results[model_id].append(result)

    metrics = {}

    for model_id, results in model_results.items():
        # Compute accuracy
        correct_count = sum(
            1 for r in results if r.get("metrics", {}).get("correctness", False)
        )
        total_count = len(results)
        accuracy = (correct_count / total_count * 100) if total_count > 0 else 0.0

        # Compute mean latency
        latencies = [
            r.get("metrics", {}).get("total_time", 0) for r in results
            if r.get("metrics", {}).get("total_time", 0) > 0
        ]
        mean_latency = sum(latencies) / len(latencies) if latencies else 0.0

        # Compute mean tokens/second
        tps_values = [
            r.get("metrics", {}).get("tokens_per_second", 0) for r in results
            if r.get("metrics", {}).get("tokens_per_second", 0) > 0
        ]
        mean_tps = sum(tps_values) / len(tps_values) if tps_values else 0.0

        # Group by category
        category_results = defaultdict(list)
        for r in results:
            benchmark_id = r.get("benchmark_id", "unknown")
            # Extract category (first part before '.')
            category = benchmark_id.split(".")[0] if "." in benchmark_id else benchmark_id
            category_results[category].append(r)

        by_category = {}
        for category, cat_results in category_results.items():
            cat_correct = sum(
                1 for r in cat_results if r.get("metrics", {}).get("correctness", False)
            )
            cat_total = len(cat_results)
            cat_accuracy = (cat_correct / cat_total * 100) if cat_total > 0 else 0.0
            by_category[category] = {"accuracy": cat_accuracy}

        metrics[model_id] = {
            "accuracy": accuracy,
            "mean_latency": mean_latency,
            "mean_tokens_per_second": mean_tps,
            "by_category": by_category
        }

    return metrics


def compare_models_across_benchmarks(metrics: dict[str, Any]) -> dict[str, Any]:
    """
    Compare models head-to-head based on computed metrics.

    Args:
        metrics: Dictionary of metrics per model

    Returns:
        Comparison results
    """
    model_ids = list(metrics.keys())
    comparison = {}

    # Pairwise comparisons
    for i, model_a in enumerate(model_ids):
        for model_b in model_ids[i+1:]:
            key = f"{model_a}_vs_{model_b}"

            # Compare accuracy
            acc_a = metrics[model_a].get("accuracy", 0)
            acc_b = metrics[model_b].get("accuracy", 0)

            if acc_a > acc_b:
                winner = model_a
            elif acc_b > acc_a:
                winner = model_b
            else:
                winner = "tie"

            comparison[key] = {
                "accuracy_winner": winner,
                f"{model_a}_accuracy": acc_a,
                f"{model_b}_accuracy": acc_b,
                "accuracy_delta": abs(acc_a - acc_b)
            }

    return {"comparison": comparison}


def compute_heavy_mode_advantage(metrics: dict[str, Any]) -> dict[str, float]:
    """
    Calculate percentage advantage of heavy mode over normal mode.

    Args:
        metrics: Dictionary with metrics for both modes

    Returns:
        Dictionary with advantage percentages
    """
    normal_metrics = metrics.get("kimi_k2_normal", {})
    heavy_metrics = metrics.get("kimi_k2_heavy", {})

    advantages = {}

    # Accuracy advantage
    normal_acc = normal_metrics.get("accuracy", 0)
    heavy_acc = heavy_metrics.get("accuracy", 0)

    if normal_acc > 0:
        acc_advantage = ((heavy_acc - normal_acc) / normal_acc) * 100
    else:
        acc_advantage = 0.0

    advantages["accuracy_advantage"] = round(acc_advantage, 2)

    # Latency comparison (negative if heavy is slower)
    normal_lat = normal_metrics.get("mean_latency", 0)
    heavy_lat = heavy_metrics.get("mean_latency", 0)

    if normal_lat > 0:
        lat_advantage = ((normal_lat - heavy_lat) / normal_lat) * 100  # Positive if faster
    else:
        lat_advantage = 0.0

    advantages["latency_advantage"] = round(lat_advantage, 2)

    return advantages


def summarize_head_to_head(
    model_a: str,
    model_b: str,
    case_results: list[dict[str, Any]]
) -> dict[str, int]:
    """
    Count wins, losses, and ties between two models.

    Args:
        model_a: First model identifier
        model_b: Second model identifier
        case_results: List of per-case comparison results

    Returns:
        Dictionary with wins, losses, ties counts
    """
    wins = 0
    losses = 0
    ties = 0

    for case in case_results:
        a_correct = case.get("model_a_correct", False)
        b_correct = case.get("model_b_correct", False)

        if a_correct and not b_correct:
            wins += 1
        elif b_correct and not a_correct:
            losses += 1
        else:
            ties += 1  # Both correct or both wrong

    return {
        "wins": wins,
        "losses": losses,
        "ties": ties
    }


def compute_trajectory_diversity(trajectories: list[str]) -> float:
    """
    Compute diversity score among trajectories.

    Uses simple uniqueness ratio: unique/total

    Args:
        trajectories: List of trajectory strings (8 for heavy mode)

    Returns:
        Diversity score between 0 and 1
    """
    if not trajectories:
        return 0.0

    unique_count = len(set(trajectories))
    total_count = len(trajectories)

    # Normalize to 0-1 range
    # If all unique, diversity = 1
    # If all same, diversity = 1/total
    diversity = unique_count / total_count

    return round(diversity, 4)


def identify_convergence_pattern(trajectories: list[str]) -> str:
    """
    Identify the convergence pattern among trajectories.

    Args:
        trajectories: List of trajectory answers

    Returns:
        Pattern: 'unanimous', 'majority', 'split', or 'divergent'
    """
    if not trajectories:
        return "unknown"

    from collections import Counter

    counts = Counter(trajectories)
    total = len(trajectories)
    most_common_count = counts.most_common(1)[0][1]

    # Unanimous: all same
    if most_common_count == total:
        return "unanimous"

    # Majority: >50% same
    if most_common_count > total / 2:
        return "majority"

    # Split: no clear majority, but some agreement
    if most_common_count >= 2:
        return "split"

    # Divergent: mostly unique answers
    return "divergent"


def compute_hybridization_quality(
    trajectories: list[str],
    hybridized: str,
    ground_truth: str
) -> float:
    """
    Assess quality of hybridized output.

    Compares hybridized output against ground truth.
    Also considers if hybridized is better than best individual trajectory.

    Args:
        trajectories: List of individual trajectory outputs
        hybridized: The hybridized/final output
        ground_truth: The expected correct answer

    Returns:
        Quality score between 0 and 1
    """
    if not ground_truth:
        return 0.5  # Can't assess without ground truth

    # Simple check: does hybridized contain/match ground truth?
    gt_lower = ground_truth.lower()
    hyb_lower = hybridized.lower()

    # Check if ground truth is in hybridized output
    if gt_lower in hyb_lower:
        hybridized_correct = True
    else:
        hybridized_correct = False

    # Check individual trajectories
    traj_correct_count = sum(
        1 for t in trajectories if gt_lower in t.lower()
    )

    # Quality scoring
    if hybridized_correct and traj_correct_count == 0:
        # Hybridization found correct answer when no individual did
        return 1.0
    elif hybridized_correct and traj_correct_count > 0:
        # Hybridization correct, some individuals also correct
        return 0.8
    elif not hybridized_correct and traj_correct_count > 0:
        # Hybridization wrong, but some individuals were correct
        return 0.3
    else:
        # Both hybridized and all individuals wrong
        return 0.1


def generate_comparison_table(metrics: dict[str, Any]) -> str:
    """
    Generate a formatted comparison table.

    Args:
        metrics: Dictionary of metrics per model

    Returns:
        Formatted table as string
    """
    # Header
    table = "| Model | Accuracy (%) | Mean Latency (s) | Tokens/s |\n"
    table += "|-------|--------------|------------------|----------|\n"

    # Rows
    for model_id, model_metrics in sorted(metrics.items()):
        accuracy = model_metrics.get("accuracy", 0)
        latency = model_metrics.get("mean_latency", 0)
        tps = model_metrics.get("mean_tokens_per_second", 0)

        table += f"| {model_id} | {accuracy:.2f} | {latency:.3f} | {tps:.1f} |\n"

    return table
