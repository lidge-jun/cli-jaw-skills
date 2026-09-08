# Two extractions clear the 500-line cap; one stale "47" count still contradicts them

**Reader contract:** a maintainer who was not in the session, deciding whether to approve the reader-documents PR; already knows the cli-jaw skills repo layout and that each `SKILL.md` is size-capped, but has no session context. Document type: report.

The skills repo enforces a 500-line cap per `SKILL.md` through `scripts/validate_public_surface.py`, and `dev/SKILL.md` currently sits at 504, so the validator exits 1 on main (A1, A3). The same cap also blocks the other half of the work: the deep-research protocol cannot be inlined into `search/SKILL.md`, which is already at 472 lines (A4). Both problems are resolved by moving content into `references/` folders — `dev` §7.2's mapping table to `dev/references/static-analysis.md` for a net −11 lines to 496 (A13), and the deep-research protocol into `search/references/` (A14). Before approving, check one thing: creating `search/references/` raises the reference-folder count to 48 while the README badge, README prose, and the docs site all still say 47 (A6, A7, A15).

## Contents

- dev/SKILL.md breaches the cap on main, and the §7.2 extraction lands it at 496
- The deep-research protocol belongs under search/references/, not inside search/SKILL.md
- The new reference folder makes three published "47" counts wrong
- Green CI on main does not cover the validator failure
- What this does not cover
- Next steps
- Appendix: evidence

## dev/SKILL.md breaches the cap on main, and the §7.2 extraction lands it at 496

The validator fails on main today, naming `dev/SKILL.md:504` (A1). That is a real breach, not a threshold artifact: the script hard-codes a 500-line cap, an `EXPECTED_SKILLS` count of 226, and four Office exemptions (A3), and the repo does contain 226 skill folders (A2), so the only failing condition is the line count.

The fix moves the §7.2 static-analysis mapping table out to `dev/references/static-analysis.md`, a net −11 lines that brings the file to 496 (A13). That leaves four lines of headroom under the cap — thin enough that a reviewer should expect the next `dev/SKILL.md` addition to force another extraction. This structure has precedent in the repo: `dev-architecture/references/` already holds exactly this kind of split-out material (A11).

## The deep-research protocol belongs under search/references/, not inside search/SKILL.md

Inlining was arithmetically impossible. `search/SKILL.md` is 472 lines and the protocol is about 140, so the combined file would breach the same 500-line cap (A4, A14).

Ownership rules point the same direction. `dev/SKILL.md`'s Skill Ownership Map states that skills MUST NOT duplicate canonical content (A8), and `search/SKILL.md` already declares itself the standalone owner of tier policy (A9). Placing the protocol in `search/references/` keeps it under the owning skill without inflating the routing surface a sub-agent has to read.

## The new reference folder makes three published "47" counts wrong

This is the one contradiction the PR introduces rather than inherits. Three published surfaces state 47: the README badge `reference_assets-47` at line 10, README prose at line 30 ("47 skills include reference/"), and `docs/index.html` line 137 ("Reference folders | 47 skills") (A6, A7). Creating `search/references/` makes the true count 48 (A15).

*Assumption (not in the notes):* it is unclear whether the PR already updates these three locations, or whether the count is validated automatically. A reviewer should confirm both by inspection.

## Green CI on main does not cover the validator failure

The last CI run on main, `25e30780` (2026-09-05), succeeded (A5) even though the validator fails on main today (A1). Local test coverage is also narrower than it looks: `pytest tests/` requires the `officecli` binary, and CI only runs `test_dev_frontend_refresh.py` (A16).

*Assumption (not in the notes):* the most likely explanation for green CI alongside a failing validator is that `validate_public_surface.py` is not wired into the CI workflow, or that the 504-line state postdates that run. The notes do not say which, so treat the surface check as effectively unverified in automation until confirmed.

## What this does not cover

- **Registry drift.** `registry.json` has 230 entries against 226 skill folders (A12). The notes mark this pre-existing, so it is not caused by this PR and is not fixed by it.
- **Vendored deep-research provenance.** `deep-research/SKILL.md` is vendored Apache-2.0 material (author sanjay3290) wrapping a Gemini agent (A10). The notes record no license, attribution, or extraction-permission review.
- **Whether the decisions are implemented.** The notes record both extractions as decisions taken (A13, A14); they do not record the resulting file states or a re-run of the validator.

## Next steps

1. **PR author** — re-run `python3 scripts/validate_public_surface.py` on the PR head and attach the exit-0 result; the 496 figure (A13) is currently a projection, not a measurement.
2. **PR author** — update the three "47" references (A6, A7) to 48, or state why they remain correct.
3. **Reviewer** — confirm whether `validate_public_surface.py` runs in CI; if it does not, the cap is enforced only by hand (A5, A16).
4. **Reviewer** — decide separately whether the vendored deep-research attribution (A10) and the registry drift (A12) need their own issues.

## Appendix: evidence

All items below are from the WP2 session notes; no source has a URL or an independent date beyond those stated.

| Anchor | Kind | Record |
|--------|------|--------|
| A1 | command | `python3 scripts/validate_public_surface.py` on main → exit 1, `dev/SKILL.md:504` |
| A2 | command | `ls */SKILL.md \| wc -l` → 226 |
| A3 | file read | `scripts/validate_public_surface.py`: `EXPECTED_SKILLS=226`, 500-line cap, 4 Office exemptions |
| A4 | command | `wc -l search/SKILL.md` → 472 |
| A5 | command | `gh run list` → last CI on main `25e30780` success (2026-09-05) |
| A6 | grep | `README.md` line 10 badge `reference_assets-47`; line 30 "47 skills include reference/" |
| A7 | grep | `docs/index.html` line 137 "Reference folders \| 47 skills" |
| A8 | file read | `dev/SKILL.md` Skill Ownership Map: "MUST NOT duplicate canonical content" |
| A9 | file read | `search/SKILL.md` declares itself standalone owner of tier policy |
| A10 | file read | `deep-research/SKILL.md` is vendored Apache-2.0 (author sanjay3290), Gemini agent wrapper |
| A11 | probe | `dev-architecture/references/` holds `barrel-discipline.md`, `circular-dependencies.md`, `coupling-taxonomy.md` only |
| A12 | probe | `registry.json` has 230 entries vs 226 skill folders (pre-existing drift) |
| A13 | decision | Extract `dev` §7.2 mapping table to `dev/references/static-analysis.md`; net −11 lines → 496 |
| A14 | decision | Put the deep-research protocol under `search/references/`, not in `SKILL.md` (472+140 would breach 500) |
| A15 | risk | Creating `search/references/` makes the reference-folder count 48; README and docs say 47 |
| A16 | risk | `pytest tests/` needs the `officecli` binary; CI only runs `test_dev_frontend_refresh.py` |

