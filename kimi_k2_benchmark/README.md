# Kimi K2 Benchmark Framework

Comprehensive benchmark framework for evaluating **Kimi K2 Heavy Mode vs Normal Mode vs Qwen3-Coder:30B**.

## Objective

1. **Evaluate Kimi K2 Heavy Mode** - 8 parallel trajectories with hybridization
2. **Compare Kimi K2 (normal/heavy) vs Qwen3-Coder:30B** (local Ollama)
3. **Deep analysis of hybridization mechanics** - diversity, convergence, failure modes

## Project Structure

```
kimi_k2_benchmark/
├── config/
│   ├── models.yaml          # Model configurations (Kimi, Qwen)
│   ├── benchmarks.yaml      # Benchmark definitions
│   └── metrics.yaml         # Metrics and evaluation criteria
├── benchmarks/
│   ├── reasoning/           # Multi-hop, constraint satisfaction
│   ├── coding/              # Optimization, refactoring, debugging
│   ├── math/                # Competition problems, proofs
│   ├── creative/            # Style transfer, narrative
│   ├── agentic/             # Tool chains, replanning
│   └── stress/              # Adversarial, extreme context
├── results/
│   ├── raw/                 # Raw JSON/CSV results
│   ├── analysis/            # Jupyter notebooks
│   └── visualizations/      # Charts and final reports
├── src/
│   ├── evaluator.py         # Main benchmark runner
│   ├── comparator.py        # Model comparison logic
│   └── reporter.py          # Report generation
├── tests/                   # TDD test suite
├── docs/
│   └── adr/                 # Architecture Decision Records
├── requirements.txt
└── pyproject.toml
```

## Models Under Test

| Model | Provider | Heavy Mode | Local | Cost |
|-------|----------|------------|-------|------|
| Kimi K2 Normal | Chutes.ai | No | No | Per token |
| Kimi K2 Heavy | Chutes.ai | Yes (8 trajectories) | No | Per token |
| Qwen3-Coder:30B | Ollama | N/A | Yes | Free |

## Benchmark Categories

- **Reasoning** (60 cases): Multi-hop puzzles, recursive decomposition, constraints, causal chains
- **Coding** (39 cases): Optimization, refactoring, multi-paradigm, debugging, architecture
- **Math** (49 cases): Competition (IMO/Putnam/AIME), proofs, applied modeling
- **Creative** (10 cases): Style transfer, narrative coherence
- **Agentic** (16 cases): Long tool chains, dynamic replanning, multi-agent
- **Stress** (26 cases): Adversarial inputs, extreme context (200K tokens), 300 tool calls

**Total: 200+ benchmark cases**

## Key Metrics

- **Correctness**: Accuracy percentage
- **Reasoning Depth**: Length of reasoning chain
- **Performance**: Tokens/second, latency
- **Code Quality**: Cyclomatic complexity, maintainability
- **Heavy Mode Specific**: Trajectory diversity, hybridization quality, convergence patterns
- **Comparative**: Heavy mode advantage, wins/losses/ties vs Qwen

## Quick Start

```bash
# 1. Setup environment
cd kimi_k2_benchmark
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 2. Configure credentials
cp .env.template .env
# Edit .env with your API keys (see ~/.env on RTX)

# 3. Run tests (TDD)
pytest tests/

# 4. Execute benchmarks
python -m src.evaluator --models all --benchmarks all

# 5. Generate report
python -m src.reporter --output results/visualizations/report.md
```

## Architecture Decision Records

- **ADR-001**: Modular Python framework (evaluator/comparator/reporter)
- **ADR-002**: Results storage (raw → analysis → visualizations)
- **ADR-003**: Execution schema with full metadata

## Session ID for Commits

```
rtx_071226_2321650_f5b85b5d
```

## Phase Status

- [x] **Phase 1**: Architecture and Plan (CURRENT)
- [ ] **Phase 2**: TDD Framework (BLOCKING)
- [ ] **Phase 3**: Implementation
- [ ] **Phase 4**: Execute Benchmarks
- [ ] **Phase 5**: Deep Analysis Heavy Mode
- [ ] **Phase 6**: Final Report and Recommendations

---

**Author**: Jose @ RTX (192.168.0.103)
**Date**: 2025-11-16
**License**: MIT
