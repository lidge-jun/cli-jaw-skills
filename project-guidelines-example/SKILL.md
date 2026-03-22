---
name: project-guidelines-example
description: Example project-specific skill template based on a real production application — use as a starting point for your own project skills.
---

# Project Guidelines (Example Template)

Template for creating project-specific skills. Adapt the sections below to your own project.

Based on a real production application: [Zenith](https://zenith.chat) — AI-powered customer discovery platform.

## When to Use

Reference a project skill when working on its specific project. A project skill typically contains:
- Architecture overview and file structure
- Code patterns and conventions
- Testing requirements
- Deployment workflow

---

## Architecture Overview

**Tech Stack:**
- **Frontend**: Next.js 15 (App Router), TypeScript, React
- **Backend**: FastAPI (Python), Pydantic models
- **Database**: Supabase (PostgreSQL)
- **AI**: Claude API with tool calling and structured output
- **Deployment**: Google Cloud Run
- **Testing**: Playwright (E2E), pytest (backend), React Testing Library

**Services:**
```
Frontend (Next.js 15 + TypeScript + TailwindCSS)
    │
    ▼
Backend (FastAPI + Python 3.11 + Pydantic)
    │
    ├── Supabase (Database)
    ├── Claude API
    └── Redis (Cache)
```

---

## File Structure

```
project/
├── frontend/src/
│   ├── app/              # Next.js app router pages
│   ├── components/       # React components (ui/, forms/, layouts/)
│   ├── hooks/            # Custom React hooks
│   ├── lib/              # Utilities
│   ├── types/            # TypeScript definitions
│   └── config/           # Configuration
│
├── backend/
│   ├── routers/          # FastAPI route handlers
│   ├── models.py         # Pydantic models
│   ├── main.py           # FastAPI app entry
│   ├── services/         # Business logic
│   └── tests/            # pytest tests
│
├── deploy/               # Deployment configs
└── scripts/              # Utility scripts
```

---

## Code Patterns

### API Response Format (FastAPI)

```python
class ApiResponse(BaseModel, Generic[T]):
    success: bool
    data: Optional[T] = None
    error: Optional[str] = None

    @classmethod
    def ok(cls, data: T) -> "ApiResponse[T]":
        return cls(success=True, data=data)

    @classmethod
    def fail(cls, error: str) -> "ApiResponse[T]":
        return cls(success=False, error=error)
```

### Frontend API Calls (TypeScript)

```typescript
async function fetchApi<T>(
  endpoint: string,
  options?: RequestInit
): Promise<ApiResponse<T>> {
  const response = await fetch(`/api${endpoint}`, {
    ...options,
    headers: { 'Content-Type': 'application/json', ...options?.headers },
  })
  if (!response.ok) return { success: false, error: `HTTP ${response.status}` }
  return await response.json()
}
```

---

## Testing Requirements

### Backend (pytest)
```bash
pytest tests/                          # all tests
pytest tests/ --cov=. --cov-report=html  # with coverage
pytest tests/test_auth.py -v           # specific file
```

### Frontend
```bash
npm run test                  # unit tests
npm run test -- --coverage    # with coverage
npm run test:e2e              # Playwright E2E
```

---

## Deployment

### Pre-Deployment Checklist
- [ ] All tests passing locally
- [ ] Build succeeds (frontend + backend)
- [ ] No hardcoded secrets
- [ ] Environment variables documented
- [ ] Database migrations ready

### Deploy Commands
```bash
cd frontend && npm run build && gcloud run deploy frontend --source .
cd backend && gcloud run deploy backend --source .
```

---

## Project Rules

1. Immutability — prefer returning new instances over mutation
2. TDD — write tests before implementation
3. 80% coverage minimum
4. Many small files — 200–400 lines typical, 800 max
5. Remove debug logging before merging
6. Proper error handling with try/catch
7. Input validation with Pydantic/Zod
