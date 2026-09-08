# wp2 audit — validator rewrite + modular test suite

Commit a3aa9b8 against 10_validator.md / 20_tests.md. All checks run, not read.

## VERDICT: NEAR-PASS

Every plan acceptance criterion holds under execution. Two defects are real but narrow:
one sync regex matches nothing, and one test asserts a tautology.

## Evidence

- Validator exits 0; prints `validated 236 registered skills (52/30/2)`. `rg -n 'EXPECTED_|== *[0-9]{2,}' scripts/ tests/` returns nothing (exit 1).
- Synthetic breakage, each named and non-zero (fixtures created and removed; `git status` clean apart from the pre-existing untracked wp5-runtime.md):
  (a) no frontmatter -> `no parseable frontmatter block`; (b) `frontmatter has no description`;
  (c) `declares name 'something-else' in directory ...`; (d) dangling registry entry ->
  `registry entry points at a missing zz-ghost/SKILL.md`; (e) 505 lines -> `exceeds the 500-line readability limit`.
- Bundles: all six discovered. `static-analysis`->codeql and `terraform`->azure-verified-modules
  are `is_bundle=True` and checked on registry key, so the inner-name divergence passes correctly.
  The other four resolve to `<id>/skills/<id>/SKILL.md` and are `is_bundle=False`, hitting the
  ordinary name check — also correct.
- Block scalars: `description: >-` with two indented lines folds to `"first line second line"`;
  an empty block scalar yields `''` and fails with a named reason (both bare `>-` and `>-` + blank line).
- Suite: `21 passed, 16 deselected` in 0.09s. `-m officecli` collects exactly those 16 and they
  import cleanly (test_cjk_regression.py now resolves `run_officecli`/`run_officecli_json`).
  Run from /tmp against an absolute path: identical result, so no test depends on cwd.
- sync: idempotent — second run prints `no changes needed`, no diff.
- CI parity: `canonical`, `og:image`, `twitter:card` are checked in check_docs_assets()
  (validate_public_surface.py:225) plus both asset files; only the deleted `[0-9]+ inspectable skills`
  grep is gone, which is the intended count removal.
- Python: validator and sync both exit 0 under 3.11 (nearest available to CI's 3.12); no 3.12+/3.14-only
  syntax. `sys.modules` registration before `exec_module` (conftest.py:35) is required — I reproduced
  the `@dataclass ... 'NoneType' object has no attribute '__dict__'` crash without it. Correctly handled.

## BLOCKERS

None.

## NITS

1. sync_public_surface.py:39 — `(\| Skill library \| )\d+( top-level)` matches nothing. README.md:29
   reads `| Skill library | 236 registered skills |`, not "top-level". I tested all 14 patterns
   individually: 13 hit exactly once, this one hits zero. That count silently stops being generated,
   which is the failure mode the rewrite exists to remove. Fix to `( registered skills)`.
2. tests/structure/test_skill_layout.py:22 — `assert skill.path.is_relative_to(skill.path.parents[-2])`
   is vacuously true: `parents[-2]` is `/Users` for an absolute path, so every path passes. It cannot
   fail. Compare against `repo_root / skill.skill_id` instead.
3. README.md:34 still says CI does "skill count validation, known long-skill drift checks, docs drift
   checks" — the vocabulary this commit deliberately retired. Prose the sync script does not own.
4. validate_public_surface.py:237 documents "~104 ... in 15 skills"; actual output is 138 in 15.
   The docstring number is already stale, mildly ironic in this commit.
5. Root `conftest.py` (tracked, from f2fd91b) survives with a duplicate `run_officecli` and
   `OFFICECLI_DEFAULT = ~/.local/bin/officecli` that the new tests/conftest.py does not consult.
   Harmless today, a future collision.
6. Six `*.pyc` files under jaw-hwp/ and jaw-pdf-vision/ are tracked despite .gitignore. Pre-existing.


## Fold (main, 2026-09-08)

No blockers. All six nits folded:

1. The dead `| Skill library | N top-level` pattern is fixed to match the real wording,
   and `sync_public_surface.py` now uses `re.subn` and **exits 1 listing any pattern that
   matched nothing**. Running it immediately caught its own dead pattern, which is the
   point: a generator that silently updates nothing is the same failure as a grep that
   silently passes. Idempotent: second run reports "no changes needed", exit 0.
2. The vacuous `parents[-2]` assertion now compares against `repo_root / skill_id`.
3. The README CI row no longer advertises "skill count validation … docs drift checks".
4. The docstring's stale ~104 corrected to ~138.
5. The duplicate `run_officecli` is removed from `tests/conftest.py`; the office suites
   use the root `conftest.py` that already had working helpers, and the CJK import points
   there. One version of the helper, not two.
6. Six tracked `.pyc` files untracked (`git ls-files | rg '\.pyc$'` now empty).

Re-verified after the folds: suite 21 passed / 16 deselected, `-m officecli` collects
exactly 16, validator exits 0, whitespace clean.
