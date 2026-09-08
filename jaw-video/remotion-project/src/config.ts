export const FEATURES = {
  CUSTOM_REACT_COMPOSITIONS: false,
} as const;

export function secondsToFrames(seconds: number, fps = 30): number {
  return Math.round(seconds * fps);
}

export function framesToSeconds(frames: number, fps = 30): number {
  return frames / fps;
}
