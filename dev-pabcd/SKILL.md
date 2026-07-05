---
name: dev-pabcd
description: "MUST USE for cli-jaw PABCD orchestration workflows — orchestrate, phase, attest/attestation, interview mode, goal mode, checkpoints, and multi-phase development. Triggers: orchestrate, phase, attest, attestation, interview, goal mode, checkpoint, PABCD, 요구사항 정리, 인터뷰, 스펙 정리. Operate state transitions only when the user explicitly requests orchestration or an active PABCD phase is injected — do not transition state merely because a document mentions phases, goals, or checkpoints."
metadata:
  short-description: "cli-jaw PABCD orchestration workflow for interview, phases, attest, and checkpoints."
  last-verified: "2026-07-03"
---

Structured 5-phase development. Advance only with user approval.

> **C0/C1 work (e.g. small in-place patches):** See `dev` §0.0 Work Classifier and §0.1 Patch
> Fast-Path first — full PABCD is mandatory for C4 and conditional for C3, not the baseline for every task.

## §1. Interview Trigger (MUST)

When the user asks for an interview in any form — "인터뷰하자", "인터뷰 모드", "interview",
"요구사항 정리", "스펙 정리해줘", "뭘 만들어야 하는지 정리", or any variation — you MUST
immediately run:

    cli-jaw orchestrate I

Do NOT:
- Ask clarifying questions in IDLE mode instead of entering Interview
- Use the `/interview` slash command instead of `cli-jaw orchestrate I`
- Skip Interview and go straight to P for unclear requests
- Forget to run the command — actually execute it in Bash

The `/interview` slash command is a user-facing shortcut that triggers the same transition.
As the Boss agent, always use `cli-jaw orchestrate I` directly.

**Interview MUST settle three things before P** (DEFAULT, INTERVIEW-CLASSIFY-01):
the work class (dev §0.0), the **loop archetype** (§11.4) — ask "does a verifier
define *done* for this work, or only *better*?" — and the **unit residence**
(UNIT-RESIDENCE-01, §3.1): which implementation unit (`devlog/_plan/YYMMDD_slug/`)
this work belongs to, an existing unit or a new one. This applies in HITL and goal
mode alike. An archetype discovered mid-loop — after candidates have already been
burned — is an Interview failure, not a Build failure.

## §2. How It Works

PABCD is a forward progression with Interview return.

```
IDLE ──→ P ──→ A ──→ B ──→ C ──→ D ──→ IDLE
         │      │      │      │      │
        STOP   STOP   STOP   auto   auto
        wait   wait   wait
         └──────┴──────┴──────┴──────┘
                      ↓
                 I (Interview)
              context preserved
```

You can return to Interview (I) from any phase to clarify requirements. Context (plan, audit status) is preserved.

To restart from scratch:
```
cli-jaw orchestrate reset   → returns to IDLE (context cleared)
```
Then re-enter with `cli-jaw orchestrate P`.

Transition commands:
```
cli-jaw orchestrate I       → enter Interview (from any state, context preserved)
cli-jaw orchestrate P       → enter Planning (from IDLE or I)
cli-jaw orchestrate A       → enter Plan Audit (from P only)
cli-jaw orchestrate B       → enter Build (from A only)
cli-jaw orchestrate C       → enter Check (from B only)
cli-jaw orchestrate D       → enter Done (from C only, returns to IDLE)
cli-jaw orchestrate reset   → return to IDLE (from any state)
```

### §2.1 Evidence gate (forward transitions)

The four forward transitions (P→A, A→B, B→C, C→D) require an **evidence attestation** — a
real `cli-jaw orchestrate` command with an `--attest` JSON, not narration. The server gates the
agent (identified by its boss token); a human's `/orchestrate X` keeps the free pass.
P, A, and B also require user approval before advancing; C and D proceed automatically once
their work is done. In goal mode, §4 rule 4 replaces user approval with evidence-backed
checkpoints.

```
cli-jaw orchestrate A --attest '{"from":"P","to":"A","did":"<the concrete plan you wrote: files/surfaces + devlog path>"}'
cli-jaw orchestrate B --attest '{"from":"A","to":"B","did":"<who audited the plan + the verdict>"}'
cli-jaw orchestrate C --attest '{"from":"B","to":"C","did":"<what you built + who verified it>"}'
cli-jaw orchestrate D --attest '{"from":"C","to":"D","did":"<what you checked>","checkOutput":"<paste the real tsc/test tail>","exitCode":0}'
```

The gate is **form-only**: it checks that the block is well-formed and that `did` is a real
narrative (booleans/placeholders are rejected); C→D additionally requires a non-empty
`checkOutput` and, if present, `exitCode:0`. It does NOT cross-check the narrative against
runtime state — the goal is to force a deliberate, specific claim, not to defeat a malicious
agent.

**Evidence pointers (DEFAULT, ATTEST-EVIDENCE-01):** even though the gate checks form
only, write `did` with artifact pointers: plan/devlog path, changed-file list, verifier
command, exit code, and relevant `cli-jaw goal update` checkpoint when goal mode is
active. That lets a later reader or stronger future gate re-check the claim against
the repo. Saying "현재는 B입니다" without running the command does nothing: the state machine only
moves on the command.

Threat model = laziness, not malice. Accepted residuals (NOT bugs): a fabricated `did`, the
hidden `--force` emergency hatch, a `pendingAttestation` emitted in a prior turn, and an agent
that deliberately strips its own boss token to pose as a human. Closing the last one would risk
the legitimate human-via-CLI free pass, so it is out of scope unless the threat model expands.

## §3. Phases

### P — Plan

If the request has unclear scope or unspecified technology, return to Interview (`cli-jaw orchestrate I`). Within Interview:
- Present 2–3 options as `<TechName> — <plain explanation>`
- Recommend one with project-specific reasoning
- Confirm once, then proceed

For broad changes or unfamiliar repositories, P phase MUST include:
- Compact tree of the current repository shape
- Detected repo conventions: docs, plans, architecture notes, source-of-truth logs, naming, tests
- Whether existing `structure/`, `devlog/`, `docs/`, `plans/`, or equivalent logs were read and will be reused
- Whether `structure/` or `devlog/` is proposed
- The SoT sync target (SOT-SYNC-01): which general source-of-truth doc
  (`structure/`, architecture/INDEX docs) this unit will patch in C — or, if the
  repo has none, the plan recommends creating one (dev-scaffolding §2.1)

Do not create new project-level source-of-truth folders during B unless approved in P or explicitly requested by the user.

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

Read project docs and dev skills first. Write the complete plan internally, then report it simply — like a developer reporting to the CEO.

Write a plan with two parts:
- **Part 1**: Easy explanation — what will be built, in non-developer terms.
- **Part 2**: Diff-level precision — exact file paths (NEW/MODIFY/DELETE), before/after diffs for MODIFY, complete content for NEW.

**Loop-spec header (DEFAULT, C2+):** open the plan with a compact loop-spec:
Loop archetype (§11.4, carried from Interview) · Trigger · Goal (user-visible outcome) ·
Non-goals · Verifier (the command/gate and what it measures, not only pass/fail) · Stop
condition · Memory artifact (worklog/devlog/checkpoint path) · Expected terminal states
(§11.2) · Escalation condition. Goal mode also states the §11.5 resource scope.

**Instrumentation before candidates:** when the archetype is open-ended optimization,
the loop-spec MUST include a divergence plan: descriptor axes, cell/archetype
assignments, candidate count, deterministic selection rule, and telemetry schema. If
the verifier only reports win/lose or score-only output, B's first work item is the
telemetry, not a candidate. A scalar-only verifier plus discarded candidates is the §10
plateau signature reproduced by design.

If anything is unclear, return to Interview (`cli-jaw orchestrate I`) — do NOT ask questions in P.

### §3.1 Implementation-Unit Documents

Full documentation routine (P concretizes the docs, A audits them as a hard gate, D
archives to `_fin/`, plus the mainstream design-doc/RFC translation table):
`dev-scaffolding/references/implementation-log.md`.

**Difflevel roadmap plan (STRICT, DIFFLEVEL-ROADMAP-01):** for any multi-phase unit
(2+ work-phases), the FIRST P — or the dedicated design-only Phase-0 pass (§5) —
must deliver the entire roadmap concretized: `00_plan.md` (objective, constraints,
dependency-ordered work-phase map) PLUS every phase's decade doc written to full
diff-level precision (exact paths, NEW/MODIFY/DELETE, before/after diffs) — each one
a copy-paste-executable PRD, not an outline. Scaffolding empty decade files to "fill
per cycle" does NOT satisfy this rule. Each later cycle's P starts from its
pre-written doc: re-verify it against the current codebase (stale check — earlier
phases may have moved lines, signatures, or files), amend the doc, then execute.
LOOP-CONTINUITY-01 (§10) applies on top.

**Lexicographic separation (STRICT, LEXICO-SPLIT-01):** every document in a unit
carries a numeric lexicographic prefix — bare semantic filenames (`PLAN.md`,
`DIFF_PLAN.md`, `PHASES.md`, `RCA.md`, an unnumbered `mvpplan/`-style folder) are an
A-phase FAIL, not a style nit. Research/spec material (00-range) and implementation
phase designs (decade ranges) are SEPARATE documents: no diffs inside a research
doc, no survey prose padding a phase doc — a document that mixes both fails the
audit.

**Unit residence (STRICT, UNIT-RESIDENCE-01):** every piece of development work
belongs to an implementation unit (`devlog/_plan/YYMMDD_slug/`). Ceremony scales
with class (§9); residence does not. C0-C1 fast-path work skips the PABCD ceremony
but MUST leave a numbered record doc in its owning unit — next free index in the
matching decade, e.g. `40_hotfix_dropdown_crash.md` — stating what changed, why the
fast path applied (class call), and the verification evidence. No owning unit →
create a minimal unit folder holding only that record. Interview settles residence
before P (§1).

Devlog plan artifacts use decade-range numbering to separate concerns:

| Range | Purpose | Examples |
|-------|---------|----------|
| 00–09 | Research, specs, MOC | `00_plan.md`, `01_api-survey.md`, `02_competitor-analysis.md` |
| 10–19 | Phase 1 | `10_phase1-auth-module.md`, `11_phase1-db-schema.md` |
| 20–29 | Phase 2 | `20_phase2-frontend.md` |
| 30–39 | Phase 3 | ... |

Rules:
- 00-range durable research is **mandatory for C4**, and for C3 only when state must persist
  across turns/agents, public contract or architecture decisions need durable audit, or the
  user/repo already uses devlog planning for that task; optional for C0-C2 and
  low-persistence C3 (a response-level plan is enough — but the work still leaves its
  numbered record in a unit, UNIT-RESIDENCE-01).
- Default: sequential within decade (`00`, `01`, `02`...).
- Overflow (>10 docs in a range): use sub-index (`00_0_name.md`, `00_1_name.md`).
- NEVER use bare filenames like `PLAN.md`, `DIFF_PLAN.md`, `PHASES.md`, `RCA.md`.

Present to the user:
1. Part 1 summary (≤5 sentences) + diagram + devlog file path
2. "Is there any business logic I must not decide alone?" and "Is this direction correct?"

⛔ Present the plan. Revise on feedback.
When user approves, advance with the canonical P→A attestation form in §2.1.

### A — Plan Audit
Spawn a worker to audit the plan (not code). The worker verifies:
- All file paths and imports in the plan actually exist
- Function signatures match real code
- No integration risks
- Existing source-of-truth docs/logs were read when present
- No new `structure/`, `devlog/`, docs, or AGENTS files are introduced without user approval
- New JS/TS files follow TypeScript preference rules unless the plan states why JS is required
- New TypeScript is strict-compatible or limitations are stated
- New devlog phase documents use the numbered lexicographic filename convention;
  bare-named or research/implementation-mixed docs are a FAIL (LEXICO-SPLIT-01).
- Multi-phase units satisfy DIFFLEVEL-ROADMAP-01: every roadmap phase has a
  diff-level decade doc (no outline-only or missing phases), and the phase map is
  dependency-ordered, not effort-bucketed (PHASE-SPLIT-01).

Output worker JSON for the audit. Review results when they come back.
- If FAIL → fix the plan → output worker JSON again to re-audit
- If PASS → report results to the user

⛔ Wait for user approval. When approved, advance with the canonical A→B attestation form in §2.1.

### B — Build
Implement the plan. You write all code by default. Workers are read-only verifiers unless dispatched with `--mutable` (see Pitfalls).

Do not create `structure/` or `devlog/` unless approved in P or explicitly requested by the user.

After implementing, output worker JSON for verification. The worker checks your code exists and integrates cleanly.
- If NEEDS_FIX → you fix the issues → re-verify (repair thresholds: §11.3)
- If DONE → report results to the user

⛔ Wait for user approval. When approved, advance with the canonical B→C attestation form in §2.1.

### C — Check
Final sanity check:
1. Verify all files saved and consistent
2. Run `npx tsc --noEmit` (if TypeScript project)
3. **SoT sync (DEFAULT, SOT-SYNC-01):** locate the repo's general source-of-truth
   docs (`structure/`, architecture/INDEX docs) — found in P, patched HERE so SoT
   and code never diverge silently; if the repo has none, recommend creating one
   (dev-scaffolding §2.1) in the D summary
4. Report completion summary

**DEFAULT (C-RENDER-GROUNDING-01):** when the work-phase produces an artifact whose
correctness only shows when run or rendered (HTML page, SVG, game, UI, chart,
animation, script with observable visual/interactive output), C MUST include a
render-grounding loop before C→D: (1) **RUN** it in its natural execution
environment — headless-browser screenshot for web, SVG→PNG render, execute scripts,
drive games/wizards until the first interactive state change; (2) **OBSERVE** the
output — actually read the screenshot/console back; a produced-but-unread screenshot
is not observation; (3) **FIX** what the observation reveals, then re-run and
re-observe. Trigger on artifact type + change ("could this look or behave wrong in a
way that only shows when it runs?"), never on task depth alone. Stop after ONE clean
observation; re-render only after a change. Well-formed (tsc/lint/parse passing) is
not correct — static gates do not satisfy this rule. Defaults (HEURISTIC — deviate
with a stated reason): 1280x720 viewport; stateful artifacts driven until the first
interactive state change. Evidence scales with class: C2-C3 record the observation
in the attestation narrative; C4 (STRICT) additionally persists the screenshot to
the devlog. The render observation is valid `checkOutput` evidence for C→D and the
`did` must reference it. Excluded: pure logic/config/prose covered by its own test
suite. (Adopted 2026-07-05 from fablize verification-grounding; devlog
`260705_pabcd_render_grounding`.)

Long external gates (CI runs, deploys) inside cli-jaw: do not block the turn —
register `cli-jaw bgtask add --cmd '[...]' --prompt "..."` and end the turn; the
server re-invokes the boss on completion and PABCD state persists across turns.
Local tsc/tests stay blocking.

When done, advance with the canonical C→D attestation form in §2.1; C→D uniquely requires a pasted check tail.

### D — Done
Summarize the entire flow:
- What was planned (P), audited (A), built (B), checked (C)
- List of files changed
- Any follow-up items

**Pessimistic close-out (DEFAULT, LOOP-PESSIMIST-01):** for loop/multi-pass work, D also
records the negative delta: what did NOT improve, which hypothesis died this cycle, and
one sentence answering "what evidence would show the current direction is wrong?" The
next P quotes this (§10 LOOP-CONTINUITY-01). Treat D→IDLE→P as a context/bias-flush
boundary: the next cycle resumes from disk artifacts (worklog, devlog, checkpoints,
death log), not from the transcript's accumulated assumptions.

State returns to IDLE automatically.

Project root configuration is persistent. D completion resets the PABCD state, but it
does not clear configured `projectDirs`; use `cli-jaw project clear` only when the
user explicitly asks to unset the project root.

## §4. Rules

1. One phase per response (the gate-and-wait turn boundary; canonical approval rule in §2.1).
   Goal-mode exception: when a goal is active this does not permit ending a turn before D
   when more PABCD-phases remain in the current cycle — keep going P→A→B→C→D, then close D
   and re-enter P for the next work-phase.
2. Sequence: P → A → B → C → D. Use `cli-jaw orchestrate reset` to restart.
3. Workers verify (read-only). You write all code directly in B.
4. Goal-mode precedence: when a jaw goal is active (dev §0.4), use §2.1 with
   evidence-backed checkpoints (`cli-jaw goal update`) instead of user approval. Phase order,
   audit conditions, and verification intensity are unchanged.

Gate quick-reference (strict vs goal mode):

| Gate | Strict PABCD | Goal mode |
|------|--------------|-----------|
| P→A, A→B, B→C | user approval + `--attest` | evidence-backed checkpoint + `--attest` |
| C→D | auto + `--attest` w/ `checkOutput`/`exitCode` | same |
| Turn boundary | one phase per response | continue P→D within the cycle |

## §5. Terminology: work-phase vs PABCD-phase

- **work-phase**: one outcome slice of a larger goal (e.g. "Phase 3: Management API"). A
  multi-phase goal has several work-phases done in sequence.
- **PABCD-phase**: one of the letters P/A/B/C/D inside a single orchestration cycle.

**Invariant: one work-phase = one full PABCD cycle.** Run P→A→B→C→D for a work-phase, close
D (state → IDLE), then run `cli-jaw orchestrate P` to start the next work-phase. Do NOT run
B for several work-phases back-to-back, and do NOT commit a work-phase out of B without
passing C and D. Depth scales per work-phase class (see "PABCD Depth by Work Class"), but
the P→D **sequence** is never skipped for a work-phase.

**Loop / multi-pass tasks**: a "loop"/"루프" request (or work too large for one cycle) runs
as MULTIPLE PABCD passes — one per work-phase. Pre-plan the full slice map and WRITE
all per-phase decade docs (10_phase1, 20_phase2, ...) to diff-level up front
(DIFFLEVEL-ROADMAP-01, §3.1) — scaffolding empty files is not pre-planning. Each
later cycle's P re-verifies its pre-written doc against the current codebase and
amends it before building. The first pass MAY be a design-only PABCD pass (Phase 0):
a code-free whole-system design/documentation cycle that produces exactly this
difflevel roadmap before the first implementation work-phase.

**Faithful execution (anti-skip)**: do the real work of each PABCD-phase — P writes the
real diff-level plan, A really dispatches the audit, B really implements AND verifies, C
really runs tsc/tests/scrutiny, D really summarizes with evidence. Advancing the state is
NOT the same as doing the phase; never rubber-stamp a phase to move on.

## §6. Repository Root Contract

Before writing a PABCD plan or dispatching an employee, determine the actual
working repository root with `pwd -P` from the target repo.

If `Project root` is injected at the top of the system prompt, use that value directly.
If it is NOT set, recommend the user configure it:
- Manager UI → Project settings
- CLI: `cli-jaw project add /path/to/repo`

Setting project root prevents confusion between JAW_HOME (`~/.cli-jaw-*`) and the actual codebase.

Every A/B phase `cli-jaw dispatch` task body MUST begin with:

```text
Project root: /absolute/path/to/current/repo
```

Rules:
- `Project root` must be the current working repository, not `JAW_HOME`.
- Never let workers infer the repo root from `~/.cli-jaw*`, `process.cwd()`, or an employee temp directory.
- Resolve all relative repo paths (`src/...`, `tests/...`, `structure/...`, `skills_ref/...`) against `Project root`.
- If `Project root` is unknown, STOP and ask before dispatching.

## §7. Shared Plan (auto-injected)

When P completes, the plan is saved to the **worklog `## Plan` section** (single source of truth) and kept in `ctx.plan`. No project-root file is created.

- In A and B, the orchestrator **auto-injects the full plan body** at the top of every `cli-jaw dispatch` task under `## Approved Plan`.
- Workers never read a plan file. Your task body should contain only the actual audit/verify instruction — the plan is prepended for you.
- Example: write the brief file (`Project root: /absolute/path/to/current/repo` + the
  audit instruction) with your file tool, then
  `cli-jaw dispatch --agent "Backend" --task-file /tmp/audit-brief.md --async` — no
  "read the plan" line needed; the runId returns immediately and the result re-enters
  as employee-results context. Omit `--async` only for a quick (<2 min) blocking verify.
  Parallel fan-out: `--batch --agents-file <path> --async`; role overlays: `--task-tags "testing,security"`.

## §8. Pitfalls

### Delegation Trap
- B phase: **Boss writes all code by default**. Workers are READ-ONLY verifiers.
- 💡 To let a worker write, use `--mutable` (optionally `--scope`): `cli-jaw dispatch --agent "Name" --mutable --task "..."`.
- ⛔ Without `--mutable`: `"implement the feature"`, `"write the code"`, `"create the file"` are forbidden.
- ✅ Always allowed: `"verify src/x.ts compiles"`, `"check integration of Y"`, `"report DONE or NEEDS_FIX"`.

### Context Drift
- If a worker says *"I'll proceed based on my assumption of the plan"* → STOP. Verify the dispatch went through `/api/orchestrate/dispatch` (only that path auto-injects the plan).
- Never let workers reconstruct the plan from a short task description.

### Phase Skip
- A (audit) is **mandatory for C4**, and for C3 when public contract, architecture,
  persistence, cross-agent, or cross-session risk exists; use a micro-audit for C2 and
  optional audit for C0-C1 (see `dev` §0.0 for classes).
- B verification is never "skippable". Untested code is not "done" — but verification
  intensity scales with the work class (PABCD-AUTO-01).
- The orchestrator does not enforce these gates today — YOU do.

## §9. PABCD Depth by Work Class

| Class | Plan (P) | Audit (A) | Build (B) | Check (C) | Record (D) |
|-------|----------|-----------|-----------|-----------|------------|
| C0-C1 | None/inline | Optional | Direct fix | Smallest proof | One-line summary as a numbered record doc in the owning unit (UNIT-RESIDENCE-01) |
| C2 | Compact plan | Micro-audit | Boss writes, focused tests | Targeted gate | Summary |
| C3 | Compact or full PABCD plan depending on persistence/risk | Required when public contract, architecture, persistence, cross-agent, or cross-session risk exists; otherwise focused audit | Boss writes, employees verify only when useful | Affected suite + docs consistency when docs/contracts changed | Summary + evidence; durable record only when state must persist |
| C4 | Full PABCD plan (mandatory) | Required, independent | Boss writes, employee verifies | Full relevant gates | Durable risk/approval/evidence record |
| C5 | Interview/research first | — | — | — | Reclassify, then follow the new class |

Render-artifact work-phases add C-RENDER-GROUNDING-01 (§3 C) to the Check column at C2+; C4 escalates its evidence to STRICT (persisted screenshot).

## §10. Optimization-Loop Meta-Rules (plateau discipline)

These rules apply to score/objective-maximization loops and repeated PABCD passes where
candidates are being discarded by evidence gates. Gate validity itself is owned by
`dev-testing` §9.5 Limited-Oracle / Score-Objective Evaluation.

- **DEFAULT (LOOP-PHASE-DEATH-01):** Track each discarded candidate's killing PABCD-phase
  (P/A/B/C/D) and change class: parameter-tweak, branch-toggle, state-space redesign, or
  evaluator change. After N consecutive same-phase, same-class deaths (starting value
  N=3 — HEURISTIC, tune per domain), the next work-phase MUST target the killing
  mechanism itself, usually the evaluation gate, not another candidate of that class.
  Repeated D-evidence collapses mean the gate, not the candidates, is probably the
  bottleneck.
- **STRICT (LOOP-CONTINUITY-01):** P must begin by quoting the previous cycle's D
  conclusions and next-direction. A new candidate that contradicts the recorded
  next-direction requires an explicit stated reason.
- **DEFAULT (LOOP-CANDIDATE-ANCHOR-01):** For score/objective-maximization work, source
  divergence candidates from domain-state evidence such as logs, trajectories, and
  opponent/instance analysis, not only from existing code parameters. If every candidate
  is a threshold, guard, or suppression tweak on existing levers, treat that as
  parameter-space anchoring and regenerate from the state space.
- **HEURISTIC (LOOP-INSTANCE-CHECK-01):** Check whether evaluation instances are fixed and
  enumerable: fixed opponents, fixed test maps, fixed graders. If yes, per-instance
  specialization such as fingerprint plus playbook is a legitimate, evaluable widening
  move; consider it before generic-strategy tweaks.

Grounding: observed in a 14-discard optimization plateau where a prefix-only replay gate
and a hard draw-protection invariant locked a 3.5/8 score. Single-incident induction —
treat the constants as starting values, keep the per-domain death log, and revise these
rules when a second domain's evidence contradicts them.

## §11. Loop-Engineering Alignment

PABCD is the macro loop: phase-level control with gates. Loop engineering supplies the
inner-loop rules for prompts, verifiers, repair, exploration, and resource bounds inside
each PABCD phase.

### §11.1 Loop values (DEFAULT)

- **Feedback must change the next action.** A result that does not alter the next step is
  a retry, not a loop. Read the failure delta before acting again.
- **The verifier outranks the prompt.** Prefer deterministic evidence (tests, exit
  codes, diffs, telemetry) over model self-assessment; use `cli-jaw dispatch` employees
  as independent verifiers when the class/risk warrants it.
- **Memory lives on disk**, not only in the transcript: worklog `## Plan`, devlog,
  attestations, goal checkpoints, and death logs. The next iteration must resume from
  artifacts alone.
- **Budget exhaustion is not done.** Never report a budget stop as success.
- **Interview does not solve intent transfer.** It produces an initial loop-spec; later
  evidence may force `cli-jaw orchestrate I` because intent is refined cyclically.

### §11.2 Terminal-state vocabulary (DEFAULT)

D is the success exit, not the only exit. D summaries must name the actual report state:
`DONE` (verified success), `NOOP` (nothing needed), `BLOCKED` (external dependency),
`UNSAFE` (needs a human risk decision), `NEEDS_HUMAN` (judgment only the user can make),
or `BUDGET_EXHAUSTED` (resources ran out; adopt best-so-far and say so). These are
report states, not extra FSM states: cli-jaw still closes via D or `cli-jaw orchestrate
reset`, and the D summary states the real terminal state.

### §11.3 Repair-loop discipline (C→B returns)

The B/C inner loop is: implement → run verifier → read the failure delta → repair only
the failing delta → re-verify.

- **DEFAULT (LOOP-REPAIR-01):** 2 consecutive failed repairs of the same failure means
  stop patching and enter root-cause mode (`dev-debugging`). 3 means replan
  (`cli-jaw orchestrate P`) or return to Interview (`cli-jaw orchestrate I`).
- **HEURISTIC (LOOP-DOOM-01):** 3 attestation failures in the same phase within one
  work-phase means no progress; force an Interview return. The server may not enforce
  this, so the Boss agent self-applies it.

### §11.4 Loop archetype by problem type (DEFAULT, LOOP-ARCHETYPE-01)

Classify the work-phase's problem type before choosing the inner loop shape:

- **Spec-satisfaction**: the verifier defines done (tests, contracts, `npx tsc
  --noEmit`). Use the §11.3 repair loop; it can converge.
- **Open-ended optimization**: the verifier defines only better (scores, win rates,
  adversarial opponents). Repair loops plateau here. Use an explore-and-select loop:
  generate diverse candidates in parallel, evaluate them on the same instances, keep
  best-so-far, regenerate from the winner, and stop on plateau (§10
  LOOP-PHASE-DEATH-01) or budget. The terminal state is `BUDGET_EXHAUSTED` with the
  best candidate adopted, not `DONE`.

A repair loop applied to an optimization problem is a category error; the fix is loop
shape, not more cycles.

### §11.4a Analysis-before-regeneration (DEFAULT, LOOP-REANALYZE-01)

Repair fixes actions; analysis revises the model that generates them. In an
explore-and-select loop, every generation MUST begin with an analysis deliverable:

1. **Updated problem/opponent model** from evidence (telemetry, replays, failure deltas):
   what did the opponent/environment actually do, and what does it imply?
2. **Capability-gap hypotheses**: what can the artifact not currently sense or do? A gap
   hypothesis may expand the allowed patch surface; that is a P-level amendment, which
   is why new capabilities do not emerge from a surface-bounded repair loop.

Candidates are sourced from these hypotheses (§10 LOOP-CANDIDATE-ANCHOR-01), and the
next P quotes them (§10 LOOP-CONTINUITY-01). Regenerating straight from scores is a
repair loop wearing an explore-and-select label.

### §11.5 Unattended-loop resource policy (DEFAULT)

Goal-mode loop-specs must state tool/credential scope, token/cost budget, and wall-clock
bound. Record resource decisions in the plan and evidence-backed `cli-jaw goal update`
checkpoints. For C4 surfaces, an unattended loop with unstated scope is an
ESCALATE-class omission: stop and ask before running it.
