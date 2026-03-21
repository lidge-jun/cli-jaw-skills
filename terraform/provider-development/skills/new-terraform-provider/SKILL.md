---
name: new-terraform-provider
description: Use this when scaffolding a new Terraform provider.
license: MPL-2.0
metadata:
  copyright: Copyright IBM Corp. 2026
  version: "0.0.1"
---

To scaffold a new Terraform provider with Plugin Framework:

1. If already in a Terraform provider workspace, confirm before creating a new
   one. Skip remaining steps if declined.
1. Create a workspace root directory prefixed with `terraform-provider-`.
   Run all subsequent steps inside it.
1. Initialize a new Go module.
1. Run `go get -u github.com/hashicorp/terraform-plugin-framework@latest`.
1. Write a `main.go` following [the example](assets/main.go).
1. Remove TODO comments from `main.go`.
1. Run `go mod tidy`.
1. Run `go build -o /dev/null`.
1. Run `go test ./...`.

