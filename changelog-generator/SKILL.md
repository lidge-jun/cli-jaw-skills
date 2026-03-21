---
name: changelog-generator
description: Generate user-facing changelogs from git commits. Categorizes changes, filters internal noise, and formats for customers.
---

# Changelog Generator

Generate user-facing changelogs from git commit history.

## Goal

Read git log for a given range, categorize commits, and produce a markdown changelog suitable for end users.

## Instructions

1. Determine the commit range (tag-to-tag, date range, or since-last-release)
2. Run `git log --oneline --no-merges` for the range
3. Categorize each commit and format output

## Categories

| Section | Commit types to include |
|---------|------------------------|
| New Features | `feat:`, new user-visible capabilities |
| Improvements | `perf:`, `refactor:` with user-visible effect, UX changes |
| Fixes | `fix:`, resolved bugs |
| Breaking Changes | commits with `BREAKING CHANGE` in body or `!` in type |
| Security | `security:`, dependency patches for CVEs |

## Exclusions

Do NOT include in the changelog:

- `chore:`, `ci:`, `build:` commits (internal tooling)
- Merge commits
- Commits touching only tests, docs, or CI config with no user-facing effect
- `[agent]` prefixed commits unless they contain a `feat:` or `fix:`

## Format

```markdown
# Changelog — {version or date range}

## New Features
- **{Feature name}**: {1-sentence user-facing description}

## Improvements
- **{Area}**: {What changed for the user}

## Fixes
- {What was broken and is now fixed}

## Breaking Changes
- **{What changed}**: {Migration action required}
```

- Use bold for the item label, plain text for description
- One bullet per commit (collapse related commits into one bullet)
- Omit empty sections

## Verification

Before finalizing:

1. Confirm every included commit maps to a real `git log` entry
2. Confirm no internal-only commits leaked through
3. If a `CHANGELOG_STYLE.md` exists in the repo, apply its conventions on top of these defaults
