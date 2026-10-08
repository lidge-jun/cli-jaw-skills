# Agent PR Intake

Applies to repositories receiving agent-assisted contributions. Canonical rule:
`DEVOPS-AGENT-INTAKE-01`. The maintainer chooses the policy strength; this
reference supplies review evidence and options.

## §1 Identity (`DEVOPS-AGENT-IDENTITY-01`, DEFAULT)

| Tier | Observable signal | Use |
|---|---|---|
| 0 | Machine-style branch prefix | Heuristic for triage, never proof of authorship. |
| 1 | PR disclosure or accepted commit trailer | Useful only if the upstream contributor policy permits its form. |
| 2 | Bot/App author identity | Strong enough for an identity-based host rule, after verifying the actual account. |

`jaw dispatch --agent` starts an employee run; it does not establish the GitHub
author of a later PR. Do not infer a policy from the branch name or dispatch record.

## §2 Draft-first (`DEVOPS-DRAFT-FIRST-01`, DEFAULT)

The repository may ask agent-assisted PRs to open as drafts, with a person or
declared gate marking them ready after checks and explanation. Preserve workflow
approval for untrusted code. Check current host behavior before relying on a
draft exemption from a PR limit.

## §3 Supersede (`DEVOPS-PR-SUPERSEDE-01`, STRICT)

1. Compare the candidate with the landed replacement by behavior and scope.
   Classify it `LIVE`, `PARTIAL`, or `SUPERSEDED`; age and overlapping files are
   insufficient.
2. Preserve author credit in an accepted form and link the replacement PR.
   State what was carried, what was dropped, and why.
3. Label and close only truly `SUPERSEDED` work. Keep `PARTIAL` work visible with
   a focused follow-up or review request.
4. Keep a stack parent while any open child targets it. A closed head becomes a
   cleanup candidate only under `branch-lifecycle.md` keep rules 1–10.

`gh pr comment`, `gh pr edit`, and `gh pr close` change GitHub state. Use them only
when the task authorizes the corresponding action.

## §4 Policy options

| Control | Weak | Medium | Strong |
|---|---|---|---|
| Identity | Heuristic label | Accepted disclosure | Verified bot/App identity |
| Draft | Optional | Draft until checks pass | Human marks ready |
| Linked issue | Optional | Requested for larger work | Required by contributor policy |
| PR limit | None | Declared cap with draft behavior checked | Lower cap and explicit bypass owners |
| Review | Human review | Automated first pass plus human | Required check plus human |
| Supersede | Manual review | §3 procedure | §3 with a maintained automation |

Choose and document a column or a deliberate mix. No cap, deadline, trailer,
auto-close rule or agent-specific ban is selected here. A contributor's ability
to explain and verify the change matters regardless of the tools used.

## §5 Anti-patterns

| Avoid | Reason |
|---|---|
| Bot-account filter as the only detector | Human accounts can submit agent-assisted changes. |
| Automatically approving workflows for untrusted PR code | It can expose privileged CI context. |
| Requiring a trailer the upstream bans | Contributors cannot satisfy both policies. |
| Closing `PARTIAL` work as superseded | It silently discards remaining scope. |
