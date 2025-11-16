# Deep Analysis: Kimi K2 Heavy Mode vs Normal vs Qwen3-Coder:30B

## Executive Summary

Based on controlled benchmarks (5 cases × 3 models = 15 executions), we found:

1. **Heavy Mode provides NO accuracy advantage** in our test suite
2. **Heavy Mode is 24.5% slower** than normal mode
3. **Heavy Mode has higher throughput** (92.2 vs 82.8 tokens/s)
4. **Qwen3-Coder:30B is 3.6x faster** than Kimi Normal (local inference)
5. **Models have complementary strengths** (Kimi: math, Qwen: creative)

---

## Detailed Performance Metrics

### Overall Statistics

| Model | Accuracy | Mean Latency | Tokens/s | Cost/Query |
|-------|----------|--------------|----------|------------|
| **kimi_k2_normal** | 80% | 22.66s | 82.8 | ~$0.02-0.05 |
| **kimi_k2_heavy** | 80% | 28.22s | 92.2 | ~$0.10-0.25 |
| **qwen3_coder_30b** | 80% | 6.21s | 117.7 | $0 (local) |

### Per-Category Accuracy

```
Category     | Kimi Normal | Kimi Heavy | Qwen3-Coder
-------------|-------------|------------|-------------
Reasoning    | 100%        | 100%       | 100%
Coding       | 100%        | 100%       | 100%
Math         | 100%        | 100%       | 0% ⚠️
Creative     | 0% ⚠️       | 0% ⚠️      | 100%
```

**Critical Finding**: Models have **complementary weaknesses**:
- Kimi K2 struggles with creative/stylistic tasks
- Qwen3-Coder struggles with competition-level math

---

## Heavy Mode Analysis

### Hypothesis vs Reality

**Hypothesis**: Heavy mode (8 parallel trajectories + hybridization) should excel at:
- Complex reasoning problems
- Tasks requiring exploration of multiple solution paths
- Problems with non-obvious solutions

**Reality (based on our tests)**:
- No measurable accuracy improvement
- Consistent 24-50% latency overhead
- Higher throughput (more tokens generated)
- Same final answers as normal mode

### Why Heavy Mode Didn't Improve Accuracy

Possible explanations:
1. **Test cases not complex enough** - May need deeper recursive problems
2. **Convergence to same solution** - 8 trajectories all find same answer
3. **Hybridization doesn't add value** - When trajectories agree, nothing to hybridize
4. **API doesn't expose trajectories** - We can't see internal diversity

### When Heavy Mode MIGHT Help

Based on theory and our observations:
- Tasks with **multiple valid approaches** (not our binary correct/wrong cases)
- Problems requiring **diverse perspectives** (philosophical, design)
- Scenarios where **exploration breadth matters** more than depth

---

## Qwen3-Coder:30B Analysis

### Strengths
- **Fastest inference**: 6.21s vs 22-28s for Kimi
- **Highest throughput**: 117.7 tokens/s
- **Zero cost**: Local inference
- **Creative tasks**: Excels at style transfer, writing

### Weaknesses
- **Math reasoning**: Failed competition-level problem (sum of divisors)
- **May lack extended context**: Not tested beyond 4K tokens

### Use Case Recommendations

**Use Qwen3-Coder:30B for:**
- Code generation and refactoring
- Creative writing and style tasks
- Quick local iterations
- Cost-sensitive workflows

**Use Kimi K2 for:**
- Mathematical reasoning
- Competition-level problems
- Tasks requiring extended thinking
- When accuracy > speed

---

## Heavy Mode Cost-Benefit Analysis

### Costs
- **Latency**: +24.5% slower (28.2s vs 22.7s)
- **API cost**: Likely 8x token consumption (8 trajectories)
- **No observable benefit** in our test suite

### Benefits
- **Higher throughput**: More detailed responses
- **Potential for diversity** (not measured in our tests)
- **May help with truly complex problems**

### Recommendation

**Default to Normal Mode** unless:
1. You need maximum response detail (throughput)
2. You're solving highly complex multi-step problems
3. You have budget for experimentation

---

## Decision Tree: When to Use Each Model

```
Start: What's your priority?
├─ Maximum Accuracy?
│   ├─ Math/Reasoning → Kimi K2 Normal ✓
│   ├─ Creative/Writing → Qwen3-Coder ✓
│   └─ Coding → Either (both 100%)
├─ Minimum Latency?
│   └─ Qwen3-Coder (6.2s) ✓
├─ Zero Cost?
│   └─ Qwen3-Coder (local) ✓
├─ Complex Multi-Step Reasoning?
│   └─ Try Kimi Heavy (monitor results)
└─ General Purpose?
    └─ Kimi Normal (balanced)
```

---

## Limitations of This Analysis

1. **Sample size**: Only 5 test cases
2. **Heavy mode opacity**: Can't inspect 8 trajectories
3. **No stress testing**: Didn't test extreme contexts (200K tokens)
4. **Single-turn only**: No multi-turn conversations
5. **Binary correctness**: Simple pass/fail metric

### Recommended Next Steps

1. **Expand test suite** to 50+ cases across more categories
2. **Test extreme contexts** (100K+ tokens) where heavy mode might shine
3. **Monitor actual API costs** for heavy mode
4. **Try problems with subjective answers** where trajectory diversity matters
5. **Request trajectory visibility** from Chutes.ai API

---

## Conclusion

**For José's workflow:**

1. **Use Qwen3-Coder:30B** for daily coding tasks (fast, free, accurate)
2. **Use Kimi K2 Normal** for mathematical reasoning and complex problems
3. **Avoid Heavy Mode** until proven necessary (extra cost, no accuracy gain)
4. **Monitor model updates** - Heavy mode may improve with future releases

The 8-trajectory heavy mode is an interesting architectural choice, but in practice:
- It slows down inference
- It doesn't improve accuracy (for our tests)
- It costs more
- Its main benefit (trajectory diversity) isn't measurable via current API

**Bottom Line**: Normal mode is currently the sweet spot for Kimi K2.

---

*Analysis generated: 2025-11-16*
*Session ID: rtx_071226_2321650_f5b85b5d*
