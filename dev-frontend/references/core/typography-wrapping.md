# Typography Wrapping — CSS Text Control

Production CSS for text wrapping, line breaks, orphan prevention, and readable line lengths.
Apply globally in resets or design system base styles.

---

## Global Production Template (2026 Standard)

```css
/* Headings — balance for visual hierarchy */
h1, h2, h3, h4, h5, h6,
blockquote, figcaption, .hero-title {
  text-wrap: balance;
}

/* Body text — pretty for orphan prevention */
p, li, dt, dd, .prose {
  text-wrap: pretty;
}

/* Editable content — stable for no-reflow typing */
[contenteditable], .live-text {
  text-wrap: stable;
}

/* Readable line lengths */
h1 { max-width: 50ch; }
h2 { max-width: 55ch; }
h3 { max-width: 60ch; }
p, li, article, .prose { max-width: 65ch; }

/* CJK text handling */
[lang|="zh"], [lang|="ja"], [lang|="ko"] {
  word-break: keep-all;
}

/* URLs and unbreakable strings */
a[href], code {
  overflow-wrap: break-word;
}

/* Never-wrap elements */
.cta-label, .badge, .nav-link, .tag {
  white-space: nowrap;
}
```

**Fallback for older browsers:**
```css
@supports not (text-wrap: balance) {
  h1, h2, h3 { max-width: min(90vw, 45ch); }
}
```

---

## `text-wrap: balance`

Distributes characters evenly across lines. Prevents long first line + stubby orphan last line.

**When to use:** Headings, captions, blockquotes, hero titles, card titles.
**When NOT to use:** Body paragraphs (performance cost, limited to ~6 lines in Chromium, 10 in Firefox).

**Tailwind:** `text-balance`

Test with both centered AND left-aligned headings. Combine with `max-width` in `ch` units for best results.

---

## `text-wrap: pretty`

Higher-quality algorithm focused on the last few lines. Prevents typographic orphans.

**When to use:** Body copy, articles, prose, content-heavy sections.
**Tailwind:** `text-pretty`

---

## `text-wrap: stable`

Prevents reflow of previous lines during editing. Content before the cursor stays fixed.

**When to use:** `contenteditable`, note-taking fields, real-time collaborative editing, live chat input.

---

## `max-width` in `ch` Units

| Element | Recommended `max-width` | Rationale |
|---------|------------------------|-----------|
| Hero title | 40–45ch | Short, punchy, fits viewport |
| Section title | 50–55ch | Room for longer phrases |
| Card title | 30–35ch | Compact containers |
| Body paragraph | 60–65ch | Optimal readability (45–75ch range) |
| Article/prose | 65ch | Standard reading measure |

Combine with fluid typography:
```css
h1 {
  font-size: clamp(2rem, 5vw + 1rem, 4rem);
  max-width: min(90vw, 45ch);
  text-wrap: balance;
}
```

---

## Rag Control

| Problem | Solution |
|---------|----------|
| Uneven rag (jagged right edge) | `text-wrap: pretty` on paragraphs |
| Orphaned last word | `text-wrap: pretty` or `text-wrap: balance` for short blocks |
| Very long lines | `max-width: 65ch` |
| Rivers in justified text | Avoid `text-align: justify` or add `hyphens: auto` + `lang` attribute |
| Heading stubs | `text-wrap: balance` + `max-width` in `ch` |

---

## `word-break` vs `overflow-wrap`

| Scenario | Use |
|----------|-----|
| Long URLs in narrow containers | `overflow-wrap: break-word` |
| Maximum flexibility with accurate sizing | `overflow-wrap: anywhere` |
| Aggressive character-level breaking | `word-break: break-all` |
| Preserve CJK word integrity | `word-break: keep-all` |
| User-generated content | `overflow-wrap: anywhere` |

**`word-break: break-word` is DEPRECATED** — use `overflow-wrap: break-word` instead.

---

## Responsive Heading Breaks

Do NOT use manual `<br>` tags for line breaks. They break on different viewports.

```css
/* If you must use <br> for a specific breakpoint: */
h1 br { display: none; }
@media (min-width: 768px) { h1 br { display: block; } }
```

**Preferred approach:** Let `text-wrap: balance` + `max-width` handle it naturally.

---

## `widows` and `orphans` (Print Only)

These CSS properties only work in multi-column layouts and paged media. NOT for standard web layouts.

For web, use `text-wrap: pretty` instead.

---

## Production Pattern

Common across Vercel, Linear, Stripe: `text-wrap: balance` on headings, `text-wrap: pretty` on body, `font-size: clamp()` for fluid scaling, tighter line-height (1.1–1.2) for headings.

For Korean-specific typography considerations, see also `korea-2026.md`.

---

## Sources

- [MDN: text-wrap](https://developer.mozilla.org/en-US/docs/Web/CSS/Reference/Properties/text-wrap)
- [Chrome: CSS text-wrap balance](https://developer.chrome.com/docs/css-ui/css-text-wrap-balance)
