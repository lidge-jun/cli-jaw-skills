# Drop the count checks, modularize the tests, clean the duplicates

Loop-spec: satisfy-spec; trigger: the user's 2026-09-08 request to remove pointless number
counting from validation, modularize tests like ../opencodex, normalize the skill list,
clean duplicates against the active runtime, and deploy. Goal: CI that fails only when
something is actually wrong, a test suite that grows by adding a file to a folder, and one
copy of each skill in the runtime. Non-goals: the cli-jaw runtime source repo, codexclaw,
rewriting skill content, the 24 pre-existing dirty files in the main checkout. Verifier:
the rewritten validator, the new suite from its single entry point, and a re-read of
`~/.cli-jaw/skills` after cleanup. Stop: six criteria met and the PR merged. Memory
artifact: `devlog/_plan/260908_validator_tests/`. Escalation: main reclaims a slice after
two distinct leaf failures. Resource bounds: no user cap; Opus-5 subagents unlimited; push,
PR, merge and runtime modification are authorized in this session.

## What is actually wrong today

**The validator counts instead of checking.** `scripts/validate_public_surface.py` asserts
`EXPECTED_SKILLS`, then greps README for the literal strings `"230"`, `"28 skills"`,
`"2 skills"`, greps `docs/index.html` for `"230"`, and (from last cycle) compares a
measured reference-folder count against both files. Every one of these fires on a
bookkeeping mismatch, never on a broken skill. Adding a skill breaks CI until three
documents are hand-edited. Worse, the literals have already published falsehoods: main
carried "47 reference folders" while the tree held 52, and CI stayed green because the
grep only asked whether the string `"47 skills"` appeared *somewhere*.

The 500-line cap is the one size check worth keeping, but it currently reads as drift
detection ("unexpected new SKILL.md line-limit drift") with a hardcoded four-file
exemption. It should read as a readability rule with a named, explained exemption list.

**The tests are two files and a coincidence.** `tests/` holds
`test_cjk_regression.py` (needs the `officecli` binary), `test_dev_frontend_refresh.py`,
and `test_officecli_data_pipeline.py`. CI runs exactly one of them by name, so the other
two are dead weight in CI and break locally for anyone without officecli. `pyproject.toml`
already registers markers (`slow`, `cjk`, `regression`, `officecli`) that nothing skips on.

**The validator cannot see bundle skills.** It reports 236 registry entries against 232
directories, but the six "missing" ones — differential-review, insecure-defaults,
modern-python, property-based-testing, static-analysis, terraform — are real plugin
bundles whose SKILL.md sits one level down, and each registry entry already carries a
resolving `entry` key. The inventory globs `*/SKILL.md` and misses them while
`validate_registry()` honors `entry`: two functions in one file disagreeing about what a
skill is. pptx_original and xlsx_original are genuinely unregistered and stay that way —
they are proprietary upstream originals with no LICENSE.txt present.

**The runtime looked duplicated and is not.** `~/.cli-jaw/skills` shows 64 entries, but
30 are **symlinks** (`dev -> jaw-dev`, `search -> jaw-search`, ...) created deliberately by
`cli-jaw/lib/mcp/skills-migration.ts` as the compat layer for the jaw-* rename. That module
states the link does not create a duplicate skill: every enumerator filters on
`Dirent.isDirectory()`, false for a symlink, so loadActiveSkills, the CLI listing, doctor,
soft reset and the Electron bootstrap all skip them. `resolveSkillId` maps legacy ids in
code as well. The one true duplicate is apple-calendar-reminders, a real directory whose
content differs from jaw-calendar-reminders by a single frontmatter line.

## The opencodex model for tests

`../opencodex` splits `tests/` by domain — `adapters/`, `cli/`, `config/`, `providers/`,
`routing/`, `server/`, `storage/`, `e2e-style/`, `helpers/`, `fixtures/` — behind a single
runner (`bun scripts/test.ts`, wired as `npm test`), with shared helpers building isolated
environments rather than each test improvising. CI invokes the runner, not a file list.

The Python analogue for this repo: `tests/` split by concern, a root `conftest.py`
providing the skill inventory once, markers that make binary-dependent suites skip, and
one CI step that runs the suite rather than naming a file.

## Work-phase map

| wp | Delivers | Verifiable close |
|---|---|---|
| wp1 | this roadmap + 10/20/30/40/50 diff-level docs | independent audit PASS |
| wp2 | validator rewritten around invariants; counts generated | validator exits 0, no literal count left |
| wp3 | `tests/` split by concern + conftest + CI entry point | full suite green from one command |
| wp4 | one skill-discovery function honoring `entry`; bundles stop looking orphaned | enforcing test passes |
| wp5 | runtime inventory verified; the one real duplicate resolved | re-read: 34 dirs, 30 links intact |
| wp6 | PR, CI, merge, deployment confirmed | merged with CI green |

Detail: [10_validator.md](10_validator.md), [20_tests.md](20_tests.md),
[30_registry.md](30_registry.md), [40_runtime.md](40_runtime.md),
[50_delivery.md](50_delivery.md).

