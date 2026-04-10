# Chart.js + D3 Integration Reference

## Library Versions (CDN)

| Library | Version | CDN URL |
|---|---|---|
| Chart.js | 4.4.1 | `https://cdnjs.cloudflare.com/ajax/libs/Chart.js/4.4.1/chart.umd.js` |
| D3.js | 7.8.5 | `https://cdnjs.cloudflare.com/ajax/libs/d3/7.8.5/d3.min.js` |
| TopoJSON | 3.0.2 | `https://cdnjs.cloudflare.com/ajax/libs/topojson/3.0.2/topojson.min.js` |

## Theme Token Usage

Canvas cannot resolve CSS `var()` — use `window.__jawTokens` for computed values.

```javascript
const isDark = window.__jawTheme?.isDark ?? true;
const T = window.__jawTokens || {};

const chartColors = {
  text:   T['--text']     || (isDark ? '#e8e6e3' : '#1a1a1a'),
  dim:    T['--text-dim'] || (isDark ? '#999'     : '#666'),
  grid:   (isDark ? 'rgba(255,255,255,0.08)' : 'rgba(0,0,0,0.06)'),
  border: T['--border']   || (isDark ? 'rgba(255,255,255,0.15)' : 'rgba(0,0,0,0.1)'),
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
