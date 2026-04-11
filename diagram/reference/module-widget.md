# Rich Widget Reference (Physics, Math, Games)

Beyond Chart.js and D3, `diagram-html` iframes support additional libraries
for physics simulations, math visualization, and interactive mini-games.
All libraries below work with the current sandbox (`allow-scripts`, no CSP changes).

## Library Versions (CDN)

| Library | Version | CDN URL | Size (gz) |
|---|---|---|---|
| Matter.js | 0.20.0 | `https://cdnjs.cloudflare.com/ajax/libs/matter-js/0.20.0/matter.min.js` | ~26 KB |
| Math.js | 14.8.1 | `https://cdnjs.cloudflare.com/ajax/libs/mathjs/14.8.1/math.min.js` | ~193 KB |
| Vanilla JS | — | No CDN needed | 0 KB |

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

  // Static ground
  const ground = Bodies.rectangle(
    canvas.clientWidth / 2, 390, canvas.clientWidth, 20,
    { isStatic: true, render: { fillStyle: window.__jawTokens?.['--border'] || '#444' } }
  );
  Composite.add(engine.world, [ground]);

  // Click to spawn physics objects
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

    // Axis
    ctx.strokeStyle = dim;
    ctx.lineWidth = 0.5;
    ctx.beginPath();
    ctx.moveTo(0, canvas.height / 2);
    ctx.lineTo(canvas.width, canvas.height / 2);
    ctx.stroke();

    // Wave
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

## General Widget Rules
- Style-first, script-last (same as Chart.js widgets)
- Height 400px or less recommended (ResizeObserver auto-adjusts, 2000px max)
- Always add `onerror` on CDN `<script>` tags
- Theme tokens: `window.__jawTheme.isDark`, `window.__jawTokens['--*']`
- `sendPrompt(text)` to populate chat input (max 500 chars, rate-limited)
