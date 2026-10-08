# Implementation Log (devlog) Routine — the documentation loop inside PABCD

Canonical spec for the per-implementation-unit documentation routine that rides the
PABCD cycle. Companion to `jaw-dev-pabcd/SKILL.md` §3.1 (numbering) and
`jaw-dev-scaffolding/SKILL.md` §2.1 (folder proposal rules). Read before any development
work that needs a unit; the C0/C1 exemptions and UNIT-RESIDENCE-01 live in `../../jaw-dev-pabcd/references/implementation-units.md`. The full routine below is for C2+/multi-phase work.

## The unit: one implementation unit = one plan folder

```
devlog/
  _plan/
    YYMMDD_slug/          ← one implementation unit (not one issue, not one commit)
      00_plan.md          ← master plan: objective, constraints, work-phase map
      01_research_*.md    ← research/spec docs (00-09 range)
      10_phase1_*.md      ← phase 1 design at diff-level precision
      20_phase2_*.md      ← phase 2 ...
  _fin/                   ← completed units move here (closure record kept, not deleted)
```

Numbering: decade ranges separate concerns — `00-09` research/specs/MOC, `10-19`
phase 1, `20-29` phase 2, and so on. Two-digit (`00_`, `10_`) is the default; a repo
may standardize on three digits (`000_`, `010_`) — pick ONE per repo and never mix.
Never bare semantic filenames (`PLAN.md`, `RCA.md`) — the numeric prefix is the
ordering and the audit trail.

## How the routine rides PABCD (the loop)

| Phase | Documentation action | Gate |
|-------|---------------------|------|
| P | CONCRETIZE: write `00_plan.md` (objective, measured baseline, dependency-ordered work-phase map, risks) + research docs `01+`; decade docs for **EVERY roadmap phase** at **diff-level precision** (exact paths, NEW/MODIFY/DELETE, before/after for MODIFY) — DIFFLEVEL-ROADMAP-01 | plan exists as files, not chat |
| A | AUDIT THE DOCS: an independent reviewer checks the plan docs — paths/signatures real, research coverage complete, phases sized, no ownership violations, no contradictions vs research | FAIL → fix docs → re-audit |
| B | Implementation cites the doc it executes; deviations are edited back into the doc BEFORE coding past them | doc and code never diverge silently |
| C | Gate results (commands + tails) recorded into the unit; general SoT docs patched to match the change (SOT-SYNC-01 — recommend creating one if absent) | evidence lives next to the plan |
| D | Attestation/summary appended to `00_plan.md`; on unit completion the folder moves `_plan/` → `_fin/` | durable closure record |

Multi-cycle units: one full PABCD per work-phase; ALL phase design docs are written
to diff-level in the FIRST P (or the design-only Phase-0 pass) —
DIFFLEVEL-ROADMAP-01. P of each later cycle re-verifies its pre-written doc against
the current codebase (stale check) and amends it BEFORE building; it never writes
the doc fresh mid-unit. The attestation log in `00_plan.md` is the continuity spine
— each new P quotes the previous D conclusion from it (see `jaw-dev-pabcd` §10
LOOP-CONTINUITY-01).

## Mapping to mainstream developer practice (translation table)

This routine is NOT an issue tracker. Issues are the industry's unit of *tracking*
(small, cheap, closable); this is the industry's unit of *thinking* — the design-doc
lineage. Mature orgs run BOTH and link them. If a collaborator says "devlog isn't
standard", translate:

| This routine | Mainstream equivalent |
|--------------|----------------------|
| `_plan/YYMMDD_slug/` unit folder | Design doc / RFC per feature (Google design docs, Rust RFCs, PEPs) |
| `00-09` research docs | RFC "Motivation / Prior art" sections |
| Diff-level phase docs | Detailed design; kernel patch-series cover letter |
| A-phase doc audit | Design review / RFC final-comment-period — review BEFORE code |
| Evidence in C, attestation in D | CI gate records + review sign-off |
| `_fin/` closure record | Shipped postmortem + changelog entry |
| Hard-to-reverse decisions | ADR (see `jaw-dev-scaffolding` §2.1 — separate, immutable) |
| Issue/ticket | Still useful: one issue per unit LINKING to the folder; sub-issues for tracking granularity |

Two deliberate differences from common practice, kept on purpose:
1. **Diff-level precision in the plan** — most design docs stop at architecture;
   agents execute better from exact-path plans, and the A audit becomes mechanical.
2. **Docs gate execution** (A before B) — in many teams design review is advisory;
   here it is a hard gate because the executor (an agent) will otherwise
   confidently build from a flawed plan.

## Reader narrative vs evidence

The top plan answers what was decided and why, in terms a new reader can act on. Put raw receipts, probe logs, and check tails in linked evidence rather than inline narrative. See `../../jaw-dev/references/reader-documents.md` for the canonical reader-document rules; link each material claim to its evidence.

## Ceremony follows the class

The full routine above (master plan, all-phase diff-level docs, and doc audit) applies to C4, any multi-phase unit, and C3 when state must persist across turns or contracts need a durable audit trail. For C0/C1, follow `../../jaw-dev-pabcd/references/implementation-units.md`: C0 has no numbered record; C1 records change, reason, and proof only inside an existing owning unit. Do not create a unit solely for C1.
