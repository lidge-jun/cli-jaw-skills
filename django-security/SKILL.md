---
name: django-security
description: Django security best practices, authentication, authorization, CSRF protection, SQL injection prevention, XSS prevention, and secure deployment configurations.
---

# Django Security Best Practices

Security guidelines for Django applications covering common vulnerabilities and hardening practices.

## When to Activate

- Setting up Django authentication and authorization
- Implementing user permissions and roles
- Configuring production security settings
- Reviewing Django application for security issues
- Deploying Django applications to production

## Core Security Settings

Set all of the following for production deployments:

```python
DEBUG = False
ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', '').split(',')
SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY')

SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'
SESSION_COOKIE_HTTPONLY = True
CSRF_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = 'Lax'
CSRF_COOKIE_SAMESITE = 'Lax'
```

See `references/code-examples.md` § Production Settings for complete configuration including password validators.

## Authentication

- **Custom User Model**: Extend `AbstractUser` with `USERNAME_FIELD = 'email'`. Set `AUTH_USER_MODEL` in settings. Define early — changing later requires migration surgery.
- **Password Hashing**: Use Argon2 as primary hasher (`django.contrib.auth.hashers.Argon2PasswordHasher`).
- **Session Management**: Use cache-backed sessions (`SESSION_ENGINE = 'django.contrib.sessions.backends.cache'`), set reasonable `SESSION_COOKIE_AGE`.

See `references/code-examples.md` § Custom User Model and § Password Hashing.

## Authorization

### Django Permissions

Use `LoginRequiredMixin` and `PermissionRequiredMixin` for class-based views. Define custom permissions in `Meta.permissions`:

```python
class Meta:
    permissions = [
        ('can_publish', 'Can publish posts'),
        ('can_edit_others', 'Can edit posts of others'),
    ]
```

### DRF Permissions

Create custom `BasePermission` subclasses for API authorization:

```python
class IsOwnerOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.author == request.user
```

### Role-Based Access Control

Add a `role` field to the User model with choices like `admin`/`moderator`/`user`. Create mixins like `AdminRequiredMixin` for view-level enforcement.

See `references/code-examples.md` § Authorization for complete permission, RBAC, and mixin examples.

## SQL Injection Prevention

The Django ORM automatically parameterizes queries. Follow these rules:

```python
# Preferred: ORM methods are safe
User.objects.get(username=username)
User.objects.filter(email__iexact=email)

# Preferred: parameterized raw queries
User.objects.raw('SELECT * FROM users WHERE username = %s', [query])

# Avoid: string interpolation in raw queries (vulnerable)
User.objects.raw(f'SELECT * FROM users WHERE username = {username}')
```

Use `Q` objects for complex queries — they are also safe from injection.

## XSS Prevention

### Template Escaping

Django auto-escapes template variables by default:

```django
{{ user_input }}              {# auto-escaped — safe #}
{{ trusted_html|safe }}       {# not escaped — use only for trusted content #}
{{ user_input|striptags }}    {# removes all HTML tags #}

<script>
    var username = {{ username|escapejs }};
</script>
```

### Safe String Handling

Use `format_html()` instead of `mark_safe()` for HTML with variables. If using `mark_safe()`, always `escape()` user input first. See `references/code-examples.md` § XSS Prevention.

### Security Headers

Set `SECURE_CONTENT_TYPE_NOSNIFF`, `X_FRAME_OPTIONS = 'DENY'`, and add a `Content-Security-Policy` header via middleware. See `references/code-examples.md` § Security Headers Middleware.

## CSRF Protection

CSRF protection is enabled by default. Key settings:

```python
CSRF_COOKIE_SECURE = True
CSRF_COOKIE_HTTPONLY = True
CSRF_COOKIE_SAMESITE = 'Lax'
CSRF_TRUSTED_ORIGINS = ['https://example.com']
```

In templates, include `{% csrf_token %}` in every `<form method="post">`. For AJAX requests, read the `csrftoken` cookie and send it as `X-CSRFToken` header. See `references/code-examples.md` § CSRF for the JavaScript helper.

Use `@csrf_exempt` sparingly — only for webhooks from external services.

## File Upload Security

Validate file extension and size before accepting uploads. Use validators on `FileField`:

- Restrict extensions to an allowlist (e.g., `.jpg`, `.png`, `.pdf`)
- Enforce a maximum file size (e.g., 5 MB)
- Serve user uploads from a separate domain or CDN, not directly from the app

See `references/code-examples.md` § File Upload Validation.

## API Security

### Rate Limiting

Configure DRF throttle classes to protect against abuse:
- `AnonRateThrottle`: 100/day for unauthenticated users
- `UserRateThrottle`: 1000/day for authenticated users
- Custom scopes for sensitive endpoints (e.g., `upload`: 10/hour)

### Authentication

Use token-based or JWT authentication for APIs. Set `DEFAULT_PERMISSION_CLASSES` to `IsAuthenticated`.

See `references/code-examples.md` § API Rate Limiting and § API Authentication.

## Environment Variables

Use `django-environ` or `python-decouple` to load secrets from `.env` files. Store `SECRET_KEY`, `DATABASE_URL`, and `ALLOWED_HOSTS` as environment variables. Ensure `.env` is in `.gitignore`.

See `references/code-examples.md` § Environment Variables.

## Logging Security Events

Configure Django's `django.security` and `django.request` loggers to write warnings and errors to dedicated log files.

See `references/code-examples.md` § Logging Security Events.

## Quick Security Checklist

| Check | Description |
|-------|-------------|
| `DEBUG = False` | Set False for production |
| HTTPS only | Force SSL, secure cookies |
| Strong secrets | Use environment variables for SECRET_KEY |
| Password validation | Enable all password validators |
| CSRF protection | Enabled by default — keep it active |
| XSS prevention | Django auto-escapes; avoid `|safe` with user input |
| SQL injection | Use ORM; avoid string concatenation in queries |
| File uploads | Validate file type and size |
| Rate limiting | Throttle API endpoints |
| Security headers | CSP, X-Frame-Options, HSTS |
| Logging | Log security events |
| Updates | Keep Django and dependencies updated |

Security is a continuous process. Review and update practices regularly.
