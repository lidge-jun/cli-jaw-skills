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


## Round 2 — fold verification (independent audit, 2026-09-08)

Re-read 00/10/20/30/40/50 at plan commit b1c0ceb. All six Round 1 blockers are folded
correctly and the corrected claims were re-verified against the tree and against
cli-jaw source. Three new defects surfaced, all in the *new* text.

### Fold 1 — registry detector (30_registry.md): CORRECT, INCOMPLETE
Verified: all six bundle entries resolve; a discovery function honoring `entry`
yields 238 discovered vs 236 registry, unresolved-registry = 0, unregistered =
exactly {pptx_original, xlsx_original}. The VENDORED_UNREGISTERED list is then
consistent with 30_registry.md:53-54.
NEW DEFECT: 30_registry.md:35-36 routes the name-match check at 10_validator.md:20
onto the resolved bundle SKILL.md, whose frontmatter `name` is the *inner* skill:
static-analysis -> "codeql", terraform -> "azure-verified-modules". 2 of 6 bundles
fail name==dirkey on the current tree. 30_registry.md:52 ("entry keys match their
directory name") is true of the key, but the frontmatter name check is not.

### Fold 2 — runtime (40_runtime.md): CORRECT
skills-migration.ts:19-20 states verbatim that the link does not create a duplicate
skill because enumerators filter on Dirent.isDirectory(); confirmed at
skills-migration.ts:171,276, skills-reset.ts:202, skills-distribution.ts:60, and
skills-utils.ts:71-72. resolveSkillId callers confirmed in src/prompt/builder.ts:49,
src/routes/skills.ts:28,50,66, src/cli/commands.ts:359. Backup convention confirmed:
skills-migration.ts:11 names `<home>/backups/skills-conflicts/<stamp>/` via
createBackupContext/movePathToBackup (skills-symlinks.ts), and the module never
recursive-deletes (skills-migration.ts:144). The plan's path matches, minus the
per-run `<stamp>` segment.
scripts/ uniqueness resolved: `diff -r` of the two directories reports ONLY
SKILL.md line 2 (the name). All 14 scripts and references/applescript-patterns.md are
byte-identical. Nothing unique is lost.
NOTE: ~/.cli-jaw/backups/ does not exist yet; the backup step creates it.

### Fold 3 — referenced-path warning (10_validator.md:31-37): UNDERSTATED
Skipping glob metacharacters removes only 6 of 110. **104 unresolved paths across 15
skills still print every run**, dominated by cloudflare-deploy (61 — it has no
references/ directory at all), speech (11), sora (9), imagegen (6). 10_validator.md:33
implies globs are the main contributor; they are 5%. As a warning this is not a CI
failure, but it is 104 lines of noise on every validator run.

### Fold 4 — tests (20_tests.md): ACHIEVABLE
testpaths=["tests"] correct (docx/xlsx/pptx tests confirmed absent). repo_root fixture
and importlib loading both correct. The run_officecli fallback at 20_tests.md:43-45 is
the honest resolution.

### New defect — frontmatter parser vs YAML block scalars
12 SKILL.md files write `description: >-` with the text on following indented lines
(jaw-pdf-vision, prompt-engineering, 10 supply-chain skills, plus the differential-review
and codeql bundle entries). The naive parser at 10_validator.md:15-19 reads the value as
the literal ">-", which is non-empty, so the check passes for the wrong reason: a truly
empty block scalar would also pass. Round 1's "232/232 parse, 0 missing descriptions" is
reproduced but is partly an artifact of this. Handle block scalars or state the limit.

### Unverifiable / stale claims remaining
- 00_plan.md:22-24 "main carried 47 reference folders while the tree held 52": no README
  commit touching "47 skills" exists (`git log -S` returns only unrelated commits).
  Cannot confirm; it is narrative, not a work item.
- 00_plan.md:8 "the 24 pre-existing dirty files in the main checkout": the sibling
  checkout is clean for the paths sampled. Non-goal, so harmless.
- 50_delivery.md:20 still lists registry.json as committable; after the fold no registry
  edit is planned. Harmless but now inaccurate.

VERDICT: NEAR-PASS — one real blocker (bundle name-match), two accuracy defects.


## Round 3 — fold verification (independent audit, 2026-09-08)

Re-read 00_plan.md, 10_validator.md, 30_registry.md, 50_delivery.md. All three Round-2
blockers are folded and each fold was re-measured against the tree.

### Fold 1 — name-match split by skill kind (10_validator.md:24-30): CORRECT & SUFFICIENT
Re-measured all six bundles. Entry KEY equals the directory for 6/6. Inner frontmatter
name is non-empty for 6/6, and is the inner skill for exactly the two named:
static-analysis -> "codeql", terraform -> "azure-verified-modules"; the other four
happen to match their key (differential-review, insecure-defaults, modern-python,
property-based-testing). The rule as written passes 6/6 today, and the two divergent
bundles are correctly the stated reason for the split rather than an exception list.
Checked the adjacent risk: no bundle inner name collides with any top-level skill
directory, and duplicate-name detection over the full discovered set (232 top-level +
6 bundles) returns zero collisions, so item 3 remains satisfiable once bundles enter
the inventory.

### Fold 2 — referenced-path warning restated (10_validator.md:40-46): CORRECT
Numbers match my measurement exactly: 375 total, 110 unresolved across 18 skills,
glob-skip removes 6, leaving 104 across 15 skills, with cloudflare-deploy 61 (no
references/ directory at all), speech 11, sora 9, imagegen 6. The per-skill summary
count is the right output shape for a 15-line worklist, and "never a gate" removes the
CI-failure risk entirely.

### Fold 3 — block scalars (10_validator.md:15-22): CORRECT
Census confirmed at 12 files: 10 top-level (jaw-pdf-vision, prompt-engineering, and the
eight-plus supply-chain skills — carrier-relationship-management,
customs-trade-compliance, energy-procurement, inventory-demand-planning,
logistics-exception-management, production-scheduling, quality-nonconformance,
returns-reverse-logistics) plus 2 bundle entry files (differential-review, codeql). The
document's parenthetical says "ten supply-chain skills" where the ten top-level files
include jaw-pdf-vision and prompt-engineering, so the supply-chain subset is eight; the
total of twelve and the mechanism are right. Cosmetic only.
The escape hatch at line 22 ("or state the limitation in the output") leaves an
implementer free to keep the naive parse if it documents itself. Acceptable — the
artifact is disclosed either way — but consuming the folded value is the better branch.

### Nits
- 50_delivery.md:19-23 corrected: registry.json removed from the committable list with
  the reason stated. Verified no other doc still plans a registry edit.
- 00_plan.md:22-24 STILL CARRIES the unverifiable 47-vs-52 anecdote, which the round-3
  brief said was removed. `git log -S'47 skills' -- README.md` still returns no such
  commit. Narrative only; no work item depends on it, and the mechanism argument at
  lines 17-21 stands without it. Not a blocker; delete the sentence when convenient.

### Residual observations (non-blocking)
- 10_validator.md:32-35 still reports "232/232 skills" for items 1-3; after the
  discovery fold the inventory is 238 (232 + 6 bundles). The stale figure is in the
  measurement note, not in a check.
- 30_registry.md:52 ("entry keys match their directory name") is now the authority for
  bundle naming and is consistent with 10_validator.md:29.
- 00_plan.md:70 keeps "no literal count left" as wp2's close, disambiguated at
  10_validator.md:55-57.

No blocker remains. The plan's checks all pass on the current tree as specified, the
destructive steps of the original draft are gone, and every acceptance criterion is
observable. Build phase may start.

VERDICT: PASS

