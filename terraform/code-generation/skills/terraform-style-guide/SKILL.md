---
name: terraform-style-guide
description: Generate Terraform HCL code following HashiCorp's official style conventions and best practices. Use when writing, reviewing, or generating Terraform configurations.
---

# Terraform Style Guide

Ref: [HashiCorp Terraform Style Guide](https://developer.hashicorp.com/terraform/language/style)

## Code Generation Order

1. Provider configuration and version constraints
2. Data sources before dependent resources
3. Resources in dependency order
4. Outputs for key resource attributes
5. Variables for all configurable values

## File Organization

| File | Purpose |
|------|---------|
| `terraform.tf` | Terraform and provider version requirements |
| `providers.tf` | Provider configurations |
| `main.tf` | Primary resources and data sources |
| `variables.tf` | Input variable declarations (alphabetical) |
| `outputs.tf` | Output value declarations (alphabetical) |
| `locals.tf` | Local value declarations |

## Code Formatting

- Two spaces per nesting level (no tabs)
- Align equals signs for consecutive arguments
- Arguments precede blocks; meta-arguments first

```hcl
resource "aws_instance" "example" {
  # Meta-arguments
  count = 3

  # Arguments
  ami           = "ami-0c55b159cbfafe1f0"
  instance_type = "t2.micro"

  # Blocks
  root_block_device {
    volume_size = 20
  }

  # Lifecycle last
  lifecycle {
    create_before_destroy = true
  }
}
```

## Naming Conventions

- Lowercase with underscores for all names
- Descriptive nouns excluding the resource type
- Singular resource names
- Use `main` when only one instance exists and a specific name adds no clarity

```hcl
# ✗
resource "aws_instance" "webAPI-aws-instance" {}

# ✓
resource "aws_instance" "web_api" {}
resource "aws_vpc" "main" {}
variable "application_name" {}
```

## Variables

Every variable requires `type` and `description`:

```hcl
variable "instance_type" {
  description = "EC2 instance type for the web server"
  type        = string
  default     = "t2.micro"

  validation {
    condition     = contains(["t2.micro", "t2.small", "t2.medium"], var.instance_type)
    error_message = "Instance type must be t2.micro, t2.small, or t2.medium."
  }
}

variable "database_password" {
  description = "Password for the database admin user"
  type        = string
  sensitive   = true
}
```

## Outputs

Every output requires `description`. Mark sensitive values:

```hcl
output "instance_id" {
  description = "ID of the EC2 instance"
  value       = aws_instance.web.id
}

output "database_password" {
  description = "Database administrator password"
  value       = aws_db_instance.main.password
  sensitive   = true
}
```

## Dynamic Resource Creation

Prefer `for_each` over `count` — stable references by name instead of index:

```hcl
resource "aws_instance" "web" {
  for_each = toset(["web-1", "web-2", "web-3"])
  tags     = { Name = each.key }
}
```

Use `count` only for conditional creation:

```hcl
resource "aws_cloudwatch_metric_alarm" "cpu" {
  count = var.enable_monitoring ? 1 : 0

  alarm_name = "high-cpu-usage"
  threshold  = 80
}
```

## Security

- Enable encryption at rest by default
- Configure private networking where applicable
- Apply least-privilege for security groups
- Enable logging and monitoring
- Mark sensitive outputs with `sensitive = true`
- Never hardcode credentials

### Example: Secure S3 Bucket

```hcl
resource "aws_s3_bucket" "data" {
  bucket = "${var.project}-${var.environment}-data"
  tags   = local.common_tags
}

resource "aws_s3_bucket_versioning" "data" {
  bucket = aws_s3_bucket.data.id

  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "data" {
  bucket = aws_s3_bucket.data.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm     = "aws:kms"
      kms_master_key_id = aws_kms_key.s3.arn
    }
  }
}

resource "aws_s3_bucket_public_access_block" "data" {
  bucket = aws_s3_bucket.data.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}
```

## Provider Configuration

```hcl
provider "aws" {
  region = "us-west-2"

  default_tags {
    tags = {
      ManagedBy = "Terraform"
      Project   = var.project_name
    }
  }
}

# Aliased provider for multi-region
provider "aws" {
  alias  = "east"
  region = "us-east-1"
}
```
