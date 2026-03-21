---
name: azure-verified-modules
description: Azure Verified Modules (AVM) requirements and best practices for developing certified Azure Terraform modules. Use when creating or reviewing Azure modules that need AVM certification.
---

# Azure Verified Modules (AVM) Requirements

References: [AVM Docs](https://azure.github.io/Azure-Verified-Modules/) | [Terraform Specs](https://azure.github.io/Azure-Verified-Modules/specs/terraform/)

---

## Module Cross-Referencing (TFFR1)

- Reference other AVM modules via HashiCorp registry with pinned version: `source = "Azure/xxx/azurerm"` + `version = "1.2.3"`
- Use only AVM modules — no git references (`git::`, `github.com/`)

---

## Azure Provider Requirements (TFFR3)

| Provider | Min Version | Max Version |
|----------|-------------|-------------|
| azapi    | >= 2.0      | < 3.0       |
| azurerm  | >= 4.0      | < 5.0       |

- Use `required_providers` block to enforce versions
- Prefer pessimistic version constraint (`~>`)

See [references/code-examples.md](references/code-examples.md) for provider configuration example.

---

## Code Style Standards

### Naming (TFNFR4)

Use `lower_snake_case` for all locals, variables, outputs, resource symbolic names, and module symbolic names.

### Resource Ordering (TFNFR6)

Place depended-on resources first. Keep resources with dependencies close to each other.

### Count & for_each (TFNFR7)

- Use `count` for conditional resource creation
- Use `map(xxx)` or `set(xxx)` as `for_each` collection with static literal keys

### Resource Block Internal Ordering (TFNFR8)

1. **Top meta-arguments:** `provider`, `count`, `for_each`
2. **Arguments/blocks (alphabetical):** required arguments → optional arguments → required nested blocks → optional nested blocks
3. **Bottom meta-arguments:** `depends_on`, `lifecycle` (sub-order: `create_before_destroy`, `ignore_changes`, `prevent_destroy`)

Separate sections with blank lines.

### Module Block Ordering (TFNFR9)

1. **Top:** `source`, `version`, `count`, `for_each`
2. **Arguments (alphabetical):** required → optional
3. **Bottom:** `depends_on`, `providers`

### Lifecycle ignore_changes (TFNFR10)

Use unquoted attributes: `ignore_changes = [tags]` (not `["tags"]`). Quoted strings cause silent failures.

### Conditional Creation (TFNFR11)

Wrap parameters requiring conditional creation with `object` type to avoid "known after apply" issues during plan.

### Dynamic Blocks (TFNFR12)

Use `for_each = <condition> ? [<item>] : []` pattern for optional nested blocks.

### Default Values (TFNFR13)

Prefer `coalesce()` or `try()` over ternary expressions for default values — shorter and more readable.

### Provider Declarations (TFNFR27)

- Declare `provider` blocks in modules only for `configuration_aliases`
- Provider configurations should be passed in by module users, because modules should remain provider-agnostic

---

## Variable Requirements

### Prohibited Variables (TFNFR14)

Avoid `enabled` or `module_depends_on` variables that control entire module operation. Feature toggles for specific resources are acceptable.

### Definition Order (TFNFR15)

1. Required fields (alphabetical)
2. Optional fields (alphabetical)

### Naming (TFNFR16)

Follow [HashiCorp naming rules](https://www.terraform.io/docs/extend/best-practices/naming.html). Use positive statements for feature switches: `xxx_enabled` instead of `xxx_disabled`.

### Descriptions (TFNFR17)

Write descriptions targeting module users (not developers). For `object` types, use HEREDOC format.

### Types (TFNFR18)

- Define `type` for every variable, as precise as possible
- Use `bool` for true/false values (not `string`/`number`)
- Use concrete `object` instead of `map(any)`
- Reserve `any` for adequately justified cases only

### Sensitive Data (TFNFR19)

For `object` variables with sensitive fields: either set `sensitive = true` on the entire variable, or extract sensitive fields into separate variables.

### Non-Nullable Collections (TFNFR20)

Set `nullable = false` for collection values (sets, maps, lists) used in loops, because null collections cause runtime errors in `for_each`.

### Nullability (TFNFR21)

Avoid `nullable = true` unless null carries specific semantic meaning.

### Sensitive Defaults (TFNFR22, TFNFR23)

- Omit `sensitive = false` (it is the default)
- Do not set default values for sensitive inputs (e.g., passwords)

### Deprecated Variables (TFNFR24)

- Move to `deprecated_variables.tf`
- Prefix description with `DEPRECATED` and declare the replacement name
- Clean up during major version releases

---

## Output Requirements

### Computed Outputs (TFFR2)

Output discrete computed attributes (anti-corruption layer pattern) rather than entire resource objects, because resource schemas change across provider versions.

- Avoid outputting values that are already inputs (except `name`)
- Use `sensitive = true` for sensitive attributes
- For `for_each` resources, output computed attributes in a map structure

### Sensitive Outputs (TFNFR29)

Mark outputs containing confidential data with `sensitive = true`.

### Deprecated Outputs (TFNFR30)

Move deprecated outputs to `deprecated_outputs.tf`. Define new outputs in `outputs.tf`. Clean up during major version releases.

---

## Local Values (TFNFR31–33)

- Keep `locals` blocks in `locals.tf` (advanced: declare next to related resources)
- Arrange expressions alphabetically
- Use precise types (e.g., `number` for age, not `string`)

---

## Terraform Configuration

### Version Requirements (TFNFR25)

`terraform.tf` requirements:
- Single `terraform` block, `required_version` on first line
- Include min and max major version constraints
- Prefer `~> #.#` or `>= #.#.#, < #.#.#` format

### Providers in required_providers (TFNFR26)

- Each provider specifies `source` (format: `namespace/name`) and `version`
- Providers sorted alphabetically
- Include only directly required providers
- Version includes min and max major version constraints

---

## Testing Requirements (TFNFR5, TFNFR36)

Required tools: `terraform validate/fmt/test`, terrafmt, Checkov, tflint (with azurerm ruleset), Go (optional).

Set `prevent_deletion_if_contains_resources = false` in test provider configs for clean teardown.

---

## Documentation (TFNFR2)

Generate docs via [terraform-docs](https://github.com/terraform-docs/terraform-docs). A `.terraform-docs.yml` file is required in the module root.

---

## Feature Toggles (TFNFR34)

New resources in minor/patch versions require a toggle variable defaulting to `false` to avoid unexpected resource creation.

---

## Breaking Changes (TFNFR35)

See [references/breaking-changes.md](references/breaking-changes.md) for the full list of patterns that constitute breaking changes in resource, variable, and output blocks.

---

## Contribution Standards (TFNFR3)

Set branch protection on the default branch: require PRs, approval, linear history, CODEOWNERS review. Prevent force pushes and branch deletion. No bypass for administrators.

---

## References

- [Code examples](references/code-examples.md) — HCL patterns for all requirements
- [Compliance checklist](references/compliance-checklist.md) — module review checklist
- [Breaking changes](references/breaking-changes.md) — detailed breaking change patterns
