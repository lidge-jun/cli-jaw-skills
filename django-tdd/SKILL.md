---
name: django-tdd
description: Django testing strategies with pytest-django, TDD methodology, factory_boy, mocking, coverage, and testing Django REST Framework APIs.
---

# Django Testing with TDD

Test-driven development for Django applications using pytest, factory_boy, and Django REST Framework.

## When to Activate

- Writing new Django applications or REST Framework APIs
- Testing Django models, views, and serializers
- Setting up testing infrastructure for Django projects

## TDD Workflow

### Red-Green-Refactor Cycle

```python
# 1. Red — write a failing test
def test_user_creation():
    user = User.objects.create_user(email='test@example.com', password='testpass123')
    assert user.email == 'test@example.com'
    assert user.check_password('testpass123')
    assert not user.is_staff

# 2. Green — make the test pass (create User model or factory)
# 3. Refactor — improve while keeping tests green
```

## Setup

### pytest Configuration

```ini
# pytest.ini
[pytest]
DJANGO_SETTINGS_MODULE = config.settings.test
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts =
    --reuse-db
    --nomigrations
    --cov=apps
    --cov-report=html
    --cov-report=term-missing
    --strict-markers
markers =
    slow: marks tests as slow
    integration: marks tests as integration tests
```

### Test Settings

```python
# config/settings/test.py
from .base import *

DEBUG = True
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
}

class DisableMigrations:
    def __contains__(self, item): return True
    def __getitem__(self, item): return None

MIGRATION_MODULES = DisableMigrations()

PASSWORD_HASHERS = ['django.contrib.auth.hashers.MD5PasswordHasher']
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
CELERY_TASK_ALWAYS_EAGER = True
CELERY_TASK_EAGER_PROPAGATES = True
```

### conftest.py

```python
# tests/conftest.py
import pytest
from django.contrib.auth import get_user_model

User = get_user_model()

@pytest.fixture(autouse=True)
def timezone_settings(settings):
    settings.TIME_ZONE = 'UTC'

@pytest.fixture
def user(db):
    return User.objects.create_user(
        email='test@example.com',
        password='testpass123',
        username='testuser'
    )

@pytest.fixture
def admin_user(db):
    return User.objects.create_superuser(
        email='admin@example.com',
        password='adminpass123',
        username='admin'
    )

@pytest.fixture
def authenticated_client(client, user):
    client.force_login(user)
    return client

@pytest.fixture
def api_client():
    from rest_framework.test import APIClient
    return APIClient()

@pytest.fixture
def authenticated_api_client(api_client, user):
    api_client.force_authenticate(user=user)
    return api_client
```

## Factory Boy

### Factory Setup

```python
# tests/factories.py
import factory
from factory import fuzzy
from django.contrib.auth import get_user_model
from apps.products.models import Product, Category

User = get_user_model()

class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User

    email = factory.Sequence(lambda n: f"user{n}@example.com")
    username = factory.Sequence(lambda n: f"user{n}")
    password = factory.PostGenerationMethodCall('set_password', 'testpass123')
    first_name = factory.Faker('first_name')
    last_name = factory.Faker('last_name')
    is_active = True

class CategoryFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Category

    name = factory.Faker('word')
    slug = factory.LazyAttribute(lambda obj: obj.name.lower())
    description = factory.Faker('text')

class ProductFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Product

    name = factory.Faker('sentence', nb_words=3)
    slug = factory.LazyAttribute(lambda obj: obj.name.lower().replace(' ', '-'))
    description = factory.Faker('text')
    price = fuzzy.FuzzyDecimal(10.00, 1000.00, 2)
    stock = fuzzy.FuzzyInteger(0, 100)
    is_active = True
    category = factory.SubFactory(CategoryFactory)
    created_by = factory.SubFactory(UserFactory)

    @factory.post_generation
    def tags(self, create, extracted, **kwargs):
        if not create or not extracted:
            return
        for tag in extracted:
            self.tags.add(tag)
```

Use `ProductFactory()`, `ProductFactory.create_batch(10)`, or pass overrides like `ProductFactory(price=100)`. See `references/code-examples.md` § Using Factories for full examples.

## Model Testing

Test models with factories and `@pytest.mark.django_db`. Cover creation, string representation, field validation, custom managers, and domain methods.

See `references/code-examples.md` § Model Testing for complete TestUserModel and TestProductModel examples.

## View Testing

Test Django views using `client` (anonymous) and `authenticated_client` fixtures. Verify status codes, context data, redirects, and permission enforcement.

See `references/code-examples.md` § View Testing for full TestProductViews examples.

## DRF API Testing

Test serializers for serialization, deserialization, and field validation. Test API viewsets for CRUD operations, authentication requirements, filtering, and search.

See `references/code-examples.md` § DRF Serializer Testing and § DRF API ViewSet Testing for complete examples.

## Mocking and Patching

Use `@patch` to isolate external service calls. Configure return values or side effects on the mock, then assert both response behavior and mock interactions.

```python
from unittest.mock import patch
import pytest

class TestPaymentView:
    @patch('apps.payments.services.stripe')
    def test_successful_payment(self, mock_stripe, client, user, product):
        mock_stripe.Charge.create.return_value = {
            'id': 'ch_123', 'status': 'succeeded', 'amount': 9999,
        }

        client.force_login(user)
        response = client.post(reverse('payments:process'), {
            'product_id': product.id, 'token': 'tok_visa',
        })

        assert response.status_code == 302
        mock_stripe.Charge.create.assert_called_once()
```

For email testing with `mail.outbox` and `@override_settings`, see `references/code-examples.md` § Mocking Email.

## Integration Testing

Test full user flows (register → login → browse → cart → checkout) end-to-end, combining real views with mocked payment services.

See `references/code-examples.md` § Integration Testing for a complete checkout flow example.

## Testing Best Practices

### Do

- Use factories instead of manual object creation
- Keep tests focused with descriptive names like `test_user_cannot_delete_others_post`
- Test edge cases: empty inputs, None values, boundary conditions
- Mock external services; use fixtures to eliminate duplication
- Test permissions and keep tests fast with `--reuse-db` and `--nomigrations`

### Avoid

- Testing Django internals or third-party library code — trust them to work
- Ignoring failing tests or creating inter-test dependencies
- Over-mocking — mock only external dependencies
- Testing private methods — test the public interface
- Using a production database — always use a test database

## Coverage

```bash
pytest --cov=apps --cov-report=html --cov-report=term-missing
open htmlcov/index.html
```

### Coverage Goals

| Component   | Target Coverage |
|-------------|-----------------|
| Models      | 90%+            |
| Serializers | 85%+            |
| Views       | 80%+            |
| Services    | 90%+            |
| Utilities   | 80%+            |
| Overall     | 80%+            |

## Quick Reference

| Pattern | Usage |
|---------|-------|
| `@pytest.mark.django_db` | Enable database access |
| `client` | Django test client |
| `api_client` | DRF API client |
| `factory.create_batch(n)` | Create multiple objects |
| `patch('module.function')` | Mock external dependencies |
| `override_settings` | Temporarily change settings |
| `force_authenticate()` | Bypass authentication in tests |
| `assertRedirects` | Check for redirects |
| `assertTemplateUsed` | Verify template usage |
| `mail.outbox` | Check sent emails |

Tests are documentation — good tests explain how your code should work. Keep them simple, readable, and maintainable.
