---
name: tts
description: "Text-to-speech with edge-tts (primary, high-quality neural voices) and macOS say (fallback). Supports Korean, English, Japanese, and 40+ languages. Includes Telegram voice delivery workflow."
metadata:
  {
    "openclaw":
      {
        "emoji": "🔊",
        "requires": "edge-tts (pip), ffmpeg (brew)",
        "install": "pip install edge-tts && brew install ffmpeg",
      },
  }
---

# Text-to-Speech

## Tool Priority

| Tool | Quality | Languages | File Output | Use When |
|------|---------|-----------|-------------|----------|
| **edge-tts** (primary) | Neural, natural | 40+ | Fast, reliable | Default for all TTS tasks |
| **macOS say** (fallback) | Robotic | ~30 | ⚠️ Hangs on Korean | English-only speaker output |

> ⚠️ macOS `say -o` hangs indefinitely for Korean text. Always use edge-tts for Korean file output.

## Quick Start (edge-tts)

### Install

```bash
pip install edge-tts  # In your project venv
brew install ffmpeg   # For format conversion
```

### Generate Voice File

Write a Python script (heredoc/inline causes encoding issues with non-ASCII text):

```python
# /tmp/tts_gen.py
import asyncio, edge_tts

async def main():
    text = "Hello! This is a test voice message from Jaw agent."
    voice = "en-US-JennyNeural"  # or "ko-KR-SunHiNeural" for Korean
    comm = edge_tts.Communicate(text, voice)
    await comm.save("/tmp/voice.mp3")

asyncio.run(main())
```

```bash
python3 /tmp/tts_gen.py
```

### Send to Telegram as Voice Message

```bash
# Convert to OGG Opus (Telegram voice format)
ffmpeg -y -i /tmp/voice.mp3 -c:a libopus /tmp/voice.ogg

# Send via Bot API (use python requests — curl multipart may hang)
python3 /tmp/tg_voice.py
```

```python
# /tmp/tg_voice.py
import json, requests

with open("/Users/junny/.cli-jaw/settings.json") as f:
    s = json.load(f)
token = s["telegram"]["token"]
chat_id = s["telegram"]["allowedChatIds"][-1]

with open("/tmp/voice.ogg", "rb") as f:
    r = requests.post(
        f"https://api.telegram.org/bot{token}/sendVoice",
        data={"chat_id": chat_id, "caption": "Voice message"},
        files={"voice": f}
    )
print(r.status_code, r.json().get("ok"))
```

## Available Voices

### Korean (Recommended)

| Voice | Gender | Style |
|-------|--------|-------|
| `ko-KR-SunHiNeural` | Female | Friendly, natural |
| `ko-KR-InJoonNeural` | Male | Friendly, natural |
| `ko-KR-HyunsuMultilingualNeural` | Male | Multilingual capable |

### English

| Voice | Gender | Style |
|-------|--------|-------|
| `en-US-JennyNeural` | Female | Natural, conversational |
| `en-US-GuyNeural` | Male | Natural, conversational |
| `en-US-AriaNeural` | Female | Professional |
| `en-GB-SoniaNeural` | Female | British |

### Japanese

| Voice | Gender |
|-------|--------|
| `ja-JP-NanamiNeural` | Female |
| `ja-JP-KeitaNeural` | Male |

### List All Voices

```bash
edge-tts --list-voices                    # All voices
edge-tts --list-voices | grep ko-KR      # Korean only
edge-tts --list-voices | grep en-US      # US English only
```

## Advanced Options

### Speed and Pitch Control

```python
comm = edge_tts.Communicate(
    text,
    "ko-KR-SunHiNeural",
    rate="+20%",     # Speed: -50% to +100%
    pitch="+5Hz",    # Pitch adjustment
    volume="+0%"     # Volume adjustment
)
```

### SSML for Fine Control

```python
ssml = """
<speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis" xml:lang="en-US">
  <voice name="en-US-JennyNeural">
    <prosody rate="medium" pitch="medium">
      Hello there. <break time="500ms"/> Pausing briefly before continuing.
    </prosody>
  </voice>
</speak>
"""
```

### Batch Generation

```python
import asyncio, edge_tts

async def generate(text, output, voice="en-US-JennyNeural"):
    comm = edge_tts.Communicate(text, voice)
    await comm.save(output)

async def main():
    tasks = [
        generate("First message", "/tmp/msg1.mp3"),
        generate("Second message", "/tmp/msg2.mp3"),
        generate("Third in Korean", "/tmp/msg3.mp3", "ko-KR-SunHiNeural"),
    ]
    await asyncio.gather(*tasks)

asyncio.run(main())
```

## macOS `say` (Fallback — English Only)

```bash
say "Hello world"                          # Speak through speakers
say -v Samantha "Hello world"              # Specific voice
say -r 200 "Fast speech"                   # Speed control
say -o /tmp/out.aiff "Hello world"         # Save to file (English OK)
say -v '?' | grep en_                      # List English voices
```

> ⚠️ Do NOT use `say -o` with Korean/CJK text — it hangs indefinitely on macOS.

## Troubleshooting

| Problem | Solution |
|---------|----------|
| `edge-tts` not found | `pip install edge-tts` in active venv |
| Korean `say -o` hangs | Use edge-tts instead |
| Telegram curl hangs | Use python `requests` instead |
| OGG conversion fails | `brew install ffmpeg` |
| Inline Python encoding error | Write to .py file first, then `python3 file.py` |

## Complete Workflow Example

```bash
# 1. Generate voice
python3 /tmp/tts_gen.py

# 2. Convert for Telegram
ffmpeg -y -i /tmp/voice.mp3 -c:a libopus /tmp/voice.ogg

# 3. Send to Telegram
python3 /tmp/tg_voice.py

# 4. Cleanup
rm /tmp/tts_gen.py /tmp/tg_voice.py /tmp/voice.mp3 /tmp/voice.ogg
```
