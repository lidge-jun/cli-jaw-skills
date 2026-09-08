# Claim-to-source ledger — WP3 forward

Tier 1 = `web_search` discovery (snippets, never sufficient on their own).
Tier "fetch" = a body actually retrieved via `curl` and read.
Status vocabulary is `search`'s: `sufficient` / `partial` / `browse-needed` / `insufficient`.

| # | Claim | Source (publisher, date) | URL | Tier | Status | Contradictions |
|---|-------|--------------------------|-----|------|--------|----------------|
| L1 | `anthropics/skills` exists, described "Public repository for Agent Skills", `license` field null, 175,075 stars, pushed 2026-09-03 | GitHub REST, fetched 2026-09-08 | api.github.com/repos/anthropics/skills | fetch | sufficient | none |
| L2 | `anthropics/skills` has no `.github/workflows` on the default branch | GitHub REST returned `{"message":"Not Found"}`, 2026-09-08 | api.github.com/repos/anthropics/skills/contents/.github/workflows | fetch | sufficient | none; absence proven by a 404 on the exact path, which does not exclude checks living elsewhere |
| L3 | `anthropics/skills` exposes no repo-level validator script; the `.py`/`.sh` matches are per-skill tooling (`skills/docx/scripts/…`) and OOXML `.xsd` schemas | git tree, recursive, 2026-09-08 | api.github.com/repos/anthropics/skills/git/trees/main?recursive=1 | fetch | partial | my filter regex was truncated at 60 rows; a validator under an unmatched name could exist |
| L4 | `agent-ecosystem/skill-validator` is MIT, 237 stars, created 2026-02-13, pushed 2026-08-24, and self-describes as validating "Skill content against Agent Skill specification, with additional content density and quality checks" | GitHub REST, 2026-09-08 | api.github.com/repos/agent-ecosystem/skill-validator | fetch | sufficient | none |
| L5 | It ships `cmd/validate.go`, `cmd/check.go`, `cmd/validate_links.go`, `cmd/validate_structure.go`, `links/check.go`, `content/content.go`, `contamination/`, `judge/`, and a copyable `examples/ci/` | git tree, 2026-09-08 | api.github.com/repos/agent-ecosystem/skill-validator/git/trees/main?recursive=1 | fetch | sufficient | none |
| L6 | Its example CI script validates only skill dirs changed vs `origin/<base>`, falls back to all skills when the diff is unavailable, runs `skill-validator check --strict --emit-annotations -o markdown` per skill, and exits 1 on any failure | file body, 2026-09-08 | raw.githubusercontent.com/agent-ecosystem/skill-validator/main/examples/ci/.github/scripts/validate-skills.sh | fetch | sufficient | none |
| L7 | Its example workflow triggers on `pull_request` limited to `skills/**`, checks out with `fetch-depth: 0`, and installs the validator with `go install …@latest` | file body, 2026-09-08 | raw.githubusercontent.com/agent-ecosystem/skill-validator/main/examples/ci/.github/workflows/validate-skills.yml | fetch | sufficient | `@latest` means the enforced rule set can change without a commit in the consuming repo |
| L8 | `cockroachlabs/cockroachdb-skills` is Apache-2.0, 21 stars, created 2026-02-19, pushed 2026-07-22 | GitHub REST, 2026-09-08 | api.github.com/repos/cockroachlabs/cockroachdb-skills | fetch | sufficient | none |
| L9 | It runs `python scripts/validate-spec.py skills/ --github` on PRs and pushes to main, filtered to `skills/**`, `scripts/**`, and the workflow file | file body, 2026-09-08 | raw.githubusercontent.com/cockroachlabs/cockroachdb-skills/main/.github/workflows/validate-skills.yml | fetch | sufficient | the trailing `if [ $? -eq 0 ]` summary step inspects the exit code of `echo`, so that step is decorative; the real gate is the preceding step |
| L10 | Its caps are `MAX_NAME_LENGTH = 64`, `MAX_DESCRIPTION_LENGTH = 1024`, `MAX_SKILL_LINES = 500` | file body (grepped), 2026-09-08 | raw.githubusercontent.com/cockroachlabs/cockroachdb-skills/main/scripts/validate-spec.py | fetch | sufficient | none |
| L11 | The 500-line cap is a **warning**, not a failure: the constant is commented `# Warning threshold` and line 263-264 calls `self.warning(...)` | same file, lines 48-50 and 262-264 | (as L10) | fetch | sufficient | none |
| L12 | `elastic/elastic-docs-skills` is Apache-2.0, 71 stars, created 2025-08-20, pushed 2026-09-07 | GitHub REST, 2026-09-08 | api.github.com/repos/elastic/elastic-docs-skills | fetch | sufficient | none |
| L13 | Its workflow enforces required frontmatter (`name`, `description`, `version`), kebab-case names, a mandatory `docs-` name prefix, SemVer versions, and **duplicate skill-name detection** across `skills/*/*/SKILL.md` | file body, 2026-09-08 | raw.githubusercontent.com/elastic/elastic-docs-skills/main/.github/workflows/validate-skills.yml | fetch | sufficient | none |
| L14 | It additionally validates `evals.json` (JSON syntax, an `evals` array, per-eval `id`/`prompt`/`expectations`, non-empty expectations) and, on PRs only, fails when `skills` changed without a strictly greater `.claude-plugin/plugin.json` version | same file | (as L13) | fetch | sufficient | none |
| L15 | No repo among those opened validates a README skill-**count** claim or README/skill **drift** | absence across O4-O14 | (all above) | fetch | partial | absence over 5 repos is suggestive, not exhaustive; the search lane was capped |
| L16 | `Winbda/claude-skills-collection` (MIT, 3 stars, created 2026-04-05) has no reachable `main` tree and no enforcement surface | GitHub REST + git tree, 2026-09-08 | api.github.com/repos/Winbda/claude-skills-collection | fetch | partial | the tree call returned null; the repo may be empty or use another default branch, which I did not spend an open to distinguish |

## Tier-1-only claims (open questions, never promoted)

- Whether any *large* community skill collection (the "N skills" awesome-list class)
  enforces its own count. Discovery for this family was cut short when `web_search`
  returned its usage limit after one call; no such repo was opened, so nothing is claimed.

