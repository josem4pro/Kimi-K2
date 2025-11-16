"""
TDD Tests for src/evaluator.py
These tests MUST FAIL initially (RED phase) before implementation.
"""
import pytest
from pathlib import Path
import json
from unittest.mock import Mock, patch, MagicMock


class TestConfigLoading:
    """Tests for configuration loading"""

    def test_load_models_config(self):
        """Should load models.yaml and return dict of model configs"""
        from src.evaluator import load_configs

        configs = load_configs()

        assert "models" in configs
        assert "kimi_k2_normal" in configs["models"]
        assert "kimi_k2_heavy" in configs["models"]
        assert "qwen3_coder_30b" in configs["models"]

    def test_model_config_has_required_fields(self):
        """Each model config should have provider, model, max_tokens, temperature"""
        from src.evaluator import load_configs

        configs = load_configs()

        for model_id, model_config in configs["models"].items():
            assert "provider" in model_config
            assert "model" in model_config
            assert "max_tokens" in model_config
            assert "temperature" in model_config

    def test_load_benchmarks_config(self):
        """Should load benchmarks.yaml with all categories"""
        from src.evaluator import load_configs

        configs = load_configs()

        assert "benchmarks" in configs
        assert "reasoning" in configs["benchmarks"]
        assert "coding" in configs["benchmarks"]
        assert "math" in configs["benchmarks"]
        assert "creative" in configs["benchmarks"]
        assert "agentic" in configs["benchmarks"]
        assert "stress" in configs["benchmarks"]

    def test_load_metrics_config(self):
        """Should load metrics.yaml with metric definitions"""
        from src.evaluator import load_configs

        configs = load_configs()

        assert "metrics" in configs
        assert "correctness" in configs["metrics"]
        assert "reasoning_depth" in configs["metrics"]


class TestBenchmarkExecution:
    """Tests for benchmark execution"""

    def test_run_single_case_returns_result_object(self):
        """Should return a structured result with all required fields"""
        from src.evaluator import run_single_case

        # Mock case specification
        case_spec = {
            "prompt": "What is 2 + 2?",
            "expected_answer": "4",
            "benchmark_id": "math.simple_addition.case_001"
        }

        result = run_single_case("kimi_k2_normal", "math.simple_addition", case_spec)

        # Check required fields per ADR-003
        assert "execution_id" in result
        assert "timestamp" in result
        assert "model_id" in result
        assert "benchmark_id" in result
        assert "config" in result
        assert "input" in result
        assert "output" in result
        assert "metrics" in result

    def test_run_single_case_captures_reasoning_field(self):
        """Should capture reasoning field if model provides it"""
        from src.evaluator import run_single_case

        case_spec = {
            "prompt": "Solve step by step: 15 * 23",
            "expected_answer": "345",
            "benchmark_id": "math.multiplication.case_001"
        }

        result = run_single_case("kimi_k2_normal", "math.multiplication", case_spec)

        # Output should have reasoning field (may be empty for some models)
        assert "reasoning" in result["output"]

    def test_run_single_case_measures_latency(self):
        """Should measure time_to_first_token and total_time"""
        from src.evaluator import run_single_case

        case_spec = {
            "prompt": "Hello",
            "expected_answer": "response",
            "benchmark_id": "simple.greeting.case_001"
        }

        result = run_single_case("kimi_k2_normal", "simple.greeting", case_spec)

        assert "time_to_first_token" in result["metrics"]
        assert "total_time" in result["metrics"]
        assert result["metrics"]["total_time"] >= 0

    def test_run_benchmark_suite_iterates_all_models(self):
        """Should run benchmarks for all specified models"""
        from src.evaluator import run_benchmark_suite

        model_ids = ["kimi_k2_normal", "kimi_k2_heavy"]
        benchmark_group = "reasoning.multi_hop_puzzles"

        results = run_benchmark_suite(model_ids, benchmark_group)

        # Should have results for both models
        assert len(results) >= 2
        model_ids_in_results = set(r["model_id"] for r in results)
        assert "kimi_k2_normal" in model_ids_in_results
        assert "kimi_k2_heavy" in model_ids_in_results

    def test_heavy_mode_captures_trajectories(self):
        """Heavy mode should capture all 8 trajectories"""
        from src.evaluator import run_single_case

        case_spec = {
            "prompt": "Complex problem",
            "expected_answer": "solution",
            "benchmark_id": "reasoning.complex.case_001"
        }

        result = run_single_case("kimi_k2_heavy", "reasoning.complex", case_spec)

        # Should have heavy_mode_data with trajectories
        assert "heavy_mode_data" in result
        if result["heavy_mode_data"]:  # Only if heavy mode is active
            assert "trajectories" in result["heavy_mode_data"]
            assert "hybridized_output" in result["heavy_mode_data"]


class TestResultPersistence:
    """Tests for saving results"""

    def test_save_raw_result_creates_json_file(self, tmp_path):
        """Should save result to JSON file in results/raw/"""
        from src.evaluator import save_raw_result

        result = {
            "execution_id": "test-123",
            "model_id": "kimi_k2_normal",
            "benchmark_id": "test.benchmark",
            "timestamp": "2025-11-16T12:00:00",
            "output": {"response": "test"}
        }

        output_dir = tmp_path / "results" / "raw"
        output_dir.mkdir(parents=True)

        filepath = save_raw_result(result, output_dir=output_dir)

        assert filepath.exists()
        assert filepath.suffix == ".json"

        # Verify content
        with open(filepath) as f:
            saved_data = json.load(f)
        assert saved_data["execution_id"] == "test-123"

    def test_save_raw_result_uses_unique_filename(self, tmp_path):
        """Filenames should be unique (include timestamp/uuid)"""
        from src.evaluator import save_raw_result

        result1 = {"execution_id": "uuid-1", "model_id": "m1", "benchmark_id": "b1"}
        result2 = {"execution_id": "uuid-2", "model_id": "m1", "benchmark_id": "b1"}

        output_dir = tmp_path / "results" / "raw"
        output_dir.mkdir(parents=True)

        path1 = save_raw_result(result1, output_dir=output_dir)
        path2 = save_raw_result(result2, output_dir=output_dir)

        assert path1 != path2  # Different files


class TestModelClients:
    """Tests for model client creation"""

    def test_create_client_for_chutes(self):
        """Should create OpenAI-compatible client for Chutes.ai"""
        from src.evaluator import create_model_client

        client = create_model_client("kimi_k2_normal")

        assert client is not None
        # Should be configured with Chutes base URL

    def test_create_client_for_ollama(self):
        """Should create client for local Ollama"""
        from src.evaluator import create_model_client

        client = create_model_client("qwen3_coder_30b")

        assert client is not None

    def test_load_api_key_from_env(self):
        """Should load API key from environment"""
        from src.evaluator import get_api_key

        # This should read from ~/.env
        key = get_api_key("chutes")
        assert key is not None
        assert len(key) > 10  # Basic sanity check
