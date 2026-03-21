# State Management — Full Examples

## Finder Function

Wrap API Get calls in a finder that returns `retry.NotFoundError` when the resource is missing.
This enables consistent NotFound handling across CRUD operations.

```go
func findExampleByID(ctx context.Context, conn *example.Client, id string) (*example.Example, error) {
    input := &example.GetExampleInput{
        Id: &id,
    }

    output, err := conn.GetExample(ctx, input)
    if err != nil {
        var notFound *types.ResourceNotFoundException
        if errors.As(err, &notFound) {
            return nil, &retry.NotFoundError{
                LastError:   err,
                LastRequest: input,
            }
        }
        return nil, err
    }

    if output == nil || output.Example == nil {
        return nil, tfresource.NewEmptyResultError(input)
    }

    return output.Example, nil
}
```

## State Waiters

For async resources, use `retry.StateChangeConf` to poll until the resource reaches a target state.

```go
func waitExampleCreated(ctx context.Context, conn *example.Client, id string, timeout time.Duration) (*example.Example, error) {
    stateConf := &retry.StateChangeConf{
        Pending: []string{"CREATING", "PENDING"},
        Target:  []string{"ACTIVE", "AVAILABLE"},
        Refresh: statusExample(ctx, conn, id),
        Timeout: timeout,
    }

    outputRaw, err := stateConf.WaitForStateContext(ctx)
    if output, ok := outputRaw.(*example.Example); ok {
        return output, err
    }

    return nil, err
}

func statusExample(ctx context.Context, conn *example.Client, id string) retry.StateRefreshFunc {
    return func() (interface{}, string, error) {
        output, err := findExampleByID(ctx, conn, id)
        if tfresource.NotFound(err) {
            return nil, "", nil
        }
        if err != nil {
            return nil, "", err
        }
        return output, string(output.Status), nil
    }
}
```
