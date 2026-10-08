# Phase control on cli-jaw

Use `jaw orchestrate status` before and after each authorized edge. The FSM is server-scoped, so
confirm that the current cycle belongs to this conversation before mutation
(SESSION-IDENTITY-01). A narrated phase is not a persisted transition (ORCH-MANDATE-01).
Advancing requires the phase's real artifact, not merely plausible attestation text
(ORCH-ARTIFACT-01).

| Edge | Agent CLI attestation and artifact |
|---|---|
| Any state→I; IDLE/I→P | Legal entry or clarification; no `--attest` required. Enter only when authorized. |
| P→A | `from`, `to`, `did`; point to the diff-level plan. Add `planUnit` at the repository-approved location; its absence is advisory. |
| A→B | `from`, `to`, `did`; identify review output and boss judgment. Carry `auditOutput`, `auditVerdict`, and residual dispositions. Declared `fail` blocks; `near-pass` needs `auditResidual`. |
| B→C | `from`, `to`, `did`; point to the implementation delta. |
| C→D | `from`, `to`, `did`, nonempty `checkOutput`; `exitCode`, if supplied, must be zero. Point to fresh, relevant verification. D closes to IDLE. |

For every gated edge, `--attest` takes JSON with the exact `from` and `to` and a specific,
non-placeholder `did` (ATTEST-SHAPE-01). `planUnit`, `workPhaseId`, `auditOutput`,
`auditVerdict`, and `auditResidual` survive parsing; the latter two verdict conditions above are
enforced. Other audit fields are advisory when absent, so do not describe them as a hard gate.
`did` should name the artifact path, changed files, verifier command and exit code, and a goal
checkpoint when applicable (ATTEST-EVIDENCE-01). The parser does not independently prove the
narrative true. Example: `jaw orchestrate B --attest '{"from":"A","to":"B","did":"audited plan
at <path>; folded blockers","auditOutput":"<review
tail>","auditVerdict":"near-pass","auditResidual":"<each residual and disposition>"}'`.

The CLI has no `--attest-file` or `--session` argument. It does not support `testReceiptPath` or
an Interview `override` attestation. Do not infer enforcement for such fields. `jaw orchestrate
reset` is an explicit reset, not an ordinary forward edge. User and project authorization still
govern entry, phase pauses, and exceptional resets.
