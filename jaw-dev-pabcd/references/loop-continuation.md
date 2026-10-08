# Goal and loop continuation

Use this reference only for an authorized goal or multi-cycle PABCD loop. Read `jaw goal status`
and `jaw orchestrate status` on entry, after D, and after context loss. Preserve the user's
original objective, acceptance criteria and approved scope; do not narrow them to justify
stopping. Jaw goal and orchestration state are separate. A phase transition is not proof that
its work is complete (LOOP-READS-PABCD-01).

## Checkpoint and completion

For each completed work-phase, record a specific checkpoint with `jaw goal update <summary>
--evidence <proof>`. Point to current artifact paths, commands, exit codes and observed results.
Use `jaw goal done` only when every recorded criterion has fresh evidence
(GOAL-COMPLETE-GATE-01). Do not use a force path to launder missing proof. State whether the
real outcome is DONE, NOOP, BLOCKED, UNSAFE, NEEDS_HUMAN or BUDGET_EXHAUSTED; a stated budget
limit must actually be reached before using the last label. Pausing, compaction and IDLE are not
success.

**GOAL-IDLE-CONTINUE-01, LOOP-CONTINUE-01:** D closes the current cycle to IDLE. If in-scope
work remains under an active goal, quote D's conclusion and next direction, amend the existing
work-phase map at P as needed, and enter the next P. A new in-scope unit belongs to the same
goal; a changed direction needs a reason (LOOP-CONTINUITY-01, LOOP-UNIT-CHAIN-01). The parent
loop owner controls this decision (LANE-LOOP-AUTH-01); a bounded employee never starts its own
orchestration or goal. The initial cycle for a multi-cycle loop writes and audits the full
docs-only roadmap before implementation (LOOP-DOCS-FIRST-01, DIFFLEVEL-ROADMAP-01 in
[implementation units](implementation-units.md)). Follow the repository branch and commit rules
for authorized work (LOOP-GIT-01; [jaw-dev](../../jaw-dev/SKILL.md)).

## Repair and divergence

Read the failing observation before patching again. Two failed repairs of the same failure call
for root-cause analysis; three call for a changed P plan (LOOP-REPAIR-01). Three failed
attestations in one phase are no progress (LOOP-DOOM-01). In interactive HITL, return to
Interview when unresolved intent requires the user. With an active goal, replan at P from the
evidence or report a real terminal blocker; do not claim an Interview round occurred. A failed
independent review needs per-blocker accept/rebut synthesis before redispatch
(REVIEW-SYNTHESIS-01).

For optimization, the canonical candidate, plateau and mechanism rules remain in [SKILL.md §10
and §11](../SKILL.md#10-optimization-loop-meta-rules-plateau-discipline); this reference only
routes to them. Record divergence entry, comparison verifier and collapse decision in P/D.
Prefer conceptual alternatives first; escalate to isolated implementation spikes only when the
choice is load-bearing and evidence requires running code (DIVERGE-TIER-01). For specification
work, collapse at P when pass/fail is locally checkable; for deceptive maximize metrics, compare
candidates on the same instances and collapse at D. A mode decision is documented plan content,
not an extra CLI command.
