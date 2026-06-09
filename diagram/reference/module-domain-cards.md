# Domain-Specific Rich Card Templates

HTML card templates for domain data (weather, finance, sports, products).
Use inside `diagram-html` blocks with jaw theme tokens.

## Common Card Style

```css
.domain-card {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 12px;
  padding: 16px;
  font-family: var(--font-family, system-ui);
  color: var(--text);
}
.positive { color: #22c55e; }
.negative { color: #ef4444; }
.card-header { font-size: 18px; font-weight: 600; margin-bottom: 12px; }
.card-meta { font-size: 13px; color: var(--text-dim); }
```

## Weather Card

```html
<div class="domain-card weather-card">
  <div class="card-header">
    <span class="weather-icon">☀️</span>
    <span class="weather-temp">24°C</span>
    <span class="card-meta">Seoul, KR</span>
  </div>
  <div class="weather-details" style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 8px; margin: 12px 0;">
    <div>💧 Humidity 65%</div>
    <div>💨 Wind 12km/h</div>
    <div>🌡️ Feels like 26°C</div>
  </div>
  <div class="forecast" style="display: flex; gap: 8px; overflow-x: auto;">
    <!-- 5-day forecast items -->
    <div class="forecast-day" style="text-align: center; min-width: 60px;">
      <div class="card-meta">Mon</div>
      <div>⛅</div>
      <div>22° / 15°</div>
    </div>
  </div>
</div>
```

### Rules
- Icon: emoji or SVG (no external image dependencies)
- Temperature: always include unit (°C or °F)
- Forecast: horizontal scroll for 5+ days
- Details grid: 3-column on desktop, stack on mobile

## Finance Card

```html
<div class="domain-card finance-card">
  <div class="card-header">
    <span class="ticker-symbol" style="font-weight: 700;">AAPL</span>
    <span class="card-meta">Apple Inc.</span>
  </div>
  <div class="ticker-price" style="margin: 8px 0;">
    <span style="font-size: 28px; font-weight: 700;">$198.45</span>
    <span class="positive" style="margin-left: 8px;">+2.31 (+1.18%)</span>
  </div>
  <div class="chart-container" style="height: 200px;">
    <!-- ECharts candlestick or line chart -->
  </div>
  <div class="metrics" style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 8px; margin-top: 12px; font-size: 13px;">
    <div>Open: $196.14</div>
    <div>High: $199.02</div>
    <div>Volume: 48.2M</div>
    <div>P/E: 31.2</div>
  </div>
</div>
```

### Rules
- Price change: `.positive` (green) for up, `.negative` (red) for down
- Chart: ECharts candlestick preferred, line chart acceptable
- Metrics: 2-column grid, keep to 4-6 key metrics
- Number format: see module-chart.md "Data Formatting" section

## Sports Scoreboard

```html
<div class="domain-card scoreboard">
  <div class="card-meta" style="text-align: center; margin-bottom: 12px;">
    EPL · Matchday 15 · Dec 7
  </div>
  <div class="match-row" style="display: flex; align-items: center; justify-content: center; gap: 16px;">
    <div class="team" style="text-align: right; flex: 1;">
      <span style="font-weight: 600;">Liverpool</span>
    </div>
    <div class="score" style="font-size: 28px; font-weight: 700; min-width: 80px; text-align: center;">
      3 - 1
    </div>
    <div class="team" style="text-align: left; flex: 1;">
      <span style="font-weight: 600;">Manchester City</span>
    </div>
  </div>
  <div class="match-details" style="display: flex; justify-content: center; gap: 24px; margin-top: 12px; font-size: 13px; color: var(--text-dim);">
    <div>⚽ Salah 12', 45' · Gakpo 67'</div>
    <div>⚽ Haaland 33'</div>
  </div>
</div>
```

### Rules
- Team logos: emoji or text initials (no external image dependencies unless URL is provided)
- Score: large centered text, bold
- Match details: smaller text below score
- Multiple matches: repeat `.match-row` blocks with dividers

## Product Card Grid

```html
<div class="product-grid" style="display: grid; grid-template-columns: repeat(auto-fill, minmax(160px, 1fr)); gap: 12px;">
  <div class="domain-card" style="padding: 12px; text-align: center;">
    <div style="font-size: 48px; margin-bottom: 8px;">📦</div>
    <div style="font-weight: 600; margin-bottom: 4px;">Product Name</div>
    <div style="font-size: 18px; font-weight: 700; margin-bottom: 4px;">₩45,000</div>
    <div class="card-meta">⭐ 4.5 (1,234)</div>
  </div>
  <!-- repeat cards -->
</div>
```

### Rules
- Image: emoji placeholder if no URL available
- Price: bold, prominent
- Rating: star emoji + numeric + review count
- Grid: `auto-fill, minmax(160px, 1fr)` for responsive columns

## Routing

| Data type | Card template | Chart |
|-----------|--------------|-------|
| Stock / FX | Finance card | ECharts candlestick |
| Weather | Weather card | None (icon-based) |
| Match results | Scoreboard | None (table-based) |
| Standings / rankings | Sortable table (see module-chart.md) | Optional bar chart |
| Product comparison | Product grid | Optional radar chart |
