---
name: context-compression
description: This skill should be used when the user asks to "compress context", "summarize conversation history", "implement compaction", "reduce token usage", or mentions context compression, structured summarization, tokens-per-task optimization, or long-running agent sessions exceeding context limits.
---

# Context Compression Strategies

When agent sessions generate millions of tokens of conversation history, compression becomes mandatory. Optimize for tokens per task (total tokens to complete a task, including re-fetching costs), not tokens per request.

## When to Activate

- Agent sessions exceeding context window limits
- Codebases exceeding context windows (5M+ token systems)
- Designing conversation summarization strategies
- Debugging cases where agents "forget" modified files

## Three Approaches

1. **Anchored Iterative Summarization**: Maintain structured, persistent summaries with explicit sections for session intent, file modifications, decisions, and next steps. On compression, summarize only the newly-truncated span and merge with existing summary. Structure forces preservation by dedicating sections to specific information types.

2. **Opaque Compression**: Produce compressed representations optimized for reconstruction fidelity. Achieves highest compression ratios (99%+) but sacrifices interpretability.

3. **Regenerative Full Summary**: Generate detailed structured summaries on each compression. Readable output but may lose details across repeated cycles due to full regeneration rather than incremental merging.

**Key insight**: structure forces preservation. Dedicated sections act as checklists the summarizer must populate.

## The Artifact Trail Problem

Artifact trail integrity is the weakest dimension across all compression methods (2.2–2.5/5.0). Coding agents need to track:
- Which files were created or modified and what changed
- Which files were read but not changed
- Function names, variable names, error messages

This likely requires specialized handling beyond general summarization: a separate artifact index or explicit file-state tracking.

## Structured Summary Template

```markdown
## Session Intent
[What the user is trying to accomplish]

## Files Modified
- auth.controller.ts: Fixed JWT token generation
- config/redis.ts: Updated connection pooling

## Decisions Made
- Using Redis connection pool instead of per-request connections

## Current State
- 14 tests passing, 2 failing

## Next Steps
1. Fix remaining test failures
2. Run full test suite
```

## Compression Trigger Strategies

| Strategy | Trigger Point | Trade-off |
|----------|---------------|-----------|
| Fixed threshold | 70–80% context utilization | Simple but may compress too early |
| Sliding window | Keep last N turns + summary | Predictable context size |
| Importance-based | Compress low-relevance sections first | Complex but preserves signal |
| Task-boundary | Compress at logical task completions | Clean summaries but unpredictable timing |

Sliding window with structured summaries provides the best balance for most coding agent use cases.

## Probe-Based Evaluation

Traditional metrics (ROUGE, embedding similarity) fail to capture functional quality. Use probe questions after compression:

| Probe Type | What It Tests | Example |
|------------|---------------|---------|
| Recall | Factual retention | "What was the original error message?" |
| Artifact | File tracking | "Which files have we modified?" |
| Continuation | Task planning | "What should we do next?" |
| Decision | Reasoning chain | "What did we decide about the Redis issue?" |

## Six Evaluation Dimensions

1. **Accuracy**: Technical details correct? File paths, function names, error codes
2. **Context Awareness**: Response reflects current conversation state?
3. **Artifact Trail**: Agent knows which files were read or modified?
4. **Completeness**: Response addresses all parts of the question?
5. **Continuity**: Work can continue without re-fetching information?
6. **Instruction Following**: Response respects stated constraints?

## Three-Phase Compression Workflow

For large codebases or agent systems exceeding context windows:

1. **Research Phase**: Produce a research document from architecture diagrams, docs, and key interfaces. Output: single structured analysis.
2. **Planning Phase**: Convert research into implementation spec with function signatures, type definitions, and data flow. A 5M token codebase compresses to ~2,000 words.
3. **Implementation Phase**: Execute against the spec rather than raw codebase exploration.

## Implementing Anchored Iterative Summarization

1. Define explicit summary sections matching your agent's needs
2. On first compression, summarize truncated history into sections
3. On subsequent compressions, summarize only new truncated content
4. Merge into existing sections rather than regenerating
5. Track which information came from which compression cycle

## When to Use Each Approach

| Approach | Best when |
|----------|-----------|
| Anchored iterative | Long sessions (100+ messages), file tracking matters, need verifiability |
| Opaque | Maximum token savings needed, short sessions, low re-fetching costs |
| Regenerative | Summary interpretability critical, clear phase boundaries |

## Compression Ratios

| Method | Compression | Quality (5.0) | Notes |
|--------|-------------|---------------|-------|
| Anchored Iterative | 98.6% | 3.70 | Best quality |
| Regenerative | 98.7% | 3.44 | Good quality |
| Opaque | 99.3% | 3.35 | Best compression, quality loss |

The 0.7% additional tokens retained by structured summarization buys 0.35 quality points — worthwhile when re-fetching costs matter.

## Guidelines

1. Optimize for tokens-per-task, not tokens-per-request
2. Use structured summaries with explicit file tracking sections
3. Trigger compression at 70–80% context utilization
4. Use incremental merging rather than full regeneration
5. Test compression quality with probe-based evaluation
6. Track artifact trail separately when file tracking is critical

## References

- [Evaluation Framework Reference](./references/evaluation-framework.md) — probe types and scoring rubrics
- Related skills: context-degradation, context-optimization, evaluation, memory-systems
- Factory Research: Evaluating Context Compression for AI Agents (December 2025)
- Netflix Engineering: "The Infinite Software Crisis" — three-phase workflow (AI Summit 2025)
