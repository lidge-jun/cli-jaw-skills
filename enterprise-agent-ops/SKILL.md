---
name: enterprise-agent-ops
description: Operate long-lived agent workloads with observability, security boundaries, and lifecycle management. Updated June 2026 with trace-level monitoring, OpenTelemetry, drift detection, and cost attribution.
---

# Enterprise Agent Ops

Use this skill for cloud-hosted or continuously running agent systems that need operational controls beyond single CLI sessions.

## When to Activate

- Deploying agents in production (cloud, on-prem, or hybrid)
- Operating multi-agent systems with SLA requirements
- Setting up monitoring, alerting, and observability for AI agents
- Managing agent security, permissions, and audit trails
- Debugging production agent failures or behavioral drift

## Operational Domains

### 1. Runtime Lifecycle

| Phase | Actions | Controls |
|-------|---------|----------|
| Start | Deploy artifact, inject secrets, warm caches | Health check gate before accepting traffic |
| Run | Process tasks, handle tool calls, manage state | Hard timeout per task, retry budget |
| Pause | Graceful drain, checkpoint state | Preserve in-flight context for resume |
| Stop | Flush logs, archive traces, release resources | Confirm all async work settled |
| Restart | Roll back to last-known-good on repeated failures | Automatic restart with exponential backoff |

### 2. Observability (Trace-Level)

Modern agent observability requires **trace-level visibility** — not just request/response logging.

**What to capture per agent step:**
- Reasoning chain / thinking content (if available)
- Tool call inputs, outputs, and latency
- RAG retrieval queries and returned chunks
- Token consumption (input/output/cache) per step
- Model selection decisions (if using model routing)

**Recommended stack:**
- **OpenTelemetry** for standardized tracing — use semantic conventions for GenAI
- **LangSmith** or **Logfire** for agent-specific trace visualization
- **Grafana + Prometheus** for metrics dashboards
- **Structured JSON logs** with correlation IDs linking traces to business transactions

```python
# OpenTelemetry trace example for an agent step
from opentelemetry import trace

tracer = trace.get_tracer("agent.ops")

with tracer.start_as_current_span("agent.tool_call") as span:
    span.set_attribute("agent.model", "claude-sonnet-4-6")
    span.set_attribute("agent.tool", tool_name)
    span.set_attribute("agent.tokens.input", input_tokens)
    span.set_attribute("agent.tokens.output", output_tokens)
    span.set_attribute("agent.cost_usd", step_cost)
    result = execute_tool(tool_name, tool_input)
    span.set_attribute("agent.tool.success", result.success)
```

### 3. Safety Controls

- **Least-privilege credentials**: Each agent gets only the permissions it needs
- **Scope boundaries**: Define which tools, APIs, and file paths an agent can access
- **Kill switches**: Remote disable via feature flag or admin API
- **Rate limiting**: Per-agent and per-tool rate limits to prevent runaway loops
- **Hard budget caps**: Circuit breakers that halt execution when cost exceeds threshold
- **Human-in-the-loop gates**: Require approval for destructive actions (delete, deploy, payment)

### 4. Change Management

- **Immutable deployment artifacts**: Never patch running agents in-place
- **Canary rollouts**: Test new agent versions on subset of traffic before full deploy
- **Rollback plan**: Every deployment must have a one-command rollback path
- **Audit log**: Record all configuration changes, permission grants, and agent actions
- **Version pinning**: Pin model versions and tool schemas; don't auto-update in production

## Metrics to Track

### Quality Metrics
| Metric | Description | Target |
|--------|-------------|--------|
| Task success rate | % of tasks completed without error | > 95% |
| Hallucination rate | % of outputs flagged as incorrect/fabricated | < 2% |
| Task completion score | Semantic evaluation of output quality (LLM-as-judge) | > 0.85 |

### Operational Metrics
| Metric | Description | Alert Threshold |
|--------|-------------|-----------------|
| Mean retries per task | Average retry attempts before success/failure | > 2.0 |
| Time to recovery | From failure detection to resolution | > 15 min |
| P95 task latency | 95th percentile end-to-end task duration | > 5 min |
| Error rate by class | Breakdown: auth / rate-limit / timeout / tool-error / model-error | Any class > 5% |

### Cost Metrics
| Metric | Description | |
|--------|-------------|---|
| Cost per successful task | Total API spend / successful completions | Track trend |
| Cost per step | Token cost attributed to each agent reasoning step | Detect inefficiency |
| Budget burn rate | Projected spend vs. budget at current consumption | Alert at 80% |

## Drift Detection

Agent behavior can drift silently due to model updates, prompt changes, or data shifts.

**Detection methods:**
1. **Output schema validation**: Verify structured outputs match expected schemas
2. **Behavioral regression tests**: Run golden-set tasks on every deployment
3. **Statistical monitoring**: Track output distribution changes (token length, tool call frequency, error patterns)
4. **LLM-as-judge sampling**: Periodically evaluate a random sample of outputs for quality

```python
# Simple drift detection: compare output distributions
def detect_drift(recent_metrics: list[float], baseline_metrics: list[float], threshold: float = 2.0) -> bool:
    """Alert if recent metrics deviate from baseline by more than threshold standard deviations."""
    import statistics
    baseline_mean = statistics.mean(baseline_metrics)
    baseline_stdev = statistics.stdev(baseline_metrics) or 0.01
    recent_mean = statistics.mean(recent_metrics)
    z_score = abs(recent_mean - baseline_mean) / baseline_stdev
    return z_score > threshold
```

## Incident Pattern

When failure spikes:
1. **Freeze** — halt new rollout, stop canary promotion
2. **Capture** — collect representative traces with full reasoning chains
3. **Isolate** — identify failing route (model? tool? prompt? data?)
4. **Triage** — classify: transient (retry), systematic (fix), external (escalate)
5. **Patch** — apply smallest safe change, never batch fixes during incidents
6. **Verify** — run regression + security checks on the fix
7. **Resume** — gradual traffic increase with monitoring

## Automated Remediation

For known failure classes, implement automated recovery:

```python
REMEDIATION_MAP = {
    "rate_limit": lambda: backoff_and_retry(multiplier=2),
    "model_overloaded": lambda: failover_to_secondary_model(),
    "tool_timeout": lambda: retry_with_extended_timeout(),
    "budget_exceeded": lambda: pause_and_alert_ops(),
    "auth_expired": lambda: refresh_credentials_and_retry(),
}
```

## Deployment Integrations

| Platform | Use Case | Notes |
|----------|----------|-------|
| PM2 | Process management for Node.js agents | Cluster mode for multi-instance |
| systemd | Linux service management | Restart policies, journal logging |
| Docker / K8s | Container orchestration | Resource limits, health probes |
| CI/CD | Deployment pipeline | Gate on regression tests + cost projections |
| Feature flags | Gradual rollout / kill switch | LaunchDarkly, Unleash, or custom |

## Observe → Evaluate → Optimize → Deploy Loop

Production agent ops follows a continuous improvement cycle:

1. **Observe**: Collect traces, metrics, and user feedback
2. **Evaluate**: Score agent performance against quality benchmarks
3. **Optimize**: Tune prompts, adjust routing, update tools based on findings
4. **Deploy**: Push changes through canary → staged → full rollout

Each cycle iteration should be tracked with a timestamp, evidence, and measurable improvement.
