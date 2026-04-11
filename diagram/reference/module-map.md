# Interactive Map Reference (Leaflet)

Use Leaflet for interactive maps: tile-based panning/zooming, markers, popups, polylines, polygons, circles. No API key required (OpenStreetMap tiles). D3 choropleth in `module-chart.md` remains the right choice for **static** country/state boundary fills without tile imagery.

## Library Version (CDN)

| Library | Version | CDN URL |
|---|---|---|
| Leaflet JS | 1.9.4 | `https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/leaflet.js` |
| Leaflet CSS | 1.9.4 | `https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/leaflet.css` |

## Minimal Template

```html
<link rel="stylesheet"
  href="https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/leaflet.css" />
<div id="map" role="img" aria-label="Interactive map of Seoul"
  style="width:100%; height:420px; border-radius: 8px; overflow: hidden;">
  Interactive map of Seoul. Requires JavaScript.
</div>
<script src="https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/leaflet.js"
  onerror="document.body.innerHTML='<p style=&quot;color:#999&quot;>Leaflet failed to load.</p>'">
</script>
<script>
  // Explicit marker icon URLs — belt-and-suspenders against Leaflet's CSS-based auto-detect,
  // which can fail if leaflet.css loads slowly or is blocked. Pin to the same CDN as the script.
  // Uses non-deprecated prototype.options pattern (L.Icon.Default.imagePath is deprecated as of Leaflet 1.x).
  const LEAFLET_CDN = 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/';
  Object.assign(L.Icon.Default.prototype.options, {
    iconUrl:       LEAFLET_CDN + 'marker-icon.png',
    iconRetinaUrl: LEAFLET_CDN + 'marker-icon-2x.png',
    shadowUrl:     LEAFLET_CDN + 'marker-shadow.png',
  });

  const map = L.map('map', { zoomControl: true }).setView([37.5665, 126.9780], 12);

  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    subdomains: ['a', 'b', 'c'],
    maxZoom: 19,
    attribution: '© OpenStreetMap contributors',
  }).addTo(map);

  L.marker([37.5665, 126.9780])
    .addTo(map)
    .bindPopup('<b>Seoul City Hall</b><br/>Capital of South Korea')
    .openPopup();
</script>
```

## Leaflet Rules

- **Tile source**: use OpenStreetMap standard tiles only — `https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png` with `subdomains: ['a','b','c']`. Any other tile server (Mapbox, Stamen, Thunderforest, Esri) is blocked by CSP and must not be used.
- **Container**: outer `<div>` needs explicit height (px or vh), `role="img"`, `aria-label`, and fallback text for screen readers. Width: 100% of widget. Recommended height: 360–480px.
- **Map creation**: `L.map(id, options).setView([lat, lng], zoom)`. Latitude first, then longitude (opposite of some APIs). Initial zoom 10–14 for city scale, 4–6 for country scale, 2 for world.
- **Markers**: `L.marker([lat, lng]).addTo(map).bindPopup('...')`. Default icon URLs MUST be set explicitly via `Object.assign(L.Icon.Default.prototype.options, { iconUrl, iconRetinaUrl, shadowUrl })` right after the Leaflet script loads — do NOT rely on Leaflet's CSS-based auto-detection (fragile if `leaflet.css` load is delayed), and do NOT use the deprecated `L.Icon.Default.imagePath` property. Do NOT override icon URLs with other external domains.
- **Popups**: HTML strings inside `bindPopup(...)` are sanitized by Leaflet itself. Keep them small and text-first. No scripts inside popups.
- **Layers**: `L.polyline`, `L.polygon`, `L.circle`, `L.geoJSON(data)` all work. Pass GeoJSON data **inlined in the script** — do not fetch from external URLs (blocked by `connect-src`).
- **Theme integration**: Leaflet doesn't have a dark mode built in. For dark cli-jaw theme, invert the tile layer with CSS — see "Dark mode" below.
- **Attribution**: the `© OpenStreetMap contributors` attribution is required by the ODbL license. Do not remove it.
- **`onerror` required** on the script tag, same rule as every other CDN script.
- **Do not** use Leaflet plugins (Leaflet.draw, Leaflet.heat, markercluster, etc.) in this phase — core 1.9.4 only.

## Dark Mode

Leaflet 1.x has no native dark mode. Use a CSS filter on the tile layer for a usable dark appearance:

```html
<style>
  /* Apply only when host theme is dark */
  .jaw-dark #map .leaflet-tile-pane {
    filter: invert(0.92) hue-rotate(200deg) saturate(0.3) brightness(0.85) contrast(1.1);
  }
</style>
<script>
  // Add theme class to the iframe body on load and on theme change
  const setTheme = () => {
    document.body.classList.toggle('jaw-dark', window.__jawTheme?.isDark ?? true);
  };
  setTheme();
  window.addEventListener('jaw-theme-change', setTheme);
</script>
```

## Accessibility

- Always set `role="img"` and `aria-label` on the outer `<div>` (describes the map purpose, not the specific coordinates)
- Keyboard panning is built into Leaflet when the map container has focus
- Marker popups are keyboard-focusable by default
- Provide text fallback inside the `<div>` for screen readers and no-JS contexts

## When NOT to use Leaflet

Use **D3 choropleth** (`module-chart.md`) when:
- You need a static country/state fill based on a metric (no tiles)
- The audience doesn't need to pan or zoom
- You want the diagram to print or export cleanly

Use **Mermaid** when:
- The "map" is actually a network diagram (use `flowchart` or `architecture-beta`)
- The goal is conceptual, not geographic

## CSP Note (host-managed)

When your `diagram-html` block contains the string `leaflet` or `L.tileLayer` or `tile.openstreetmap.org`, the cli-jaw host iframe-renderer automatically expands `img-src` and `style-src` to allow OpenStreetMap tiles, Leaflet CDN marker icons, and Leaflet CSS. You do not need to request a CSP change — just use Leaflet correctly and the host does the rest.
