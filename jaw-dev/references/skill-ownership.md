# Skill Ownership Map

Companion to `../SKILL.md`. Read when adding a rule area, or when two skills look like
they say the same thing and you need to know which one is authoritative.

Factored out of `../SKILL.md` because a router file should route. Consult this
table when adding a rule area or reconciling overlapping advice.

Each rule area has exactly one canonical owner. Other skills may contain stubs but MUST NOT duplicate canonical content.

| Rule Area | Canonical Owner | Stub Locations |
|-----------|----------------|----------------|
| Circular dependencies | jaw-dev-architecture | jaw-dev, jaw-dev-code-reviewer |
| Module boundaries / layers | jaw-dev-architecture | jaw-dev-backend, jaw-dev-frontend |
| Coupling taxonomy | jaw-dev-architecture | jaw-dev-code-reviewer |
| Barrel / re-export | jaw-dev-architecture | jaw-dev-scaffolding |
| Pre-write search (DEV-NECESSITY-01, DEV-MAP-FIRST-01, DEV-READ-FIRST-01) | jaw-dev/references/development-practice.md | jaw-dev-code-reviewer |
| Edge-first testing | jaw-dev-testing §6 | — |
| Test-induced defense | jaw-dev-testing §6.7 | jaw-dev-code-reviewer |
| Boundary-only defense | jaw-dev-architecture §4 | jaw-dev-backend, jaw-dev-security |
| Process isolation | jaw-dev-backend refs/ | jaw-dev-code-reviewer |
| Code quality signals / antipatterns | jaw-dev-code-reviewer §3 | jaw-dev §6 |
| Long-lived connections (server lifecycle) | jaw-dev-backend §1 | jaw-dev-frontend |
| Browser connection budgets | jaw-dev-frontend refs/performance-budget | — |
| Async task queue | jaw-dev-backend §2 | — |
| Debugging methodology | jaw-dev-debugging | jaw-dev-code-reviewer |
| Data pipeline patterns | jaw-dev-data | jaw-dev-backend |
| Design intent discovery | jaw-dev-uiux-design | jaw-dev-frontend |
| Design judgment | jaw-dev-uiux-design | jaw-dev-frontend |
| Frontend implementation | jaw-dev-frontend | jaw-dev-uiux-design |
| Project scaffolding / docs | jaw-dev-scaffolding | jaw-dev-pabcd |
| Reader-facing document structure (READER-DOC-*, FAMILY-READER-01, REPORT-STORY-00) | jaw-dev/references/reader-documents.md | jaw-dev-pabcd, jaw-dev-scaffolding, jaw-diagram, doc-coauthoring |
| Orchestration workflow | jaw-dev-pabcd | — |
| Operational gates | jaw-dev-devops | jaw-dev-backend, jaw-dev-scaffolding |
| Stacked PRs (DEV-STACK-01..07, DEV-STACK-OPT-IN-01) | jaw-dev/references/stacked-prs.md | jaw-dev-pabcd, jaw-dev-code-reviewer, jaw-dev-devops |
| Hosted CI evidence (DEV-CI-EVIDENCE-01) | jaw-dev/references/hosted-ci-evidence.md | jaw-dev-pabcd, jaw-dev-devops |
| Safe shell/public text (DEV-SHELL-TEXT-01, DEV-PRIVACY-01) | jaw-dev/references/safe-public-text.md | all jaw-dev-* |
| Flaky tests / CI re-run (TEST-FLAKE-*) | jaw-dev-testing refs/ci-pipeline.md §5 | jaw-dev-debugging, jaw-dev-devops refs/ci-cd-deploy.md §6 |
| Browser capability selection | jaw-dev/references/browser-routing.md | jaw-dev/references/browse-qa-ladders.md |
| Search and QA depth | active search skill; jaw-dev-testing | jaw-dev/references/browse-qa-ladders.md |
| Manual surface QA / evidence matrix | jaw-dev-testing | jaw-dev/references/browser-routing.md |
| Anti-slop output | jaw-dev §Family Invariants | all jaw-dev-* |
| file:line evidence | jaw-dev §Family Invariants | all jaw-dev-* |
| Completion proof | jaw-dev §Family Invariants | jaw-dev-pabcd, all jaw-dev-* |

When updating a rule, update the canonical owner first, then verify stubs still point correctly.
