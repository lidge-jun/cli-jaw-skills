# Upstream port: codexclaw 0.2.41 → jaw-* skills

This records how the jaw-* development skills track their upstream,
[lidge-jun/codexclaw](https://github.com/lidge-jun/codexclaw). It is the lineage note for the
October 2026 port; read it when you wonder why a codexclaw rule is, or is not, present here.

- Upstream revision: codexclaw main 96e8d5ce (plugin 0.2.41).
- Delta reviewed: 048ae759..96e8d5ce, everything that changed in codexclaw skills after the
  2026-09-02 backport (122 files, about 130 rule ids absent from jaw-*).

## Method

The port is rule by rule, never a folder copy. A rule keeps its upstream id when its substance
survives translation, so cross-references resolve in both trees, and each id has exactly one owner
here. Every reviewed rule and file got one of four dispositions:

| Disposition | Meaning |
|---|---|
| PORT | Applies as written once skill names are translated. |
| ADAPT | Applies, but is rebound to a real cli-jaw surface (a command, route or file that exists). |
| COVERED | jaw-* already says this; no second copy. |
| N-A | Depends on something cli-jaw does not have; the reason is listed below. |

To find where a rule lives, search its id: rg -n "DEV-CI-EVIDENCE-01" jaw-*. The defining section
is the one that states the rule; other hits are pointers to it. Rules that were ported, adapted or
already covered therefore need no list here; only the N-A decisions are recorded below, because
their absence is otherwise invisible.

## Ownership map

| Upstream skill | jaw owner |
|---|---|
| dev | jaw-dev (router) with references for development practice, methodology overlays, browser routing, hosted CI evidence, safe public text, stacked PRs and reader documents |
| dev-architecture, dev-backend, dev-data, dev-debugging, dev-security, dev-scaffolding, dev-frontend, dev-uiux-design, dev-code-reviewer, dev-testing, dev-devops | the matching jaw-dev-* skill |
| pabcd, loop, interview, goalplan, orchestrate | jaw-dev-pabcd, with references for interview, phase control, plan, audit, check, implementation units, dispatch and loop continuation |
| qa | jaw-dev-testing (manual surface QA references); no separate QA skill |
| dev-visualizer, dev-diagram-viewer | jaw-diagram for figures, render verification and visual-report composition; PDF production stays with jaw-pdf |
| search | jaw-search |
| kwrite | jaw-dev-write (only additions; the jaw skill is newer on generation and revision boundaries) |
| recall | jaw-memory |
| worktree-guardian | generic worktree and branch safety in jaw-dev-devops; nothing else |
| lunasearch, remote, skill-hub, ast-grep | not ported (see N-A) |
| repo-map | existing standalone skill here; nothing in this delta changes it |

Rules that span owners keep one home: hosted CI evidence and stacked-PR rules live in jaw-dev,
desktop acceptance (DESKTOP-*) in jaw-dev-devops, reader-document rules (including REPORT-STORY-00)
in jaw-dev, research handoff (REPORT-RESEARCH-01) in jaw-search, Korean prose signals (CAT-11) in
jaw-dev-write, and visual report composition (REPORT-DESIGN, -EXHIBIT, -VIZ, -PRINT, -QA and
related ids) in jaw-diagram. The others point to them.

## Runtime glossary

| codexclaw / Codex concept | cli-jaw translation |
|---|---|
| subagent spawn, read-only or write scope | cli-jaw dispatch --agent <employee> with --read-only, --mutable, --scope, --task-file |
| waiting on and reading a child | cli-jaw worker status, watch or read <runId> |
| cxc orchestrate with attestation | cli-jaw orchestrate I/P/A/B/C/D --attest '<json>' |
| host goal | cli-jaw goal set, status, update --evidence, done |
| recall | cli-jaw chat search and cli-jaw memory search |
| browser routing | cli-jaw browser fetch for a URL; navigate, snapshot, screenshot for rendered checks |
| repository map | cli-jaw map |
| Codex threads and worktree lanes, peer task messages | none; use separate checkouts under the repository's branch policy |
| Stop-hook continuation, PreToolUse guards | none; the rule's discipline is kept as guidance without claiming enforcement |
| asynchronous question tool | none; ask one focused question in the conversation |
| Code Mode / native tool execution | none; portable shell advice only |

## Not applicable, with reasons

| Upstream rules or files | Reason |
|---|---|
| WORKTREE-GUARD-01..04, SHELL-SUBST-01, WG-CONCEPT/FACTS/HOOK/LIMIT/AGENTS | Codex hook and Codex-app worktree semantics; cli-jaw has no equivalent hook, so prose cannot promise enforcement. DEV-SHELL-TEXT-01 keeps the quoting advice. |
| DISPATCH-SCHEMA-DETECT-01, DISPATCH-AUTHORITY-01, DISPATCH-LANE-MANIFEST-01, DISPATCH-SHARED-TREE-01, LANE-PACKET-01, LANE-MERGE-GRANT-01 | Codex collab tool families, thread creation and task manifests. |
| DEV-STACK-08 | An owner-authorized [skip ci] batch exception; it conflicts with cli-jaw's push-CI contract. |
| DESKTOP-FFI-01, DESKTOP-WIDGET-01, verify-lipo-command.mjs | Tauri/Swift FFI, WidgetKit and universal binaries; cli-jaw ships an arm64 Electron app. |
| async-questions, code-mode-examples, native-execution, peer-collaboration references | Codex-only surfaces (see glossary). |
| dev-visualizer scripts and assets, port-maintenance, upstream sync files | An upstream report exporter and its maintenance; cli-jaw has no such command. The rules they enforce are ported as guidance in jaw-diagram. |
| durable goalplan schema, receipts, final gate, QA validate-evidence.mjs | codexclaw state files and validators with no cli-jaw consumer. |
| lunasearch, remote, skill-hub, agents/openai.yaml files | A fixed model lane, an unrelated onboarding skill, a deprecated redirect, and Codex display metadata. |
| ast-grep | A codexclaw helper script; the delta only added its license notice, and cli-jaw ships no ast-grep skill. |
| VIZ-SCOPE-01 | Governs upstream-first maintenance of a separate visualizer project; jaw-diagram is maintained here. |
| REPORT-VOICE-01 | Referenced upstream but never defined there. |
| QA-01, VIZ-01, UTF-16, DS-01, DS-02, PK-01, RT-01, UI-01..03, READER-01 | Text that only looks like a rule id (abbreviations, sample rows, a character encoding). |
