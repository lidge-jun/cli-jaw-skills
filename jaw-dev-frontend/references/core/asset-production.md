# Asset Production and Image-Set Continuity

Companion to [`asset-requirements.md`](asset-requirements.md). Use the entry point for sourcing, prompt construction, candidate generation, and selection; use this file for cutout preparation, frontend recipes, continuity, and composition-anchor rotation.

## Asset Background Strategy (FE-ASSET-BG-01, DEFAULT)

GPT Image 2 does not reliably produce true transparent (alpha) backgrounds.
Requesting "transparent background" or "PNG with alpha" yields unpredictable
results — sometimes a faint checkerboard pattern, sometimes a solid color
pretending to be transparent. Use the solid-background-then-remove strategy:

**Generation: pure solid background.**

For cutout assets (icons, product shots, 3D objects, illustrations, logos,
stickers, UI elements that must float over arbitrary backgrounds):

```bash
# Pure black background — best for light/reflective subjects (chrome, glass, metal)
ima2 gen "3D render of a liquid chrome splash blob, organic starburst shape, \
  mirror-polished surface with iridescent cyan and gold reflections. \
  Floating on a PURE SOLID BLACK background. The background must be 100% flat \
  pure black hex #000000. No checkerboard, no transparency pattern, no gradient, \
  no floor plane, no shadow, no vignette, no ambient glow on the background." \
  --quality high --size 1024x1024 --mode direct -o chrome-splash.png

# Pure white background — best for dark/opaque subjects (products, dark UI elements)
ima2 gen "Clean product photo of a matte black wireless earbud, centered, \
  floating at slight angle. PURE SOLID WHITE background hex #ffffff. \
  No shadow, no gradient, no surface, no reflection plane." \
  --quality high --size 1024x1024 --mode direct -o earbud-cutout.png

# Solid brand color background — when the target surface color is known
ima2 gen "Flat illustration of a coffee cup with steam, centered. \
  PURE SOLID background hex #f5f0eb (exact match required). \
  No gradient, no texture, no shadow." \
  --quality medium --size 512x512 --mode direct -o coffee-icon.png
```

**Background prompt rules:**
- State the exact hex code and repeat the constraint: "PURE SOLID [color] background hex #XXXXXX"
- Explicitly ban common AI additions: "No checkerboard, no transparency pattern, no gradient, no floor plane, no shadow, no vignette, no ambient glow"
- Use `--mode direct` to prevent server-side prompt rewriting that might soften the constraint
- Black works best for reflective/metallic/glass subjects; white for dark/matte subjects
- Match the target page background color when the destination is known

**Post-processing: background removal.**

| Method | When to Use | How |
|--------|-------------|-----|
| **CSS `mix-blend-mode`** | Black bg → light page | `mix-blend-mode: screen` makes black transparent, keeps light content |
| **CSS `mix-blend-mode`** | White bg → dark page | `mix-blend-mode: multiply` makes white transparent, keeps dark content |
| **ima2 Canvas Mode** | Interactive cleanup | Open in Canvas Mode → background cleanup → export with alpha or matte |
| **Programmatic removal** | Build pipeline | `sharp` / ImageMagick / rembg for batch processing |
| **ima2 edit** | Targeted fix | `ima2 edit asset.png --prompt "remove the background completely, keep only the [subject]"` |

**CSS blend-mode recipe (zero post-processing):**

```css
/* Black background asset on a light page */
.chrome-asset {
  mix-blend-mode: screen;  /* black → transparent, light content preserved */
}

/* White background asset on a dark page */
.product-asset {
  mix-blend-mode: multiply;  /* white → transparent, dark content preserved */
}

/* For arbitrary backgrounds, layer with isolation */
.asset-container {
  isolation: isolate;  /* prevent blend from leaking to parent */
}
```

**`$imagegen` fallback:** same solid-background prompting strategy applies.
No Canvas Mode available; use CSS blend modes or programmatic removal only.

**Anti-pattern:** requesting "transparent background" or "PNG with alpha channel"
directly in the prompt. The model will often produce a fake checkerboard pattern
burned into the image, or ignore the request entirely. Always use the
solid-background strategy above.

### Prompt Iteration

- Start with one high-detail prompt. Inspect the result by reading the image back.
- On the next iteration, make ONE targeted change and re-specify all constraints.
  Do not rewrite the entire prompt from scratch.
- Repeat invariants every iteration to prevent drift.
- If the model consistently fails on a detail, try rephrasing or breaking the
  request into a base generation + edit pass.

### Frontend Asset Quick Recipes

**Hero image (landing page):**
```bash
ima2 gen "Use case: product-mockup. Asset type: landing page hero. A premium wireless headphone floating at a slight angle against a soft warm-gray studio backdrop. Matte black finish with brushed aluminum accents. Soft three-point studio lighting, key light from upper-left. Shallow depth of field. Wide composition with generous negative space on the right for headline overlay. No text, no logos, no watermark." \
  --quality high --size 1536x1024 -o hero.png
```

**OG / social share image:**
```bash
ima2 gen "Use case: ads-marketing. Asset type: social share card. Clean product flat-lay of a notebook, pen, and ceramic mug on a white marble desk. Overhead shot. Soft diffused daylight. Space in the upper third for title overlay. Warm neutral palette. No text, no logos, no watermark." \
  --quality high --size 1200x640 -o og-image.png
```

**App screenshot mockup background:**
```bash
ima2 gen "Use case: stylized-concept. Asset type: hero background for device mockup. Soft abstract gradient from #f0f4f8 to #dbeafe with subtle geometric shapes at 5% opacity. Clean, modern, minimal. No objects, no patterns, no text." \
  --quality medium --size 1920x1088 -o mockup-bg.png
```

**Avatar / profile placeholder:**
```bash
ima2 gen "Use case: stylized-concept. Asset type: user avatar. Friendly stylized portrait of a young professional, neutral expression, looking slightly left. Flat illustration style with subtle shadows. Solid #e5e7eb background. Circular crop safe. No text." \
  --quality medium --size 512x512 -o avatar.png
```

---

## Image-Set Continuity (FE-IMAGE-SET-CONTINUITY-01, DEFAULT)

Source: taste-skill imagegen-frontend-web (62k stars), adapted for the local ima2 workflow.

Multi-image sets for landing/marketing pages must maintain visual-world continuity
across all frames. A viewer flipping through every per-section frame must still
recognize one brand — anything that breaks brand recall is over-variation.

### Frame-count defaults

| Request type | Sections | Frames |
|-------------|----------|--------|
| Hero only | 1 | 1 |
| Landing page | 6 | 6 |
| Full website | 8 | 8 |
| Marketing site | 8 | 8 |
| Product page | 6 | 6 |
| Portfolio | 6 | 6 |

Generate one separate horizontal image (16:9 or 21:9) per section. Each image
is one section, generated as its own ima2 call. Use `--ref` to the first frame
as style anchor for subsequent frames.

### Continuity contract (enforce across all frames)

- Same brand world, palette, and accent logic
- Same type-scale logic and spacing discipline
- Same CTA family (style variations fine, identity changes not)
- Same icon/illustration mood and image treatment (grade, framing, material)
- Same tonal language in copy
- Same border-radius language

### Allowed variation

- Composition anchor (MUST vary — see FE-IMAGE-ANCHOR-ROTATION-01)
- Background mode (solid, full-bleed photo, duotone, atmospheric)
- Section size and density
- Placement of the single second-read moment

---

## Image Anchor Rotation (FE-IMAGE-ANCHOR-ROTATION-01, DEFAULT)

Source: taste-skill imagegen-frontend-web, adapted for UX-CONCEPT-GEN-01.

### Composition anchors (pick one per section)

- Centered statement
- Top-left lead, support bottom-right
- Bottom-left text over background image
- Bottom-right CTA cluster
- Left-third caption + right-two-thirds visual
- Right-third caption + left-two-thirds visual
- Centered low
- Off-grid editorial offset
- Stacked center
- Image-as-canvas with text overlaid in clean safe area

### Rotation rules

- At least 3 different anchors must appear across a multi-section set.
- Same anchor cannot repeat more than 2 sections in a row.
- Same background mode cannot repeat more than 3 sections in a row.
- The classic left-third/right-two-thirds anchor: sparingly, never twice in a row.
- Non-minimalist sites must include at least one full-bleed/duotone/atmospheric
  background AND at least one mini-minimalist section.

### Application to UX-CONCEPT-GEN-01

In the 5-render concept pass, each render MUST vary the composition anchor.
Repetitive same-layout renders are wasted candidates. The element ledger
(step 3) must cite WHICH variant used which anchor and which was best.
