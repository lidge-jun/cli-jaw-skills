---
name: canvas-design
description: Create beautiful visual art in .png and .pdf documents using design philosophy. You should use this skill when the user asks to create a poster, piece of art, design, or other static piece. Create original visual designs, never copying existing artists' work to avoid copyright violations.
license: Complete terms in LICENSE.txt
---

Two-phase process: design philosophy (.md) → canvas expression (.pdf/.png).

## Phase 1: Design Philosophy

Write a `.md` file that defines the visual language — not a layout spec, but principles for form, space, color, and composition.

### Requirements
1. **Name** (1–2 words) — e.g., "Brutalist Joy", "Chromatic Silence".
2. **Body** (4–6 paragraphs) covering: space/form, color/material, scale/rhythm, composition, visual hierarchy.
3. Each aspect appears once — no redundancy.
4. Keep it context-agnostic so it applies to any canvas size or medium.

## Phase 2: Canvas Creation

Express the philosophy on canvas using these rules:

### Composition
- All elements must stay within canvas boundaries with ≥5% margin on each side.
- No overlapping elements unless the philosophy explicitly calls for layering.
- Color palette: ≤5 colors unless the philosophy specifies otherwise.
- Include at least one repeating pattern or systematic visual element.

### Typography
- Fonts: use `./canvas-fonts` directory (60+ fonts available). Use ≥2 different fonts per piece.
- Text is visual — size and placement serve composition, not readability alone.

### Refinement pass
- After initial creation, do one revision pass focused on cohesion: tighten spacing, unify color usage, remove anything that doesn't serve the composition.

### Output
- Deliver `.pdf` or `.png` alongside the philosophy `.md`.
- Multi-page: when requested, each page uses the same philosophy but a distinct expression. Bundle as one `.pdf` or multiple `.png` files.
