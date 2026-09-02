---
name: jaw-dev-pabcd
description: "MUST USE for cli-jaw PABCD orchestration workflows — orchestrate, phase, attest/attestation, interview mode, goal mode, checkpoints, and multi-phase development. Triggers: orchestrate, phase, attest, attestation, interview, goal mode, checkpoint, PABCD, 요구사항 정리, 인터뷰, 스펙 정리. Operate state transitions only when the user explicitly requests orchestration or an active PABCD phase is injected — do not transition state merely because a document mentions phases, goals, or checkpoints."
metadata:
  short-description: "cli-jaw PABCD orchestration workflow for interview, phases, attest, and checkpoints."
  last-verified: "2026-07-03"
---

Structured 5-phase development. Advance only with user approval.
> **C0/C1 work:** see `dev` §0.0 Work Classifier and §0.1 Patch Fast-Path first — full
> PABCD is mandatory for C4 and conditional for C3, not the baseline for every task.

> **`dev` is canonical:** `dev` §0.2 Rule Classes, §3 Verification Gate, and §5 Safety Rules apply to all work governed by this skill.

## §1. Interview Trigger (MUST)

When the user asks for an interview in any form — "인터뷰하자", "인터뷰 모드", "interview",
"요구사항 정리", "스펙 정리해줘", "뭘 만들어야 하는지 정리", or any variation — you MUST
immediately run:

    cli-jaw orchestrate I

Do NOT ask clarifying questions in IDLE instead of entering Interview, skip Interview
for unclear requests, or merely narrate — actually execute the command in Bash.
`/interview` is the user-facing shortcut; the Boss agent always runs the command directly.

**Interview MUST settle three things before P** (DEFAULT, INTERVIEW-CLASSIFY-01):
the work class (dev §0.0), the **loop archetype** (§11.4) — ask "does a verifier
define *done* for this work, or only *better*?" — and the **unit residence**
(UNIT-RESIDENCE-01, §3.1). Applies in HITL and goal mode alike; an archetype
discovered mid-loop, after candidates were burned, is an Interview failure.

## §2. How It Works

```
IDLE ──→ P ──→ A ──→ B ──→ C ──→ D ──→ IDLE
         │      │      │      │      │
        STOP   STOP   STOP   auto   auto
        wait   wait   wait
         └──────┴──── I (Interview) — reachable from any phase, context preserved

Transitions (each phase accepts only its predecessor):
cli-jaw orchestrate I|P|A|B|C|D   → I from any state (context preserved); P from IDLE/I;
                                    A←P, B←A, C←B, D←C (D returns to IDLE)
cli-jaw orchestrate reset         → IDLE from any state (context cleared); re-enter with P
```

### §2.1 Evidence gate (forward transitions)

The four forward transitions (P→A, A→B, B→C, C→D) require an **evidence attestation** — a
real `cli-jaw orchestrate` command with an `--attest` JSON, not narration. The server gates the
agent (identified by its boss token); a human's `/orchestrate X` keeps the free pass.
P, A, and B also require user approval; C and D proceed automatically once their work
is done. In goal mode, §4 rule 4 replaces user approval with evidence-backed checkpoints.

```
cli-jaw orchestrate A --attest '{"from":"P","to":"A","did":"<the concrete plan you wrote: files/surfaces + devlog path>"}'
cli-jaw orchestrate B --attest '{"from":"A","to":"B","did":"<who audited the plan + the verdict>"}'
cli-jaw orchestrate C --attest '{"from":"B","to":"C","did":"<what you built + who verified it>"}'
cli-jaw orchestrate D --attest '{"from":"C","to":"D","did":"<what you checked>","checkOutput":"<paste the real tsc/test tail>","exitCode":0}'
```

The gate is **form-only**: well-formed block, real `did` narrative (booleans/placeholders
rejected); C→D additionally requires non-empty `checkOutput` and, if present, `exitCode:0`.
It does NOT cross-check the narrative against runtime state — it forces a deliberate,
specific claim, not malice-proofing.

**Evidence pointers (DEFAULT, ATTEST-EVIDENCE-01):** even though the gate checks form
only, write `did` with artifact pointers: plan/devlog path, changed-file list, verifier
command, exit code, and relevant `cli-jaw goal update` checkpoint when goal mode is
active, so a later reader can re-check the claim. Narration without running the
command does nothing: the state moves only on the command.

Threat model = laziness, not malice. Accepted residuals (NOT bugs): fabricated `did`,
the hidden `--force` hatch, a prior-turn `pendingAttestation`, and boss-token stripping
(closing it would break the legitimate human-via-CLI free pass).

### 2.2 Orchestration invariants

Four rules govern what a transition means. The gate above enforces none of them —
they are what makes the recorded cycle worth reading.

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

Work performed outside the state machine does not count as progress: re-enter and
attest it before building on it. Per the Runtime adapter note at the top of this file,
"persisted" scales with the host — a runtime with an FSM persists the transition
itself; a runtime without one persists it as the announced transition plus the
attestation JSON appended to the worklog. What is never acceptable is a transition
that exists only in the reply text.

**ORCH-ARTIFACT-01 (DEFAULT) — advancing a phase is not doing it.** Each forward edge
must carry its real artifact, not just an attestation string:

| Edge | Required artifact |
|---|---|
| P→A | the actual diff-level plan document |
| A→B | an audit verdict that names its blockers |
| B→C | the implementation delta |
| C→D | fresh typecheck/test/gate output — non-empty `checkOutput`, `exitCode: 0` |
| D | a cycle summary with evidence and the next-phase decision |

A phase whose artifact is absent is not done, regardless of adjacency. The gate is
form-only and cannot tell a real artifact from a plausible sentence; this rule is the
discipline the gate cannot enforce.

**ATTEST-SHAPE-01 (STRICT) — name the edge.** Every attestation carries `from` and
`to` naming the edge it advances, on every edge including ungated entry edges, and it
matters before `did` does: an attestation that does not say which transition it
belongs to is not an attestation, it is a sentence. A later reader reconstructing the
cycle from the log has only those two keys to order it by.

P→A additionally names its plan unit — a real `devlog/_plan/YYMMDD_slug/` holding
numbered docs (UNIT-RESIDENCE-01) — **inside `did`**, not as a separate key.

That placement is not a style choice. cli-jaw's attest parser accepts exactly
`from`, `to`, `did`, `checkOutput`, and `exitCode`; every other key is **silently
dropped**, with no error and no warning. A `planUnit`, `workPhaseId`, `auditOutput`,
`auditVerdict`, or `testReceiptPath` field written into the JSON simply vanishes, so a
rule demanding them would document a gate that does not exist. Carry them in the `did`
narrative, where they survive and stay readable, and treat the shape as what makes the
log re-readable rather than what makes the gate pass.

**SESSION-IDENTITY-01 (STRICT) — do not attest for a state you do not own.** cli-jaw
keeps one FSM per server rather than one per session, and `jaw orchestrate` takes no
`--session` flag, so there is no id to get wrong here. What remains is the failure the
rule exists to prevent: advancing a phase that another conversation is mid-cycle on.
Read the current phase before claiming one, and when several conversations share the
server, confirm the in-flight cycle is yours before advancing it.

Two cycles writing one record is not a mistake that reports itself: the other
conversation's phase moves without it acting, and neither side can tell from inside.
That is why this is STRICT rather than hygiene.

## §3. Phases

### P — Plan

If the request has unclear scope or unspecified technology, return to Interview
(`cli-jaw orchestrate I`): present 2–3 options as `<TechName> — <plain explanation>`,
recommend one with project-specific reasoning, confirm once, then proceed.

For broad changes or unfamiliar repositories, P phase MUST include:
- Compact tree of the current repository shape
- Detected repo conventions (docs, plans, architecture notes, naming, tests)
- Whether existing SoT logs (`structure/`, `devlog/`, `docs/`, `plans/`) were read and
  will be reused, and whether new ones are proposed
- The SoT sync target (SOT-SYNC-01): which general source-of-truth doc
  this unit will patch in C — or, if the repo has none, the plan recommends creating
  one (dev-scaffolding §2.1)

Do not create new project-level source-of-truth folders during B unless approved in P
or explicitly requested.

Design phases before mapping them to PABCD. **Slice and order phases by
dependency/architecture structure (STRICT, PHASE-SPLIT-01)** — the orthodox
unlimited-time build order: foundations (schema, contracts, core data flow) → core
capabilities → integration → hardening/polish — so each phase consumes the verified
output of the previous one. DB/API/UI/test work inside a phase are subtasks, and every
phase closes with something independently verifiable (build, tests, or a demonstrable
surface). Effort-based bucketing is FORBIDDEN (no "quick win vs heavy" buckets,
impact/effort matrices, or time-boxed slices): phase boundaries encode build order,
not the schedule. Larger work splits into multiple PABCD passes (§5).

Read project docs and dev skills first. Write the complete plan internally, then report it simply — like a developer reporting to the CEO.

Write a plan with two parts: **Part 1** — easy explanation of what will be built, in
non-developer terms; **Part 2** — diff-level precision: exact file paths
(NEW/MODIFY/DELETE), before/after diffs for MODIFY, complete content for NEW.

For every planned conditional path, the accept criteria name its activation scenario
(C-ACTIVATION-GROUNDING-01 — owner: C phase below).

**Loop-spec header (DEFAULT, C2+):** open the plan with a compact loop-spec:
Loop archetype (§11.4, carried from Interview) · Trigger · Goal (user-visible outcome) ·
Non-goals · Verifier (the command/gate and what it measures, not only pass/fail) · Stop
condition · Memory artifact (worklog/devlog/checkpoint path) · Expected terminal states
(§11.2) · Escalation condition. Goal mode also states the §11.5 resource scope.

**Instrumentation before candidates:** when the archetype is open-ended optimization,
the loop-spec MUST include a divergence plan: descriptor axes, cell/archetype
assignments, candidate count, deterministic selection rule, and telemetry schema. With
a score-only verifier, B's first work item is the telemetry, not a candidate — a
scalar-only verifier plus discarded candidates is the §10 plateau signature by design.

If anything is unclear, return to Interview (`cli-jaw orchestrate I`) — do NOT ask questions in P.

### §3.1 Implementation-Unit Documents

Full documentation routine (P concretizes the docs, A audits them as a hard gate, D
archives to `_fin/`, plus the mainstream design-doc/RFC translation table):
`dev-scaffolding/references/implementation-log.md`.

**Difflevel roadmap plan (STRICT, DIFFLEVEL-ROADMAP-01):** for any multi-phase unit
(2+ work-phases), the FIRST P — or the dedicated design-only Phase-0 pass (§5) —
must deliver the entire roadmap concretized: `000_plan.md` (objective, constraints,
dependency-ordered work-phase map) PLUS every phase's decade doc written to full
diff-level precision — each a copy-paste-executable PRD, not an outline or empty
scaffold. Each later cycle's P re-verifies its pre-written doc against the current
codebase (stale check), amends it, then executes. LOOP-CONTINUITY-01 (§10) applies.

**Lexicographic separation (STRICT, LEXICO-SPLIT-01):** every document in a unit
carries a numeric lexicographic prefix — bare semantic filenames (`PLAN.md`,
`DIFF_PLAN.md`, `PHASES.md`, `RCA.md`, unnumbered folders) are an A-phase FAIL, not a
style nit. Research/spec material (00-range) and implementation phase designs (decade
ranges) are SEPARATE documents; mixing both in one doc fails the audit.

**Unit residence (STRICT, UNIT-RESIDENCE-01):** every piece of development work
belongs to an implementation unit (`devlog/_plan/YYMMDD_slug/`). Ceremony scales
with class (§9); residence does not. C0-C1 fast-path work skips the PABCD ceremony
but MUST leave a numbered record doc in its owning unit — next free index in the
matching decade — stating what changed, why the fast path applied, and the
verification evidence; no owning unit → create a minimal unit folder for it.
Interview settles residence before P (§1).

Devlog plan artifacts use decade-range numbering to separate concerns. **Prefixes are
three digits** (`000_`, `010_`, `020_`); do not mix two-digit and three-digit prefixes.

| Range | Purpose |
|-------|---------|
| 000–009 | Research, specs, MOC (`000_plan.md`, `001_api-survey.md`) |
| 010–019, 020–029, ... | Phase 1, Phase 2, ... (`010_phase1-auth-module.md`) |

Rules:
- 000-range durable research is **mandatory for C4**, and for C3 only when state must persist
  across turns/agents, public contract or architecture decisions need durable audit, or the
  user/repo already uses devlog planning; optional for C0-C2 and low-persistence C3
  (the work still leaves its numbered record in a unit, UNIT-RESIDENCE-01).
- Sequential within decade; overflow (>10 docs) uses sub-index (`000_0_name.md`).
- NEVER use bare filenames like `PLAN.md`, `DIFF_PLAN.md`, `PHASES.md`, `RCA.md`.

Three digits rather than two because the range carries the meaning, and two digits make
the tens column do double duty: `10` reads as both "decade 1" and "tenth document". With
three, `010` is unambiguously phase 1's first doc and `001` is research's first.

This rule was previously written as two-digit while current practice is three. Measured
in `devlog/_plan/`: 492 three-digit documents against 107 two-digit ones, and the
two-digit files are concentrated in units from 2026-06 (`260610_*`, `260618_*`,
`260621_*`) while every unit from 2026-08 onward is three-digit. So the repository
migrated and the rule text did not follow.

Historical units keep their prefixes. Renaming them would break every inbound reference
for no gain, so this rule governs new units.

#### §3.2 Plan-quality rules

Three authoring rules for P. Each is also an A blocker (§3 A, "Plan-rule checks"),
so failing one at P costs an audit round.

**PLAN-VERIFIER-REAL-01 (DEFAULT).** Before writing a verifier command into the
plan, **run it.** A command that does not exist — missing script, missing config —
or that does not read the change target is not a verifier. Record one line next to
each: its exit code, and whether it actually reads this unit's change target.

Prove the "reads the target" half with one of:

- the target path appears as a direct argument;
- a script or glob definition that includes it — quote the glob;
- a config `include` / `files` entry — quote it;
- a call chain into a sub-script that reads it — cite `file:line`.

If none holds, write "this command does not observe this change" and classify that
acceptance row as **human review**. Do not claim a gate protects it. Two traps
recur: a command that silently checks nothing when its config file is absent, and
naming a gate as the verifier for prose it never reads.

**PLAN-FIELD-CHAIN-01 (DEFAULT).** A plan that adds a field to a type, or a value to
an enum, must enumerate that value's whole chain in the file-change map:

creation (input type, builder, CLI arg) → serialization → deserialization (reviver,
unknown-value handling) → every consumer

When adding an enum value, search three things rather than one: the type name, the
field name, and **every existing enum value**. Then check non-comparison
consumption — destructuring and aliases, `default` branches, generic predicates, and
every function taking that type.

Give each of the four stages a path or an explicit `N/A + reason`; a blank is
indistinguishable from "did not check". The two failure shapes differ and both are
silent: a missed **consumer** makes the new value a ghost state that nothing counts,
while a missed **creation** path means the value can never be produced at all — so
any condition depending on it never arms. That second one is
C-ACTIVATION-GROUNDING-01's failure reached through the type system instead of
through control flow.

**PLAN-BYPASS-NAMED-01 (DEFAULT).** A plan that adds enforcement must also record
**how to bypass it**, in five fields:

1. **Enforcement strength** — on whatever tier vocabulary the repository uses. With
   none, name the mechanism kind plainly: runtime gate, CI check, pre-commit hook, or
   agent-followed prose.
2. **Executing surface** — which script, job, hook, or human actually runs it.
3. **Known bypass path** — the concrete way around it.
4. **Residual risk** — what stays reachable once the layer is in place.
5. **Wording downgrade** — whether the claim had to be weakened once (3) was known.

A bypassable layer is called an **early warning**, never **enforcement**.
`final layer: none` is an allowed answer: the point is to stop claiming enforcement
that does not exist, not to manufacture an unbypassable layer. If you claim no
bypass exists, give the evidence — that claim is usually wrong.

**PLAN-TRACK-01 (DEFAULT).** Mirror the plan's work items into the worklog `## Plan`
section at P and keep their statuses current through B. That section is the
**visibility** channel between turns, and it is not the plan: the diff-level document
in the unit stays the single source of truth, and ticking an item is never a substitute
for the phase's artifact (ORCH-ARTIFACT-01).

cli-jaw has no separate plan/todo tool surface -- the worklog IS it -- so there is
nothing to mirror *into* beyond that section. Do not report having updated a tracker
this runtime does not have.

Present to the user: the Part 1 summary (≤5 sentences) + diagram + devlog file path,
plus "Is there any business logic I must not decide alone?" and "Is this direction
correct?"

⛔ Present the plan; revise on feedback. On approval, advance with the canonical P→A
attestation form in §2.1.

### A — Plan Audit
Spawn a worker to audit the plan (not code). The worker verifies:
- All file paths and imports in the plan actually exist; function signatures match
  real code; no integration risks; existing source-of-truth docs/logs were read
- No new `structure/`, `devlog/`, docs, or AGENTS files are introduced without user approval
- New JS/TS files follow TypeScript preference rules (strict-compatible, or limitations
  stated) unless the plan states why JS is required
- New devlog phase documents use the numbered lexicographic filename convention;
  bare-named or research/implementation-mixed docs are a FAIL (LEXICO-SPLIT-01).
- Multi-phase units satisfy DIFFLEVEL-ROADMAP-01: every roadmap phase has a
  diff-level decade doc (no outline-only or missing phases), and the phase map is
  dependency-ordered, not effort-bucketed (PHASE-SPLIT-01).
- Each planned conditional path: trigger reachable from states the system actually
  visits, not consumed upstream first, activation scenario named
  (C-ACTIVATION-GROUNDING-01). Unreachable-by-construction = plan blocker, not a
  C-phase discovery.

**Plan-rule checks.** The reviewer additionally verifies each of these, and any one
failing is a blocker: (a) every verifier command the plan names actually exists AND
reads the change target — the reviewer RUNS it rather than trusting the plan
(PLAN-VERIFIER-REAL-01); (b) each new field or enum value has its full
creation → serialization → deserialization → consumer chain enumerated, with
`N/A + reason` where a stage does not apply (PLAN-FIELD-CHAIN-01); (c) when several
documents reference a shared type, the field NAMES match, not just the concept;
(d) each document's header dependency declaration matches the types its body
actually uses; (e) any plan adding enforcement records the five bypass fields and
either names the final enforcement layer or states `none`
(PLAN-BYPASS-NAMED-01). All three plan rules are defined in §3.2 below.

Instruct the reviewer to end with a normalized final line —
`VERDICT: PASS | GO-WITH-FIXES (blockers=N) | FAIL` — followed by numbered
blockers. No code changes.

**Audit loop (STRICT, AUDIT-LOOP-01).** A is a **loop** — audit → synthesize →
amend plan → re-audit — not a single round. Exit A→B only when the main agent
judges the round:

- **pass** — the reviewer approved; or
- **near-pass** — every High/Critical blocker was folded into the plan as a
  concrete amendment or explicitly rebutted with recorded rationale, and only
  non-blocking residuals remain. `GO-WITH-FIXES; 2 blockers folded back` qualifies.

A **FAIL** round never exits. Apply REVIEW-SYNTHESIS-01 (§11.3), amend the plan,
and re-audit with the **same reviewer** so it keeps the context it already built
(DISPATCH-ACTOR-01, §7.2). LOOP-REPAIR-01 bounds the loop: after 3 failed rounds
return to P with a changed plan, or to Interview when human clarification is what
is actually missing.

Three details in that rule are load-bearing and easy to lose:

- **The main agent is the judge, not a string parser.** `near-pass` is a judgment
  about whether the blockers were really addressed. A reviewer's closing line is
  evidence for that judgment, not a substitute for it — and a pasted verdict whose
  final line says FAIL does not become a pass because the summary claims one.
- **Same reviewer on re-audit, fresh reviewer for the final adversarial pass.** Reuse
  preserves context across rounds; independence matters when the reviewer has
  already shaped the fix. Those pull in opposite directions, which is why the rule
  names both rather than one.
- **The loop is bounded because an unbounded audit loop is a stall, not rigor.**
  Three failed rounds means the plan is wrong in a way re-auditing cannot find.

**Verification is not pinned to A (LEAN-REVIEW-01, DEFAULT).** Dispatch review lanes
wherever they help — plan audit at A, implementation review at B, check
verification at C — instead of treating A as the one phase that owns review. A
review lane costs one dispatch and returns evidence you can paste into the next
attestation.

Where a runtime records reviewer verdicts, a recorded verdict is **binding**: it
cannot be contradicted by your own attestation, spent across a re-plan, or spent on
a plan whose files changed after approval. Where the runtime records nothing, the
same discipline is yours to keep.

What must not be built is a review gate whose failure mode traps the cycle. Recorded
2026-08-18 in the codexclaw lineage: A→B once required a verdict only an automatic
observer could write, so every reason that observer failed to fire — a matcher that
missed the runtime's role vocabulary, a reviewer whose closing lines did not parse,
a reinstall that moved the plugin root under a live session — left the cycle in a
phase it could never leave, and the only escape was hand-feeding the gate its own
payload. **A gate whose normal recovery is forging its own input is not a gate.**
Apply that when designing any gate here: if the recovery path is "fabricate the
evidence the gate wanted", the gate is worse than none.

Output worker JSON for the audit. On FAIL, synthesize (§11.3), amend the plan, and
re-audit with the SAME reviewer. On pass or near-pass, report results with the residual
disposition to the user.

⛔ Wait for user approval. When approved, advance with the canonical A→B attestation form in §2.1.

### B — Build
Implement the plan. You write code by default and own every verdict; a worker may
write when its slice passes DISPATCH-ECONOMY-01 (§7.1) and the dispatch is
explicitly write-capable with a bounded scope (see Pitfalls). Workers without that
grant are read-only verifiers. Do not create `structure/` or
`devlog/` unless approved in P or explicitly requested. After implementing, output
worker JSON for verification (code exists, integrates cleanly): NEEDS_FIX → fix and
re-verify (repair thresholds §11.3); DONE → report to the user.

⛔ Wait for user approval. When approved, advance with the canonical B→C attestation form in §2.1.

### C — Check
Final sanity check: (1) verify all files saved and consistent; (2) run `npx tsc
--noEmit` (TypeScript projects); (3) **SoT sync (DEFAULT, SOT-SYNC-01)** — patch the
repo's general source-of-truth docs (found in P) HERE so SoT and code never diverge
silently, or recommend creating one (dev-scaffolding §2.1) in the D summary; (4)
report the completion summary.

**DEFAULT (C-RENDER-GROUNDING-01):** when the work-phase produces an artifact whose
correctness only shows when run or rendered (HTML page, SVG, game, UI, chart,
animation, script with observable visual/interactive output), C MUST include a
render-grounding loop before C→D: (1) **RUN** it in its natural execution
environment — headless-browser screenshot for web, SVG→PNG render, execute scripts,
drive games/wizards until the first interactive state change; (2) **OBSERVE** the
output — actually read the screenshot/console back; a produced-but-unread screenshot
is not observation; (3) **FIX** what the observation reveals, then re-run and
re-observe. Trigger on artifact type + change, never task depth; stop after ONE clean
observation. Static gates (tsc/lint/parse) do not satisfy this rule. Defaults
(HEURISTIC): 1280x720 viewport. Evidence scales: C2-C3 record the observation in the
attestation narrative; C4 (STRICT) persists the screenshot to the devlog. The render
observation is valid `checkOutput` for C→D and the `did` references it. Excluded:
pure logic/config/prose covered by its own test suite. (Adopted 2026-07-05; devlog
`260705_pabcd_render_grounding`.)

**DEFAULT (C-ACTIVATION-GROUNDING-01):** the conditional-path sibling of render
grounding. When the work-phase adds/changes a code path that only runs under a
trigger absent from the happy path (error handlers, fallbacks, retries, caches,
guards, gated branches, mode switches, migration handlers, threshold behaviors),
C MUST include activation evidence before C->D: (1) **TRIGGER** the condition for
real (test, scenario, threshold fixture, fault injection); (2) **OBSERVE** the path
execute with its intended effect via an assertion, log line, counter, or trace read
back; (3) **FIX** and re-trigger if observation contradicts intent. "All tests
green" does not satisfy this when no test drives the trigger. Retroactive-check
signals: byte-identical output to baseline (presume dead, instrument first) and a D
claim of "handled/falls back" with no fired-path artifact. The activation observation
is valid `checkOutput` for C->D; the `did` references it. Excluded: unconditional
straight-line changes under existing coverage. P names the activation scenario; A
checks trigger reachability.

Long external gates (CI runs, deploys): do not block the turn — register
`cli-jaw bgtask add --cmd '[...]' --prompt "..."` and end the turn; the server
re-invokes the boss on completion and PABCD state persists. Local tsc/tests stay blocking.

When done, advance with the canonical C→D attestation form in §2.1; C→D uniquely requires a pasted check tail.

### D — Done
Summarize the entire flow: what was planned (P), audited (A), built (B), checked (C);
the list of files changed; any follow-up items.

**Pessimistic close-out (DEFAULT, LOOP-PESSIMIST-01):** for loop/multi-pass work, D also
records the negative delta: what did NOT improve, which hypothesis died this cycle, and
one sentence answering "what evidence would show the current direction is wrong?" The
next P quotes this (§10 LOOP-CONTINUITY-01). D→IDLE→P is a context/bias-flush boundary:
the next cycle resumes from disk artifacts, not the transcript's accumulated assumptions.

State returns to IDLE automatically. Project root configuration is persistent: D
resets PABCD state but not `projectDirs`; `cli-jaw project clear` only on explicit
user request.

## §4. Rules

1. One phase per response (the gate-and-wait turn boundary; canonical approval rule in §2.1).
   Goal-mode exception: with an active goal, do not end the turn before D while
   PABCD-phases remain — keep going P→D, close D, re-enter P for the next work-phase.
2. Sequence: P → A → B → C → D. Use `cli-jaw orchestrate reset` to restart.
3. Workers verify (read-only) by default; write-capable dispatch follows §7.1
   DISPATCH-ECONOMY-01. Verdicts stay with the boss in B.
4. Goal-mode precedence: when a jaw goal is active (dev §0.4), use §2.1 with
   evidence-backed checkpoints (`cli-jaw goal update`) instead of user approval; phase
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
then `cli-jaw orchestrate P` for the next work-phase. Never run B for several
work-phases back-to-back or commit out of B without passing C and D. Depth scales per
class (§9); the P→D **sequence** is never skipped.

**Loop / multi-pass tasks**: a "loop"/"루프" request (or work too large for one cycle) runs
as MULTIPLE PABCD passes — one per work-phase. Pre-plan the full slice map and WRITE
all per-phase decade docs (10_phase1, 20_phase2, ...) to diff-level up front
(DIFFLEVEL-ROADMAP-01, §3.1; re-verify/amend per cycle). The first pass MAY be a
design-only Phase-0 cycle producing exactly this difflevel roadmap.
**Docs-first multi-cycle entry (LOOP-DOCS-FIRST-01, DEFAULT).** The first pass is a
design-only PABCD pass (Phase 0) — a code-free whole-system design and documentation
cycle that produces exactly this diff-level roadmap before the first implementation
work-phase. This used to read "MAY"; it is the default for any loop of 2+ work-phases,
and mandatory when the loop runs unattended.

A loop is a chain of PABCD cycles, and a chain is only as disciplined as the documents
each cycle re-reads at P. Memory lives on disk, not in the transcript — so a loop
spanning 2+ work-phases buys its memory first.

1. **Register and document in one motion.** Arm the work-phase map (a skeleton is
   fine) AND run the first work-phase as a docs-only cycle. Its deliverable is the
   devlog unit: `000-009` research plus EVERY implementation phase's decade doc
   (`010`, `020`, `030`, … with sub-docs like `021` where a phase needs finer grain)
   at full diff-level precision (DIFFLEVEL-ROADMAP-01).
2. **The roadmap cycle's D is the roadmap lock.** Closing it finalizes the map: phases
   are refined to map 1:1 onto the decade docs. The initial registration is a
   skeleton; the lock is the docs-only D, and the map stays APPEND-friendly afterwards.
3. **Implementation starts at the NEXT cycle.** Each later work-phase consumes exactly
   one decade doc as one full cycle: its P re-verifies the pre-written doc against the
   current tree, amends it, then executes. Never implement two decade docs in one B.
4. **Docs-only means docs-only.** Allowed: research notes, inventories, design docs,
   repro and state snapshots, the decade docs themselves. Not allowed: production code
   patches, deploy actions, or completion claims for implementation criteria.

Exemptions: a loop that genuinely fits one work-phase skips the docs-only cycle, and
C0/C1 fast-path work is untouched. If multi-cycle scope is **discovered** mid-loop the
docs-first debt comes due — the next P is the roadmap amendment that writes the missing
decade docs before any further implementation cycle.

The slice map is APPEND-friendly (LOOP-UNIT-CHAIN-01): an independent unit discovered
mid-loop becomes a NEW work-phase appended to the map via a P-phase amendment, then
runs as the next cycle in the same session.

**Faithful execution (anti-skip)**: do the real work of each PABCD-phase — P writes
the real plan, A really dispatches the audit, B really implements AND verifies, C
really runs tsc/tests, D really summarizes with evidence. Never rubber-stamp a phase.

## §6. Repository Root Contract

Before writing a PABCD plan or dispatching an employee, determine the actual
working repository root with `pwd -P` from the target repo. If `Project root` is
injected at the top of the system prompt, use it directly; if not, recommend the user
configure it (Manager UI → Project settings, or `cli-jaw project add /path/to/repo`)
to avoid JAW_HOME/codebase confusion. Every A/B phase `cli-jaw dispatch` task body
MUST begin with `Project root: /absolute/path/to/current/repo`.

Rules: `Project root` is the current working repository, never `JAW_HOME`; workers never infer
the root from `~/.cli-jaw*`, `process.cwd()`, or a temp dir; all relative repo paths
resolve against `Project root`; if it is unknown, STOP and ask before dispatching.

## §7. Shared Plan (auto-injected)

When P completes, the plan is saved to the **worklog `## Plan` section** (single source
of truth) and kept in `ctx.plan`; no project-root file is created. In A and B the
orchestrator **auto-injects the full plan body** at the top of every `cli-jaw dispatch`
task under `## Approved Plan`, so workers never read a plan file — the task body holds
only the audit/verify instruction. Example: write a brief file (`Project root: ...` +
the instruction), then `cli-jaw dispatch --agent "Backend" --task-file
/tmp/audit-brief.md --async`; the result re-enters as employee-results context. Omit
`--async` only for a quick (<2 min) blocking verify. Fan-out: `--batch --agents-file
<path> --async`; overlays: `--task-tags "testing,security"`.

### §7.1 Parallel dispatch: isolation, specialists, decorrelated review

- **DEFAULT (DISPATCH-ISOLATION-01):** Parallel employee lanes in the same
  work-phase are context-isolated: each dispatch task names an explicit access
  list — which prior outputs (paths or pasted excerpts) this lane may read — and
  nothing else from peer lanes is visible. Never paste one lane's in-progress
  trajectory or draft output into another outside the access list: the first
  finished trajectory otherwise steers every later lane into redundant agreement
  (orchestration collapse) and the parallelism buys nothing. This generalizes the
  §11.8 star topology from divergence lanes to ALL parallel dispatch. Durable
  cross-cycle artifacts (worklog `## Plan`, devlog, D summaries) stay shared;
  widening an access list is a stated decision in the dispatch task.
- **HEURISTIC (SPECIALIST-CRUX-01):** When P or A identifies a narrow crux outside
  the main line's domain — a derivation, a protocol subtlety, a domain constant, a
  security property — dispatch a specialist lane to re-derive that crux from first
  principles before merging the work that depends on it. The specialist's return
  names its assumptions, the derivation or trace, and the exact decision its
  verdict changes.
- **HEURISTIC (REVIEW-DECORRELATE-01):** When the runtime offers more than one
  model family, run the A reviewer — and any §11.3 clean-slate re-examination after
  repeated failed repairs — on a different model family than the one that produced
  the plan or build. Same-family reviewers share blind spots; decorrelating the
  reviewer is the cheapest independence upgrade available.
- **DEFAULT (DISPATCH-ECONOMY-01):** Decide delegation on three axes —
  specifiability (can the task packet state its inputs, outputs, and decision
  boundary completely?), verifiability (can the return be checked mechanically:
  anchors, figures, reproduction commands?), and judgment ownership
  (collapse/crux VERDICTS stay with the boss; re-derivation, standardized
  implementation, research, and audits are dispatchable). A slice that fails any
  axis stays with the boss. Complexity or importance is NOT an axis: a hard
  derivation that passes all three axes is dispatchable (SPECIALIST-CRUX-01 above),
  and a trivial slice whose packet cannot state its decision boundary is not.
  Output side: every return receives an accept/reject/merge disposition with a
  one-line rationale BEFORE the next wave is dispatched (wave-granular allowed).
  Returns must carry verbatim anchors — file:line quotes, exact figures, URLs — a
  paraphrase-only summary creates correlated blind spots between boss and reviewer.
  Prefer batch-waves with a single synthesis over drip-feed spawning. Speculative
  dispatch of a later phase's work is default-OFF; the one exception is
  phase-invariant EXTERNAL research (reads no repo state), quarantined as
  `candidate — unverified` and discarded by default on plan amendment.

(Adopted 2026-07-07 from the Sakana Fugu learned-orchestrator report,
arXiv:2606.21228; canonical record: pabcd_initiative devlog
`260707_fugu_orchestration_adoption`. DISPATCH-ECONOMY-01 adopted 2026-07-11 from
an adversarial fork-debate + Tier-2 arXiv claim ledger (10 papers, evidence grades
recorded; codexclaw devlog `260711_dispatch_economy_docs_site`).)

### §7.2 Dispatch packet, lane, and lifecycle

§7.1 decides **whether** to dispatch. These decide **how**, and each one names a
failure that looks like something else when you hit it.

**DISPATCH-TASK-01 (DEFAULT) — the packet.** Every dispatch carries a structured
packet with these sections, in this order:

`TASK` · `SCOPE` · `MUST DO` · `MUST NOT` · `PROOF` · `RETURN FORMAT` · decision boundary

- **Write scopes must be disjoint** across concurrent lanes, with explicit read
  bounds. Two lanes that can touch one file are one lane.
- **The plan travels with the dispatch.** Pass the concrete plan and scope; never
  let a worker reconstruct the plan from a thin task description (§8 Context Drift).
- **Name every required skill explicitly** — nothing infers an omitted one.
- **Workers return evidence and unresolved judgments; the dispatching session
  decides and integrates.** Judgment ownership never delegates
  (DISPATCH-ECONOMY-01).

**DISPATCH-AGENT-TYPE-01 (DEFAULT) — the lane.** The read-only/write-capable split
is a **dispatch-time classification**, not a description of what the worker happens
to do:

- **read-only lane** — plan audit, research, review, verification. The default, and
  what the A gate, the B review lane, and the C verification lane all use.
- **write-capable lane** — a deliberate implementation slice only, with a bounded
  write scope named in the packet (§8).

Mismatching the lane to the packet is a real failure with a misleading symptom. A
read-only packet sent down a write-capable lane produces a worker held to
obligations it has no permission to satisfy, and what you observe is a worker
repeating the same answer against the same directive. When you see that, check the
lane before rewriting the prompt — it is almost always the lane.

**LEAF-TOPOLOGY-01 (DEFAULT) — the topology.** A dispatched worker is a leaf: it
does its scoped task and returns, without standing up its own orchestration layer.
Recursion is a deliberate per-dispatch grant, never a default. A runtime whose
workers may fan out internally should say so explicitly rather than leaving it
ambiguous, because an unplanned second layer makes write scopes unprovable.

**DISPATCH-ACTOR-01 (DEFAULT) — reuse across rounds.** Follow-up rounds in the same
role and work context **reuse the existing worker** rather than spawning fresh. The
point is context preservation: the reviewer or builder keeps what it already read,
so round two argues about the change instead of re-deriving the baseline.

If the runtime distinguishes "send more work" from "deliver context only", know
which is which — using the context-only channel to request work produces a worker
that never runs and a caller that waits forever.

Do **not** justify reuse with "same provider, so the prompt cache is warm". That
was tested and rejected in the lineage this rule comes from. Reuse is about
context, not cost.

**Carve-out.** The final adversarial pass at C — and any reviewer that has already
shaped the fix through synthesis rounds — gets a **fresh** reviewer, or a direct
independent `file:line` audit. Anchoring must never grade its own influence. Same
independence argument as REVIEW-DECORRELATE-01 (§7.1), applied across rounds instead
of across model families.

**DISPATCH-RETIRE-01 (DEFAULT) — the exception to reuse.** A worker that failed —
error, timeout, unresponsive, nonsense output — is retired, not nursed.

- **At most ONE retry** against the same worker, then abandon it and spawn fresh
  with the failure folded into the new packet.
- A worker that has produced nothing after roughly three wait cycles is a failed
  dispatch, and **that retirement consumes the one retry.** Silence does not earn a
  second chance on top of the silence.
- **Packet-failure reclaim.** When a second, distinct worker also fails the SAME
  packet, stop blaming workers: two independent failures on one packet are evidence
  the packet failed DISPATCH-ECONOMY-01's specifiability bar. The dispatching
  session reclaims that slice and does the work directly rather than dispatching a
  third copy.

Both lifecycle rules are agent-followed doctrine, not runtime gates — nothing
watches worker lifecycles for you.

## §8. Pitfalls

**Delegation Trap** — B phase: Boss writes by default. Workers are READ-ONLY verifiers
unless granted otherwise. A worker may write only when the slice passes
DISPATCH-ECONOMY-01 (§7.1: specifiable, verifiable, no verdict ownership) AND the
dispatch is explicitly write-capable with a bounded scope (`--mutable`, optionally
`--scope`). Without `--mutable`, "implement/write/create" tasks are forbidden. Always
allowed: `"verify src/x.ts compiles"`, `"check integration of Y"`, `"report DONE or
NEEDS_FIX"`.

**Context Drift** — a worker saying *"I'll proceed based on my assumption of the plan"*
→ STOP; verify the dispatch went through `/api/orchestrate/dispatch` (only that path
auto-injects the plan). Never let workers reconstruct the plan from a short task.

**Phase Skip** — A (audit) is mandatory for C4, and for C3 when public contract,
architecture, persistence, cross-agent, or cross-session risk exists; micro-audit for
C2, optional for C0-C1 (`dev` §0.0). B verification is never "skippable"; intensity
scales with class (PABCD-AUTO-01). The orchestrator does not enforce these gates — YOU do.

## §9. PABCD Depth by Work Class

| Class | Plan (P) | Audit (A) | Build (B) | Check (C) | Record (D) |
|-------|----------|-----------|-----------|-----------|------------|
| C0-C1 | None/inline | Optional | Direct fix | Smallest proof | One-line summary as a numbered record doc in the owning unit (UNIT-RESIDENCE-01) |
| C2 | Compact plan | Micro-audit | Boss-led build, focused tests | Targeted gate | Summary |
| C3 | Compact or full PABCD plan depending on persistence/risk | Required when public contract, architecture, persistence, cross-agent, or cross-session risk exists; otherwise focused audit | Boss-led build (economy-eligible slices dispatchable, §7.1), employees verify only when useful | Affected suite + docs consistency when docs/contracts changed | Summary + evidence; durable record only when state must persist |
| C4 | Full PABCD plan (mandatory) | Required, independent | Boss-led build, employee verifies | Full relevant gates | Durable risk/approval/evidence record |
| C5 | Interview/research first | — | — | — | Reclassify, then follow the new class |

Render-artifact work-phases add C-RENDER-GROUNDING-01 (§3 C) to the Check column at C2+; C4 escalates its evidence to STRICT (persisted screenshot).

## §10. Optimization-Loop Meta-Rules (plateau discipline)

These rules apply to score/objective-maximization loops and repeated PABCD passes where
candidates are being discarded by evidence gates. Gate validity itself is owned by
`dev-testing` §9.5 Limited-Oracle / Score-Objective Evaluation.

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
  codes, diffs, telemetry) over model self-assessment; use `cli-jaw dispatch` employees
  as independent verifiers when the class/risk warrants it.
- **Memory lives on disk**, not only in the transcript: worklog `## Plan`, devlog,
  attestations, goal checkpoints, death logs — the next iteration resumes from artifacts.
- **Budget exhaustion is not done.** Never report a budget stop as success.
- **Context pressure is not budget exhaustion.** Compaction is survivable BY DESIGN
  because memory lives on disk: an approaching context limit means checkpoint durable
  state (worklog, goalplan, devlog) and continue after the flush — never grounds to
  close the goal, shrink the plan, or report `DONE`/`BUDGET_EXHAUSTED`.
  `BUDGET_EXHAUSTED` requires a bound the plan actually stated (tokens, cost,
  wall-clock).
- **Interview does not solve intent transfer.** It yields an initial loop-spec; later
  evidence may force `cli-jaw orchestrate I` — intent refines cyclically.

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
patching, enter root-cause mode (`dev-debugging`); 3 → replan (`cli-jaw orchestrate P`)
or return to Interview. **HEURISTIC (LOOP-DOOM-01):** 3 attestation failures in the
same phase within one work-phase means no progress; force an Interview return — the
server may not enforce this, so the Boss agent self-applies it.

### §11.4 Loop archetype by problem type (DEFAULT, LOOP-ARCHETYPE-01)

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
bound; record resource decisions in the plan and `cli-jaw goal update` checkpoints. For
C4 surfaces an unattended loop with unstated scope is an ESCALATE-class omission: stop
and ask before running it.

### §11.6 Continuation doctrine (DEFAULT, LOOP-CONTINUE-01)

The loop keeps the turn alive; the agent decides what "remaining work" means. On loop
re-entry or after a D close: do not redefine the objective downward (P/goalplan
criteria are the bar); audit completion against current repo state, not memory; read
durable state first (worklog/devlog/goalplan ledger) to recover remaining
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
  `cli-jaw dispatch` employee lanes each produce ONE one-page candidate direction
  doc (no code, no worktrees) with mandatory front-matter: `assumptions`, `risks`,
  `kill-criteria`, `evidence-needed`. Lane research stays read-only; the doc write
  is scoped to the worklog/devlog plan archive. The BOSS session (collapse owner)
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
  decision in the worklog/devlog plan.

Budget rationale: employee tokens may be near-free, but wall-clock and the Boss's
triage attention are not. Tier inflation (defaulting to Tier 2 because employees are
cheap) is a discipline violation; so is tier deflation that lets a load-bearing
conflict collapse from paper arguments alone.

Unknowns lane: the first Tier-1 dispatch of a research-heavy or unfamiliar-surface
unit SHOULD be a blindspot/unknowns pass (known unknowns, unknown knowns recoverable
from references, unknown unknowns from codebase/web search), so candidates are sourced
from evidence, not parameter tweaks (§10 LOOP-CANDIDATE-ANCHOR-01).

Topology: candidates and critiques never flow employee-to-employee; exchange is
file-mediated through the worklog/devlog archive, and the Boss schedules rounds and
owns the collapse (star-shaped exchange). Employees MAY use their own CLI sub-agents
internally per the agent-spawn doctrine; that internal parallelism does not change
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
