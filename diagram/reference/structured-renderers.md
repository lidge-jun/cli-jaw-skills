# Native Web UI Structured Renderer Boundary

Canonical schemas for `search-results`, `compose-block`, `dataframe`, `chart-json`, and `diff` now live in the dedicated `structured-renderers` skill:

Load `structured-renderers/SKILL.md` from the active skill root.

Diagram keeps only the visualization boundary:

- Use `chart-json` through `structured-renderers` for simple single-series bar, line, and pie charts.
- Use `diagram-html` through `diagram` for maps, multi-series charts, advanced chart types, custom JavaScript, external libraries, or richer interaction.
- Use `structured-renderers` for non-chart native cards: source/result lists, editable drafts, dataframes, and diffs.
