# Layout Discipline Rules

## Hero Discipline (MANDATORY)
1. Hero MUST fit initial viewport — headline ≤2 lines, subtext ≤20 words, CTA visible
2. Font-scale: plan font + image together; default text-4xl md:text-5xl lg:text-6xl
3. Top padding cap: max pt-24 (6rem) at desktop
4. Stack discipline: max 4 text elements (eyebrow|brand-strip, headline, subtext, CTAs)
5. Banned inside hero: tagline below CTAs, trust strip, pricing teaser, feature bullets
6. "Used by" logo wall → separate section directly below hero

## Eyebrow Restraint (MANDATORY)
- Maximum 1 eyebrow per 3 sections (hero counts as 1)
- Pre-flight mechanical check: count uppercase+tracking instances ≤ ceil(sectionCount / 3)
- Alternative: drop the eyebrow. Headline alone is enough.

## Section Layout Repetition Ban
- Each layout family (3-col cards, split-text-image, full-width-quote, etc.) at most ONCE per page
- 8-section page needs ≥4 different layout families
- Cross-ref: aesthetics.md § Spatial Composition also bans 3-col cards and centered heroes

## Zigzag Alternation Cap
- Max 2 consecutive left-image/right-text alternating sections
- 3rd consecutive = fail. Break with full-width, vertical-stack, bento, or different family
- Note: aesthetics.md recommends zigzag as alternative to 3-cards — that's fine for 1-2 uses, this rule caps overuse

## Split-Header Ban
- "Left big headline + right small explainer paragraph" as section header: BANNED as default
- Stack vertically: headline on top, body below, max-width 65ch

## Bento Rules
- Cell count: EXACTLY as many cells as content items. No empty cells.
- Background diversity: ≥2-3 cells need real visual variation (image, gradient, pattern)
- Rhythm: no one-sided repetition (6 left-image/right-text rows)

## Section Content Limits
- Default per section: short headline (≤8 words) + sub-paragraph (≤25 words) + one visual/CTA
- Long lists (>5 items): use cards/tabs/accordion/scroll-snap/carousel, not default <ul>
- Spec sheets: 2-col card grid, scroll-snap pills, grouped chunks, or featured-vs-rest
- Quotes: max 3 lines, attribution = name + role [+ company]
