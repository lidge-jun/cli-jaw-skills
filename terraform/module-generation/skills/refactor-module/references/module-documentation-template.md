# Module Documentation Template

Each module needs a README.md with the following sections.

```markdown
# VPC Module

## Overview
Creates a VPC with configurable public and private subnets across multiple availability zones.

## Features
- Multi-AZ subnet deployment
- Optional NAT gateway configuration
- VPC Flow Logs integration
- Customizable CIDR allocation

## Usage

\`\`\`hcl
module "vpc" {
  source = "./modules/vpc"

  name               = "my-vpc"
  cidr_block         = "10.0.0.0/16"
  availability_zones = ["us-east-1a", "us-east-1b"]

  create_public_subnets  = true
  create_private_subnets = true
  enable_nat_gateway     = true

  tags = {
    Environment = "production"
  }
}
\`\`\`

## Requirements

| Name | Version |
|------|---------|
| terraform | >= 1.5.0 |
| aws | ~> 5.0 |

## Inputs

| Name | Description | Type | Default | Required |
|------|-------------|------|---------|----------|
| name | Name prefix for resources | `string` | n/a | yes |
| cidr_block | VPC CIDR block | `string` | n/a | yes |
| availability_zones | List of AZs | `list(string)` | n/a | yes |

## Outputs

| Name | Description |
|------|-------------|
| vpc_id | VPC identifier |
| public_subnet_ids | Map of public subnet IDs |
| private_subnet_ids | Map of private subnet IDs |

## Examples

See [examples/](./examples/) directory for complete usage examples.
```
