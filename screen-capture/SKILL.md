---
name: screen-capture
description: "Screen capture and camera snapshots using macOS built-in tools. Full screen, region, window, webcam, and video recording. Use as default when tool-specific capture (Figma, Playwright, CDP) is unavailable. Prefer cli-jaw browser screenshot for web pages."
metadata:
  {
    "openclaw":
      {
        "emoji": "📸",
        "requires": null,
        "install":
          [
            {
              "id": "brew-imagesnap",
              "kind": "brew",
              "formula": "imagesnap",
              "bins": ["imagesnap"],
              "label": "Install imagesnap (optional, for webcam capture)",
            },
          ],
      },
  }
---

# Screen Capture (macOS)

## Quick Start

```bash
screencapture -x ~/screenshot.png          # Full screen (silent)
screencapture -i ~/selection.png           # Interactive region select
screencapture -c                            # Capture to clipboard
```

## Commands

### Full Screen

```bash
screencapture -x ~/screenshot.png                    # Silent full screen
screencapture ~/screenshot.png                       # Full screen with shutter sound
screencapture -T 3 ~/screenshot.png                  # 3-second delay
```

### Region / Window

```bash
screencapture -i ~/region.png                        # Interactive: drag to select region
screencapture -iW ~/window.png                       # Interactive: click to select window
screencapture -R 0,0,1280,720 ~/region.png           # Specific coordinates (x,y,w,h)
```

### Specific Application Window

```bash
# Capture Chrome window by window ID
screencapture -l$(osascript -e 'tell app "Google Chrome" to id of window 1') ~/chrome.png

# Capture any app window
screencapture -l$(osascript -e 'tell app "Safari" to id of window 1') ~/safari.png

# Capture frontmost window
screencapture -l$(osascript -e 'tell app "System Events" to id of first window of (first process whose frontmost is true)') ~/front.png
```

### Clipboard

```bash
screencapture -c                                     # Full screen to clipboard
screencapture -ic                                    # Region select to clipboard
```

### Multiple Displays

```bash
screencapture ~/screen1.png ~/screen2.png            # One file per display
screencapture -D 1 ~/main.png                        # Main display only
screencapture -D 2 ~/secondary.png                   # Secondary display
```

### Video Recording

```bash
screencapture -v ~/recording.mov                     # Record screen video
screencapture -V 10 ~/recording.mov                  # Record 10 seconds
```

## Webcam Capture (requires imagesnap)

```bash
# Install
brew install imagesnap

# Capture
imagesnap ~/camera.png                               # Take photo
imagesnap -w 2 ~/camera.png                          # 2-second warmup (better quality)
imagesnap -d "FaceTime HD Camera" ~/camera.png       # Specific camera

# List cameras
imagesnap -l
```

## Output Formats

```bash
screencapture -t png ~/screenshot.png                # PNG (default)
screencapture -t jpg ~/screenshot.jpg                # JPEG
screencapture -t pdf ~/screenshot.pdf                # PDF
screencapture -t tiff ~/screenshot.tiff              # TIFF
```

## Common Workflows

### Capture Specific App State

```bash
# Bring app to front, then capture
osascript -e 'tell app "Finder" to activate'
sleep 0.5
screencapture -x ~/finder.png
```

## Useful Flags

| Flag            | Description                      |
| --------------- | -------------------------------- |
| `-x`            | Silent (no shutter sound)        |
| `-i`            | Interactive selection mode       |
| `-c`            | Copy to clipboard                |
| `-R x,y,w,h`    | Capture specific rectangle       |
| `-T seconds`    | Delay before capture             |
| `-t format`     | Output format (png/jpg/pdf/tiff) |
| `-l windowID`   | Capture specific window          |
| `-D displayNum` | Capture specific display         |
| `-v`            | Record video                     |
| `-V seconds`    | Record video for N seconds       |

## Notes

- Screen Recording permission may be required (System Settings > Privacy > Screen Recording).
- For browser-specific screenshots, prefer `cli-jaw browser screenshot` (captures via CDP).
