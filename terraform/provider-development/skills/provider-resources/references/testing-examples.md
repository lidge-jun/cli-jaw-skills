# Testing — Full Examples

## Basic Acceptance Test

```go
func TestAccExampleResource_basic(t *testing.T) {
    ctx := acctest.Context(t)
    rName := sdkacctest.RandomWithPrefix(acctest.ResourcePrefix)
    resourceName := "provider_example.test"

    resource.ParallelTest(t, resource.TestCase{
        PreCheck:                 func() { acctest.PreCheck(ctx, t) },
        ProtoV5ProviderFactories: acctest.ProtoV5ProviderFactories,
        CheckDestroy:             testAccCheckExampleDestroy(ctx),
        Steps: []resource.TestStep{
            {
                Config: testAccExampleConfig_basic(rName),
                Check: resource.ComposeTestCheckFunc(
                    testAccCheckExampleExists(ctx, resourceName),
                    resource.TestCheckResourceAttr(resourceName, "name", rName),
                    resource.TestCheckResourceAttrSet(resourceName, "arn"),
                ),
            },
            {
                ResourceName:      resourceName,
                ImportState:       true,
                ImportStateVerify: true,
            },
        },
    })
}
```

## Disappears Test

```go
func TestAccExampleResource_disappears(t *testing.T) {
    ctx := acctest.Context(t)
    rName := sdkacctest.RandomWithPrefix(acctest.ResourcePrefix)
    resourceName := "provider_example.test"

    resource.ParallelTest(t, resource.TestCase{
        PreCheck:                 func() { acctest.PreCheck(ctx, t) },
        ProtoV5ProviderFactories: acctest.ProtoV5ProviderFactories,
        CheckDestroy:             testAccCheckExampleDestroy(ctx),
        Steps: []resource.TestStep{
            {
                Config: testAccExampleConfig_basic(rName),
                Check: resource.ComposeTestCheckFunc(
                    testAccCheckExampleExists(ctx, resourceName),
                    acctest.CheckResourceDisappears(ctx, acctest.Provider, ResourceExample(), resourceName),
                ),
                ExpectNonEmptyPlan: true,
            },
        },
    })
}
```

## Test Helper Functions

```go
func testAccCheckExampleExists(ctx context.Context, name string) resource.TestCheckFunc {
    return func(s *terraform.State) error {
        rs, ok := s.RootModule().Resources[name]
        if !ok {
            return fmt.Errorf("Not found: %s", name)
        }

        conn := acctest.Provider.Meta().(*conns.Client).ExampleClient(ctx)
        _, err := findExampleByID(ctx, conn, rs.Primary.ID)

        return err
    }
}

func testAccCheckExampleDestroy(ctx context.Context) resource.TestCheckFunc {
    return func(s *terraform.State) error {
        conn := acctest.Provider.Meta().(*conns.Client).ExampleClient(ctx)

        for _, rs := range s.RootModule().Resources {
            if rs.Type != "provider_example" {
                continue
            }

            _, err := findExampleByID(ctx, conn, rs.Primary.ID)
            if tfresource.NotFound(err) {
                continue
            }
            if err != nil {
                return err
            }

            return fmt.Errorf("Example %s still exists", rs.Primary.ID)
        }

        return nil
    }
}
```

## Running Tests

```bash
# Compile check
go test -c -o /dev/null ./internal/service/<service>

# Run acceptance tests
TF_ACC=1 go test ./internal/service/<service> -run TestAccExample -v -timeout 60m

# Run sweeper to clean up
TF_ACC=1 go test ./internal/service/<service> -sweep=<region> -v
```
