# Static Analysis Reference

Extracted from `dev` section 7.2 to keep `SKILL.md` under the repository's 500-line
limit. The gate commands, thresholds and escape-hatch rules stay in `dev/SKILL.md`;
this file holds the illustrative mapping only.

## Common Rule ↔ Prose Mapping

| Anti-Pattern (prose) | ESLint / Biome Rule |
|---|---|
| Unused variable/import | `no-unused-vars`, `@typescript-eslint/no-unused-vars` |
| Unsafe `any` type | `@typescript-eslint/no-explicit-any` |
| Loose equality (`==`) | `eqeqeq` |
| Circular import | `import/no-cycle` |
| Unhandled async | `@typescript-eslint/no-floating-promises` |
| `var` usage | `no-var`, `prefer-const` |
| Complex function | `complexity`, `max-depth`, `max-lines-per-function` |

This table is not exhaustive — check project config for the canonical set.
