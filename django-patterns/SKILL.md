---
name: django-patterns
description: Django architecture patterns, REST API design with DRF, ORM best practices, caching, signals, middleware, and production-grade Django apps.
---

# Django Development Patterns

Production-grade Django architecture patterns for scalable, maintainable applications.

## When to Activate

- Building Django web applications
- Designing Django REST Framework APIs
- Working with Django ORM and models
- Setting up Django project structure
- Implementing caching, signals, middleware

## Project Structure

### Recommended Layout

```
myproject/
├── config/
│   ├── __init__.py
│   ├── settings/
│   │   ├── __init__.py
│   │   ├── base.py          # Base settings
│   │   ├── development.py   # Dev settings
│   │   ├── production.py    # Production settings
│   │   └── test.py          # Test settings
│   ├── urls.py
│   ├── wsgi.py
│   └── asgi.py
├── manage.py
└── apps/
    ├── __init__.py
    ├── users/
    │   ├── __init__.py
    │   ├── models.py
    │   ├── views.py
    │   ├── serializers.py
    │   ├── urls.py
    │   ├── permissions.py
    │   ├── filters.py
    │   ├── services.py
    │   └── tests/
    └── products/
        └── ...
```

Split settings across `base.py`, `development.py`, `production.py`, and `test.py`. See `references/code-examples.md` § Split Settings for full configuration.

## Model Design Patterns

### Model Best Practices

- Use `AbstractUser` for custom user models with email-based auth
- Add `Meta` with `db_table`, `ordering`, `indexes`, `constraints`
- Use `DecimalField` for money, `PositiveIntegerField` for counts
- Override `save()` for auto-generated fields (e.g., slug from name)

```python
class Product(models.Model):
    name = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    price = models.DecimalField(max_digits=10, decimal_places=2,
                                validators=[MinValueValidator(0)])
    stock = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    category = models.ForeignKey('Category', on_delete=models.CASCADE,
                                  related_name='products')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['slug']),
            models.Index(fields=['category', 'is_active']),
        ]
```

### Custom QuerySet

Chain reusable query methods via a custom `QuerySet.as_manager()`:

```python
class ProductQuerySet(models.QuerySet):
    def active(self):
        return self.filter(is_active=True)

    def with_category(self):
        return self.select_related('category')

    def in_stock(self):
        return self.filter(stock__gt=0)

# Usage: Product.objects.active().with_category().in_stock()
```

See `references/code-examples.md` § Model Design for full models, QuerySet, and Manager examples.

## Django REST Framework Patterns

### Serializer Patterns

- Use separate serializers for read vs. create/update
- Add field-level and cross-field validation
- Use `SerializerMethodField` for computed fields
- Use `source='related.field'` for nested attribute access

```python
class ProductSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)

    class Meta:
        model = Product
        fields = ['id', 'name', 'slug', 'price', 'category_name', 'created_at']
        read_only_fields = ['id', 'slug', 'created_at']

    def validate_price(self, value):
        if value < 0:
            raise serializers.ValidationError("Price cannot be negative.")
        return value
```

### ViewSet Patterns

- Use `get_serializer_class()` for action-specific serializers
- Use `perform_create()` to inject request context (e.g., `created_by`)
- Add `@action` for custom endpoints beyond CRUD
- Configure `filter_backends`, `search_fields`, `ordering_fields`

```python
class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.select_related('category')
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ['name', 'description']

    def get_serializer_class(self):
        if self.action == 'create':
            return ProductCreateSerializer
        return ProductSerializer

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)
```

See `references/code-examples.md` § DRF Serializers and § DRF ViewSets for complete implementations.

## Service Layer Pattern

Encapsulate business logic in service classes, keeping views thin. Use `@transaction.atomic` for multi-step operations.

See `references/code-examples.md` § Service Layer for OrderService example.

## Caching Strategies

| Level | Approach | Duration |
|-------|----------|----------|
| View | `@cache_page(timeout)` decorator | Minutes |
| Template | `{% cache ttl key %}` fragment tag | Minutes |
| Low-level | `cache.get()` / `cache.set()` | Minutes–Hours |
| QuerySet | Cache `list(queryset)` results | Minutes–Hours |

See `references/code-examples.md` § Caching for examples of each level.

## Signals

Use `post_save` / `pre_save` signals for cross-cutting concerns (e.g., auto-creating profiles). Register in `AppConfig.ready()`.

See `references/code-examples.md` § Signals for implementation.

## Middleware

Use middleware for request/response processing (logging, user tracking, timing). Extend `MiddlewareMixin` with `process_request` / `process_response`.

See `references/code-examples.md` § Middleware for examples.

## Performance Optimization

### N+1 Query Prevention

```python
# Avoid: N+1 queries (separate query per product)
for product in Product.objects.all():
    print(product.category.name)

# Prefer: single query with select_related (FK)
for product in Product.objects.select_related('category').all():
    print(product.category.name)

# Prefer: prefetch_related for M2M
products = Product.objects.prefetch_related('tags').all()
```

### Database Indexing

Add indexes in `Meta.indexes` for columns used in `WHERE`, `ORDER BY`, and frequent JOINs. Use composite indexes for multi-column filtering.

### Bulk Operations

Use `bulk_create()` and `bulk_update()` for batch data operations. See `references/code-examples.md` § Bulk Operations.

## Quick Reference

| Pattern | Description |
|---------|-------------|
| Split settings | Separate dev/prod/test settings |
| Custom QuerySet | Reusable query methods |
| Service Layer | Business logic separation |
| ViewSet | REST API endpoints |
| Serializer validation | Request/response transformation |
| select_related | Foreign key optimization |
| prefetch_related | Many-to-many optimization |
| Cache first | Cache expensive operations |
| Signals | Event-driven actions |
| Middleware | Request/response processing |

For production applications, structure and organization matter more than concise code. Build for maintainability.
