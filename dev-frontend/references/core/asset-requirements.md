# Asset Requirements

Visual surfaces need real visual evidence. Abstract backgrounds, blobs, and generic icons are not enough when users need to understand a product, place, object, workflow, game, or state.

## Asset Decision Table

| Surface | Required Asset Type |
| --- | --- |
| Product / object / venue / person page | real or generated bitmap showing the subject |
| Marketing / landing page | concrete product, scene, screenshot, or generated hero image |
| Dashboard / tool | real state preview, chart, table, workflow screenshot, or diagram |
| AI tool | process state, provenance, result preview, permission boundary, or diagram |
| Education / kids / community | illustration, character, or guided visual allowed |
| Fintech / gov / B2B | restrained screenshot, data view, trust visual, or high-polish semantic 3D |
| Game | game assets mandatory |
| Documentation | screenshots or diagrams when they clarify a task |

## What Does Not Count

- abstract gradient mesh
- decorative blob/orb
- generic icon row
- fake dashboard with random numbers
- low-polish AI image
- stock photo unrelated to the task
- public 3D icon pack used without brand adaptation

## Rules

- Use the repo's existing asset system first.
- If no asset exists and the surface needs one, generate a bitmap asset or create a real diagram/chart.
- For external or generated assets, record provenance/licensing in the dev note, PR description, or project asset manifest when one exists.
- Make the first viewport identify the product/place/object when relevant.
- Do not obscure text or primary actions with visuals.
- Verify assets render on mobile and desktop.
- Verify intrinsic dimensions, aspect ratio, crop, alt text, and loading behavior.
- Optimize heavy media; do not ship huge 3D/video assets without a reason.
