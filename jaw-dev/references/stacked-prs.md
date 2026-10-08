# Stacked Pull Requests (canonical — `DEV-STACK-*`)

Canonical owner: `jaw-dev`. Other skills carry pointer stubs only. Rules here are
tool-agnostic: the portable model first, CLI recipes second.

## DEV-STACK-OPT-IN-01 — Native stacks are task-specific

Use ordinary PRs by default and a manual branch chain when dependencies justify
one. Native GitHub stacks require a clear, task-specific user selection. A generic
request to stack, split PRs, follow a phase map, merge, or improve CI does not
select native registration. A PR base, body map, or Can Stack banner does not
select it either. One unmistakable request naming the feature is sufficient;
retain that authorization within its scope and respect later changes.

Read-only membership inspection remains allowed for safety. It does not authorize
registering, converting, restacking, merging, or dissolving a native stack. If
membership blocks an ordinary authorized operation, explain the blocker and
continue independent work. An explicit request to leave a stack is a separate
scoped action.

## The model

A **stack** is an ordered chain of branches. The **bottom** branch is based on
trunk (usually `main`); every branch above is based on the branch below it. Each
branch gets its own PR whose base is the branch below, so each PR's diff shows
only that layer.

```
feature/ui        → PR #3 (base: feature/api)     ← top
feature/api       → PR #2 (base: feature/schema)
feature/schema    → PR #1 (base: main)            ← bottom
──────────────────  main (trunk)
```

Four invariants hold across every stacking tool (GitHub `gh stack`, Graphite, Git
Town, plain git). Learn these, not a vendor's flags:

1. **The base ref is the dependency edge.** It makes the chain reviewable.
2. **Editing a lower layer invalidates every layer above it** — always cascade.
3. **Merging is bottom-up.** Out-of-order merges are the pathological case.
4. **Every layer must stand alone for review**: own thesis, own build, own tests.

## DEV-STACK-06 — Determine membership before writes

During PR creation, review, restack or merge, inspect topology and native
membership read-only. Keep three states distinct:

| State | Evidence | Meaning |
|---|---|---|
| Manual chain | Same-repository child base names parent head; successful native lookup has no membership | Layered diffs without native guarantees |
| Registered native stack | API identifies ordered members and trunk | Native behavior may apply |
| Unknown | API denied, unavailable, or unsupported | Report uncertainty; do not infer absence |

For a GitHub repository, inspect the actual PR and repository:

```sh
gh pr view <number> -R <owner/repo> --json number,baseRefName,headRefName,headRefOid,isCrossRepository
gh api 'repos/<owner>/<repo>/pulls/<number>'
gh api 'repos/<owner>/<repo>/stacks?pull_request=<number>'
```

Compare repository identities as well as branch names. Record stack number,
trunk, and ordered members when membership is confirmed. A successful empty
response means absent; an unsuccessful request means unknown. Refresh before a
write because another actor may change membership. A body map, parent base,
label, or Can Stack banner is not registration. Native registration requires
DEV-STACK-OPT-IN-01 and authority for that write; re-read membership afterward.

## DEV-STACK-07 — Diagnose CI separately

Record topology, membership, every layer's head/check SHA, and workflow
event/ref/concurrency. Native membership does not deduplicate CI: applicable
workflows may run for each registered layer. Manual chains need their actual
branch rules and workflow filters inspected; trunk coverage is not inherited
by assumption.

For repeated or missing CI, inspect workflow triggers and guards with `gh pr
checks`, `gh run list`, and `gh run view`. Distinguish separate PRs, duplicate
events for one PR/head, rerun attempts, old heads, and cancelled runs. A
per-PR concurrency key does not cancel across the chain. Missing, skipped,
or cancelled tests are not passing tests. Apply DEV-CI-EVIDENCE-01 in
`hosted-ci-evidence.md` before claiming coverage or changing the workflow.
Cost optimization is a separate, authorized change that must preserve truthful
evidence for each mergeable layer and final integration.

## DEV-STACK-01 — When to stack (DEFAULT)

Stack when **all** of these hold:

- the work splits into 2+ parts with a real dependency order (later parts consume
  earlier parts' output), and
- shipping it as one PR would produce a diff too large to review in one sitting —
  by your repository's own review-size convention if it has one, otherwise
  reviewer judgment, and
- the lower parts are mergeable on their own — they do not need the upper parts to
  be correct or safe.

A `jaw-dev-pabcd` PHASE-SPLIT-01 map orders implementation dependencies. It
does not select a PR chain or native GitHub registration. Apply the criteria
above to decide whether a manual chain is useful; native use still requires
DEV-STACK-OPT-IN-01.

Do **not** stack when:

- the change is one cohesive thesis (splitting adds review and CI surface, buys
  nothing);
- the parts are independent — open parallel PRs off trunk instead, since a stack
  imposes a false merge order;
- the lower layer is speculative and likely to be rewritten (every rewrite
  re-cascades);
- you cannot name what each layer proves on its own (that is a slicing failure —
  fix the slice before opening anything).

**Depth (HEURISTIC — practitioner guidance, not a measured limit).** Aim for 2–4
layers and think hard at 5. Community practice guides suggest each layer be
reviewable in roughly 10–15 minutes and report stacks becoming unwieldy past about
4–5 layers; treat that as experience, not a rule. What is certain: every layer is
a separate fully gated PR with its own review and its own CI, and every layer
above an edit has to be re-stacked by hand or by tool. If the map is longer, ship
the bottom half, land it, then stack the rest.

**Slice by dependency, never by effort.** "Quick wins first" produces layers whose
dependency runs opposite to the merge order, so the stack cannot land bottom-up.
This is `jaw-dev-pabcd` PHASE-SPLIT-01 applied to branches.

## DEV-STACK-02 — Cascading edits (STRICT)

When a lower layer changes, check every layer above it against the new lower
tip. A rewrite can leave descendants on obsolete ancestry. Re-push the
cascade before asking for review:

- Plain git: `git rebase --update-refs` updates branches pointing inside the
  rebased range, except branches checked out in another worktree. Prefer this
  per-invocation flag; do not alter global Git configuration incidentally.
- In an explicitly selected native workflow, `gh stack rebase` fetches origin and cascades from trunk upward; if a layer's PR
  has already merged it switches to `--onto` mode automatically. Conflicts pause
  the run; resume with `--continue`, unwind everything with `--abort`. Scope with
  `--downstack` / `--upstack` / `--no-trunk`.
- Other tools (Graphite `gt restack` / `gt modify`, Git Town `git town sync`,
  `spr diff`) express the same cascade — read their own docs before using their
  flags.

After the cascade, publish with `git push --force-with-lease` (never bare
`--force`) and re-check each PR's base ref. A rebase rewrites the reviewed
commits, so depending on repository settings a force-push can invalidate existing
review state and leave inline comments attached to commits that no longer exist.
Assume review state is stale after a cascade: say what changed and re-request
review rather than expecting prior approvals to carry.

**Verification (STRICT):** a cascade is not done because the command exited 0.
Confirm each upper branch contains the new lower tip with
`git merge-base --is-ancestor <lower> <upper>`; inspect
`git log --oneline <lower>..<upper>` for only that layer's commits, and check that
each PR's base ref still names the branch below it.

## DEV-STACK-03 — Layer shape (DEFAULT)

Each layer:

- has one thesis, stated in its PR title;
- builds and passes its own tests at its own tip — do not defer a layer's tests
  upward;
- carries a stack map in its PR body so reviewers can navigate:

```markdown
**Stack** (merge bottom-up):
| # | PR | Layer | Review focus |
|---|----|-------|--------------|
| 3 | #103 | UI | integration only |
| 2 | #102 | API | endpoint behavior |
| 1 | #101 | schema ← you are here | migration + rollback |

Depends on #101. Review this PR's diff only.
```

Mid-stack layers are **not** lightly gated. In a registered GitHub stack,
branch protection and applicable CI cover every member. For manual chains,
inspect actual branch rules and workflow coverage (DEV-STACK-07).

## DEV-STACK-05 — Reviewing a layer (DEFAULT)

When you are reviewing one layer of a stack:

- **Review this layer's diff only.** Its base is the branch below, so the diff is
  already scoped to the layer. Do not re-litigate a lower layer's decisions here —
  comment on that layer's own PR.
- **Judge the layer standalone** (`DEV-STACK-03`). Does it build and pass its tests
  at its own tip? "Tests come in the next PR" is a blocking finding, not a
  courtesy.
- **Verify the base ref.** A layer whose base points at trunk instead of its
  parent, or whose branch lacks the parent's latest commits, is a stale cascade
  (`DEV-STACK-02`) — block until it is re-stacked.
- **Re-check your findings after a force-push.** A cascade rewrites commits, so
  confirm earlier findings and approvals survived rather than assuming they
  carried.
- **Approving a layer is not approval to merge the stack.** Merge order and
  authorization stay with `DEV-STACK-04`.

## DEV-STACK-04 — Merging and safety (ESCALATE)

First identify membership (DEV-STACK-06), affected members, current heads,
required checks, and the user's authorization. A generic request to merge one
PR does not authorize merging lower native members. Do not convert or dissolve
a stack to bypass a merge error.

- **Manual chain:** a child PR merges into its parent branch, not directly into
  trunk. Landing the bottom PR and then restacking/retargeting children is a
  separate sequence; verify each new base/head and CI. Keep a parent branch while
  an open child targets it. Merge order must follow the chosen landing procedure,
  not a universal bottom-up assertion.
- **Registered native stack:** merging the top PR can include lower members;
  merging a middle PR includes its lower prefix. This requires explicit native
  selection and authority for every affected member. The merge API is
  asynchronous; queued is not merged. Verify final landing and resulting heads.
- Merging remains user-authorized (DEV-STACK-04). Never enable auto-merge, bypass
  a queue, or reorder an already merged layer on the agent's initiative.
- Squash merging changes ancestry. Restack a manual child's descendants; for
  native stacks verify the resulting automatic rebase and refresh review/CI.
- Shared heads can interact with required reviews. Inspect pending or rejected
  reviews before retrying. Native merge requirements follow the bottom PR base.

For an authorized native merge, inspect installed CLI support. The supported
GitHub async REST endpoint takes a reviewed head SHA and returns a request UUID:

```sh
gh api --method PUT 'repos/OWNER/REPO/pulls/PR/merge-async' \
  -f sha='REVIEWED_HEAD_SHA' -f merge_method=merge -f merge_action=default
gh api 'repos/OWNER/REPO/pulls/PR/merge-async/UUID'
```

The SHA guards the requested PR, not separate lower members. On acceptance,
retain the returned UUID and poll with bounded waits; HTTP 200 may still say
pending. On conflict, inspect the existing request before resubmitting. Verify
`status: merged`, returned SHA, and each PR's target integration. Do not retry
`gh pr merge --admin` as a workaround for a native async-merge requirement.

## Anti-patterns

| Anti-pattern | Why it bites |
|---|---|
| Deep stacks (practitioner guidance: past ~4–5 layers) | Every added layer is another gated PR to review and another branch to re-stack on each cascade; practitioners report navigation cost outweighing the benefit past that range (experience, not a measured limit — see Depth above) |
| Effort-bucketed layers ("quick wins first") | Produces layers whose dependency runs opposite to the merge order, so the stack cannot land bottom-up |
| Mid-stack rewrites without a cascade | Upper branches keep a base that no longer exists; the PR diff shows unrelated commits |
| Force-push without `--force-with-lease` | Overwrites collaborator work, and may invalidate existing review state |
| Treating a base chain as native registration | Native behavior requires verified membership |
| Assuming native membership deduplicates CI | Applicable workflows still run per member |
| Assuming manual children inherit trunk rules | Inspect branch protection and workflow filters |
| Merging a native top PR expecting only that layer | It can bring lower members |
| Stacking a single cohesive change | Every layer is a separately gated PR with its own review and CI, for no parallelism gain |

## Tooling

You do not need an extension for a manual chain: `gh pr create --base
<branch-below>` expresses the dependency. Pass `--base` explicitly for
every layer: when it is omitted, `gh` uses the `branch.<current>.gh-merge-base`
config and, if that is unset, the repository's default branch — so a layer can
silently target trunk instead of its parent.

Only for task-specific native opt-in, inspect available tools. GitHub's
first-party extension is `gh stack`
(`gh extension install github/gh-stack`, requires `gh` v2.0+). Core verbs:
`init`, `add`, `push`, `view`, `submit`, `rebase`, `modify`; `up`/`down` navigate
(up = away from trunk). Stack metadata lives in `.git/gh-stack` (JSON,
uncommitted) and it enables `git rerere` on init so conflict resolutions replay
across cascades. It also ships an agent-facing skill:
`gh skill install github/gh-stack`.

Verify current feature status and installed CLI support before relying on
native behavior.

Sources last checked 2026-09-05: Git `rebase --update-refs` documentation,
GitHub documentation for [stacked pull requests](https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/proposing-changes-to-your-work-with-pull-requests/about-stacked-pull-requests)
and [asynchronous merge](https://docs.github.com/en/rest/pulls/pulls#merge-a-pull-request-asynchronously),
the `gh pr create` manual, and the `github/gh-stack` README. Reverify
time-sensitive behavior before use.
