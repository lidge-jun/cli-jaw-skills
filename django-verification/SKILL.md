---
name: django-verification
description: "Verification loop for Django projects: migrations, linting, tests with coverage, security scans, and deployment readiness checks before release or PR."
---

# Django Verification Loop

## Goal

Run a structured verification pipeline before PRs, after major changes, or pre-deploy. Catches migration, quality, security, and config issues.

## When to Activate

- Before opening a pull request
- After model changes, migration updates, or dependency upgrades
- Pre-deployment verification

## Phase 1: Environment Check

```bash
python --version
which python
python manage.py check
```

Verify the project's Python version requirement is met and the virtualenv is active. If misconfigured, stop and fix before proceeding.

## Phase 2: Code Quality

Run the project's configured linter, formatter, and type checker. Use whatever tools the project already has (e.g., ruff, flake8, black, mypy, isort). The key commands:

```bash
# Lint + format (use project's configured tools)
python manage.py check --deploy
```

Adapt to the project's `pyproject.toml` / `setup.cfg` — do not assume specific tools are installed.

## Phase 3: Migrations

```bash
python manage.py showmigrations
python manage.py makemigrations --check
python manage.py migrate --plan
```

Report:
- Pending migrations count
- Migration conflicts
- Model changes missing migrations

If conflicts exist: `python manage.py makemigrations --merge`

## Phase 4: Tests + Coverage

```bash
# Use the project's test runner (pytest or manage.py test)
python manage.py test  # or: pytest --cov
```

Report:
- Total: X passed, Y failed, Z skipped
- Coverage: XX%

Coverage targets (adjust per project):

| Component | Target |
|-----------|--------|
| Models | 90%+ |
| Views | 80%+ |
| Services | 90%+ |
| Overall | 80%+ |

## Phase 5: Security Scan

```bash
python manage.py check --deploy
pip-audit  # or: safety check
```

Optional (if installed): `bandit -r .`, `gitleaks detect --source .`

Report:
- Vulnerable dependencies
- Security misconfigurations
- Hardcoded secrets
- DEBUG mode status

## Phase 6: Static Assets & Commands

```bash
python manage.py collectstatic --noinput
python manage.py check --database default
```

If the project uses a frontend build step, run it before collectstatic.

## Phase 7: Diff Review

```bash
git diff --stat
git diff | grep -iE "todo|fixme|hack|print\(|pdb|breakpoint|DEBUG\s*=\s*True"
```

Checklist:
- No debug statements (print, pdb, breakpoint)
- No hardcoded secrets
- Migrations included for model changes
- Error handling for external calls
- Transaction management where needed

## Output Template

```
DJANGO VERIFICATION REPORT
==========================
Phase 1: Environment  ✓/✗
Phase 2: Code Quality ✓/✗  (N issues)
Phase 3: Migrations   ✓/✗  (N pending)
Phase 4: Tests        X passed, Y failed, Z skipped — Coverage: XX%
Phase 5: Security     ✓/✗  (N vulnerabilities)
Phase 6: Assets       ✓/✗
Phase 7: Diff Review  ✓/✗

RECOMMENDATION: [pass / fix X before deploying]
```

## Pre-Deployment Checklist

- [ ] All tests passing
- [ ] Coverage ≥ 80%
- [ ] No security vulnerabilities
- [ ] No unapplied migrations
- [ ] DEBUG = False
- [ ] SECRET_KEY properly configured
- [ ] ALLOWED_HOSTS set
- [ ] Static files collected
- [ ] Logging and error monitoring configured
- [ ] HTTPS/SSL configured

## Quick Reference

| Check | Command |
|-------|---------|
| Django check | `python manage.py check --deploy` |
| Migrations | `python manage.py makemigrations --check` |
| Tests | `python manage.py test` or `pytest --cov` |
| Security | `pip-audit` |
| Static | `python manage.py collectstatic --noinput` |
| Diff | `git diff --stat` |

## Constraints

- Adapt commands to project's actual toolchain — do not assume specific linters/formatters are installed.
- Use `python manage.py test` as fallback if pytest is not configured.
- SQLite is acceptable for dev/test — do not flag it as an error.
- This skill complements, not replaces, manual code review and staging tests.
