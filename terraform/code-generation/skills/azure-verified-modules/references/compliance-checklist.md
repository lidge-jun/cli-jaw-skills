# AVM Compliance Checklist

Use this checklist when developing or reviewing Azure Verified Modules.

## Module Structure
- [ ] Module cross-references use registry sources with pinned versions
- [ ] Azure providers (azurerm/azapi) versions meet AVM requirements
- [ ] `.terraform-docs.yml` present in module root
- [ ] CODEOWNERS file present

## Code Style
- [ ] All names use lower snake_casing
- [ ] Resources ordered with dependencies first
- [ ] `for_each` uses `map()` or `set()` with static keys
- [ ] Resource/data/module blocks follow proper internal ordering
- [ ] `ignore_changes` not quoted
- [ ] Dynamic blocks used for conditional nested objects
- [ ] `coalesce()` or `try()` used for default values

## Variables
- [ ] No `enabled` or `module_depends_on` variables
- [ ] Variables ordered: required (alphabetical) then optional (alphabetical)
- [ ] All variables have precise types (avoid `any`)
- [ ] All variables have descriptions
- [ ] Collections have `nullable = false`
- [ ] No `sensitive = false` declarations
- [ ] No default values for sensitive inputs
- [ ] Deprecated variables moved to `deprecated_variables.tf`

## Outputs
- [ ] Outputs use anti-corruption layer pattern (discrete attributes)
- [ ] Sensitive outputs marked `sensitive = true`
- [ ] Deprecated outputs moved to `deprecated_outputs.tf`

## Terraform Configuration
- [ ] `terraform.tf` has version constraints (`~>` format)
- [ ] `required_providers` block present with all providers
- [ ] No `provider` declarations in module (except aliases)
- [ ] Locals arranged alphabetically

## Testing & Quality
- [ ] Required testing tools configured
- [ ] New resources have feature toggles
- [ ] Breaking changes reviewed and documented
