# wp6 — PR, merge and deployment (diff-level)

## Checks before the PR

```bash
python3 scripts/validate_public_surface.py    # exits 0, prints the measured inventory
python3 -m pytest -q                          # whole suite, office suites skipped
                                              # pytest is absent from the local python3
                                              # (3.14): use a scratch venv locally and treat
                                              # the CI run as authoritative
git diff --check                              # whitespace
```

Plus the negative demonstrations wp2 and wp4 owe: a synthetic frontmatter breakage and a
synthetic registry drift each produce a named failure, then are reverted.

## Files this task may commit

`scripts/validate_public_surface.py`, `scripts/sync_public_surface.py`, `tests/**`,
`pyproject.toml`, `.github/workflows/ci.yml`, `README.md`,
`docs/index.html`, and `devlog/_plan/260908_validator_tests/`. Nothing else — note `registry.json` is NOT
edited: the fold keeps every entry and fixes the detector instead. The
runtime cleanup (wp5) touches no repository file.

## PR

Base `main`, head `codex/validator-tests`. The description leads with the behavior
change — CI stops failing on bookkeeping and starts failing on broken skills — then the
test layout, the registry normalization, and the runtime cleanup as a separate operational
note. Wait for CI, merge.

## Deployment

"Deploy" here means the runtime, since this repo is source material: the wp5 cleanup is
the deployment, and it is confirmed by re-reading `~/.cli-jaw/skills` after the merge and
recording the final inventory. If the runtime pulls from this repo by a sync job rather
than by copy, note the mechanism and whether a refresh is needed.

## Acceptance

- CI green at the PR head; PR merged.
- Runtime re-read recorded in `evidence/`.
- Worktree removed after merge.

