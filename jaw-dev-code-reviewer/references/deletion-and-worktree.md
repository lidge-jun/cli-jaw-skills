# Guard removal, retired-capability creep, and review worktrees

Canonical owner: `jaw-dev-code-reviewer`. Extracted from the router so it stays
under its line budget; the rules are unchanged.

## Guard Removal (REVIEW-GUARD-REMOVAL-01, DEFAULT)

Deleting input validation or error handling at a **trust boundary** requires a
regression test that actually **exercises the deleted path**. For an input-validation
guard that means malformed or hostile input; for an error handler it means injecting
the fault that reaches it — network timeout, connection reset, filesystem I/O failure,
subprocess failure. Attaching an unrelated input test to satisfy the form does not meet
this bar.

Without that test, the deletion is a **High** blocker. In particular, the
"over-defense" antipattern in §3 is **not by itself** grounds for calling a boundary
guard unnecessary — that row is about defense piled up behind a boundary, not about the
boundary check itself.

Trust boundaries are where external input first lands: process stdin, CLI arguments,
file parsing, network responses, and sub-agent output.

Judge by the **kind** of deletion, because the expected test result inverts between
them:

- A **replacing or relocating** deletion — the check moves to a different layer — must
  stay **green** after the old guard is removed, and go **red** only when the surviving
  boundary check is also removed. Green here proves the relocation worked.
- A **non-replacing** deletion — the check is simply gone — has a regression test that
  goes **red**. Red here proves the guard was load-bearing, which means the deletion
  should not land.

Getting that inversion backwards is how a relocation gets blocked and a genuine
removal gets approved.

## Retired-Capability Creep (REVIEW-REMOVED-BACKEND-01, DEFAULT)

A change touching a document that lists **available capabilities** — a search-backend
list, a provider roster, a supported-runtime table, a tool ladder — gets checked for
capabilities that were retired reappearing as if they were still available. A retired
name may appear only in explicitly historical or non-goal framing.

There is no automated check for this, and often there cannot be a useful one: the prose
has no registry in code to compare against, which is exactly the
`TEST-PROMPT-SEAM-01` situation (`jaw-dev-testing`). A scan that reads one prose file for
phrase existence breaks on rewording and proves nothing, so the protection belongs to a
reviewer's read rather than to a test. If a registry ever lands in code, revisit whether
a real two-source check is possible.

The upstream version of this rule names a specific list of retired backends. That list
is that ecosystem's own retirement history and is deliberately not reproduced here —
what transfers is the reviewer obligation, not the names. Keep your own retired-name
list wherever the retirement was decided.

## Review Worktree (REVIEW-WORKTREE-01, DEFAULT)

Never check out another review ref in the worktree you were handed. If the review
target is already checked out where the dispatcher put you, review it there; otherwise
create or attach a **dedicated named worktree** and run the checkout, tests, and QA in
that one. Record `pwd -P` and the target `HEAD` alongside the interdiff anchors above.

The condition is **observable state, not ownership**. A reviewer — often a sub-agent —
cannot know which branch the parent session considers its own, but it can always see
what is checked out where it stands. Framing the rule around ownership would make it
unenforceable by exactly the actor who has to follow it.
