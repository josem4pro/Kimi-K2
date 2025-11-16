"""
Kimi K2 Benchmark Evaluator
Main benchmark runner for executing tests against LLM models.
"""
import os
import json
import uuid
import time
from pathlib import Path
from datetime import datetime
from typing import Any

import yaml
from dotenv import load_dotenv
from openai import OpenAI


# Load environment variables from home directory
load_dotenv(Path.home() / '.env')


def load_configs() -> dict[str, Any]:
    """
    Load all configuration files (models, benchmarks, metrics).

    Returns:
        dict with keys 'models', 'benchmarks', 'metrics'
    """
    config_dir = Path(__file__).parent.parent / "config"

    configs = {}

    # Load models.yaml
    with open(config_dir / "models.yaml") as f:
        models_data = yaml.safe_load(f)
        configs["models"] = models_data.get("models", {})

    # Load benchmarks.yaml
    with open(config_dir / "benchmarks.yaml") as f:
        benchmarks_data = yaml.safe_load(f)
        configs["benchmarks"] = benchmarks_data.get("benchmarks", {})

    # Load metrics.yaml
    with open(config_dir / "metrics.yaml") as f:
        metrics_data = yaml.safe_load(f)
        configs["metrics"] = metrics_data.get("metrics", {})

    return configs


def get_api_key(provider: str) -> str:
    """
    Get API key for a provider from environment variables.

    Args:
        provider: Provider name (chutes, moonshot, openrouter)

    Returns:
        API key string
    """
    key_mapping = {
        "chutes": "CHUTES_API_KEY",
        "moonshot": "MOONSHOT_API_KEY",
        "openrouter": "OPENROUTER_API_KEY"
    }

    env_var = key_mapping.get(provider.lower())
    if not env_var:
        raise ValueError(f"Unknown provider: {provider}")

    key = os.getenv(env_var)
    if not key:
        raise ValueError(f"{env_var} not found in environment")

    return key


def create_model_client(model_id: str) -> OpenAI:
    """
    Create an OpenAI-compatible client for a specific model.

    Args:
        model_id: Model identifier (e.g., 'kimi_k2_normal')

    Returns:
        OpenAI client configured for the model's provider
    """
    configs = load_configs()
    model_config = configs["models"].get(model_id)

    if not model_config:
        raise ValueError(f"Model {model_id} not found in config")

    provider = model_config["provider"]

    if provider == "ollama":
        # Ollama doesn't need API key
        client = OpenAI(
            api_key="ollama",  # Dummy key for Ollama
            base_url=model_config.get("api_base", "http://localhost:11434/v1")
        )
    else:
        # Chutes, OpenRouter, Moonshot use API keys
        api_key = get_api_key(provider)
        client = OpenAI(
            api_key=api_key,
            base_url=model_config.get("api_base", "https://llm.chutes.ai/v1")
        )

    return client


def run_single_case(
    model_id: str,
    benchmark_id: str,
    case_spec: dict[str, Any]
) -> dict[str, Any]:
    """
    Execute a single benchmark case against a model.

    Args:
        model_id: Model identifier
        benchmark_id: Benchmark identifier (e.g., 'reasoning.multi_hop')
        case_spec: Case specification with prompt, expected_answer, etc.

    Returns:
        Result dictionary following ADR-003 schema
    """
    configs = load_configs()
    model_config = configs["models"].get(model_id)

    if not model_config:
        raise ValueError(f"Model {model_id} not found")

    # Create client
    client = create_model_client(model_id)

    # Prepare request
    messages = [
        {"role": "system", "content": "You are a helpful AI assistant. Think step by step."},
        {"role": "user", "content": case_spec["prompt"]}
    ]

    # Build request kwargs
    request_kwargs = {
        "model": model_config["model"],
        "messages": messages,
        "max_tokens": model_config.get("max_tokens", 4000),
        "temperature": model_config.get("temperature", 0.3)
    }

    # Add heavy mode if configured
    if model_config.get("heavy_mode"):
        request_kwargs["extra_body"] = {"heavy_mode": True}

    # Execute with timing
    start_time = time.perf_counter()
    first_token_time = None

    try:
        response = client.chat.completions.create(**request_kwargs)
        end_time = time.perf_counter()

        # Extract response
        message = response.choices[0].message
        response_text = message.content or ""

        # Calculate metrics
        total_time = end_time - start_time
        output_tokens = response.usage.completion_tokens if response.usage else 0
        tokens_per_second = output_tokens / total_time if total_time > 0 else 0

        # Simple correctness check (can be enhanced)
        expected = case_spec.get("expected_answer", "")
        correctness = expected.lower() in response_text.lower() if expected else True

        # Build result
        result = {
            "execution_id": str(uuid.uuid4()),
            "timestamp": datetime.utcnow().isoformat(),
            "model_id": model_id,
            "benchmark_id": case_spec.get("benchmark_id", benchmark_id),
            "config": {
                "max_tokens": model_config.get("max_tokens", 4000),
                "temperature": model_config.get("temperature", 0.3),
                "heavy_mode": model_config.get("heavy_mode", False),
                "seed": case_spec.get("seed", None)
            },
            "input": {
                "prompt": case_spec["prompt"],
                "system_prompt": "You are a helpful AI assistant. Think step by step.",
                "context_tokens": response.usage.prompt_tokens if response.usage else 0
            },
            "output": {
                "response": response_text,
                "reasoning": ""  # Would need special handling for reasoning models
            },
            "metrics": {
                "correctness": correctness,
                "time_to_first_token": total_time * 0.1,  # Approximation
                "tokens_per_second": tokens_per_second,
                "total_time": total_time,
                "output_tokens": output_tokens
            }
        }

        # Add heavy mode data if applicable
        if model_config.get("heavy_mode"):
            result["heavy_mode_data"] = {
                "trajectories": [],  # Would need API support to capture
                "hybridized_output": response_text,
                "diversity_score": 0.0,
                "convergence_pattern": "unknown"
            }
        else:
            result["heavy_mode_data"] = None

        return result

    except Exception as e:
        # Return error result
        return {
            "execution_id": str(uuid.uuid4()),
            "timestamp": datetime.utcnow().isoformat(),
            "model_id": model_id,
            "benchmark_id": case_spec.get("benchmark_id", benchmark_id),
            "config": model_config,
            "input": {"prompt": case_spec["prompt"]},
            "output": {
                "response": f"ERROR: {str(e)}",
                "reasoning": ""
            },
            "metrics": {
                "correctness": False,
                "time_to_first_token": 0,
                "tokens_per_second": 0,
                "total_time": 0,
                "output_tokens": 0
            },
            "heavy_mode_data": None
        }


def run_benchmark_suite(
    model_ids: list[str],
    benchmark_group: str
) -> list[dict[str, Any]]:
    """
    Run a benchmark group against multiple models.

    Args:
        model_ids: List of model identifiers
        benchmark_group: Benchmark group identifier (e.g., 'reasoning.multi_hop_puzzles')

    Returns:
        List of result dictionaries
    """
    results = []

    # For now, create dummy cases (in production, load from benchmark files)
    dummy_cases = [
        {
            "prompt": f"Test case for {benchmark_group}",
            "expected_answer": "test",
            "benchmark_id": f"{benchmark_group}.case_001"
        }
    ]

    for model_id in model_ids:
        for case in dummy_cases:
            result = run_single_case(model_id, benchmark_group, case)
            results.append(result)

    return results


def save_raw_result(
    result: dict[str, Any],
    output_dir: Path | None = None
) -> Path:
    """
    Save a benchmark result to JSON file.

    Args:
        result: Result dictionary
        output_dir: Directory to save to (defaults to results/raw/)

    Returns:
        Path to saved file
    """
    if output_dir is None:
        output_dir = Path(__file__).parent.parent / "results" / "raw"

    output_dir.mkdir(parents=True, exist_ok=True)

    # Create unique filename
    execution_id = result.get("execution_id", str(uuid.uuid4()))
    timestamp = result.get("timestamp", datetime.utcnow().isoformat())
    timestamp_safe = timestamp.replace(":", "-").replace(".", "-")

    filename = f"{execution_id}_{timestamp_safe}.json"
    filepath = output_dir / filename

    with open(filepath, "w") as f:
        json.dump(result, f, indent=2, default=str)

    return filepath
