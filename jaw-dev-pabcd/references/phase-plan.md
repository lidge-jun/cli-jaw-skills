# Plan phase

P explores and plans within the authorized scope; it does not implement. Read project
instructions and the live tree. For a broad or unfamiliar repository, include a compact tree,
existing conventions and source-of-truth documents, tests, proposed document locations, and the
SoT sync target (SOT-SYNC-01). Do not create a new project-level source-of-truth folder during B
unless approved in P. Present an answer-first reader summary following [reader
documents](../../jaw-dev/references/reader-documents.md), then an executable file map with
NEW/MODIFY/DELETE, before/after behavior for MODIFY, complete proposed content for NEW, and a
verifier for each outcome. Present the short user-facing direction and its planned location; ask
which business logic must remain a user decision.

## Loop-spec

For C2+ record nine fields: loop archetype, trigger, user-visible goal, non-goals, verifier and
what it measures, stop condition, memory artifact at the approved location, expected terminal
states, and escalation condition. In goal mode add resource and credential scope. For open-ended
optimization, record descriptor axes, candidate count, selection rule and telemetry before
generating candidates. A plan-only or no-tests instruction is authoritative: mark the verifier
`NOT RUN` with the reason; do not execute it merely to satisfy this reference.

**PLAN-VERIFIER-REAL-01:** For an executable plan, run each proposed verifier before claiming it
works. Record exit code and prove the command reads its target through a direct argument,
script/glob, config include, or cited call chain. If the command cannot observe the change,
classify that acceptance row as human review. A green gate for unrelated files is not evidence
for this plan.

**PLAN-FIELD-CHAIN-01:** For a new field or enum value, map creation → serialization →
deserialization/unknown-value handling → every consumer. Search the type, field and existing
values, including aliases, destructuring and default branches. Give each stage a path or `N/A +
reason` so an uncreatable value and an ignored value are both visible.

**PLAN-BYPASS-NAMED-01:** For new enforcement, record strength/mechanism, executing surface,
concrete bypass, residual risk and any wording downgrade. An agent-followed statement or
bypassable warning is not an unbreakable runtime gate; `final layer: none` is valid when
supported by evidence.

Name an activation scenario for every new conditional path so C can trigger and observe it
(C-ACTIVATION-GROUNDING-01). Mirror work items and statuses into the worklog `## Plan` for
visibility while keeping the approved diff-level document authoritative (PLAN-TRACK-01). The
reviewer in A checks every field and path.

## Consultation when available

Where delegation is authorized and a suitable employee exists, dispatch a read-only architect
proposal. Main writes the executable plan, then sends the actual plan for reflection and uses an
independent reviewer in A. Record returned `runId` and employee identity; do not claim
consultation from an unanswered dispatch. If delegation is unavailable or barred, note the gap
and complete the plan locally. The main agent owns the final plan and business decisions.
