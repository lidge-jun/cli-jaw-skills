# Load & Performance Testing

> Deep reference for `jaw-dev-testing` §1.3 risk-first priorities and CI pipeline performance gates.

**Last reviewed**: 2026-06-16
**Applies to**: k6 0.52.x, Locust 2.x, Node 22+, Python 3.12+
**When to read**: `task_tags` includes `performance`, `load_test`, or C3+ production-facing API work
**Canonical owner**: `jaw-dev-testing` — infrastructure-level performance (auto-scaling, resource sizing) → `jaw-dev-devops`

---

## §1 When to Load Test

Load testing is required when **any** of these apply:

- [ ] C3+ classification with production traffic
- [ ] Public API with external consumers
- [ ] Expected traffic spike (launch, campaign, seasonal)
- [ ] Infrastructure migration (DB, CDN, region)
- [ ] Performance SLO defined in product requirements

Skip for C0–C2 internal tools with <10 concurrent users. Use unit benchmarks (`vitest bench`, `pytest-benchmark`) for micro-optimization instead.

---

## §2 Tool Selection

| Criterion | k6 0.52 ✅ | Locust 2.x ✅ | Artillery 2.x |
|-----------|-----------|--------------|---------------|
| **Language** | JavaScript/TypeScript | Python | YAML + JS hooks |
| **Protocol** | HTTP, gRPC, WebSocket, browser | HTTP, custom | HTTP, WebSocket, Socket.IO |
| **Distributed** | `k6 cloud` / `k6 operator` (K8s) | built-in master/worker | Artillery Cloud |
| **CI integration** | `grafana/setup-k6-action@v1` | `pip install locust` + script | `npx artillery` |
| **Browser perf** | `k6/browser` (Chromium) | ✕ | ✕ |
| **Dashboard** | Grafana Cloud k6 / InfluxDB | built-in web UI | Artillery Cloud |
| **Best for** | JS/TS teams, CI gates, CWV | Python teams, custom protocols | YAML-first, quick smoke |

**Decision rule**: JS/TS stack → k6. Python stack or custom protocol → Locust. Neither is wrong; pick one and standardize.

**Banned**: Running both k6 and Locust in the same project without a documented reason.

---

## §3 Test Types

| Type | Purpose | When | VUs | Duration |
|------|---------|------|-----|----------|
| **Smoke** | Basic function under minimal load | Every PR | 1–5 | 30s |
| **Load** | Normal traffic verification | main merge / nightly | 50–200 | 5–10 min |
| **Stress** | Find breaking point | Pre-release | Ramp to limit | 15–30 min |
| **Spike** | Sudden burst resilience | Pre-release | 0 → max → 0 | 5–10 min |
| **Soak** | Long-term stability (memory leaks, connection pool) | Weekly / pre-release | Normal load | 1–4 hr |

Start with **smoke** in CI. Add load/stress only after smoke is stable.

---

## §4 k6 Quick Start

```javascript
import http from "k6/http";
import { check, sleep } from "k6";

export const options = {
  scenarios: {
    smoke: {
      executor: "shared-iterations",
      vus: 5,
      iterations: 50,
    },
  },
  thresholds: {
    http_req_duration: ["p(95)<300", "p(99)<500"],
    http_req_failed: ["rate<0.01"],
    checks: ["rate==1.0"],
  },
};

export default function () {
  const res = http.get(`${__ENV.BASE_URL}/api/health`);
  check(res, {
    "status 200": (r) => r.status === 200,
    "body has status": (r) => JSON.parse(r.body).status === "ok",
  });
  sleep(1);
}
```

- `thresholds` are the pass/fail gate — without them, the test measures but never judges
- `checks` validate response correctness; `thresholds` on checks enforce the gate
- Run locally: `k6 run --env BASE_URL=http://localhost:3000 tests/perf/smoke.js`
- Run with cloud dashboard: `k6 cloud tests/perf/smoke.js` (requires `K6_CLOUD_TOKEN`)

---

## §5 Measure → Profile → Verify

```
1. Measure    ──→  k6 baseline (smoke → load → record p95/p99/error rate)
       │
2. Profile    ──→  identify bottleneck (traces, flame graphs, DB slow query log)
       │
3. Optimize   ──→  hypothesis-driven change (N+1 fix, cache, query tune)
       │
4. Re-measure ──→  same scenario, compare against baseline
       │
5. Gate       ──→  CI threshold pass → merge; fail → block deploy
```

| Banned | Symptom | Fix |
|--------|---------|-----|
| "It's slow, add cache" without profiling | Cache added but wrong bottleneck | Measure first — `k6 run` → flame graph → then decide |
| Screenshot-only results | No regression detection possible | Export JSON/HTML report: `k6 run --out json=results.json` |
| One-time manual run, no CI | Performance regresses silently | Add smoke to PR pipeline (§6) |

---

## §6 CI Integration

```yaml
# .github/workflows/performance.yml
name: Performance
on:
  pull_request:
    branches: [main]
  push:
    branches: [main]

jobs:
  smoke:
    if: github.event_name == 'pull_request'
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: grafana/setup-k6-action@v1
      - uses: grafana/run-k6-action@v1
        with:
          path: tests/perf/smoke.js
          flags: --env BASE_URL=http://localhost:3000

  load:
    if: github.ref == 'refs/heads/main'
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: grafana/setup-k6-action@v1
      - uses: grafana/run-k6-action@v1
        env:
          K6_CLOUD_TOKEN: ${{ secrets.K6_CLOUD_TOKEN }}
        with:
          path: tests/perf/load.js
          cloud-run-locally: true
```

- **PR**: smoke only (fast, <1 min)
- **main merge**: full load test with cloud dashboard
- **Release branch**: stress + soak (manual trigger or scheduled)
- Threshold failure = non-zero exit = blocked deploy

**Banned**: Load testing directly against production. Use staging or a dedicated perf environment.

---

## §7 Anti-Patterns

| Banned | Symptom | Fix |
|--------|---------|-----|
| Threshold-free load test | "We ran k6" but no pass/fail judgment | Add `thresholds` with p95/p99/error rate targets |
| Production load test | Degraded user experience, potential outage | Use staging or isolated perf environment |
| Tool salad (k6 + Locust + Artillery in one project) | Inconsistent results, maintenance burden | Pick one (§2 decision table), standardize |
| Hardcoded URLs in test scripts | Breaks across environments | Use `__ENV.BASE_URL` or equivalent env vars |
| Ignoring soak tests | Memory leaks and connection pool exhaustion ship | Schedule weekly soak on staging |

## Pre-flight

Before merging a load test change:

- [ ] `thresholds` defined with p95, p99, and error rate targets
- [ ] Test runs against staging or local — never production
- [ ] `BASE_URL` parameterized via environment variable
- [ ] CI workflow updated (`smoke` on PR, `load` on main)
- [ ] Results exported as JSON/HTML, not screenshots
- [ ] Measure → Profile → Verify loop documented for any optimization claim
- [ ] Cross-ref: `jaw-dev-devops` for infra-level scaling; `ci-pipeline.md` for pipeline placement

---

## Cross-References

- `jaw-dev-testing` §5 CI Pipeline — pipeline stage ordering
- `references/ci-pipeline.md` — full GHA/GitLab CI templates
- `jaw-dev-backend` §9 — p95 SLO definitions and observability
- `jaw-dev-devops` — infrastructure-level performance (auto-scaling, resource allocation)
