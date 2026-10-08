# Local Worktree and Branch Cleanup

Applies to Git worktrees and GitHub-backed branches. Canonical rule:
`DEVOPS-LOCAL-GC-01`. Remote deletion's ten keep rules live only in
`branch-lifecycle.md`.

## §1 Merge truth

Join local branches to PR state and exact head SHA, using `gh pr list --state all
--limit 1000 --json number,state,headRefName,headRefOid,baseRefName,mergedAt,closedAt,mergeCommit,isCrossRepository`.
A `MERGED` PR plus integration evidence is primary; ancestry is secondary because
squash and rebase merges rewrite it. Recheck any proposed removal against live
state. No-PR branches are report-only.

## §2 Candidate classes

| Class | Required evidence | Decision |
|---|---|---|
| Integrated | Tip is on the declared integration line, a related PR records a terminal decision, and no active checkout or unique work remains | Candidate |
| PR merged | PR says `MERGED`, tip matches its head SHA, no open child uses it as base | Candidate |
| Upstream gone, PR merged | Gone tracking ref and the merged-PR evidence above | Candidate |
| Upstream gone, PR closed | All related PRs closed beyond declared grace, permitted namespace, exact closed head SHA | Candidate only after `branch-lifecycle.md` rules |
| No PR, or `backup/`, `archive/`, `wip/` | No terminal decision or intentionally retained name | Report or preserve |

## §3 Worktree safety (`WG-NEVER-01`, `WG-MOVE-01`)

Snapshot refs and `git worktree list --porcelain` first. Never remove or move the
current worktree, its ancestor or any worktree that may be active elsewhere.
Exclude locked, dirty, untracked, unknown user-owned and detached worktrees with
unique commits. Inspect every path in place; an absent path can have recoverable
admin state. A temporary-location worktree with work is a recovery candidate.

Move or repair only an inactive worktree after inspecting its state. Use
`git worktree move` when supported, or `git worktree repair` after an already
performed manual move. Do not delete and recreate a worktree to rename it.

For an authorized cleanup, order is snapshot → status audit → unforced
`git worktree remove <path>` → remote refs → local refs. Treat Git's refusal as
a stop to inspect, never a reason to add `--force`. `git worktree prune -n` is
the dry run for stale administrative entries; pruning does not remove branches.
The Manager offers a worktree preview and guarded operations, not automatic GC.
There is no `jaw worktree gc` CLI command.

## §4 Scheduled reports (`DEVOPS-LOCAL-GC-SCHEDULE-01`, DEFAULT)

A scheduled local run reports candidates, dirty/locked trees, uncertain cases,
temporary paths and the proposed snapshot location. It deletes nothing. A
LaunchAgent is one optional implementation, not an installed default. A later
deletion needs its own authorized invocation and fresh evidence.

## §5 Anti-patterns

| Avoid | Reason |
|---|---|
| `git branch --merged` as sole proof | Squash and rebase merges can hide integration. |
| `rm -rf` on a worktree | Bypasses Git's checks and strands admin state. |
| Unlocking inside cleanup | A lock is a retention signal. |
| Treating temporary paths as disposable | They may contain unique work. |
| Changing `fetch.pruneTags` by reflex | A tag refspec can delete local tags. |
