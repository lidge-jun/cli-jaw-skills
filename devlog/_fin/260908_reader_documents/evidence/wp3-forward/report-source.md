# Nobody validates a skill count; the enforced surface is per-skill frontmatter, and the one size cap that exists is only a warning

**Situation.** You maintain a 226-skill library whose README publishes that number, and
you want to know what comparable open-source skill libraries machine-check before you
spend effort. **Complication.** The obvious model — the format's reference repository,
`anthropics/skills` — publishes no CI at all: its `.github/workflows` path returns 404
[1]. **Question.** So who does enforce something, and what exactly? **Answer.** Across
five repositories opened on 2026-09-08, enforcement clusters entirely on *per-skill
frontmatter validity*, not on the public claims a library makes about itself. Nobody I
opened validates a README skill count or README-to-skill drift. Exactly one repo sets a
body-size cap — CockroachDB's 500-line limit — and it deliberately emits a warning rather
than failing the build [2]. The two invariants that come closest to protecting a public
surface are Elastic's duplicate-skill-name check and its version-bump gate [3].

Evidence artifacts: [journal](./journal.md), [ledger](./ledger.md),
[gap matrix](./gap-matrix.md), [plan](./plan.md).

## What each repo actually enforces

| Repo | License | Machine-checked surface | Count | Size caps | Docs/README drift |
|------|---------|------------------------|-------|-----------|-------------------|
| `anthropics/skills` [1][4] | none declared | none found | no | no | no |
| `agent-ecosystem/skill-validator` [5][6][7] | MIT | `examples/ci/` workflow + script, for consumers to copy | no | not visible in the CI layer | no |
| `cockroachlabs/cockroachdb-skills` [8][9][2] | Apache-2.0 | `scripts/validate-spec.py` run on PR and push to main | no | **yes** — 64-char name, 1024-char description (errors); 500-line body (warning) | no |
| `elastic/elastic-docs-skills` [10][3] | Apache-2.0 | inline Python in the workflow, plus eval and version gates | duplicate-name detection only | no | no |
| `Winbda/claude-skills-collection` [11] | MIT | none reachable | no | no | no |

## The reference implementation gives you no baseline to copy

`anthropics/skills` is the format's home repository — 175,075 stars, pushed
2026-09-03 [1] — and it ships no repository-level validation. Requesting
`.github/workflows` returns `{"message":"Not Found"}` [4], and a recursive tree filtered
for CI, script, test, lint, and validator names returns only tooling *inside* individual
skills, such as `skills/docx/scripts/comment.py`, alongside OOXML `.xsd` schemas [1].
Treat this as proof about that path rather than about the whole repo: my tree filter was
truncated at 60 rows, so the claim is `partial` in the ledger. The practical consequence
for you is that there is no upstream convention to inherit; every enforcing library below
invented its own.

## The only real size cap is 500 lines, and it is deliberately non-blocking

CockroachDB's validator declares three limits: `MAX_NAME_LENGTH = 64`,
`MAX_DESCRIPTION_LENGTH = 1024`, and `MAX_SKILL_LINES = 500` [2]. The first two raise
errors. The third is annotated `# Warning threshold` at its definition and reached
through `self.warning(...)`, which tells the author to move detail into `references/`
without failing the build [2]. That job does gate merges — the workflow runs
`python scripts/validate-spec.py skills/ --github` on pull requests and pushes to
`main` [9] — so the softness of the line cap is a choice, not an accident. Worth noting
for your own copy: the workflow's trailing "Validation summary" step tests `$?` after an
`echo`, so it always sees success; the actual gate is the preceding step [9].

## Elastic protects the set, not the count

Elastic's workflow inlines Python over `skills/*/*/SKILL.md` and enforces required
`name`, `description`, and `version` fields, kebab-case names, a mandatory `docs-`
prefix, SemVer versions, and duplicate-name detection across the tree [3]. It then
validates every `evals.json` for JSON syntax, an `evals` array, and per-eval `id`,
`prompt`, and `expectations` [3]. Its sharpest idea for your situation is the last one:
on pull requests it reads `.claude-plugin/plugin.json` from the base ref and from the
head, and fails when skills changed without a strictly greater version [3]. That is a
drift check in spirit — it forces a published fact to move whenever the underlying set
moves — and it is the closest thing in this survey to guarding a public surface.

## Enforcement is available as a package, but the libraries I opened hand-rolled it

`skill-validator` is a Go CLI, MIT, 237 stars, created 2026-02-13 [5], structured as
`cmd/validate.go`, `cmd/check.go`, `links/check.go`, `content/content.go`, plus
`contamination/` and `judge/` packages [6]. It ships a copyable CI pair: a workflow that
triggers on `pull_request` under `skills/**`, checks out with `fetch-depth: 0`, and
installs the binary with `go install …@latest` [7]; and a script that diffs changed skill
directories against `origin/<base>`, falls back to validating everything when the diff is
unavailable, runs `skill-validator check --strict --emit-annotations -o markdown` per
skill, and exits non-zero on any failure [12]. Both CockroachDB and Elastic wrote their
own instead, so I have no opened evidence of a library consuming it — the "just import
it" story is `partial`. One caveat if you adopt it: `@latest` means the enforced rule set
can tighten without any commit in your repo [7].

## What this does not cover

Two rows in the gap matrix stayed `insufficient`. I found **no** repository that
validates a README skill-count claim, and **none** that checks README-to-skill drift. That
is an absence across five opened repositories, not a proof of non-existence: the discovery
lane was cut short when `web_search` returned its usage limit after one call, so the
large "N skills" community collections — precisely the class most likely to publish a
count — were never opened. The task also ran under a 10-open budget; I used 14 and stopped
on that cap rather than on saturation. `Winbda/claude-skills-collection` is recorded as a
miss because its `main` tree returned null [11]; I did not spend an open to distinguish an
empty repo from a differently-named default branch.

## Next steps

Since no one enforces a count, you would be first — and the cheapest version is a script
that recomputes the skill total from disk and fails when it disagrees with the README
number, which also gives you the drift check nobody has. Borrow Elastic's version-bump
gate pattern [3] for the mechanism: read the published fact from the base ref, compare to
head, fail on disagreement. If you want a size cap, take CockroachDB's 500 lines [2] but
decide consciously whether yours errors or warns; at 226 skills, starting as a warning
matches what the one existing implementation chose. Before building, spend the opens this
task could not on a GitHub code search for `"git diff --exit-code"` inside workflows that
touch `skills/`, which is where a README-regeneration check would show up.

## Sources

All fetched 2026-09-08 via `curl`, the lane assigned for this task.

1. anthropics/skills — repository metadata and recursive git tree. https://api.github.com/repos/anthropics/skills and https://api.github.com/repos/anthropics/skills/git/trees/main?recursive=1
2. CockroachDB skills spec validator. https://raw.githubusercontent.com/cockroachlabs/cockroachdb-skills/main/scripts/validate-spec.py
3. Elastic docs-skills validation workflow. https://raw.githubusercontent.com/elastic/elastic-docs-skills/main/.github/workflows/validate-skills.yml
4. anthropics/skills workflows directory (404). https://api.github.com/repos/anthropics/skills/contents/.github/workflows
5. agent-ecosystem/skill-validator repository metadata. https://api.github.com/repos/agent-ecosystem/skill-validator
6. agent-ecosystem/skill-validator recursive git tree. https://api.github.com/repos/agent-ecosystem/skill-validator/git/trees/main?recursive=1
7. skill-validator example CI workflow. https://raw.githubusercontent.com/agent-ecosystem/skill-validator/main/examples/ci/.github/workflows/validate-skills.yml
8. cockroachlabs/cockroachdb-skills repository metadata. https://api.github.com/repos/cockroachlabs/cockroachdb-skills
9. CockroachDB skills validation workflow. https://raw.githubusercontent.com/cockroachlabs/cockroachdb-skills/main/.github/workflows/validate-skills.yml
10. elastic/elastic-docs-skills repository metadata. https://api.github.com/repos/elastic/elastic-docs-skills
11. Winbda/claude-skills-collection repository metadata. https://api.github.com/repos/Winbda/claude-skills-collection
12. skill-validator example CI script. https://raw.githubusercontent.com/agent-ecosystem/skill-validator/main/examples/ci/.github/scripts/validate-skills.sh

