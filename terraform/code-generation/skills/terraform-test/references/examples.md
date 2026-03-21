# Terraform Test Examples

Complete test suite examples, mock provider testing, and CI/CD integration.

## Complete VPC Module Test Suite

### Unit Tests (Plan Mode)

```hcl
# tests/vpc_module_unit_test.tftest.hcl

variables {
  environment = "test"
  aws_region  = "us-west-2"
}

run "test_defaults" {
  command = plan

  variables {
    vpc_cidr = "10.0.0.0/16"
    vpc_name = "test-vpc"
  }

  assert {
    condition     = aws_vpc.main.cidr_block == "10.0.0.0/16"
    error_message = "VPC CIDR should match input"
  }

  assert {
    condition     = aws_vpc.main.enable_dns_hostnames == true
    error_message = "DNS hostnames should be enabled by default"
  }

  assert {
    condition     = aws_vpc.main.tags["Name"] == "test-vpc"
    error_message = "VPC name tag should match input"
  }
}

run "test_subnets" {
  command = plan

  variables {
    vpc_cidr        = "10.0.0.0/16"
    vpc_name        = "test-vpc"
    public_subnets  = ["10.0.1.0/24", "10.0.2.0/24"]
    private_subnets = ["10.0.10.0/24", "10.0.11.0/24"]
  }

  assert {
    condition     = length(aws_subnet.public) == 2
    error_message = "Should create 2 public subnets"
  }

  assert {
    condition     = length(aws_subnet.private) == 2
    error_message = "Should create 2 private subnets"
  }

  assert {
    condition = alltrue([
      for subnet in aws_subnet.private :
      subnet.map_public_ip_on_launch == false
    ])
    error_message = "Private subnets should not assign public IPs"
  }
}

run "test_outputs" {
  command = plan

  variables {
    vpc_cidr = "10.0.0.0/16"
    vpc_name = "test-vpc"
  }

  assert {
    condition     = output.vpc_id != ""
    error_message = "VPC ID output should not be empty"
  }

  assert {
    condition     = can(regex("^vpc-", output.vpc_id))
    error_message = "VPC ID should have correct format"
  }

  assert {
    condition     = output.vpc_cidr == "10.0.0.0/16"
    error_message = "VPC CIDR output should match input"
  }
}

run "test_invalid_cidr" {
  command = plan

  variables {
    vpc_cidr = "invalid"
    vpc_name = "test-vpc"
  }

  expect_failures = [
    var.vpc_cidr
  ]
}
```

### Integration Tests (Apply Mode)

```hcl
# tests/vpc_module_integration_test.tftest.hcl

variables {
  environment = "integration-test"
  aws_region  = "us-west-2"
}

run "integration_test_vpc_creation" {
  # command defaults to apply

  variables {
    vpc_cidr = "10.100.0.0/16"
    vpc_name = "integration-test-vpc"
  }

  assert {
    condition     = aws_vpc.main.id != ""
    error_message = "VPC should be created with valid ID"
  }

  assert {
    condition     = aws_vpc.main.state == "available"
    error_message = "VPC should be in available state"
  }
}
```

## Mock Provider Testing

### Full Mock Provider Definition

```hcl
# tests/vpc_module_mock_test.tftest.hcl

mock_provider "aws" {
  mock_resource "aws_instance" {
    defaults = {
      id                          = "i-1234567890abcdef0"
      arn                         = "arn:aws:ec2:us-west-2:123456789012:instance/i-1234567890abcdef0"
      instance_type               = "t2.micro"
      ami                         = "ami-12345678"
      availability_zone           = "us-west-2a"
      subnet_id                   = "subnet-12345678"
      vpc_security_group_ids      = ["sg-12345678"]
      associate_public_ip_address = true
      public_ip                   = "203.0.113.1"
      private_ip                  = "10.0.1.100"
      tags                        = {}
    }
  }

  mock_resource "aws_vpc" {
    defaults = {
      id                       = "vpc-12345678"
      arn                      = "arn:aws:ec2:us-west-2:123456789012:vpc/vpc-12345678"
      cidr_block              = "10.0.0.0/16"
      enable_dns_hostnames    = true
      enable_dns_support      = true
      instance_tenancy        = "default"
      tags                    = {}
    }
  }

  mock_resource "aws_subnet" {
    defaults = {
      id                      = "subnet-12345678"
      arn                     = "arn:aws:ec2:us-west-2:123456789012:subnet/subnet-12345678"
      vpc_id                  = "vpc-12345678"
      cidr_block             = "10.0.1.0/24"
      availability_zone       = "us-west-2a"
      map_public_ip_on_launch = false
      tags                    = {}
    }
  }

  mock_resource "aws_s3_bucket" {
    defaults = {
      id                  = "test-bucket-12345"
      arn                 = "arn:aws:s3:::test-bucket-12345"
      bucket              = "test-bucket-12345"
      bucket_domain_name  = "test-bucket-12345.s3.amazonaws.com"
      region              = "us-west-2"
      tags                = {}
    }
  }

  mock_data "aws_ami" {
    defaults = {
      id                  = "ami-0c55b159cbfafe1f0"
      name                = "ubuntu/images/hvm-ssd/ubuntu-focal-20.04-amd64-server-20210430"
      architecture        = "x86_64"
      root_device_type    = "ebs"
      virtualization_type = "hvm"
      owners              = ["099720109477"]
    }
  }

  mock_data "aws_availability_zones" {
    defaults = {
      names = ["us-west-2a", "us-west-2b", "us-west-2c"]
      zone_ids = ["usw2-az1", "usw2-az2", "usw2-az3"]
    }
  }

  mock_data "aws_vpc" {
    defaults = {
      id                   = "vpc-12345678"
      cidr_block          = "10.0.0.0/16"
      enable_dns_hostnames = true
      enable_dns_support   = true
    }
  }
}

run "test_instance_with_mocks" {
  command = plan

  variables {
    instance_type = "t2.micro"
    ami_id        = "ami-12345678"
  }

  assert {
    condition     = aws_instance.example.instance_type == "t2.micro"
    error_message = "Instance type should match input variable"
  }

  assert {
    condition     = aws_instance.example.id == "i-1234567890abcdef0"
    error_message = "Mock should return consistent instance ID"
  }
}

run "test_data_source_with_mocks" {
  command = plan

  assert {
    condition     = data.aws_ami.ubuntu.id == "ami-0c55b159cbfafe1f0"
    error_message = "Mock data source should return predictable AMI ID"
  }

  assert {
    condition     = length(data.aws_availability_zones.available.names) == 3
    error_message = "Should return 3 mocked availability zones"
  }
}

run "test_multiple_subnets_with_mocks" {
  command = plan

  variables {
    subnet_cidrs = {
      "public-a"  = "10.0.1.0/24"
      "public-b"  = "10.0.2.0/24"
      "private-a" = "10.0.10.0/24"
      "private-b" = "10.0.11.0/24"
    }
  }

  assert {
    condition     = length(keys(aws_subnet.subnets)) == 4
    error_message = "Should create 4 subnets from for_each map"
  }

  assert {
    condition = alltrue([
      for name, subnet in aws_subnet.subnets :
      can(regex("^public-", name)) ? subnet.map_public_ip_on_launch == true : true
    ])
    error_message = "Public subnets should map public IPs on launch"
  }
}

run "test_conditional_resources_with_mocks" {
  command = plan

  variables {
    create_bastion     = true
    create_nat_gateway = false
  }

  assert {
    condition     = length(aws_instance.bastion) == 1
    error_message = "Bastion should be created when enabled"
  }

  assert {
    condition     = length(aws_nat_gateway.nat) == 0
    error_message = "NAT gateway should not be created when disabled"
  }
}

run "test_invalid_cidr_with_mocks" {
  command = plan

  variables {
    vpc_cidr = "192.168.0.0/8"
  }

  expect_failures = [
    var.vpc_cidr
  ]
}
```

### When to Use Mock Tests

| Use case | Mock tests | Integration tests |
|----------|-----------|-------------------|
| Logic and conditionals | ✅ | ✅ |
| Variable transformations | ✅ | ✅ |
| for_each and count | ✅ | ✅ |
| Output calculations | ✅ | ✅ |
| Local dev without cloud | ✅ | ❌ |
| Fast CI/CD feedback | ✅ | ❌ |
| Actual provider behavior | ❌ | ✅ |
| Real resource side effects | ❌ | ✅ |
| API-level interactions | ❌ | ✅ |
| End-to-end validation | ❌ | ✅ |

## CI/CD Integration

### GitHub Actions

```yaml
name: Terraform Tests

on:
  pull_request:
    branches: [ main ]
  push:
    branches: [ main ]

jobs:
  terraform-test:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Setup Terraform
        uses: hashicorp/setup-terraform@v3
        with:
          terraform_version: 1.9.0

      - name: Terraform Format Check
        run: terraform fmt -check -recursive

      - name: Terraform Init
        run: terraform init

      - name: Terraform Validate
        run: terraform validate

      - name: Run Terraform Tests
        run: terraform test -verbose
        env:
          AWS_ACCESS_KEY_ID: ${{ secrets.AWS_ACCESS_KEY_ID }}
          AWS_SECRET_ACCESS_KEY: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
```

### GitLab CI

```yaml
terraform-test:
  image: hashicorp/terraform:1.9
  stage: test
  before_script:
    - terraform init
  script:
    - terraform fmt -check -recursive
    - terraform validate
    - terraform test -verbose
  only:
    - merge_requests
    - main
```
