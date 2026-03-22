---
name: kotlin-patterns
description: Idiomatic Kotlin patterns, best practices, and conventions for building robust, efficient, and maintainable Kotlin applications with coroutines, null safety, and DSL builders.
---

# Kotlin Development Patterns

Idiomatic Kotlin patterns and best practices for building robust, efficient, and maintainable applications.

## When to Use

- Writing new Kotlin code
- Reviewing Kotlin code
- Refactoring existing Kotlin code
- Designing Kotlin modules or libraries
- Configuring Gradle Kotlin DSL builds

## How It Works

This skill enforces idiomatic Kotlin conventions across seven key areas: null safety using the type system and safe-call operators, immutability via `val` and `copy()` on data classes, sealed classes and interfaces for exhaustive type hierarchies, structured concurrency with coroutines and `Flow`, extension functions for adding behaviour without inheritance, type-safe DSL builders using `@DslMarker` and lambda receivers, and Gradle Kotlin DSL for build configuration.

## Examples

**Null safety with Elvis operator:**
```kotlin
fun getUserEmail(userId: String): String {
    val user = userRepository.findById(userId)
    return user?.email ?: "unknown@example.com"
}
```

**Sealed class for exhaustive results:**
```kotlin
sealed class Result<out T> {
    data class Success<T>(val data: T) : Result<T>()
    data class Failure(val error: AppError) : Result<Nothing>()
    data object Loading : Result<Nothing>()
}
```

**Structured concurrency with async/await:**
```kotlin
suspend fun fetchUserWithPosts(userId: String): UserProfile =
    coroutineScope {
        val user = async { userService.getUser(userId) }
        val posts = async { postService.getUserPosts(userId) }
        UserProfile(user = user.await(), posts = posts.await())
    }
```

## Core Principles

### 1. Null Safety

Kotlin's type system distinguishes nullable and non-nullable types. Use non-nullable types by default and handle nulls with safe calls and the Elvis operator.

```kotlin
// Prefer non-nullable types with fallback
fun getUser(id: String): User {
    return userRepository.findById(id)
        ?: throw UserNotFoundException("User $id not found")
}

// Use safe calls and Elvis operator
fun getUserEmail(userId: String): String {
    val user = userRepository.findById(userId)
    return user?.email ?: "unknown@example.com"
}

// Avoid force-unwrapping (can throw NPE)
val email = user?.email // Safe; returns null if user is null
```

### 2. Immutability by Default

Prefer `val` over `var`, immutable collections over mutable ones. Use `copy()` to create modified versions.

```kotlin
// Immutable data with copy()
data class User(val id: String, val name: String, val email: String)

fun updateEmail(user: User, newEmail: String): User =
    user.copy(email = newEmail)

// Prefer immutable collections
val users: List<User> = listOf(user1, user2)
val filtered = users.filter { it.email.isNotBlank() }

// Avoid mutable state and mutable collections unless necessary
// var currentUser: User? = null  // Don't do this
// val mutableUsers = mutableListOf<User>()  // Only when truly needed
```

### 3. Expression Bodies and Single-Expression Functions

Use expression bodies for concise, readable functions. Use `when` as an expression for exhaustive pattern matching.

```kotlin
// Expression body
fun isAdult(age: Int): Boolean = age >= 18
fun formatFullName(first: String, last: String): String = "$first $last".trim()
fun User.displayName(): String = name.ifBlank { email.substringBefore('@') }

// When as expression for exhaustive matching
fun statusMessage(code: Int): String = when (code) {
    200 -> "OK"
    404 -> "Not Found"
    500 -> "Internal Server Error"
    else -> "Unknown status: $code"
}

// Avoid unnecessary block bodies
// fun isAdult(age: Int): Boolean { return age >= 18 }  // Use expression instead
```

### 4. Data Classes and Value Classes

Use data classes for value objects. Use value classes (`@JvmInline`) for type-safe zero-overhead wrappers.

```kotlin
// Data class with auto-generated copy, equals, hashCode, toString
data class CreateUserRequest(
    val name: String,
    val email: String,
    val role: Role = Role.USER,
)

// Value class for type safety (zero runtime overhead)
@JvmInline
value class UserId(val value: String) {
    init { require(value.isNotBlank()) { "UserId cannot be blank" } }
}

@JvmInline
value class Email(val value: String) {
    init { require('@' in value) { "Invalid email: $value" } }
}

fun getUser(id: UserId): User = userRepository.findById(id)
```

## Sealed Classes and Interfaces

### Exhaustive Type Hierarchies

Use sealed classes for exhaustive pattern matching. Combine with `when` to ensure all cases are covered.

```kotlin
// Sealed class for exhaustive when expressions
sealed class Result<out T> {
    data class Success<T>(val data: T) : Result<T>()
    data class Failure(val error: AppError) : Result<Nothing>()
    data object Loading : Result<Nothing>()
}

fun <T> Result<T>.getOrNull(): T? = when (this) {
    is Result.Success -> data
    is Result.Failure -> null
    is Result.Loading -> null
}

fun <T> Result<T>.getOrThrow(): T = when (this) {
    is Result.Success -> data
    is Result.Failure -> throw error.toException()
    is Result.Loading -> throw IllegalStateException("Still loading")
}
```

### Sealed Interfaces for API Responses

```kotlin
sealed interface ApiError {
    val message: String

    data class NotFound(override val message: String) : ApiError
    data class Unauthorized(override val message: String) : ApiError
    data class Validation(override val message: String, val field: String) : ApiError
    data class Internal(override val message: String, val cause: Throwable? = null) : ApiError
}

fun ApiError.toStatusCode(): Int = when (this) {
    is ApiError.NotFound -> 404
    is ApiError.Unauthorized -> 401
    is ApiError.Validation -> 422
    is ApiError.Internal -> 500
}
```

## Scope Functions

### When to Use Each

```kotlin
// let: Transform nullable or scoped result
val length: Int? = name?.let { it.trim().length }

// apply: Configure an object, returns the object itself
val user = User().apply {
    name = "Alice"
    email = "alice@example.com"
}

// also: Side effects, returns the object itself
val user = createUser(request).also { logger.info("Created user: ${it.id}") }

// run: Execute a block with receiver, returns the result
val result = connection.run {
    prepareStatement(sql)
    executeQuery()
}

// with: Non-extension form of run
val csv = with(StringBuilder()) {
    appendLine("name,email")
    users.forEach { appendLine("${it.name},${it.email}") }
    toString()
}
```

### Avoid Deeply Nested Scope Functions

Chain safe calls instead. Use `let` only when necessary.

```kotlin
// Prefer direct null-safe chain over nested lets
val city = user?.address?.city
city?.let { process(it) }

// Avoid: Nesting scope functions (hard to read)
// user?.let { u -> u.address?.let { a -> a.city?.let { c -> process(c) } } }
```

## Extension Functions

Add behavior without inheritance. Keep extensions domain-specific and scoped when appropriate.

```kotlin
// Domain-specific extensions
fun String.toSlug(): String =
    lowercase()
        .replace(Regex("[^a-z0-9\\s-]"), "")
        .replace(Regex("\\s+"), "-")
        .trim('-')

fun Instant.toLocalDate(zone: ZoneId = ZoneId.systemDefault()): LocalDate =
    atZone(zone).toLocalDate()

// Collection extensions
fun <T> List<T>.second(): T = this[1]
fun <T> List<T>.secondOrNull(): T? = getOrNull(1)

// Scoped extensions (avoid polluting global namespace)
class UserService {
    private fun User.isActive(): Boolean =
        status == Status.ACTIVE && lastLogin.isAfter(Instant.now().minus(30, ChronoUnit.DAYS))

    fun getActiveUsers(): List<User> = userRepository.findAll().filter { it.isActive() }
}
```

## Coroutines and Flow

Use `coroutineScope` and `async`/`await` for structured concurrency. Use `Flow` for cold, reactive streams with proper cancellation and error handling. See `references/code-examples.md` for detailed examples of structured concurrency, Flow operators, and cancellation patterns.

## Delegation

Use `by` for property delegation (`lazy`, `observable`, map-backed) and interface delegation to reuse implementations.

```kotlin
// Lazy initialization
val expensiveData: List<User> by lazy { userRepository.findAll() }

// Observable property with logging
var name: String by Delegates.observable("initial") { _, old, new ->
    logger.info("Name changed from '$old' to '$new'")
}

// Interface delegation for wrapper classes
class LoggingUserRepository(
    private val delegate: UserRepository,
) : UserRepository by delegate {
    override suspend fun findById(id: String): User? {
        logger.info("Finding user: $id")
        return delegate.findById(id).also { logger.info("Found: ${it?.name ?: "null"}") }
    }
}
```

See `references/code-examples.md` for more delegation patterns.

## DSL Builders

Create type-safe domain-specific languages using `@DslMarker` and lambda receivers. Builders provide readable, fluent syntax.

```kotlin
// Type-safe builder with @DslMarker
@DslMarker
annotation class ServerConfigDsl

@ServerConfigDsl
class ServerConfigBuilder {
    var host: String = "0.0.0.0"
    var port: Int = 8080

    fun build(): ServerConfig = ServerConfig(host, port)
}

fun serverConfig(init: ServerConfigBuilder.() -> Unit): ServerConfig =
    ServerConfigBuilder().apply(init).build()

// Usage: fluent, type-safe configuration
val config = serverConfig {
    host = "127.0.0.1"
    port = 443
}
```

See `references/code-examples.md` for HTML DSL and configuration DSL examples.

## Sequences for Lazy Evaluation

Use sequences for large collections with multiple chained operations to avoid creating intermediate lists. See `references/code-examples.md` for sequence examples and infinite sequence patterns.

## Gradle Kotlin DSL

Use Kotlin DSL in `build.gradle.kts` for type-safe build configuration. See `references/code-examples.md` for a complete example with Ktor, Exposed, Koin, and testing dependencies.

## Error Handling Patterns

Use `Result<T>` or custom sealed classes for domain operations. Use `require()` and `check()` for preconditions.

```kotlin
// Use Result<T> for recoverable errors
suspend fun createUser(request: CreateUserRequest): Result<User> = runCatching {
    require(request.name.isNotBlank()) { "Name cannot be blank" }
    require('@' in request.email) { "Invalid email format" }
    userRepository.save(User(id = UUID.randomUUID().toString(), name = request.name, email = request.email))
}

val displayName = createUser(request)
    .map { it.name }
    .getOrElse { "Unknown" }

// Preconditions and postconditions
fun withdraw(account: Account, amount: Money): Account {
    require(amount.value > 0) { "Amount must be positive: $amount" }
    check(account.balance >= amount) { "Insufficient balance: ${account.balance} < $amount" }
    return account.copy(balance = account.balance - amount)
}
```

## Collection Operations

Key patterns for filtering, grouping, aggregation, and association. See `references/code-examples.md` for advanced examples.

```kotlin
// Chained operations with filter, map, sort
val activeAdminEmails: List<String> = users
    .filter { it.role == Role.ADMIN && it.isActive }
    .sortedBy { it.name }
    .map { it.email }

// Grouping and aggregation
val usersByRole: Map<Role, List<User>> = users.groupBy { it.role }
val oldestByRole: Map<Role, User?> = users.groupBy { it.role }
    .mapValues { (_, users) -> users.minByOrNull { it.createdAt } }

// Associate for efficient map creation
val usersById: Map<UserId, User> = users.associateBy { it.id }

// Partition for splitting into two groups
val (active, inactive) = users.partition { it.isActive }
```

## Quick Reference: Kotlin Idioms

| Idiom | Description |
|-------|-------------|
| `val` over `var` | Prefer immutable variables |
| `data class` | For value objects with equals/hashCode/copy |
| `sealed class/interface` | For restricted type hierarchies |
| `value class` | For type-safe wrappers with zero overhead |
| Expression `when` | Exhaustive pattern matching |
| Safe call `?.` | Null-safe member access |
| Elvis `?:` | Default value for nullables |
| `let`/`apply`/`also`/`run`/`with` | Scope functions for clean code |
| Extension functions | Add behavior without inheritance |
| `copy()` | Immutable updates on data classes |
| `require`/`check` | Precondition assertions |
| Coroutine `async`/`await` | Structured concurrent execution |
| `Flow` | Cold reactive streams |
| `sequence` | Lazy evaluation |
| Delegation `by` | Reuse implementation without inheritance |

## Anti-Patterns to Avoid

```kotlin
// Avoid: Force-unwrapping nullable types
// val name = user!!.name  // Can throw NPE

// Prefer: Safe calls and Elvis operator
val name = user?.name ?: "Unknown"

// Avoid: Mutable data classes
// data class MutableUser(var name: String, var email: String)

// Prefer: Use copy() for updates
val updated = user.copy(name = "New Name")

// Avoid: Using exceptions for control flow
// try { val user = findUser(id) } catch (e: NotFoundException) { }

// Prefer: Nullable return or Result type
val user: User? = findUserOrNull(id)
val result: Result<User> = runCatching { findUser(id) }

// Avoid: GlobalScope for coroutines
// GlobalScope.launch { }

// Prefer: Structured concurrency with proper scope
coroutineScope { launch { } }

// Avoid: Deeply nested scope functions
// user?.let { u -> u.address?.let { a -> a.city?.let { c -> process(c) } } }

// Prefer: Direct null-safe chains
user?.address?.city?.let { process(it) }
```
