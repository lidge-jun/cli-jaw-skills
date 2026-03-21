# Skills Reference

CLI-JAW's skill system — 118 skills across 9 categories.

**23 active** (auto-injected into every AI prompt) · **95 reference** (loaded on demand)

---

## Where Skills Are Registered

| Location                                      | Purpose                                                                | Format                        |
| --------------------------------------------- | ---------------------------------------------------------------------- | ----------------------------- |
| `skills_ref/registry.json`                    | **Master registry** — metadata for all skills                          | JSON object keyed by skill ID |
| `skills_ref/<id>/SKILL.md`                    | **Skill definition** — instructions the AI reads                       | Markdown                      |
| `lib/mcp-sync.ts` → `OPENCLAW_ACTIVE`         | **Auto-activate list** — skills promoted to active on install/reset    | TypeScript `Set`              |
| `lib/mcp-sync.ts` → `CODEX_ACTIVE`            | **Codex-origin active** — skills sourced from `~/.codex/skills/`       | TypeScript `Set`              |
| `registry.json` → `category: "orchestration"` | **Auto-activate by category** — orchestration skills are always active | JSON field                    |

### Runtime Directories

| Directory                | Purpose                                                                 |
| ------------------------ | ----------------------------------------------------------------------- |
| `~/.cli-jaw/skills/`     | **Active skills** — injected into system prompt                         |
| `~/.cli-jaw/skills_ref/` | **Reference skills** — AI reads on demand via `cli-jaw skill read <id>` |

---

## How to Add a New Skill

### 1. Create the skill directory

```
skills_ref/<your-skill-id>/
├── SKILL.md          ← required (AI reads this)
├── scripts/          ← optional (helper scripts)
└── ...               ← optional (templates, configs)
```

### 2. Write `SKILL.md`

Follow the format in `skills_ref/skill-creator/SKILL.md` for guidance. Key sections:

```markdown
# Skill Name

One-line description. Triggers: "keyword1", "keyword2".
Covers: what it does. Do NOT use for: what it doesn't do.

---

## Quick Reference
(table of commands)

## Detailed Usage
(step-by-step instructions)

## Rules
(DO / DON'T lists)
```

### 3. Register in `registry.json`

Add an entry to `skills_ref/registry.json` → `skills` object:

```json
{
  "skills": {
    "your-skill-id": {
      "name": "Display Name",
      "name_ko": "한국어 이름",
      "name_en": "English Name",
      "emoji": "🔧",
      "category": "devtools",
      "description": "Primary description (Korean or English)",
      "desc_ko": "한국어 설명",
      "desc_en": "English description",
      "requires": {
        "bins": ["required-cli-tool"],
        "env": ["REQUIRED_API_KEY"]
      },
      "install": "npm install -g something",
      "version": "1.0.0"
    }
  }
}
```

#### Required fields

| Field         | Type   | Description                                                                                                                     |
| ------------- | ------ | ------------------------------------------------------------------------------------------------------------------------------- |
| `name`        | string | Display name                                                                                                                    |
| `emoji`       | string | Single emoji                                                                                                                    |
| `category`    | string | One of: `automation`, `ai-media`, `communication`, `devtools`, `media`, `orchestration`, `productivity`, `smarthome`, `utility` |
| `description` | string | Short description                                                                                                               |
| `version`     | semver | Skill version (e.g. `"1.0.0"`)                                                                                                  |

#### Optional fields

| Field                 | Type     | Description                      |
| --------------------- | -------- | -------------------------------- |
| `name_ko` / `name_en` | string   | Localized names                  |
| `desc_ko` / `desc_en` | string   | Localized descriptions           |
| `requires.bins`       | string[] | Required CLI binaries            |
| `requires.env`        | string[] | Required environment variables   |
| `install`             | string   | Install command for dependencies |

### 4. Make it auto-active (optional)

To promote a skill to **always active** (injected into every prompt), pick one:

**Option A — Add to `OPENCLAW_ACTIVE`** (most skills):

```typescript
// lib/mcp-sync.ts
const OPENCLAW_ACTIVE = new Set([
    'browser', 'notion', 'memory', /* ... */ 'your-skill-id',
]);
```

**Option B — Set `category: "orchestration"`** in registry.json:

Orchestration-category skills are auto-activated by the registry scanner at install/reset time. Use this for dev-guide skills that all agents need.

### 5. Verify

```bash
# Hard reset to test fresh install behavior
jaw skill reset --hard

# Check active count
jaw doctor

# Check if your skill appears
jaw skill list
```

---

## Skill Reset Behavior

| Command                  | What it does                                                                                          |
| ------------------------ | ----------------------------------------------------------------------------------------------------- |
| `jaw skill reset`        | **Soft reset** — restores registered skills to bundled defaults, preserves custom/unregistered skills |
| `jaw skill reset --hard` | **Hard reset** — deletes everything, re-copies from bundle, re-activates defaults                     |

After reset, auto-active skills = `CODEX_ACTIVE` ∪ `OPENCLAW_ACTIVE` ∪ `category:orchestration` = **23 skills**.

---

## Categories

### orchestration (10) — *auto-active*

| Skill               |     | Description                                                                     | Version |
| ------------------- | --- | ------------------------------------------------------------------------------- | ------- |
| `dev`               | 🔧   | Common development guide. Modular dev, self-reference patterns, changelog.      | 1.1.0   |
| `dev-backend`       | ⚙️   | Backend role guide. API design, architecture patterns, database optimization.   | 1.1.0   |
| `dev-code-reviewer` | 🔍   | Code review guide. Pre-scan, quality thresholds, security/perf quick-checks.    | 1.1.0   |
| `dev-data`          | 📊   | Data role guide. ETL pipelines, dbt, data quality, streaming decisions.          | 1.1.0   |
| `dev-debugging`     | 🐛   | Systematic debugging. Root cause analysis, boundary instrumentation, postmortem. | 1.0.0   |
| `dev-frontend`      | 🎨   | Frontend role guide. Unique UI/UX, component design, aesthetic standards.       | 1.0.0   |
| `dev-pabcd`         | 🎯   | PABCD orchestration workflow with human checkpoints between phases.             | 2.0.0   |
| `dev-scaffolding`   | 🏗️   | Project scaffolding following the Lidge Standard.                               | 1.0.0   |
| `dev-security`      | 🛡️   | Security hardening. OWASP Top 10, auth, validation, secrets, supply chain.      | 1.0.0   |
| `dev-testing`       | 🧪   | Testing guide. Strategy selection, backend/API harnesses, Playwright, CI gates. | 1.1.0   |

### automation (3) — `browser`, `vision-click` are auto-active

| Skill          |     | Description                                                      | Version |
| -------------- | --- | ---------------------------------------------------------------- | ------- |
| `browser`      | 🌐   | Chrome automation — snapshot, click, navigate, screenshot.       | 1.0.0   |
| `vision-click` | 👁️   | Vision-based coordinate clicking. Screenshot → AI → pixel click. | 1.0.0   |
| `web-routing`  | 🧭   | Routing guide for browser requests.                              | 1.0.0   |

### media (1) — `video` is auto-active

| Skill   |     | Description                                           | Version |
| ------- | --- | ----------------------------------------------------- | ------- |
| `video` | 🎬   | JSON-driven video generation pipeline using Remotion. | 0.1.0   |

### ai-media (13)

| Skill                        |     | Description                                               | Version |
| ---------------------------- | --- | --------------------------------------------------------- | ------- |
| `algorithmic-art`            | 🎨   | p5.js generative art. Algorithm-based visual artwork.     | 1.0.0   |
| `atlas`                      | 🌍   | Control ChatGPT Atlas app (macOS).                        | 1.0.0   |
| `canvas-design`              | 🖼️   | Create PNG/PDF visual designs via Canvas API.             | 1.0.0   |
| `fal-image-edit`             | ✏️   | fal.ai AI image editing (style transfer, object removal). | 1.0.0   |
| `hugging-face-cli`           | 🤗   | HF Hub CLI for model/dataset/space management.            | 1.0.0   |
| `hugging-face-evaluation`    | 📊   | vLLM/lighteval model evaluation and benchmarks.           | 1.0.0   |
| `hugging-face-model-trainer` | 🏋️   | TRL: SFT/DPO/GRPO model training.                         | 1.0.0   |
| `imagegen`                   | 🖼️   | Generate/edit images via OpenAI Images API.               | 1.0.0   |
| `nano-banana-pro`            | 🖼️   | Generate/edit images with Gemini 3 Pro.                   | 1.0.0   |
| `sora`                       | 🎥   | Sora video generation. OpenAI API.                        | 1.0.0   |
| `speech`                     | 🗣️   | OpenAI TTS voice synthesis.                               | 1.0.0   |
| `theme-factory`              | 🎭   | Reusable themes for document/slide/HTML outputs.          | 1.0.0   |
| `transcribe`                 | 🎤   | Whisper speech-to-text + speaker diarization.             | 1.0.0   |

### communication (6) — `telegram-send` is auto-active

| Skill                |     | Description                                       | Version |
| -------------------- | --- | ------------------------------------------------- | ------- |
| `email-draft-polish` | ✉️   | Email draft tone adjustment/formatting.           | 1.0.0   |
| `gog`                | 🌐   | Gmail, Calendar, Drive, Sheets, Docs integration. | 1.0.0   |
| `himalaya`           | 📧   | Terminal email read/write/reply/search.           | 1.0.0   |
| `telegram-send`      | 📨   | Send voice/photo/document via Telegram.           | 1.0.0   |
| `whatsapp`           | 💬   | WhatsApp message automation.                      | 1.0.0   |
| `xurl`               | 🐦   | Tweet post/search/reply/DM/media upload.          | 1.0.0   |

### devtools (55) — `github`, `openai-docs` are auto-active via `OPENCLAW_ACTIVE`

| Skill                         |     | Description                                                | Version |
| ----------------------------- | --- | ---------------------------------------------------------- | ------- |
| `agents-sdk`                  | 🤖   | Cloudflare Workers AI Agents SDK.                          | 1.0.0   |
| `api-design-reviewer`         | 📐   | REST API design review.                                    | 1.0.0   |
| `apple-hig-skills`            | 🍎   | Apple HIG 14 guides.                                       | 1.0.0   |
| `aws-skills`                  | ☁️   | AWS infrastructure automation (CDK/CloudFormation/Lambda). | 1.0.0   |
| `brainstorming`               | 💡   | Pre-coding idea refinement → design document.              | 1.0.0   |
| `changelog-generator`         | 📰   | git commit → changelog/release notes.                      | 1.0.0   |
| `cloudflare-deploy`           | ☁️   | Deploy to Cloudflare Workers/Pages.                        | 1.0.0   |
| `codebase-orientation`        | 🗺️   | Project entrypoint/module/build mapping.                   | 1.0.0   |
| `config-file-explainer`       | ⚙️   | Config file structure/keys/defaults explanation.           | 1.0.0   |
| `context-compression`         | 🗜️   | Context compression for long sessions.                     | 1.0.0   |
| `data-structure-chooser`      | 🏗️   | Data structure tradeoff recommendations.                   | 1.0.0   |
| `database-designer`           | 🗃️   | Schema design, normalization, index optimization.          | 1.0.0   |
| `debugging-checklist`         | ✅   | Reproduce → isolate → log → verify debugging.              | 1.0.0   |
| `debugging-helpers`           | 🐛   | Systematic debugging helpers.                              | 1.0.0   |
| `deep-research`               | 🔬   | Multi-step research: search → analyze → summarize.         | 1.0.0   |
| `dependency-install-helper`   | 📦   | Platform-specific dependency installation.                 | 1.0.0   |
| `develop-web-game`            | 🎮   | Web game development + Playwright test loop.               | 1.0.0   |
| `differential-review`         | 🔎   | Security-focused diff review.                              | 1.0.0   |
| `dispatching-parallel-agents` | 🔀   | Parallel sub-agent dispatch patterns.                      | 1.0.0   |
| `durable-objects`             | 💾   | Cloudflare Durable Objects (RPC+SQLite+WebSocket).         | 1.0.0   |
| `error-message-explainer`     | 💬   | Error → cause + fix suggestions.                           | 1.0.0   |
| `figma-implement-design`      | 🎨   | Figma designs to 1:1 code.                                 | 1.0.0   |
| `git-worktrees`               | 🌲   | git worktree-based branch workflow.                        | 1.0.0   |
| `github`                      | 🐙   | GitHub gh CLI: issues, PRs, CI, code review.               | 1.0.0   |
| `insecure-defaults`           | 🔒   | Detect hardcoded secrets, weak crypto.                     | 1.0.0   |
| `ios-simulator`               | 📱   | iOS Simulator control.                                     | 1.0.0   |
| `jupyter-notebook`            | 📓   | .ipynb create/edit.                                        | 1.0.0   |
| `linter-fix-guide`            | 🧹   | Lint rule explanation + minimal fix.                       | 1.0.0   |
| `log-summarizer`              | 📄   | Log grouping + first failure ID.                           | 1.0.0   |
| `mcp-builder`                 | 🔌   | Design/implement MCP servers.                              | 1.0.0   |
| `modern-python`               | 🐍   | uv+ruff+ty+pytest Python best practices.                   | 1.0.0   |
| `netlify-deploy`              | 🔺   | Deploy Netlify sites.                                      | 1.0.0   |
| `openai-docs`                 | 📖   | OpenAI product/API official docs.                          | 1.0.0   |
| `postgres`                    | 🐘   | PostgreSQL read-only queries.                              | 1.0.0   |
| `property-based-testing`      | 🧪   | Multi-language property-based testing.                     | 1.0.0   |
| `react-best-practices`        | ⚛️   | React patterns, performance, component design.             | 1.0.0   |
| `receiving-code-review`       | 📩   | Code review feedback reception.                            | 1.0.0   |
| `render-deploy`               | 🚀   | Deploy Render services.                                    | 1.0.0   |
| `requesting-code-review`      | 📝   | Internal agent code review.                                | 1.0.0   |
| `security-best-practices`     | 🛡️   | Language-specific security review.                         | 1.0.0   |
| `security-ownership-map`      | 👥   | Codebase owner/bus-factor mapping.                         | 1.0.0   |
| `security-threat-model`       | ⚠️   | Per-repo threat model (STRIDE/DREAD).                      | 1.0.0   |
| `senior-architect`            | 🏛️   | ADR, pattern selection, dependency analysis.               | 1.0.0   |
| `sentry`                      | 🐛   | Sentry issue/event lookup.                                 | 1.0.0   |
| `skill-creator`               | 🏗️   | Auto-generate new SKILL.md.                                | 1.0.0   |
| `static-analysis`             | 🔍   | CodeQL+Semgrep+SARIF static analysis.                      | 1.0.0   |
| `tdd`                         | 🔴   | RED-GREEN-REFACTOR TDD cycle.                              | 1.0.0   |
| `terraform`                   | 🏗️   | HashiCorp Terraform IaC.                                   | 1.0.0   |
| `tmux`                        | 🧵   | tmux session remote control.                               | 1.0.0   |
| `ui-design-system`            | 🎨   | Design tokens, color palettes, typography.                 | 1.0.0   |
| `ux-researcher`               | 🔬   | User personas, journey mapping, usability testing.         | 1.0.0   |
| `vercel-deploy`               | ▲   | Vercel project deployment.                                 | 1.0.0   |
| `web-artifacts-builder`       | 🧱   | React/Tailwind web artifact creation.                      | 1.0.0   |
| `web-perf`                    | ⚡   | Core Web Vitals audit via Lighthouse.                      | 1.0.0   |
| `writing-plans`               | 📋   | Task decomposition with file paths/code.                   | 1.0.0   |

### productivity (16) — `docx`, `hwp`, `notion`, `pptx`, `xlsx` are auto-active

| Skill                           |     | Description                                      | Version |
| ------------------------------- | --- | ------------------------------------------------ | ------- |
| `apple-notes`                   | 🍎   | Apple Notes create/search (AppleScript).         | 1.0.0   |
| `apple-reminders`               | 🔔   | Apple Reminders add/complete/list (AppleScript). | 1.0.0   |
| `doc-coauthoring`               | ✍️   | Document co-authoring workflow.                  | 1.0.0   |
| `docx`                          | 📄   | .docx create/edit/read + visual verification.    | 1.0.0   |
| `html2pptx`                     | 🔄   | HTML slides → native PowerPoint.                 | 1.0.0   |
| `hwp`                           | 🇰🇷   | HWP/HWPX document create/read/edit/convert.      | 1.0.0   |
| `linear`                        | 📐   | Linear issue/project/cycle management.           | 1.0.0   |
| `notion`                        | 📝   | Notion page/DB CRUD via curl API.                | 1.0.0   |
| `notion-knowledge-capture`      | 📚   | Conversation → Notion wiki/FAQ/HOW-TO.           | 1.0.0   |
| `notion-meeting-intelligence`   | 📊   | Meeting prep (per-attendee context, agenda).     | 1.0.0   |
| `notion-research-documentation` | 🔬   | Multi-source → Notion report synthesis.          | 1.0.0   |
| `notion-spec-to-implementation` | 📋   | PRD/spec → implementation plan + tasks.          | 1.0.0   |
| `obsidian`                      | 🗃️   | Obsidian vault note management.                  | 1.0.0   |
| `pptx`                          | 📽️   | .pptx create/edit/analyze.                       | 1.0.0   |
| `things-mac`                    | ✅   | Things 3 todo management (AppleScript).          | 1.0.0   |
| `trello`                        | 📋   | Trello board/list/card management.               | 1.0.0   |

### smarthome (2)

| Skill            |     | Description                         | Version |
| ---------------- | --- | ----------------------------------- | ------- |
| `openhue`        | 💡   | Hue light/scene control.            | 1.0.0   |
| `spotify-player` | 🎵   | Spotify play/pause/search/playlist. | 1.0.0   |

### utility (12) — `memory`, `pdf`, `pdf-vision`, `screen-capture` are auto-active

| Skill              |     | Description                                    | Version |
| ------------------ | --- | ---------------------------------------------- | ------- |
| `1password`        | 🔐   | 1Password CLI for password/OTP lookup.         | 1.0.0   |
| `goplaces`         | 📍   | Google Places API search.                      | 1.0.0   |
| `memory`           | 🧠   | Long-term memory across sessions.              | 1.0.0   |
| `pdf`              | 📄   | PDF read/create/edit/review.                   | 1.0.0   |
| `pdf-vision`       | 📄   | Hybrid PDF: image rendering + text extraction. | 1.0.0   |
| `screen-capture`   | 📸   | macOS screenshot/webcam/recording.             | 1.0.0   |
| `summarize`        | 📑   | Summarize URLs, YouTube, files to text.        | 1.0.0   |
| `tts`              | 🔊   | macOS `say` command text-to-speech.            | 1.0.0   |
| `video-downloader` | 🎬   | yt-dlp wrapper for media download.             | 1.0.0   |
| `video-frames`     | 🎬   | Extract video frames/segments (ffmpeg).        | 1.0.0   |
| `weather`          | 🌤️   | wttr.in weather/forecast lookup.               | 1.0.0   |
| `xlsx`             | 📊   | .xlsx/.csv/.tsv create/edit/analyze.           | 1.0.0   |

---

## Quick Commands

```bash
jaw skill list                  # List all active + reference skills
jaw skill install <id>          # Promote a reference skill to active
jaw skill uninstall <id>        # Demote an active skill to reference
jaw skill read <id>             # Print SKILL.md contents
jaw skill reset                 # Soft reset (restore registered, keep custom)
jaw skill reset --hard          # Hard reset (delete all, re-copy from bundle)
```
