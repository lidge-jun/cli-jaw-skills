---
name: "figma-implement-design"
description: "Translate Figma nodes into production-ready code with 1:1 visual fidelity using the Figma MCP workflow (design context, screenshots, assets, and project-convention translation). Trigger when the user provides Figma URLs or node IDs, or asks to implement designs or components that must match Figma specs. Requires a working Figma MCP server connection."
---

# Implement Design

Translate Figma designs into production-ready code with pixel-perfect accuracy via the Figma MCP server. Supports read (design context, screenshots, assets) and write (create/update canvas nodes) workflows.

## Prerequisites

- Figma MCP server connected and accessible
- Figma URL in format `https://figma.com/design/:fileKey/:fileName?node-id=1-2`
  - Or with `figma-desktop` MCP: select a node directly in the Figma desktop app (no URL required)

## Setup (if MCP not configured)

1. `codex mcp add figma --url https://mcp.figma.com/mcp`
2. Set `[features].rmcp_client = true` in `config.toml` or run `codex --enable rmcp_client`
3. `codex mcp login figma`
4. Tell user to restart codex after login

## Upstream: Figma Make

If the design doesn't exist yet, use **Figma Make** (AI-powered design generation) as the upstream step:
1. Describe the desired UI to Figma Make to generate an initial design
2. Refine the generated design in Figma
3. Then follow the implementation workflow below to translate the finalized design into code

Figma Make produces structured Figma nodes — the same workflow below applies to Make-generated designs.

## Workflow

### Step 1: Get Node ID

**From URL**: Extract `:fileKey` (segment after `/design/`) and node ID (`node-id` query param).
- Example: `https://figma.com/design/kL9xQn2VwM8pYrTb4ZcHjF/DesignSystem?node-id=42-15`
  - fileKey: `kL9xQn2VwM8pYrTb4ZcHjF`, nodeId: `42-15`

**From desktop app** (`figma-desktop` MCP only): tools auto-use the currently selected node; `fileKey` is not needed.

### Step 2: Fetch Design Context

```
get_design_context(fileKey=":fileKey", nodeId="1-2")
```

Returns layout properties, typography, colors, component structure, spacing.

If response is truncated:
1. Run `get_metadata(fileKey, nodeId)` for the node map
2. Fetch individual child nodes with `get_design_context`

### Step 3: Capture Visual Reference

```
get_screenshot(fileKey=":fileKey", nodeId="1-2")
```

Keep this screenshot accessible throughout implementation — it's the source of truth.

### Step 4: Download Assets

Download images, icons, SVGs returned by the MCP server.
- Use `localhost` sources directly when provided
- Use assets from the Figma payload rather than importing new icon packages

### Step 4b: Extract Figma Variables as Design Tokens

Use Figma Variables (collections of color, spacing, typography, and sizing values) as the canonical design token source:
- Map Figma Variable collections to your project's token files (CSS custom properties, JSON, or platform-specific formats)
- Prefer Figma Variables over hardcoded values extracted from individual node properties
- Use the `get_design_context` response to identify which Variables are applied to each node

### Step 5: Translate to Project Conventions

- Treat Figma MCP output (typically React + Tailwind) as a design representation, not final code
- Replace Tailwind utilities with the project's design system tokens
- Reuse existing components (buttons, inputs, typography) instead of duplicating
- Respect existing routing, state management, and data-fetch patterns

### Step 6: Achieve Visual Parity

- Match the Figma design exactly; avoid hardcoded values — use design tokens
- When project tokens differ from Figma specs, prefer project tokens but adjust spacing/sizing to maintain visual fidelity
- Follow WCAG accessibility requirements

### Step 7: Validate

Compare final UI against the Figma screenshot:

- [ ] Layout matches (spacing, alignment, sizing)
- [ ] Typography matches (font, size, weight, line height)
- [ ] Colors match exactly
- [ ] Interactive states work (hover, active, disabled)
- [ ] Responsive behavior follows Figma constraints
- [ ] Assets render correctly
- [ ] Accessibility standards met

### Step 8: Write Back to Canvas (Optional)

The Figma MCP server supports **write-to-canvas** — creating or updating Figma nodes programmatically:
- Use `create_node` or `update_node` to push generated component variants back into Figma
- Useful for syncing implementation-driven changes (e.g., new states, responsive variants) back to design
- Coordinate with designers before writing to shared files

## Code Connect

Link production components to their Figma counterparts with **Code Connect**:
- Define `.figma.tsx` (React) or `.figma.swift` (SwiftUI) files mapping Figma components to code
- Designers see live code snippets in Figma's Dev Mode inspect panel
- Keeps implementation and design in sync as either side evolves

```tsx
// Button.figma.tsx
import figma from '@figma/code-connect'
import { Button } from './Button'

figma.connect(Button, 'https://figma.com/design/xyz/file?node-id=1-2', {
  props: {
    label: figma.string('Label'),
    variant: figma.enum('Variant', { Primary: 'primary', Secondary: 'secondary' }),
  },
  example: ({ label, variant }) => <Button variant={variant}>{label}</Button>,
})
```

## Implementation Rules

- Place components in the project's designated design system directory
- Extend existing components rather than creating new ones when a match exists
- Map Figma design tokens to project design tokens
- Extract hardcoded values to constants or design tokens
- Add TypeScript types for component props

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Figma output truncated | Use `get_metadata` for node structure, then fetch specific nodes |
| Design doesn't match | Compare side-by-side with screenshot; check spacing, colors, typography in design context data |
| Assets not loading | Verify MCP server's assets endpoint accessible; use `localhost` URLs directly |
| Token values differ from Figma | Prefer project tokens for consistency; adjust spacing/sizing for visual fidelity |

## Resources

- [Figma MCP Server Documentation](https://developers.figma.com/docs/figma-mcp-server/)
- [Figma MCP Tools and Prompts](https://developers.figma.com/docs/figma-mcp-server/tools-and-prompts/)
- [Figma Variables and Design Tokens](https://help.figma.com/hc/en-us/articles/15339657135383-Guide-to-variables-in-Figma)
