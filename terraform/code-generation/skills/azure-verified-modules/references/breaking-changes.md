# Breaking Changes Reference (TFNFR35)

Review these patterns when making changes to avoid unintended breaking changes.

## Resource Block Breaking Changes

1. Adding new resource without conditional creation
2. Adding arguments with non-default values
3. Adding nested blocks without `dynamic`
4. Renaming resources without `moved` blocks
5. Changing `count` to `for_each` or vice versa

## Variable/Output Block Breaking Changes

1. Deleting or renaming variables
2. Changing variable `type`
3. Changing variable `default` values
4. Changing `nullable` to false
5. Changing `sensitive` from false to true
6. Adding variables without `default`
7. Deleting outputs
8. Changing output `value`
9. Changing output `sensitive` value

## Mitigation

- New resources in minor/patch versions: add a toggle variable defaulting to `false` (TFNFR34)
- Renamed resources: use `moved` blocks
- Changed variable types: release as major version
