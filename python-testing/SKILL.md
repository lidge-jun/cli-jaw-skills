---
name: python-testing
description: Python testing strategies using pytest, TDD methodology, fixtures, mocking, parametrization, and coverage requirements.
---

# Python Testing Patterns

Comprehensive testing strategies for Python applications using pytest, TDD methodology, and best practices.

> Full code examples: [references/code-examples.md](references/code-examples.md)

## When to Activate

- Writing new Python code (follow TDD: red, green, refactor)
- Designing test suites for Python projects
- Reviewing Python test coverage
- Setting up testing infrastructure

## Core Testing Philosophy

### Test-Driven Development (TDD)

Follow the TDD cycle:

1. **Red**: Write a failing test for the desired behavior
2. **Green**: Write minimal code to make the test pass
3. **Refactor**: Improve code while keeping tests green

```python
# Step 1: Write failing test (Red)
def test_add_numbers():
    result = add(2, 3)
    assert result == 5

# Step 2: Write minimal implementation (Green)
def add(a, b):
    return a + b

# Step 3: Refactor if needed
```

### Coverage Requirements

- **Target**: 80%+ code coverage
- **Critical paths**: 100% coverage required

```bash
pytest --cov=mypackage --cov-report=term-missing --cov-report=html
```

## pytest Fundamentals

### Basic Test Structure

```python
import pytest

def test_addition():
    assert 2 + 2 == 4

def test_string_uppercase():
    assert "hello".upper() == "HELLO"
```

### Assertions

| Assertion | Usage |
|-----------|-------|
| `assert result == expected` | Equality |
| `assert result` / `assert not result` | Truthiness |
| `assert result is None` | Identity |
| `assert item in collection` | Membership |
| `assert isinstance(result, str)` | Type check |
| `pytest.raises(ValueError)` | Exception |
| `pytest.raises(ValueError, match="msg")` | Exception with message |

```python
# Exception testing
with pytest.raises(ValueError, match="invalid input"):
    raise ValueError("invalid input provided")

# Check exception attributes
with pytest.raises(ValueError) as exc_info:
    raise ValueError("error message")
assert str(exc_info.value) == "error message"
```

## Fixtures

Fixtures provide reusable test setup. See [references/code-examples.md](references/code-examples.md) for full examples.

### Key Concepts

- **Basic**: Return test data with `@pytest.fixture`
- **Setup/Teardown**: Use `yield` to split setup and cleanup
- **Scopes**: `function` (default), `module`, `session`
- **Parameters**: `@pytest.fixture(params=[...])` for multi-run fixtures
- **Autouse**: `autouse=True` runs automatically for every test
- **Shared**: Put shared fixtures in `conftest.py`

```python
@pytest.fixture
def database():
    db = Database(":memory:")
    db.create_tables()
    yield db
    db.close()

def test_query(database):
    result = database.query("SELECT * FROM users")
    assert len(result) > 0
```

## Parametrization

Run the same test with different inputs:

```python
@pytest.mark.parametrize("a,b,expected", [
    (2, 3, 5),
    (0, 0, 0),
    (-1, 1, 0),
    (100, 200, 300),
])
def test_add(a, b, expected):
    assert add(a, b) == expected
```

Use `ids=` for readable test names:

```python
@pytest.mark.parametrize("input,expected", [
    ("valid@email.com", True),
    ("invalid", False),
], ids=["valid-email", "missing-at"])
def test_email_validation(input, expected):
    assert is_valid_email(input) is expected
```

## Markers and Test Selection

### Custom Markers

```python
@pytest.mark.slow
def test_slow_operation():
    time.sleep(5)

@pytest.mark.integration
def test_api_integration():
    response = requests.get("https://api.example.com")
    assert response.status_code == 200
```

### Running by Marker

```bash
pytest -m "not slow"              # Skip slow tests
pytest -m integration             # Only integration tests
pytest -m "unit and not slow"     # Combine markers
```

### Marker Registration (pytest.ini)

```ini
[pytest]
markers =
    slow: marks tests as slow
    integration: marks tests as integration tests
    unit: marks tests as unit tests
```

## Mocking and Patching

Mock external dependencies to keep tests fast and isolated. See [references/code-examples.md](references/code-examples.md) for all patterns.

### Core Patterns

```python
from unittest.mock import patch, Mock

@patch("mypackage.external_api_call")
def test_with_mock(api_call_mock):
    api_call_mock.return_value = {"status": "success"}
    result = my_function()
    api_call_mock.assert_called_once()
    assert result["status"] == "success"
```

Key mocking techniques:
- `return_value` — set what the mock returns
- `side_effect = Exception(...)` — make the mock raise
- `autospec=True` — catch API misuse
- `mock_open` — mock file operations
- `PropertyMock` — mock properties

## Testing Async Code

```python
@pytest.mark.asyncio
async def test_async_function():
    result = await async_add(2, 3)
    assert result == 5
```

Use `assert_awaited_once()` instead of `assert_called_once()` for async mocks.

## Test Organization

```
tests/
├── conftest.py           # Shared fixtures
├── unit/                 # Unit tests
│   ├── test_models.py
│   └── test_services.py
├── integration/          # Integration tests
│   └── test_api.py
└── e2e/                  # End-to-end tests
    └── test_user_flow.py
```

Group related tests in classes:

```python
class TestUserService:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.service = UserService()

    def test_create_user(self):
        user = self.service.create_user("Alice")
        assert user.name == "Alice"
```

## Best Practices

### Do

- Follow TDD: write tests before code (red-green-refactor)
- Test one behavior per test
- Use descriptive names: `test_user_login_with_invalid_credentials_fails`
- Use fixtures to eliminate duplication
- Mock external dependencies (network, database, filesystem)
- Test edge cases: empty inputs, None values, boundary conditions
- Aim for 80%+ coverage on critical paths
- Keep tests fast; use marks to separate slow tests

### Avoid

- Testing implementation details instead of behavior
- Complex conditionals in tests
- Ignoring test failures
- Testing third-party library internals
- Sharing mutable state between tests
- Catching exceptions in tests (use `pytest.raises` instead)
- Over-specific mocks that make tests brittle

## pytest Configuration (pyproject.toml)

```toml
[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py"]
python_classes = ["Test*"]
python_functions = ["test_*"]
addopts = [
    "--strict-markers",
    "--cov=mypackage",
    "--cov-report=term-missing",
]
markers = [
    "slow: marks tests as slow",
    "integration: marks tests as integration tests",
    "unit: marks tests as unit tests",
]
```

## Running Tests

```bash
pytest                              # Run all tests
pytest tests/test_utils.py          # Run specific file
pytest tests/test_utils.py::test_fn # Run specific test
pytest -v                           # Verbose output
pytest --cov=mypackage              # With coverage
pytest -m "not slow"                # Skip slow tests
pytest -x                           # Stop on first failure
pytest --maxfail=3                  # Stop after N failures
pytest --lf                         # Run last failed
pytest -k "test_user"               # Run by pattern
pytest --pdb                        # Debugger on failure
```

## Quick Reference

| Pattern | Usage |
|---------|-------|
| `pytest.raises()` | Test expected exceptions |
| `@pytest.fixture()` | Create reusable test fixtures |
| `@pytest.mark.parametrize()` | Run tests with multiple inputs |
| `@pytest.mark.slow` | Mark slow tests |
| `pytest -m "not slow"` | Skip slow tests |
| `@patch()` | Mock functions and classes |
| `tmp_path` fixture | Automatic temp directory |
| `pytest --cov` | Generate coverage report |
| `assert` | Simple and readable assertions |

Tests are code too — keep them clean, readable, and maintainable.
