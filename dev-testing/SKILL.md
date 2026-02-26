---
name: dev-testing
description: "Testing and debugging guide for orchestrated sub-agents. Playwright-based webapp testing, reconnaissance-then-action pattern. Auto-injected during debugging phase (phase 4)."
license: Complete terms in LICENSE.txt
---

# Web Application Testing & QA

This skill covers two areas: **test strategy & coverage analysis** (general) and **Playwright browser testing** (specific).

---

## 1. Test Strategy Overview

### Test Pyramid

| Layer | Scope | Tools | Speed | Proportion |
|-------|-------|-------|-------|------------|
| Unit | Single function/component | Jest, Vitest, node:test | Fast | ~70% |
| Integration | Module interactions | Supertest, MSW, test containers | Medium | ~20% |
| E2E | Full user flows | Playwright, Cypress | Slow | ~10% |

### Coverage Targets

| Metric | Minimum | Ideal |
|--------|---------|-------|
| Line coverage | 70% | 85%+ |
| Branch coverage | 60% | 80%+ |
| Function coverage | 80% | 90%+ |

### When to Write Tests

- **Always:** New features, bug fixes, refactoring, behavior changes
- **Test-first preferred:** Write failing test → implement → verify green
- See `tdd/SKILL.md` for the full TDD workflow

---

## 2. Component Test Scaffolding

When testing React/TypeScript components, follow this pattern:

```typescript
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';

describe('ComponentName', () => {
  it('renders with default props', () => {
    render(<Component />);
    expect(screen.getByRole('button')).toBeInTheDocument();
  });

  it('handles user interaction', async () => {
    const onClick = vi.fn();
    render(<Component onClick={onClick} />);
    await userEvent.click(screen.getByRole('button'));
    expect(onClick).toHaveBeenCalledTimes(1);
  });

  it('shows error state', () => {
    render(<Component error="Something failed" />);
    expect(screen.getByText(/something failed/i)).toBeInTheDocument();
  });
});
```

**Prioritize testing:**
- Components with event handlers and state
- Components with conditional rendering
- Components with data fetching
- Form components with validation

---

## 3. Coverage Analysis Workflow

1. **Generate coverage report:**
   ```bash
   npm test -- --coverage
   # or: npx vitest run --coverage
   ```

2. **Review by priority:**
   - P0: Uncovered critical paths (auth, payment, data mutations)
   - P1: Untested error/edge cases in business logic
   - P2: Missing branch coverage in utility functions

3. **Write targeted tests for gaps** — focus on behavior, not line-counting

4. **Verify improvement:**
   ```bash
   npm test -- --coverage --coverageReporters=lcov,json
   ```

---

## 4. Playwright Browser Testing

**Helper Scripts Available**:
- `scripts/with_server.py` - Manages server lifecycle (supports multiple servers)

**Always run scripts with `--help` first** to see usage. DO NOT read the source until you try running the script first and find that a customized solution is abslutely necessary. These scripts can be very large and thus pollute your context window. They exist to be called directly as black-box scripts rather than ingested into your context window.

## Decision Tree: Choosing Your Approach

```
User task → Is it static HTML?
    ├─ Yes → Read HTML file directly to identify selectors
    │         ├─ Success → Write Playwright script using selectors
    │         └─ Fails/Incomplete → Treat as dynamic (below)
    │
    └─ No (dynamic webapp) → Is the server already running?
        ├─ No → Run: python scripts/with_server.py --help
        │        Then use the helper + write simplified Playwright script
        │
        └─ Yes → Reconnaissance-then-action:
            1. Navigate and wait for networkidle
            2. Take screenshot or inspect DOM
            3. Identify selectors from rendered state
            4. Execute actions with discovered selectors
```

## Example: Using with_server.py

To start a server, run `--help` first, then use the helper:

**Single server:**
```bash
python scripts/with_server.py --server "npm run dev" --port 5173 -- python your_automation.py
```

**Multiple servers (e.g., backend + frontend):**
```bash
python scripts/with_server.py \
  --server "cd backend && python server.py" --port 3000 \
  --server "cd frontend && npm run dev" --port 5173 \
  -- python your_automation.py
```

To create an automation script, include only Playwright logic (servers are managed automatically):
```python
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True) # Always launch chromium in headless mode
    page = browser.new_page()
    page.goto('http://localhost:5173') # Server already running and ready
    page.wait_for_load_state('networkidle') # CRITICAL: Wait for JS to execute
    # ... your automation logic
    browser.close()
```

## Reconnaissance-Then-Action Pattern

1. **Inspect rendered DOM**:
   ```python
   page.screenshot(path='/tmp/inspect.png', full_page=True)
   content = page.content()
   page.locator('button').all()
   ```

2. **Identify selectors** from inspection results

3. **Execute actions** using discovered selectors

## Common Pitfall

❌ **Don't** inspect the DOM before waiting for `networkidle` on dynamic apps
✅ **Do** wait for `page.wait_for_load_state('networkidle')` before inspection

## Best Practices

- **Use bundled scripts as black boxes** - To accomplish a task, consider whether one of the scripts available in `scripts/` can help. These scripts handle common, complex workflows reliably without cluttering the context window. Use `--help` to see usage, then invoke directly. 
- Use `sync_playwright()` for synchronous scripts
- Always close the browser when done
- Use descriptive selectors: `text=`, `role=`, CSS selectors, or IDs
- Add appropriate waits: `page.wait_for_selector()` or `page.wait_for_timeout()`

## Reference Files

- **examples/** - Examples showing common patterns:
  - `element_discovery.py` - Discovering buttons, links, and inputs on a page
  - `static_html_automation.py` - Using file:// URLs for local HTML
  - `console_logging.py` - Capturing console logs during automation