# Interview evidence and closeout

Use this reference when the user requests an interview or an authorized PABCD cycle enters I.
Interview behavior alone does not enter the server state machine. The main agent owns questions,
synthesis, and any transition.

## Questions grounded in the current state

Before each question, show what is known, the weakest of goal, constraint, success, and
ontology, the remaining gap, and what the answer will change (INTERVIEW-RENDER-01). Target that
weak dimension and expose a consequential assumption or boundary, rather than collecting a
feature list (INTERVIEW-Q-01). Ground questions in the user's answer and repository evidence; do
not ask again for facts already established. Ask dependent questions in sequence; bundle only
questions whose answers cannot change one another (INTERVIEW-INDEPENDENT-01).

Present concrete trade-offs when choice is open. Include one materially different option to
counter a set of near-identical choices. If a cheap comparison can settle a load-bearing
uncertainty, offer `A · B · BOTH (bounded spike, select by evidence)` and name its comparison
verifier (INTERVIEW-OPTION-01). Do not invent options where the repository or user has already
decided.

After each answer, reconcile the existing `<interview_tracker>` knowns, unknowns, assumptions,
and contradictions with the answer before composing the next question (INTERVIEW-GROUND-01). A
vague answer leaves its gap open. Rescan semantic contradictions after each answer and
immediately before a proceed decision (INTERVIEW-SCAN-01). Jaw's I→P readiness check is soft;
this rescan and the evidence summary are agent discipline, not a hard ledger gate.

## Assumption provenance

In the plan, give each inferred assumption an id, `proposed` or `open` status, source,
low/medium/high confidence, and an `if wrong` consequence (INTERVIEW-ASSUME-01). Source a
repository claim as `path:line` or a user claim as `user reply <date/turn>` with the actual
reply quoted and located in the conversation or plan. Example: `A3 [proposed] exports remain CSV
— source: src/export.ts:41; confidence: medium; if wrong: include the XLSX writer and tests.`
Only an actual user answer can make an item confirmed or rejected. Keep open assumptions
separate from confirmed requirements and rejected decisions; do not promote an inference by
repetition.

## Optional read-only lenses

Where delegation is authorized and a suitable employee exists, send a compact tracker snapshot
and one named contradiction lens through `jaw dispatch --agent <employee> --read-only
--task-file <brief>` (MIND-SPAWN-SHAPE-01). Useful lenses are contrarian, socratic, ontologist,
evaluator, and simplifier. The brief states its evidence scope and asks for contradictions,
assumptions, and source anchors; the employee neither asks the user nor changes the plan. Main
triages its findings. If no employee is available, reason locally and do not call that
independent evidence.

## Closeout

Show confirmed requirements with their sources, then open assumptions and consequences. Offer
`Proceed to Plan`, `Keep interviewing`, or `Record assumptions and pause` (INTERVIEW-FORK-01).
Proceed means Plan entry, not permission to build. When stateful orchestration is authorized,
run `jaw orchestrate status`, then `jaw orchestrate P`, then verify status; otherwise provide
the interview result without a state transition.
