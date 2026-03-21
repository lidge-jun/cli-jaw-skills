---
name: provider-resources
description: Implement Terraform Provider resources and data sources using the Plugin Framework. Use when developing CRUD operations, schema design, state management, and acceptance testing for provider resources.
metadata:
  copyright: Copyright IBM Corp. 2026
  version: "0.0.1"
---

# Provider Resources Implementation

References: [Plugin Framework](https://developer.hashicorp.com/terraform/plugin/framework) · [Resources](https://developer.hashicorp.com/terraform/plugin/framework/resources) · [Data Sources](https://developer.hashicorp.com/terraform/plugin/framework/data-sources)

## File Structure

```
internal/service/<service>/
├── <resource_name>.go              # Resource implementation
├── <resource_name>_test.go         # Acceptance tests
├── <resource_name>_data_source.go  # Data source (if applicable)
├── find.go                         # Finder functions
├── exports_test.go                 # Test exports
└── service_package_gen.go          # Auto-generated registration

website/docs/r/<service>_<resource_name>.html.markdown  # Resource docs
website/docs/d/<service>_<resource_name>.html.markdown  # Data source docs
```

## Resource Structure

### Plugin Framework Pattern (preferred)

```go
type resourceExample struct {
    framework.ResourceWithConfigure
}

func (r *resourceExample) Metadata(_ context.Context, req resource.MetadataRequest, resp *resource.MetadataResponse) {
    resp.TypeName = req.ProviderTypeName + "_example"
}

func (r *resourceExample) Schema(ctx context.Context, req resource.SchemaRequest, resp *resource.SchemaResponse) {
    resp.Schema = schema.Schema{
        Attributes: map[string]schema.Attribute{
            "id": framework.IDAttribute(),
            "name": schema.StringAttribute{
                Required: true,
                PlanModifiers: []planmodifier.String{
                    stringplanmodifier.RequiresReplace(),
                },
                Validators: []validator.String{
                    stringvalidator.LengthBetween(1, 255),
                },
            },
            "arn": schema.StringAttribute{
                Computed: true,
                PlanModifiers: []planmodifier.String{
                    stringplanmodifier.UseStateForUnknown(),
                },
            },
        },
    }
}
```

### SDKv2 Pattern (legacy — use only when extending existing SDKv2 resources)

```go
func ResourceExample() *schema.Resource {
    return &schema.Resource{
        CreateWithoutTimeout: resourceExampleCreate,
        ReadWithoutTimeout:   resourceExampleRead,
        UpdateWithoutTimeout: resourceExampleUpdate,
        DeleteWithoutTimeout: resourceExampleDelete,

        Importer: &schema.ResourceImporter{
            StateContext: schema.ImportStatePassthroughContext,
        },

        Schema: map[string]*schema.Schema{
            // ...
        },
        CustomizeDiff: verify.SetTagsDiff,
    }
}
```

## CRUD Operations

Each resource implements Create, Read, Update, and Delete methods.

Key patterns:
- **Create**: deserialize plan → call API → set ID and computed fields → save state
- **Read**: load state → call finder → handle NotFound by removing from state → update state
- **Update**: compare plan vs state → call API for changed fields → save state
- **Delete**: load state → call API → handle NotFound gracefully

See [references/crud-operations.md](references/crud-operations.md) for complete code examples.

## Schema Design

### Attribute Types

| Terraform Type | Framework Type | Use Case |
|----------------|----------------|----------|
| `string` | `schema.StringAttribute` | Names, ARNs, IDs |
| `number` | `schema.Int64Attribute`, `schema.Float64Attribute` | Counts, sizes |
| `bool` | `schema.BoolAttribute` | Feature flags |
| `list` | `schema.ListAttribute` | Ordered collections |
| `set` | `schema.SetAttribute` | Unordered unique items |
| `map` | `schema.MapAttribute` | Key-value pairs |
| `object` | `schema.SingleNestedAttribute` | Complex nested config |

### Plan Modifiers

```go
stringplanmodifier.RequiresReplace()       // Force replacement when value changes
stringplanmodifier.UseStateForUnknown()    // Preserve computed value during plan

// Custom plan modifier
stringplanmodifier.RequiresReplaceIf(
    func(ctx context.Context, req planmodifier.StringRequest, resp *stringplanmodifier.RequiresReplaceIfFuncResponse) {
        // Custom logic
    },
    "description",
    "markdown description",
)
```

### Validators

```go
// String
stringvalidator.LengthBetween(1, 255)
stringvalidator.RegexMatches(regexp.MustCompile(`^[a-z0-9-]+$`), "must be lowercase alphanumeric with hyphens")
stringvalidator.OneOf("option1", "option2", "option3")

// Int64
int64validator.Between(1, 100)
int64validator.AtLeast(1)
int64validator.AtMost(1000)

// List
listvalidator.SizeAtLeast(1)
listvalidator.SizeAtMost(10)
```

### Sensitive Attributes

Mark attributes containing secrets as `Sensitive: true` to prevent values from appearing in logs and plan output.

```go
"password": schema.StringAttribute{
    Required:  true,
    Sensitive: true,
    Validators: []validator.String{
        stringvalidator.LengthAtLeast(8),
    },
}
```

## State Management

### Finder Functions

Wrap API Get calls in a finder that returns `retry.NotFoundError` when the resource is missing, enabling consistent NotFound handling across CRUD operations.

### State Waiters

For async resources, use `retry.StateChangeConf` to poll until the resource reaches a target state.

See [references/state-management.md](references/state-management.md) for implementation examples.

## Error Handling

### API Error Matching

```go
var notFound *types.ResourceNotFoundException
if errors.As(err, &notFound) { /* resource missing */ }

var conflict *types.ConflictException
if errors.As(err, &conflict) { /* state conflict */ }

var throttle *types.ThrottlingException
if errors.As(err, &throttle) { /* rate limited — SDK handles retry */ }
```

### Diagnostics

```go
resp.Diagnostics.AddError("Error creating resource",
    fmt.Sprintf("Could not create resource: %s", err))

resp.Diagnostics.AddWarning("Resource modified outside Terraform",
    "State may be inconsistent")

resp.Diagnostics.AddAttributeError(path.Root("name"),
    "Invalid name", "Name must be lowercase alphanumeric")
```

## Testing

Run acceptance tests with `TF_ACC=1`:

```bash
go test -c -o /dev/null ./internal/service/<service>                 # compile check
TF_ACC=1 go test ./internal/service/<service> -run TestAccExample -v -timeout 60m
TF_ACC=1 go test ./internal/service/<service> -sweep=<region> -v     # cleanup
```

Every resource needs:
- Basic acceptance test with import state verification
- Disappears test (`acctest.CheckResourceDisappears`)
- `testAccCheckExampleExists` and `testAccCheckExampleDestroy` helpers

See [references/testing-examples.md](references/testing-examples.md) for full test code.

## Documentation

Each resource and data source requires an HTML markdown doc with: Example Usage, Argument Reference, Attribute Reference, Import.

See [references/documentation-template.md](references/documentation-template.md) for the standard template.

## Pre-Submission Checklist

- [ ] Code compiles without errors
- [ ] All tests pass locally
- [ ] All CRUD operations implemented
- [ ] Import implemented and tested
- [ ] Disappears test included
- [ ] Documentation complete with examples
- [ ] Error messages are clear and actionable
- [ ] Sensitive attributes marked
- [ ] Plan modifiers set appropriately
- [ ] Validators cover edge cases

## External References

- [Terraform Plugin Framework](https://developer.hashicorp.com/terraform/plugin/framework)
- [Terraform Plugin SDKv2](https://developer.hashicorp.com/terraform/plugin/sdkv2)
- [Acceptance Testing](https://developer.hashicorp.com/terraform/plugin/testing/acceptance-tests)
- [terraform-plugin-framework GitHub](https://github.com/hashicorp/terraform-plugin-framework)
