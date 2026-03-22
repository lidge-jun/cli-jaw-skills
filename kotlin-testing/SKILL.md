---
name: kotlin-testing
description: Kotlin testing patterns with Kotest, MockK, coroutine testing, property-based testing, and Kover coverage. Follows TDD methodology with idiomatic Kotlin practices.
---

# Kotlin Testing Patterns

Comprehensive Kotlin testing patterns for writing reliable, maintainable tests following TDD methodology with Kotest and MockK.

## When to Use

- Writing new Kotlin functions or classes
- Adding test coverage to existing Kotlin code
- Implementing property-based or data-driven tests
- Following TDD workflow in Kotlin projects
- Configuring Kover for code coverage

## How It Works

1. **Identify target code** — Find the function, class, or module to test
2. **Write a Kotest spec** — Choose a spec style (FunSpec, StringSpec, BehaviorSpec, DescribeSpec) matching the test scope
3. **Mock dependencies** — Use MockK to isolate the unit under test
4. **Run tests (RED)** — Verify the test fails with the expected error
5. **Implement code (GREEN)** — Write minimal code to pass the test
6. **Refactor** — Improve the implementation while keeping tests green
7. **Check coverage** — Run `./gradlew koverHtmlReport` and verify 80%+ coverage

## TDD Cycle

```
RED     → Write a failing test first
GREEN   → Write minimal code to pass the test
REFACTOR → Improve code while keeping tests green
REPEAT  → Continue with next requirement
```

For full step-by-step EmailValidator walkthrough, see `references/code-examples.md`.

## Kotest Spec Styles

### FunSpec (Recommended for Most Tests)

```kotlin
class UserServiceTest : FunSpec({
    val repository = mockk<UserRepository>()
    val service = UserService(repository)

    test("getUser returns user when found") {
        val expected = User(id = "1", name = "Alice")
        coEvery { repository.findById("1") } returns expected

        val result = service.getUser("1")

        result shouldBe expected
    }

    test("getUser throws when not found") {
        coEvery { repository.findById("999") } returns null

        shouldThrow<UserNotFoundException> {
            service.getUser("999")
        }
    }
})
```

For StringSpec, BehaviorSpec, and DescribeSpec examples, see `references/code-examples.md`.

## Kotest Matchers

### Core Matchers

```kotlin
// Equality
result shouldBe expected
result shouldNotBe unexpected

// Strings
name shouldStartWith "Al"
name shouldEndWith "ice"
name shouldContain "lic"
name shouldMatch Regex("[A-Z][a-z]+")
name.shouldBeBlank()

// Collections
list shouldContain "item"
list shouldHaveSize 3
list.shouldBeSorted()
list.shouldContainAll("a", "b", "c")
list.shouldBeEmpty()

// Nulls
result.shouldNotBeNull()
result.shouldBeNull()

// Types
result.shouldBeInstanceOf<User>()

// Numbers
count shouldBeGreaterThan 0
price shouldBeInRange 1.0..100.0

// Exceptions
shouldThrow<IllegalArgumentException> {
    validateAge(-1)
}.message shouldBe "Age must be positive"

shouldNotThrow<Exception> {
    validateAge(25)
}
```

For custom matchers, see `references/code-examples.md`.

## MockK Basics

```kotlin
class UserServiceTest : FunSpec({
    val repository = mockk<UserRepository>()
    val logger = mockk<Logger>(relaxed = true) // Returns defaults for all calls
    val service = UserService(repository, logger)

    beforeTest {
        clearMocks(repository, logger)
    }

    test("findUser delegates to repository") {
        val expected = User(id = "1", name = "Alice")
        every { repository.findById("1") } returns expected

        val result = service.findUser("1")

        result shouldBe expected
        verify(exactly = 1) { repository.findById("1") }
    }

    test("suspend function mocking") {
        coEvery { repository.findById("1") } returns User(id = "1", name = "Alice")

        val result = service.getUser("1")

        result.name shouldBe "Alice"
        coVerify { repository.findById("1") }
    }
})
```

For advanced MockK patterns (argument capture, spy, coroutine mocking), see `references/code-examples.md`.

## Coroutine Testing

Use `runTest` from `kotlinx.coroutines.test` for suspend functions and coroutines:

```kotlin
test("concurrent fetches complete together") {
    runTest {
        val service = DataService(testScope = this)
        val result = service.fetchAllData()
        result.users.shouldNotBeEmpty()
    }
}
```

For Flow testing, TestDispatcher, and advanced coroutine patterns, see `references/code-examples.md`.

## Property-Based & Data-Driven Testing

**Property-based testing**: Automatically generates test cases using Kotest's `Arb` (arbitrary) generators. Great for pure functions.

**Data-driven testing**: `withData` allows parameterized test cases for multiple inputs.

Examples and custom generators available in `references/code-examples.md`.

## Test Lifecycle and Fixtures

Use `beforeTest`/`afterTest` for test-level setup/cleanup, and `beforeSpec`/`afterSpec` for suite-level initialization.

```kotlin
beforeSpec { db = setupDatabase() }
afterSpec { db.close() }
beforeTest { db.clear() }
```

Kotest extensions enable reusable test infrastructure. See `references/code-examples.md` for DatabaseExtension example.

## Kover Coverage Configuration

### Gradle Setup

```kotlin
// build.gradle.kts
plugins {
    id("org.jetbrains.kotlinx.kover") version "0.9.7"
}

kover {
    reports {
        total {
            html { onCheck = true }
            xml { onCheck = true }
        }
        filters {
            excludes {
                classes("*.generated.*", "*.config.*")
            }
        }
        verify {
            rule {
                minBound(80) // Fail build below 80% coverage
            }
        }
    }
}
```

### Coverage Commands

```bash
./gradlew koverHtmlReport     # Generate HTML report
./gradlew koverVerify         # Verify coverage meets thresholds
./gradlew koverXmlReport      # Generate XML for CI

# View report (macOS)
open build/reports/kover/html/index.html
```

### Coverage Targets

| Code Type | Target |
|-----------|--------|
| Critical business logic | 100% |
| Public APIs | 90%+ |
| General code | 80%+ |
| Generated / config code | Exclude |

## Testing Commands

```bash
./gradlew test                                  # Run all tests
./gradlew test --tests "com.example.UserServiceTest"  # Run specific class
./gradlew test --tests "com.example.UserServiceTest.getUser*"  # Run by pattern
./gradlew test --info                          # Verbose output
./gradlew koverHtmlReport                      # Tests + coverage report
./gradlew detekt                               # Static analysis
./gradlew ktlintCheck                          # Formatting check
./gradlew test --continuous                    # Watch mode
```

## Effective Patterns

- **Write tests FIRST** — Follow TDD strictly. RED phase catches bugs early.
- **Use Kotest consistently** — Pick a spec style (FunSpec recommended) and stick with it across the project.
- **Mock suspend functions with `coEvery`/`coVerify`** — Never use `every`/`verify` for coroutines.
- **Use `runTest` for coroutines** — Never use `Thread.sleep()` in coroutine tests; use `advanceTimeBy` or `advanceUntilIdle`.
- **Test behavior, not implementation** — Focus on what the code does, not how it does it.
- **Use real instances for immutable objects** — Don't mock data classes; create real test fixtures.
- **Leverage property-based testing** — Excellent for pure functions and edge case discovery.
- **Keep fixtures in `data class`es** — Makes test intent clear and setup reusable.
- **Use `relaxed = true` for loggers/observers** — They're usually not critical to test assertions.

## Patterns to Avoid

- Mixing test frameworks — Kotest and JUnit don't play well together; commit fully to Kotest.
- Mocking immutable objects — Use real instances instead for simplicity.
- Complex test setup — If setup takes >10 lines, extract to a helper or factory.
- Flaky tests from timing — Use `advanceTimeBy` or `runTest` scheduler control instead of delays.
- Testing private functions directly — Private functions are tested indirectly via public APIs.
- Ignoring test failures — Flaky tests hide real bugs; fix or skip immediately.
- Tight coupling to implementation — Refactorings should not require rewriting tests.

## Quick References

- **Kotest spec styles**: See `references/code-examples.md` for StringSpec, BehaviorSpec, DescribeSpec
- **EmailValidator TDD walkthrough**: Full RED-GREEN-REFACTOR example in `references/code-examples.md`
- **Advanced MockK**: Argument capture, spy, coroutine mocking in `references/code-examples.md`
- **Flow testing**: Testing Kotlin Flows and debounce patterns in `references/code-examples.md`
- **Custom matchers**: Build domain-specific assertions in `references/code-examples.md`
- **CI/CD integration**: GitHub Actions YAML workflow in `references/code-examples.md`

---

**Remember**: Tests are documentation. They show how your Kotlin code is meant to be used. Use Kotest's expressive matchers to make tests readable and MockK for clean mocking of dependencies.
