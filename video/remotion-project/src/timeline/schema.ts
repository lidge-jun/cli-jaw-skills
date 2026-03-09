/**
 * Timeline JSON schema types + manual validation.
 * No zod dependency — manual type guards only.
 */

export type PresetKey = "Landscape-720p" | "Landscape-1080p" | "Portrait-1080p" | "Square-1080p";

export interface Timeline {
  meta: TimelineMeta;
  elements: TimelineElement[];
  audio: TimelineAudio[];
}

export interface TimelineMeta {
  title: string;
  description?: string;
  preset: PresetKey;
  fps?: number;
  totalDurationSec?: number;
  ttsVoice?: string;
  ttsProvider?: "gemini" | "supertone" | "supertonic";
  ttsSpeed?: number;
  theme?: {
    aesthetic?: string;
    font?: { display?: string; body?: string; code?: string };
    color?: { bg?: string; surface?: string; accent?: string; text?: string; textMuted?: string };
    gradient?: { hero?: string; slide?: string; glow?: string };
    card?: { background?: string; border?: string; shadow?: string; blur?: number; borderRadius?: number };
  };
  captions?: {
    src: string;
    style?: "bottom-center" | "bottom-left" | "top-center";
    fontSize?: number;
    fontFamily?: string;
    backgroundColor?: string;
  };
  audioVisualizer?: {
    enabled: boolean;
    style?: "bars" | "waveform";
    position?: "bottom" | "top";
    height?: number;
    color?: string;
  };
}

export type ElementType =
  | "title"
  | "content"
  | "code"
  | "diagram"
  | "image"
  | "stat"
  | "quote"
  | "comparison"
  | "video"
  | "gif"
  | "lottie"
  | "chart";

export interface TimelineElement {
  id?: string;
  type: ElementType;
  startSec?: number;
  durationSec: number;
  props: Record<string, unknown>;
  transition?: TransitionConfig;
  animation?: AnimationConfig;
  narration?: string;
  voiceControl?: VoiceControl;
}

export interface VoiceControl {
  voice?: string;
  tonePrompt?: string;
  style?: string;
  pitch?: number;
  pitchVariance?: number;
  speed?: number;
}

export interface TransitionConfig {
  type: "fade" | "slide" | "wipe" | "flip" | "clock-wipe" | "none";
  direction?: "from-left" | "from-right" | "from-top" | "from-bottom";
  durationSec?: number;
  timing?: "linear" | "spring";
}

export interface AnimationConfig {
  enter: "fade-in" | "slide-up" | "scale-in" | "none";
  exit?: "fade-out" | "slide-down" | "scale-out" | "none";
  staggerItems?: boolean;
  staggerDelaySec?: number;
}

export interface TimelineAudio {
  type: "tts" | "music" | "sfx" | "user";
  src: string;
  startSec?: number;
  durationSec?: number;
  volume?: number;
  elementId?: string;
  loop?: boolean;
  fadeInSec?: number;
  fadeOutSec?: number;
  trimStartSec?: number;
}

export interface StatProps {
  stats: Array<{
    value: number;
    prefix?: string;
    suffix?: string;
    decimals?: number;
    label: string;
    trend?: "up" | "down" | "neutral";
  }>;
  title?: string;
}

export interface QuoteProps {
  quote: string;
  author?: string;
  source?: string;
}

export interface ComparisonProps {
  title?: string;
  left: { label: string; items: string[]; accent?: string };
  right: { label: string; items: string[]; accent?: string };
}

export interface ChartProps {
  chartType: "bar" | "pie" | "line";
  data: {
    labels: string[];
    datasets: Array<{
      label: string;
      data: number[];
      color?: string;
    }>;
  };
  title?: string;
  showLegend?: boolean;
}

export interface TimelineElement {
  id?: string;
  type: ElementType;
  startSec?: number;
  durationSec: number;
  props: Record<string, unknown>;
  transition?: TransitionConfig;
  animation?: AnimationConfig;
  narration?: string;
  voiceControl?: VoiceControl;
}

export interface VoiceControl {
  voice?: string;
  tonePrompt?: string;
  style?: string;
  pitch?: number;
  pitchVariance?: number;
  speed?: number;
}

const VALID_PRESETS: PresetKey[] = ["Landscape-720p", "Landscape-1080p", "Portrait-1080p", "Square-1080p"];
const VALID_ELEMENT_TYPES: ElementType[] = [
  "title", "content", "code", "diagram", "image",
  "stat", "quote", "comparison",
  "video", "gif", "lottie", "chart",
];

export function validateTimeline(data: unknown): { valid: boolean; errors: string[]; timeline?: Timeline } {
  const errors: string[] = [];
  if (!data || typeof data !== "object") {
    return { valid: false, errors: ["Root must be an object"] };
  }

  const obj = data as Record<string, unknown>;

  // meta
  if (!obj.meta || typeof obj.meta !== "object") {
    errors.push("Missing or invalid 'meta'");
  } else {
    const meta = obj.meta as Record<string, unknown>;
    if (typeof meta.title !== "string") errors.push("meta.title must be a string");
    if (!VALID_PRESETS.includes(meta.preset as PresetKey)) {
      errors.push(`meta.preset must be one of: ${VALID_PRESETS.join(", ")}`);
    }
    // totalDurationSec is now auto-calculated, so allow missing
    if (meta.totalDurationSec !== undefined && (typeof meta.totalDurationSec !== "number" || meta.totalDurationSec <= 0)) {
      errors.push("meta.totalDurationSec must be a positive number if provided");
    }
  }

  // elements
  if (!Array.isArray(obj.elements)) {
    errors.push("Missing or invalid 'elements' array");
  } else {
    for (let i = 0; i < obj.elements.length; i++) {
      const el = obj.elements[i] as Record<string, unknown>;
      if (!VALID_ELEMENT_TYPES.includes(el.type as ElementType)) {
        errors.push(`elements[${i}].type must be one of: ${VALID_ELEMENT_TYPES.join(", ")}`);
      }
      if (typeof el.durationSec !== "number" || el.durationSec <= 0) {
        errors.push(`elements[${i}].durationSec must be a positive number`);
      }
      if (!el.props || typeof el.props !== "object") {
        errors.push(`elements[${i}].props must be an object`);
      }
    }
  }

  // audio (optional array)
  if (obj.audio !== undefined && !Array.isArray(obj.audio)) {
    errors.push("'audio' must be an array if provided");
  }

  if (errors.length > 0) return { valid: false, errors };
  return { valid: true, errors: [], timeline: data as Timeline };
}

/**
 * Compute actual start times accounting for transition overlaps.
 * Returns per-element audioStartSec and total composition duration.
 */
export function computeTiming(elements: TimelineElement[]): {
  audioStartSec: number[];
  totalDurationSec: number;
} {
  const starts: number[] = [];
  let cursor = 0;

  for (let i = 0; i < elements.length; i++) {
    const transitionBefore = i > 0
      ? (elements[i].transition?.durationSec ?? 0.5)
      : 0;
    starts.push(cursor);
    cursor += elements[i].durationSec - (i < elements.length - 1
      ? (elements[i + 1]?.transition?.durationSec ?? 0.5)
      : 0);
  }

  // Total = sum of durations - sum of transition overlaps
  let total = 0;
  for (const el of elements) {
    total += el.durationSec;
  }
  for (let i = 1; i < elements.length; i++) {
    total -= (elements[i].transition?.durationSec ?? 0.5);
  }

  return { audioStartSec: starts, totalDurationSec: Math.max(total, 0) };
}
