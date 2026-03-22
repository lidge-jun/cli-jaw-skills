---
name: agent-setup-wizard
description: Interactive installer for agent skills and rules across any AI coding agent framework. Guides users through selecting and installing skills and rules to user-level or project-level directories, verifies paths, and optionally optimizes installed files.
---

# Agent Setup Wizard

An interactive, step-by-step installation wizard for skill and rule libraries. Guides users through selective installation of skills and rules, verifies correctness, and offers optimization.

## When to Activate

- User says "setup skills", "install skills", "configure agent", or similar
- User wants to selectively install skills or rules from a skill library
- User wants to verify or fix an existing skills installation
- User wants to optimize installed skills or rules for their project

## Step 1: Identify Source Repository

Ask the user for the source repository containing skills and rules:

```
Question: "Where is the skill/rule library located?"
Options:
  - "Git URL" — "Clone from a remote repository"
  - "Local path" — "Use a local directory"
```

If a git URL is provided, clone to a temporary directory and set `SOURCE_ROOT` to that path. If a local path is provided, set `SOURCE_ROOT` directly.

## Step 2: Choose Installation Level

Ask the user where to install:

```
Question: "Where should components be installed?"
Options:
  - "User-level" — "Applies to all projects (e.g., ~/.config/agent/)"
  - "Project-level" — "Applies only to the current project (e.g., .agents/)"
  - "Both" — "Shared items user-level, project-specific items project-level"
```

Store the choice as `INSTALL_LEVEL`. Set the target directory based on the agent framework in use. Create the target directories if they don't exist:

```bash
mkdir -p $TARGET/skills $TARGET/rules
```

## Step 3: Discover and Select Skills

### 3a: Scan Available Skills

Scan `$SOURCE_ROOT` for directories containing `SKILL.md` files. Group by category if the source uses a category structure, otherwise list them flat.

### 3b: Choose Skills

Present the discovered skills to the user for selection. For large catalogs (more than 10 skills), organize by category and offer batch selection:

```
Question: "Which skills do you want to install?"
Options:
  - "All skills" — "Install everything"
  - "Select by category" — "Choose categories, then refine"
  - "Pick individually" — "Select specific skills from the full list"
```

### 3c: Execute Installation

For each selected skill, copy the entire skill directory (not just SKILL.md — some skills include config files, scripts, or reference documents):

```bash
cp -r $SOURCE_ROOT/skills/<skill-name> $TARGET/skills/
```

## Step 4: Discover and Select Rules

Scan `$SOURCE_ROOT` for rule files (typically `.md` files in a `rules/` directory). Present them for selection using the same pattern as skills.

Execute installation:
```bash
cp -r $SOURCE_ROOT/rules/<selected>/* $TARGET/rules/
```

If the source organizes rules into base and extension sets, warn when extensions are selected without their base.

## Step 5: Post-Installation Verification

### 5a: Verify File Existence

Confirm all selected files exist at the target location.

### 5b: Check Path References

Scan installed `.md` files for hardcoded paths that may not match the installation target. Flag:
- References to paths outside the installation target
- Cross-references to skills that were not installed
- Framework-specific paths that don't match the user's agent framework

### 5c: Report Issues

For each issue found, report:
1. **File**: The file containing the problematic reference
2. **Line**: The line number
3. **Issue**: What's wrong
4. **Suggested fix**: What to do

## Step 6: Optimize Installed Files (Optional)

Ask the user whether to tailor the installed files:

```
Question: "Optimize the installed files for your project?"
Options:
  - "Optimize skills" — "Remove irrelevant sections, adjust paths, tailor to your tech stack"
  - "Optimize rules" — "Adjust targets, add project-specific patterns"
  - "Optimize both"
  - "Skip" — "Keep everything as-is"
```

If optimizing:
1. Ask the user about their tech stack and preferences
2. Edit files in-place at the installation target only
3. Fix any path issues found in Step 5

## Step 7: Summary

Clean up any temporary directories (e.g., cloned repos in `/tmp`).

Print a summary:

```
## Installation Complete

### Target
- Level: [user-level / project-level / both]
- Path: [target path]

### Skills Installed ([count])
- skill-1, skill-2, ...

### Rules Installed ([count])
- [list]

### Verification
- [count] issues found, [count] fixed
- [remaining issues if any]

### Optimizations
- [changes made, or "None"]
```

## Troubleshooting

### Skills not being picked up
- Verify the skill directory contains a `SKILL.md` file (not just loose .md files)
- Check that the target path matches your agent's expected skills directory
- Restart the agent after installing new skills

### Rules not applying
- Rules are typically flat files in the rules directory; avoid nesting under subdirectories unless the agent framework expects it
- Restart the agent after installing rules

### Path reference errors after project-level install
- Some skills may contain hardcoded user-level paths. Run the verification step to find and fix these.
