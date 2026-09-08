# wp3 — Modular test suite (diff-level)

Verifier: `python3 -m pytest -q` from the repo root runs every suite; officecli-dependent
tests report as skipped, not failed, on a machine without the binary; CI runs that one
command.

## Layout, modeled on ../opencodex

opencodex splits `tests/` by domain behind one runner. The Python analogue:

```
tests/
  conftest.py            # shared fixtures: skill inventory, registry, repo root
  structure/             # directory shape, line cap, name/dir agreement
    test_skill_layout.py
  frontmatter/           # frontmatter parses, required keys, no duplicate names
    test_frontmatter.py
  registry/              # registry <-> directory correspondence
    test_registry.py
  docs/                  # docs assets and required metadata markers
    test_docs_surface.py
  content/               # existing content regressions
    test_dev_frontend_refresh.py   (moved)
  office/                # binary-dependent suites
    test_cjk_regression.py         (moved)
    test_officecli_data_pipeline.py (moved)
```

`tests/conftest.py` provides the inventory once — `repo_root`, `skill_dirs`,
`skill_frontmatter` (parsed lazily, cached), `registry` — so no test re-walks the tree,
and an `officecli` autouse guard that skips the `office/` package when the binary is
absent. Import the shared logic from scripts/validate_public_surface.py via
importlib.util.spec_from_file_location — the pattern already used at
tests/test_officecli_data_pipeline.py:14-19. There is no package and no scripts/__init__.py,
so a plain `from scripts...` import fails.

**Moving a test one level deeper breaks its root computation.** test_dev_frontend_refresh.py:8
and test_officecli_data_pipeline.py:11 both compute parents[1]; after the move each takes
repo_root from the conftest fixture instead of counting parents.

**test_cjk_regression.py cannot import today**: line 9 does `from conftest import
run_officecli` against a conftest.py that does not exist anywhere in the repo. The new
tests/conftest.py must provide run_officecli for that file to run at all. If the helper
cannot be reconstructed faithfully, the suite is marked officecli and skipped with the
reason recorded, rather than silently passing.

## MODIFY pyproject.toml

testpaths becomes ["tests"] alone. The current value lists docx/tests, xlsx/tests and
pptx/tests — **none of those directories exist**; the config has been pointing at nothing.
Markers stay as declared and the officecli one finally gets used. Keep --import-mode=importlib.

## MODIFY .github/workflows/ci.yml

Replace `python3 -m pytest tests/test_dev_frontend_refresh.py -q` with
`python3 -m pytest -q` — one entry point for the whole suite. Keep the validator step and
the whitespace check.

## Acceptance

- `python3 -m pytest -q` collects and passes from the root; office suites skip cleanly
  without the binary and the skip reason names it.
- Every existing test still runs (moved, not deleted); no test asserts a literal count.
- CI's test step names no individual file.

