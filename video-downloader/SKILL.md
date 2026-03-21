---
name: video-downloader
description: Download videos using yt-dlp. Supports quality selection, format conversion, and audio extraction.
---

# Video Downloader

Download videos via `yt-dlp` with quality, format, and audio-only options.

## Goal

Download a video (or extract audio) from a URL to a local directory.

## Instructions

Run `scripts/download_video.py` with the target URL. The script wraps `yt-dlp` and installs it automatically if missing.

```bash
python scripts/download_video.py "<URL>" [options]
```

## CLI Reference

| Flag | Values | Default | Effect |
|------|--------|---------|--------|
| `-q` / `--quality` | `best`, `1080p`, `720p`, `480p`, `360p`, `worst` | `best` | Video resolution cap |
| `-f` / `--format` | `mp4`, `webm`, `mkv` | `mp4` | Container format (video only) |
| `-a` / `--audio-only` | flag | off | Extract audio as MP3 |
| `-o` / `--output` | path | `/mnt/user-data/outputs/` | Output directory |

## Constraints

- Single videos only — playlists are skipped by default
- Filename is derived from the video title (not configurable)
- Requires network access and a URL supported by yt-dlp
- Audio extraction (`-a`) always outputs MP3 regardless of `-f`