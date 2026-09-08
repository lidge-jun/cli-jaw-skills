# Document Design System Reference

Named palettes, font pairings, and a personality map for Word documents. Use after the Design Read
(SKILL.md §5.0): pick a palette + font pair + personality, then commit to them across the document.
If the user names a brand or template, match that first — these are calibrated seeds, not a menu.

## Palettes

Roles: **Primary** (headings, rules, accents — one dominant), **Accent** (sparing emphasis), **Text**
(body, near-black not pure black), **Muted** (captions, footers, source lines).

| Palette | Primary | Accent | Text | Muted | Reads as |
|---|---|---|---|---|---|
| Executive Navy | `1F3864` | `2E74B5` | `262626` | `808080` | corporate, board, annual report |
| Slate Professional | `2C3E50` | `C0392B` | `333333` | `7A8A94` | consulting, proposal |
| Forest Formal | `2C5F2D` | `97804F` | `2D2D2D` | `6B8E6B` | sustainability, public sector |
| Charcoal Minimal | `36454F` | `0F6FC6` | `2B2B2B` | `8A8A8A` | tech whitepaper, modern memo |
| Academic Plum | `4A235A` | `884EA0` | `212121` | `7F8C8D` | thesis, scholarly paper |
| Warm Editorial | `7B341E` | `B7791F` | `2D2A26` | `8C7B75` | magazine, brand story |

Rules: one Primary dominates; one Accent only; body stays `Text` (near-black). Never 4+ colors in body.
On a dark cover/section band, body/heading text on it must be white or brightness > 80%.

## Font Pairings

| Heading | Body | Best for |
|---|---|---|
| Georgia | Calibri | formal business, finance |
| Cambria | Calibri Light | academic, polished |
| Calibri | Calibri | clean corporate default (give it identity via palette + scale) |
| Trebuchet MS | Calibri | friendly tech, startup memo |
| Palatino Linotype | Garamond | elegant, editorial |
| Segoe UI Semibold | Segoe UI | modern MS-native |

Korean-first: **Noto Sans KR** / **Pretendard** (body), pair with a CJK-safe heading; avoid Malgun Gothic
as sole primary. Two faces max (a third display face only for a cover title).

## Personality → Document Type

| Personality | Doc type | Palette + dials |
|---|---|---|
| Authoritative / trustworthy | board report, annual review | Executive Navy · serif heading · dense, conservative spacing |
| Rigorous / scholarly | thesis, research paper | Academic Plum · Cambria/Calibri · numbered headings, TOC, footnotes |
| Sharp / persuasive | proposal, pitch memo | Slate Professional · strong accent · generous whitespace, callouts |
| Modern / technical | whitepaper, spec | Charcoal Minimal · Segoe UI · code blocks, diagrams, tight scale |
| Warm / narrative | brand story, newsletter | Warm Editorial · editorial serif · pull-quotes, imagery |

## Type Scale (anchor)
Title ≥ 26pt; H1 18–20pt; H2 14–16pt; H3 12–13pt; body 11pt; caption/source 9pt muted. Set sizes on
real heading styles (not manual bold) so the TOC + navigation work (SKILL.md §5.1).
