# Resource Documentation Template

Place resource docs in `website/docs/r/` and data source docs in `website/docs/d/`.

```markdown
---
subcategory: "Service Name"
layout: "provider"
page_title: "Provider: provider_example"
description: |-
  Manages an Example resource.
---

# Resource: provider_example

Manages an Example resource.

## Example Usage

### Basic Usage

\```hcl
resource "provider_example" "example" {
  name = "my-example"
}
\```

## Argument Reference

* `name` - (Required) Name of the example.
* `description` - (Optional) Description of the example.

## Attribute Reference

* `id` - ID of the example.
* `arn` - ARN of the example.

## Import

Example can be imported using the ID:

\```
$ terraform import provider_example.example example-id-12345
\```
```
