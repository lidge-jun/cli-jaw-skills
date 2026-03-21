# Terraform Test Patterns

Common unit test and integration test patterns for `.tftest.hcl` files.

## Unit Test Patterns (Plan Mode)

### Testing Module Outputs

```hcl
run "test_module_outputs" {
  command = plan

  assert {
    condition     = output.vpc_id != null
    error_message = "VPC ID output must be defined"
  }

  assert {
    condition     = can(regex("^vpc-", output.vpc_id))
    error_message = "VPC ID should start with 'vpc-'"
  }

  assert {
    condition     = length(output.subnet_ids) >= 2
    error_message = "Should output at least 2 subnet IDs"
  }
}
```

### Testing Resource Counts

```hcl
run "test_resource_count" {
  command = plan

  variables {
    instance_count = 3
  }

  assert {
    condition     = length(aws_instance.workers) == 3
    error_message = "Should create exactly 3 worker instances"
  }
}
```

### Testing Conditional Resources

```hcl
run "test_conditional_resource_created" {
  command = plan

  variables {
    create_nat_gateway = true
  }

  assert {
    condition     = length(aws_nat_gateway.main) == 1
    error_message = "NAT gateway should be created when enabled"
  }
}

run "test_conditional_resource_not_created" {
  command = plan

  variables {
    create_nat_gateway = false
  }

  assert {
    condition     = length(aws_nat_gateway.main) == 0
    error_message = "NAT gateway should not be created when disabled"
  }
}
```

### Testing Tags

```hcl
run "test_resource_tags" {
  command = plan

  variables {
    common_tags = {
      Environment = "production"
      ManagedBy   = "Terraform"
    }
  }

  assert {
    condition     = aws_instance.example.tags["Environment"] == "production"
    error_message = "Environment tag should be set correctly"
  }

  assert {
    condition     = aws_instance.example.tags["ManagedBy"] == "Terraform"
    error_message = "ManagedBy tag should be set correctly"
  }
}
```

### Sequential Tests with Dependencies

```hcl
run "setup_vpc" {
  variables {
    vpc_cidr = "10.0.0.0/16"
  }

  assert {
    condition     = output.vpc_id != ""
    error_message = "VPC should be created"
  }
}

run "test_subnet_in_vpc" {
  command = plan

  variables {
    vpc_id = run.setup_vpc.vpc_id
  }

  assert {
    condition     = aws_subnet.example.vpc_id == run.setup_vpc.vpc_id
    error_message = "Subnet should be created in the VPC from setup_vpc"
  }
}
```

### Testing Data Sources

```hcl
run "test_data_source_lookup" {
  command = plan

  assert {
    condition     = data.aws_ami.ubuntu.id != ""
    error_message = "Should find a valid Ubuntu AMI"
  }

  assert {
    condition     = can(regex("^ami-", data.aws_ami.ubuntu.id))
    error_message = "AMI ID should be in correct format"
  }
}
```

### Testing Validation Rules

```hcl
# In variables.tf
variable "environment" {
  type = string

  validation {
    condition     = contains(["dev", "staging", "prod"], var.environment)
    error_message = "Environment must be dev, staging, or prod"
  }
}

# In test file
run "test_valid_environment" {
  command = plan

  variables {
    environment = "staging"
  }

  assert {
    condition     = var.environment == "staging"
    error_message = "Valid environment should be accepted"
  }
}

run "test_invalid_environment" {
  command = plan

  variables {
    environment = "invalid"
  }

  expect_failures = [
    var.environment
  ]
}
```

### Complex Conditions

```hcl
run "test_complex_validation" {
  command = plan

  assert {
    condition = alltrue([
      for subnet in aws_subnet.private :
      can(regex("^10\\.0\\.", subnet.cidr_block))
    ])
    error_message = "All private subnets should use 10.0.0.0/8 CIDR range"
  }

  assert {
    condition = alltrue([
      for instance in aws_instance.workers :
      contains(["t2.micro", "t2.small", "t3.micro"], instance.instance_type)
    ])
    error_message = "Worker instances should use approved instance types"
  }
}
```

## Integration Test Patterns (Apply Mode)

```hcl
run "integration_test_full_stack" {
  # command defaults to apply

  variables {
    environment = "integration-test"
    vpc_cidr    = "10.100.0.0/16"
  }

  assert {
    condition     = aws_vpc.main.id != ""
    error_message = "VPC should be created"
  }

  assert {
    condition     = length(aws_subnet.private) == 2
    error_message = "Should create 2 private subnets"
  }

  assert {
    condition     = aws_instance.bastion.public_ip != ""
    error_message = "Bastion instance should have a public IP"
  }
}
```

## Advanced Features

### Refresh-Only Mode

```hcl
run "test_refresh_only" {
  command = plan

  plan_options {
    mode = refresh-only
  }

  assert {
    condition     = aws_instance.example.tags["Environment"] == "production"
    error_message = "Tags should be refreshed correctly"
  }
}
```

### Targeted Resources

```hcl
run "test_specific_resource" {
  command = plan

  plan_options {
    target = [
      aws_instance.example
    ]
  }

  assert {
    condition     = aws_instance.example.instance_type == "t2.micro"
    error_message = "Targeted resource should be planned"
  }
}
```

### Multiple Modules in Parallel

```hcl
run "test_networking_module" {
  command  = plan
  parallel = true

  module {
    source = "./modules/networking"
  }

  variables {
    cidr_block = "10.0.0.0/16"
  }

  assert {
    condition     = output.vpc_id != ""
    error_message = "VPC should be created"
  }
}

run "test_compute_module" {
  command  = plan
  parallel = true

  module {
    source = "./modules/compute"
  }

  variables {
    instance_type = "t2.micro"
  }

  assert {
    condition     = output.instance_id != ""
    error_message = "Instance should be created"
  }
}
```

### Custom State Management

```hcl
run "create_foundation" {
  command   = apply
  state_key = "foundation"

  assert {
    condition     = aws_vpc.main.id != ""
    error_message = "Foundation VPC should be created"
  }
}

run "create_application" {
  command   = apply
  state_key = "foundation"  # Share state with foundation

  variables {
    vpc_id = run.create_foundation.vpc_id
  }

  assert {
    condition     = aws_instance.app.vpc_id == run.create_foundation.vpc_id
    error_message = "Application should use foundation VPC"
  }
}
```
