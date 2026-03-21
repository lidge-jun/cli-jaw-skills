# State Migration Examples

## Declarative Migration (Terraform 1.1+)

Use `moved` blocks for state refactoring. Add these to a `migration.tf` file:

```hcl
moved {
  from = aws_vpc.main
  to   = module.vpc.aws_vpc.main
}

moved {
  from = aws_subnet.public_1
  to   = module.vpc.aws_subnet.public["us-east-1a"]
}

moved {
  from = aws_subnet.public_2
  to   = module.vpc.aws_subnet.public["us-east-1b"]
}

moved {
  from = aws_internet_gateway.main
  to   = module.vpc.aws_internet_gateway.main[0]
}
```

## Manual Migration (Pre-1.1)

```bash
terraform state mv aws_vpc.main module.vpc.aws_vpc.main
terraform state mv aws_subnet.public_1 'module.vpc.aws_subnet.public["us-east-1a"]'
terraform state mv aws_subnet.public_2 'module.vpc.aws_subnet.public["us-east-1b"]'
terraform state mv aws_internet_gateway.main 'module.vpc.aws_internet_gateway.main[0]'
```

## Verification

Always verify migration produces no changes before applying to production:

```bash
terraform plan -out=migration.tfplan    # expect no changes
terraform show migration.tfplan         # review carefully
terraform apply migration.tfplan        # apply only if clean
```
