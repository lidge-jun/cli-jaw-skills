---
name: python-patterns
description: Pythonic idioms, PEP 8 standards, type hints, and best practices for building robust, efficient, and maintainable Python applications.
---

# Python Development Patterns

Idiomatic Python patterns and best practices for building robust, efficient, and maintainable applications.

> Full code examples: [references/code-examples.md](references/code-examples.md)

## When to Activate

- Writing new Python code
- Reviewing Python code
- Refactoring existing Python code
- Designing Python packages/modules

## Core Principles

### 1. Readability Counts

Python prioritizes readability. Code should be obvious and easy to understand.

```python
# Good: Clear and readable
def get_active_users(users: list[User]) -> list[User]:
    return [user for user in users if user.is_active]
```

### 2. Explicit is Better Than Implicit

Avoid magic; be clear about what your code does.

### 3. EAFP — Easier to Ask Forgiveness Than Permission

Python prefers exception handling over checking conditions.

```python
# Good: EAFP style
try:
    return dictionary[key]
except KeyError:
    return default_value
```

## Type Hints

### Modern Type Hints (Python 3.9+)

Use built-in types directly. Fall back to `typing` module for Python 3.8.

```python
# Python 3.9+
def process_items(items: list[str]) -> dict[str, int]:
    return {item: len(item) for item in items}
```

### Type Aliases and Generics

```python
from typing import TypeVar, Union

JSON = Union[dict[str, Any], list[Any], str, int, float, bool, None]
T = TypeVar('T')

def first(items: list[T]) -> T | None:
    return items[0] if items else None
```

### Protocol-Based Duck Typing

```python
from typing import Protocol

class Renderable(Protocol):
    def render(self) -> str: ...

def render_all(items: list[Renderable]) -> str:
    return "\n".join(item.render() for item in items)
```

## Error Handling

- Catch **specific** exceptions, not bare `except:`
- Chain exceptions with `raise ... from e` to preserve tracebacks
- Build custom exception hierarchies rooted in a single base class

```python
def load_config(path: str) -> Config:
    try:
        with open(path) as f:
            return Config.from_json(f.read())
    except FileNotFoundError as e:
        raise ConfigError(f"Config file not found: {path}") from e
    except json.JSONDecodeError as e:
        raise ConfigError(f"Invalid JSON in config: {path}") from e
```

## Context Managers

Use `with` for all resource management. Create custom context managers with `@contextmanager` or `__enter__`/`__exit__`.

```python
from contextlib import contextmanager

@contextmanager
def timer(name: str):
    start = time.perf_counter()
    yield
    elapsed = time.perf_counter() - start
    print(f"{name} took {elapsed:.4f} seconds")
```

## Comprehensions and Generators

- **List comprehensions**: for simple transformations
- **Generator expressions**: for lazy evaluation (avoid creating large intermediate lists)
- **Generator functions**: for streaming large datasets

```python
# Generator for lazy evaluation — avoids building full list in memory
total = sum(x * x for x in range(1_000_000))
```

Keep comprehensions simple — if they need multiple conditions or nested loops, use a function instead.

## Data Classes and Named Tuples

- Use `@dataclass` for data containers with auto-generated methods
- Use `__post_init__` for validation
- Use `NamedTuple` for immutable data

```python
from dataclasses import dataclass, field

@dataclass
class User:
    id: str
    name: str
    email: str
    created_at: datetime = field(default_factory=datetime.now)
    is_active: bool = True
```

## Decorators

- Use `@functools.wraps` to preserve function metadata
- Parameterized decorators need a three-level nesting pattern
- Class-based decorators are useful for stateful decoration

```python
import functools

def timer(func: Callable) -> Callable:
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        result = func(*args, **kwargs)
        elapsed = time.perf_counter() - start
        print(f"{func.__name__} took {elapsed:.4f}s")
        return result
    return wrapper
```

## Concurrency Patterns

| Task Type | Tool | Why |
|-----------|------|-----|
| I/O-bound (network, files) | `ThreadPoolExecutor` | GIL released during I/O |
| CPU-bound (compute) | `ProcessPoolExecutor` | Separate processes bypass GIL |
| Concurrent I/O (async) | `asyncio` + `aiohttp` | Single-thread event loop |

```python
# Threading for I/O-bound tasks
with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
    future_to_url = {executor.submit(fetch_url, url): url for url in urls}
    for future in concurrent.futures.as_completed(future_to_url):
        url = future_to_url[future]
        results[url] = future.result()
```

## Package Organization

### Standard Layout

```
myproject/
├── src/mypackage/
│   ├── __init__.py
│   ├── main.py
│   ├── api/
│   ├── models/
│   └── utils/
├── tests/
├── pyproject.toml
└── README.md
```

### Import Order

1. Standard library
2. Third-party packages
3. Local modules

Use `isort` for automatic sorting.

### `__init__.py` Exports

```python
__version__ = "1.0.0"
from mypackage.models import User, Post
from mypackage.utils import format_name
__all__ = ["User", "Post", "format_name"]
```

## Memory and Performance

- **`__slots__`**: reduces memory for classes with many instances
- **Generators**: yield items one at a time for large datasets
- **`str.join()`**: O(n) vs O(n²) for string concatenation in loops
- **`pathlib.Path`**: prefer over `os.path` for path operations

## Python Tooling

### Essential Commands

```bash
# Formatting
black .
isort .

# Linting
ruff check .

# Type checking
mypy .

# Testing
pytest --cov=mypackage --cov-report=html

# Security
bandit -r .
pip-audit
```

### pyproject.toml Configuration

```toml
[project]
name = "mypackage"
version = "1.0.0"
requires-python = ">=3.9"
dependencies = ["requests>=2.31.0", "pydantic>=2.0.0"]

[project.optional-dependencies]
dev = ["pytest>=7.4.0", "black>=23.0.0", "ruff>=0.1.0", "mypy>=1.5.0"]

[tool.black]
line-length = 88
target-version = ['py39']

[tool.ruff]
line-length = 88
select = ["E", "F", "I", "N", "W"]

[tool.mypy]
python_version = "3.9"
warn_return_any = true
disallow_untyped_defs = true

[tool.pytest.ini_options]
testpaths = ["tests"]
addopts = "--cov=mypackage --cov-report=term-missing"
```

## Quick Reference: Python Idioms

| Idiom | Description |
|-------|-------------|
| EAFP | Easier to Ask Forgiveness than Permission |
| Context managers | Use `with` for resource management |
| List comprehensions | For simple transformations |
| Generators | For lazy evaluation and large datasets |
| Type hints | Annotate function signatures |
| Dataclasses | For data containers with auto-generated methods |
| `__slots__` | For memory optimization |
| f-strings | For string formatting (Python 3.6+) |
| `pathlib.Path` | For path operations (Python 3.4+) |
| `enumerate` | For index-element pairs in loops |

## Anti-Patterns

| Anti-Pattern | Fix |
|---|---|
| Mutable default args (`def f(x=[])`) | Use `None` and create inside |
| `type(obj) == list` | Use `isinstance(obj, list)` |
| `value == None` | Use `value is None` |
| `from module import *` | Explicit imports |
| Bare `except:` | Catch specific exceptions |
| String concatenation in loops | Use `str.join()` |

Python code should be readable, explicit, and follow the principle of least surprise. When in doubt, prioritize clarity over cleverness.
