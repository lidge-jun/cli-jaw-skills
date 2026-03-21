---
name: fal-image-edit
description: Edit images using AI on fal.ai. Style transfer, object removal, background changes, and more. Use when the user requests "Edit image", "Remove object", "Change background", "Apply style", or similar image editing tasks.
metadata:
  author: fal-ai
  version: "1.0.0"
---

# fal.ai Image Edit

Edit images using AI: style transfer, object removal, background changes, and more.

## Models

| Model | Best For |
|-------|----------|
| `fal-ai/nano-banana-pro` | General editing and T2I (recommended default) |
| `fal-ai/flux-kontext` | Background change, context-aware editing |
| `fal-ai/flux/dev/image-to-image` | Style transfer (strength 0.3–0.5 subtle, 0.7–0.9 dramatic) |
| `fal-ai/bria/fibo-edit` | Object removal (works without masks) |
| `fal-ai/flux/dev/inpainting` | Masked inpainting (requires binary mask: white = edit area) |

## CLI Usage

```bash
bash /mnt/skills/user/fal-image-edit/scripts/edit-image.sh [options]
```

| Argument | Description |
|----------|-------------|
| `--image-url` | URL of image to edit (required) |
| `--prompt` | Description of desired edit (required) |
| `--operation` | `style`, `remove`, `background`, `inpaint` (default: `style`) |
| `--mask-url` | Mask image URL (required for inpainting) |
| `--strength` | Edit strength 0.0–1.0 (default: 0.75) |

Examples:

```bash
# Style transfer
bash /mnt/skills/user/fal-image-edit/scripts/edit-image.sh \
  --image-url "https://example.com/photo.jpg" \
  --prompt "Convert to anime style" \
  --operation style

# Remove object
bash /mnt/skills/user/fal-image-edit/scripts/edit-image.sh \
  --image-url "https://example.com/photo.jpg" \
  --prompt "Remove the person on the left" \
  --operation remove

# Change background
bash /mnt/skills/user/fal-image-edit/scripts/edit-image.sh \
  --image-url "https://example.com/portrait.jpg" \
  --prompt "Place in a tropical beach setting" \
  --operation background

# Inpainting with mask
bash /mnt/skills/user/fal-image-edit/scripts/edit-image.sh \
  --image-url "https://example.com/photo.jpg" \
  --mask-url "https://example.com/mask.png" \
  --prompt "Fill with flowers" \
  --operation inpaint
```

## MCP Tool Alternative

### General Edit (Recommended)
```javascript
mcp__fal-ai__generate({
  modelId: "fal-ai/nano-banana-pro",
  input: {
    image_url: "https://example.com/photo.jpg",
    prompt: "Make the sky more dramatic with sunset colors"
  }
})
```

### Style Transfer
```javascript
mcp__fal-ai__generate({
  modelId: "fal-ai/flux/dev/image-to-image",
  input: {
    image_url: "https://example.com/photo.jpg",
    prompt: "Convert to anime style",
    strength: 0.75
  }
})
```

### Object Removal
```javascript
mcp__fal-ai__generate({
  modelId: "bria/fibo-edit",
  input: {
    image_url: "https://example.com/photo.jpg",
    prompt: "Remove the person on the left"
  }
})
```

### Background Change
```javascript
mcp__fal-ai__generate({
  modelId: "fal-ai/flux-kontext",
  input: {
    image_url: "https://example.com/portrait.jpg",
    prompt: "Place the subject in a tropical beach setting"
  }
})
```

### Inpainting
```javascript
mcp__fal-ai__generate({
  modelId: "fal-ai/flux/dev/inpainting",
  input: {
    image_url: "https://example.com/photo.jpg",
    mask_url: "https://example.com/mask.png",
    prompt: "Fill with flowers"
  }
})
```

## Mask Tips

- White pixels = areas to edit, black pixels = areas to preserve
- Use PNG format
- Feathered edges create smoother transitions

## Tuning

- Edit too subtle → increase `--strength` (e.g., 0.85)
- Edit too dramatic → decrease `--strength` (e.g., 0.3)
- Object not fully removed → be more specific in prompt, or use inpainting with explicit mask
- Background artifacts → use FLUX Kontext for better edge handling
