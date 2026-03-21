---
name: dev-testing
description: "Testing guide for orchestrated sub-agents. Covers strategy selection, backend/API harnesses, contract verification, Playwright E2E, CI pipelines, TDD enforcement, security scanning, and coverage gates. Inject when testing or regression verification is required."
license: Complete terms in LICENSE.txt
---
# Testing & QA
This skill covers **test strategy**, **backend & API testing**, **contract testing**, **Playwright browser testing**, **CI pipeline integration**, **TDD enforcement**, **security testing**, and **coverage / quality gates**.
**Balance target**: ~40% Frontend/E2E (Playwright), ~40% Backend/API, ~20% Cross-cutting (CI, Security, TDD, Coverage).
**Ownership boundary**:
- `dev-testing` owns the **test harness**: fixtures, factories, mock policy, API runners, containerized integration tests, Playwright execution, CI jobs, coverage gates, and contract verification.
- **→ Delegated**: root-cause analysis, failure narrowing, bisecting, instrumentation strategy, and debugging playbooks are owned by `dev-debugging`.
- This skill answers: **what test to write, how to run it, and what gate must pass before completion**.
---
## 1. Test Strategy
### 1.1 Models
| Model | Best For | Emphasis |
|-------|----------|----------|
| Test Pyramid | monoliths, libraries | speed, isolation |
| **Testing Trophy** | modern web apps, REST backends | confidence-to-cost |
| Test Honeycomb | microservices, async systems | boundary verification |
```text
Architecture → Strategy Selector
Monolith / library            → Pyramid
Modern web app / REST API     → Trophy
Microservices / event-driven  → Honeycomb
Unsure / full-stack product   → Trophy
```
### 1.2 Recommended Trophy Distribution
| Layer | Default Share | Typical Tools |
|-------|---------------|---------------|
| Static analysis | base layer | `tsc`, ESLint, mypy, Ruff |
| Unit | ~25% | Vitest, Jest, pytest |
| **Integration** | **~50%** | Supertest, httpx, Testcontainers |
| Contract | ~10% | Pact, OpenAPI validators, Schemathesis |
| E2E | ~10% | Playwright |
| Manual / exploratory | ~5% | human review |
### 1.3 Risk-First Priorities
1. auth / session / permission boundaries
2. money movement, quota, credits
3. data mutation and irreversible actions
4. file upload / parsing / external webhooks
5. shared API contracts used by frontend clients
6. error paths, retries, rollback behavior
### 1.4 Harness Selector
| Problem | Primary Harness | Avoid |
|---------|-----------------|-------|
| pure business rule | unit / service test | browser test |
| route + middleware + serialization | API integration test | mocking the route itself |
| DB query / migration / transaction | real DB integration test | fake repository for SQL correctness |
| frontend consuming backend JSON | contract test | manual-only verification |
| rendered critical flow | Playwright smoke | asserting internal React state |
### 1.5 General Rules
- Write tests for **new features, bug fixes, refactors, and behavior changes**.
- Prefer **one behavioral concern per test**.
- Use factories / builders for setup; avoid repeated inline blobs.
- A fast real dependency beats a mock. A mock beats an untested branch.
- If the failure is mysterious, **delegate methodology to `dev-debugging`**, then return here for the regression harness.
---
## 2. Backend & API Testing
> Deep reference: `references/backend-testing.md`
### 2.1 Coverage Map
| Layer | Verify | TypeScript Default | Python Default |
|-------|--------|-------------------|----------------|
| Service layer | validation, orchestration, domain errors | Vitest | pytest |
| API layer | status, envelope, middleware, auth | Supertest | httpx / ASGITransport |
| Repository layer | SQL / ORM correctness | Testcontainers + real DB | Testcontainers + real DB |
| Background jobs | idempotency, retry, dead-letter | Vitest + fake clock | pytest + monkeypatch |
### 2.2 Mock Strategy Hierarchy
```text
real deterministic dependency
→ Testcontainers / ephemeral infra
→ recorded responses / thin fake
→ manual stub / fake
→ framework mock as last resort
```
### 2.3 Service Pattern — TypeScript
```typescript
import { describe, it, expect, vi } from 'vitest';
import { UserService } from '../src/services/user.service';

describe('UserService.create', () => {
  it('normalizes input and creates the user', async () => {
    const repo = { findByEmail: vi.fn().mockResolvedValue(null), create: vi.fn().mockResolvedValue({ id: 'u_1', email: 'alice@example.com' }) };
    const service = new UserService({ repo });
    const result = await service.create({ email: ' Alice@Example.com ', name: 'Alice' });
    expect(repo.findByEmail).toHaveBeenCalledWith('alice@example.com');
    expect(repo.create).toHaveBeenCalledWith({ email: 'alice@example.com', name: 'Alice' });
    expect(result.id).toBe('u_1');
  });
});
```
### 2.4 Service Pattern — Python
```python
import pytest
from unittest.mock import AsyncMock
from app.services.user_service import UserService

@pytest.mark.asyncio
async def test_create_user_normalizes_input():
    repo = AsyncMock(); repo.find_by_email.return_value = None; repo.create.return_value = {"id": "u_1", "email": "alice@example.com"}
    service = UserService(repo=repo)
    result = await service.create({"email": " Alice@Example.com ", "name": "Alice"})
    repo.find_by_email.assert_awaited_once_with("alice@example.com")
    assert result["id"] == "u_1"
```
### 2.5 API Pattern — TypeScript
```typescript
import request from 'supertest';

it('returns a stable success envelope', async () => {
  const response = await request(app).post('/api/users').send({ email: 'alice@example.com', name: 'Alice' });
  expect(response.status).toBe(201);
  expect(response.body).toMatchObject({ success: true, data: { email: 'alice@example.com' }, meta: expect.any(Object) });
  expect(response.headers['x-request-id']).toBeTruthy();
});
```
### 2.6 API Pattern — Python
```python
import pytest

@pytest.mark.asyncio
async def test_create_user_returns_success_envelope(client):
    response = await client.post("/api/users", json={"email": "alice@example.com", "name": "Alice"})
    body = response.json()
    assert response.status_code == 201
    assert body["success"] is True
    assert body["data"]["email"] == "alice@example.com"
    assert response.headers["x-request-id"]
```
### 2.7 Database Truth with Testcontainers
Use a **real database** when verifying migrations, transactions, unique constraints, foreign keys, query translation, and performance-sensitive SQL.
```typescript
import { PostgreSqlContainer } from '@testcontainers/postgresql';
let pg: Awaited<ReturnType<PostgreSqlContainer['start']>>;
beforeAll(async () => { pg = await new PostgreSqlContainer('postgres:16-alpine').start(); process.env.DATABASE_URL = pg.getConnectionUri(); });
afterAll(async () => { await pg.stop(); });
```
```python
from testcontainers.postgres import PostgresContainer
@pytest.fixture(scope="session")
def pg_url():
    with PostgresContainer("postgres:16-alpine") as container:
        yield container.get_connection_url()
```
### 2.8 Fixture / Seed Synchronization
- Prefer builders / factories over copied JSON snapshots.
- Keep shared contract examples in `fixtures/contracts/` or equivalent.
- Seed data should expose **stable IDs** used by Playwright smoke flows.
- If frontend mocks drift from backend fixtures, write or update a **contract test first**.
---
## 3. Contract Testing
Contract tests protect the **frontend↔backend boundary**. They sit between API tests and browser tests.
**Rule**: Playwright proves the experience. Contract tests prove the shared shape.
### 3.1 Contract-Stable Surface
- response envelope: `success`, `data`, `error`, `meta`
- error taxonomy: HTTP status + machine-readable `error.code`
- pagination fields, auth headers, cookie behavior
- `requestId` propagation
- nullability, timestamps, enums, money serialization
### 3.2 Contract Options
| Style | Best For | Tooling |
|-------|----------|---------|
| consumer-driven contract | rapidly changing frontend/backend teams | Pact |
| schema-first contract | OpenAPI-led backends | OpenAPI validators, Schemathesis |
| type-level contract | TS monorepos | shared types / codegen |
| full-stack smoke | final user confidence | Playwright |
### 3.3 Consumer Contract — TypeScript (Full Verification Loop)
```typescript
import { PactV3, MatchersV3 } from '@pact-foundation/pact';
import { resolve } from 'path';

const provider = new PactV3({
  consumer: 'web-frontend',
  provider: 'api-backend',
  dir: resolve(__dirname, '..', 'pacts'),
});

describe('User Profile Contract', () => {
  it('accepts the user profile contract', async () => {
    // 1. Define the expected interaction
    provider
      .given('user profile exists')
      .uponReceiving('a request for user profile')
      .withRequest({ method: 'GET', path: '/api/me' })
      .willRespondWith({
        status: 200,
        body: {
          success: true,
          data: {
            id: MatchersV3.string('u_1'),
            email: MatchersV3.email('alice@example.com'),
          },
          meta: MatchersV3.like({ requestId: 'req_123' }),
        },
      });

    // 2. Execute the test against the Pact mock server
    await provider.executeTest(async (mockServer) => {
      const response = await fetch(`${mockServer.url}/api/me`);
      const body = await response.json();

      // 3. Assert the consumer's expectations
      expect(response.status).toBe(200);
      expect(body.success).toBe(true);
      expect(body.data.id).toBeDefined();
      expect(body.data.email).toContain('@');
      expect(body.meta.requestId).toBeDefined();
    });
    // 4. Pact file is auto-written to `pacts/` dir → publish to broker → provider verifies
  });
});
```
### 3.4 Schema Verification — Python
```python
import schemathesis
schema = schemathesis.openapi.from_path("openapi.yaml")
@schema.parametrize(endpoint="/api/users", method="POST")
def test_openapi_contract(case):
    response = case.call_asgi(create_app(testing=True))
    case.validate_response(response)
```
### 3.5 Rules
- Contract tests are **mandatory** when frontend and backend are developed in parallel.
- E2E success does **not** replace provider verification.
- Store golden examples near the contract, not inside one app only.
- If the shape is intentionally breaking, update the contract first, then all consumers.
---
## 4. Playwright Browser Testing
Use Playwright after API and contract tests are already trustworthy. Browser tests should validate rendered flows, accessibility-critical interactions, and real integration seams that lower layers cannot prove alone.
**Helper Scripts Available**:
- `scripts/with_server.py` - Manages server lifecycle (supports multiple servers)
**Always run scripts with `--help` first** to see usage. DO NOT read the source until you try running the script first and find that a customized solution is abslutely necessary. These scripts can be very large and thus pollute your context window. They exist to be called directly as black-box scripts rather than ingested into your context window.
## Decision Tree: Choosing Your Approach
```
User task → Static HTML? → Read file → find selectors → write Playwright script
         → Dynamic app? → Server running? → No: `python scripts/with_server.py --help`
                                           → Yes: Recon-then-action (navigate → screenshot → selectors → act)
```
## Example: Using with_server.py
```bash
# Single server:
python scripts/with_server.py --server "npm run dev" --port 5173 -- python your_automation.py

# Multiple servers:
python scripts/with_server.py \
  --server "cd backend && python server.py" --port 3000 \
  --server "cd frontend && npm run dev" --port 5173 \
  -- python your_automation.py
```
## Reconnaissance-Then-Action Pattern
1. Wait for `networkidle` → 2. Screenshot/inspect DOM → 3. Identify selectors → 4. Execute actions

❌ **Don't** inspect DOM before `networkidle` on dynamic apps
✅ **Do** `page.wait_for_load_state('networkidle')` before inspection

## Best Practices
- **Use bundled scripts as black boxes** — run `--help` first, invoke directly.
- Use `sync_playwright()` for synchronous scripts; always close the browser.
- Use descriptive selectors: `text=`, `role=`, CSS, or IDs.
- Add waits: `page.wait_for_selector()` or `page.wait_for_timeout()`.
## Reference Files
- **examples/** - Examples showing common patterns:
  - `element_discovery.py` - Discovering buttons, links, and inputs on a page
  - `static_html_automation.py` - Using file:// URLs for local HTML
  - `console_logging.py` - Capturing console logs during automation
### Browser Testing Rules
- Run **contract tests and API tests first** for broken-data bugs.
- Use Playwright for **rendered truth**, not as a replacement for service tests.
- Prefer one smoke flow per critical path over many brittle micro-flows.
- If a failure looks like data-shape drift, go back to **§2 Backend & API Testing** or **§3 Contract Testing**.
---
## 5. CI Pipeline Integration
> Full workflow templates: `references/ci-pipeline.md`
### 5.1 Pipeline Order
```text
quality (lint / typecheck)
→ unit + integration tests
→ contract tests
→ Playwright E2E
→ security scan
→ coverage aggregation + artifacts
```
### 5.2 GitHub Actions Template
```yaml
name: test
on:
  push:
  pull_request:
concurrency:
  group: test-${{ github.ref }}
  cancel-in-progress: true
jobs:
  quality:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with: { node-version: 22, cache: npm }
      - run: npm ci
      - run: npm run lint
      - run: npx tsc --noEmit
  backend-tests:
    needs: quality
    runs-on: ubuntu-latest
    strategy:
      fail-fast: false
      matrix: { node-version: [20, 22], shard: [1, 2] }
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with: { node-version: ${{ matrix.node-version }}, cache: npm }
      - run: npm ci
      - run: npx vitest run --coverage --shard=${{ matrix.shard }}/2
  contract-tests:
    needs: backend-tests
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: npm ci
      - run: npm run test:contract
  e2e:
    needs: contract-tests
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with: { node-version: 22, cache: npm }
      - run: npm ci
      - run: npx playwright install --with-deps chromium
      - run: npx playwright test --shard=1/1
```
### 5.3 Matrix & Parallelization
| Dimension | When to Use |
|-----------|-------------|
| Node / Python version matrix | packages, SDKs, shared libraries |
| OS matrix | native modules, CLI behavior |
| shard matrix | large suites exceeding CI budget |
```bash
npx vitest run --shard=1/4
npx playwright test --shard=1/4 --workers=4
pytest -n auto --dist=loadgroup
```
### 5.4 Flaky Test Remediation
| Symptom | First Fix |
|---------|-----------|
| passes locally, fails in CI | deterministic seeds, containerized deps, explicit waits |
| order-dependent failure | reset shared state in fixtures |
| green on retry only | remove wall-clock / random assumptions |
| screenshot noise | stable CI image, mask dynamic regions |
Protocol: detect → quarantine if blocking → assign owner → reinstate after repeated green runs.
### 5.5 Rules
- Do not let Playwright be the **only** blocking job.
- Contract tests should run **before** browser tests.
- Upload artifacts for failures: coverage, junit, traces, screenshots.
- Fail the build on broken thresholds, not only test exit codes.
---
## 6. TDD Enforcement Mode
When `ENFORCE_TDD=true` is set in project instructions or explicitly requested, this section becomes mandatory.
### 6.1 RED → GREEN → REFACTOR
1. **RED** — write the failing test first and verify it fails for the right reason.
2. **GREEN** — write the minimum implementation to pass.
3. **REFACTOR** — clean up after green, then rerun the affected suite.
### 6.2 Self-Audit Checklist
| Check | Pass Criteria |
|-------|--------------|
| Test written before implementation? | test file added / updated before or with code |
| Failure observed before fix? | red state was actually executed |
| Behavior-focused assertions? | checks outputs, side effects, contracts |
| Regression locked in? | failing case is now protected by a persistent test |
### 6.3 Default Style
| Style | Best For |
|-------|----------|
| London / mockist | orchestration-heavy boundaries |
| Chicago / classicist | domain logic and transforms |
| **Hybrid** | most production code |
Default to **Hybrid**: mock external systems, keep internal collaboration real unless it becomes too slow or unstable.
### 6.4 Boundary with dev-debugging
- `dev-testing` owns the **regression harness** and enforcement loop.
- `dev-debugging` owns **root-cause methodology** once a failure is mysterious or multi-layered.
- After `dev-debugging` isolates the cause, come back here to lock it in with tests.
---
## 7. Security Testing
**→ Delegated**: threat modeling and secure design policy belong to `dev-security`.
This section covers the **automated test hooks and CI gates** that enforce those rules.
### 7.1 Minimum Security Stack
```text
fast local checks
→ Semgrep / CodeQL gate
→ dependency audit
→ auth / validation regression tests
```
### 7.2 Dependency Scanning Commands
```bash
npm audit --audit-level=high
pip-audit --strict --desc
```
### 7.3 Semgrep Gate
```yaml
- uses: returntocorp/semgrep-action@v1
  with:
    config: >-
      p/default
      p/javascript
      p/typescript
      p/python
```
### 7.4 Security Regressions — TypeScript & Python
```typescript
it('returns 401 without a bearer token', async () => {
  const response = await request(app).get('/api/admin/users');
  expect(response.status).toBe(401);
  expect(response.body.error.code).toBe('AUTH_REQUIRED');
});
```
```python
@pytest.mark.asyncio
async def test_admin_route_requires_auth(client):
    response = await client.get("/api/admin/users")
    assert response.status_code == 401
    assert response.json()["error"]["code"] == "AUTH_REQUIRED"
```
### 7.5 Rules
- dependency audit in CI
- Semgrep or equivalent SAST
- auth / permission regression tests
- validation tests for malicious or malformed input
- a blocking rule for high / critical dependency findings
---
## 8. Coverage & Quality Gates
### 8.1 Minimum Thresholds
| Metric | Minimum | Ideal |
|--------|---------|-------|
| Line coverage | 70% | 85%+ |
| Branch coverage | 60% | 80%+ |
| Function coverage | 80% | 90%+ |
| Diff coverage | 80% | 90%+ |
### 8.2 Outcome Metrics
| Metric | Target |
|--------|--------|
| Defect detection rate | > 80% |
| Mean time to detect | < 1 CI run |
| Test signal-to-noise | > 95% |
| Contract drift rate | near 0 |
### 8.3 Coverage Workflow
1. generate coverage reports
   ```bash
   npm test -- --coverage
   npx vitest run --coverage
   pytest --cov --cov-report=xml
   ```
2. review by priority: auth, payment, mutations, upload, contracts first
3. write targeted tests for the gaps
4. publish artifacts and fail the merge when thresholds drop
### 8.4 Quality Gate Checklist
- [ ] focused unit / service tests
- [ ] API integration tests for changed routes
- [ ] contract tests for shared payload changes
- [ ] Playwright smoke for critical rendered journeys
- [ ] security scan / dependency scan
- [ ] coverage thresholds and diff coverage
- [ ] CI artifacts uploaded for failure analysis
---
## 9. Pre-Flight Test Checklist
### 9.1 Change-Type Routing
- [ ] pure business logic change → add / update unit or service tests
- [ ] API or middleware change → add / update API integration tests
- [ ] shared frontend↔backend payload change → add / update contract tests
- [ ] rendered user flow change → add / update Playwright smoke coverage
- [ ] auth / upload / billing / external integration change → add security or edge-case regression coverage
### 9.2 Harness Readiness
- [ ] fixtures are deterministic and reusable
- [ ] real dependencies are used where correctness matters
- [ ] Testcontainers are used for DB truth, not mocked SQL
- [ ] external APIs are mocked or recorded intentionally, not accidentally called live
- [ ] `ENFORCE_TDD` requirements were followed if enabled
### 9.3 Contract & Data Integrity
- [ ] response envelope remains stable or contract was updated first
- [ ] error codes are asserted, not only HTTP status
- [ ] `requestId`, pagination, and nullability are verified where relevant
- [ ] frontend fixtures do not drift from backend examples
### 9.4 CI & Reporting
- [ ] relevant CI jobs exist and are actually executed
- [ ] sharding / matrix choices match project size
- [ ] flaky failures were investigated instead of blindly retried
- [ ] coverage / junit / trace artifacts are available on failure
### 9.5 Final Rule
If you can only point to a manual click-through or one green Playwright run, the testing story is incomplete.
```text
unit / service
→ API integration
→ contract verification
→ Playwright smoke
→ CI gate + coverage + security scan
```
