# CRUD Operations — Full Examples

## Create Operation

```go
func (r *resourceExample) Create(ctx context.Context, req resource.CreateRequest, resp *resource.CreateResponse) {
    var data resourceExampleModel
    resp.Diagnostics.Append(req.Plan.Get(ctx, &data)...)
    if resp.Diagnostics.HasError() {
        return
    }

    conn := r.Meta().ExampleClient(ctx)

    input := &example.CreateExampleInput{
        Name: data.Name.ValueStringPointer(),
    }

    output, err := conn.CreateExample(ctx, input)
    if err != nil {
        resp.Diagnostics.AddError(
            "Error creating Example",
            fmt.Sprintf("Could not create example %s: %s", data.Name.ValueString(), err),
        )
        return
    }

    data.ID = types.StringPointerValue(output.Id)
    data.ARN = types.StringPointerValue(output.Arn)

    resp.Diagnostics.Append(resp.State.Set(ctx, &data)...)
}
```

## Read Operation

```go
func (r *resourceExample) Read(ctx context.Context, req resource.ReadRequest, resp *resource.ReadResponse) {
    var data resourceExampleModel
    resp.Diagnostics.Append(req.State.Get(ctx, &data)...)
    if resp.Diagnostics.HasError() {
        return
    }

    conn := r.Meta().ExampleClient(ctx)

    output, err := findExampleByID(ctx, conn, data.ID.ValueString())
    if tfresource.NotFound(err) {
        resp.Diagnostics.AddWarning(
            "Resource not found",
            fmt.Sprintf("Example %s not found, removing from state", data.ID.ValueString()),
        )
        resp.State.RemoveResource(ctx)
        return
    }
    if err != nil {
        resp.Diagnostics.AddError(
            "Error reading Example",
            fmt.Sprintf("Could not read example %s: %s", data.ID.ValueString(), err),
        )
        return
    }

    data.Name = types.StringPointerValue(output.Name)
    data.ARN = types.StringPointerValue(output.Arn)

    resp.Diagnostics.Append(resp.State.Set(ctx, &data)...)
}
```

## Update Operation

```go
func (r *resourceExample) Update(ctx context.Context, req resource.UpdateRequest, resp *resource.UpdateResponse) {
    var plan, state resourceExampleModel
    resp.Diagnostics.Append(req.Plan.Get(ctx, &plan)...)
    resp.Diagnostics.Append(req.State.Get(ctx, &state)...)
    if resp.Diagnostics.HasError() {
        return
    }

    conn := r.Meta().ExampleClient(ctx)

    if !plan.Description.Equal(state.Description) {
        input := &example.UpdateExampleInput{
            Id:          plan.ID.ValueStringPointer(),
            Description: plan.Description.ValueStringPointer(),
        }

        _, err := conn.UpdateExample(ctx, input)
        if err != nil {
            resp.Diagnostics.AddError(
                "Error updating Example",
                fmt.Sprintf("Could not update example %s: %s", plan.ID.ValueString(), err),
            )
            return
        }
    }

    resp.Diagnostics.Append(resp.State.Set(ctx, &plan)...)
}
```

## Delete Operation

```go
func (r *resourceExample) Delete(ctx context.Context, req resource.DeleteRequest, resp *resource.DeleteResponse) {
    var data resourceExampleModel
    resp.Diagnostics.Append(req.State.Get(ctx, &data)...)
    if resp.Diagnostics.HasError() {
        return
    }

    conn := r.Meta().ExampleClient(ctx)

    _, err := conn.DeleteExample(ctx, &example.DeleteExampleInput{
        Id: data.ID.ValueStringPointer(),
    })

    if tfresource.NotFound(err) {
        return
    }

    if err != nil {
        resp.Diagnostics.AddError(
            "Error deleting Example",
            fmt.Sprintf("Could not delete example %s: %s", data.ID.ValueString(), err),
        )
        return
    }
}
```
