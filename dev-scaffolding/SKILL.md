---
name: dev-scaffolding
description: "Scaffold new projects or add feature modules following the Lidge Standard (Feature-based + Colocation + Barrel Export + devlog). Language-agnostic — auto-detects project type from config files. Also audits existing projects for structural compliance. Triggers: scaffold, new project, new feature, init project, audit structure, scaffolding, add module, project setup."
---

# Dev Scaffolding

Rules for generating and auditing project structures. Create files directly following these rules. Use the audit script (§10) for verification.

## 1. The Lidge Standard

Apply for new projects or when a repo has no clear structural convention of its own; defer to an existing mature convention when one is present (§2). Three pillars:

1. **Screaming Architecture** — folder names reveal what the app does (`stock-price/`, `auth/`, `report/`)
2. **Colocation** — related files live together (logic + test + schema in the same folder)
3. **Barrel Export** — each feature exposes a single entry point (`index.ts`, `index.js`, `__init__.py`, or Go package)

## 2. Existing Repo First

Before scaffolding inside an existing repo:
1. Detect existing architecture, docs, plans, changelog, ADR, agent-context, source-of-truth, and devlog conventions.
2. Read existing `structure/`, `devlog/`, `docs/`, `plans/`, or equivalent source-of-truth logs before proposing new structure.
3. Reuse clear conventions instead of imposing the Lidge/Jawdev default.
4. Show a compact tree before broad additions.
5. Do not create `structure/`, `devlog/`, `docs/`, `AGENTS.md`, or similar project-level folders without approval.

MUST preserve mature repo conventions over the Lidge/Jawdev default.

## 2.1 Lightweight Jawdev Source of Truth

Use this only when:
- The repo is immature, undocumented, or inconsistent; or
- The user asks for Jawdev/Lidge-style structure; or
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

Jawdev devlog method:
- Split large work into phase-level documents instead of one huge plan.
- Keep diff-level plans in files, not chat: exact paths, NEW/MODIFY/DELETE, before/after diffs for MODIFY, complete content for NEW.
- Keep chat summaries short: explain the phase, show a compact tree/change map, then link the plan file.
- Move completed phase folders to `_fin/`; keep pending/future work under `_plan/` or an existing equivalent.

Jawdev phase document naming uses decade-range prefixes (see `dev-pabcd/SKILL.md` for the canonical table):
- Plan unit folder: `devlog/_plan/YYMMDD_slug/`
- `00–09` research/specs/MOC (mandatory before implementation), `10–19` Phase 1, `20–29` Phase 2, and so on.
- Default sequential within a decade (`00`, `01`, `02`…); on overflow use a sub-index (`00_0_name.md`, `00_1_name.md`).
- `00_*` (e.g. `00_plan.md` or `00_overview.md`) is the plan-folder index and file map.
- The numeric prefix is the source of ordering. Never use bare semantic filenames (`PLAN.md`, `DIFF_PLAN.md`, `PHASES.md`, `RCA.md`).
- When adding a document, scan siblings and choose the next unused prefix in the correct decade.

Before creating any `structure/`/`devlog/` folders, ask concisely: state that no source-of-truth docs were found, show the proposed tree, give a specific recommendation, and confirm you will not create them without approval.

## 2.2 Project Skeleton

For a new project, propose the source-of-truth structure in the plan.
If the user explicitly asks for Lidge/Jawdev standard, create it.
Otherwise ask once before adding `structure/` and `devlog/`.

When creating an approved new project skeleton, include the source-of-truth and feature-based essentials: `AGENTS.md` + `README.md` (context/overview), `.env.example` + `.gitignore`, `devlog/_plan/` + `devlog/_fin/` (and `str_func/` only for the full standard, §8), `src/` with a `shared/` for truly-shared code, `config/`, `docs/`, and `tests/e2e/`. Then add the language-appropriate package manifest, entry point, language config, and shared barrel from detection (§3). Defer exact layout to the framework's own generator when one exists.

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

| Language   | Folder        | Main File      | Test File      | Barrel               |
| ---------- | ------------- | -------------- | -------------- | -------------------- |
| JavaScript | `kebab-case/` | `name.tool.js` | `name.test.js` | `index.js`           |
| TypeScript | `kebab-case/` | `name.tool.ts` | `name.test.ts` | `index.ts`           |
| Python     | `kebab-case/` | `name_tool.py` | `test_name.py` | `__init__.py`        |
| Go         | `kebab-case/` | `name.go`      | `name_test.go` | *(package = barrel)* |
| Rust       | `kebab-case/` | `mod.rs`       | `name_test.rs` | `mod.rs`             |

Principle: "flat until you can't" — start flat, sub-folder only when a folder becomes hard to scan.

## 6. Naming Conventions

| Item                | Rule                  | Example                      |
| ------------------- | --------------------- | ---------------------------- |
| Folders             | kebab-case            | `stock-price/`, `user-auth/` |
| JS/TS files         | kebab-case + suffix   | `stock-price.tool.ts`        |
| Python files        | snake_case + suffix   | `stock_price_tool.py`        |
| Go files            | snake_case            | `stock_price.go`             |
| Rust files          | snake_case            | `stock_price.rs`             |
| devlog plan folders | `YYMMDD_slug/`        | `260510_jawdev_phase_doc_naming/` |
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

`str_func` is part of the full Lidge/Jawdev standard, not the lightweight default.

Use it when:
- The user explicitly asks for full Lidge/Jawdev structure.
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

## 10. Audit

Run the scaffold audit if one is available for the repo (e.g. `bash <SKILL_DIR>/scripts/scaffold-audit.sh [project-path]`) to check structural compliance. Audit checks should reflect the project's own conventions — covering feature-based structure, colocation, barrel exports, devlog presence, `.env` safety, file length, and AGENTS.md where those apply.
