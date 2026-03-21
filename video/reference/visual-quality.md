# Visual Quality — Video Anti-Slop Guide

Adapts `dev-frontend/anti-slop.md` for Remotion motion context.
Video is more dynamic than static UI — every frame is a first impression.

## Banned Patterns → Alternatives

| Banned                                               | Do Instead                                                                   |
| :--------------------------------------------------- | :--------------------------------------------------------------------------- |
| Same glow-orb → card → text structure on every slide | Each slide type has its own layout rhythm                                     |
| Everything centered with uniform padding             | TitleSlide = left-aligned, ContentSlide = asymmetric, QuoteSlide = offset    |
| One accent color flat everywhere                     | Accent as highlight only — not header + divider + bullets all the same       |
| Font weight only 700/800                             | Use extremes: 200(thin labels) vs 900(black hero). Create tension            |
| Uniform `borderRadius: 20` on everything             | Outer card 24, inner chip/badge 8, stat card 16. Vary intentionally          |
| Static background gradient on every slide            | Shift gradient direction per slide type. Move glow orb position              |
| Bullet points are just text lines                    | Each bullet has a visual anchor: dot, number badge, icon, color bar          |
| All exits are identical fade-to-zero                 | Mix: scale-down, slide-away, blur-out. Exit is part of the rhythm            |

## Layout Diversity per Slide Type

| Slide           | Layout Pattern                                                        | Avoid               |
| :-------------- | :-------------------------------------------------------------------- | :------------------- |
| TitleSlide      | Left-aligned, full-bleed background, accent line                      | Centered text blob   |
| ContentSlide    | Header left + bullets right (split), or header top + dense grid       | Centered stack       |
| CodeSlide       | Terminal-style frame, mono bg, glow on syntax                         | Card with code text  |
| StatSlide       | Asymmetric cards, stagger scale-in, big number / small label contrast | Equal centered cards |
| QuoteSlide      | Large `"` glyph 200px, quote offset right, author small bottom-left   | Centered italic text |
| ComparisonSlide | True split — left vs right with different accent hues                 | Two identical cards  |
| ChartSlide      | Chart fills 70%, labels crisp (min 20px), axis lines visible          | Tiny chart in card   |

## Motion Principles

- **One hero animation per slide** — pick one element that moves big, rest enters quietly
- **Stagger creates rhythm** — bullets, stat cards, chart bars. `delay = BASE + i * STEP` (6-10 frames between items)
- **Background is alive** — glow orbs drift slowly, gradient shifts over time. Static bg = dead frame
- **Exit is choreography** — the exit of slide N should visually connect to the entrance of slide N+1
- **Weight extremes create depth** — 200 weight label + 900 weight number = instant premium
- **Strategic negative space** — emptiness makes content breathe; filling every pixel creates noise

## Typography for Video

- Minimum readable size: **24px** (1080p) / **28px** (portrait)
- Heading: **900 weight, tight letter-spacing (-0.03em), line-height 1.1**
- Body: **400 weight, generous line-height (1.6-1.7)**
- Labels/captions: **200-300 weight, wide letter-spacing (0.08em), uppercase**
- Numbers (stat): **`font-variant-numeric: tabular-nums`** for alignment during count-up
