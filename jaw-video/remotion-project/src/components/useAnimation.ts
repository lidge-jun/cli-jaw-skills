import {
  spring,
  interpolate,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";
import type { AnimationConfig } from "../timeline/schema";

type AnimationResult = {
  opacity: number;
  transform: string;
};

export function useEntranceAnimation(
  config?: AnimationConfig,
  delay: number = 0,
): AnimationResult {
  const frame = useCurrentFrame();
  const { fps, durationInFrames } = useVideoConfig();

  const enter = config?.enter ?? "slide-up";
  const exit = config?.exit ?? "fade-out";

  // Entrance
  const springConfig = getSpringConfig(enter);
  const enterProgress = spring({
    frame: Math.max(0, frame - delay),
    fps,
    config: springConfig,
  });

  // Exit fade
  const exitStart = durationInFrames - 12;
  const exitProgress =
    exit === "none"
      ? 1
      : interpolate(frame, [exitStart, durationInFrames], [1, 0], {
          extrapolateLeft: "clamp",
          extrapolateRight: "clamp",
        });

  const enterTransform = getEnterTransform(enter, enterProgress);
  const exitTransform = getExitTransform(exit, 1 - exitProgress);

  return {
    opacity: enterProgress * exitProgress,
    transform: `${enterTransform} ${exitTransform}`.trim(),
  };
}

function getSpringConfig(enter: string) {
  switch (enter) {
    case "scale-in":
      return { damping: 12, stiffness: 200, mass: 0.8 };
    case "fade-in":
      return { damping: 200, mass: 1 };
    case "slide-up":
    default:
      return { damping: 80, mass: 0.9 };
  }
}

function getEnterTransform(enter: string, progress: number): string {
  switch (enter) {
    case "scale-in": {
      const s = interpolate(progress, [0, 1], [0.8, 1]);
      return `scale(${s})`;
    }
    case "fade-in":
      return "";
    case "slide-up":
    default: {
      const y = interpolate(progress, [0, 1], [40, 0]);
      return `translateY(${y}px)`;
    }
    case "none":
      return "";
  }
}

function getExitTransform(
  exit: string | undefined,
  progress: number,
): string {
  if (!exit || exit === "none") return "";
  switch (exit) {
    case "scale-out": {
      const s = interpolate(progress, [0, 1], [1, 0.9]);
      return `scale(${s})`;
    }
    case "slide-down": {
      const y = interpolate(progress, [0, 1], [0, 30]);
      return `translateY(${y}px)`;
    }
    case "fade-out":
    default:
      return "";
  }
}
