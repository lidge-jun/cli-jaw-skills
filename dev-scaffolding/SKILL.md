---
name: dev-scaffolding
description: "MUST USE for project setup, feature scaffolding, structural audits, or documentation scaffolding — applies the Lidge Standard, colocation, public boundary exports, repo-first convention reuse, and source-of-truth doc planning. Triggers: scaffold, scaffolding, new project, init project, new feature, add module, project setup, structure audit, architecture docs, source-of-truth docs, monorepo setup, API docs, 스캐폴딩, 새 프로젝트, 새 기능, 구조 점검, 모듈 추가."
metadata:
  short-description: "Project and module scaffolding with repo-first convention reuse and structural audits."
  last-verified: "2026-07-02"
---

# Dev Scaffolding

> **C0/C1 work (small local patches):** See `dev` §0.0 Work Classifier + §0.1 Patch Fast-Path before reading references.

Rules for generating and auditing project structures. Create files directly following these rules. Use the audit script (§12) for verification.
This skill activates by change surface: new project setup, feature/module scaffolding, structural audits, or documentation scaffolding.

## Modular References

| File | When to Read | What It Covers |
|------|-------------|----------------|
| `references/implementation-log.md` | C3+/multi-phase/cross-session work units | Full devlog routine: decade-numbered plan folders, P-concretize → A-audit → D-archive loop, mainstream design-doc/RFC mapping |
| `references/api-docs.md` | API documentation generation | OpenAPI 3.1, developer portal, CI doc drift, SDK generation |
| `references/monorepo-tooling.md` | Setting up or optimizing monorepo builds | Turborepo vs Nx 2026 decision table, task graph for AI agents, CI optimization |

## External/current scaffolding evidence

For current generator behavior, template commands, package versions, framework
recommendations, provider bootstrap docs, or source-sensitive tooling choices,
read the active `search` skill and follow its query-rewrite, source-fetch, and
evidence-status rules. Browser fetch/open/text/get-dom/snapshot is used only
after candidate URLs exist and the setup claim needs source verification.

## 1. The Lidge Standard

Apply for new projects or when a repo has no clear structural convention of its own; defer to an existing mature convention when one is present (§2). Three pillars:

1. **Screaming Architecture** — folder names reveal what the app does (`stock-price/`, `auth/`, `report/`)
2. **Colocation** — related files live together (logic + test + schema in the same folder)
3. **Public Boundary Export** — each feature/package exposes a single public entry point (`index.ts`, `index.js`, `__init__.py`, or Go package) at its boundary; internal convenience barrels are banned (owned by `dev-architecture` §5)

## 2. Existing Repo First

Before scaffolding inside an existing repo:
1. Detect existing architecture, docs, plans, changelog, ADR, agent-context, source-of-truth, and devlog conventions.
2. Read existing `structure/`, `devlog/`, `docs/`, `plans/`, or equivalent source-of-truth logs before proposing new structure.
3. Reuse clear conventions instead of imposing the Lidge/source-of-truth default.
4. Show a compact tree before broad additions.
5. Do not create `structure/`, `devlog/`, `docs/`, `AGENTS.md`, or similar project-level folders without approval.

MUST preserve mature repo conventions over the Lidge/source-of-truth default.

## 2.1 Lightweight Source of Truth (implementation-unit devlog)

The implementation-unit devlog routine (`devlog/_plan/` units — `dev-pabcd` §3.1,
UNIT-RESIDENCE-01) is the DEFAULT for any repo you do development work in — a
process rule, not a named style to be requested. Propose the `structure/`
architecture docs when:
- The repo is immature, undocumented, or inconsistent; or
- The user asks for a durable source-of-truth structure; or
- A broad change needs a durable plan/current-architecture record.

Default proposal:

```
structure/
  README.md              # index of current architecture docs
  architecture.md        # current system shape, not future wishes
  conventions.md         # naming, layout, commands, testing
devlog/
  _plan/                 # active plans
  _fin/                  # completed work summaries
```

Folder names are advisory. If the repo already has `docs/`, `adr/`, `plans/`, `changelog/`, or another convention, propose using those instead.
Also detect optional lightweight source-of-truth files such as `CONTEXT.md`,
`CONTEXT-MAP.md`, and `docs/adr/`. Reuse them when present. Do not create them unless
the repo already uses that convention or the user approves. Create an ADR only for a
decision that is hard to reverse, surprising without context, or has a real tradeoff.

**SoT sync (DEFAULT, SOT-SYNC-01):** before patching a repo, FIND its general
source-of-truth docs first (`structure/`, `architecture.md`, INDEX/context docs)
and read them; any unit that changes architecture, contracts, or structure patches
the SoT doc in the SAME unit (C gate, dev-pabcd §3 C). If the repo has no SoT doc,
recommend creating one — once, via the proposal flow above — rather than silently
working without a source of truth.

Implementation-unit devlog method:
- Split large work into phase-level documents instead of one huge plan —
  dependency-ordered (PHASE-SPLIT-01), ALL written to diff-level up front
  (DIFFLEVEL-ROADMAP-01; both defined in `dev-pabcd`).
- Keep diff-level plans in files, not chat: exact paths, NEW/MODIFY/DELETE, before/after diffs for MODIFY, complete content for NEW.
- Keep chat summaries short: explain the phase, show a compact tree/change map, then link the plan file.
- Move completed phase folders to `_fin/`; keep pending/future work under `_plan/` or an existing equivalent.

Phase document naming uses decade-range prefixes (LEXICO-SPLIT-01). For the canonical table (00–09 research, 10–19 Phase 1, etc.), see `dev-pabcd/SKILL.md` §3.1 Implementation-Unit Documents — that is the single source of truth.
- Plan unit folder: `devlog/_plan/YYMMDD_slug/`
- The numeric prefix is the source of ordering. Never use bare semantic filenames (`PLAN.md`, `DIFF_PLAN.md`, `PHASES.md`, `RCA.md`).
- When adding a document, scan siblings and choose the next unused prefix in the correct decade.

Before creating any `structure/`/`devlog/` folders, ask concisely: state that no source-of-truth docs were found, show the proposed tree, give a specific recommendation, and confirm you will not create them without approval. This gate governs INTRODUCING the convention to a repo (the first `devlog/` or `structure/`); once `devlog/_plan/` exists, creating unit subfolders — including the minimal record unit mandated by UNIT-RESIDENCE-01 — is routine and needs no approval dialogue.

## 2.2 Project Skeleton

For a new project, propose the source-of-truth structure in the plan.
If the user explicitly asks for the full source-of-truth standard (§8), create it.
Otherwise ask once before adding `structure/` and `devlog/`.

When creating an approved new project skeleton, include the source-of-truth and feature-based essentials: `AGENTS.md` + `README.md` (context/overview), `.env.example` + `.gitignore`, `devlog/_plan/` + `devlog/_fin/` (and `str_func/` only for the full standard, §8), `src/` with a `shared/` for truly-shared code, `config/`, `docs/`, and `tests/e2e/`. Then add the language-appropriate package manifest, entry point, language config, and per-feature public boundary exports (per `dev-architecture` §5; file names from language detection, §3). Defer exact layout to the framework's own generator when one exists.

## 3. Language Detection

Detect project type from existing files. Priority order:

| File Found                             | Project Type                  |
| -------------------------------------- | ----------------------------- |
| `tsconfig.json`                        | TypeScript (Node)             |
| `package.json` (no tsconfig)           | JavaScript (Node)             |
| `pyproject.toml` or `requirements.txt` | Python                        |
| `go.mod`                               | Go                            |
| `Cargo.toml`                           | Rust                          |
| None of the above                      | → Tech Stack Decision (below) |

For greenfield projects, use the Tech Stack Decision process (§3.1) instead of asking "What language?"

## 3.1 Tech Stack Decision (New Projects)

When creating a new project with no existing framework, guide the user through plain-language choices:

1. **Type**: What are they building? (static site, interactive app, full-stack service, CLI tool, data pipeline)
2. **Scale**: How big? (1-3 pages, multi-page, ongoing content, large app)
3. **Features**: Login needed? Data storage? Real-time?

Present options as `<Framework> — <what it gives you>`, recommend one with reasoning, let user pick.

Match tool complexity to task complexity. Escalate tooling only when justified by user requirements (SEO, CMS, scaling).

## 4. Fullstack Split Rule

Decide project layout based on runtime:

| Scenario           | Layout                   | Example                                  |
| ------------------ | ------------------------ | ---------------------------------------- |
| Single runtime     | `src/` modular           | Next.js, Node CLI + API, Python monolith |
| Multiple runtimes  | `frontend/` + `backend/` | React + FastAPI, Vue + Go API            |
| Monorepo (3+ apps) | `packages/` or `apps/`   | Turborepo, Nx                            |

Each side gets its own package manifest and entry point. Shared types go in root `shared/` or `packages/shared/`.

## 5. Feature Module Rules

When adding a new feature, create a folder under `src/` with these files:

| Language   | Folder        | Main File      | Test File      | Public boundary export |
| ---------- | ------------- | -------------- | -------------- | ---------------------- |
| JavaScript | `kebab-case/` | `name.tool.js` | `name.test.js` | `index.js`             |
| TypeScript | `kebab-case/` | `name.tool.ts` | `name.test.ts` | `index.ts`             |
| Python     | `kebab-case/` | `name_tool.py` | `test_name.py` | `__init__.py`          |
| Go         | `kebab-case/` | `name.go`      | `name_test.go` | *(package = boundary)* |
| Rust       | `kebab-case/` | `name.rs`      | inline `#[cfg(test)]` or `tests/` | `lib.rs`/parent `mod name;` |

The `index.*` file is the feature's **public boundary export**. Barrel discipline is owned
by `dev-architecture` §5: external consumers import this boundary, internal code imports
sources directly, and convenience-only internal barrels are banned.

Principle: "flat until you can't" — start flat, sub-folder only when a folder becomes hard to scan.

## 6. Naming Conventions

| Item                | Rule                  | Example                      |
| ------------------- | --------------------- | ---------------------------- |
| Folders             | kebab-case            | `stock-price/`, `user-auth/` |
| JS/TS files         | kebab-case + suffix   | `stock-price.tool.ts`        |
| Python files        | snake_case + suffix   | `stock_price_tool.py`        |
| Go files            | snake_case            | `stock_price.go`             |
| Rust files          | snake_case            | `stock_price.rs`             |
| devlog plan folders | `YYMMDD_slug/`        | `260510_phase_doc_naming/` |
| devlog phase docs   | decade-prefixed `NN_slug.md`, `00_*` is the index | `00_plan.md`, `10_phase1_skill_contract.md` |
| Functions (JS/TS)   | camelCase             | `getStockPrice()`            |
| Functions (Python)  | snake_case            | `get_stock_price()`          |
| Functions (Go)      | PascalCase (exported) | `GetStockPrice()`            |
| Functions (Rust)    | snake_case            | `get_stock_price()`          |

## 7. File Suffixes

| Suffix                                             | Role                    | Languages    |
| -------------------------------------------------- | ----------------------- | ------------ |
| `.tool.ts` / `.tool.js` / `_tool.py`               | Core business logic     | JS/TS/Python |
| `.test.ts` / `.test.js` / `test_*.py` / `_test.go` | Tests                   | All          |
| `.schema.ts` / `.schema.js`                        | Type/schema definitions | JS/TS        |
| `.route.ts` / `.route.js`                          | API routes              | JS/TS        |
| `.template.md`                                     | Templates               | All          |

## 8. str_func Rules

`str_func` is part of the full Lidge standard, not the lightweight default.

Use it when:
- The user explicitly asks for the full Lidge structure.
- The repo already maintains `str_func` docs.
- A broad feature needs durable module-level function documentation.

When used:
- One `.md` file per feature folder (e.g., `price.md`, `auth.md`)
- Keep each document concise, bounded, and task-oriented — not padded to a fixed length
- Required sections: File Tree, Module Responsibility, Key Function Signatures, Dependencies, Dependents, Sync Checklist
- Update the corresponding `.md` whenever a feature is added or modified
- Template: `<SKILL_DIR>/assets/str_func_template.md`

Do not generate heavy feature docs by default for small or immature repos.
Prefer lightweight `structure/architecture.md` and `structure/conventions.md` first.

## 9. Split Rules

Split smells (heuristics, not hard gates):

| Condition                       | Action                                        |
| ------------------------------- | --------------------------------------------- |
| File grows past ~500 lines      | Split into focused modules within same folder |
| Folder becomes hard to scan     | Create sub-folders by responsibility          |
| Different runtime needed        | Split into `frontend/` + `backend/`           |
| 3+ apps share code              | Extract to `shared/` or monorepo `packages/`  |

## 10. Cross-Cutting Scaffolding

### Health Endpoints
Backend scaffolds should propose health routes (skip if the mature repo already handles health checks per §2):
- `src/routes/health.ts` (or equivalent) — `/health` (liveness) and `/ready` (readiness)
- See `dev-backend/references/core/health-checks.md` for response format

### SEO Boilerplate (Web Projects)
Web project templates should include:
- `public/robots.txt` with AI crawler allowlist
- Meta tag component with OG defaults
- JSON-LD helper utility
- Sitemap generation (static or dynamic)

### CI Template
Generate CI config scaffold:
```
lint → typecheck → test (unit) → test (integration) → build → deploy (staging)
```

### Security Boilerplate
Generate security scaffolding: CSP headers, CORS config, rate limiting middleware, `.env.example` with placeholder secrets. See `dev-security/SKILL.md` for full patterns.

---

## 11. Documentation Generation

When `role=docs` or when generating project documentation:

### README Generation
1. Read existing structure (§2 Existing Repo First)
2. Generate README with: project purpose, quick start, architecture overview (link to structure/ if present), contribution guide
3. Match tone to project maturity: immature repos get setup-heavy READMEs; mature repos get architecture-heavy ones

### API Documentation
1. Scan route files and extract endpoint signatures
2. Generate per-endpoint docs: method, path, params, request/response shape, auth requirements
3. Place alongside code (colocation) or in `docs/api/` per project convention

### Structure Documentation
1. Generate `structure/README.md` or update existing structure docs
2. Include: directory tree, module responsibility map, dependency flow
3. Follow source-of-truth conventions (§2.1) when applicable

### Devlog Documentation
1. Follow decade numbering (`dev-pabcd/SKILL.md` §3.1, LEXICO-SPLIT-01): 00-09 research, 10-19 phase 1, etc.
2. Each devlog entry: title, date, what changed, why, evidence paths
3. Cross-reference related devlog entries within the same _plan/ folder

---

## 12. Audit

Run the scaffold audit if one is available for the repo (e.g. `bash <SKILL_DIR>/scripts/scaffold-audit.sh [project-path]`) to check structural compliance. Audit checks should reflect the project's own conventions — covering feature-based structure, colocation, public boundary exports (dev-architecture §5), devlog presence, `.env` safety, file length, and AGENTS.md where those apply.
