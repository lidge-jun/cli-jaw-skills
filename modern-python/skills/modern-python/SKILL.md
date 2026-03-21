---
name: modern-python
description: Configures Python projects with modern tooling (uv, ruff, ty). Use when creating projects, writing standalone scripts, or migrating from pip/Poetry/mypy/black.
---

# Modern Python

Ref: [trailofbits/cookiecutter-python](https://github.com/trailofbits/cookiecutter-python)

## Tool Choices

| Use | Instead of | Why |
|-----|-----------|-----|
| `uv add` / `uv sync` | `uv pip install`, manual pyproject.toml edits | Manages lockfile and venv automatically |
| `uv run <cmd>` | `source .venv/bin/activate` | No manual venv management |
| `uv_build` backend | `hatchling` | Simpler, sufficient for most cases |
| uv | Poetry | Faster, better ecosystem integration |
| pyproject.toml / PEP 723 | requirements.txt | Modern standard |
| ty | mypy / pyright | Faster, from Astral team |
| `[dependency-groups]` (PEP 735) | `[project.optional-dependencies]` | Dedicated dev/test grouping |
| `[tool.ty.environment]` python-version | `[tool.ty]` python-version | Correct config nesting |
| prek ([setup](./references/prek.md)) | pre-commit | Faster, Rust-native |

## Decision Tree

```
What are you doing?
│
├─ Single-file script with dependencies?
│   └─ PEP 723 inline metadata (./references/pep723-scripts.md)
│
├─ New multi-file project (not distributed)?
│   └─ Minimal uv setup (Quick Start below)
│
├─ New reusable package/library?
│   └─ Full project setup (Full Setup below)
│
└─ Migrating existing project?
    └─ Migration Guide below
```

## Tool Overview

| Tool | Purpose | Replaces |
|------|---------|----------|
| **uv** | Package/dependency management | pip, virtualenv, pip-tools, pipx, pyenv |
| **ruff** | Linting and formatting | flake8, black, isort, pyupgrade |
| **ty** | Type checking | mypy, pyright |
| **pytest** | Testing with coverage | unittest |
| **prek** | Pre-commit hooks | pre-commit |

### Security Tools

| Tool | Purpose |
|------|---------|
| **shellcheck** | Shell script linting |
| **detect-secrets** | Secret detection |
| **actionlint** | Workflow syntax validation |
| **zizmor** | Workflow security audit |
| **pip-audit** | Dependency vulnerability scanning |

See [security-setup.md](./references/security-setup.md) for configuration.

## Quick Start: Minimal Project

```bash
uv init myproject && cd myproject
uv add requests rich
uv add --group dev pytest ruff ty

uv run python src/myproject/main.py
uv run pytest
uv run ruff check .
```

## Full Project Setup

For distributable packages, consider the Trail of Bits cookiecutter:

```bash
uvx cookiecutter gh:trailofbits/cookiecutter-python
```

Or manually:

```bash
uv init --package myproject && cd myproject
```

### pyproject.toml Configuration

See [pyproject.md](./references/pyproject.md) for complete reference.

```toml
[project]
name = "myproject"
version = "0.1.0"
requires-python = ">=3.11"
dependencies = []

[dependency-groups]
dev = [{include-group = "lint"}, {include-group = "test"}, {include-group = "audit"}]
lint = ["ruff", "ty"]
test = ["pytest", "pytest-cov"]
audit = ["pip-audit"]

[tool.ruff]
line-length = 100
target-version = "py311"

[tool.ruff.lint]
select = ["ALL"]
ignore = ["D", "COM812", "ISC001"]

[tool.pytest]
addopts = ["--cov=myproject", "--cov-fail-under=80"]

[tool.ty.terminal]
error-on-warning = true

[tool.ty.environment]
python-version = "3.11"

[tool.ty.rules]
possibly-unresolved-reference = "error"
unused-ignore-comment = "warn"
```

### Install and Verify

```bash
uv sync --all-groups
```

### Makefile

```makefile
.PHONY: dev lint format test build

dev:
uv sync --all-groups

lint:
uv run ruff format --check && uv run ruff check && uv run ty check src/

format:
uv run ruff format .

test:
uv run pytest

build:
uv build
```

## Migration Guide

### From requirements.txt + pip

**Scripts:** Convert to PEP 723 inline metadata ([pep723-scripts.md](./references/pep723-scripts.md))

**Projects:**
```bash
uv init --bare
uv add requests rich  # add each dependency
uv sync
```

Then delete `requirements.txt`, `requirements-dev.txt`, old venvs. Add `uv.lock` to version control.

### From setup.py / setup.cfg

1. `uv init --bare` to create pyproject.toml
2. `uv add` each dependency from `install_requires`
3. `uv add --group dev` for dev dependencies
4. Copy metadata (name, version, description) to `[project]`
5. Delete `setup.py`, `setup.cfg`, `MANIFEST.in`

### From flake8 + black + isort → ruff

1. Remove old tools, delete `.flake8`, `[tool.black]`, `[tool.isort]` configs
2. `uv add --group dev ruff`
3. Configure ruff ([ruff-config.md](./references/ruff-config.md))
4. `uv run ruff check --fix . && uv run ruff format .`

### From mypy / pyright → ty

1. Remove old tools, delete `mypy.ini`, `pyrightconfig.json`
2. `uv add --group dev ty`
3. `uv run ty check src/`

## uv Command Reference

| Command | Description |
|---------|-------------|
| `uv init` / `uv init --package` | Create project / distributable package |
| `uv add <pkg>` | Add dependency |
| `uv add --group dev <pkg>` | Add to dependency group |
| `uv remove <pkg>` | Remove dependency |
| `uv sync` / `uv sync --all-groups` | Install dependencies |
| `uv run <cmd>` | Run command in venv |
| `uv run --with <pkg> <cmd>` | Run with temporary dependency (one-off usage) |
| `uv build` / `uv publish` | Build / publish package |

## References

- [pyproject.md](./references/pyproject.md) — pyproject.toml reference
- [uv-commands.md](./references/uv-commands.md) — uv command reference
- [ruff-config.md](./references/ruff-config.md) — Ruff configuration
- [testing.md](./references/testing.md) — pytest and coverage
- [pep723-scripts.md](./references/pep723-scripts.md) — PEP 723 inline metadata
- [prek.md](./references/prek.md) — Pre-commit hooks
- [security-setup.md](./references/security-setup.md) — Security tools
- [dependabot.md](./references/dependabot.md) — Automated updates
- [migration-checklist.md](./references/migration-checklist.md) — Migration cleanup
