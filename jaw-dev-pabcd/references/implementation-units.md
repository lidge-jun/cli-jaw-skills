# Implementation units

This reference owns DIFFLEVEL-ROADMAP-01, LEXICO-SPLIT-01, and UNIT-RESIDENCE-01. Follow the
repository-approved plan location. For projects that allow in-tree records,
`devlog/_plan/YYMMDD_slug/` is the default convention; a repository that forbids in-tree records
uses its approved external location. Never put private plans, audits, or evidence into a public
checkout.

## Class-scaled residence (UNIT-RESIDENCE-01)

- C0 trivial text changes create no numbered record. A concise change and proof report suffices.
- C1 local patches use a short change/reason/proof note only when an owning unit already exists. Do not create a unit solely for C1.
- C2+ use an implementation unit at the repository-approved location, with class-scaled planning and evidence. For C3, durable research is needed when state must persist across turns or workers, or when a public contract or architecture decision needs an audit trail. C4 requires durable research and risk evidence.

## Multi-cycle roadmap (DIFFLEVEL-ROADMAP-01)

When a loop has two or more work-phases, its first PABCD cycle is docs-only. Write a
`000_plan.md` with objective, constraints and dependency-ordered work-phase map, plus every
phase's decade document at executable diff-level precision. Name exact NEW/MODIFY/DELETE paths
and before/after behavior; an outline or empty scaffold cannot authorize implementation. The
roadmap cycle's D locks the map. Implementation begins in the next cycle. Each later P reads the
live tree, quotes the previous D conclusion, revalidates its prewritten decade document, and
amends stale paths before building. If multi-cycle scope emerges later, pay this roadmap debt at
the next P. See [loop continuation](loop-continuation.md) for cycle order.

## Numbering and separation (LEXICO-SPLIT-01)

Use three-digit lexicographic prefixes within a new unit: `000`–`009` for research/spec/MOC,
`010`–`019` for the first implementation phase, `020`–`029` for the second, and so on. Keep
research/spec material and implementation designs in separate documents. Bare semantic filenames (`PLAN.md`,
`DIFF_PLAN.md`, `PHASES.md`, `RCA.md`, unnumbered folders) or a mixed research/implementation document fail audit
for a C2+ unit. Use the next free number
within a decade, with a sub-index if it overflows. Preserve historical names to avoid breaking
inbound links. Numbering is a convention within the approved record location, never a reason to
create a private record in a forbidden checkout.

| Range | Purpose |
|-------|---------|
| 000-009 | Research, specs, MOC (`000_plan.md`, `001_api-survey.md`) |
| 010-019, 020-029, ... | Phase 1, Phase 2, ... (`010_phase1-auth-module.md`) |

Three digits rather than two because the range carries the meaning: with two digits `10` reads as
both "decade 1" and "tenth document"; with three, `010` is phase 1's first document and `001`
research's first. Do not mix two- and three-digit prefixes in one unit.

The P plan orders phases by dependency: foundations and contracts, then capabilities,
integration and hardening (PHASE-SPLIT-01). Each work-phase still ends in independently
observable proof. Do not group phases solely by effort, payoff, or team function. The
documentation routine may be extended by the installed `jaw-dev-scaffolding` owner; repository
policy takes precedence over any generic example.
