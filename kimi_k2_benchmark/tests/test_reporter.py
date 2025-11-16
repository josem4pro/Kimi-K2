"""
TDD Tests for src/reporter.py
These tests MUST FAIL initially (RED phase) before implementation.
"""
import pytest
from pathlib import Path
import json


class TestMarkdownReportGeneration:
    """Tests for generating Markdown reports"""

    def test_generate_markdown_report_creates_file(self, tmp_path):
        """Should create a Markdown file with report content"""
        from src.reporter import generate_markdown_report

        metrics = {
            "kimi_k2_normal": {"accuracy": 75.0, "mean_latency": 3.0},
            "kimi_k2_heavy": {"accuracy": 85.0, "mean_latency": 4.5},
            "qwen3_coder_30b": {"accuracy": 70.0, "mean_latency": 2.5}
        }

        out_path = tmp_path / "report.md"
        generate_markdown_report(metrics, out_path)

        assert out_path.exists()
        content = out_path.read_text()
        assert "# " in content  # Has headers
        assert "kimi_k2" in content.lower()

    def test_report_includes_executive_summary(self, tmp_path):
        """Report should have executive summary section"""
        from src.reporter import generate_markdown_report

        metrics = {
            "kimi_k2_normal": {"accuracy": 75.0},
            "kimi_k2_heavy": {"accuracy": 85.0},
            "qwen3_coder_30b": {"accuracy": 70.0}
        }

        out_path = tmp_path / "report.md"
        generate_markdown_report(metrics, out_path)

        content = out_path.read_text()
        assert "summary" in content.lower() or "executive" in content.lower()

    def test_report_includes_comparison_tables(self, tmp_path):
        """Report should include comparison tables"""
        from src.reporter import generate_markdown_report

        metrics = {
            "kimi_k2_normal": {"accuracy": 75.0, "mean_latency": 3.0},
            "kimi_k2_heavy": {"accuracy": 85.0, "mean_latency": 4.5}
        }

        out_path = tmp_path / "report.md"
        generate_markdown_report(metrics, out_path)

        content = out_path.read_text()
        # Should have table markers (| for columns)
        assert "|" in content

    def test_report_includes_heavy_mode_analysis(self, tmp_path):
        """Report should have section for heavy mode analysis"""
        from src.reporter import generate_markdown_report

        metrics = {
            "kimi_k2_normal": {"accuracy": 75.0},
            "kimi_k2_heavy": {
                "accuracy": 85.0,
                "heavy_mode_advantage": 13.33,
                "trajectory_diversity": 0.65
            }
        }

        out_path = tmp_path / "report.md"
        generate_markdown_report(metrics, out_path)

        content = out_path.read_text()
        assert "heavy" in content.lower()

    def test_report_includes_recommendations(self, tmp_path):
        """Report should include recommendations section"""
        from src.reporter import generate_markdown_report

        metrics = {
            "kimi_k2_normal": {"accuracy": 75.0},
            "kimi_k2_heavy": {"accuracy": 85.0},
            "qwen3_coder_30b": {"accuracy": 70.0}
        }

        out_path = tmp_path / "report.md"
        generate_markdown_report(metrics, out_path)

        content = out_path.read_text()
        assert "recommend" in content.lower() or "conclusion" in content.lower()


class TestVisualizationGeneration:
    """Tests for generating visualizations"""

    def test_generate_plots_creates_png_files(self, tmp_path):
        """Should create PNG plot files"""
        from src.reporter import generate_plots

        metrics = {
            "kimi_k2_normal": {"accuracy": 75.0, "mean_latency": 3.0},
            "kimi_k2_heavy": {"accuracy": 85.0, "mean_latency": 4.5},
            "qwen3_coder_30b": {"accuracy": 70.0, "mean_latency": 2.5}
        }

        out_dir = tmp_path / "plots"
        out_dir.mkdir()

        generate_plots(metrics, out_dir)

        # Should create at least one plot
        png_files = list(out_dir.glob("*.png"))
        assert len(png_files) >= 1

    def test_generate_accuracy_comparison_chart(self, tmp_path):
        """Should generate accuracy comparison bar chart"""
        from src.reporter import generate_accuracy_chart

        metrics = {
            "kimi_k2_normal": {"accuracy": 75.0},
            "kimi_k2_heavy": {"accuracy": 85.0},
            "qwen3_coder_30b": {"accuracy": 70.0}
        }

        out_path = tmp_path / "accuracy_comparison.png"
        generate_accuracy_chart(metrics, out_path)

        assert out_path.exists()

    def test_generate_latency_comparison_chart(self, tmp_path):
        """Should generate latency comparison chart"""
        from src.reporter import generate_latency_chart

        metrics = {
            "kimi_k2_normal": {"mean_latency": 3.0},
            "kimi_k2_heavy": {"mean_latency": 4.5},
            "qwen3_coder_30b": {"mean_latency": 2.5}
        }

        out_path = tmp_path / "latency_comparison.png"
        generate_latency_chart(metrics, out_path)

        assert out_path.exists()

    def test_generate_heavy_mode_advantage_chart(self, tmp_path):
        """Should generate chart showing heavy mode advantage by category"""
        from src.reporter import generate_heavy_mode_chart

        category_advantages = {
            "reasoning": 15.0,
            "coding": 10.0,
            "math": 20.0,
            "creative": 5.0,
            "agentic": 25.0,
            "stress": 12.0
        }

        out_path = tmp_path / "heavy_mode_advantage.png"
        generate_heavy_mode_chart(category_advantages, out_path)

        assert out_path.exists()


class TestDataExport:
    """Tests for exporting data in various formats"""

    def test_export_to_csv(self, tmp_path):
        """Should export metrics to CSV file"""
        from src.reporter import export_to_csv

        metrics = {
            "kimi_k2_normal": {"accuracy": 75.0, "mean_latency": 3.0},
            "kimi_k2_heavy": {"accuracy": 85.0, "mean_latency": 4.5}
        }

        out_path = tmp_path / "metrics.csv"
        export_to_csv(metrics, out_path)

        assert out_path.exists()
        content = out_path.read_text()
        # Should have header row with model names
        assert "kimi_k2_normal" in content or "model" in content.lower()

    def test_export_to_json(self, tmp_path):
        """Should export metrics to JSON file"""
        from src.reporter import export_to_json

        metrics = {
            "kimi_k2_normal": {"accuracy": 75.0},
            "kimi_k2_heavy": {"accuracy": 85.0}
        }

        out_path = tmp_path / "metrics.json"
        export_to_json(metrics, out_path)

        assert out_path.exists()

        with open(out_path) as f:
            loaded = json.load(f)
        assert loaded == metrics


class TestDecisionTree:
    """Tests for generating decision tree recommendations"""

    def test_generate_decision_tree(self):
        """Should generate when-to-use decision tree"""
        from src.reporter import generate_decision_tree

        metrics = {
            "kimi_k2_normal": {
                "accuracy": 75.0,
                "mean_latency": 3.0,
                "by_category": {
                    "reasoning": {"accuracy": 80.0},
                    "coding": {"accuracy": 70.0}
                }
            },
            "kimi_k2_heavy": {
                "accuracy": 85.0,
                "mean_latency": 4.5,
                "by_category": {
                    "reasoning": {"accuracy": 95.0},
                    "coding": {"accuracy": 75.0}
                }
            },
            "qwen3_coder_30b": {
                "accuracy": 70.0,
                "mean_latency": 2.5,
                "by_category": {
                    "reasoning": {"accuracy": 65.0},
                    "coding": {"accuracy": 75.0}
                }
            }
        }

        tree = generate_decision_tree(metrics)

        # Should be a structured recommendation
        assert tree is not None
        # Should mention when to use each model
        tree_str = str(tree)
        assert "heavy" in tree_str.lower() or "normal" in tree_str.lower()

    def test_generate_recommendations_list(self):
        """Should generate list of practical recommendations"""
        from src.reporter import generate_recommendations

        metrics = {
            "kimi_k2_normal": {"accuracy": 75.0, "mean_latency": 3.0},
            "kimi_k2_heavy": {"accuracy": 85.0, "mean_latency": 4.5},
            "qwen3_coder_30b": {"accuracy": 70.0, "mean_latency": 2.5}
        }

        recommendations = generate_recommendations(metrics)

        # Should be a list of strings or dict
        assert isinstance(recommendations, (list, dict))
        assert len(recommendations) >= 1
