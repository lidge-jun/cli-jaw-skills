---
name: provider-actions
description: Implement Terraform Provider actions using the Plugin Framework. Use when developing imperative operations that execute at lifecycle events (before/after create, update, destroy).
metadata:
  copyright: Copyright IBM Corp. 2026
  version: "0.0.1"
---

# Terraform Provider Actions

Terraform Actions enable imperative operations during the Terraform lifecycle — experimental features for performing provider operations at specific lifecycle events.

**References:**
- [Terraform Plugin Framework](https://developer.hashicorp.com/terraform/plugin/framework)
- [Terraform Actions RFC](https://github.com/hashicorp/terraform/blob/main/docs/plugin-protocol/actions.md)

## File Structure

```
internal/service/<service>/
├── <action_name>_action.go
├── <action_name>_action_test.go
└── service_package_gen.go        # Auto-generated registration

website/docs/actions/
└── <service>_<action_name>.html.markdown

.changelog/
└── <pr_number_or_description>.txt
```

## Action Schema Definition

```go
func (a *actionType) Schema(ctx context.Context, req action.SchemaRequest, resp *action.SchemaResponse) {
    resp.Schema = schema.Schema{
        Attributes: map[string]schema.Attribute{
            "resource_id": schema.StringAttribute{
                Required:    true,
                Description: "ID of the resource to operate on",
            },
            "timeout": schema.Int64Attribute{
                Optional:    true,
                Computed:    true,  // required when Default is set
                Description: "Operation timeout in seconds",
                Default:     int64default.StaticInt64(1800),
            },
        },
    }
}
```

### Schema Pitfalls

1. **Type mismatches** — use `fwtypes.String` / `fwtypes.StringType` in model structs and schema (not `types.String` / `types.StringType`)

2. **Missing ElementType on collections:**
   ```go
   // Wrong
   "items": schema.ListAttribute{Optional: true}
   // Correct
   "items": schema.ListAttribute{Optional: true, ElementType: fwtypes.StringType}
   ```

3. **Computed + Optional** — attributes with defaults need both `Optional: true` and `Computed: true`

4. **Validator imports** — use `terraform-plugin-framework-validators/{int64validator,stringvalidator}`

5. **Region handling** — use framework-provided region handling when available instead of manual schema definitions

### Schema Checklist

Before proceeding, verify:
- [ ] All attributes have descriptions
- [ ] List/Map attributes have ElementType
- [ ] Validators imported and applied
- [ ] Model struct uses correct framework types (`fwtypes.*`)
- [ ] Optional + default attributes marked Computed
- [ ] `go build` passes without type errors

## Action Invoke Method

```go
func (a *actionType) Invoke(ctx context.Context, req action.InvokeRequest, resp *action.InvokeResponse) {
    var data actionModel
    resp.Diagnostics.Append(req.Config.Get(ctx, &data)...)

    conn := a.Meta().Client(ctx)
    resp.Progress.Set(ctx, "Starting operation...")

    // Implement action logic
    // Use context for timeout management
    // Poll for completion if async

    resp.Progress.Set(ctx, "Operation completed")
}
```

## Implementation Requirements

### Progress Reporting

- Use `resp.SendProgress(action.InvokeProgressEvent{...})` for real-time updates
- Update at key milestones; include elapsed time for long operations

### Timeout Management

- Include configurable timeout parameter (default: 1800s, range: 60-7200s)
- Use `context.WithTimeout()` for API calls
- Handle timeout errors gracefully

### Error Handling

```go
// Specific error
var notFound *types.ResourceNotFoundException
if errors.As(err, &notFound) {
    resp.Diagnostics.AddError(
        "Resource Not Found",
        fmt.Sprintf("Resource %s was not found", resourceID),
    )
    return
}

// Generic error — include context and identifiers
resp.Diagnostics.AddError(
    "Operation Failed",
    fmt.Sprintf("Could not complete operation for %s: %s", resourceID, err),
)
```

Guidelines:
- Provide clear error messages with resource identifiers
- Map provider error types to user-friendly messages
- Document all possible error cases

### Provider SDK Integration

- Use SDK clients from `a.Meta().<Service>Client(ctx)`
- Handle pagination for list operations
- Implement retry logic for transient failures

### Polling and Waiting

```go
result, err := wait.WaitForStatus(ctx,
    func(ctx context.Context) (wait.FetchResult[*ResourceType], error) {
        resource, err := findResource(ctx, conn, id)
        if err != nil {
            return wait.FetchResult[*ResourceType]{}, err
        }
        return wait.FetchResult[*ResourceType]{
            Status: wait.Status(resource.Status),
            Value:  resource,
        }, nil
    },
    wait.Options[*ResourceType]{
        Timeout:            timeout,
        Interval:           wait.FixedInterval(5 * time.Second),
        SuccessStates:      []wait.Status{"AVAILABLE", "COMPLETED"},
        TransitionalStates: []wait.Status{"CREATING", "PENDING"},
        ProgressInterval:   30 * time.Second,
        ProgressSink: func(fr wait.FetchResult[any], meta wait.ProgressMeta) {
            resp.SendProgress(action.InvokeProgressEvent{
                Message: fmt.Sprintf("Status: %s, Elapsed: %v", fr.Status, meta.Elapsed.Round(time.Second)),
            })
        },
    },
)
```

## Common Action Patterns

| Pattern | Key Steps |
|---------|-----------|
| Batch Operations | Process in configurable batches, report per-batch progress, handle partial failures |
| Command Execution | Submit → get operation ID → poll completion → retrieve output |
| Service Invocation | Invoke with params → wait if synchronous → return results |
| Resource State Change | Validate current state → apply change → poll for target state |
| Async Job | Submit job → get job ID → optionally wait → report status |

## Action Triggers

```hcl
action "provider_service_action" "name" {
  config {
    parameter = value
  }
}

resource "terraform_data" "trigger" {
  lifecycle {
    action_trigger {
      events  = [after_create]
      actions = [action.provider_service_action.name]
    }
  }
}
```

### Available Trigger Events (Terraform 1.14.0)

| Event | Supported |
|-------|-----------|
| `before_create` | ✅ |
| `after_create` | ✅ |
| `before_update` | ✅ |
| `after_update` | ✅ |
| `before_destroy` | ❌ (validation error) |
| `after_destroy` | ❌ (validation error) |

## Testing

### Acceptance Test Pattern

```go
func TestAccServiceAction_basic(t *testing.T) {
    ctx := acctest.Context(t)
    resource.ParallelTest(t, resource.TestCase{
        PreCheck:                 func() { acctest.PreCheck(ctx, t) },
        ProtoV5ProviderFactories: acctest.ProtoV5ProviderFactories,
        TerraformVersionChecks: []tfversion.TerraformVersionCheck{
            tfversion.SkipBelow(tfversion.Version1_14_0),
        },
        Steps: []resource.TestStep{
            {
                Config: testAccActionConfig_basic(),
                Check: resource.ComposeTestCheckFunc(
                    testAccCheckResourceExists(ctx, "provider_resource.test"),
                ),
            },
        },
    })
}
```

### Test Sweep (cleanup test resources)

```go
func sweepResources(region string) error {
    ctx := context.Background()
    client := /* get client for region */
    var sweeperErrs *multierror.Error

    pages := service.NewListPaginator(client, &service.ListInput{})
    for pages.HasMorePages() {
        page, err := pages.NextPage(ctx)
        if err != nil {
            sweeperErrs = multierror.Append(sweeperErrs, err)
            continue
        }
        for _, item := range page.Items {
            if !strings.HasPrefix(item.Id, "tf-acc-test") {
                continue
            }
            if _, err := client.Delete(ctx, &service.DeleteInput{Id: item.Id}); err != nil {
                sweeperErrs = multierror.Append(sweeperErrs, err)
            }
        }
    }
    return sweeperErrs.ErrorOrNil()
}
```

### Testing Notes

- Check service-specific prerequisites before running action tests
- Terraform wraps action errors — use flexible regex: `regexache.MustCompile(\`(?s)Error Title.*key phrase\`)`
- Actions trigger on lifecycle events, not config reapplication
- `before_destroy` / `after_destroy` tests unsupported in Terraform 1.14.0

### Running Tests

```bash
go test -c -o /dev/null ./internal/service/<service>           # compile check
TF_ACC=1 go test ./internal/service/<service> -run TestAccServiceAction_ -v  # run
TF_ACC=1 go test ./internal/service/<service> -sweep=<region> -v            # sweep
```

## Documentation Standards

Each action doc file includes:

1. **Front matter** — subcategory, layout, page_title, description
2. **Header** — beta/alpha notice, warning about unintended consequences
3. **Example usage** — basic, advanced, trigger-based, real-world
4. **Argument reference** — required/optional args with descriptions and defaults
5. **Formatting** — run `terrafmt fmt` and verify with `terrafmt diff`

## Changelog Entry

```
.changelog/<pr_number_or_description>.txt
```

Format:
```release-note:new-action
action/provider_service_action: Brief description of the action
```

## Pre-Submission Checklist

- [ ] `go build -o /dev/null .` passes
- [ ] `go test -c -o /dev/null ./internal/service/<service>` passes
- [ ] `make fmt` applied
- [ ] `terrafmt fmt` applied to documentation
- [ ] Changelog entry created
- [ ] Schema uses correct types with ElementType on collections
- [ ] Progress updates implemented for long operations
- [ ] Error messages include context and resource identifiers
- [ ] Documentation includes examples and prerequisite warnings

## References

- [Terraform Plugin Framework](https://developer.hashicorp.com/terraform/plugin/framework)
- [terraform-plugin-framework (GitHub)](https://github.com/hashicorp/terraform-plugin-framework)
- [terraform-plugin-testing](https://github.com/hashicorp/terraform-plugin-testing)
