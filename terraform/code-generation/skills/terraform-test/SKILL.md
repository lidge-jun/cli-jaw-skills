---
name: terraform-test
description: Guide for writing Terraform tests (.tftest.hcl). Covers run blocks, assertions, mock providers, test modes, and CI integration.
metadata:
  copyright: Copyright IBM Corp. 2026
  version: "0.0.1"
---

# Terraform Test

Terraform's built-in testing framework validates that configuration updates work correctly. Tests execute against temporary resources, protecting existing infrastructure and state.

## File Structure

Test files use `.tftest.hcl` extension, organized in a `tests/` directory. Name files to distinguish unit vs integration tests:

```
my-module/
├── main.tf
├── variables.tf
├── outputs.tf
└── tests/
    ├── validation_unit_test.tftest.hcl
    ├── edge_cases_unit_test.tftest.hcl
    └── full_stack_integration_test.tftest.hcl
```

A test file contains:
- Zero to one `test` block (settings)
- One or more `run` blocks (test executions)
- Zero to one `variables` block (input values)
- Zero or more `provider` / `mock_provider` blocks

## Test Block

Optional test-wide settings (since v1.6.0):

```hcl
test {
  parallel = true  # Enable parallel run blocks (default: false)
}
```

## Run Block

Each `run` block executes one test scenario. Run blocks execute sequentially by default.

```hcl
run "test_default_configuration" {
  command = plan  # "apply" (default) or "plan"

  assert {
    condition     = aws_instance.example.instance_type == "t2.micro"
    error_message = "Instance type should be t2.micro by default"
  }
}
```

**Attributes:**

| Attribute | Description |
|-----------|-------------|
| `command` | `apply` (default) or `plan` |
| `plan_options` | Plan behavior config (mode, refresh, replace, target) |
| `variables` | Override test-level variable values |
| `module` | Reference alternate modules |
| `providers` | Customize provider availability |
| `assert` | Validation conditions (multiple allowed) |
| `expect_failures` | Expected validation failures |
| `state_key` | State file isolation (since v1.9.0) |
| `parallel` | Enable parallel execution (since v1.9.0) |

### Plan Options

```hcl
run "test_refresh_only" {
  command = plan

  plan_options {
    mode    = refresh-only  # "normal" (default) or "refresh-only"
    refresh = true
    replace = [aws_instance.example]
    target  = [aws_instance.example]
  }
}
```

## Variables

Define at file level (all run blocks) or within individual run blocks. Test file variables take the highest precedence, overriding env vars, `.tfvars`, and CLI input.

```hcl
# File-level
variables {
  aws_region    = "us-west-2"
  instance_type = "t2.micro"
}

# Run-level override
run "test_override" {
  command = plan
  variables {
    instance_type = "t3.large"
  }
}

# Reference prior run outputs
run "setup_vpc" {
  command = apply
}

run "use_vpc" {
  command = plan
  variables {
    vpc_id = run.setup_vpc.vpc_id
  }
}
```

## Assert Block

All assertions within a run block must pass for the test to succeed:

```hcl
assert {
  condition     = <expression>
  error_message = "failure description"
}
```

Supports resource attributes, outputs, `run.<name>.<output>` references, and complex expressions like `alltrue()`, `can(regex(...))`, `length()`.

## Expect Failures

Test that invalid input is properly rejected. The test passes if the listed checkable objects report an error:

```hcl
run "test_invalid_input_rejected" {
  command = plan
  variables {
    instance_count = -1
  }
  expect_failures = [
    var.instance_count
  ]
}
```

Checkable objects: input variables, output values, check blocks, resources, data sources.

## Module Block

Test a specific module rather than root configuration. Supports local paths and registry modules (Git/HTTP sources are not supported).

```hcl
run "test_vpc_module" {
  command = plan

  module {
    source  = "./modules/vpc"          # local
    # source  = "hashicorp/vpc/aws"    # registry
    # version = "5.0.0"                # registry only
  }

  variables {
    cidr_block = "10.0.0.0/16"
  }
}
```

## Provider Configuration

Override providers for tests. Since v1.7.0, provider blocks can reference test variables.

```hcl
provider "aws" {
  region = "us-west-2"
}

provider "aws" {
  alias  = "secondary"
  region = "us-east-1"
}

run "test_with_secondary" {
  command = plan
  providers = {
    aws = provider.aws.secondary
  }
}
```

## State Key

Controls which state file a run block uses. By default, main config shares state across all run blocks; each alternate module gets its own state.

```hcl
run "create_vpc" {
  command   = apply
  module    { source = "./modules/vpc" }
  state_key = "shared_state"
}

run "create_subnet" {
  command   = apply
  module    { source = "./modules/subnet" }
  state_key = "shared_state"  # shares state with create_vpc
}
```

## Parallel Execution

Enable with `parallel = true` (since v1.9.0). Requirements:
- No inter-run output references between parallel blocks
- Different state files (via different modules or state keys)

```hcl
run "test_module_a" {
  command  = plan
  parallel = true
  module   { source = "./modules/module-a" }
}

run "test_module_b" {
  command  = plan
  parallel = true
  module   { source = "./modules/module-b" }
}

# Non-parallel block creates a synchronization point
run "test_integration" {
  command = plan
}
```

## Mock Providers

Simulate provider behavior without creating real infrastructure (since v1.7.0). Mocks only work with `command = plan`.

```hcl
mock_provider "aws" {
  mock_resource "aws_instance" {
    defaults = {
      id            = "i-1234567890abcdef0"
      instance_type = "t2.micro"
      ami           = "ami-12345678"
    }
  }

  mock_data "aws_ami" {
    defaults = {
      id = "ami-12345678"
    }
  }
}

run "test_with_mocks" {
  command = plan
  assert {
    condition     = aws_instance.example.id == "i-1234567890abcdef0"
    error_message = "Mock instance ID should match"
  }
}
```

Use mocks for: testing logic/conditionals, local dev without cloud access, fast CI feedback.
See `references/examples.md` for comprehensive mock provider definitions.

## Cleanup

Resources are destroyed in reverse run block order after test completion — important for dependency ordering. Use `terraform test -no-cleanup` for debugging.

## Test Execution

```bash
terraform test                                    # all tests
terraform test tests/defaults.tftest.hcl          # specific file
terraform test -verbose                           # detailed output
terraform test -test-directory=integration-tests  # custom directory
terraform test -filter=test_vpc_configuration     # filter by name
terraform test -no-cleanup                        # keep resources for debugging
```

## Best Practices

1. **Naming**: `*_unit_test.tftest.hcl` for plan-mode, `*_integration_test.tftest.hcl` for apply-mode
2. **Plan mode first**: use `command = plan` for fast, cost-free validation; reserve `apply` for integration tests
3. **Mock providers**: isolate unit tests from cloud dependencies (v1.7.0+)
4. **Clear error messages**: write assertion messages that diagnose failures without requiring investigation
5. **Variable coverage**: test different combinations to validate all code paths
6. **Negative testing**: use `expect_failures` for invalid inputs
7. **Parallel execution**: use `parallel = true` for independent tests with separate state
8. **CI integration**: run `terraform test` in CI pipelines to catch regressions

## References

- `references/test-patterns.md` — common unit and integration test patterns, advanced features
- `references/examples.md` — complete test suites, mock provider templates, CI/CD configs
- `references/troubleshooting.md` — common issues and solutions
- [Terraform Testing Documentation](https://developer.hashicorp.com/terraform/language/tests)
- [Terraform Test Command Reference](https://developer.hashicorp.com/terraform/cli/commands/test)
