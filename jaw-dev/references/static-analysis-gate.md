# Static Analysis Gate — Toolchain Commands & Rule Mapping

Companion to `dev/SKILL.md` §7. Read when running the static-analysis part of the
verification gate or configuring lint/typecheck for a project.

## Per-Toolchain Gate Commands

| Toolchain      | Command                               | Must Pass                    |
| -------------- | ------------------------------------- | ---------------------------- |
| TypeScript     | `tsc --noEmit`                        | Zero errors                  |
| Python (typed) | `mypy .` or `pyright`                 | Zero errors on changed files |
| ESLint / Biome | `npx eslint .` or `npx biome check .` | Zero errors                  |
| Go             | `go vet ./...`                        | Zero issues                  |
| Rust           | `cargo clippy -- -D warnings`         | Zero warnings                |
| C#             | `dotnet build /warnaserror`           | Zero warnings                |

## Per-Language Type Annotation Rules

| Language   | Rule                                                                                |
| ---------- | ----------------------------------------------------------------------------------- |
| TypeScript | `strict: true` in tsconfig. Avoid implicit `any`; explicit `any` requires a line comment with justification. |
| Python     | Type hints on all function params and returns (`def fetch(url: str) -> Response:`). |
| Go         | Already enforced by compiler — ensure exported types have doc comments.             |
| C# / Java  | Use nullability annotations (`?`, `@Nullable`). Avoid raw `Object` or `dynamic`.    |
| General    | If the language supports a strict/pedantic mode, enable it.                         |

## Common Rule ↔ Prose Mapping

| Anti-Pattern (prose) | ESLint / Biome Rule |
|---|---|
| Unused variable/import | `no-unused-vars`, `@typescript-eslint/no-unused-vars` |
| Unsafe `any` type | `@typescript-eslint/no-explicit-any` |
| Loose equality (`==`) | `eqeqeq` |
| Circular import | `import/no-cycle` (ESLint), `noBarrelFile`/`useImportRestrictions` (Biome) |
| Unhandled async | `@typescript-eslint/no-floating-promises` |
| `var` usage | `no-var`, `prefer-const` |
| Complex function | `complexity`, `max-depth`, `max-lines-per-function` |

This table is not exhaustive — the project's own config is the canonical rule set.

## New-File Language Default

For new JavaScript/TypeScript source files, prefer TypeScript:

- Use `.ts` for logic and `.tsx` for typed UI components when the project already supports
  TypeScript or is greenfield JS/TS.
- Use `.js`/`.jsx` only when the repo is clearly JS-only, build or runtime constraints
  require JS, or the user asks for JS.
- Do not introduce TypeScript tooling, convert existing JS, or change `tsconfig` without
  user approval. Migrating a language is a decision with a cost the user is paying.

New TypeScript is strict-compatible from the first patch, not after a cleanup pass:

- No implicit `any`.
- Explicit `any` requires a nearby justification comment.
- Prefer `unknown` plus narrowing over `any`.
- Type exported function parameters and return values.
- Handle null and undefined deliberately.
- Avoid code that only passes because `strict` is disabled — it becomes someone else's
  failure the moment the flag is turned on.

Verification: run the project's configured typecheck when available. If TypeScript is
present but no typecheck script exists, use the closest safe equivalent (`tsc --noEmit`).
If strict compatibility cannot be verified, say so rather than implying it was checked.

## Escape Hatches

When bypassing the type system is unavoidable:

- Add a comment explaining why the escape is needed — not what it does.
- Scope it minimally: cast at the narrowest point, not the broadest.
- Prefer assertion functions over raw casts (`assertIsString(x)` over `x as string`).
- A double cast through `unknown` requires a linked issue or TODO. It defeats the checker
  entirely, so it should be traceable to a reason that can expire.
- A blanket type-checker suppression must name the specific error code it suppresses, so
  it stops applying when that error stops being the one that occurs.

## Sources

| Claim | Source | Checked |
|---|---|---|
| Biome barrel-file rule exists (`noBarrelFile`) | https://biomejs.dev/linter/rules/no-barrel-file/ | 2026-07-02 |
| ponytail necessity-gate discipline (DEV-NECESSITY-01 source) | https://github.com/DietrichGebert/ponytail | 2026-07-02 |
