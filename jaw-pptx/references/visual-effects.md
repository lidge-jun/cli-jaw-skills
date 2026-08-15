# Visual Effects Reference

OfficeCLI supports a full shape/text effect vocabulary. Use effects to create depth and focus —
sparingly. One or two effects per slide; never gradient-on-everything (§5.13).

> Grammar source of truth: `officecli help all` (pptx shape rows). Two footguns:
> **opacity needs a fill to attach to**, and a **shadow on a text-only shape routes to the text run**
> (rPr) — for a card/panel shadow, put it on a *filled* shape.

## Recipes (copy-paste, adjust x/y/size)

### 1. Gradient hero background (full-bleed)
```bash
officecli add deck.pptx '/slide[1]' --type shape --prop geometry=rect \
  --prop x=0cm --prop y=0cm --prop width=33.87cm --prop height=19.05cm \
  --prop gradient="0F2027-203A43-2C5364-45" --prop line=none
```
4th gradient segment (`-45`) is the angle in degrees.

### 2. Soft card shadow (modern elevation, not harsh black)
```bash
officecli add deck.pptx '/slide[1]' --type shape --prop geometry=roundRect \
  --prop fill=FFFFFF --prop x=2cm --prop y=4cm --prop width=10cm --prop height=6cm \
  --prop shadow="000000-12-90-4-25"
```
`shadow=color-blur-angle-dist-opacity` — low opacity (25) + large blur (12) = soft depth.

### 3. Glow accent / focus halo (KPI dots, active nodes)
```bash
officecli add deck.pptx '/slide[1]' --type shape --prop geometry=ellipse \
  --prop fill=4472C4 --prop width=1.2cm --prop height=1.2cm --prop glow="4472C4-18-60"
```

### 4. Glassmorphism / frosted card (use on a textured/photo bg, not flat white)
```bash
officecli add deck.pptx '/slide[1]' --type shape --prop geometry=roundRect \
  --prop fill=FFFFFF --prop opacity=0.18 --prop line=FFFFFF:0.75 --prop softEdge=2
```

### 5. Gradient text title
```bash
officecli add deck.pptx '/slide[1]' --type shape --prop geometry=rect --prop line=none \
  --prop text='Quarterly Results' --prop textFill="7F00FF-E100FF" --prop size=54 --prop bold=true
```

### 6. Inner-shadow inset panel (recessed well / pressed state)
```bash
officecli add deck.pptx '/slide[1]' --type shape --prop geometry=roundRect \
  --prop fill=1A1A2E --prop innerShadow="000000-8-90-3-40"
```

### 7. Reflection logo / hero (premium decks)
```bash
officecli add deck.pptx '/slide[1]' --type picture --prop path=logo.png \
  --prop x=12cm --prop y=3cm --prop width=8cm --prop reflection=half
```

### 8. Subtle pattern band (texture without an image asset)
```bash
officecli add deck.pptx '/slide[1]' --type shape --prop geometry=rect \
  --prop x=0cm --prop y=16cm --prop width=33.87cm --prop height=3cm \
  --prop pattern="ltUpDiag:F0F0F0:FFFFFF"
```

## Effect → prop quick reference

| Effect | Prop | Grammar |
|--------|------|---------|
| Linear gradient | `gradient` | `C1-C2[-ANGLE]` or `C@pos-C@pos-...` |
| Radial gradient | `gradient` | `radial:C1-C2[-FOCUS]` (focus tl/tr/bl/br/center) |
| Outer shadow | `shadow` | `color-blur-angle-dist-opacity` or `true` |
| Inner shadow | `innerShadow` | `color-blur-angle-dist-opacity` |
| Glow | `glow` | `color-radius-opacity` or `true` |
| Soft edge | `softEdge` | radius in pt |
| Reflection | `reflection` | `tight`/`half`/`full`/`true` |
| Fill opacity | `opacity` | `0.0`–`1.0` (needs a fill) |
| Pattern fill | `pattern` | `preset[:fg[:bg]]` (e.g. `diagBrick`, `ltUpDiag`) |
| Text fill / gradient | `textFill` | color or gradient |
| 3D bevel / depth | `bevel` / `depth` | preset / pt |
