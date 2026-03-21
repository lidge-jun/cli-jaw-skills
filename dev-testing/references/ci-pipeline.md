# CI Pipeline Templates
> Deep reference for `dev-testing` §5 CI Pipeline Integration.

## 1. Node.js Workflow Template

```yaml
name: node-test
on:
  push:
  pull_request:
concurrency:
  group: node-test-${{ github.ref }}
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
  test:
    needs: quality
    runs-on: ubuntu-latest
    strategy:
      fail-fast: false
      matrix: { node-version: [20, 22], shard: [1, 2, 3] }
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with: { node-version: ${{ matrix.node-version }}, cache: npm }
      - run: npm ci
      - run: npx vitest run --coverage --shard=${{ matrix.shard }}/3
      - run: npm run test:contract
  e2e:
    needs: test
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with: { node-version: 22, cache: npm }
      - run: npm ci
      - run: npx playwright install --with-deps chromium
      - run: npx playwright test
```

## 2. Python Workflow Template

```yaml
name: python-test
on:
  push:
  pull_request:
jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      fail-fast: false
      matrix:
        python-version: ["3.11", "3.12", "3.13"]
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: ${{ matrix.python-version }}
          cache: pip
      - run: pip install -r requirements-dev.txt
      - run: pytest --cov --cov-report=xml -n auto
      - run: pytest tests/contracts -q
      - run: pip-audit --strict
```

## 3. Matrix / Parallelization

| Axis | Include When | Example |
|------|--------------|---------|
| runtime versions | library or SDK compatibility matters | Node 20/22, Python 3.11-3.13 |
| OS | native modules or CLI behavior matter | ubuntu + macOS |
| shards | suites exceed CI budget | `1/4..4/4` |

```bash
npx vitest run --shard=2/4
npx playwright test --shard=2/4 --workers=4
pytest -n auto --dist=loadgroup
```

## 4. Coverage Reporting Integration

- publish `lcov.info` or `coverage.xml`
- upload junit / XML results for annotations
- keep contract reports separate from unit coverage
- fail the build when thresholds or diff coverage drop

## 5. Flaky Test Quarantine Strategy

1. detect the flaky test by exact name
2. move it to a quarantine tag or job
3. keep quarantine non-blocking but visible
4. assign an owner and removal deadline
5. restore only after repeated green runs

| Signal | Action |
|--------|--------|
| intermittent timeout | replace implicit timing with deterministic waits |
| order-dependent failure | reset shared state or fixture leakage |
| CI-only HTTP failure | remove live network dependency |
| snapshot variance | stabilize fonts, time, locale, and dynamic regions |

## 6. Recommended Job Order

```text
quality
→ backend / unit / integration
→ contract
→ e2e
→ security
→ coverage aggregation
```
