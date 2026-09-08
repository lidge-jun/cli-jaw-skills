/**
 * Video resolution presets.
 * Source: jhartquist/claude-remotion-kickstart
 */
export const PRESETS = {
  'Landscape-720p': { width: 1280, height: 720, fps: 30 },
  'Landscape-1080p': { width: 1920, height: 1080, fps: 30 },
  'Portrait-1080p': { width: 1080, height: 1920, fps: 30 },
  'Square-1080p': { width: 1080, height: 1080, fps: 30 },
};

export function getPreset(key) {
  if (key && key in PRESETS) return PRESETS[key];
  return PRESETS['Landscape-1080p'];
}
