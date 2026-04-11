# Rich Widget Reference (Physics, Math, 3D, Audio, Games)

Beyond Chart.js and D3, `diagram-html` iframes support additional libraries
for physics simulations, math visualization, 3D rendering, audio, and interactive mini-games.
All libraries below work with the current sandbox (`allow-scripts`, no CSP changes needed).

## Library Versions (CDN)

| Library | Version | CDN | Size (gz) | Tier |
|---|---|---|---|---|
| Matter.js | 0.20.0 | cdnjs | ~26 KB | 1 (drop-in) |
| Math.js | 14.8.1 | cdnjs | ~193 KB | 1 (drop-in) |
| Three.js (WebGL 2, default) | 0.172.0 | jsdelivr (ES Module) | ~176 KB | 2 (WebGL) |
| Three.js (WebGPU, optional)  | 0.180.0 | jsdelivr (ES Module) | ~200 KB | 3 (advanced) |
| p5.js | 1.11.10 | cdnjs | ~269 KB | 2 (creative) |
| Tone.js | 15.1.22 | cdnjs | ~77 KB | 2 (audio) |
| Vanilla JS | — | — | 0 KB | 1 |

## Theme Token Usage

Same pattern as Chart.js — use `window.__jawTokens` for computed values:

```javascript
const isDark = window.__jawTheme?.isDark ?? true;
const T = window.__jawTokens || {};
const textColor = T['--text'] || (isDark ? '#e2e0dd' : '#1a1a1a');
const accent = T['--accent'] || '#3b82f6';
const surface = T['--surface'] || (isDark ? '#1a1a1a' : '#fff');
const border = T['--border'] || (isDark ? 'rgba(255,255,255,0.25)' : 'rgba(0,0,0,0.15)');
```

---

## Matter.js — 2D Physics Simulation

Use for: gravity, collisions, springs, pendulums, Galton boards.

```html
<canvas id="physics" style="width:100%; height:400px;"></canvas>
<script src="https://cdnjs.cloudflare.com/ajax/libs/matter-js/0.20.0/matter.min.js"
  onerror="document.body.innerHTML='<p>Physics library failed to load.</p>'">
</script>
<script>
  const { Engine, Render, Runner, Bodies, Composite } = Matter;
  const canvas = document.getElementById('physics');
  const engine = Engine.create();
  const render = Render.create({
    canvas,
    engine,
    options: {
      width: canvas.clientWidth,
      height: 400,
      background: 'transparent',
      wireframes: false,
    }
  });

  const ground = Bodies.rectangle(
    canvas.clientWidth / 2, 390, canvas.clientWidth, 20,
    { isStatic: true, render: { fillStyle: window.__jawTokens?.['--border'] || '#444' } }
  );
  Composite.add(engine.world, [ground]);

  canvas.addEventListener('click', (e) => {
    const rect = canvas.getBoundingClientRect();
    const ball = Bodies.circle(
      e.clientX - rect.left, e.clientY - rect.top, 15,
      { restitution: 0.7, render: { fillStyle: window.__jawTokens?.['--accent'] || '#3b82f6' } }
    );
    Composite.add(engine.world, [ball]);
  });

  Render.run(render);
  Runner.run(Runner.create(), engine);
</script>
```

### Matter.js Rules
- Use `Composite.add()` (NOT deprecated `World.add()`)
- Use `Runner.run()` (NOT deprecated `Engine.run()`)
- Set `wireframes: false` for solid rendering
- Use `restitution` for bounciness (0 = no bounce, 1 = full elastic)
- Keep body count under 200 for smooth performance in iframe
- Always add `onerror` on CDN script tag

---

## Math.js — Dynamic Function Graphs

Use for: interactive math graphs, equation evaluation, sliders controlling variables.

```html
<style>
  .controls { display: flex; align-items: center; gap: 12px; margin: 0 0 1rem; }
  .controls label { font-size: 14px; color: var(--text-dim); }
  .controls span { font-size: 14px; font-weight: 500; min-width: 32px; }
</style>
<div class="controls">
  <label>Frequency</label>
  <input type="range" id="freq" min="0.5" max="5" step="0.1" value="1"
    style="flex:1;" aria-label="Wave frequency" />
  <span id="freq-out">1.0</span>
</div>
<canvas id="graph" style="width:100%; height:250px;"></canvas>
<script src="https://cdnjs.cloudflare.com/ajax/libs/mathjs/14.8.1/math.min.js"
  onerror="document.body.innerHTML='<p>Math library failed to load.</p>'">
</script>
<script>
  const canvas = document.getElementById('graph');
  const ctx = canvas.getContext('2d');
  canvas.width = canvas.clientWidth;
  canvas.height = 250;

  const accent = window.__jawTokens?.['--accent'] || '#3b82f6';
  const dim = window.__jawTokens?.['--text-dim'] || '#888';

  function draw() {
    const f = parseFloat(document.getElementById('freq').value);
    document.getElementById('freq-out').textContent = f.toFixed(1);
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    ctx.strokeStyle = dim;
    ctx.lineWidth = 0.5;
    ctx.beginPath();
    ctx.moveTo(0, canvas.height / 2);
    ctx.lineTo(canvas.width, canvas.height / 2);
    ctx.stroke();

    ctx.strokeStyle = accent;
    ctx.lineWidth = 2;
    ctx.beginPath();
    for (let px = 0; px < canvas.width; px++) {
      const x = (px / canvas.width) * 4 * Math.PI;
      const y = math.evaluate('sin(f * x)', { f, x });
      const py = canvas.height / 2 - y * (canvas.height / 2 - 20);
      px === 0 ? ctx.moveTo(px, py) : ctx.lineTo(px, py);
    }
    ctx.stroke();
  }

  document.getElementById('freq').addEventListener('input', draw);
  draw();
</script>
```

### Math.js Rules
- Use `math.evaluate(expr, scope)` with fixed expressions only
- NEVER pass user-typed text directly to `math.evaluate()` (security risk)
- For pure trig, `Math.sin()` is fine — use math.js only when advanced expressions are needed
- Use `parseFloat()` on slider values before passing to evaluate
- Always add `onerror` on CDN script tag

---

## Three.js — 3D Rendering (WebGL)

Use for: 3D models, procedural geometry, interactive 3D scenes.
WebGL works in `sandbox="allow-scripts"` without `allow-same-origin`.

**Important**: Three.js r172+ is ES Module only — must use `<script type="module">`.

**Textures**: CDN-hosted textures (cdnjs, jsdelivr, unpkg) are allowed by CSP.
External URLs from other domains are blocked. For procedural textures, use `ShaderMaterial` or canvas-generated `CanvasTexture`.

```html
<div id="c" style="width:100%; height:400px;"></div>
<script type="module">
  import * as THREE from 'https://cdn.jsdelivr.net/npm/three@0.172.0/build/three.module.min.js';
  const el = document.getElementById('c');

  const testCanvas = document.createElement('canvas');
  if (!testCanvas.getContext('webgl2')) {
    el.textContent = 'WebGL 2 not supported';
  }

  const scene = new THREE.Scene();
  const camera = new THREE.PerspectiveCamera(60, el.clientWidth / 400, 0.1, 100);
  camera.position.z = 3;
  const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
  renderer.setSize(el.clientWidth, 400);
  el.appendChild(renderer.domElement);

  const geo = new THREE.SphereGeometry(1.2, 64, 64);
  const mat = new THREE.MeshStandardMaterial({ color: 0x2266aa, roughness: 0.7 });
  const sphere = new THREE.Mesh(geo, mat);
  scene.add(sphere);
  scene.add(new THREE.AmbientLight(0xffffff, 0.4));
  scene.add(new THREE.DirectionalLight(0xffffff, 0.8));

  (function animate() {
    requestAnimationFrame(animate);
    sphere.rotation.y += 0.005;
    renderer.render(scene, camera);
  })();
</script>
```

### Three.js Rules
- `<script type="module">` required (UMD build removed in r172+)
- Use static `import` only — dynamic `import()` is unreliable in srcdoc iframes
- OrbitControls: `import { OrbitControls } from 'https://cdn.jsdelivr.net/npm/three@0.172.0/examples/jsm/controls/OrbitControls.js'`
- r163+ requires WebGL 2 — add capability guard
- Textures: `data:` and `blob:` only (CSP blocks external URLs). Use procedural textures.
- External models (`.glb`/`.gltf`): blocked by `connect-src 'none'`
- Always add `onerror` fallback for WebGL failure
- jsdelivr only (NOT cdnjs — Three.js not available as UMD on cdnjs)

### Optional: WebGPU path (r171+, pinned r0.180.0)

Use only when you need GPGPU compute, custom TSL shaders, or compute-heavy particles that hit WebGL 2 limits. **Default remains the WebGL 2 path above** — do not switch unless the widget specifically benefits.

Top-level `await` inside `<script type="module">` is standard ES2022+ and works in Chrome/Edge/Safari/Firefox. cli-jaw's iframe CSP already allows `script-src 'unsafe-inline'` for inline module scripts, so the pattern below works as-is inside srcdoc. Dynamic `import()` is used inside the `else` branch because static `import` cannot be conditional.

```html
<div id="gpu" style="width:100%; height:400px;"></div>
<script type="module">
  const el = document.getElementById('gpu');

  // Capability guard — WebGPU is not available in very old browsers or disabled contexts
  if (!('gpu' in navigator)) {
    el.textContent = 'WebGPU not available — this widget requires WebGPU';
  } else {
    const THREE = await import('https://cdn.jsdelivr.net/npm/three@0.180.0/build/three.webgpu.min.js');

    const scene = new THREE.Scene();
    const camera = new THREE.PerspectiveCamera(60, el.clientWidth / 400, 0.1, 100);
    camera.position.z = 3;

    const renderer = new THREE.WebGPURenderer({ antialias: true, alpha: true });
    await renderer.init();               // REQUIRED — WebGPU async device bootstrap
    renderer.setSize(el.clientWidth, 400);
    el.appendChild(renderer.domElement);

    // ... scene setup identical to WebGL path ...

    renderer.setAnimationLoop(() => renderer.render(scene, camera));
  }
</script>
```

**WebGPU-specific rules**:
- Entry point is `build/three.webgpu.min.js` — **not** the main `three.module.min.js`
- Version pinned to `0.180.0`. Minimum for production WebGPURenderer is r171 (2025-09); r180 is the current safe anchor as of 2026-04. Do NOT use `^` / `~` / `+` ranges in the URL.
- `renderer.init()` is **async** — must `await` before using the renderer. Pattern above uses dynamic `import()` inside an `if/else` block (static `import` can't be conditional). Alternative: wrap the whole thing in an `async` IIFE after a top-level static import.
- Use `renderer.setAnimationLoop(cb)` instead of `requestAnimationFrame` recursion — required for WebXR/WebGPU frame pacing
- TSL shaders (`tsl` module) let you write one shader that compiles to both WGSL and GLSL — useful only if you're writing custom materials
- Falls back silently if device init fails — always include the `'gpu' in navigator` guard + user-visible message
- **Do not** mix WebGL and WebGPU in the same widget; pick one per iframe
- Browser support: Chrome/Edge 113+, Safari 26 (2025-09) + iOS 26, Firefox 141+ (2025 late). Guard above handles old browsers gracefully.

**When to use which**:

| Scenario | Use |
|---|---|
| Static or lightly-animated 3D scene (≤100 objects) | WebGL 2 (r0.172.0 default) |
| Physics, particles, cloth, GPU compute (10k+ instances) | WebGPU (r0.180.0, min r171) |
| Custom fragment/vertex shaders in GLSL | WebGL 2 |
| Custom shaders targeting both backends (TSL) | WebGPU |
| Torus knot / single mesh demo | WebGL 2 — simpler, smaller bundle |

---

## p5.js — Creative Coding

Use for: generative art, particle systems, creative visual demos.
Runs in global mode (attaches to `window.setup`/`window.draw`).

```html
<script src="https://cdnjs.cloudflare.com/ajax/libs/p5.js/1.11.10/p5.min.js"
  onerror="document.body.innerHTML='<p>p5.js failed to load.</p>'">
</script>
<script>
  const particles = [];
  function setup() { createCanvas(600, 400); }
  function draw() {
    background(window.__jawTheme?.isDark ? 20 : 245);
    if (mouseIsPressed) {
      particles.push({
        x: mouseX, y: mouseY,
        vx: random(-2, 2), vy: random(-4, -1),
        life: 60,
      });
    }
    for (let i = particles.length - 1; i >= 0; i--) {
      const p = particles[i];
      p.x += p.vx; p.y += p.vy; p.vy += 0.1; p.life--;
      fill(100, 150, 255, map(p.life, 0, 60, 0, 255));
      noStroke();
      ellipse(p.x, p.y, 8);
      if (p.life <= 0) particles.splice(i, 1);
    }
  }
</script>
```

### p5.js Rules
- 269 KB — heavy for a chat widget. Prefer vanilla Canvas API for simple 2D
- p5.js best for: educational demos, generative art, rapid prototyping
- Global mode is fine in sandboxed iframe (isolated `window`)
- Keep particle/element count reasonable (<500 for smooth performance)
- Always add `onerror` on CDN script tag

---

## Tone.js — Audio Synthesis

Use for: synths, sequencers, audio visualizations.
Requires user gesture before audio playback (browser autoplay policy).

**Click-to-start pattern** (mandatory for audio widgets):

```html
<button id="startBtn" style="padding: 8px 16px; font-size: 14px;
  border: 0.5px solid var(--border); border-radius: var(--radius-md);
  background: transparent; color: var(--text); cursor: pointer;">
  Click to start audio
</button>
<div id="controls" style="display: none;">
  <input type="range" id="freq" min="100" max="1000" value="440"
    style="width: 100%;" aria-label="Frequency" />
  <span id="freq-out" style="font-size: 14px; color: var(--text-dim);">440 Hz</span>
</div>
<script src="https://cdnjs.cloudflare.com/ajax/libs/tone/15.1.22/Tone.min.js"
  onerror="document.body.innerHTML='<p>Audio library failed to load.</p>'">
</script>
<script>
  document.getElementById('startBtn').addEventListener('click', async () => {
    await Tone.start();
    document.getElementById('startBtn').style.display = 'none';
    document.getElementById('controls').style.display = 'block';
    const synth = new Tone.Synth().toDestination();
    document.getElementById('freq').addEventListener('input', (e) => {
      const f = parseFloat(e.target.value);
      document.getElementById('freq-out').textContent = f + ' Hz';
      synth.triggerAttackRelease(f, '8n');
    });
  });
</script>
```

### Tone.js Rules
- ALWAYS include a "click to start" button — `Tone.start()` requires user gesture
- Never auto-play audio on widget load
- Controls hidden until audio context is started
- `allow-same-origin` NOT needed
- Always add `onerror` on CDN script tag

---

## Vanilla JS — Mini-Games and Interactive Demos

Use for: tic-tac-toe, quizzes, calculators, simple canvas animations.
No external library needed — zero loading time.

```html
<style>
  .cell {
    width: 80px; height: 80px; font-size: 2em; cursor: pointer;
    border: 1px solid var(--border, #444);
    background: var(--surface, #1a1a1a);
    color: var(--text, #eee);
    transition: background 0.15s;
  }
  .cell:hover { background: color-mix(in oklch, var(--accent, #3b82f6) 15%, transparent); }
  #status { font-size: 14px; color: var(--text-dim); margin-top: 8px; }
</style>
<div id="board" style="display: grid; grid-template-columns: repeat(3, 80px); gap: 4px;"></div>
<p id="status">X's turn</p>
<button id="reset" style="margin-top: 8px; padding: 4px 12px; font-size: 13px;
  border: 0.5px solid var(--border); border-radius: var(--radius-md);
  background: transparent; color: var(--text); cursor: pointer;">Reset</button>
<script>
  let board = Array(9).fill(''), turn = 'X', done = false;
  const wins = [[0,1,2],[3,4,5],[6,7,8],[0,3,6],[1,4,7],[2,5,8],[0,4,8],[2,4,6]];
  const el = document.getElementById('board');
  const status = document.getElementById('status');
  const cells = [];

  for (let i = 0; i < 9; i++) {
    const btn = document.createElement('button');
    btn.className = 'cell';
    btn.setAttribute('aria-label', 'Cell ' + (i + 1));
    btn.onclick = () => {
      if (board[i] || done) return;
      board[i] = turn;
      btn.textContent = turn;
      if (wins.some(c => c.every(j => board[j] === turn))) {
        status.textContent = turn + ' wins!';
        done = true;
      } else if (board.every(c => c)) {
        status.textContent = 'Draw!';
        done = true;
      } else {
        turn = turn === 'X' ? 'O' : 'X';
        status.textContent = turn + "'s turn";
      }
    };
    cells.push(btn);
    el.appendChild(btn);
  }

  document.getElementById('reset').onclick = () => {
    board = Array(9).fill('');
    turn = 'X';
    done = false;
    cells.forEach(c => c.textContent = '');
    status.textContent = "X's turn";
  };
</script>
```

### Vanilla JS Rules
- Use CSS variables (`var(--text)`, `var(--surface)`, etc.) for theme compatibility
- Keep DOM operations minimal — batch updates
- Add `aria-label` to interactive elements
- Include a reset/restart mechanism for games
- `sendPrompt()` available for drill-down (e.g., "Explain this move")

---

## General Widget Rules
- Style-first, script-last (same as Chart.js widgets)
- Height 400px or less recommended (ResizeObserver auto-adjusts, 2000px max)
- Always add `onerror` on CDN `<script>` tags
- Theme tokens: `window.__jawTheme.isDark`, `window.__jawTokens['--*']`
- `sendPrompt(text)` to populate chat input (max 500 chars, rate-limited)
- CDN allowlist (CSP-enforced): `cdnjs.cloudflare.com`, `cdn.jsdelivr.net`, `unpkg.com`, `esm.sh`
- Import maps auto-injected for Three.js bare specifiers (`import from 'three'`)
- If widget includes its own `<script type="importmap">`, the auto-injection is skipped
