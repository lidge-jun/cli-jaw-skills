# Interactive Widget Reference

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

  function updateChart() {
    const rate = parseFloat(rateInput.value) / 100;
    rateOut.textContent = rateInput.value + '%';
    const data = Array.from({length: 30}, (_, i) => Math.round(10000 * Math.pow(1 + rate, i)));
    if (chart) {
      chart.data.datasets[0].data = data;
      chart.update('none');
    }
  }

  rateInput.addEventListener('input', updateChart);
</script>
```

## Keyboard Accessibility
- All form controls must have labels (explicit `<label>` or `aria-label`)
- Buttons must be focusable (default for `<button>`)
- Range inputs are keyboard-accessible by default (arrow keys)
- Custom widgets: add `tabindex="0"`, `role`, and keyboard handlers

## Style-First, Script-Last
Always order content as:
1. `<style>` and `<link>` tags
2. HTML structure (visible content)
3. `<script>` tags

This ensures visual content renders during streaming before scripts execute.
