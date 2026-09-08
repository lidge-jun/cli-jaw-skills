# Fresh reader response — wp2-forward status report

**1. Answer/state.** The 500-line `SKILL.md` cap is the binding constraint. `dev/SKILL.md` is 504 on main so the validator fails, and the deep-research protocol cannot fit inside `search/SKILL.md` (472 + ~140). Both are handled by moving content into `references/` folders. The decisions are made but not yet measured, and one published "47" reference-folder count becomes wrong.

**2. Why I believe it.** The arithmetic is checkable and the report shows its work: validator exit 1 naming `dev/SKILL.md:504` (A1), the hard-coded 500 cap (A3), `wc -l search/SKILL.md` → 472 (A4), and three exact "47" locations with line numbers (A6, A7). It also flags its own soft spots — 496 is labeled a projection, and the green-CI explanation is marked an assumption — which made the confident parts easier to trust.

**3. What to do next.** Re-run `validate_public_surface.py` on the PR head and attach exit 0; change the three "47" strings to 48; confirm whether the validator runs in CI at all; file registry drift (A12) and vendored deep-research attribution (A10) separately.

**4. Where I got lost.** The green-CI section. "The last CI run on main, `25e30780` (2026-09-05), succeeded (A5) even though the validator fails on main today (A1)." I re-read this twice because it reads as a contradiction before the assumption paragraph resolves it, and the resolution offers two incompatible explanations without choosing. The heading also says CI "does not cover" the failure, which asserts more than the evidence supports.
