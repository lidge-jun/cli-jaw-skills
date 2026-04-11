# Interactive Widget Reference

## Design Principles for Interactive Widgets

- **Immediate feedback**: every control must update something visible within one frame. Listen on `input`, not `change`, for sliders.
- **Show the current value**: numeric/range controls always display their value beside the control (`<span id="out">`). Users should never guess what a slider means.
- **Control budget**: **≤3 primary controls** per widget. 4+ = redesign or split into two widgets. A "primary" control meaningfully changes the output; a play/pause/reset is not counted.
- **Sensible defaults**: the widget must render a meaningful state on first mount, before any interaction. Pick defaults that already tell the story.
- **Reversibility**: widgets with 2+ controls should offer a Reset button that restores defaults.
- **Layout**: controls go **above** the canvas, not below. Visual output is the payload; controls are the instrument.
- **Theme-aware**: use `var(--border)`, `var(--text)`, `var(--text-dim)`, `var(--accent)`, `var(--surface)` — never hardcode colors. Use `window.__jawTheme.isDark` for JS-side logic.
- **Debounce expensive work**: if updating involves recomputing large datasets, chart re-renders, or physics steps, debounce with `requestAnimationFrame` or 16ms throttle. Cheap DOM text updates need no debounce.

## Control Layout Pattern

Use a consistent control row: `label — input — value display`.

```html
<div class="controls" style="display: flex; flex-direction: column; gap: 12px;
  padding: 12px; border: 0.5px solid var(--border); border-radius: var(--radius-md);
  background: var(--surface); margin-bottom: 1rem;">
  <div style="display: flex; align-items: center; gap: 12px;">
    <label for="n" style="font-size: 14px; color: var(--text-dim); min-width: 80px;">Count</label>
    <input type="range" id="n" min="1" max="50" value="20" style="flex: 1;" aria-label="Count" />
    <span id="n-out" style="font-size: 14px; font-weight: 500; min-width: 32px; text-align: right;">20</span>
  </div>
  <!-- additional control rows here -->
</div>
```

Rules:
- Each row: same label width, same value-display width → visual alignment
- Container has subtle border + padding, not a raw strip of inputs
- Max 3 rows; 4+ means the widget is doing too much

## Slider Control
```html
<div style="display: flex; align-items: center; gap: 12px; margin: 0 0 1.5rem;">
  <label style="font-size: 14px; color: var(--text-dim);">Years</label>
  <input type="range" min="1" max="40" value="20" id="years"
    style="flex: 1;" aria-label="Number of years" />
  <span style="font-size: 14px; font-weight: 500; min-width: 24px;"
    id="years-out">20</span>
</div>
<script>
  document.getElementById('years').addEventListener('input', (e) => {
    document.getElementById('years-out').textContent = e.target.value;
  });
</script>
```

## Other Control Types

### Select / dropdown
```html
<select id="mode" aria-label="Mode"
  style="padding: 6px 10px; border: 0.5px solid var(--border); border-radius: var(--radius-md);
    background: var(--surface); color: var(--text); font-size: 14px;">
  <option value="linear">Linear</option>
  <option value="exp" selected>Exponential</option>
  <option value="log">Logarithmic</option>
</select>
```
Use for 3–6 mutually exclusive options. For 2 options use a toggle; for 7+ use a search input.

### Segmented button group (mode switcher)
For 2–4 exclusive modes where all options should be visible at once.

```html
<div role="radiogroup" aria-label="View mode"
  style="display: inline-flex; border: 0.5px solid var(--border); border-radius: var(--radius-md); overflow: hidden;">
  <button role="radio" aria-checked="true" data-mode="day"
    style="padding: 6px 14px; font-size: 13px; background: var(--accent); color: var(--bg); border: none; cursor: pointer;">
    Day
  </button>
  <button role="radio" aria-checked="false" data-mode="week"
    style="padding: 6px 14px; font-size: 13px; background: transparent; color: var(--text); border: none; border-left: 0.5px solid var(--border); cursor: pointer;">
    Week
  </button>
  <button role="radio" aria-checked="false" data-mode="month"
    style="padding: 6px 14px; font-size: 13px; background: transparent; color: var(--text); border: none; border-left: 0.5px solid var(--border); cursor: pointer;">
    Month
  </button>
</div>
<script>
  document.querySelectorAll('[role="radiogroup"]').forEach(group => {
    const radios = group.querySelectorAll('[role="radio"]');
    radios.forEach(btn => {
      btn.addEventListener('click', () => {
        radios.forEach(b => {
          const active = b === btn;
          b.setAttribute('aria-checked', active);
          b.style.background = active ? 'var(--accent)' : 'transparent';
          b.style.color = active ? 'var(--bg)' : 'var(--text)';
        });
        // update output...
      });
    });
  });
</script>
```

### Toggle / checkbox
```html
<label style="display: inline-flex; align-items: center; gap: 8px; font-size: 14px; cursor: pointer;">
  <input type="checkbox" id="grid" checked />
  <span>Show grid</span>
</label>
```

### Number input with stepper
```html
<div style="display: inline-flex; align-items: center; border: 0.5px solid var(--border); border-radius: var(--radius-md);">
  <button aria-label="Decrease" style="padding: 4px 10px; background: transparent; border: none; color: var(--text); cursor: pointer;">−</button>
  <input type="number" value="10" min="1" max="100"
    style="width: 48px; padding: 4px; border: none; background: transparent; color: var(--text); text-align: center; font-size: 14px;" />
  <button aria-label="Increase" style="padding: 4px 10px; background: transparent; border: none; color: var(--text); cursor: pointer;">+</button>
</div>
```

### Play / pause / reset (time-based simulations)
```html
<div style="display: inline-flex; gap: 4px;">
  <button id="play" aria-label="Play" style="padding: 6px 12px; border: 0.5px solid var(--border); border-radius: var(--radius-md); background: transparent; color: var(--text); cursor: pointer;">▶</button>
  <button id="pause" aria-label="Pause" style="padding: 6px 12px; border: 0.5px solid var(--border); border-radius: var(--radius-md); background: transparent; color: var(--text); cursor: pointer;" disabled>⏸</button>
  <button id="reset" aria-label="Reset" style="padding: 6px 12px; border: 0.5px solid var(--border); border-radius: var(--radius-md); background: transparent; color: var(--text); cursor: pointer;">↺</button>
</div>
```
Drive animations with `requestAnimationFrame`, not `setInterval`. Cancel the frame handle on pause and on widget unmount.

## Throttling, Debouncing, and Performance

- **Cheap updates** (DOM text, CSS variable): no coalescing needed — handle directly in `input` event.
- **Chart re-renders** / **animation-frame work**: **throttle** by coalescing to `requestAnimationFrame` (one update per frame max). Use Chart.js `update('none')` to skip the chart's own animation.
- **Heavy recomputation that should run only after the user stops** (>10ms, expensive network/worker call): **debounce** with `setTimeout` (150ms) so it only fires once on the trailing edge. Use `requestIdleCallback` if ordering-independent.
- Never block the input event handler on synchronous heavy work — the slider will judder.

```javascript
// Throttle (coalesce) pattern — use for live chart updates
let rafId = null;
function onSliderInput(value) {
  if (rafId) return;
  rafId = requestAnimationFrame(() => {
    updateChart(value);
    rafId = null;
  });
}

// Debounce (trailing-edge) pattern — use when work should run after user stops
let debounceId = null;
function onSliderDebounced(value) {
  clearTimeout(debounceId);
  debounceId = setTimeout(() => runExpensive(value), 150);
}
```

## sendPrompt Button
Populates the chat input with a prompt — user must click Send manually.
Rate-limited to 1 call per 3 seconds.

```html
<button onclick="sendPrompt('Break down Q4 by region')"
  style="display: inline-flex; align-items: center; gap: 4px; padding: 6px 12px;
    border: 0.5px solid var(--border); border-radius: var(--radius-md);
    background: transparent; cursor: pointer; font-size: 13px; color: var(--text);">
  Drill into Q4 ↗
</button>
```

### sendPrompt Rules
- Max 500 characters per prompt
- Populates `#chatInput` only — does NOT auto-send (requires user gesture)
- Rate limited: 1 call per 3 seconds (both client and host side)
- Keep prompts actionable and concise

## Live State Management
When combining sliders with charts, update chart data on input events:

```html
<div style="display: flex; align-items: center; gap: 12px; margin-bottom: 1rem;">
  <label style="font-size: 14px; color: var(--text-dim);">Interest Rate</label>
  <input type="range" min="1" max="15" value="5" step="0.5" id="rate"
    style="flex: 1;" aria-label="Interest rate percentage" />
  <span id="rate-out" style="font-size: 14px; font-weight: 500;">5%</span>
</div>
<canvas id="growthChart" role="img" aria-label="Investment growth over time">
  Investment growth chart
</canvas>
<script>
  const rateInput = document.getElementById('rate');
  const rateOut = document.getElementById('rate-out');
  let chart;
  let rafId = null;

  function computeAndRender() {
    const rate = parseFloat(rateInput.value) / 100;
    const data = Array.from({length: 30}, (_, i) => Math.round(10000 * Math.pow(1 + rate, i)));
    if (chart) {
      chart.data.datasets[0].data = data;
      chart.update('none');
    }
  }

  rateInput.addEventListener('input', () => {
    // Cheap text readout — update immediately
    rateOut.textContent = rateInput.value + '%';
    // Chart re-render — throttle to one per frame
    if (rafId) return;
    rafId = requestAnimationFrame(() => {
      computeAndRender();
      rafId = null;
    });
  });
</script>
```

## Keyboard Accessibility
- All form controls must have labels (explicit `<label>` or `aria-label`)
- Buttons must be focusable (default for `<button>`)
- Range inputs are keyboard-accessible by default (arrow keys)
- Custom widgets: add `tabindex="0"`, `role`, and keyboard handlers

## Style-First, Script-Last
See the `Style-First, Script-Last` section in the parent `SKILL.md` — same rule applies to interactive widgets. Controls markup goes before `<script>`; scripts only wire up pre-existing DOM.
