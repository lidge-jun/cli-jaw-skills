# Skill Ownership Map

Companion to `jaw-dev/SKILL.md`. Read when adding a rule area, or when two skills look like
they say the same thing and you need to know which one is authoritative.

Factored out of `SKILL.md` because a router file should route: the map is a lookup table
consulted at a specific moment, not something every reader of the skill needs inline. It is
a separate file upstream for the same reason.

Each rule area has exactly one canonical owner. Other skills may contain stubs but MUST NOT duplicate canonical content.

| Rule Area | Canonical Owner | Stub Locations |
|-----------|----------------|----------------|
| Circular dependencies | dev-architecture | dev, dev-code-reviewer |
| Module boundaries / layers | dev-architecture | dev-backend, dev-frontend |
| Coupling taxonomy | dev-architecture | dev-code-reviewer |
| Barrel / re-export | dev-architecture | dev-scaffolding |
| Pre-write search | dev §1.5 | dev-code-reviewer |
| Edge-first testing | dev-testing §6 | — |
| Test-induced defense | dev-testing §6.7 | dev-code-reviewer |
| Boundary-only defense | dev-architecture §4 | dev-backend, dev-security |
| Process isolation | dev-backend refs/ | dev-code-reviewer |
| Code quality signals / antipatterns | dev-code-reviewer §3 | dev §6 |
| Long-lived connections (server lifecycle) | dev-backend §1 | dev-frontend |
| Browser connection budgets | dev-frontend refs/performance-budget | — |
| Async task queue | dev-backend §2 | — |
| Debugging methodology | dev-debugging | dev-code-reviewer |
| Data pipeline patterns | dev-data | dev-backend |
| Design intent discovery | dev-uiux-design | dev-frontend |
| Design judgment | dev-uiux-design | dev-frontend |
| Frontend implementation | dev-frontend | dev-uiux-design |
| Project scaffolding / docs | dev-scaffolding | dev-pabcd |
| Orchestration workflow | dev-pabcd | — |
| Operational gates | dev-devops | dev-backend, dev-scaffolding |
| Stacked pull requests (DEV-STACK-*) | dev refs/stacked-prs.md | dev-pabcd, dev-code-reviewer, dev-devops |
| Flaky tests / CI re-run (TEST-FLAKE-*) | dev-testing refs/ci-pipeline.md §5 | dev-debugging, dev-devops refs/ci-cd-deploy.md §6 |
| Browse / QA tool routing | dev-testing (QA ladder), the active search skill (search ladder) | dev refs/browse-qa-ladders.md (routing summary) |
| Manual surface QA / evidence matrix | the Manager embedded browser surface | dev-testing (tool routing stays there) |
| Anti-slop output | dev §Family Invariants | all dev-* |
| file:line evidence | dev §Family Invariants | all dev-* |
| Completion proof | dev §Family Invariants | dev-pabcd, all dev-* |

When updating a rule, update the canonical owner first, then verify stubs still point correctly.
