# wp1 plan audit (independent, Opus-5)

VERDICT: FAIL — three of five action phases rested on wrong facts. Two would have
destroyed working assets. The corrections are folded into the plan; this is the record.

## Blocker 1 — the six "orphaned" registry entries are real skills

`differential-review`, `insecure-defaults`, `modern-python`, `property-based-testing`,
`static-analysis`, `terraform` are multi-skill plugin bundles whose `SKILL.md` sits at a
nested path. Every entry already carries a resolving `entry` key
(`static-analysis/skills/codeql/SKILL.md` and so on, all `exists=True`), git tracks them,
and commit `78cb936` added them. My claim that no deletion commit existed was wrong.
Deleting the entries would have de-registered six working skills.

The real defect: `validate_public_surface.py:66` globs `*/SKILL.md` while
`validate_registry()` at line 39 honors `entry` — two functions in one file disagreeing
about what a skill is. **Fold: fix the detector, delete nothing.** (30_registry.md rewritten.)

## Blocker 2 — the referenced-path check would fail CI immediately

Of 375 backtick-quoted reference paths, 110 do not resolve across 18 skills, including
glob forms (`scripts/*.py` in the Office skills) and prose mentions. **Fold: ship it as a
printed warning that skips globs, not a gate.**

## Blocker 3 — the runtime has no duplicates

All 30 "legacy copies" are symlinks (`find -maxdepth 1 -type l` = 30, real dirs 34),
created deliberately by `cli-jaw/lib/mcp/skills-migration.ts` as the `jaw-*` compat
layer. That module states the links do not create duplicate skills because every
enumerator filters on `Dirent.isDirectory()`, and `resolveSkillId` maps legacy ids in
code. Removing them would break literal-path references and be undone by the next
`ensureCompatSymlinks` pass. **Fold: verify and leave them; wp5 becomes an inventory
plus the one real duplicate.**

## Blocker 4 — the one true duplicate is the inverse of the framing

`apple-calendar-reminders` is a real directory differing from `jaw-calendar-reminders`
by exactly one line (the frontmatter `name`). Folded into wp5 as the actual work.

## Blocker 5 — the test config already points at nothing

`pyproject.toml` lists `docx/tests`, `xlsx/tests`, `pptx/tests`; none exist.
`test_cjk_regression.py:9` imports `run_officecli` from a `conftest.py` that does not
exist anywhere, so it cannot run today. **Fold: `testpaths = ["tests"]`, and the new
conftest must supply `run_officecli` or that suite is skipped with the reason recorded.**

## Blocker 6 — moving tests breaks their root computation

Both surviving tests compute `parents[1]`; imports of `scripts/` need
`importlib.util.spec_from_file_location` since there is no package. **Fold: `repo_root`
comes from the conftest fixture.**

## Nits folded

Items 1-3 of the validator already pass on the current tree (232/232 parse, 0 mismatches,
0 duplicates), so their negative demonstration needs a synthetic fixture — recorded.
Dropping the docs greps is safe; no workflow outside `ci.yml` reads them.
`pptx_original`/`xlsx_original` stay unregistered, named in a `VENDORED_UNREGISTERED`
list with the proprietary-license reason, because their `LICENSE.txt` is missing.
"no literal count" means none is asserted as a pass condition. Local `pytest` is absent
from Python 3.14 here; CI is authoritative.

