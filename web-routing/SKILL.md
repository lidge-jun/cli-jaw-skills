---
name: web-routing
description: Route browser-related requests to the appropriate skill (browser vs dev-testing).
---

# Web Routing

Route browser-related requests to the correct skill.

## Routing Rules

| Request type | Skill |
|-------------|-------|
| Web browsing, page interaction, form input, screenshots, posting | `browser` |
| Local webapp E2E / regression / test automation | `dev-testing` |
| Playwright request (not for testing) | `browser` |
| Playwright request (explicitly for testing) | `dev-testing` |

## Decision Rule

- Request contains test keywords (`e2e`, `regression`, `smoke`, `test`) → `dev-testing`
- All other browser requests → `browser`
