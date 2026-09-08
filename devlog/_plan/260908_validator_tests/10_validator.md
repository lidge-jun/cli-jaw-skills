# wp2 — Validator rewrite (diff-level)

Verifier: `python3 scripts/validate_public_surface.py` exits 0 on the current tree and
prints no count assertion; `rg -n 'EXPECTED_|== *[0-9]{2,}|"2[0-9]{2}"' scripts/` returns
nothing; deliberately breaking one invariant (a temp skill with no frontmatter) makes it
exit 1 with a named reason.

## REWRITE scripts/validate_public_surface.py

Delete every count assertion: `EXPECTED_SKILLS`, the README needle loop
(`"230"`, `"28 skills"`, `"2 skills"`), the docs needle `"230"`, and the
reference-folder comparison added last cycle. What replaces them, each failing only when
something is genuinely broken:

1. **Frontmatter is parseable and complete.** Every `*/SKILL.md` starts with a `---`
   block that yields a mapping with non-empty `name` and `description`. Parse without a
   YAML dependency (the repo has none): read the block, accept `key: value` and quoted
   forms, and treat nested/complex metadata as opaque — only `name` and `description`
   are required at top level. Report the file and the reason.
2. **Name matches directory.** `name` in the frontmatter equals the directory name.
   This is the invariant that would have caught the `jaw-*` rename leaving stale names.
3. **No duplicate skill names** across directories.
   Measured today: 232/232 skills parse with a naive top-level parser, 0 name/dir
   mismatches, 0 missing descriptions, 0 duplicate names. These pass now — they guard
   against reintroducing the class of defect the jaw-* rename could have caused, so their
   negative demonstration needs a synthetic fixture (wp2 C).
4. **Registry correspondence** — via the single skill-discovery function described in
   [30_registry.md](30_registry.md), which honors the registry entry key so bundle skills
   (static-analysis/skills/codeql/SKILL.md) are found. The current detector globs
   */SKILL.md only, which is why six real skills looked orphaned.
5. **Referenced local paths exist — as a warning, not a gate.** The audit measured the
   naive version: of 375 backtick-quoted reference paths, **110 do not resolve across 18
   skills**, including glob forms (scripts/*.py in jaw-docx, jaw-hwp, jaw-pptx, jaw-xlsx)
   and prose mentions in imagegen, sora, jupyter-notebook, cloudflare-deploy. As a hard
   check it would fail CI on its first run. Ship it as a reported warning that skips any
   path containing a glob metacharacter, and leave promotion to a gate for a later
   cleanup pass. The count of unresolved paths is printed, not asserted.

6. **Docs assets exist** — `docs/assets/favicon.svg`, `docs/assets/social-preview.svg`
   (kept; a missing asset is a real breakage).
7. **Line cap as a readability rule.** Keep the 500-line limit, renamed from "drift" to a
   stated rule, with the exemption list carrying a one-line reason ("Office format skills
   document a large command surface"). Exemptions stay `docx`/`hwp`/`pptx`/`xlsx` under
   their `jaw-` names as present on disk.

sync_public_surface.py necessarily contains the badge and table format strings it
writes; "no literal count" means no count is *asserted* as a pass condition, not that no
digit appears in the repo.

Counts become **output, not assertions**: the script ends by printing the measured
inventory (skills, reference folders, script folders, template folders) so a human or a
generator can use it. Add `--json` for machine use by the docs generator below.

## NEW scripts/sync_public_surface.py

Generates the published numbers instead of asserting them. Reads the measured inventory
and rewrites the four spots that currently carry hand-maintained figures: the README
badges (skills, reference assets), the README public-surface table rows, the
`docs/index.html` hero metrics, and the docs surface-table rows. Idempotent; prints a
diff summary. CI does not run it (it writes); it exists so the numbers are refreshed by a
command rather than by hand. If regenerating proves to reach too far into hand-written
prose, the fallback is to delete the specific counts from README/docs prose and keep only
the badge line, which the script then owns end to end — decided at B after reading both
files.

## MODIFY .github/workflows/ci.yml

Drop the four inline `grep` steps for docs markers (`canonical`, `og:image`,
`twitter:card`, and the `[0-9]+ inspectable skills` regex) — the first three become
invariant checks inside the validator, and the fourth is a count check that goes away.
Keep `git diff --check`.

## Acceptance

- No literal count assertion remains in `scripts/`.
- Validator exits 0 on the current tree and prints the measured inventory.
- A synthetic breakage (missing `description`, name/dir mismatch, dangling
  `references/` path) each produce a named non-zero failure — demonstrated at C.

