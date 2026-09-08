export type PresetKey = keyof typeof PRESETS;

export const PRESETS = {
  "Landscape-720p": { width: 1280, height: 720, fps: 30 },
  "Landscape-1080p": { width: 1920, height: 1080, fps: 30 },
  "Portrait-1080p": { width: 1080, height: 1920, fps: 30 },
  "Square-1080p": { width: 1080, height: 1080, fps: 30 },
} as const;

export type VideoPreset = (typeof PRESETS)[PresetKey];

export function getPreset(key?: string): VideoPreset {
  if (key && key in PRESETS) return PRESETS[key as PresetKey];
  return PRESETS["Landscape-1080p"];
}
