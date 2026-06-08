---
name: nextjs-turbopack
description: Next.js 16+ and Turbopack — incremental bundling, FS caching, dev speed, production builds, Server Fast Refresh, and when to fall back to webpack.
---

# Next.js and Turbopack

> **Current version: Next.js 16.2.x (June 2026)**

Next.js 16+ uses Turbopack as its default bundler for both development and production builds. Turbopack is an incremental bundler written in Rust that significantly speeds up dev startup, hot updates, and production build times.

## When to Use

- **Turbopack (default)**: Used for both `next dev` and `next build`. Faster cold start, HMR, and production builds, especially in large apps.
- **Webpack (legacy fallback)**: Use only if you hit a Turbopack bug or rely on a webpack-only plugin. Disable Turbopack with `--no-turbopack` flag or set `NEXT_DISABLE_TURBOPACK=1` environment variable.

Use when: developing or debugging Next.js 16+ apps, diagnosing slow dev startup or HMR, or optimizing production bundles.

## How It Works

- **Turbopack**: Incremental bundler for both dev and production. Uses file-system caching so restarts and rebuilds are much faster (e.g. 5–14x on large projects).
- **Default bundler**: From Next.js 16, both `next dev` and `next build` use Turbopack unless explicitly disabled.
- **File-system caching**: Restarts reuse previous work; cache is typically under `.next`; no extra config needed for basic use.
- **Server Fast Refresh (16.2+)**: Server Components now support fast refresh — edits to server components are reflected without a full page reload, preserving client state.
- **Bundle Analyzer (Next.js 16.1+)**: Experimental Bundle Analyzer to inspect output and find heavy dependencies; enable via config or experimental flag (see Next.js docs for your version).

## Examples

### Commands

```bash
next dev
next build
next start
```

### Usage

Run `next dev` for local development with Turbopack. Use the Bundle Analyzer (see Next.js docs) to optimize code-splitting and trim large dependencies. Prefer App Router and server components where possible.

## Best Practices

- Stay on Next.js 16.2.x or later for stable Turbopack dev + production builds and Server Fast Refresh.
- If dev is slow, ensure you're on Turbopack (default) and that the cache isn't being cleared unnecessarily.
- For production bundle size issues, use the official Next.js bundle analysis tooling for your version.
- If you need to fall back to webpack, prefer `NEXT_DISABLE_TURBOPACK=1` in CI or `--no-turbopack` locally.
