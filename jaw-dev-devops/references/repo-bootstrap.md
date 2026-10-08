# Repository Bootstrap

Applies to GitHub repository settings. Canonical rule: `DEVOPS-REPO-BOOTSTRAP-01`.

## §0 Authority

Read actual settings first. A request to audit does not authorize changing rulesets,
merge settings, labels, or jobs. Apply only settings within the task's declared scope.
Record the observed value and the proposed delta separately.

## §1 Branch model

Read the target repository's branch and release contract before selecting controls.
For cli-jaw, feature PRs target `dev`; `preview` is the release candidate, and
`main` receives the certified fast-forward release. `preview` and `main` do not
take ordinary development commits. A generic promotion-PR template would misstate
that contract.

## §2 Rulesets (`DEVOPS-RULESET-FIRST-01`, DEFAULT)

Inspect both repository rulesets and classic branch protection before proposing
either. Compare their target refs, deletion and force-push rules, required checks,
review requirements, bypass actors and enforcement state. A migration to rulesets
is an option, not an automatic replacement. Do not remove classic protection before
the replacement is active and read back. Check that any merge queue has CI for its
merge-group event and that signature requirements fit every accepted author path.

## §3 Merge settings (`DEVOPS-MERGE-SETTINGS-01`, DEFAULT)

| Field | Audit question |
|---|---|
| `delete_branch_on_merge` | Are merged PR heads deleted? Closed-unmerged heads need the separate `branch-lifecycle.md` decision. |
| `allow_auto_merge` | Do required status checks and review rules make this safe? |
| `allow_update_branch` | Can a stale PR base be refreshed, and is that wanted here? |
| Squash, merge-commit, rebase methods | Which methods preserve the repository's stated history and release contract? |

Recommend each setting from observed policy; do not copy a default PATCH payload.
For cli-jaw, preserve its `dev → preview → main` fast-forward release path.

## §4 Closed-PR cleanup

A scheduled job is an optional repository decision. Declare disposable prefixes
and a grace period per repository. The job must apply all keep rules in
`branch-lifecycle.md`, run from the default branch, and have a reviewed write
identity. A closed PR alone is not deletion proof. Local worktree cleanup is
separately owned by `local-gc.md`.

## §5 PR limits (`DEVOPS-PR-LIMITS-01`, DEFAULT)

Check whether the host offers a per-contributor PR cap and whether drafts are
exempt before recommending a value. Reverify the current UI/API support when
implementing; do not assume a REST setter. A cap, bypass list and draft-first
choice belong to the repository maintainer.

## §6 Labels and templates

Use labels only for a review state the repository will maintain. A PR template
may ask for provenance, linked issue, scope and verification evidence. Do not
impose a generic label set or attribution convention; align it with
`agent-pr-intake.md` and the repository's contributor policy.

## §7 Read-only audit

With `OWNER`, `REPO` and `DEFAULT` set for the target, inspect:

```sh
gh api "repos/$OWNER/$REPO" --jq '{default_branch,delete_branch_on_merge,allow_auto_merge,allow_update_branch,allow_squash_merge,allow_merge_commit,allow_rebase_merge}'
gh api "repos/$OWNER/$REPO/rulesets" --jq 'map({id,name,target,enforcement})'
gh api "repos/$OWNER/$REPO/branches/$DEFAULT/protection"
gh label list -R "$OWNER/$REPO" --json name --jq 'map(.name)'
gh api "repos/$OWNER/$REPO/actions/workflows" --jq '.workflows | map({name,path,state})'
```

A 404 on classic protection means inspect rulesets; it is not proof the branch is
unprotected. For each control, report `expected | observed | delta | authority`.
