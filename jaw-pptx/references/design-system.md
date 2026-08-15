# Design System Reference

## Color Palettes (20 options)

Select a palette that matches the content theme. Column roles: **Primary** dominates (60-70% of
visual weight), **Secondary** supports (30%), **Accent** is one-hit emphasis (10%), **Text** is body
copy on light fills, **Muted** is captions / axis labels / footer.

> Deriving Text/Muted: **Text** = a near-black harmonized with the family (warm palettes → warm
> near-black, cool → cool near-black). **Muted** = a desaturated mid-tone (~45-55% lightness) of the
> primary family. Dark-background palettes (Navy Corporate, Neon Dark, Cyber Blue) use **Text** as the
> light on-dark tone.

### Business & Professional

| Theme              | Primary (60%) | Secondary (30%) | Accent (10%) | Text     | Muted    |
| ------------------ | ------------- | --------------- | ------------ | -------- | -------- |
| Midnight Executive | `1E2761`      | `CADCFC`        | `FFFFFF`     | `333333` | `8899BB` |
| Charcoal Minimal   | `36454F`      | `F2F2F2`        | `212121`     | `333333` | `7A8A94` |
| Navy Corporate     | `0D1B2A`      | `1B3A5C`        | `E0E1DD`     | `E0E1DD` | `6B7C8D` |
| Slate Professional | `2C3E50`      | `ECF0F1`        | `E74C3C`     | `333333` | `7A8A94` |

### Nature & Wellness

| Theme          | Primary (60%) | Secondary (30%) | Accent (10%) | Text     | Muted    |
| -------------- | ------------- | --------------- | ------------ | -------- | -------- |
| Forest & Moss  | `2C5F2D`      | `97BC62`        | `F5F5F5`     | `2D2D2D` | `6B8E6B` |
| Sage Calm      | `84B59F`      | `69A297`        | `50808E`     | `2D3A36` | `6E8B82` |
| Ocean Gradient | `065A82`      | `1C7293`        | `21295C`     | `2B3A4E` | `6B8FAA` |
| Earth Warm     | `5D4037`      | `D7CCC8`        | `FF8F00`     | `3E2B25` | `8C7B73` |

### Energy & Creative

| Theme           | Primary (60%) | Secondary (30%) | Accent (10%) | Text     | Muted    |
| --------------- | ------------- | --------------- | ------------ | -------- | -------- |
| Coral Energy    | `F96167`      | `F9E795`        | `2F3C7E`     | `333333` | `8B7E6A` |
| Cherry Bold     | `990011`      | `FCF6F5`        | `2F3C7E`     | `2D1518` | `8A6B6E` |
| Berry & Cream   | `6D2E46`      | `A26769`        | `ECE2D0`     | `3D2233` | `8C6B7A` |
| Electric Purple | `5B2C6F`      | `D2B4DE`        | `F39C12`     | `2E2233` | `8B7A95` |

### Tech & Modern

| Theme       | Primary (60%) | Secondary (30%) | Accent (10%) | Text     | Muted    |
| ----------- | ------------- | --------------- | ------------ | -------- | -------- |
| Teal Trust  | `028090`      | `00A896`        | `02C39A`     | `1F3A3D` | `5E8A8C` |
| Neon Dark   | `121212`      | `1DB954`        | `FFFFFF`     | `FFFFFF` | `8A8A8A` |
| Cyber Blue  | `0A192F`      | `64FFDA`        | `CCD6F6`     | `CCD6F6` | `8892B0` |
| Glass Light | `F8F9FA`      | `E9ECEF`        | `495057`     | `212529` | `6C757D` |

### Warmth & Friendly

| Theme           | Primary (60%) | Secondary (30%) | Accent (10%) | Text     | Muted    |
| --------------- | ------------- | --------------- | ------------ | -------- | -------- |
| Warm Terracotta | `B85042`      | `E7E8D1`        | `A7BEAE`     | `3D2B2B` | `8C7B75` |
| Golden Hour     | `F4A261`      | `264653`        | `E76F51`     | `264653` | `8A7B6A` |
| Rose Soft       | `FADBD8`      | `F5B7B1`        | `922B21`     | `4A2522` | `A88B88` |
| Sand Dune       | `C4A35A`      | `F5F0E1`        | `3E2723`     | `3E2723` | `9A8763` |

## Font Pairings

| Header       | Body           | Mood                  |
| ------------ | -------------- | --------------------- |
| Georgia      | Calibri        | Classic, trustworthy   |
| Arial Black  | Arial          | Bold, intuitive        |
| Trebuchet MS | Calibri        | Modern, clean          |
| Cambria      | Calibri Light  | Academic, polished     |
| Impact       | Arial          | Impactful              |
| Palatino     | Garamond       | Elegant, formal        |
| Consolas     | Calibri        | Tech, code             |
| Segoe UI     | Segoe UI Light | MS native, contemporary|

## Korean Fonts

| Font               | License   | Cross-platform | Best for           |
| ------------------ | --------- | -------------- | ------------------ |
| Noto Sans KR       | OFL       | Win/Mac/Linux  | Safest choice      |
| Pretendard         | OFL       | Win/Mac/Linux  | Modern UI          |
| Malgun Gothic      | MS bundle | Windows only   | Windows-only decks |
| NanumGothic        | OFL       | Win/Mac/Linux  | General Korean     |

## Product-Personality → Slide Tokens

When a user references a product ("Notion 느낌", "Linear처럼"), start from these. Adjust to brand.
Web-only signatures (Cmd+K, real-time cursors, backdrop-blur) are intentionally stripped — they are
projection-unsafe.

| Reference | Palette seed | Dials (VAR/DEN/MOT) | Corner radius | Signature move |
|-----------|--------------|---------------------|---------------|----------------|
| **Notion** | off-white `F6F5F4` bg, black text, blue accent `097FE8` | 3 / 5 / 1 | 8-12px | warm-clean block composition |
| **Linear** | pure-black bg, purple-gradient accent | 6 / 3 / 4 | 6-8px sharp | premium dark, minimal |
| **Vercel** | near-monochrome, Geist/Pretendard | 4 / 2 / 1 | 0-4px | aggressive whitespace, austere data |
| **Stripe** | multi-color complementary gradients, weight-300 type | 7 / 4 / 5 | 4-8px | polished sales, sharp copy |
| **Apple** | charcoal/midnight, system font, 40px+ margins | 4 / 2 / 6 | 12-20px | spacious luxury keynote (NO backdrop-blur) |
| **Figma** | neutral chrome + colorful content primitives | 6 / 5 / 4 | 8px | playful workshop/creative |
