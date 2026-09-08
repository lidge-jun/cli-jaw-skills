# HyperFrames Route

HyperFrames is the HTML-first route for code-based video tasks where an AI coding agent should directly edit the composition. Use it for HTML/CSS/GSAP scenes, website-capture experiments, agent-editable motion graphics, and premium tech briefing videos.

## Use When

- The requested video can be authored as `index.html`.
- The user wants an agent-friendly edit loop: change text, layout, timing, media, and transitions directly.
- The visual direction benefits from web-native composition, GSAP-style motion, or reusable HTML blocks.
- The output needs deterministic local MP4 evidence from a code artifact.

## Do Not Use When

- The existing Remotion JSON timeline, TTS, caption, or component pipeline already fits the task.
- The task is only a media transform such as trim, concat, transcode, proxy, loudness, or reframe; use FFmpeg first.
- A route requires global Codex/Claude/HyperFrames skill installation and the user did not explicitly ask for that.
- Docker is missing but local non-Docker render is enough; do not block on Docker for local smoke renders.

## Commands

```bash
npx --yes hyperframes doctor
npx --yes hyperframes init /tmp/my-video --example blank --non-interactive --skip-skills --resolution landscape
npx --yes hyperframes lint /tmp/my-video
npx --yes hyperframes inspect /tmp/my-video
npx --yes hyperframes render /tmp/my-video --output /tmp/my-video/renders/out.mp4 --format mp4 --quality standard --fps 30
ffprobe -v error -show_format -show_streams -of json /tmp/my-video/renders/out.mp4
```

If `hyperframes snapshot` fails or is unavailable, extract frames with FFmpeg:

```bash
mkdir -p /tmp/my-video/snapshots
ffmpeg -y -i /tmp/my-video/renders/out.mp4 -vf fps=1/3 /tmp/my-video/snapshots/frame_%02d.png
```

## Production Loop

1. Summarize the source into 3-4 beats.
2. Write a short storyboard with durations.
3. Produce a design read using `reference/visual-direction.md`: mood, palette, typography, density, and motion intensity.
4. Choose a style pack from `reference/style-packs.md` or define a project-specific one.
5. Author or replace the HyperFrames `index.html`; do not render the untouched blank scaffold.
6. Run `hyperframes lint`.
7. Run `hyperframes inspect` or capture representative snapshots.
8. Render to MP4.
9. Validate with `ffprobe`.
10. Inspect frames for blank output, text clipping, poor hierarchy, and motion quality.
11. Record commands, artifact paths, and visual QA in devlog.

## Premium Tech Briefing Style

Use this style when the user asks for dev-frontend/dev-uiux-design polish or when the task is a tech-news explainer.
For the full reusable style-pack contract, read `reference/style-packs.md`.

- Background: off-black, charcoal, or zinc-950; never pure black.
- Accent: restrained chrome/cyan or one high-contrast cool accent.
- Typography: large CJK-safe headline, compact labels, no emoji as visual UI.
- Layout: asymmetric news/developer briefing; avoid centered card stacks.
- Motion: one clear hero motion per beat, with quiet secondary movement.
- Texture: subtle grain, scanline, grid, or terminal-like evidence only if it serves the content.
- Avoid: AI-purple/blue gradient blobs, generic glass cards, same layout every beat, decorative assets without evidence value.

## GeekNews HyperFrames Smoke Recipe

Use the user-provided GeekNews summary as the source. A source URL is not required for this smoke test if the prompt already included the article summary.

Target:

- Duration: 10-15 seconds.
- Aspect: 16:9 landscape.
- Tone: premium tech briefing.
- Output: local MP4 plus frame/snapshot evidence.

Beats:

1. Title: "HyperFrames" and "HTML로 만드는 AI-agent video".
2. Difference: plain `index.html` authoring instead of React/TSX.
3. Workflow: agent writes HTML/CSS/GSAP, then lint, preview, render.
4. Value: deterministic MP4, Apache 2.0, commercially permissive.

Source attribution should be small footer text, visible but not dominant.

## Verification Gates

All gates must pass before calling the HyperFrames route successful:

| Gate | Evidence |
| ---- | -------- |
| Environment | `hyperframes doctor` output; Docker failure is non-blocking for local non-Docker render |
| Composition | edited `index.html` or composition files, not untouched scaffold |
| Lint/inspect | `hyperframes lint`, plus `inspect` or equivalent frame checks |
| Render | MP4 created by `hyperframes render` |
| Artifact | `ffprobe` duration, codec, and resolution evidence |
| Visual QA | representative frames are nonblank, readable, unclipped, and match the selected style |

If render fails, keep Remotion unaffected and document the exact failure in devlog. Do not silently fall back to a different engine.
