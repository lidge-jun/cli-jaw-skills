---
name: jaw-dev-pabcd
description: "MUST USE for cli-jaw PABCD orchestration workflows — orchestrate, phase, attest/attestation, interview mode, goal mode, checkpoints, and multi-phase development. Triggers: orchestrate, phase, attest, attestation, interview, goal mode, checkpoint, PABCD, 요구사항 정리, 인터뷰, 스펙 정리. Operate state transitions only when the user explicitly requests orchestration or an active PABCD phase is injected — do not transition state merely because a document mentions phases, goals, or checkpoints."
metadata:
  short-description: "cli-jaw PABCD orchestration workflow for interview, phases, attest, and checkpoints."
  last-verified: "2026-10-08"
---

Structured 5-phase development. Advance with the required user approval or, in authorized goal mode, an evidence-backed checkpoint.
> **C0/C1 work:** see `jaw-dev` §0.0 Work Classifier and §0.1 Patch Fast-Path first — full
> PABCD is mandatory for C4 and conditional for C3, not the baseline for every task.

> **`jaw-dev` is canonical:** `jaw-dev` §0.2 Rule Classes, §3 Verification Gate, and §5 Safety Rules apply to all work governed by this skill.

## §1. Interview Trigger (MUST)

Use Interview behavior for an interview request; read [Interview evidence and closeout](references/interview.md). Enter persisted I only when the user explicitly requests stateful orchestration or an active authorized PABCD workflow requires it. Read `jaw orchestrate status` first. An interview-only, read-only, or plan-only request does not itself authorize a state transition. Jaw's I→P readiness gate is soft; keep textual evidence and contradiction checks.

- **Teach the decision space, don't only narrow it** (DEFAULT, INTERVIEW-TEACH-01):
  intent transfer is bidirectional — a user cannot choose among options they have
  never seen. Questions that merely confirm details the user already stated are the
  weak form; the strong form maps the option landscape (research it first when
  needed) with a trade-off explanation per option, at every load-bearing altitude:
  stack, architecture, **algorithm/strategy**, data structure, evaluation method.
- Recommend one with project-specific reasoning
- Confirm once, then proceed

For broad changes or unfamiliar repositories, P phase MUST include:
- Compact tree of the current repository shape
- Detected repo conventions: docs, plans, architecture notes, source-of-truth logs, naming, tests
- Whether existing `structure/`, `devlog/`, `docs/`, `plans/`, or equivalent logs were read and will be reused
- Whether `structure/` or `devlog/` is proposed
- The SoT sync target (SOT-SYNC-01): which general source-of-truth doc
  (`structure/`, architecture/INDEX docs) this unit will patch in C — or, if the
  repo has none, the plan recommends creating one (jaw-dev-scaffolding §2.1)

Do not create new project-level source-of-truth folders during B unless approved in P or explicitly requested by the user.

For every planned conditional path (error handler, fallback, retry, cache, guard,
feature-gated branch, threshold behavior), the plan's accept criteria name its
**activation scenario**: how C will trigger the condition and what observable effect
proves the path ran (C-ACTIVATION-GROUNDING-01, §3 C).

Design phases before mapping them to PABCD. **Slice and order phases by
dependency/architecture structure (STRICT, PHASE-SPLIT-01)** — the orthodox
unlimited-time build order: foundations (schema, contracts, core data flow) → core
capabilities → integration → hardening/polish — so each phase consumes the verified
output of the previous one. DB/API/UI/test work inside a phase are subtasks, not
top-level phases by default, and every phase must still close with something
independently verifiable (build, tests, or a demonstrable surface). Effort-based
bucketing is FORBIDDEN: never split or order phases by estimated effort or payoff
speed — no "quick win vs heavy" buckets, no impact/effort matrices, no time-boxed
slices. Phase boundaries encode the system's build order, not the schedule. A simple
task can finish in one PABCD with several small phases; larger work splits into
multiple PABCD passes — one full P→A→B→C→D per work-phase, closed by D and
re-entered at P for the next work-phase (see Terminology / Rule 4).

Read project docs and jaw-dev skills first. Write the complete plan internally, then report it simply — like a developer reporting to the CEO.

Write a plan with two parts:

**Before P settle three things** (DEFAULT, INTERVIEW-CLASSIFY-01):
the work class (dev §0.0), the **loop archetype** (§11.4) — ask "does a verifier
define *done* for this work, or only *better*?" — and the **unit residence**
(UNIT-RESIDENCE-01, §3.1). Apply this in HITL Interview when authorized, or in goal-mode planning without inventing an Interview round. An archetype discovered after candidates were burned indicates inadequate initial classification.

**Interview may widen, not only narrow** (DEFAULT, INTERVIEW-DIVERGE-01): sometimes the
truest transfer of intent is "we don't know yet — test both." When a load-bearing
choice is genuinely uncertain and a spike is cheap, present options as
`A · B · BOTH (parallel spike, select by evidence)` instead of forcing one pick.
Generate the option list against typicality bias: the 2-3 options a model volunteers
are usually one attractor family — deliberately include at least one atypical
(low-probability) approach. A `BOTH` answer becomes an explore-and-select work-phase
(§11.4) with the comparison verifier declared in the loop-spec. Divergence seeded at
Interview is far cheaper than divergence discovered at a plateau.

**Interview sub-modes** (DEFAULT, INTERVIEW-CATALOG-01): pick by the user's knowledge level.
*Clarification* (existing) — the user already knows roughly what they want; questions structure
goals, constraints, success criteria. *Catalog Discovery* — the user names a vague domain but no
features ("사주 앱 만들고 싶어", "뭘 만들지 모르겠어"); see below. *Configurator* — compile the
selections into a spec. Heuristic: concrete feature/goal → Clarification; vague domain, no tech
specifics → Catalog Discovery; explicit user request → honor it.

**Catalog Discovery — design/UX LEADS** (DEFAULT, CATALOG-DESIGN-FIRST-01): the user cannot choose
from options they have never seen (the strong form of INTERVIEW-TEACH-01). Present the option
ontology in `references/catalog-discovery.yaml`. *Hard barrier:* iterate `axis_order` by ascending
`stage`; do NOT present a stage until every `required` entry of all earlier stages is answered.
Stage 1 is design, so all six design dials (mood, lightness, density, shape, typography, motion),
each `required: true`, MUST be answered before any Stage 2 (domain) or Stage 3 (feature/data/
security/ops/cost) question appears. This is the load-bearing invariant — backend is asked on top
of design, never before it.

- *Design methodology — Product-Personality Selection first* (`design_methodology.primary`, from
  jaw-dev-uiux-design §1): for each design dial show its `question_options` (labels + trade-offs)
  anchored on familiar products, then ask (present-then-ask, not confirm-what-they-said); refine
  via the declared `followups` — Korean Request Translation (§3), Reference Discovery (§1 Step 6),
  Design Read (§2).
- *Deriving backend questions* — two paths populate Stage 3 from earlier answers, never a flat
  list: **structural** — a chosen Stage-2 domain entry's `implies[]` plus each Stage-3 entry's
  `derived_from` (resolve `implies[]` transitively); **keyword** — scan the user's INITIAL
  free-text request against Stage-3 `auto_activate_rules` (e.g. "사주"/"생년월일" pre-activates
  `security.pii_protection`). Confirm high-impact activations.
- The catalog is a DATA STRUCTURE — do not invent entries not in it. The YAML encodes derivation
  INPUTS + dependency metadata; this prose is the agent procedure that reads it. Automated runtime
  filtering is out of scope (it would escalate to code).

**Configurator**: once selections are complete, compile them (with resolved `implies[]` chains)
into a spec — PRD sections, an MVP cut ordered by `cost_class`, a risk register of every
`risk_class: high` entry, and a PABCD plan seed carrying the work class + loop archetype from
INTERVIEW-CLASSIFY-01.

## §2. How It Works

```
IDLE ──→ P ──→ A ──→ B ──→ C ──→ D ──→ IDLE
         │      │      │      │      │
        STOP   STOP   STOP   auto   auto
        wait   wait   wait
         └──────┴──── I (Interview) — reachable from any phase, context preserved

Transitions (each phase accepts only its predecessor):
jaw orchestrate I|P|A|B|C|D   → I from any state (context preserved); P from IDLE/I;
                                    A←P, B←A, C←B, D←C (D returns to IDLE)
jaw orchestrate reset         → IDLE from any state (context cleared); re-enter with P
```

### §2.1 Evidence gate (forward transitions)

The four forward transitions (P→A, A→B, B→C, C→D) require an **evidence attestation** — a
real `jaw orchestrate` command with an `--attest` JSON, not narration. The server gates the
agent (identified by its boss token); a human's `/orchestrate X` keeps the free pass.
P, A, and B also require user approval; C and D proceed automatically once their work
is done. In goal mode, §4 rule 4 replaces user approval with evidence-backed checkpoints.

```
jaw orchestrate A --attest '{"from":"P","to":"A","did":"<the concrete plan you wrote: files/surfaces + approved plan path>"}'
jaw orchestrate B --attest '{"from":"A","to":"B","did":"<audit and disposition>","auditOutput":"<review tail>","auditVerdict":"pass"}'
jaw orchestrate C --attest '{"from":"B","to":"C","did":"<what you built + who verified it>"}'
jaw orchestrate D --attest '{"from":"C","to":"D","did":"<what you checked>","checkOutput":"<paste the real tsc/test tail>","exitCode":0}'
```

The gate validates form and declared audit outcomes: a specific `did` is required; declared `auditVerdict:"fail"` blocks A→B, and `near-pass` requires `auditResidual`. C→D requires non-empty `checkOutput` and, if present, `exitCode:0`.
It does NOT cross-check the narrative against runtime state — it forces a deliberate,
specific claim, not malice-proofing.

**Evidence pointers (DEFAULT, ATTEST-EVIDENCE-01):** even though the gate checks form
only, write `did` with artifact pointers: approved plan path, changed-file list, verifier
command, exit code, and relevant `jaw goal update` checkpoint when goal mode is
active, so a later reader can re-check the claim. Narration without running the
command does nothing: the state moves only on the command.

Threat model = laziness, not malice. Accepted residuals (NOT bugs): fabricated `did`,
the hidden `--force` hatch, a prior-turn `pendingAttestation`, and boss-token stripping
(closing it would break the legitimate human-via-CLI free pass).

### 2.2 Orchestration invariants

Four rules govern what a transition means. The gate enforces attestation shape and some declared outcomes; artifact truth and cycle ownership remain agent duties.

**ORCH-MANDATE-01 (STRICT) — a narrated phase did not happen.** A phase claim without
a persisted transition is invalid. Narrating phases — "now I'm in B", "the audit
passed" — without issuing them is the failure this rule exists to stop: nothing gated
anything, the log is empty, and the cycle is one ordinary turn wearing a PABCD
costume. §2.1 already says it for one edge; this generalizes it to entry and re-entry.

1. **Read the real state before claiming one.** Query the current phase, or read the
   last recorded transition. Do not resume from memory.
2. **Arm the mode explicitly** — enter at `orchestrate I` or `orchestrate P`.
3. **Advance every forward edge with an evidence-bearing attestation**, carrying that
   phase's real artifact (ORCH-ARTIFACT-01 below).
4. **After D closes, read durable state** — the plan record and the transition log —
   to confirm what remains, then re-enter P for the next work-phase (LOOP-UNIT-CHAIN-01).

Work outside an authorized cycle does not become a recorded phase by narration. Read actual server state and document the real artifact before advancing; never fabricate a prior transition.

**ORCH-ARTIFACT-01 (DEFAULT) — advancing a phase is not doing it.** Each forward edge
must carry its real artifact, not just an attestation string:

| Edge | Required artifact |
|---|---|
| P→A | the actual diff-level plan document |
| A→B | an audit verdict that names its blockers |
| B→C | the implementation delta |
| C→D | fresh relevant check output — non-empty `checkOutput`, zero `exitCode` when supplied |
| D | a cycle summary with evidence and the next-phase decision |

A phase whose artifact is absent is not done, regardless of adjacency. The gate is
form-only and cannot tell a real artifact from a plausible sentence; this rule is the
discipline the gate cannot enforce.

**ATTEST-SHAPE-01 (STRICT) — name the edge.** Every supplied `--attest` object carries exact `from`, `to`, and a specific `did` for the transition. P→A may carry `planUnit` at the repository-approved plan location; its absence is advisory. A→B carries actual `auditOutput`, boss `auditVerdict`, and residual dispositions. The parser preserves `planUnit`, `workPhaseId`, `auditOutput`, `auditVerdict`, and `auditResidual`; declared `fail` blocks A→B and `near-pass` requires `auditResidual`. `testReceiptPath` is unsupported. See [phase control](references/phase-control.md) for real edge requirements and CLI limits.

**SESSION-IDENTITY-01 (STRICT) — do not attest for a state you do not own.** cli-jaw
keeps one FSM per server rather than one per session, and `jaw orchestrate` takes no
`--session` flag, so there is no id to get wrong here. What remains is the failure the
rule exists to prevent: advancing a phase that another conversation is mid-cycle on.
Read the current phase before claiming one, and when several conversations share the
server, confirm the in-flight cycle is yours before advancing it.

Two cycles writing one record is not a mistake that reports itself: the other
conversation's phase moves without it acting, and neither side can tell from inside.
That is why this is STRICT rather than hygiene. See [phase control](references/phase-control.md).

## §3. Phases

### P — Plan

Read [Plan phase](references/phase-plan.md) for the loop-spec, consultation when authorized, verifier/field-chain/bypass checks, and the reader summary. **PHASE-SPLIT-01:** order work-phases by dependency and give each a verifiable outcome. Name activation scenarios for conditional paths (C-ACTIVATION-GROUNDING-01). Plan-only scope does not authorize execution. Present the plan and obtain any required approval before P→A.

### §3.1 Implementation-Unit Documents

For C2+ planning or any multi-cycle roadmap, read [Implementation units](references/implementation-units.md) (DIFFLEVEL-ROADMAP-01, LEXICO-SPLIT-01, UNIT-RESIDENCE-01). Use the repository-approved plan location; never create private records in a public checkout. C0 creates no numbered record; C1 records only inside an already-existing unit. C2+ follows the approved unit convention. For projects allowing in-tree records, `devlog/_plan/YYMMDD_slug/` remains the default placeholder; repositories forbidding them use an approved external location.

### A — Plan Audit

Read [Audit phase](references/phase-audit.md) for actual path, verifier and evidence review, then synthesize blockers and re-audit (AUDIT-LOOP-01). A declared `fail` cannot advance; near-pass records each residual disposition. The main agent judges the verdict and carries `auditOutput`, `auditVerdict` and, when applicable, `auditResidual` into A→B. Independent review is conditional on authorized delegation and an available employee.

### B — Build
Implement the plan. You write code by default and own every verdict; a worker may
write when its slice passes DISPATCH-ECONOMY-01 ([dispatch](references/dispatch.md)) and the dispatch is
explicitly write-capable with a bounded scope (see Pitfalls). Workers without that
grant are read-only verifiers. Do not create new source-of-truth folders unless approved in P; keep private records only in the repository-approved location. After implementing, output
worker JSON for verification (code exists, integrates cleanly): NEEDS_FIX → fix and
re-verify (repair thresholds §11.3); DONE → report to the user.

⛔ Wait for user approval. When approved, advance with the canonical B→C attestation form in §2.1.

### C — Check

Read [Check phase](references/phase-check.md) for fresh target-specific verification, SoT sync (SOT-SYNC-01), rendered and paged artifacts (C-RENDER-GROUNDING-01), reachable conditional paths (C-ACTIVATION-GROUNDING-01), and the reader check (C-READER-01). C→D carries real nonempty `checkOutput`; an `exitCode`, if supplied, must be zero. Register and verify a `jaw bgtask` wake before yielding on a long external gate.

### D — Done
Summarize the entire flow: what was planned (P), audited (A), built (B), checked (C);
the list of files changed; any follow-up items.

**Pessimistic close-out (DEFAULT, LOOP-PESSIMIST-01):** for loop/multi-pass work, D also
records the negative delta: what did NOT improve, which hypothesis died this cycle, and
one sentence answering "what evidence would show the current direction is wrong?" The
next P quotes this (§10 LOOP-CONTINUITY-01). D→IDLE→P is a context/bias-flush boundary:
the next cycle resumes from disk artifacts, not the transcript's accumulated assumptions.

State returns to IDLE automatically. Project root configuration is persistent: D
resets PABCD state but not `projectDirs`; `jaw project clear` only on explicit
user request.

## §4. Rules

1. One phase per response (the gate-and-wait turn boundary; canonical approval rule in §2.1).
   Goal-mode exception: with an active goal, do not end the turn before D while
   PABCD-phases remain — keep going P→D, close D, re-enter P for the next work-phase.
2. Sequence: P → A → B → C → D. Use `jaw orchestrate reset` to restart.
3. Workers verify (read-only) by default; write-capable dispatch follows [dispatch](references/dispatch.md)
   DISPATCH-ECONOMY-01. Verdicts stay with the boss in B.
4. Goal-mode precedence: when a jaw goal is active (dev §0.4), use §2.1 with
   evidence-backed checkpoints (`jaw goal update`) instead of user approval; phase
   order, audit conditions, and verification intensity are unchanged.

Gate quick-reference (strict vs goal mode):

| Gate | Strict PABCD | Goal mode |
|------|--------------|-----------|
| P→A, A→B, B→C | user approval + `--attest` | evidence-backed checkpoint + `--attest` |
| C→D | auto + `--attest` w/ `checkOutput`/`exitCode` | same |
| Turn boundary | one phase per response | continue P→D within the cycle |

## §5. Terminology: work-phase vs PABCD-phase

**work-phase** = one outcome slice of a larger goal (e.g. "Phase 3: Management API");
**PABCD-phase** = one letter P/A/B/C/D inside a single orchestration cycle.

Work-phases need not be slices of one feature: successive cycles in the SAME session
may target completely different features or plans under the same goal
(LOOP-UNIT-CHAIN-01). "This needs its own PABCD" is a plan statement — append the unit
to the slice map and run it as the next cycle, never a reason to end the goal or defer
to a new session.

**Invariant: one work-phase = one full PABCD cycle.** Run P→A→B→C→D, close D (→ IDLE),
then `jaw orchestrate P` for the next work-phase. Never run B for several
work-phases back-to-back or commit out of B without passing C and D. Depth scales per
class (§9); the P→D **sequence** is never skipped.

**Loop / multi-pass tasks** run one complete P→A→B→C→D cycle per work-phase. A two-or-more-cycle loop starts with a docs-only roadmap cycle (LOOP-DOCS-FIRST-01, DIFFLEVEL-ROADMAP-01); later P cycles revalidate their prewritten unit against the live tree. See [Implementation units](references/implementation-units.md) and [Goal and loop continuation](references/loop-continuation.md) (LOOP-READS-PABCD-01). With remaining authorized work, D→IDLE is followed by the next P (GOAL-IDLE-CONTINUE-01).

## §6. Repository Root Contract

Before writing a PABCD plan or dispatching an employee, determine the actual
working repository root with `pwd -P` from the target repo. If `Project root` is
injected at the top of the system prompt, use it directly; if not, recommend the user
configure it (Manager UI → Project settings, or `jaw project set /path/to/repo`)
to avoid JAW_HOME/codebase confusion. Every A/B phase `jaw dispatch` task body
MUST begin with `Project root: /absolute/path/to/current/repo`.

Rules: `Project root` is the current working repository, never `JAW_HOME`; workers never infer
the root from `~/.cli-jaw*`, `process.cwd()`, or a temp dir; all relative repo paths
resolve against `Project root`; if it is unknown, STOP and ask before dispatching.

## §7. Shared plan and bounded dispatch

Read [Employee dispatch and waiting](references/dispatch.md) before authorized employee work. The packet names the project root, approved plan, task, read/write bounds, exact proof and decision boundary (DISPATCH-TASK-01, DISPATCH-AGENT-TYPE-01). Confirm actual plan delivery in the worker task rather than assuming a CLI dispatch injected it. Record runId, inspect `jaw worker status|watch|read`, classify observed progress before retirement (DISPATCH-RETIRE-01), and integrate returns under main ownership. The parent alone owns goal, phase and loop authority (LANE-LOOP-AUTH-01); [loop continuation](references/loop-continuation.md) owns checkpoints and next-P decisions. Hosted CI proof lives in [jaw-dev](../jaw-dev/references/hosted-ci-evidence.md), and stack procedure in [stacked PRs](../jaw-dev/references/stacked-prs.md).

## §8. Pitfalls

**Delegation Trap** — B phase: Boss writes by default. Workers are READ-ONLY verifiers
unless granted otherwise. A worker may write only when the slice passes
DISPATCH-ECONOMY-01 ([dispatch](references/dispatch.md): specifiable, verifiable, no verdict ownership) AND the
dispatch is explicitly write-capable with a bounded scope (`--mutable`, optionally
`--scope`). Without `--mutable`, "implement/write/create" tasks are forbidden. Always
allowed: `"verify src/x.ts compiles"`, `"check integration of Y"`, `"report DONE or
NEEDS_FIX"`.

**Context Drift** — a worker reconstructing the plan from a thin brief needs the actual approved plan and scope attached. Verify what it received before relying on its result.

**Phase Skip** — A (audit) is mandatory for C4, and for C3 when public contract,
architecture, persistence, cross-agent, or cross-session risk exists; micro-audit for
C2, optional for C0-C1 (`jaw-dev` §0.0). B verification is never "skippable"; intensity
scales with class (PABCD-AUTO-01). The orchestrator does not enforce these gates — YOU do.

## §9. PABCD Depth by Work Class

| Class | Plan (P) | Audit (A) | Build (B) | Check (C) | Record (D) |
|-------|----------|-----------|-----------|-----------|------------|
| C0-C1 | None/inline | Optional | Direct fix | Smallest proof | C0: no numbered record; C1: change/reason/proof only in an existing unit (UNIT-RESIDENCE-01) |
| C2 | Compact plan | Micro-audit | Boss-led build, focused tests | Targeted gate | Summary |
| C3 | Compact or full PABCD plan depending on persistence/risk | Required when public contract, architecture, persistence, cross-agent, or cross-session risk exists; otherwise focused audit | Boss-led build (economy-eligible slices dispatchable via [dispatch](references/dispatch.md)), employees verify only when useful | Affected suite + docs consistency when docs/contracts changed | Summary + evidence; durable record only when state must persist |
| C4 | Full PABCD plan (mandatory) | Required, independent | Boss-led build, employee verifies | Full relevant gates | Durable risk/approval/evidence record |
| C5 | Interview/research first | — | — | — | Reclassify, then follow the new class |

Render-artifact work-phases add C-RENDER-GROUNDING-01 (§3 C) to the Check column at C2+; C4 escalates its evidence to STRICT (persisted screenshot).

## §10. Optimization-Loop Meta-Rules (plateau discipline)

These rules apply to score/objective-maximization loops and repeated PABCD passes where
candidates are being discarded by evidence gates. Gate validity itself is owned by
`jaw-dev-testing` §9.5 Limited-Oracle / Score-Objective Evaluation.

- **DEFAULT (LOOP-PHASE-DEATH-01):** Track each discarded candidate's killing PABCD-phase
  and change class (parameter-tweak, branch-toggle, state-space redesign, evaluator
  change). After N consecutive same-phase, same-class deaths (start N=3 — HEURISTIC,
  tune per domain), the next work-phase MUST target the killing mechanism itself —
  usually the evaluation gate — not another candidate of that class.
- **STRICT (LOOP-CONTINUITY-01):** P must begin by quoting the previous cycle's D
  conclusions and next-direction. A new candidate that contradicts the recorded
  next-direction requires an explicit stated reason.
- **DEFAULT (LOOP-CANDIDATE-ANCHOR-01):** For score/objective-maximization work, source
  divergence candidates from domain-state evidence such as logs, trajectories, and
  opponent/instance analysis, not only from existing code parameters. All-lever-tweak
  candidate sets are parameter-space anchoring: regenerate from the state space.
- **HEURISTIC (LOOP-INSTANCE-CHECK-01):** Check whether evaluation instances are fixed and
  enumerable: fixed opponents, fixed test maps, fixed graders. If yes, per-instance
  specialization (fingerprint + playbook) is a legitimate widening move; consider it
  before generic-strategy tweaks.
- **DEFAULT (LOOP-MECHANISM-PROOF-01):** A candidate whose value is a new branch or
  mechanism must carry activation evidence from the instances it targets: a counter,
  debug line, or trace showing the branch actually fired WITH its intended effect
  before adoption. Aggregate score movement is not activation proof; in a multi-feature
  combo a dead mechanism hides behind other features' gains, so each branch needs its
  own trace. Loud special cases: a zero-delta ablation means presume it never ran and
  instrument before combining or discarding; byte-identical outcomes signal a dead
  path, while a branch that runs and loses should still move some trace detail.
- **DEFAULT (LOOP-RESIDUAL-TRACE-01):** A residual failure carried through D needs a
  mechanism-level explanation: which branches fired, which did not, and why the
  outcome followed; otherwise label it `unexplained`. A plausible opponent/environment
  story is not evidence unless the trace confirms our own mechanism armed and acted.
- **HEURISTIC (LOOP-PEER-CONTRAST-01):** When a peer's bot, reference solution, or
  competitor run achieves the objective on a fixed instance we fail, the next
  generation's first analysis deliverable is the behavioral diff of the two traces
  before any new candidate — the cheapest capability-gap detector.
- **HEURISTIC (LOOP-FANOUT-TIMING-01):** Spend parallel fan-out late, not early.
  While coarse levers still move the metric, stay single-track (N=1); once coarse
  levers stabilize or plateau and the search shifts to fine-grained candidates,
  parallel candidate lanes and specialist re-derivation start paying for their
  cost. Fan-out also buys outcome consistency (cross-run variance reduction), not
  only peak score. (Adopted 2026-07-07 from Sakana Fugu, arXiv:2606.21228:
  orchestration gains on a 123-experiment autonomous training loop concentrated
  after mid-run, once coarse configuration search gave way to fine
  optimizer/schedule tuning.)

Grounding: a 14-discard plateau where a prefix-only replay gate and a hard invariant
locked a 3.5/8 score. Single-incident induction: treat constants as starting values
and revise when a second domain contradicts them.

## §11. Loop-Engineering Alignment

PABCD is the macro loop; loop engineering supplies the inner-loop rules for prompts,
verifiers, repair, exploration, and resource bounds inside each phase.

### §11.1 Loop values (DEFAULT)

- **Feedback must change the next action.** A result that does not alter the next step
  is a retry, not a loop; read the failure delta first.
- **The verifier outranks the prompt.** Prefer deterministic evidence (tests, exit
  codes, diffs, telemetry) over model self-assessment; use `jaw dispatch` employees
  as independent verifiers when the class/risk warrants it.
- **Memory lives on disk**, not only in the transcript: worklog `## Plan`, approved plan records,
  attestations, goal checkpoints, death logs — the next iteration resumes from artifacts.
- **Budget exhaustion is not done.** Never report a budget stop as success.
- **Context pressure is not budget exhaustion.** Compaction is survivable BY DESIGN
  because memory lives on disk: an approaching context limit means checkpoint durable
  state (worklog, approved plan, goal checkpoints) and continue after the flush — never grounds to
  close the goal, shrink the plan, or report `DONE`/`BUDGET_EXHAUSTED`.
  `BUDGET_EXHAUSTED` requires a bound the plan actually stated (tokens, cost,
  wall-clock).
- **Interview does not solve intent transfer.** It yields an initial loop-spec; later
  evidence may require HITL clarification. Under an active goal, replan at P or report a real blocker.

### §11.2 Terminal-state vocabulary (DEFAULT)

D is the success exit, not the only exit. D summaries must name the actual report state:
`DONE` (verified success), `NOOP` (nothing needed), `BLOCKED` (external dependency),
`UNSAFE` (human risk decision), `NEEDS_HUMAN` (user-only judgment), or
`BUDGET_EXHAUSTED` (adopt best-so-far and say so). Report states, not extra FSM
states: cli-jaw still closes via D or `reset`.

### §11.3 Repair-loop discipline (C→B returns)

The B/C inner loop is: implement → run verifier → read the failure delta → repair only
the failing delta → re-verify.
**DEFAULT (LOOP-REPAIR-01):** 2 consecutive failed repairs of the same failure → stop
patching, enter root-cause mode (`jaw-dev-debugging`); 3 → replan at P, or return to Interview in HITL when intent needs clarification. **HEURISTIC (LOOP-DOOM-01):** three attestation failures in one phase mean no progress. HITL may return to I; with an active jaw goal, replan at P from the evidence or report a truthful blocker. See [loop continuation](references/loop-continuation.md).

### §11.4 Loop archetype by problem type (DEFAULT, LOOP-ARCHETYPE-01)

The explore-and-select shape this rule selects for is also tracked as
`LOOP-EXPLORE-SELECT-01`: an open-ended optimization archetype sources candidates from
capability-gap hypotheses, compares them on common instances, and retains best-so-far
rather than converging on the first workable answer. Same rule, two ids -- the id exists
so upstream references resolve; the content is here, not duplicated elsewhere.

Classify the work-phase's problem type before choosing the inner loop shape:
**Spec-satisfaction** (verifier defines done — tests, contracts, `npx tsc --noEmit`):
use the §11.3 repair loop; it can converge. **Open-ended optimization** (verifier
defines only better — scores, win rates, adversarial opponents): repair loops plateau;
use an explore-and-select loop — generate diverse candidates, evaluate on the same
instances, keep best-so-far, regenerate from the winner, stop on plateau (§10
LOOP-PHASE-DEATH-01) or budget, terminal state `BUDGET_EXHAUSTED` with best adopted,
not `DONE`. A repair loop on an optimization problem is a category error; fix the loop
shape, not the cycle count.

### §11.4a Analysis-before-regeneration (DEFAULT, LOOP-REANALYZE-01)

Repair fixes actions; analysis revises the model that generates them. In an
explore-and-select loop, every generation MUST begin with an analysis deliverable:
(1) an **updated problem/opponent model** from evidence (telemetry, replays, failure
deltas) and (2) **capability-gap hypotheses** — what the artifact cannot yet sense or
do; a gap hypothesis may expand the allowed patch surface, which is a P-level
amendment. Candidates are sourced from these hypotheses (§10 LOOP-CANDIDATE-ANCHOR-01)
and the next P quotes them (§10 LOOP-CONTINUITY-01). Regenerating straight from scores
is a repair loop wearing an explore-and-select label.

### §11.4b Mechanism activation proof (DEFAULT, LOOP-MECHANISM-PROOF-01)

Scores select candidates; only traces verify mechanisms. Owner: §10
LOOP-MECHANISM-PROOF-01 (activation evidence with intended effect, combo masking,
zero-delta/byte-identical semantics). Grounding (NEXT NATION 2026-07): a structurally
unreachable branch shipped inside a passing combo, recorded as "weak" instead of
instrumented; one trace line at adoption time would have caught it a work-phase earlier.

### §11.5 Unattended-loop resource policy (DEFAULT)

Goal-mode loop-specs must state tool/credential scope, token/cost budget, and wall-clock
bound; record resource decisions in the plan and `jaw goal update` checkpoints. For
C4 surfaces an unattended loop with unstated scope is an ESCALATE-class omission: stop
and ask before running it.

### §11.6 Continuation doctrine (DEFAULT, LOOP-CONTINUE-01)

The loop keeps the turn alive; the agent decides what "remaining work" means. On loop
re-entry or after a D close: do not redefine the objective downward (P/goal
criteria are the bar); audit completion against current repo state, not memory; read
durable state first (worklog/approved plan/goal checkpoints) to recover remaining
work-phases/criteria; and IDLE is not the end while work remains — under an active
goal, start the next work-phase at P. Work-phases chain HETEROGENEOUS units in one
session (LOOP-UNIT-CHAIN-01): an independent feature discovered mid-loop is appended
to the plan and started at P, not deferred to a new session or used to justify
closing the goal.

### §11.7 Divergence/collapse (DEFAULT)

PABCD is convergence-first by default. For ordinary build or bug-fix goals, keep one
strategy. Divergence is a mode for the open-ended-optimization archetype (§11.4), not
a standing habit. **Entry:** deliberate in HITL (during I/P when intent is open, the
approach is genuinely uncertain, the objective is maximize/deceptive, or the user asks
to compare); in goal mode, prompted on plateau detection (non-improving metrics).

**When divergence is ON:** record at least two candidates with search provenance; collapse early at P for
spec-satisfaction work (pass/fail, locally checkable); collapse late at D for
maximize-metric work where the local metric can deceive (build candidates in
isolation, evaluate on the same instances, keep/discard by recorded metric); after
the plateau breaks or a candidate is kept/discarded, turn divergence off (N=1 loop).
Divergence never bypasses human confirmation in HITL; in goal mode the hook only
keeps the turn alive and tells the agent to re-plan — never asking or moving phases.

### §11.8 Divergence cost tiers (DEFAULT, DIVERGE-TIER-01)

Divergence (§11.7) defaults to CONCEPTUAL candidates, not implemented ones. Choose the
cheapest tier that can kill the wrong option:

- **Tier 0 — inline brainstorm.** The Boss session itself lists options with
  trade-offs inside the plan/interview. No dispatch. Default for ordinary uncertainty.
- **Tier 1 — conceptual candidate docs (the divergence default).** 2-3 parallel
  `jaw dispatch` employee lanes each produce ONE one-page candidate direction
  doc (no code, no worktrees) with mandatory front-matter: `assumptions`, `risks`,
  `kill-criteria`, `evidence-needed`. Lane research stays read-only; the doc write
  is scoped to the approved plan archive. The BOSS session (collapse owner)
  performs critique/triage directly — it holds the most context; a separate
  cross-critique round is waste. Collapse gate: N candidate docs with filled
  front-matter AND per-candidate provenance — search provenance per §11.7 for
  externally-sourced candidates; for candidates grounded in the local codebase a
  repo-evidence path is acceptable, an EXPLICIT §11.8 AMENDMENT to §11.7's
  search-only wording. The mandatory front-matter keeps the gate otherwise
  stricter than §11.7. Cross-critique rounds are NOT a gate condition.
- **Tier 2 — implementation spike (rare escalation).** Parallel worktree
  implementations judged by the same verifier, ONLY when both hold: (a) the choice is
  load-bearing and Tier-1 candidates genuinely conflict on it, and (b) judging
  requires running code (performance assumptions, live API contracts, deceptive local
  metrics). Expected frequency: 0-1 per unit. Tier-2 entry is a recorded P-level
  decision in the approved plan.

Budget rationale: employee tokens may be near-free, but wall-clock and the Boss's
triage attention are not. Tier inflation (defaulting to Tier 2 because employees are
cheap) is a discipline violation; so is tier deflation that lets a load-bearing
conflict collapse from paper arguments alone.

Unknowns lane: the first Tier-1 dispatch of a research-heavy or unfamiliar-surface
unit SHOULD be a blindspot/unknowns pass (known unknowns, unknown knowns recoverable
from references, unknown unknowns from codebase/web search), so candidates are sourced
from evidence, not parameter tweaks (§10 LOOP-CANDIDATE-ANCHOR-01).

Topology: candidates and critiques never flow employee-to-employee; exchange is
file-mediated through the approved plan archive, and the Boss schedules rounds and
owns the collapse (star-shaped exchange). Employees MAY use their own CLI sub-agents
internally only with an explicit descendant grant; that internal parallelism does not change
the star-shaped candidate exchange or move collapse ownership.

### §11.9 Crux-matched collapse (DEFAULT, COLLAPSE-AGGREGATOR-01)

Collapse and synthesis ownership follows the disputed crux. When parallel candidates
disagree, the synthesis verdict comes from whoever is strongest on the domain of the
disagreement — the Boss dispatches a crux-matched aggregator lane when it is not
itself strongest there (the lane returns a verdict; the Boss still owns the collapse
decision per §11.8 topology). A fixed aggregator caps the exercise at that
aggregator's own ceiling for the domain. The collapse record names each candidate's
partial correctness, each candidate's failure mode, and why the winner's evidence
resolves the crux. (Adopted 2026-07-07 from Sakana Fugu, arXiv:2606.21228.)
