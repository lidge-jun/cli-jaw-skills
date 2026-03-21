---
name: skill-creator
description: Create or update AgentSkills. Use when designing, structuring, or packaging skills with scripts, references, and assets.
---

# Skill Creator

## Skill Anatomy

```
skill-name/
├── SKILL.md (required)
│   ├── YAML frontmatter: name + description (required)
│   └── Markdown body: instructions (required)
└── Bundled Resources (optional)
    ├── scripts/       - Executable code for deterministic/repetitive tasks
    ├── references/    - Documentation loaded into context as needed
    └── assets/        - Files used in output (templates, icons, fonts)
```

Only include files that directly support the skill's function. No README, CHANGELOG, or auxiliary docs.

## Core Principles

### Economy of Context

The context window is shared with system prompt, conversation, other skills, and the user request. Only add knowledge the model lacks. Prefer concise examples over verbose explanations. Challenge each piece: "Does this justify its token cost?"

### Degrees of Freedom

Match specificity to task fragility:

- **High freedom** (text instructions): multiple valid approaches, context-dependent decisions
- **Medium freedom** (pseudocode/parameterized scripts): preferred pattern exists, some variation okay
- **Low freedom** (exact scripts, few params): fragile operations, consistency critical

### Progressive Disclosure

Three loading levels manage context efficiently:

1. **Metadata** (name + description) — always in context (~100 words)
2. **SKILL.md body** — loaded when skill triggers (target ≤500 lines)
3. **Bundled resources** — loaded as needed

When approaching 500 lines, split into reference files. Reference them from SKILL.md with clear descriptions of when to read each one.

Organize references by domain or variant so only relevant context loads:

```
cloud-deploy/
├── SKILL.md (workflow + provider selection)
└── references/
    ├── aws.md
    ├── gcp.md
    └── azure.md
```

Keep references one level deep from SKILL.md. For files >100 lines, include a table of contents.

## Resource Guidelines

### Scripts (`scripts/`)

Include when the same code would be rewritten repeatedly or deterministic reliability matters. Test scripts by running them before packaging.

### References (`references/`)

Store detailed schemas, API docs, and domain knowledge here — not in SKILL.md. Information lives in either SKILL.md or references, not both. For large files (>10k words), include grep patterns in SKILL.md.

### Assets (`assets/`)

Files used in output (templates, images, boilerplate). Not loaded into context — copied or modified during execution.

## Creation Process

### 1. Understand Usage

Gather concrete examples of how the skill will be used:
- What functionality should it support?
- What would users say to trigger it?
- Example queries and expected outcomes

Ask focused questions iteratively.

### 2. Plan Resources

For each example, identify:
1. What would you do from scratch?
2. What scripts, references, or assets would help when doing it repeatedly?

### 3. Initialize

Run `init_skill.py` for new skills (skip if iterating on an existing skill):

```bash
scripts/init_skill.py <skill-name> --path <output-directory> [--resources scripts,references,assets] [--examples]
```

### 4. Implement

Start with reusable resources, then write SKILL.md.

#### Naming

- Lowercase, digits, hyphens only. Under 64 characters.
- Short, verb-led phrases describing the action.
- Namespace by tool when it improves clarity (e.g., `gh-address-comments`).

#### Frontmatter

```yaml
name: skill-name
description: >
  What the skill does + when to use it. This is the primary trigger mechanism.
  Include all "when to use" info here — the body loads only after triggering.
```

No other frontmatter fields.

#### Body

Write imperative instructions for using the skill and its resources.

Design pattern guides:
- **Multi-step processes**: `references/workflows.md`
- **Output formats/quality standards**: `references/output-patterns.md`

#### Script Testing

Test added scripts by running them. For many similar scripts, test a representative sample.

### 5. Package

```bash
scripts/package_skill.py <path/to/skill-folder> [output-directory]
```

Validates (frontmatter, naming, structure, description quality) then creates a `.skill` file (zip format). Symlinks are rejected. Fix validation errors and re-run.

### 6. Iterate

After real usage: note struggles or inefficiencies → update SKILL.md or resources → test again.
