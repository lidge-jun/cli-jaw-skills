# Aesthetics — Deep Design Engineering Guide

Comprehensive design rules for building distinctive frontends. The SKILL.md references this file — read it before any frontend work.

---

## Typography

### Font Selection
- **Display/Headlines**: `text-4xl md:text-6xl tracking-tighter leading-none`
- **Body**: `text-base text-gray-600 leading-relaxed max-w-[65ch]`
- **Serif**: BANNED for Dashboard/Software UIs. OK for editorial/creative only.

### Recommended Fonts (rotate — never converge on one)
| Category         | Options                                                     |
| ---------------- | ----------------------------------------------------------- |
| Modern Sans      | Geist, Outfit, Cabinet Grotesk, Satoshi, Clash Display      |
| Premium Sans     | GT America, Neue Machina, Obviously, Reckless               |
| Mono (data/code) | Geist Mono, JetBrains Mono, Fira Code                       |
| CJK/Korean       | Pretendard, SUIT, Noto Sans KR (only if others unavailable) |

### Variable Font Pairing
Always pair a distinctive display font with a refined body font:
- `Clash Display` (display) + `Satoshi` (body)
- `Cabinet Grotesk` (display) + `Geist` (body)
- `Outfit` (display) + `Geist Mono` (code)

### Fluid Typography
Use `clamp()` for responsive sizing:
```css
--fluid-h1: clamp(2rem, 1rem + 3.6vw, 4rem);
--fluid-h2: clamp(1.75rem, 1rem + 2.3vw, 3rem);
--fluid-h3: clamp(1.5rem, 1rem + 1.4vw, 2.25rem);
--fluid-body: clamp(1rem, 0.95rem + 0.2vw, 1.125rem);
```

---

## Color & Theme

### Rules
- **Max 1 accent color.** Saturation < 80%.
- **THE LILA BAN**: "AI Purple/Blue" aesthetic is BANNED. No purple button glows, no neon gradients.
- **Neutral bases**: Zinc, Slate, Stone. Not plain gray.
- **High-contrast singular accents**: Emerald, Electric Blue, Deep Rose, Amber.
- **Consistency**: ONE palette for entire project. No warm/cool gray mixing.
- **CSS Variables**: All colors defined as `--color-*` variables.
- **Never pure black (#000000)**: Use off-black (Zinc-950, Charcoal, `#0a0a0a`).

### Color Scale
| Step    | Brightness | Use Case              |
| ------- | ---------- | --------------------- |
| 50      | Very light | Subtle backgrounds    |
| 100-200 | Light      | Hover states, borders |
| 300-400 | Mid-light  | Disabled states       |
| 500     | Base       | Default color         |
| 600-700 | Dark       | Hover (dark), active  |
| 800-900 | Very dark  | Text, headings        |

---

## Spatial Composition

### Layout Diversification
- **ANTI-CENTER BIAS**: When DESIGN_VARIANCE > 4, centered Hero/H1 is BANNED.
- Force: "Split Screen" (50/50), "Left-aligned content / Right asset", "Asymmetric white-space"
- **Grid over Flex-Math**: NEVER `w-[calc(33%-1rem)]`. ALWAYS CSS Grid.
- **NO 3-Column Card Layouts**: Generic "3 equal cards" is BANNED. Use 2-column zig-zag, asymmetric grid, or horizontal scroll.

### DESIGN_VARIANCE Definitions
| Level | Style                                                                                          |
| :---: | ---------------------------------------------------------------------------------------------- |
|  1-3  | Flexbox centered, strict 12-column symmetry, equal paddings                                    |
|  4-7  | `margin-top: -2rem` overlapping, varied aspect ratios, left-aligned headers over centered data |
| 8-10  | Masonry, CSS Grid fractional (`2fr 1fr 1fr`), massive empty zones (`padding-left: 20vw`)       |

**MOBILE OVERRIDE**: Levels 4-10 MUST fall back to strict single-column (`w-full`, `px-4`, `py-8`) on `< 768px`.

---

## Backgrounds & Visual Depth

Don't default to solid colors. Create atmosphere:
- **Gradient meshes**: Organic, lava-lamp-like animated color blobs
- **Noise textures**: Subtle grain overlays on fixed pseudo-elements
- **Geometric patterns**: SVG-based repeating patterns
- **Layered transparencies**: Frosted glass with inner refraction borders
- **Dramatic shadows**: Tinted to background hue, not generic black

### Glassmorphism (when used)
Go beyond `backdrop-blur`:
- 1px inner border: `border-white/10`
- Inner shadow: `shadow-[inset_0_1px_0_rgba(255,255,255,0.1)]`
- Simulates physical edge refraction

---

## Visual Density (VISUAL_DENSITY dial)

| Level | Style                                                                            |
| :---: | -------------------------------------------------------------------------------- |
|  1-3  | Art Gallery: lots of white space, huge section gaps, expensive/clean feel        |
|  4-7  | Daily App: normal spacing for standard web apps                                  |
| 8-10  | Cockpit: tiny paddings, 1px separators instead of cards, `font-mono` for numbers |

---

## UI States (Mandatory)

LLMs generate "static successul states." You MUST implement full interaction cycles:
- **Loading**: Skeletal loaders matching layout sizes. No generic circular spinners.
- **Empty**: Beautifully composed empty states indicating how to populate.
- **Error**: Clear inline error reporting.
- **Tactile Feedback**: On `:active`, use `-translate-y-[1px]` or `scale-[0.98]`.

---

## Image Rules

1. **Real photography** → ONLY Unsplash/Pexels/Pixabay direct URLs with `?w=1920&q=80`
2. **Conceptual/hero** → Write detailed image generation prompts
3. **Avatars** → picsum.photos or SVG UI Avatars. NO generic egg/Lucide user icons.
4. **Never invent fake image URLs**

---

## Aesthetic Archetypes (Inspiration Library)

When choosing a direction, select from these. Each has distinct rules:

| Archetype                  | Color Vibe                         | Signature Effects                                 |
| -------------------------- | ---------------------------------- | ------------------------------------------------- |
| Minimalism / Swiss         | Monochrome + 1 accent              | Razor-sharp hierarchy, micro hover lifts          |
| Glassmorphism              | Aurora/sunset + translucent whites | Frosted panels, glowing borders                   |
| Brutalism                  | Harsh primaries, black/white       | Sharp corners, huge bold text, "broken" aesthetic |
| Dark OLED Luxury           | #0a0a0a + vibrant accent           | Velvet textures, cinematic entrance animations    |
| Aurora / Mesh Gradient     | Teal→purple→pink                   | Animated mesh gradients, color breathing          |
| Retro-Futurism / Cyberpunk | Neon cyan/magenta on black         | Scanlines, glitch transitions, chrome accents     |
| Organic / Biomorphic       | Earthy or muted pastels            | SVG morphing, blob shapes, irregular borders      |
| Editorial / Magazine       | Warm neutrals, serif display       | Column layouts, pull quotes, dramatic whitespace  |

Vary between these. NEVER converge on the same archetype across generations.
