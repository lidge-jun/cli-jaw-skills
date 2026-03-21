---
name: web-artifacts-builder
description: Suite of tools for creating elaborate, multi-component claude.ai HTML artifacts using modern frontend web technologies (React, Tailwind CSS, shadcn/ui). Use for complex artifacts requiring state management, routing, or shadcn/ui components - not for simple single-file HTML/JSX artifacts.
license: Complete terms in LICENSE.txt
---

# Web Artifacts Builder

1. Initialize: `scripts/init-artifact.sh <project-name>`
2. Develop the artifact
3. Bundle: `scripts/bundle-artifact.sh` → `bundle.html`
4. Share the bundled HTML with user
5. (Optional) Test the artifact

**Stack**: React 18 + TypeScript + Vite + Parcel (bundling) + Tailwind CSS + shadcn/ui

## Design & Style Guidelines

Prefer distinctive layouts over generic defaults: vary spacing, use asymmetry, choose intentional color palettes, and pick fonts that match the artifact's purpose. Each artifact should feel hand-crafted.

Why: claude.ai artifacts are viewed side-by-side with conversation. Generic styling makes them look auto-generated and undermines user trust.

## Commands

- **Init**: `bash scripts/init-artifact.sh <project-name>` — scaffolds React + TS + Vite + Tailwind + 40+ shadcn/ui components + Parcel bundling.
- **Bundle**: `bash scripts/bundle-artifact.sh` — produces `bundle.html` (requires `index.html` in project root). All JS/CSS inlined.
- **Test**: use Playwright/Puppeteer after sharing, not before — upfront testing adds latency the user feels.

Why bundle? Claude artifacts must be a single HTML file. Parcel inlines all dependencies so the artifact is self-contained.

## Reference

- **shadcn/ui components**: https://ui.shadcn.com/docs/components