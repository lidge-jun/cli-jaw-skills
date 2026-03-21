---
name: dev-scaffolding
description: "Scaffold new projects or add feature modules following the Lidge Standard (Feature-based + Colocation + Barrel Export + devlog). Language-agnostic — auto-detects project type from config files. Also audits existing projects for structural compliance. Triggers: scaffold, new project, new feature, init project, audit structure, scaffolding, add module, project setup."
---

# Dev Scaffolding

Rules for generating and auditing project structures. Create files directly following these rules. Use the audit script (§10) for verification.

## 1. The Lidge Standard

Three pillars every project must follow:

1. **Screaming Architecture** — folder names reveal what the app does (`stock-price/`, `auth/`, `report/`)
2. **Colocation** — related files live together (logic + test + schema in the same folder)
3. **Barrel Export** — each feature exposes a single entry point (`index.ts`, `index.js`, `__init__.py`, or Go package)

## 2. Project Skeleton

When creating a new project, always generate this structure:

```
<project>/
├── AGENTS.md                 # AI context: what this project does, tech stack, conventions
├── README.md                 # Human overview, quick start, architecture summary
├── .env.example              # Environment variable template (never commit .env)
├── .gitignore                # Language-appropriate ignores
├── devlog/
│   ├── _plan/                # Active plans (move to _fin/ when complete)
│   │   └── README.md
│   ├── _fin/                 # Completed work in YYMMDD_title/ folders
│   │   └── .gitkeep
│   └── str_func/             # Module documentation (see §8)
│       └── AGENTS.md         # str_func index + rules
├── src/                      # Source code (feature-based layout)
│   └── shared/               # Truly shared utilities only
├── config/                   # Configuration files
├── docs/                     # Design docs, specs, legal
│   └── .gitkeep
└── tests/                    # Integration / e2e tests
    └── e2e/
        └── .gitkeep
```

After skeleton, add language-specific files based on detection (§3):
- Package manifest (`package.json`, `pyproject.toml`, `go.mod`, `Cargo.toml`)
- Entry point (`src/index.ts`, `src/main.py`, `src/main.go`, `src/main.rs`)
- Language config (`tsconfig.json`, `ruff.toml`, etc.)
- Shared barrel (`src/shared/index.ts`, `src/shared/__init__.py`)

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

Principle: "flat until you can't" — start flat, sub-folder only when feature exceeds 10 files.

## 6. Naming Conventions

| Item                | Rule                  | Example                      |
| ------------------- | --------------------- | ---------------------------- |
| Folders             | kebab-case            | `stock-price/`, `user-auth/` |
| JS/TS files         | kebab-case + suffix   | `stock-price.tool.ts`        |
| Python files        | snake_case + suffix   | `stock_price_tool.py`        |
| Go files            | snake_case            | `stock_price.go`             |
| Rust files          | snake_case            | `stock_price.rs`             |
| devlog entries      | `YYMMDD_title/`       | `260303_scaffolding/`        |
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

Each project must maintain `devlog/str_func/` with:
- One `.md` file per feature folder (e.g., `price.md`, `auth.md`)
- Each document: **300–500 lines**
- Required sections: File Tree, Module Responsibility, Key Function Signatures, Dependencies, Dependents, Sync Checklist
- Update the corresponding `.md` whenever a feature is added or modified
- Template: `<SKILL_DIR>/assets/str_func_template.md`

## 9. Split Rules

| Condition                | Action                                        |
| ------------------------ | --------------------------------------------- |
| File > 500 lines         | Split into focused modules within same folder |
| Feature > 10 files       | Create sub-folders by responsibility          |
| Different runtime needed | Split into `frontend/` + `backend/`           |
| 3+ apps share code       | Extract to `shared/` or monorepo `packages/`  |

## 10. Audit

Run the audit script to check structural compliance:

```bash
bash <SKILL_DIR>/scripts/scaffold-audit.sh [project-path]
```

Checks 7 items: feature-based structure, colocation, barrel exports, devlog, .env safety, file length (<500 lines), AGENTS.md.
