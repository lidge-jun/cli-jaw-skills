<p align="center">
  <strong>cli-jaw-skills</strong><br>
  Reference skill library for cli-jaw agents.
</p>

<p align="center">
  <a href="https://github.com/lidge-jun/cli-jaw-skills/actions/workflows/ci.yml"><img src="https://github.com/lidge-jun/cli-jaw-skills/actions/workflows/ci.yml/badge.svg" alt="CI"></a>
  <a href="https://github.com/lidge-jun/cli-jaw-skills/actions/workflows/pages.yml"><img src="https://github.com/lidge-jun/cli-jaw-skills/actions/workflows/pages.yml/badge.svg" alt="Pages"></a>
  <img src="https://img.shields.io/badge/skills-227-111827" alt="227 skills">
  <img src="https://img.shields.io/badge/reference_assets-47-2563eb" alt="47 skills with references">
</p>

---

# cli-jaw-skills

`cli-jaw-skills` is a public reference library of agent skills for `cli-jaw`.
Each skill is a directory with a required `SKILL.md` and optional reference
materials, scripts, templates, tests, or domain assets.

The repo is designed as source material for the active `cli-jaw` skill system:
installers and sync jobs can copy selected skills into runtime skill folders,
while maintainers can review the full library in one place.

## Public Surface

| Surface | Status |
|---------|--------|
| Skill library | 227 top-level `SKILL.md` files |
| Reference material | 47 skills include `reference/` or `references/` folders |
| Helper scripts | 28 skills include `scripts/` folders |
| Templates | 2 skills include `templates/` folders |
| Office formats | `docx`, `pptx`, `xlsx`, and `hwp` skill families are present |
| CI | Focused Python regression tests, skill count validation, known long-skill drift checks, docs drift checks |
| GitHub Pages | `/docs/index.html` static landing page, ready for Pages deployment |
| License | No root license file is currently declared |

Remote signal:

- Repository: `lidge-jun/cli-jaw-skills`, public, 4 stars, 0 forks.
- Existing workflow: `Sync OfficeCLI Skills` has one recent success and one
  recent failure from manual dispatch history.
- GitHub Pages is not enabled yet (`GET /repos/lidge-jun/cli-jaw-skills/pages`
  returns 404). The added Pages workflow deploys `/docs` after an authorized push.

## Library Shape

The library spans agent operations, browser control, document generation,
developer guides, frontend/backend/data/testing/security workflows, search,
media, office files, cloud platforms, productivity systems, and language-specific
engineering patterns.

Representative families:

| Family | Examples |
|--------|----------|
| Agent operations | `browser`, `desktop-control`, `web-ai`, `memory`, `telegram-send` |
|| Development guides | `dev`, `dev-frontend`, `dev-backend`, `dev-testing`, `dev-security`, `dev-devops` |
| Office/document work | `docx`, `pptx`, `xlsx`, `hwp`, `pdf`, `pdf-vision` |
| Cloud and web | `cloudflare-deploy`, `durable-objects`, `vercel-deploy`, `web-perf` |
| Language patterns | `python-patterns`, `rust-patterns`, `golang-patterns`, `kotlin-patterns` |
| Media and visuals | `imagegen`, `video`, `sora`, `canvas-design`, `diagram` |
| Business workflows | `market-research`, `inventory-demand-planning`, `production-scheduling` |

## Skill Directory Contract

Minimum shape:

```text
skill-id/
  SKILL.md
```

Expanded shape:

```text
skill-id/
  SKILL.md
  references/
  scripts/
  templates/
  tests/
```

`SKILL.md` files should stay focused. Large examples, templates, and background
material belong in sibling folders so the runtime can load only the context a
task needs.

## Quickstart

Clone the library:

```bash
git clone https://github.com/lidge-jun/cli-jaw-skills.git
cd cli-jaw-skills
```

Count skills:

```bash
find . -mindepth 2 -maxdepth 2 -name SKILL.md | wc -l
```

Inspect a skill:

```bash
sed -n '1,160p' dev-frontend/SKILL.md
find dev-frontend/references -maxdepth 2 -type f | sort
```

Run local validation for the public surface:

```bash
python3 -m pytest tests/test_dev_frontend_refresh.py -q
python3 scripts/validate_public_surface.py
git diff --check
```

## Validation Policy

The public repo checks should prove four things:

1. The stated skill count matches the filesystem.
2. `SKILL.md` files are present where expected, and any new line-limit drift is
   caught. The known long Office skills are tracked separately.
3. Focused frontend regression tests continue to pass.
4. README, Pages, and workflows do not drift from the real skill library.

The added CI workflow validates those checks without publishing anything.

The broader OfficeCLI CJK regression suite under `tests/test_cjk_regression.py`
requires a compatible local `officecli` binary. In this environment that suite
currently fails before exercising these documentation changes because the local
OfficeCLI install is missing `System.Collections.NonGeneric` and has command
shape drift for PPTX shape props.

## OfficeCLI Sync

`.github/workflows/sync-officecli-skills.yml` receives OfficeCLI sync events and
copies OfficeCLI-derived materials into the `docx`, `pptx`, and `xlsx` skill
families.

OfficeCLI guidance in `skills_ref` is consent-based:

- Check install state first with `command -v officecli`.
- If OfficeCLI is available, recommend it first for high-fidelity Office work,
  validation, batch/resident flows, CJK/rhwp-aware behavior, and Office-native
  output.
- If OfficeCLI is missing, do not auto-install from a skill. Ask the user to
  choose between installing the supported fork, continuing with lightweight
  fallback tools for the current task, or stopping.
- The supported cli-jaw fork is `https://github.com/lidge-jun/OfficeCLI`.
  Do not direct users to download/install upstream `iOfficeAI/OfficeCLI` unless
  they explicitly request vanilla upstream behavior.
- Before lightweight fallback, ask again and state likely feature/fidelity loss.
  If the user chooses lightweight mode, save that preference to memory for
  future Office work.

That workflow can commit and push from GitHub Actions when triggered. This local
work does not push changes; remote CI and Pages deployment require an authorized
push.

## Security Notes

- Treat skills as executable instructions: review `SKILL.md` and helper scripts
  before promoting a skill to active runtime use.
- Keep secrets out of skill files. Use environment-variable placeholders and
  user-level configuration.
- Prefer small active skill sets. Reference skills should be loaded on demand,
  not injected into every prompt.
- Keep generated or downloaded assets inspectable and attributable.

## Adding or Updating a Skill

1. Create or update a top-level `skill-id/SKILL.md`.
2. Move long supporting material into `references/`, `scripts/`, or `templates/`.
3. Run the validation commands above.
4. Update README and Pages counts if the public surface changes.
5. For OfficeCLI-derived material, prefer the sync workflow rather than manual
   copy-paste.

## Maintainer Notes

This repository is a public distribution surface, not just a scratch folder.
Avoid stale counts, hidden credential assumptions, and broad active-by-default
claims. Every public claim should be backed by a local validation command or
the current GitHub repository state.
