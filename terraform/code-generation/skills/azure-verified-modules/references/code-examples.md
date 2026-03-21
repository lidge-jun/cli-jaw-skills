# AVM Code Examples

## Provider Configuration (TFFR3)

```hcl
terraform {
  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 4.0"
    }
    azapi = {
      source  = "Azure/azapi"
      version = "~> 2.0"
    }
  }
}
```

## for_each with map (TFNFR7)

```hcl
resource "azurerm_subnet" "pair" {
  for_each             = var.subnet_map  # map(string)
  name                 = "${each.value}-pair"
  resource_group_name  = azurerm_resource_group.example.name
  virtual_network_name = azurerm_virtual_network.example.name
  address_prefixes     = ["10.0.1.0/24"]
}
```

## Lifecycle ignore_changes (TFNFR10)

```hcl
# Correct — unquoted attribute
lifecycle {
  ignore_changes = [tags]
}

# Wrong — quoted attribute
lifecycle {
  ignore_changes = ["tags"]
}
```

## Null Comparison for Conditional Creation (TFNFR11)

```hcl
variable "security_group" {
  type = object({
    id = string
  })
  default = null
}
```

## Dynamic Blocks (TFNFR12)

```hcl
dynamic "identity" {
  for_each = <condition> ? [<some_item>] : []
  content {
    # block content
  }
}
```

## Default Values with coalesce (TFNFR13)

```hcl
# Preferred
coalesce(var.new_network_security_group_name, "${var.subnet_name}-nsg")

# Avoid
var.new_network_security_group_name == null ? "${var.subnet_name}-nsg" : var.new_network_security_group_name
```

## Feature Toggles for New Resources (TFNFR34)

```hcl
variable "create_route_table" {
  type     = bool
  default  = false
  nullable = false
}

resource "azurerm_route_table" "this" {
  count = var.create_route_table ? 1 : 0
  # ...
}
```

## Terraform Version Constraints (TFNFR25)

```hcl
terraform {
  required_version = "~> 1.6"
  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 4.0"
    }
  }
}
```

## Output Patterns (TFFR2)

```hcl
# Single resource computed attribute
output "foo" {
  description = "MyResource foo attribute"
  value       = azurerm_resource_myresource.foo
}

# for_each resources — output as map
output "childresource_foos" {
  description = "MyResource children's foo attributes"
  value = {
    for key, value in azurerm_resource_mychildresource : key => value.foo
  }
}

# Sensitive output
output "bar" {
  description = "MyResource bar attribute"
  value       = azurerm_resource_myresource.bar
  sensitive   = true
}
```
