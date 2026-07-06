# Chart.js + D3 Integration Reference

## Library Versions (CDN)

| Library | Version | CDN URL | Use case |
|---|---|---|---|
| Chart.js | 4.4.1 | `https://cdnjs.cloudflare.com/ajax/libs/Chart.js/4.4.1/chart.umd.js` | bar / line / pie / scatter / doughnut / polar |
| ECharts | 6.0.0 | `https://cdnjs.cloudflare.com/ajax/libs/echarts/6.0.0/echarts.min.js` | heatmap / sankey / radar / treemap / gauge / funnel / candlestick / chord |
| D3.js | 7.8.5 | `https://cdnjs.cloudflare.com/ajax/libs/d3/7.8.5/d3.min.js` | custom SVG graphics, choropleth, force layout |
| TopoJSON | 3.0.2 | `https://cdnjs.cloudflare.com/ajax/libs/topojson/3.0.2/topojson.min.js` | D3 geo data (+ `connect-src cdn.jsdelivr.net`) |

**Chart library routing**: In cli-jaw Web UI final answers, prefer the native `chart-json` fence for simple bar/line/pie charts. Chart.js is the default inside `diagram-file` for anything it supports beyond `chart-json`. Switch to ECharts only when the chart type is in ECharts' column above (heatmap, sankey, radar, treemap, etc.). D3 is for custom SVG-based visuals that neither Chart.js nor ECharts cover.

## Web UI `chart-json` Shortcut

Use `chart-json` when the answer needs a compact, final-answer chart with simple labels and one numeric series. It renders as a native Web UI card, so it is lighter than a full iframe widget and should be the first choice for ordinary bar, line, and pie charts.

```chart-json
{
  "schemaVersion": "chart-json-v1",
  "type": "bar",
  "title": "Quarterly Revenue",
  "description": "USD, millions",
  "labels": ["Q1", "Q2", "Q3", "Q4"],
  "data": [12, 18, 16, 24]
}
```

Use `diagram-file` instead when the visualization needs custom JavaScript, multiple coordinated charts, advanced Chart.js options, ECharts-only chart types, D3 transforms, maps, live controls, or non-basic interactivity. Use `diagram-html` only as the inline fallback when chatId is unavailable or the widget is a very small throwaway.

## Theme Token Usage

Canvas cannot resolve CSS `var()` — use `window.__jawTokens` for computed values.

```javascript
const isDark = window.__jawTheme?.isDark ?? true;
const T = window.__jawTokens || {};

const chartColors = {
  text:   T['--text']     || (isDark ? '#e2e0dd' : '#1a1a1a'),
  dim:    T['--text-dim'] || (isDark ? '#aaa'    : '#555'),
  grid:   (isDark ? 'rgba(255,255,255,0.15)' : 'rgba(0,0,0,0.12)'),
  border: T['--border']   || (isDark ? 'rgba(255,255,255,0.25)' : 'rgba(0,0,0,0.15)'),
  accent: T['--accent']   || '#3b82f6',
  bg:     T['--surface']  || (isDark ? '#1a1a1a' : '#fff'),
};
```

## Chart.js Template

```html
<div style="position: relative; width: 100%; height: 300px;">
  <canvas id="myChart" role="img"
    aria-label="Description of what chart shows">
    Fallback text for screen readers.
  </canvas>
</div>
<script src="https://cdnjs.cloudflare.com/ajax/libs/Chart.js/4.4.1/chart.umd.js"
  onerror="document.body.innerHTML='<p style=&quot;color:' + (window.__jawTokens?.['--text-dim'] || '#999') + '&quot;>Chart library failed to load.</p>'">
</script>
<script>
  const isDark = window.__jawTheme?.isDark ?? true;
  const T = window.__jawTokens || {};
  const textColor = T['--text'] || (isDark ? '#e8e6e3' : '#1a1a1a');
  const gridColor = isDark ? 'rgba(255,255,255,0.08)' : 'rgba(0,0,0,0.06)';

  new Chart(document.getElementById('myChart'), {
    type: 'bar',
    data: {
      labels: ['Q1', 'Q2', 'Q3', 'Q4'],
      datasets: [{
        data: [120, 190, 300, 250],
        backgroundColor: T['--accent'] || '#3b82f6',
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: { legend: { display: false } },
      scales: {
        y: { ticks: { color: textColor }, grid: { color: gridColor } },
        x: { ticks: { color: textColor }, grid: { color: gridColor } },
      },
    }
  });
</script>
```

## Chart.js Rules
- Every `<canvas>` MUST have `role="img"` + `aria-label` + fallback text
- Height ONLY on wrapper div, never on canvas itself
- Horizontal bar: wrapper height = `(num_bars × 40) + 80` px
- Multiple charts: unique IDs (`chart1`, `chart2`)
- Always disable default legend; build custom HTML legend if needed
- Negative values: `-$5M` not `$-5M`
- Always add `onerror` handler on CDN script tags
- Use `responsive: true` + `maintainAspectRatio: false`

## Data Formatting

### Number format

| Situation | Method | Example |
|-----------|--------|---------|
| Large numbers | compact (K/M/B) | 1,234,567 → 1.2M |
| Integer | Math.round() | 42.7 → 43 |
| Decimal | toFixed(N) | 0.1234 → 0.12 |

### Currency

| Locale | prefix | Example |
|--------|--------|---------|
| USD | $ | $1,200 |
| KRW | ₩ | ₩1,200 |
| EUR | € | €1,200 |
| JPY | ¥ | ¥1,200 |

Chart.js tick formatter:
```js
options: {
  scales: {
    y: {
      ticks: {
        callback: v => '$' + (v >= 1e6 ? (v/1e6).toFixed(1)+'M' : v >= 1e3 ? (v/1e3).toFixed(0)+'K' : v)
      }
    }
  }
}
```

### Percent

Store values as integers (42 = 42%), display with "%" suffix.

### Korean number format (한국어 숫자)

| Value | Display |
|-------|---------|
| 10,000 | 1만 |
| 100,000,000 | 1억 |
| 1,000,000,000,000 | 1조 |

```js
function formatKR(v) {
  if (v >= 1e12) return (v/1e12).toFixed(1) + '조';
  if (v >= 1e8) return (v/1e8).toFixed(1) + '억';
  if (v >= 1e4) return (v/1e4).toFixed(0) + '만';
  return v.toLocaleString('ko-KR');
}
```

### ECharts formatter

```js
yAxis: {
  axisLabel: {
    formatter: v => '$' + (v >= 1e6 ? (v/1e6).toFixed(1)+'M' : v.toLocaleString())
  }
}
```

## Mobile Chart Sizing

### Label overflow prevention

- x-axis labels > 6: use `maxRotation: 45` or skip every other label
- Abbreviate on mobile: "January" → "Jan", "2026-01-15" → "1/15"

### Chart.js responsive defaults

```js
options: {
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: { position: 'bottom' }
  }
}
```

### ECharts responsive defaults

```js
option: {
  grid: { left: '15%', right: '5%', containLabel: true },
  legend: { type: 'scroll', bottom: 0 }
}
```

## Quick Chart Template

For simple bar/line/pie/scatter charts, use this minimal template to reduce boilerplate:

```js
const isDark = window.__jawTheme?.isDark ?? true;
const T = window.__jawTokens || {};
const text = T['--text'] || (isDark ? '#e8e6e3' : '#1a1a1a');
const grid = isDark ? 'rgba(255,255,255,0.08)' : 'rgba(0,0,0,0.06)';

new Chart(document.getElementById('c'), {
  type: 'bar',  // bar | line | pie | scatter | doughnut | polar
  data: {
    labels: ['A', 'B', 'C'],
    datasets: [{ data: [10, 20, 30], backgroundColor: T['--accent'] || '#3b82f6' }]
  },
  options: {
    responsive: true, maintainAspectRatio: false,
    plugins: { legend: { display: false } },
    scales: {
      y: { ticks: { color: text }, grid: { color: grid } },
      x: { ticks: { color: text }, grid: { color: grid } },
    },
  }
});
```

### Chart type routing

| Data shape | Use |
|-----------|-----|
| Simple bar/line/pie/scatter | Quick Chart Template above |
| ECharts-only types (sankey/treemap/gauge/funnel/candlestick) | Full ECharts template |
| Interactive controls needed | diagram-file with slider/select |
| Custom D3 visualization | D3 template |

## Interactive Table Widget

| Row count | Approach |
|-----------|----------|
| < 50 rows | Markdown table |
| 50-500 rows | diagram-file sortable table |
| 500+ rows | diagram-file with virtual scroll |

### Sortable table pattern

```html
<style>
  table { width: 100%; border-collapse: collapse; font-size: 14px; }
  th { cursor: pointer; user-select: none; position: sticky; top: 0;
       background: var(--surface); border-bottom: 2px solid var(--border); }
  td, th { padding: 8px 12px; text-align: left; border-bottom: 1px solid var(--border); }
  .sort-icon::after { content: ' ⇅'; opacity: 0.3; }
  .sort-asc::after { content: ' ↑'; opacity: 1; }
  .sort-desc::after { content: ' ↓'; opacity: 1; }
  input[type="text"] { width: 100%; padding: 8px; margin-bottom: 8px;
    border: 1px solid var(--border); border-radius: var(--radius-md);
    background: var(--bg); color: var(--text); }
  .table-container { max-height: 400px; overflow-y: auto; }
</style>
<input type="text" id="filter" placeholder="Filter..." aria-label="Filter table" />
<div class="table-container">
  <table id="dataTable" role="grid">
    <thead><tr></tr></thead>
    <tbody></tbody>
  </table>
</div>
<script>
  const DATA = [ /* row objects */ ];
  const COLS = Object.keys(DATA[0]);
  // Build thead, tbody, sort on th click, filter on input
</script>
```

### Rules
- Sticky header: `position: sticky; top: 0`
- Filter input above table
- Sort indicator on column headers
- Max height 400px with overflow scroll

### Virtual scroll pattern (500+ rows)

Render only the visible window — fixed row height + spacer rows keep the scrollbar true:

```html
<div class="table-container" id="vc">
  <table role="grid">
    <thead><tr><!-- th per column --></tr></thead>
    <tbody id="vb"></tbody>
  </table>
</div>
<script>
  const DATA = [ /* row objects */ ], COLS = Object.keys(DATA[0]);
  const ROW_H = 37, BUF = 10; // fixed row height (px) — required for offset math
  const vc = document.getElementById('vc'), vb = document.getElementById('vb');
  function render() {
    const start = Math.max(0, Math.floor(vc.scrollTop / ROW_H) - BUF);
    const count = Math.ceil(vc.clientHeight / ROW_H) + BUF * 2;
    const end = Math.min(DATA.length, start + count);
    const rows = DATA.slice(start, end).map(r =>
      `<tr style="height:${ROW_H}px">${COLS.map(c => `<td>${r[c]}</td>`).join('')}</tr>`);
    vb.innerHTML = `<tr style="height:${start * ROW_H}px"></tr>` + rows.join('')
      + `<tr style="height:${(DATA.length - end) * ROW_H}px"></tr>`;
  }
  let raf = null;
  vc.addEventListener('scroll', () => { if (!raf) raf = requestAnimationFrame(() => { raf = null; render(); }); });
  render();
</script>
```

- Fixed `ROW_H` on every `<tr>` is mandatory — offset math breaks otherwise
- Top/bottom spacer rows keep the scrollbar proportional to the full dataset
- Scroll handler is rAF-throttled — never re-render synchronously per event
- Reuses the sortable-table CSS above (sticky `<thead>` keeps working); sort/filter: mutate `DATA`, then call `render()`

## D3 Choropleth Template

```html
<div id="map" style="width: 100%;"></div>
<script src="https://cdnjs.cloudflare.com/ajax/libs/d3/7.8.5/d3.min.js"
  onerror="document.body.innerHTML='<p>D3 failed to load.</p>'">
</script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/topojson/3.0.2/topojson.min.js"
  onerror="document.body.innerHTML='<p>TopoJSON failed to load.</p>'">
</script>
<script>
  const isDark = window.__jawTheme?.isDark ?? true;
  const T = window.__jawTokens || {};
  const strokeColor = T['--border'] || (isDark ? 'rgba(255,255,255,.15)' : '#fff');

  const values = { 'California': 39, 'Texas': 30 };
  const color = d3.scaleQuantize([0, 40],
    isDark ? d3.schemeBlues[5] : d3.schemeBlues[7].slice(2));

  const svg = d3.select('#map').append('svg')
    .attr('viewBox', '0 0 900 560').attr('width', '100%');
  const path = d3.geoPath(d3.geoAlbersUsa().scale(1100).translate([450, 280]));

  d3.json('https://cdn.jsdelivr.net/npm/us-atlas@3/states-10m.json')
    .then(us => {
      svg.selectAll('path')
        .data(topojson.feature(us, us.objects.states).features)
        .join('path')
        .attr('d', path)
        .attr('stroke', strokeColor)
        .attr('fill', d => color(values[d.properties.name] ?? 0));
    })
    .catch(() => {
      document.getElementById('map').innerHTML =
        '<p style="color:' + (T['--text-dim'] || '#999') + '">Failed to load map data.</p>';
    });
</script>
```

## D3 Topology Sources (jsdelivr only — CSP enforced)
- US states: `https://cdn.jsdelivr.net/npm/us-atlas@3/states-10m.json`
  - Projection: `d3.geoAlbersUsa()`, object key: `.states`
- World countries: `https://cdn.jsdelivr.net/npm/world-atlas@2/countries-110m.json`
  - Projection: `d3.geoNaturalEarth1()`, object key: `.countries`

## Theme Update Handling
Listen for theme changes in the iframe:
```javascript
window.addEventListener('jaw-theme-change', (e) => {
  const isDark = e.detail.isDark;
  // Re-render chart with new colors
});
```

---

## Apache ECharts 6

Use ECharts when Chart.js can't represent the data: **heatmap, sankey, radar, treemap, gauge, funnel, candlestick, parallel, boxplot, chord**. ECharts 6 added a dedicated `chord` series (new in 6.0) for ribbon-style relationship diagrams — prefer it over the older `graph` + `layout: 'circular'` workaround.

### Theme helper (reuse for every ECharts widget)

```javascript
function buildEChartsTheme() {
  const isDark = window.__jawTheme?.isDark ?? true;
  const T = window.__jawTokens || {};
  const text = T['--text']     || (isDark ? '#e2e0dd' : '#1a1a1a');
  const dim  = T['--text-dim'] || (isDark ? '#aaa'    : '#555');
  const line = isDark ? 'rgba(255,255,255,0.12)' : 'rgba(0,0,0,0.12)';
  const accent = T['--accent'] || '#3b82f6';
  return {
    color: [accent, '#ec4899', '#a855f7', '#f97316', '#06b6d4', '#22c55e', '#f59e0b', '#ef4444'],
    backgroundColor: 'transparent',
    textStyle: { color: text, fontFamily: 'inherit' },
    title:    { textStyle: { color: text }, subtextStyle: { color: dim } },
    legend:   { textStyle: { color: text } },
    tooltip:  { backgroundColor: isDark ? '#1a1a1a' : '#fff', borderColor: line, textStyle: { color: text } },
    axisPointer: { lineStyle: { color: dim } },
    xAxis: { axisLine: { lineStyle: { color: line } }, axisLabel: { color: dim }, splitLine: { lineStyle: { color: line } } },
    yAxis: { axisLine: { lineStyle: { color: line } }, axisLabel: { color: dim }, splitLine: { lineStyle: { color: line } } },
  };
}
```

### ECharts Template (heatmap example, copy-paste ready)

Host-driven theme re-render: when the user toggles dark/light, cli-jaw's `broadcastThemeToIframes()` recreates the iframe from scratch, so the widget script re-executes with new `window.__jawTokens`. **Do NOT add a `jaw-theme-change` reload listener** — it double-reloads and fights the parent's recreation logic.

```html
<div id="heat" role="img" aria-label="Activity heatmap by day and hour"
  style="width: 100%; height: 340px;"></div>
<script src="https://cdnjs.cloudflare.com/ajax/libs/echarts/6.0.0/echarts.min.js"
  onerror="document.body.innerHTML='<p style=&quot;color:#999&quot;>ECharts failed to load.</p>'">
</script>
<script>
  const isDark = window.__jawTheme?.isDark ?? true;
  const T = window.__jawTokens || {};

  // Inline theme — same shape as buildEChartsTheme() above; paste into every ECharts widget
  const text = T['--text']     || (isDark ? '#e2e0dd' : '#1a1a1a');
  const dim  = T['--text-dim'] || (isDark ? '#aaa'    : '#555');
  const line = isDark ? 'rgba(255,255,255,0.12)' : 'rgba(0,0,0,0.12)';
  const accent = T['--accent'] || '#3b82f6';
  const theme = {
    color: [accent, '#ec4899', '#a855f7', '#f97316', '#06b6d4', '#22c55e', '#f59e0b', '#ef4444'],
    backgroundColor: 'transparent',
    textStyle: { color: text, fontFamily: 'inherit' },
    title:    { textStyle: { color: text }, subtextStyle: { color: dim } },
    legend:   { textStyle: { color: text } },
    tooltip:  { backgroundColor: isDark ? '#1a1a1a' : '#fff', borderColor: line, textStyle: { color: text } },
    axisPointer: { lineStyle: { color: dim } },
    xAxis: { axisLine: { lineStyle: { color: line } }, axisLabel: { color: dim }, splitLine: { lineStyle: { color: line } } },
    yAxis: { axisLine: { lineStyle: { color: line } }, axisLabel: { color: dim }, splitLine: { lineStyle: { color: line } } },
  };

  echarts.registerTheme('jaw', theme);
  const chart = echarts.init(document.getElementById('heat'), 'jaw', { renderer: 'canvas' });

  const hours = ['00','04','08','12','16','20'];
  const days  = ['Mon','Tue','Wed','Thu','Fri','Sat','Sun'];
  const data = [];
  for (let d = 0; d < days.length; d++)
    for (let h = 0; h < hours.length; h++)
      data.push([h, d, Math.round(Math.random() * 100)]);

  chart.setOption({
    tooltip: { position: 'top' },
    grid: { left: 60, right: 20, top: 20, bottom: 40 },
    xAxis: { type: 'category', data: hours, splitArea: { show: true } },
    yAxis: { type: 'category', data: days,  splitArea: { show: true } },
    visualMap: {
      min: 0, max: 100, orient: 'horizontal', left: 'center', bottom: 0,
      textStyle: { color: text },
      inRange: { color: isDark
        ? ['#1e293b', '#3b82f6', '#22d3ee']
        : ['#dbeafe', '#3b82f6', '#0ea5e9'] },
    },
    series: [{
      name: 'Activity',
      type: 'heatmap',
      data,
      label: { show: false },
      emphasis: { itemStyle: { shadowBlur: 0, borderColor: accent, borderWidth: 2 } },
    }],
  });

  window.addEventListener('resize', () => chart.resize());
  // Theme re-render is handled by the host — no jaw-theme-change listener needed.
</script>
```

### ECharts Sankey (flow diagram)

```javascript
chart.setOption({
  series: [{
    type: 'sankey',
    data: [
      { name: 'User' }, { name: 'Auth' }, { name: 'API' }, { name: 'DB' }, { name: 'Cache' }
    ],
    links: [
      { source: 'User', target: 'Auth', value: 100 },
      { source: 'Auth', target: 'API',  value: 95  },
      { source: 'API',  target: 'DB',   value: 60  },
      { source: 'API',  target: 'Cache', value: 35 },
    ],
    lineStyle: { color: 'gradient', curveness: 0.5 },
    label: { color: T['--text'] || '#e2e0dd' },
  }],
});
```

### ECharts Radar (skill/profile)

```javascript
chart.setOption({
  radar: {
    indicator: [
      { name: 'Speed',     max: 100 },
      { name: 'Quality',   max: 100 },
      { name: 'Reliability', max: 100 },
      { name: 'Cost',      max: 100 },
      { name: 'Security',  max: 100 },
    ],
    axisName: { color: T['--text-dim'] || '#aaa' },
    splitLine: { lineStyle: { color: isDark ? 'rgba(255,255,255,0.08)' : 'rgba(0,0,0,0.08)' } },
    splitArea: { show: false },
  },
  series: [{
    type: 'radar',
    data: [{ value: [80, 90, 70, 60, 85], name: 'Option A' }],
    areaStyle: { opacity: 0.2 },
  }],
});
```

### ECharts Rules

- **Always register the inline theme before `echarts.init(el, 'jaw')`** — never use ECharts default `dark`/`light` themes (they clash with cli-jaw oklch palette)
- `renderer: 'canvas'` (default); SVG renderer is optional but canvas performs better in iframe
- Wrapper height mandatory on outer `<div>`; container width 100%
- Always call `window.addEventListener('resize', () => chart.resize())`
- **Theme switch**: do nothing. cli-jaw's host recreates the iframe on theme toggle, so the widget re-runs from scratch with new `__jawTokens`. Do NOT add a `jaw-theme-change` listener — it will double-reload and fight the parent.
- `<canvas role="img" aria-label="...">` alternative: ECharts creates its own canvas inside the div, so add `role="img"` + `aria-label` on the outer `<div id="heat">` instead
- `onerror` on script tag required (same as Chart.js)
- Do NOT use `echarts-gl` (WebGL extension) — overlaps Three.js, huge bundle
- Do NOT use ECharts map charts in this phase — requires `connect-src` + geoJSON fetch, reconsider after Leaflet phase
- Bundle size: ECharts 6.0.0 full build is ~1 MB min / ~350 KB gz. Load one chart per widget, lazy-load on widget mount only. If the chart is a single series type, consider lightweight Chart.js instead.
- ECharts 6.0.0 is still the latest 6.x release as of 2026-04 (no 6.0.x patch shipped). Pin the exact version.
