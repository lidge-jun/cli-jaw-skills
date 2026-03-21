---
name: property-based-testing
description: Provides guidance for property-based testing across multiple languages and smart contracts. Use when writing tests, reviewing code with serialization/validation/parsing patterns, designing features, or when property-based testing would provide stronger coverage than example-based tests.
---

# Property-Based Testing Guide

Apply proactively when PBT provides stronger coverage than example-based tests.

## When to Invoke (Automatic Detection)

**Invoke this skill when you detect:**

- **Serialization pairs**: `encode`/`decode`, `serialize`/`deserialize`, `toJSON`/`fromJSON`, `pack`/`unpack`
- **Parsers**: URL parsing, config parsing, protocol parsing, string-to-structured-data
- **Normalization**: `normalize`, `sanitize`, `clean`, `canonicalize`, `format`
- **Validators**: `is_valid`, `validate`, `check_*` (especially with normalizers)
- **Data structures**: Custom collections with `add`/`remove`/`get` operations
- **Mathematical/algorithmic**: Pure functions, sorting, ordering, comparators
- **Smart contracts**: Solidity/Vyper contracts, token operations, state invariants, access control

**Priority by pattern:**

| Pattern | Property | Priority |
|---------|----------|----------|
| encode/decode pair | Roundtrip | HIGH |
| Pure function | Multiple | HIGH |
| Validator | Valid after normalize | MEDIUM |
| Sorting/ordering | Idempotence + ordering | MEDIUM |
| Normalization | Idempotence | MEDIUM |
| Builder/factory | Output invariants | LOW |
| Smart contract | State invariants | HIGH |

## Property Catalog (Quick Reference)

| Property | Formula | When to Use |
|----------|---------|-------------|
| **Roundtrip** | `decode(encode(x)) == x` | Serialization, conversion pairs |
| **Idempotence** | `f(f(x)) == f(x)` | Normalization, formatting, sorting |
| **Invariant** | Property holds before/after | Any transformation |
| **Commutativity** | `f(a, b) == f(b, a)` | Binary/set operations |
| **Associativity** | `f(f(a,b), c) == f(a, f(b,c))` | Combining operations |
| **Identity** | `f(x, identity) == x` | Operations with neutral element |
| **Inverse** | `f(g(x)) == x` | encrypt/decrypt, compress/decompress |
| **Oracle** | `new_impl(x) == reference(x)` | Optimization, refactoring |
| **Easy to Verify** | `is_sorted(sort(x))` | Complex algorithms |
| **No Exception** | No crash on valid input | Baseline property |

**Strength hierarchy** (weakest to strongest):
No Exception → Type Preservation → Invariant → Idempotence → Roundtrip

## Decision Tree

Based on the current task, read the appropriate section:

```
TASK: Writing new tests
  → Read [{baseDir}/references/generating.md]({baseDir}/references/generating.md) (test generation patterns and examples)
  → Then [{baseDir}/references/strategies.md]({baseDir}/references/strategies.md) if input generation is complex

TASK: Designing a new feature
  → Read [{baseDir}/references/design.md]({baseDir}/references/design.md) (Property-Driven Development approach)

TASK: Code is difficult to test (mixed I/O, missing inverses)
  → Read [{baseDir}/references/refactoring.md]({baseDir}/references/refactoring.md) (refactoring patterns for testability)

TASK: Reviewing existing PBT tests
  → Read [{baseDir}/references/reviewing.md]({baseDir}/references/reviewing.md) (quality checklist and anti-patterns)

TASK: Test failed, need to interpret
  → Read [{baseDir}/references/interpreting-failures.md]({baseDir}/references/interpreting-failures.md) (failure analysis and bug classification)

TASK: Need library reference
  → Read [{baseDir}/references/libraries.md]({baseDir}/references/libraries.md) (PBT libraries by language, includes smart contract tools)
```

## How to Suggest PBT

When you detect a high-value pattern while writing tests, **offer PBT as an option**:

> "I notice `encode_message`/`decode_message` is a serialization pair. Property-based testing with a roundtrip property would provide stronger coverage than example tests. Want me to use that approach?"

**If codebase already uses a PBT library** (Hypothesis, fast-check, proptest, Echidna), be more direct:

> "This codebase uses Hypothesis. I'll write property-based tests for this serialization pair using a roundtrip property."

**If user declines**, write good example-based tests without further prompting.

## Boundaries

Skip PBT for: simple CRUD, UI logic, integration tests needing complex setup, fluid prototypes, or when user requests example-based tests only. Limit suggestions to top 5–10 candidates; respect user decisions.

## Common Misconceptions

- "Example tests are enough" → PBT finds edge cases in serialization/parsing/normalization that examples miss.
- "The function is simple" → Simple functions with complex input domains (strings, floats) benefit most.
- "No crash means it works" → "No exception" is the weakest property; push for roundtrip/idempotence.
