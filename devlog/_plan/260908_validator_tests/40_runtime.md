# wp5 — Runtime skill aliases: verify, do not delete (diff-level, corrected)

The audit refuted this phase. The finding replaces the work.

## What the 30 "duplicates" actually are

`~/.cli-jaw/skills` holds 34 real directories and **30 symlinks**
(`browser -> jaw-browser`, `dev -> jaw-dev`, …). They are not a second copy of anything
and they are not drift. `cli-jaw/lib/mcp/skills-aliases.ts` and `skills-migration.ts`
document them as the compatibility layer for the `jaw-*` namespace migration:

- `resolveSkillId` maps every legacy id to its canonical `jaw-` id in code, and
  `src/prompt/builder.ts`, `src/routes/skills.ts` and `src/cli/commands.ts` all call it;
- `ensureCompatSymlinks` creates the links deliberately, because a customized `A-1.md`
  can hold a literal path like `~/.cli-jaw/skills/search/SKILL.md` that is opened off the
  filesystem and never passes through `resolveSkillId`;
- the module states that the link **does not create a duplicate skill**: every enumerator
  filters on `Dirent.isDirectory()`, which is false for a symlink, so `loadActiveSkills`,
  the CLI listing, doctor, soft reset and the Electron bootstrap all skip them.

So no agent is loading two copies of the same guidance. Deleting the 30 links would break
literal-path references for one major version and would be undone by the next
`ensureCompatSymlinks` pass anyway.

## The one real duplicate

`apple-calendar-reminders` is a **real directory**, not a link, and `diff -r` against
`jaw-calendar-reminders` shows exactly one differing line — the frontmatter `name`. It is
genuinely superseded and is the only true duplicate in the runtime, the inverse of the
original framing.

## What this phase does instead

1. Record the verified inventory: 34 real directories, 30 compat symlinks, one duplicate.
2. Resolve `apple-calendar-reminders`: back up the directory to
   `~/.cli-jaw/backups/skills-conflicts/` following the convention `skills-migration.ts`
   already uses for legacy directories, then remove it so the runtime keeps one copy.
   Its `scripts/` folder is checked for content `jaw-calendar-reminders` lacks before
   removal; if it carries anything unique, keep it and report instead.
3. Leave the 30 symlinks untouched and record why, so the next reader does not repeat
   this.

## Acceptance

- Inventory recorded in `evidence/` distinguishing directories from symlinks.
- `apple-calendar-reminders` resolved with a backup, or kept with a stated reason.
- The 30 compat symlinks still present and still resolving after the change.

