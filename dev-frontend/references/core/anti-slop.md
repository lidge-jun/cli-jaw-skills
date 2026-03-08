# Anti-Slop — Banned AI Design Patterns (2026)

Specific patterns that mark output as "AI-generated." This is the comprehensive audit checklist.
Synthesized from taste-skill, redesign-skill, Anthropic frontend-design, and Koomook.

---

## Banned Fonts
- Inter, Roboto, Arial, system-ui, -apple-system
- Space Grotesk (overused as "anti-Inter" choice — still slop)
- Any system default font

**Do instead**: Geist, Outfit, Cabinet Grotesk, Satoshi, Clash Display, GT America, Neue Machina

---

## Typography Audit
- **Browser defaults or Inter everywhere** → Replace with characterful fonts
- **Headlines lack presence** → Increase size, tighten letter-spacing, reduce line-height
- **Body text too wide** → Limit to ~65ch. Increase line-height
- **Only Regular (400) + Bold (700)** → Introduce Medium (500), SemiBold (600), or extremes (100 vs 900)
- **Numbers in proportional font** → Use mono or `font-variant-numeric: tabular-nums` for data
- **Missing letter-spacing** → Negative for large headers, positive for small caps/labels
- **All-caps subheaders everywhere** → Try lowercase italic, sentence case, or small-caps
- **Orphaned words** → Fix with `text-wrap: balance` or `text-wrap: pretty`
- **Only safe weights (400/500/600)** → Go to extremes: 100-200 (thin) vs 800-900 (black)

---

## Banned Color Patterns
- Purple gradient on white background (the #1 AI tell)
- Blue-to-indigo gradient buttons
- Oversaturated neon accents (keep saturation < 80%)
- Equally distributed pastel rainbows
- Pure black (#000000) backgrounds or text → off-black (`#0a0a0a`, Zinc-950)
- Mixing warm and cool grays in same project
- Generic `box-shadow` → tint shadows to background hue

**Do instead**: Zinc/Slate neutral base + ONE high-contrast accent. Tint shadows to background hue.

---

## Banned Layouts
- Everything centered with uniform padding
- 3 equal cards in a row (the "feature row" cliché)
- Uniform rounded corners on every element (vary: tight on inner, soft on containers)
- Centered hero with gradient background + Inter heading
- Card-heavy dashboards where every metric is boxed
- Complex flexbox `calc()` percentage math → CSS Grid
- `height: 100vh` → `min-height: 100dvh` (iOS Safari)
- No max-width container → add `max-w-7xl mx-auto`
- Cards all forced to equal height → allow variable or masonry
- Dashboard always has left sidebar → try top nav, command menu, collapsible panel
- No overlap or depth → use negative margins for layering
- Symmetrical vertical padding → bottom often needs to be slightly larger (optical)
- Buttons not bottom-aligned in card groups → pin to bottom
- Feature lists at different vertical positions → align across columns
- Mathematical centering that looks optically wrong → adjust 1-2px

---

## Banned Interaction Patterns
- Generic circular loading spinners → skeleton loaders matching layout
- Default browser focus rings → `focus-visible:ring-2`
- Emoji in code, markup, text content, or alt text
- Custom mouse cursors (outdated, accessibility issue)
- Neon/outer glow `box-shadow` effects
- Oversized gradient-fill text headers
- No hover states on buttons → add background shift, scale, or translate
- No active/pressed feedback → `scale(0.98)` or `translateY(1px)`
- Instant transitions (zero duration) → 200-300ms smooth transitions
- Dead links pointing to `#` → link to real destinations or visually disable
- Scroll jumping → `scroll-behavior: smooth`
- Animations using `top`/`left`/`width`/`height` → `transform`+`opacity`
- `window.alert()` for errors → inline error messages

---

## Banned Content (The "Jane Doe" Effect)
- Generic names: "John Doe", "Sarah Chan", "Jack Su"
- Generic company names: "Acme", "Nexus", "SmartFlow", "TechFlow"
- Predictable numbers: `99.99%`, `50%`, `$9.99`, `1234567`
- AI copywriting: "Elevate", "Seamless", "Unleash", "Next-Gen", "Cutting-edge", "Revolutionary", "Game-changer", "Delve", "Tapestry", "In the world of..."
- Exclamation marks in success messages → be confident, not loud
- "Oops!" error messages → "Connection failed. Please try again."
- Passive voice → active: "We couldn't save" not "Mistakes were made"
- Same date on all blog posts → randomize
- Same avatar for multiple users → unique for each
- Lorem Ipsum → write real draft copy
- Title Case On Every Header → sentence case
- Filler text that describes instead of demonstrates

---

## Banned Component Defaults
- shadcn/ui in generic default state → MUST customize radii, colors, shadows
- Default Tailwind blue (`bg-blue-500`) as primary
- Default browser form elements without styling
- Lucide/Heroicons egg avatar as placeholder → picsum.photos or SVG UI Avatars
- Pill-shaped "New"/"Beta" badges → square badges, flags, or plain text
- 3-card carousel testimonials with dots → masonry wall, embedded social, rotating quote
- Modals for everything → inline editing, slide-over panels, expandable sections
- Avatar circles exclusively → try squircles or rounded squares
- Sun/moon dark mode toggle → dropdown, system preference, or settings
- 4-column footer link farm → simplify
- Accordion FAQ → side-by-side list, searchable help, progressive disclosure

---

## Iconography Audit
- **Lucide/Feather exclusively** → Use Phosphor, Heroicons, or custom set
- **Rocketship for "Launch", shield for "Security"** → less cliché: bolt, fingerprint, spark, vault
- **Inconsistent stroke widths** → standardize one stroke weight globally
- **Missing favicon** → always include branded favicon
- **Stock "diverse team" photos** → real photos, candids, or consistent illustration style

---

## Code Quality Audit
- Div soup → semantic HTML: `<nav>`, `<main>`, `<article>`, `<aside>`, `<section>`
- Inline styles mixed with CSS classes → move to styling system
- Hardcoded pixel widths → relative units (`%`, `rem`, `max-width`)
- Missing or empty `alt` text on meaningful images
- Arbitrary z-index `9999` → clean z-index scale
- Commented-out dead code → remove before shipping
- Import hallucinations → verify every import exists in `package.json`
- Missing meta tags → `<title>`, `description`, `og:image`

---

## Strategic Omissions (What AI Forgets)
- No legal links (privacy policy, terms) in footer
- No "back" navigation → dead ends in user flows
- No custom 404 page
- No form validation (client-side)
- No "skip to content" link (a11y)
- No cookie consent (if jurisdiction requires)
- Random dark sections in a light page → commit to one theme or use subtle shade shifts
- Empty flat sections with no depth → add background imagery, patterns, or gradients

---

## The Anti-Convergence Rule

Each generation MUST be visually distinct from the last:
- Different font pairing each time
- Different primary aesthetic archetype
- Alternate light/dark themes
- Vary layout patterns (split → asymmetric → editorial → etc.)

---

## Redesign Fix Priority Order

When fixing an existing project, apply in this order for max impact / min risk:

1. **Font swap** — biggest instant improvement
2. **Color palette cleanup** — remove clashing/oversaturated
3. **Hover + active states** — makes it feel alive
4. **Layout + spacing** — proper grid, max-width, consistent padding
5. **Replace generic components** — swap cliché patterns
6. **Add loading/empty/error states** — makes it feel finished
7. **Polish typography scale** — the premium final touch
