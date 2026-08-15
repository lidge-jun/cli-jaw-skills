#!/usr/bin/env node
/**
 * Gate 3: Artifact validation via ffprobe.
 * Checks duration > 0, codec, resolution, file size.
 */
import { execFileSync } from "node:child_process";
import { statSync } from "node:fs";
import { getPreset } from "./presets.mjs";

export function validateVideoArtifact(mp4Path, preset) {
  const errors = [];
  let duration = 0, codec = "", width = 0, height = 0, fileSize = 0;

  try {
    fileSize = statSync(mp4Path).size;
  } catch {
    return { valid: false, duration, codec, width, height, fileSize, errors: [`File not found: ${mp4Path}`] };
  }

  if (fileSize === 0) {
    return { valid: false, duration, codec, width, height, fileSize, errors: ["File is empty (0 bytes)"] };
  }

  try {
    const raw = execFileSync("ffprobe", [
      "-v", "quiet",
      "-print_format", "json",
      "-show_format",
      "-show_streams",
      mp4Path,
    ], { encoding: "utf8" });

    const probe = JSON.parse(raw);
    const videoStream = probe.streams?.find(s => s.codec_type === "video");

    if (!videoStream) {
      errors.push("No video stream found");
    } else {
      codec = videoStream.codec_name || "";
      width = parseInt(videoStream.width, 10) || 0;
      height = parseInt(videoStream.height, 10) || 0;
    }

    duration = parseFloat(probe.format?.duration || "0");
    if (duration <= 0) errors.push("Duration <= 0");
    if (codec !== "h264") errors.push(`Expected codec h264, got ${codec}`);
    if (preset) {
      if (width !== preset.width) errors.push(`Expected width ${preset.width}, got ${width}`);
      if (height !== preset.height) errors.push(`Expected height ${preset.height}, got ${height}`);
    }
  } catch (e) {
    errors.push(`ffprobe failed: ${e.message}`);
  }

  return { valid: errors.length === 0, duration, codec, width, height, fileSize, errors };
}

// CLI entrypoint
if (process.argv[1] && process.argv[1].endsWith("validate-artifact.mjs")) {
  const mp4Path = process.argv[2];
  const presetKey = process.argv.find(a => a.startsWith("--preset="))?.split("=")[1]
    || process.argv[process.argv.indexOf("--preset") + 1];

  if (!mp4Path) {
    console.error("Usage: node validate-artifact.mjs <mp4-path> [--preset Landscape-1080p]");
    process.exit(1);
  }

  const preset = presetKey ? getPreset(presetKey) : undefined;
  const result = validateVideoArtifact(mp4Path, preset);
  console.log(JSON.stringify(result, null, 2));
  process.exit(result.valid ? 0 : 1);
}
