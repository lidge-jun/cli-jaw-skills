# wp5 — Runtime inventory and the one real duplicate

The audit refuted this phase's original premise before any change was made. Recorded
here because the correction is the result.

## What the 30 "duplicates" are

Verified on 2026-09-08: `~/.cli-jaw/skills` held 35 directory entries and **30
symlinks**. Every link resolves to its `jaw-` twin and every target holds a `SKILL.md`
(`links=30 all_resolve_to_jaw_twin=True`).

They are the deliberate compatibility layer for the `jaw-*` namespace migration.
`cli-jaw/lib/mcp/skills-migration.ts` documents both the reason and the safety:

> A customized `A-1.md` can contain a literal absolute path like
> `~/.cli-jaw/skills/search/SKILL.md`. That path is opened directly off the filesystem;
> it never passes through `resolveSkillId`.

> The link does not create a duplicate skill: every enumerator filters on
> `Dirent.isDirectory()`, which is false for a symlink (verified), so loadActiveSkills,
> the CLI listing, doctor, soft reset and the Electron bootstrap all skip it.

`resolveSkillId` in `skills-aliases.ts` maps legacy ids in code, and is called from
`src/prompt/builder.ts`, `src/routes/skills.ts` and `src/cli/commands.ts`. No agent was
loading two copies of anything. Deleting the links would have broken literal-path
references for one major version and been recreated by the next
`ensureCompatSymlinks` pass.

**Left intact.**

## The one real duplicate

`apple-calendar-reminders` was a real directory, not a link. `diff -r` against
`jaw-calendar-reminders` returned five lines: one differing file, `SKILL.md` line 2,
the frontmatter `name`. All 13 scripts and the references directory are byte-identical,
so nothing unique was lost.

Backed up to `~/.cli-jaw/backups/skills-conflicts/260908-readerdocs/` — the location and
convention `skills-migration.ts` already uses for legacy directories — with the file
count verified equal (15 = 15) before removal.

## After

| | before | after |
|---|---|---|
| real directories | 34 | 33 |
| compat symlinks | 30 | 30 |
| broken links | 0 | 0 |
| non-`jaw-` real directories | 1 | 0 |

Every remaining real skill carries the `jaw-` prefix, every legacy name still resolves
through its link, and no link is dangling.

