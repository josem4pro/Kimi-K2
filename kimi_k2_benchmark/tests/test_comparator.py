"""
TDD Tests for src/comparator.py
These tests MUST FAIL initially (RED phase) before implementation.
"""
import pytest
from pathlib import Path
import json


class TestMetricsComputation:
    """Tests for computing metrics from raw results"""

    def test_compute_metrics_returns_dict(self):
        """Should return dictionary of computed metrics"""
        from src.comparator import compute_metrics

        raw_results = [
            {
                "model_id": "kimi_k2_normal",
                "benchmark_id": "test.case_001",
                "metrics": {
                    "correctness": True,
                    "total_time": 2.5,
                    "tokens_per_second": 45.0
                }
            },
            {
                "model_id": "kimi_k2_normal",
                "benchmark_id": "test.case_002",
                "metrics": {
                    "correctness": False,
                    "total_time": 3.0,
                    "tokens_per_second": 40.0
                }
            }
        ]

        metrics = compute_metrics(raw_results)

        assert isinstance(metrics, dict)
        assert "kimi_k2_normal" in metrics

    def test_compute_accuracy_percentage(self):
        """Should compute accuracy as percentage of correct answers"""
        from src.comparator import compute_metrics

        raw_results = [
            {"model_id": "m1", "metrics": {"correctness": True}},
            {"model_id": "m1", "metrics": {"correctness": True}},
            {"model_id": "m1", "metrics": {"correctness": False}},
            {"model_id": "m1", "metrics": {"correctness": True}},
        ]

        metrics = compute_metrics(raw_results)

        # 3 out of 4 correct = 75%
        assert metrics["m1"]["accuracy"] == 75.0

    def test_compute_average_latency(self):
        """Should compute mean latency across results"""
        from src.comparator import compute_metrics

        raw_results = [
            {"model_id": "m1", "metrics": {"total_time": 2.0}},
            {"model_id": "m1", "metrics": {"total_time": 4.0}},
            {"model_id": "m1", "metrics": {"total_time": 3.0}},
        ]

        metrics = compute_metrics(raw_results)

        assert metrics["m1"]["mean_latency"] == 3.0

    def test_compute_tokens_per_second_average(self):
        """Should compute average tokens/second"""
        from src.comparator import compute_metrics

        raw_results = [
            {"model_id": "m1", "metrics": {"tokens_per_second": 50.0}},
            {"model_id": "m1", "metrics": {"tokens_per_second": 40.0}},
        ]

        metrics = compute_metrics(raw_results)

        assert metrics["m1"]["mean_tokens_per_second"] == 45.0

    def test_group_metrics_by_benchmark_category(self):
        """Should group metrics by benchmark category (reasoning, coding, etc.)"""
        from src.comparator import compute_metrics

        raw_results = [
            {"model_id": "m1", "benchmark_id": "reasoning.puzzle.001", "metrics": {"correctness": True}},
            {"model_id": "m1", "benchmark_id": "reasoning.puzzle.002", "metrics": {"correctness": False}},
            {"model_id": "m1", "benchmark_id": "coding.debug.001", "metrics": {"correctness": True}},
        ]

        metrics = compute_metrics(raw_results)

        # Should have breakdown by category
        assert "by_category" in metrics["m1"]
        assert "reasoning" in metrics["m1"]["by_category"]
        assert "coding" in metrics["m1"]["by_category"]


class TestModelComparison:
    """Tests for comparing models"""

    def test_compare_models_head_to_head(self):
        """Should compare two models and return wins/losses/ties"""
        from src.comparator import compare_models_across_benchmarks

        metrics = {
            "kimi_k2_normal": {
                "accuracy": 75.0,
                "mean_latency": 3.0,
                "mean_tokens_per_second": 45.0
            },
            "qwen3_coder_30b": {
                "accuracy": 70.0,
                "mean_latency": 2.5,
                "mean_tokens_per_second": 55.0
            }
        }

        comparison = compare_models_across_benchmarks(metrics)

        assert "kimi_k2_normal_vs_qwen3_coder_30b" in comparison or "comparison" in comparison

    def test_calculate_heavy_mode_advantage(self):
        """Should calculate percentage advantage of heavy over normal"""
        from src.comparator import compute_heavy_mode_advantage

        metrics = {
            "kimi_k2_normal": {"accuracy": 75.0},
            "kimi_k2_heavy": {"accuracy": 85.0}
        }

        advantage = compute_heavy_mode_advantage(metrics)

        # (85-75)/75 * 100 = 13.33%
        assert advantage["accuracy_advantage"] == pytest.approx(13.33, rel=0.01)

    def test_summarize_wins_losses_ties(self):
        """Should count wins/losses/ties per benchmark case"""
        from src.comparator import summarize_head_to_head

        # Per-case results
        case_results = [
            {"benchmark_id": "test.001", "model_a_correct": True, "model_b_correct": False},
            {"benchmark_id": "test.002", "model_a_correct": False, "model_b_correct": True},
            {"benchmark_id": "test.003", "model_a_correct": True, "model_b_correct": True},
            {"benchmark_id": "test.004", "model_a_correct": True, "model_b_correct": False},
        ]

        summary = summarize_head_to_head("model_a", "model_b", case_results)

        assert summary["wins"] == 2  # model_a wins
        assert summary["losses"] == 1  # model_a loses
        assert summary["ties"] == 1  # both correct


class TestHeavyModeAnalysis:
    """Tests for analyzing heavy mode trajectories"""

    def test_compute_trajectory_diversity(self):
        """Should compute diversity score among 8 trajectories"""
        from src.comparator import compute_trajectory_diversity

        trajectories = [
            "Solution approach A",
            "Different approach B",
            "Solution approach A",  # Duplicate
            "Approach C with variation",
            "Solution approach A",
            "Different approach B",
            "Approach D unique",
            "Solution approach A"
        ]

        diversity = compute_trajectory_diversity(trajectories)

        # Should be between 0 and 1
        assert 0 <= diversity <= 1

    def test_identify_convergence_pattern(self):
        """Should identify if trajectories converge, diverge, or split"""
        from src.comparator import identify_convergence_pattern

        # Unanimous case (all same)
        unanimous = ["42"] * 8
        assert identify_convergence_pattern(unanimous) == "unanimous"

        # Majority case (>50% same)
        majority = ["42"] * 5 + ["43"] * 3
        assert identify_convergence_pattern(majority) == "majority"

        # Split case (no clear majority)
        split = ["42", "43", "44", "42", "43", "44", "45", "46"]
        pattern = identify_convergence_pattern(split)
        assert pattern in ["split", "divergent"]

    def test_compute_hybridization_quality(self):
        """Should assess quality of hybridized output vs best trajectory"""
        from src.comparator import compute_hybridization_quality

        trajectories = ["Good", "Better", "Best", "Good", "Better", "Best", "Good", "Better"]
        hybridized = "Best with additional synthesis"
        ground_truth = "Best answer"

        quality = compute_hybridization_quality(trajectories, hybridized, ground_truth)

        # Should be between 0 and 1
        assert 0 <= quality <= 1


class TestComparisonTables:
    """Tests for generating comparison tables"""

    def test_generate_comparison_table(self):
        """Should generate a formatted comparison table"""
        from src.comparator import generate_comparison_table

        metrics = {
            "kimi_k2_normal": {"accuracy": 75.0, "mean_latency": 3.0},
            "kimi_k2_heavy": {"accuracy": 85.0, "mean_latency": 4.5},
            "qwen3_coder_30b": {"accuracy": 70.0, "mean_latency": 2.5}
        }

        table = generate_comparison_table(metrics)

        # Should be a string or dict that can be rendered as table
        assert table is not None
        # Should include all model names
        assert "kimi_k2_normal" in str(table)
        assert "kimi_k2_heavy" in str(table)
        assert "qwen3_coder_30b" in str(table)
