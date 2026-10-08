# Employee dispatch and waiting

This reference governs bounded employee work. The main agent retains plan, goal, phase
transitions, final judgments and integration. Dispatch does not allocate a checkout. Check
employee availability, actual repository root and permissions before asking for work.

## Surface and packet

`jaw dispatch --agent <employee> --task-file <brief> --read-only --async` sends a read-only
assignment; an authorized implementation slice uses `--mutable --scope <path>`. `jaw dispatch
--batch --agents-file <path> --async` sends a batch. `jaw worker status <runId>`, `jaw worker
watch <runId>` and `jaw worker read <runId> --tail <N>` inspect progress and results. Record the
returned runId, employee, read bounds, write scope, checkout, and owner for branch/HEAD
operations (DISPATCH-SURFACE-01, DISPATCH-LANE-ID-01). Do not assume a worker inherits the
caller's working directory. Parallel writers require disjoint scopes; one owner handles each
branch/HEAD and integration step. If a branch lane needs its own checkout, arrange and verify
that separately (DISPATCH-ROUTE-01). `--cli` and `--model` apply to virtual dispatch; do not
promise model overrides for named employees (DELEGATE-MODEL-LIST-01).

**DISPATCH-TASK-01, DISPATCH-AGENT-TYPE-01:** The packet states `TASK · SCOPE · MUST DO · MUST
NOT · PROOF · RETURN FORMAT · decision boundary`. Begin with `Project root: <absolute path>`,
name the exact files or questions, policy skills in text, allowed reads/writes, and whether the
employee is read-only or mutable. Read-only review is the default; writing needs explicit
`--mutable` and a bounded scope. For independent parallel lanes, list which prior outputs each
may read and keep in-progress peer drafts outside that list (DISPATCH-ISOLATION-01). A worker is
a leaf unless descendant dispatch is explicitly granted (LEAF-TOPOLOGY-01). A specialist can
rederive a narrow crux from first principles and return assumptions and its changed decision
(SPECIALIST-CRUX-01). Where a different model family is actually available, an independent A
reviewer may use it to reduce shared blind spots (REVIEW-DECORRELATE-01).

Dispatch only when the task is specifiable, its evidence checkable, and final judgment stays
with main (DISPATCH-ECONOMY-01). Each required verifier command must be named exactly. The
return reports one result per command with exit/status, observed target and source anchors, plus
uncertainties; separate any extra checks (DISPATCH-VERIFIER-01). Name the scope, evidence and
decision boundary even for a small read-only task. Main accepts, rejects or amends each return
with a brief reason before the next wave, then promotes accepted evidence into the current
approved plan or worklog (DISPATCH-PROMOTE-01). A worker's claim is evidence to verify, not a
phase transition.

Speculative work for a later phase is off by default. The narrow exception is external research
independent of changing repository state; label it `candidate — unverified` and recheck it at
the later P (DISPATCH-SPECULATE-01).

## Waiting and retirement

Use bounded `jaw worker watch/status/read` observations and meaningful user updates while work
continues (LOOP-WAIT-VISIBILITY-01). A timeout is an observation boundary, not a failure or
permission to stop. Check the exact runId and read the final output rather than assuming a
progress message is the answer. Consume each distinct runId result once across dispatch output
and worker reads; do not merge duplicate notifications into multiple verdicts
(DISPATCH-CONSUME-ONCE-01).

**LOOP-WAIT-EVIDENCE-01, DISPATCH-RETIRE-01:** Classify the observed run as progress, suspected
stagnation, confirmed failure, or unobservable. Progress is new findings, edits, command
evidence or an artifact advancing the packet; repeated no-op status is only liveness. Suspected
stagnation needs comparable observations and a stated next review point. Confirmed failure needs
an actual terminal error, unusable final output, or stagnation evidenced at that review point. A
quiet but healthy long command is not a failure. Unobservable means the available state cannot
establish either progress or failure; report the gap. Do not retire by elapsed waits alone.

On confirmed failure, record the reason and last meaningful activity. If a stop is available and
authorized, verify actual termination, owned processes and partial edits before replacement.
Unknown termination forbids an overlapping writer. At most one retry on the same worker where
the runtime supports it; otherwise issue a fresh dispatch with failure evidence. Two independent
failures on the same packet call for main to reclaim and rewrite the packet rather than
launching a third copy. Explicit cancellation and actual resource bounds outrank retry. Do not
label cancellation, budget exhaustion or task stagnation as a provider error. Reusing an
employee across rounds is conditional on an actual follow-up route; a fresh final adversarial
reviewer avoids judging its own influence (DISPATCH-ACTOR-01).

## Fan-out, wake and integration

Bound concurrent dispatch by configured employee/API capacity, disjoint write scopes, review
cost and a shared poll budget (DISPATCH-FANOUT-CAP-01, DISPATCH-POLL-BUDGET-01). Polling cadence
and user-update cadence are separate. Batch independent work, then synthesize before another
wave. For work outliving the current turn, verify a registered `jaw bgtask` completion wake or
another available, authorized wake; never infer one from `--async` alone (DISPATCH-WAKE-01).

Integrate separate checkout lanes serially (DISPATCH-LANE-MERGE-01). Before each integration,
record the actual ref, HEAD, tested SHA, changed paths, verification output and unresolved
conflicts; recheck after integration. The canonical hosted CI rule is
[DEV-CI-EVIDENCE-01](../../jaw-dev/references/hosted-ci-evidence.md), and the repository's stack
procedure is [stacked PRs](../../jaw-dev/references/stacked-prs.md). This reference does not
grant merge or publish authority. Keep private packet and audit records only at the
repository-approved location.
