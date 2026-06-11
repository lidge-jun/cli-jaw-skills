# Visual Direction

Run a design read before creating any non-trivial original video. This prevents
"rendered but generic" output.

## Design Read

Capture these decisions before authoring:

| Field | Questions |
|---|---|
| Audience | developers, executives, consumers, internal team, social viewers |
| Platform | 16:9 briefing, 9:16 short, square social, website hero, internal report |
| Purpose | explain, persuade, summarize, announce, teach, compare, document |
| Visual mood | premium, utilitarian, cinematic, editorial, playful, technical |
| Palette | base, accent, contrast, banned colors |
| Typography | display/body/mono style, CJK requirements |
| Density | sparse, editorial, dense evidence, social hook |
| Motion intensity | quiet, moderate, kinetic, high-energy |
| Assets | screenshots, code, charts, footage, generated images, none |
| Verification focus | text readability, chart legibility, cut boundaries, brand match |

If the user does not specify a style, choose a style pack from `style-packs.md`.

## Required Output In Planning Notes

Write a compact visual brief:

```text
Visual direction:
- Audience:
- Platform:
- Style pack:
- Palette:
- Typography:
- Density:
- Motion:
- Banned cliches:
- QA focus:
```

## Layout Before Animation

For composed videos:

1. Build the most visible frame as a static layout.
2. Confirm hierarchy, line breaks, and spacing.
3. Add entrance motion from that layout.
4. Add exit motion after the layout works.

Do not start with animated offscreen states and hope the final layout lands.

## Frame Thinking

A video frame is not a web dashboard.

- One beat should have one primary focus.
- Motion should support the viewer's reading path.
- Text must be readable at final resolution.
- Do not fill the frame with repeated cards unless the style pack explicitly
  calls for dense evidence.
- Use negative space deliberately.

## CJK Readability

For Korean/Japanese/Chinese:

- avoid orphan fragments at line breaks
- keep body text large enough for 1080p
- prefer fonts known to support the script
- check sampled frames, not only source CSS/JSX
