# wp4 — Registry and skill-list normalization (diff-level, corrected)

The audit refuted this phase's original premise. Recorded here because the correction is
the finding: **the six "orphans" are real skills and the detector is what is broken.**

## What the six entries actually are

`differential-review`, `insecure-defaults`, `modern-python`, `property-based-testing`,
`static-analysis`, `terraform` are multi-skill plugin bundles whose `SKILL.md` sits at a
nested path, and every one of them already carries a correct `entry` key that resolves:

| entry key | resolves |
|---|---|
| `differential-review/skills/differential-review/SKILL.md` | yes |
| `insecure-defaults/skills/insecure-defaults/SKILL.md` | yes |
| `modern-python/skills/modern-python/SKILL.md` | yes |
| `property-based-testing/skills/property-based-testing/SKILL.md` | yes |
| `static-analysis/skills/codeql/SKILL.md` | yes |
| `terraform/code-generation/skills/azure-verified-modules/SKILL.md` | yes |

They were added in `78cb936`, are tracked by git, and deleting their registry entries
would de-register six working skills. The original plan's claim that "no deletion commit
exists … they were registered but never added" was wrong.

The defect is in `validate_public_surface.py`: the inventory globs `*/SKILL.md` only, so a
bundle whose skill lives one level down is invisible to it, while `validate_registry()`
already honors `entry`. Two functions in the same file disagree about what a skill is.

## MODIFY the inventory, not the data

Give the validator one skill-discovery function used by every check:

- a directory is a skill when it holds `SKILL.md` **or** when a registry entry names an
  `entry` path inside it that exists;
- the inventory records the resolved `SKILL.md` path per skill, so the frontmatter,
  name-match and line-cap checks read the right file for bundles too;
- registry correspondence then compares like with like, and the six stop being reported.

## pptx_original and xlsx_original

Keep them **unregistered**. Their frontmatter declares `license: Proprietary. LICENSE.txt
has complete terms` and no `LICENSE.txt` is present in the directory. Registering them
would publish proprietary upstream content into an installable catalogue. They are
recorded in an explicit `VENDORED_UNREGISTERED` list in the validator with that reason in
a comment, so the exclusion is visible rather than silent — the objection the earlier
draft raised against exclusion is answered by naming them in code.

## NEW tests/registry/test_registry.py

- every discovered skill (including `entry`-based bundles) appears in `registry.json`;
- every registry entry resolves to an existing `SKILL.md`;
- entry keys match their directory name; no duplicate names;
- the vendored-unregistered list is exactly the set of unregistered skill directories, so
  adding a new unregistered directory fails until it is registered or listed.

## Acceptance

- No registry entry is deleted; the six bundles remain registered and now validate.
- The correspondence test fails when an entry's `entry` path is broken — demonstrated at
  C with a temporary edit.

