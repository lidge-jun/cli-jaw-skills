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
- Team logos: emoji or text initials — arbitrary external image URLs are CSP-blocked (`img-src` allows only CDN-allowlist hosts, `data:`, `blob:`)
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
- Image: emoji placeholder — external image URLs render only from CDN-allowlist hosts (CSP `img-src`); otherwise stay with emoji
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

## Real-time Data Pipeline

Domain cards are most valuable with **live data**. Since diagram-html iframes set `connect-src 'none'` by default (only a narrow D3 TopoJSON exception exists for `cdn.jsdelivr.net`), `fetch()` / `XMLHttpRequest` to external APIs will silently fail. The agent must **pre-fetch data and inline it** into the template.

### Pipeline pattern

```
1. WebSearch "{domain} {query}" → identify data source URL
2. WebFetch source URL → extract structured values
3. Inject extracted values as JS object literals into diagram-html
4. Output diagram-html with real data inlined
5. Add source attribution + timestamp footer
```

### Data source routing

| Domain | Primary source | Fallback | Fetch method |
|--------|---------------|----------|--------------|
| Weather (KR) | `wttr.in/{City}?format=j1` | weather.go.kr | WebFetch → JSON: temp_C, humidity, windspeedKmph, weatherDesc |
| Weather (global) | `wttr.in/{City}?format=j1` | AccuWeather | Same JSON extraction |
| Stock/Index (KR) | `kr.investing.com/indices/*` | finance.naver.com | WebFetch → scrape: 현재가, 변동, 변동률, 시가, 고가, 저가, 거래량 |
| Stock (US) | `investing.com/equities/*` | Yahoo Finance | WebFetch → scrape ticker values |
| FX rate | `investing.com/currencies/*` | xe.com | WebFetch → scrape rate pair |
| Sports (KR) | KBO/KFA official | flashscore.com | WebFetch → scrape scores |
| Sports (global) | ESPN | flashscore.com | WebFetch → scrape match data |

### CSP constraint (critical)

```js
// ✅ Correct — agent pre-fetched, data inlined as literal
const WEATHER = { temp: 19, humidity: 68, wind: 5, desc: "Overcast", location: "Seoul" };
const KOSPI = { value: 8096.93, change: 612.52, pct: 8.18, open: 7697.76, high: 8119.09, low: 7598.87 };

// ❌ Wrong — will fail silently in iframe (connect-src 'none')
const resp = await fetch('https://wttr.in/Seoul?format=j1');
```

### Inline data template (weather example)

```html
<script>
  // Agent injects real values here before output
  const W = { temp: 19, feels: 19, humidity: 68, wind: 5, desc: "Overcast", city: "Seoul" };
</script>
<div class="domain-card weather-card">
  <div class="card-header">
    <span class="weather-icon" id="wicon"></span>
    <span class="weather-temp" id="wtemp"></span>
    <span class="card-meta" id="wcity"></span>
  </div>
  <!-- ... template structure from Weather Card section above ... -->
  <div style="margin-top: 12px; font-size: 10px; color: var(--text-dim); text-align: right;">
    출처: wttr.in · 실시간
  </div>
</div>
<script>
  const icons = { Sunny: '☀️', Clear: '🌙', 'Partly cloudy': '⛅', Cloudy: '☁️', Overcast: '☁️',
    Rain: '🌧️', Snow: '❄️', Fog: '🌫️', Thunderstorm: '⛈️' };
  document.getElementById('wicon').textContent = icons[W.desc] || '🌤️';
  document.getElementById('wtemp').textContent = W.temp + '°C';
  document.getElementById('wcity').textContent = W.city;
</script>
```

### Error handling

When WebSearch/WebFetch fails, output a graceful degradation card or inform the user in text:

```html
<div class="domain-card" style="text-align: center; padding: 32px;">
  <div style="font-size: 24px; margin-bottom: 8px;">⚠️</div>
  <div style="color: var(--text-dim);">데이터를 가져올 수 없습니다</div>
  <div style="font-size: 12px; color: var(--text-dim); margin-top: 4px;">
    Source: wttr.in · Retry later
  </div>
</div>
```

### Source attribution (mandatory)

Every domain card with live data **must** include a footer:

```html
<div style="margin-top: 12px; font-size: 10px; color: var(--text-dim); text-align: right;">
  출처: {source_name} · {timestamp_or_status}
</div>
```

| Data type | Market/context | Timestamp format |
|-----------|---------------|-----------------|
| Weather | Any | "실시간" or "N분 전 기준" |
| Stock (market open) | 장중 | "장중 · HH:MM 기준" |
| Stock (market closed) | 장마감 | "YYYY.MM.DD 장마감 기준" |
| FX rate | Any | "YYYY.MM.DD HH:MM 기준" |
| Sports (live) | In progress | "LIVE" with accent color badge |
| Sports (final) | Finished | "종료 · YYYY.MM.DD" |

### Checklist for domain card with live data

1. WebSearch to identify current data source
2. WebFetch to extract structured values
3. Inject values as JS object literal (not fetch() inside iframe)
4. Weather icon mapping (desc → emoji)
5. Number formatting per module-chart.md Data Formatting section
6. Korean number format for KRW amounts (만/억/조)
7. Source attribution footer with timestamp
8. Positive (green `.positive`) / negative (red `.negative`) color coding for financial data
9. Theme-aware styling (`var(--surface)`, `var(--text)`, `isDark`)
