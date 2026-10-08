# Methodology overlays (task_tags)

Methodologies are **conditional overlays, never universal**. They activate via dispatch
`task_tags`, explicit user request, repo convention, or a matching strict trigger — required
evidence applies only when the strict trigger applies (low-risk/local work uses the smallest
proof that validates the claim, with the reduced scope stated).

| Tag | Loads | Strict trigger |
|-----|-------|----------------|
| `tdd` / `testing` | jaw-dev-testing | User/repo enforces TDD, or regression risk |
| `bdd_acceptance` | jaw-dev-testing, jaw-dev | Ambiguous acceptance behavior |
| `ddd` / `clean_arch` / `hexagonal` / `architecture` | jaw-dev-architecture, jaw-dev-backend | Real boundary pressure at C3/C4 |
| `vertical_slice` | jaw-dev-architecture, jaw-dev-backend, jaw-dev-frontend, jaw-dev-testing | Thin end-to-end slice (C2) |
| `adr_rfc` | jaw-dev-architecture, jaw-dev-scaffolding | Significant decision, domain vocabulary, or ADR source-of-truth work |
| `review` / `code_review` | jaw-dev-code-reviewer | Review requested or C3/C4 |
| `threat_model` / `security` | jaw-dev-security | C4 security/data/tooling risk |
| `observability` / `observability_pipeline` | jaw-dev-backend (+jaw-dev-data) | Production, incident, release, long-lived runtime |
| `debugging` / `debugging_rca` | jaw-dev-debugging | Repeated failure needs root cause |
| `migration_backfill` | jaw-dev-data, jaw-dev-backend, jaw-dev-testing | Production or non-trivial data |
| `product_discovery` (+`_ui`) | jaw-dev (+jaw-dev-uiux-design) | Ambiguous behavior/user value/metric/prototype intent |
| `release_cd` | jaw-dev-testing, jaw-dev-backend, jaw-dev-scaffolding, jaw-dev-devops | Release/CI/CD surface |
| `devops` / `infra` / `deploy` | jaw-dev-devops | Container/K8s/IaC/deploy pipeline/SRE |
| `mobile_native` | jaw-dev-frontend + jaw-dev-uiux-design + jaw-dev-backend (refs) | RN/Flutter/Swift/Kotlin native app |
| `ml` / `ai` / `llm` / `rag` | jaw-dev-backend + jaw-dev-data + jaw-dev-testing (+jaw-dev-devops) | ML serving, RAG, pipeline, evaluation |
| `frontend_ui` | jaw-dev-frontend + jaw-dev-uiux-design | UI/design intent or runnable prototype variant work |
| `crud_fullstack` | jaw-dev-backend, jaw-dev-frontend, jaw-dev-testing | Boss/direct planning signal only — when delegating, prefer split roles |
| `logging` (CLI / scripts / libraries) | jaw-dev `logging.md` | What to emit and where; service instrumentation stays with jaw-dev-backend |
| stacked pull requests (`DEV-STACK-*`) | jaw-dev `stacked-prs.md` | When to stack, cascade discipline, layer shape, review scope, merge and CI safety |
| recall lookup (`DEV-RECALL-01`) | jaw-dev `recall-lookup.md` | Where to search before asking the user |
| browse / QA ladders | jaw-dev `browse-qa-ladders.md` + `browser-routing.md` | Public versus built-UI order, session and side-effect checks |
| rule-area ownership | jaw-dev `skill-ownership.md` | Which skill is authoritative for a rule area |
| employee skill guidance | jaw-dev `skill-injection-and-discovery.md` | Naming policy skills in a dispatch brief |


Tags are normalized `task_tags`, **not** employee `role` values; the execution role stays
`frontend|backend|data|docs` (PROMPT-ROUTING-01).

The boss sets `task_tags` at dispatch. With no tags, only strict triggers (self-assessed
by the employee, reduced scope stated) activate overlays — legacy dispatches without the
field behave identically. `task_tags` must be an array; a bare string is coerced to a
single tag, and unknown tags are surfaced in the prompt, not silently dropped.

### Ordinary product reference (on-demand)

For C2 ordinary product slices, the recipe lives in
`product/crud-product-development.md` — read it when building a conventional
feature slice, not for every task.
