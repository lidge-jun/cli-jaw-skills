# Svelte / SvelteKit Stack — Development Rules

Placeholder for Svelte-specific rules. Extend when needed.
Read `core/aesthetics.md` + `core/anti-slop.md` first.

---

## Architecture

### SvelteKit (Default)
- File-based routing in `src/routes/`
- Server-side rendering by default
- `+page.svelte` for pages, `+layout.svelte` for layouts
- `+page.server.ts` for server-only data loading

### Runes (Svelte 5+)
```svelte
<script>
  let count = $state(0);
  let doubled = $derived(count * 2);
</script>
```

### Styling
- Scoped CSS by default (in `<style>` tag)
- CSS variables for design tokens
- Use Tailwind via `@tailwindcss/vite` plugin if needed

---

## Key Differences from React

| Concept   | React                | Svelte                                 |
| --------- | -------------------- | -------------------------------------- |
| State     | `useState`           | `$state` rune                          |
| Derived   | `useMemo`            | `$derived` rune                        |
| Effects   | `useEffect`          | `$effect` rune                         |
| Animation | Framer Motion        | `svelte/transition` + `svelte/animate` |
| Styling   | className + Tailwind | Scoped `<style>` or Tailwind           |

### Transitions (Built-in)
```svelte
<script>
  import { fly, fade } from 'svelte/transition';
</script>

{#if visible}
  <div transition:fly={{ y: 20, duration: 300 }}>Content</div>
{/if}
```

---

## Performance
- Svelte compiles away the framework — smaller bundles by default
- No virtual DOM overhead
- Use `{#await}` blocks for loading states
- Lazy load with `import()` for heavy components

---

## Anti-Slop Rules

Same as all stacks — see `core/anti-slop.md`. Additionally:
- Don't use default SvelteKit skeleton styles
- Override default transitions with custom spring physics
- No `<svelte:component>` with hard-to-follow dynamic components
