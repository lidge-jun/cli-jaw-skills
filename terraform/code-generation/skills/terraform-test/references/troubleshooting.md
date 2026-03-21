# Terraform Test Troubleshooting

## Assertion Failures

Review error messages, check actual vs expected values, verify variable inputs. Use `-verbose` for detailed output.

## Provider Authentication

Tests fail due to missing credentials → configure provider credentials or use mock providers for unit tests (v1.7.0+).

## Resource Dependencies

Tests fail due to missing dependencies → use sequential run blocks or create setup runs. Cleanup happens in reverse order.

## Long Test Execution

- Use `command = plan` instead of `apply` where possible
- Use mock providers
- Use `parallel = true` for independent tests
- Separate slow integration tests from fast unit tests

## State Conflicts

Multiple tests interfere with each other:
- Use different modules (automatic separate state)
- Use `state_key` attribute to control state file sharing
- Use mock providers for isolated testing

## Module Source Errors

Test fails with unsupported module source → test files only support **local** and **registry** modules. Convert Git or HTTP sources to local modules.

## Cleanup Issues

Resources destroyed in reverse run block order after test completion. For S3 buckets with objects, ensure object creation runs *after* bucket creation so objects are destroyed first:

```hcl
run "create_bucket" {
  command = apply
  # ...
}

run "add_objects" {
  command = apply
  # destroyed first (reverse order)
}
```

Use `terraform test -no-cleanup` for debugging cleanup failures.
