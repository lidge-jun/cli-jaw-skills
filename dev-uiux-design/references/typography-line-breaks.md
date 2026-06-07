# Typography Line Breaks — Design Judgment Guide

When to apply text wrapping control, how to evaluate line break quality, and what to check during visual verification.

Read `dev-frontend/references/core/typography-wrapping.md` for the CSS implementation.

---

## The Problem

AI-generated and unreviewed web pages share a common tell: **uncontrolled text wrapping**. Headings break at arbitrary points, creating orphaned words, lopsided rags, and awkward visual rhythm.

**Before (slop):**
```
Connects to what you
already run                    ← "already run" orphaned, feels broken
```

**After (controlled):**
```
Connects to what
you already run                ← Balanced, intentional
```

The difference is subtle but immediately signals whether a page was designed or merely generated.

---

## When Each Tool Applies

| Element | Tool | Rationale |
|---------|------|-----------|
| Hero headline | `text-wrap: balance` + `max-width: 40-45ch` | High-visibility, must look intentional on every viewport |
| Section title | `text-wrap: balance` + `max-width: 50-55ch` | Consistency across sections |
| Card title | `text-wrap: balance` + `max-width: 30-35ch` | Tight containers need compact control |
| Body paragraph | `text-wrap: pretty` + `max-width: 65ch` | Orphan prevention at paragraph end |
| CTA/button label | Manual — keep to 1 line | Never let a CTA break across lines |
| Navigation links | No wrapping needed | Always single-line |
| Stat label | `max-width: 20ch` | Keep compact under the number |
| Badge/tag text | `white-space: nowrap` | Never wrap |

---

## Heading Break Quality Criteria

When reviewing a heading visually, check:

1. **No orphaned single word** — The last line should have at least 2 words (or ~33% of the longest line's length)
2. **Balanced distribution** — Line lengths should be roughly equal, not one long line + one short stub
3. **Semantic grouping** — Breaks should happen between thought units, not in the middle of a phrase
4. **Viewport resilience** — The heading should look good at 390px, 768px, 1024px, AND 1440px
5. **Language-aware** — Korean (한글) headings with `word-break: keep-all` to prevent mid-word breaks

**Bad breaks (cut mid-phrase):**
```
Everything you check in Datadog, without leaving
vim                                               ← orphan
```

**Good breaks (between thought units):**
```
Everything you check in Datadog,
without leaving vim                               ← balanced, semantic
```

---

## Visual Verification Additions

Add these checks to the UX pre-flight:

- [ ] Hero headline renders balanced on desktop (1440px) AND mobile (390px)
- [ ] No heading has an orphaned single word on the last line
- [ ] Section titles do not exceed 55ch per line
- [ ] Body paragraphs do not exceed 65ch per line
- [ ] CTA buttons do not break across lines at any viewport
- [ ] Korean headlines preserve word integrity (no mid-syllable breaks)
- [ ] `text-wrap: balance` is applied to all headings globally

---

## Common Mistakes

| Mistake | Why it happens | Fix |
|---------|---------------|-----|
| Using `<br>` for line breaks | Works at one viewport, breaks at others | Use `text-wrap: balance` instead |
| `max-width` in `px` | Doesn't adapt to font size changes | Use `ch` units |
| No `max-width` on headings | Lines stretch full container width | Add `max-width: 45-55ch` |
| `text-wrap: balance` on body text | Performance cost, limited to ~6 lines | Use `text-wrap: pretty` for paragraphs |
| Ignoring mobile line breaks | Heading looks good on desktop but orphans on mobile | Test at 390px |
| Same `max-width` for all heading levels | Different font sizes produce different visual widths | Scale `max-width` by heading level |

---

## Korean Typography Notes

```css
[lang="ko"] {
  word-break: keep-all;
  overflow-wrap: break-word;
}

[lang="ko"] h1, [lang="ko"] h2 {
  text-wrap: balance;
  word-break: keep-all;
}
```

`word-break: keep-all` is critical for Korean — without it, browsers break Hangul at any syllable boundary, creating unreadable mid-word splits.
