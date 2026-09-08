# wp1 plan audit (independent, Opus-5)

VERDICT: NEAR-PASS

All seven MODIFY targets exist and every quoted anchor resolves. Constraints confirmed by
running the repo's own checks: the validator exits 1 today with `dev/SKILL.md:504`,
EXPECTED_SKILLS is 226, the 500-line cap is real, `ls */SKILL.md` counts 226, and
`search/SKILL.md` is 472 lines. The search-vs-deep-research ownership boundary is
defensible: the vendored skill already says "NOT for quick factual lookups (use `search`
skill instead)".

## Blockers, all folded

1. **The line-reclaim arithmetic was wrong.** The section-8 Redis example is lines
   498-500 — three lines, not the six-plus needed (504 + 2 = 506). Folded: the plan now
   moves the section 7.2 rule-to-prose mapping table (460-472) into
   `dev/references/static-analysis.md` for a net -11, landing at 495.
2. **The named fallback does not exist.** `dev-architecture/references/` holds only
   barrel, circular and coupling docs. Folded: fallback withdrawn.
3. **Creating `search/references/` moves a published count.** 47 skills have reference
   folders today; adding one makes 48 and falsifies README.md (badge line 10, table line
   30) and docs/index.html (line 137). The validator only greps the literal "47 skills",
   so CI would stay green while the public surface doc went false. Folded: the count
   updates are now part of wp3's change map.
4. **`pytest tests/` is not the CI gate.** `test_cjk_regression.py` needs the
   `officecli` binary; CI runs only `test_dev_frontend_refresh.py`. Folded: verifier
   narrowed everywhere it appeared.

## Nits

1-6 folded: the unit moved to `devlog/_plan/260908_reader_documents/` with the repo's
two-digit prefixes (a `000_index.md` satisfies the FSM gate and explains why),
the ownership cell uses the `dev refs/` format, cross-references use skill names,
the vendored deep-research edit is marked a local addition, the trial and worktree
criteria are now observable, and 10_ states Stage 3 remains canonical for co-authored
documents. Nit 7 (registry.json holds 230 entries against 226 skills) is pre-existing
drift, uncaught by CI, and stays out of scope.

