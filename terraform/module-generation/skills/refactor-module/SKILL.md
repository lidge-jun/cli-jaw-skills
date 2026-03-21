---
name: refactor-module
description: Transform monolithic Terraform configurations into reusable, maintainable modules following HashiCorp's module design principles and community best practices.
metadata:
  copyright: Copyright IBM Corp. 2026
  version: "0.0.1"
---

# Refactor Module

## Input Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `source_directory` | string | Yes | Path to existing Terraform configuration |
| `module_name` | string | Yes | Name for the new module |
| `abstraction_level` | string | No | "simple", "intermediate", "advanced" (default: intermediate) |
| `preserve_state` | boolean | Yes | Whether to maintain state compatibility |
| `target_registry` | string | No | Target module registry (local, private, public) |

## Execution Steps

### 1. Analysis Phase

- Group resources by logical function
- Identify repeated patterns
- Map resource dependencies and cross-references
- Evaluate state migration complexity
- Measure variable propagation depth

### 2. Module Design

#### Interface Design

Define typed input contracts with validation and descriptive outputs:

```hcl
variable "network_config" {
  description = "Network configuration parameters"
  type = object({
    cidr_block         = string
    availability_zones = list(string)
    enable_nat         = bool
  })

  validation {
    condition     = can(cidrhost(var.network_config.cidr_block, 0))
    error_message = "CIDR block must be valid IPv4 CIDR."
  }
}

output "vpc_id" {
  description = "ID of the created VPC"
  value       = aws_vpc.main.id
}

output "private_subnet_ids" {
  description = "List of private subnet IDs"
  value       = { for k, v in aws_subnet.private : k => v.id }
}
```

#### Encapsulation Guidelines

Include in module:
- Tightly coupled resources (e.g., VPC + subnets)
- Resources with shared lifecycle
- Configuration with clear boundaries

Keep separate:
- Cross-cutting concerns (monitoring, tagging)
- Resources with different lifecycles
- Provider-specific configurations

### 3. Code Transformation

Extract hardcoded values into variables, replace repeated resources with `for_each`, and use `merge()` for tag propagation.

See [references/transformation-example.md](references/transformation-example.md) for a complete monolithic→modular VPC refactoring example.

### 4. State Migration

Use `moved` blocks (Terraform 1.1+) for declarative state migration. For older versions, use `terraform state mv` commands.

See [references/state-migration.md](references/state-migration.md) for examples of both approaches.

Verify migration in non-production first:

```bash
terraform plan -out=migration.tfplan    # expect no changes
terraform show migration.tfplan         # review carefully
terraform apply migration.tfplan        # apply only if clean
```

### 5. Testing

Use skill `terraform-test`. Organize tests in a `tests/` directory:

```
my-module/
├── main.tf
├── variables.tf
├── outputs.tf
└── tests/
    ├── unit_test.tftest.hcl         # plan mode
    └── integration_test.tftest.hcl  # apply mode (creates real resources)
```

### 6. Documentation

Each module needs a README with: Overview, Usage example, Requirements, Inputs table, Outputs table.

See [references/module-documentation-template.md](references/module-documentation-template.md) for the standard template.

## Refactoring Patterns

### Pattern 1: Resource Grouping

Extract related resources into cohesive modules:
- Networking (VPC, Subnets, Route Tables)
- Compute (ASG, Launch Templates, Load Balancers)
- Data (RDS, ElastiCache, S3)

### Pattern 2: Configuration Layering

```hcl
module "vpc_base" {
  source = "./modules/vpc-base"
  # Minimal required inputs
}

module "vpc_prod" {
  source = "./modules/vpc-production"
  # Inherits from base, adds prod-specific config
}
```

### Pattern 3: Composition

Build complex infrastructure from small, focused modules:

```hcl
module "vpc" {
  source = "./modules/vpc"
}

module "security_groups" {
  source = "./modules/security-groups"
  vpc_id = module.vpc.vpc_id
}

module "application" {
  source     = "./modules/application"
  vpc_id     = module.vpc.vpc_id
  subnet_ids = module.vpc.private_subnet_ids
  sg_ids     = module.security_groups.app_sg_ids
}
```

## Common Pitfalls

### Over-Abstraction

Use specific, typed interfaces. `map(map(any))` prevents validation and obscures intent.

```hcl
# Prefer this
variable "database_config" {
  type = object({
    engine         = string
    instance_class = string
  })
}
```

### Tight Coupling

Pass dependencies through the root module rather than coupling modules directly, keeping modules independently testable.

### Missing State Migration Verification

Run `terraform plan` after migration and confirm zero changes before applying to production.

## Version Control Strategy

```hcl
# Pin module versions with semantic versioning
module "vpc" {
  source = "git::https://github.com/org/terraform-modules.git//vpc?ref=v1.2.0"
}
```

Pin exact versions in production; use version ranges in development.

## Success Criteria

- [ ] Module has single, well-defined responsibility
- [ ] All variables have descriptions and types
- [ ] Validation rules prevent invalid configurations
- [ ] Outputs provide sufficient information for consumers
- [ ] Documentation includes usage examples
- [ ] Tests verify module behavior
- [ ] State migration completed without resource recreation
- [ ] No plan differences after refactoring

## Related Skills

- [Terraform Style Guide](https://raw.githubusercontent.com/hashicorp/agent-skills/refs/heads/main/terraform/code-generation/skills/terraform-style-guide/SKILL.md)
- [Azure Verified Modules](https://raw.githubusercontent.com/hashicorp/agent-skills/refs/heads/main/terraform/code-generation/skills/azure-verified-modules/SKILL.md)

## External References

- [Terraform Module Development](https://developer.hashicorp.com/terraform/language/modules/develop)
- [Module Best Practices](https://developer.hashicorp.com/terraform/cloud-docs/registry/design)

## Revision History

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2025-11-07 | Initial skill definition |
