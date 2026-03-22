---
name: team-builder
description: Interactive agent picker for composing and dispatching parallel teams from agent persona files.
---

# Team Builder

Interactive menu for browsing and composing agent teams on demand. Works with flat or domain-subdirectory agent collections.

## When to Use

- Multiple agent personas (markdown files) available and you want to pick which ones to use
- Composing an ad-hoc team from different domains (e.g., Security + SEO + Architecture)
- Browsing available agents before deciding

## Prerequisites

Agent files are markdown files containing a persona prompt (identity, rules, workflow, deliverables). The first `# Heading` is used as the agent name and the first paragraph as the description.

Both flat and subdirectory layouts are supported:

**Subdirectory layout** — domain inferred from folder name:
```
agents/
├── engineering/
│   ├── security-engineer.md
│   └── software-architect.md
├── marketing/
│   └── seo-specialist.md
└── sales/
    └── discovery-coach.md
```

**Flat layout** — domain inferred from shared filename prefixes (2+ files sharing a prefix = domain; unique prefixes → "General"). The algorithm splits at the first `-`, so multi-word domains should use the subdirectory layout.

## Configuration

Agent directories are probed in order and results merged:
1. `./agents/**/*.md` + `./agents/*.md` — project-local agents
2. Global agents directory — shared agents

Project-local agents take precedence over global agents with the same name.

## How It Works

### Step 1: Discover Available Agents

Glob agent directories. For each file:
- **Subdirectory layout:** extract domain from parent folder
- **Flat layout:** group by filename prefix (2+ shared = domain, unique = "General")
- Extract agent name from `# Heading` (fallback: filename → title-case)
- Extract one-line summary from first paragraph

If no agent files found, report which paths were checked and stop.

### Step 2: Present Domain Menu

```
Available agent domains:
1. Engineering — Software Architect, Security Engineer
2. Marketing — SEO Specialist
3. Sales — Discovery Coach, Outbound Strategist

Pick domains or name specific agents (e.g., "1,3" or "security + seo"):
```

### Step 3: Handle Selection

Accept flexible input:
- Numbers: "1,3" selects all agents from those domains
- Names: "security + seo" fuzzy-matches against discovered agents
- "all from engineering" selects every agent in that domain

If more than 5 agents selected, ask the user to narrow down (max 5 per team).

### Step 4: Spawn Agents in Parallel

1. Read each selected agent's markdown file
2. Prompt for task description if not already provided
3. Spawn all agents in parallel (general-purpose, independent — no inter-agent communication)
4. Note any failures inline and continue with successful results

### Step 5: Synthesize Results

Collect outputs and present a unified report:
- Results grouped by agent
- Synthesis: agreements, conflicts/tensions, recommended next steps

If only 1 agent selected, skip synthesis and present output directly.

## Rules

- **Dynamic discovery only.** New files in the directory auto-appear. No hardcoded agent lists.
- **Max 5 agents per team.** More produces diminishing returns. Enforce at selection time.
- **Parallel dispatch.** All agents run simultaneously via parallel tool calls for independent work.

## Example

```
User: team builder

Claude:
Available agent domains:
1. Engineering (2) — Software Architect, Security Engineer
2. Marketing (1) — SEO Specialist

Pick domains or name specific agents:

User: security + seo

Claude:
Selected: Security Engineer + SEO Specialist
What should they work on?

User: Review my Next.js e-commerce site before launch

[Both agents spawn in parallel]

Claude:
## Security Engineer Findings
- [findings...]

## SEO Specialist Findings
- [findings...]

## Synthesis
Both agree on: [...]
Tension: Security recommends CSP that blocks inline styles, SEO needs inline schema markup.
Next steps: [...]
```
