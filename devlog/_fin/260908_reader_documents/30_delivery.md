# wp4 — Checks, PR and merge (diff-level)

Depends on wp2 and wp3.

## Checks to run on the branch

```bash
python3 scripts/validate_public_surface.py     # expects "validated 226 skills"
python3 -m pytest tests/test_dev_frontend_refresh.py -q   # the only suite CI runs
git diff --check                               # whitespace
```

`tests/test_cjk_regression.py` needs the `officecli` binary and
`requirements-office-tests.txt`; it is not a CI gate and is not run here. If pytest is
missing locally, use a scratch venv and treat the CI run as the authoritative pass.

The validator is the gate that matters: it fails on main today because
`dev/SKILL.md` is 504 lines, so this branch must leave it ≤500 and prove the validator
exits 0 — a green run here is a repair, and the PR description says so plainly.

## Files this task may commit

`dev/SKILL.md`, `dev/references/reader-documents.md`, `dev-pabcd/SKILL.md`,
`dev-scaffolding/SKILL.md`, `diagram/SKILL.md`, `doc-coauthoring/SKILL.md`,
`search/SKILL.md`, `search/references/deep-research.md`, `deep-research/SKILL.md`,
and `devlog/_plan/260908_reader_documents/`. Nothing else. The 24 uncommitted files
in the main checkout belong to other work and are in a different working tree.

## PR

Base `main`, head `codex/reader-documents`. Description leads with the behavior change
(what a report looks like before and after), names the two new references and the
ownership boundary against the Gemini skill, and reports the dev/SKILL.md line repair.
Wait for CI, then merge. Squash is not required; the repo's history uses plain commits.

## Acceptance

- CI green at the PR head and the PR merged (observable: run conclusion + merge commit).
- The linked worktree removed after the merge (observable: `git worktree list`).
- Both forward-use trials recorded under the unit's `evidence/` with the produced
  artifact and an explicit PASS/FAIL line naming the acceptance bullet it satisfies.

