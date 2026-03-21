---
name: terraform-stacks
description: Guide for HashiCorp Terraform Stacks — creating, modifying, and validating Stack configurations (.tfcomponent.hcl, .tfdeploy.hcl), managing multi-region/multi-environment infrastructure.
metadata:
  copyright: Copyright IBM Corp. 2026
  version: "0.0.1"
---

# Terraform Stacks

## Core Concepts

- **Stack**: Infrastructure unit composed of components and deployments, managed together.
- **Component**: Abstraction around a Terraform module — specifies source, inputs, and providers.
- **Deployment**: Instance of all components with specific input values (per environment, region, or account).
- **Stack Language**: Separate HCL-based language with distinct blocks and file extensions (not regular Terraform HCL).

## File Structure

| Extension | Purpose |
|-----------|---------|
| `.tfcomponent.hcl` | Component configuration |
| `.tfdeploy.hcl` | Deployment configuration |
| `.terraform.lock.hcl` | Provider lock file (generated) |

All files live at the Stack repository root. HCP Terraform processes them in dependency order.

### Recommended Layout

```
my-stack/
├── variables.tfcomponent.hcl
├── providers.tfcomponent.hcl
├── components.tfcomponent.hcl
├── outputs.tfcomponent.hcl
├── deployments.tfdeploy.hcl
├── .terraform.lock.hcl              # generated
└── modules/                         # only if using local modules
    ├── s3/
    └── compute/
```

**Module sources** (no local `modules/` dir needed for remote sources):
- Local: `./modules/vpc`
- Public registry: `terraform-aws-modules/vpc/aws`
- Private registry: `app.terraform.io/<org-name>/vpc/aws`
- Git: `git::https://github.com/org/repo.git//path?ref=v1.0.0`

## Component Configuration (.tfcomponent.hcl)

### Variable Block

Variables require a `type` field. The `validation` argument is not supported.

```hcl
variable "aws_region" {
  type        = string
  description = "AWS region for deployments"
  default     = "us-west-1"
}

variable "identity_token" {
  type        = string
  description = "OIDC identity token"
  ephemeral   = true  # prevents persistence in state
}

variable "instance_count" {
  type     = number
  nullable = false
}
```

Use `ephemeral = true` for credentials and tokens (prevents state persistence). Use `stable` for longer-lived values like license keys.

### Required Providers Block

```hcl
required_providers {
  aws = {
    source  = "hashicorp/aws"
    version = "~> 6.0"
  }
  random = {
    source  = "hashicorp/random"
    version = "~> 3.5.0"
  }
}
```

### Provider Block

Differences from traditional Terraform:
1. Supports `for_each` meta-argument
2. Aliases defined in block header (not as argument)
3. Configuration via nested `config` block

```hcl
# Single provider
provider "aws" "this" {
  config {
    region = var.aws_region
    assume_role_with_web_identity {
      role_arn           = var.role_arn
      web_identity_token = var.identity_token
    }
  }
}

# Multiple providers with for_each
provider "aws" "configurations" {
  for_each = var.regions
  config {
    region = each.value
    assume_role_with_web_identity {
      role_arn           = var.role_arn
      web_identity_token = var.identity_token
    }
  }
}
```

Prefer **workload identity** (OIDC) — avoids long-lived static credentials, provides temporary scoped credentials per deployment run. Configure with `identity_token` blocks and `assume_role_with_web_identity`. Setup: https://developer.hashicorp.com/terraform/cloud-docs/dynamic-provider-credentials

### Component Block

Each Stack needs at least one component. Components reference modules from local paths, registries, or Git.

```hcl
component "vpc" {
  source  = "app.terraform.io/my-org/vpc/aws"
  version = "2.1.0"

  inputs = {
    cidr_block  = var.vpc_cidr
    name_prefix = var.name_prefix
  }

  providers = {
    aws = provider.aws.this
  }
}
```

**Referencing outputs:**
- Single instance: `component.<name>.<output>`
- With `for_each`: `component.<name>[key].<output>`
- Aggregate: `[for x in component.s3 : x.bucket_name]`
- Provider refs: `provider.<type>.<alias>` or `provider.<type>.<alias>[each.value]`

Dependencies are inferred automatically from component references.

See `references/component-blocks.md` for dependencies, for_each, public registry, Git sources.

### Output Block

Outputs require a `type` argument. `preconditions` not supported.

```hcl
output "vpc_id" {
  type        = string
  description = "VPC ID"
  value       = component.vpc.vpc_id
}

output "endpoint_urls" {
  type  = map(string)
  value = {
    for region, comp in component.api : region => comp.endpoint_url
  }
}
```

### Locals Block

Works identically in `.tfcomponent.hcl` and `.tfdeploy.hcl`:

```hcl
locals {
  common_tags = {
    Environment = var.environment
    ManagedBy   = "Terraform Stacks"
    Project     = var.project_name
  }
}
```

### Removed Block

Safely remove components. Requires the component's providers for teardown.

```hcl
removed {
  from   = component.old_component
  source = "./modules/old-module"
  providers = {
    aws = provider.aws.this
  }
}
```

## Deployment Configuration (.tfdeploy.hcl)

### Identity Token Block

Generate JWT tokens for OIDC authentication:

```hcl
identity_token "aws" {
  audience = ["aws.workload.identity"]
}
```

Reference in deployments: `identity_token.<name>.jwt`

### Store Block

Access HCP Terraform variable sets:

```hcl
store "varset" "aws_credentials" {
  id       = "varset-ABC123"
  source   = "tfc-cloud-shared"
  category = "terraform"
}

deployment "production" {
  inputs = {
    aws_access_key = store.varset.aws_credentials.AWS_ACCESS_KEY_ID
  }
}
```

See `references/deployment-blocks.md` for details.

### Deployment Block

Minimum 1, maximum 20 deployments per Stack:

```hcl
deployment "production" {
  inputs = {
    aws_region     = "us-west-1"
    instance_count = 3
    role_arn       = local.role_arn
    identity_token = identity_token.aws.jwt
  }
}

deployment "development" {
  inputs = {
    aws_region     = "us-east-1"
    instance_count = 1
    identity_token = identity_token.aws.jwt
  }
}
```

To destroy: set `destroy = true`, upload configuration, approve destroy run, then remove the block. See `references/deployment-blocks.md`.

### Deployment Group Block

Group deployments for shared settings (Premium tier):

```hcl
deployment_group "canary" {
  auto_approve_checks = [deployment_auto_approve.safe_changes]
}

deployment "dev" {
  inputs           = { /* ... */ }
  deployment_group = deployment_group.canary
}
```

### Deployment Auto-Approve Block

Auto-approve rules for deployment plans (Premium tier):

```hcl
deployment_auto_approve "safe_changes" {
  deployment_group = deployment_group.canary
  check {
    condition = context.plan.changes.remove == 0
    reason    = "Cannot auto-approve plans with resource deletions"
  }
}
```

Context variables: `context.plan.applyable`, `context.plan.changes.add/change/remove/total`, `context.success`

`orchestrate` blocks are deprecated — use `deployment_group` and `deployment_auto_approve` instead.

### Publish Output and Upstream Input

Link Stacks by publishing outputs from one and consuming in another:

```hcl
# Network Stack — publish
publish_output "vpc_id_network" {
  type  = string
  value = deployment.network.vpc_id
}

# Application Stack — consume
upstream_input "network_stack" {
  type   = "stack"
  source = "app.terraform.io/my-org/my-project/networking-stack"
}

deployment "app" {
  inputs = {
    vpc_id = upstream_input.network_stack.vpc_id_network
  }
}
```

See `references/linked-stacks.md` for complete documentation.

## CLI Commands

GA as of Terraform CLI v1.13+. Stacks count toward RUM for HCP Terraform billing.

### Initialize and Validate

```bash
terraform stacks init              # Download providers, modules, generate lock file
terraform stacks providers-lock    # Regenerate lock file
terraform stacks validate          # Check syntax without uploading
```

### Deployment Workflow

No `plan` or `apply` commands — uploading configuration triggers deployment runs.

```bash
terraform stacks configuration upload
terraform stacks deployment-run list
terraform stacks deployment-group watch -deployment-group=...
terraform stacks deployment-run approve-all-plans -deployment-run-id=...
terraform stacks deployment-group approve-all-plans -deployment-group=...
terraform stacks deployment-run cancel -deployment-run-id=...
```

### Other Commands

```bash
terraform stacks create              # Create new Stack (interactive)
terraform stacks fmt                 # Format Stack files
terraform stacks list                # Show all Stacks
terraform stacks version             # Display version
terraform stacks configuration list
terraform stacks configuration fetch -configuration-id=...
terraform stacks deployment-group rerun -deployment-group=...
```

## API Monitoring

For automation/CI/CD, use the HCP Terraform API instead of CLI watch commands (which stream indefinitely).

- Artifacts endpoint for outputs: `GET /api/v2/stack-deployment-steps/{step-id}/artifacts?name=apply-description`
- Diagnostics endpoint requires `stack_deployment_step_id` query parameter
- Artifacts returns HTTP 307 redirect (use `curl -L`)

See `references/api-monitoring.md` for full workflow, authentication, and polling patterns.

## Common Patterns

- **Component dependencies**: Inferred automatically from output references.
- **Multi-region**: Use `for_each` on providers and components.
- **Deferred changes**: Handles values only known after apply (cluster endpoints, generated passwords).

See `references/examples.md` for complete working examples.

## Best Practices

1. Create components for logical infrastructure units that share a lifecycle
2. Modules used with Stacks cannot include provider blocks — configure providers in Stack config
3. Test public registry modules before production (some have compatibility issues with Stacks)
4. Each deployment has isolated state
5. Use variables for deployment-specific values; locals for shared values
6. Commit `.terraform.lock.hcl` to version control
7. Test in dev/staging before production

## Troubleshooting

- **Circular dependencies**: Refactor to break cycles or use intermediate components
- **Deployment destruction**: Set `destroy = true`, upload, approve destroy run
- **Empty diagnostics**: Add `stack_deployment_step_id` query parameter

See `references/troubleshooting.md` for detailed solutions.

## References

- `references/component-blocks.md` — Component block syntax and arguments
- `references/deployment-blocks.md` — Deployment block configuration options
- `references/linked-stacks.md` — Publishing outputs and upstream inputs
- `references/examples.md` — Multi-region and dependency examples
- `references/api-monitoring.md` — API workflow for automation
- `references/troubleshooting.md` — Common issues and solutions
