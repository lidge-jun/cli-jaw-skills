# Visual Verification

Do not declare frontend work complete from code alone. Render and inspect the UI.

## Required Checks

For substantial UI changes:

- run the existing dev/build command first; if it fails, stop and report the exact command/output
- use Playwright when available; otherwise use the repo's existing visual test or browser tooling
- desktop screenshot around 1440px width
- mobile screenshot around 390px width
- narrow screenshot around 320px width when text/buttons are dense
- Korean long-label stress case for Korean-first UI
- loading, empty, error, disabled, success, and permission-denied states where applicable
- keyboard tab order and focus-visible states
- reduced-motion behavior
- asset rendering and framing
- text overlap and clipping
- attach screenshot paths in the report, or state exactly what remained unverified

## What To Look For

- headings too large for the surface
- buttons with clipped Korean text
- card-heavy layout with weak hierarchy
- assets obscuring labels or CTA
- generic gradient/blob backgrounds replacing concrete visual content
- soft 3D assets that look unrelated or public-pack generic
- mobile safe-area problems
- hover/focus states changing layout dimensions
- clipped labels, especially Korean button text and dense table headers
- missing images, broken external domains, blurry generated assets
- unreadable focus rings, focus hidden under sticky headers/bottom bars
- Hero headline renders balanced on desktop (1440px) AND mobile (390px) — no orphaned single word
- Integration/partner logos use real brand SVGs, not generic stroke icons
- Logo wall has no per-item hover effect and no orphan grid cells
- CTA button labels do not break across lines at any viewport

## Tool Workflow

```ts
import { expect, test } from '@playwright/test'

test('desktop and mobile visual states', async ({ page }) => {
  await page.setViewportSize({ width: 1440, height: 1000 })
  await page.goto('/')
  await expect(page).toHaveScreenshot('desktop.png', { fullPage: true })

  await page.setViewportSize({ width: 390, height: 844 })
  await expect(page).toHaveScreenshot('mobile.png', { fullPage: true })
})
```

For component libraries, prefer Storybook stories for each state and run Chromatic, Storybook test-runner, or equivalent screenshot checks if already configured.

Fail delivery until these are resolved:
- overlap or clipped text
- missing assets or unverified external images
- unreadable focus state
- keyboard trap
- untested dense Korean labels
- soft 3D/character assets that do not pass the domain gate

## Screenshot Report

When reporting, include:

```text
desktop: checked / issue / screenshot path
mobile: checked / issue / screenshot path
narrow: checked / issue / screenshot path
states: checked / issue
assets: checked / issue
motion: checked / issue
keyboard/focus: checked / issue
```

If a browser/server/tool is unavailable, say exactly what failed and what remains unverified.
