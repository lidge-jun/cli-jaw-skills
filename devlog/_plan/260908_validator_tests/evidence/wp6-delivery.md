# wp6 — Delivery and deployment

PR [#6](https://github.com/lidge-jun/cli-jaw-skills/pull/6) merged as `060e802`, CI
`validate` green in 8s at the PR head.

## Deployment path

This repository is source material; the runtime consumes it two ways, and both were
brought to the merged commit.

**The `skills_ref` submodule** in `cli-jaw` was pinned at `25e3078` and now points at
`060e802`. Running the new validator inside the submodule surfaced a discrepancy the old
one could not have seen: it measured **53** reference folders against the repository's 52.
The cause was `jaw-dev-speech/references/`, an empty directory left over from
2026-08-25 — git does not track empty directories, so it was invisible to `git status`
while still counting as a reference folder on disk. Removed; the submodule now reports
`236 registered skills (52 with references, 30 with scripts, 2 with templates)` with a
clean tree.

The submodule pointer bump is left uncommitted: the `cli-jaw` checkout is on
`codex/doc-drift-multiline-broadcast` with unrelated work in flight, and committing a
submodule bump onto someone else's feature branch would be the wrong place for it.
The submodule content is at the merged commit; only the parent's recorded pointer waits.

**The active runtime** `~/.cli-jaw/skills` after wp5:

| | count |
|---|---|
| real skills, all `jaw-` prefixed | 33 |
| compat symlinks | 30 |
| broken links | 0 |
| links whose `jaw-` twin is missing | 0 |
| non-`jaw-` real directories | 0 |

## What this delivery is not

The 30 symlinks were not removed and should not be: they are the documented compat layer
for the `jaw-*` migration, and every skill enumerator already skips them because they are
not directories. The one real duplicate is backed up under
`~/.cli-jaw/backups/skills-conflicts/260908-readerdocs/`.

