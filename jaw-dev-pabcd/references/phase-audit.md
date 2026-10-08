# Audit phase

Audit the actual plan, not a summary. Where authorized and available, send a read-only brief
with exact plan paths and scope through `jaw dispatch --agent <reviewer> --read-only --task-file
<brief>`. If independent delegation is unavailable, record that limit and perform a clearly
labeled local audit. The boss owns the verdict and synthesis.

Check path and import existence, signatures, dependency order (PHASE-SPLIT-01), plan residence
and numbering (UNIT-RESIDENCE-01, LEXICO-SPLIT-01), and every decade document in a multi-cycle
roadmap (DIFFLEVEL-ROADMAP-01). Check trigger reachability and an observable C scenario for
conditional paths. The reviewer RUNS each applicable named verifier and confirms it observes
the target; scope one out only with a stated reason (PLAN-VERIFIER-REAL-01). Check every new field's
creation/serialization/deserialization/consumer chain, shared names and document dependencies
(PLAN-FIELD-CHAIN-01). For enforcement, check the five bypass fields and residual claim
(PLAN-BYPASS-NAMED-01). Check repository privacy and public-boundary instructions.

Ask the reviewer to end with one normalized verdict: `VERDICT: PASS (blockers=0)`,
`VERDICT: GO-WITH-FIXES (blockers=N)`, or `VERDICT: FAIL (blockers=N)`.
Require numbered blockers, source anchors and precise remedies. **AUDIT-LOOP-01:**
audit → synthesize per blocker → amend plan →
re-audit. The main agent records root cause, conflicting advice, and accept/rebut rationale
before the next round (REVIEW-SYNTHESIS-01). A `FAIL` never exits A. `near-pass` requires each
serious blocker to be amended or explicitly rebutted and every residual named with its
disposition; after three failed rounds, return to P with a changed plan (HITL may return to
Interview when human clarification is missing). A final adversarial review should be independent of a reviewer who shaped the
fix. Reuse an existing reviewer only where the jaw runtime actually supports a same-worker
follow-up; otherwise dispatch a new round with the prior evidence attached.

**LEAN-REVIEW-01:** useful review can also happen during B and C; the A audit is not a monopoly
on verification. Preserve each review’s evidence in its phase artifact. Do not claim an
automatic reviewer gate beyond jaw’s attestation checks.

For A→B, carry `auditOutput`, boss `auditVerdict` (`pass`, `near-pass`, or `fail`) and, for
near-pass, `auditResidual` in `jaw orchestrate B --attest <json>`. The parser preserves these
fields and rejects declared `fail` or near-pass without residuals. Missing audit fields receive
advisories rather than a hard proof gate, so the agent must verify the real review output. See
[phase control](phase-control.md).
