# Gap matrix — WP3 forward

Rows are the three enforcement targets the reader is choosing between, plus the two
structural questions that decide whether to copy or build.

| claim | evidence (URL, date, tier) | status | contradiction | missing | next query |
|-------|---------------------------|--------|---------------|---------|------------|
| **Skill-count enforcement exists somewhere** | none found across 5 repos opened 2026-09-08 (fetch) | insufficient | — | any repo whose CI asserts "N skills" against a README number | `path:.github/workflows "skills" "count"` code search; or open a large collection's workflow directly |
| **Count-*adjacent* invariants exist** | elastic workflow: duplicate-name detection across `skills/*/*/SKILL.md`; PR-only `plugin.json` version-bump gate — raw.githubusercontent.com/elastic/elastic-docs-skills/main/.github/workflows/validate-skills.yml, 2026-09-08 (fetch) | sufficient | these constrain the *set*, not its published cardinality | — | — |
| **File-size caps exist** | cockroachdb `validate-spec.py`: `MAX_NAME_LENGTH=64`, `MAX_DESCRIPTION_LENGTH=1024`, `MAX_SKILL_LINES=500`, 2026-09-08 (fetch) | sufficient | — | a repo that makes a body-size cap a hard failure | grep another library's validator for `MAX_` constants |
| **Size caps are actually blocking** | same file: `# Warning threshold` at line 50, `self.warning(...)` at 263-264 (fetch) | sufficient | the name/description caps *are* errors; only the body-line cap is a warning | — | — |
| **Docs/README drift enforcement exists** | no matching artifact in any of the 5 repos opened (fetch) | insufficient | — | a script regenerating a README skill table and failing on `git diff --exit-code` | search `"git diff --exit-code" README skills` in workflows |
| **The reference implementation sets the bar** | `anthropics/skills` `.github/workflows` -> 404; tree shows no repo-level validator, 2026-09-08 (fetch) | partial | 404 proves the path, not the whole repo; my tree filter was truncated at 60 rows | an unfiltered tree listing of the repo root | list `/contents/` at the repo root |
| **Enforcement is imported rather than written** | skill-validator ships `examples/ci/` workflow+script for copying; cockroachdb and elastic both hand-rolled instead, 2026-09-08 (fetch) | partial | the two adopters I opened did *not* use the shared validator, weakening "imported" | evidence of a repo actually consuming `skill-validator` in CI | GitHub code search for `go install github.com/agent-ecosystem/skill-validator` |
| **Changed-only vs whole-tree validation** | skill-validator script diffs vs `origin/<base>` with an all-skills fallback; cockroachdb and elastic validate the whole `skills/` tree, 2026-09-08 (fetch) | sufficient | — | — | — |

Stop rule S2 (open cap, 14 used against a budget of 10) ended the task with the two
`insufficient` rows unresolved. They are reported as gaps, not as negative findings.

