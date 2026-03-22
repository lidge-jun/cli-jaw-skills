---
name: fal-image-edit
description: "AI media via fal.ai — image editing, image/video/audio generation. Triggers: edit image, remove object, change background, apply style, generate image, create video, text to speech, make thumbnail."
metadata:
  author: fal-ai
  version: "1.1.0"
---

# fal.ai Media

Image editing, image generation, video generation, and audio generation via fal.ai MCP.

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

---

## Image Generation (Text-to-Image)

### Nano Banana 2 (Fast)
Best for: quick iterations, drafts, prompt exploration.

```javascript
mcp__fal-ai__generate({
  modelId: "fal-ai/nano-banana-2",
  input: {
    prompt: "a futuristic cityscape at sunset, cyberpunk style",
    image_size: "landscape_16_9",
    num_images: 1,
    seed: 42
  }
})
```

### Nano Banana Pro (High Fidelity)
Best for: production images, realism, typography, detailed prompts.

```javascript
mcp__fal-ai__generate({
  modelId: "fal-ai/nano-banana-pro",
  input: {
    prompt: "professional product photo of wireless headphones on marble surface, studio lighting",
    image_size: "square",
    num_images: 1,
    guidance_scale: 7.5
  }
})
```

### Generation Parameters

| Param | Type | Options | Notes |
|-------|------|---------|-------|
| `prompt` | string | required | Describe what you want |
| `image_size` | string | `square`, `portrait_4_3`, `landscape_16_9`, `portrait_16_9`, `landscape_4_3` | Aspect ratio |
| `num_images` | number | 1-4 | How many to generate |
| `seed` | number | any integer | Reproducibility |
| `guidance_scale` | number | 1-20 | Higher = more literal prompt following |

---

## Video Generation

### Seedance 1.0 Pro (ByteDance)
Best for: text-to-video, image-to-video with high motion quality.

```javascript
mcp__fal-ai__generate({
  modelId: "fal-ai/seedance-1-0-pro",
  input: {
    prompt: "a drone flyover of a mountain lake at golden hour, cinematic",
    duration: "5s",
    aspect_ratio: "16:9",
    seed: 42
  }
})
```

### Kling Video v3 Pro
Best for: text/image-to-video with native audio generation.

```javascript
mcp__fal-ai__generate({
  modelId: "fal-ai/kling-video/v3/pro",
  input: {
    prompt: "ocean waves crashing on a rocky coast, dramatic clouds",
    duration: "5s",
    aspect_ratio: "16:9"
  }
})
```

### Veo 3 (Google DeepMind)
Best for: video with generated sound, high visual quality.

```javascript
mcp__fal-ai__generate({
  modelId: "fal-ai/veo-3",
  input: {
    prompt: "a bustling Tokyo street market at night, neon signs, crowd noise",
    aspect_ratio: "16:9"
  }
})
```

### Image-to-Video
Start from an existing image for more controlled results:

```javascript
mcp__fal-ai__generate({
  modelId: "fal-ai/seedance-1-0-pro",
  input: {
    prompt: "camera slowly zooms out, gentle wind moves the trees",
    image_url: "<uploaded_image_url>",
    duration: "5s"
  }
})
```

### Video Parameters

| Param | Type | Options | Notes |
|-------|------|---------|-------|
| `prompt` | string | required | Describe the video (focus on motion and scene) |
| `duration` | string | `"5s"`, `"10s"` | Video length |
| `aspect_ratio` | string | `"16:9"`, `"9:16"`, `"1:1"` | Frame ratio |
| `seed` | number | any integer | Reproducibility |
| `image_url` | string | URL | Source image for image-to-video |

---

## Audio Generation

### CSM-1B (Conversational Speech)
Text-to-speech with natural, conversational quality.

```javascript
mcp__fal-ai__generate({
  modelId: "fal-ai/csm-1b",
  input: { text: "Hello, welcome to the demo.", speaker_id: 0 }
})
```

### ThinkSound (Video-to-Audio)
Generate matching audio/SFX from video content.

```javascript
mcp__fal-ai__generate({
  modelId: "fal-ai/thinksound",
  input: {
    video_url: "<video_url>",
    prompt: "ambient forest sounds with birds chirping"
  }
})
```

---

## Cost Estimation

Check estimated cost before expensive generations:

```javascript
mcp__fal-ai__estimate_cost({
  estimate_type: "unit_price",
  endpoints: { "fal-ai/nano-banana-pro": { unit_quantity: 1 } }
})
```

## Model Discovery

```javascript
mcp__fal-ai__search({ query: "text to video" })
mcp__fal-ai__find({ endpoint_ids: ["fal-ai/seedance-1-0-pro"] })
mcp__fal-ai__models()
```

## Tips

- Use `seed` for reproducible results when iterating on prompts
- Start with lower-cost models (Nano Banana 2) for prompt exploration, then switch to Pro for finals
- For video, keep prompts concise — focus on motion and scene description
- Image-to-video produces more controlled results than pure text-to-video
- Check `estimate_cost` before running expensive video generations
