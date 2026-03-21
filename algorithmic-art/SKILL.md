---
name: algorithmic-art
description: Creating algorithmic art using p5.js with seeded randomness and interactive parameter exploration. Use this when users request creating art using code, generative art, algorithmic art, flow fields, or particle systems. Create original algorithmic art rather than copying existing artists' work to avoid copyright violations.
license: Complete terms in LICENSE.txt
---

Algorithmic philosophies are computational aesthetic movements expressed through code. Output: `.md` (philosophy), `.html` (interactive viewer), `.js` (generative algorithm).

Two-step process:
1. Create an Algorithmic Philosophy (`.md`)
2. Express it as p5.js generative art (`.html` + `.js`)

---

## Step 1: Algorithmic Philosophy Creation

Create a philosophy for a generative art movement — not static images or templates.

**What to create:** An algorithmic worldview expressed through computational processes, emergent behavior, mathematical beauty, seeded randomness, noise fields, organic systems, particles, flows, fields, forces, and parametric variation.

**Relationship to user input:** The user's request is a foundation, not a constraint. Use it as a starting point for creative freedom.

### How to Write the Philosophy

1. **Name the movement** (1–2 words): e.g. "Organic Turbulence", "Quantum Harmonics"

2. **Articulate the philosophy** (4–6 paragraphs) covering:
   - Computational processes and mathematical relationships
   - Noise functions and randomness patterns
   - Particle behaviors and field dynamics
   - Temporal evolution and system states
   - Parametric variation and emergent complexity

3. **Guidelines:**
   - Each algorithmic concept appears once — avoid repeating noise theory, particle dynamics, etc.
   - Stress that the final algorithm should feel meticulously crafted, refined through deep expertise
   - Leave implementation room — be specific about direction, concise enough for interpretive choices
   - Beauty lives in the process, not the final frame

See [references/philosophy-examples.md]({baseDir}/references/philosophy-examples.md) for condensed examples.

### Core Principles

- **Process over product**: Beauty emerges from the algorithm's execution; each run is unique
- **Parametric expression**: Ideas communicated through mathematical relationships and forces
- **Artistic freedom**: Provide creative implementation room
- **Expert craftsmanship**: The algorithm should feel like the product of deep computational expertise

Output the philosophy as a `.md` file.

---

## Conceptual Seed

Before implementing, identify the subtle conceptual thread from the original request.

The concept is a **niche reference embedded within the algorithm** — not literal, always sophisticated. Someone familiar with the subject feels it intuitively; others simply experience a masterful composition. Think of a jazz musician quoting another song through algorithmic harmony.

The algorithmic philosophy provides the computational language. The conceptual seed provides the soul — quiet DNA woven into parameters, behaviors, and emergence patterns.

---

## Step 2: p5.js Implementation

With philosophy and conceptual seed established, express them through code.

### Read the Template First

Before writing any HTML:

1. **Read** `templates/viewer.html` using the Read tool
2. **Use it as the literal starting point** — keep all fixed sections exactly as shown
3. **Replace only variable sections** marked in the file's comments

### Template Structure: Fixed vs Variable

**Fixed (keep exactly as-is):**
- Layout (header, sidebar, main canvas area)
- Anthropic branding (colors: light theme, fonts: Poppins/Lora, gradient backdrop)
- Seed section: display, prev/next/random buttons, jump-to-seed input
- Actions section: regenerate, reset, download PNG buttons

**Variable (customize per artwork):**
- The entire p5.js algorithm (`setup`/`draw`/classes)
- The `params` object
- Parameters section in sidebar (slider count, names, min/max/step)
- Colors section (optional — include color pickers if palette is user-adjustable; omit for fixed/monochrome palettes)

### Technical Requirements

**Seeded Randomness (Art Blocks Pattern):**
```javascript
let seed = 12345;
randomSeed(seed);
noiseSeed(seed);
```
Same seed always produces identical output.

**Parameters — follow the philosophy:**
```javascript
let params = {
  seed: 12345,
  // Parameters that control YOUR algorithm:
  // Quantities, scales, probabilities, ratios,
  // angles, thresholds — whatever the system needs
};
```
Design parameters around tunable system properties, not "pattern types."

**Algorithm — express the philosophy:**

Let the philosophy dictate what to build. Think "how to express this philosophy through code?" rather than "which pattern should I use?"

- Organic emergence → elements that grow, random processes constrained by natural rules, feedback loops
- Mathematical beauty → geometric relationships, trigonometric harmonics, precise calculations
- Controlled chaos → random variation within strict boundaries, order from disorder

**Canvas Setup:**
```javascript
function setup() {
  createCanvas(1200, 1200);
}
function draw() {
  // Generative algorithm — static (noLoop) or animated
}
```

### Quality Standards

- **Balance**: Complexity without visual noise, order without rigidity
- **Color harmony**: Thoughtful palettes, not random RGB
- **Composition**: Visual hierarchy even in randomness
- **Performance**: Smooth real-time execution if animated

### Sidebar Controls

Build the sidebar following `templates/viewer.html` structure:

1. **Seed** (fixed) — display, prev/next/random/jump
2. **Parameters** (variable) — one `control-group` per parameter:
   ```html
   <div class="control-group">
     <label>Parameter Name</label>
     <input type="range" id="param" min="..." max="..." step="..." value="..."
            oninput="updateParam('param', this.value)">
     <span class="value-display" id="param-value">...</span>
   </div>
   ```
3. **Colors** (optional) — color pickers if needed
4. **Actions** (fixed) — regenerate, reset, download

All parameters need UI controls. All controls update in real-time.

### Output

1. **Algorithmic Philosophy** — `.md` file
2. **Single HTML artifact** — self-contained interactive art built from `templates/viewer.html`

The HTML embeds everything inline: p5.js (CDN), algorithm, parameter controls, UI. Works in claude.ai artifacts or any browser with no setup.

```html
<!DOCTYPE html>
<html>
<head>
  <script src="https://cdnjs.cloudflare.com/ajax/libs/p5.js/1.7.0/p5.min.js"></script>
  <style>/* All styling inline */</style>
</head>
<body>
  <div id="canvas-container"></div>
  <div id="controls"><!-- Parameter controls --></div>
  <script>/* All p5.js code inline */</script>
</body>
</html>
```

---

## Variations & Exploration

Seed navigation is built into every artifact (prev/next/random buttons). For highlighted variations:
- Add seed preset buttons ("Variation 1: Seed 42", etc.)
- Add a gallery mode showing thumbnails of multiple seeds

The algorithm stays consistent; each seed reveals different facets of its potential.

---

## Resources

- **`templates/viewer.html`** — Starting point for all HTML artifacts. Comments mark fixed vs variable sections.
- **`templates/generator_template.js`** — Reference for p5.js best practices: parameter organization, seeded randomness, class structure. Embed algorithms inline in HTML (not as separate `.js` files).
- **`references/philosophy-examples.md`** — Condensed philosophy examples for reference.
