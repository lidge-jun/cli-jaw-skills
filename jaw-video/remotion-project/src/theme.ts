import { FONTS } from "./fonts";

export interface Theme {
  font: { display: string; body: string; code: string };
  color: { bg: string; surface: string; accent: string; text: string; textMuted: string };
  gradient: { hero: string; slide: string; glow: string };
  card: {
    background: string;
    border: string;
    shadow: string;
    blur: number;
    borderRadius: number;
  };
}

export const DEFAULT_THEME: Theme = {
  font: {
    display: FONTS.display,
    body: FONTS.body,
    code: FONTS.code,
  },
  color: {
    bg: "#0B1120",
    surface: "rgba(34,211,238,0.06)",
    accent: "#22D3EE",
    text: "#E2E8F0",
    textMuted: "#94A3B8",
  },
  gradient: {
    hero: "radial-gradient(ellipse at 30% 50%, rgba(34,211,238,0.15) 0%, transparent 60%), linear-gradient(180deg, #0B1120 0%, #111827 100%)",
    slide: "linear-gradient(135deg, #0B1120 0%, #0F172A 40%, #1E293B 100%)",
    glow: "radial-gradient(circle at 50% 0%, rgba(34,211,238,0.12) 0%, transparent 50%)",
  },
  card: {
    background: "rgba(15, 23, 42, 0.65)",
    border: "rgba(34, 211, 238, 0.12)",
    shadow: "0 8px 32px rgba(0, 0, 0, 0.3)",
    blur: 12,
    borderRadius: 20,
  },
};

type DeepPartialTheme = {
  aesthetic?: string;
  font?: Partial<Theme["font"]>;
  color?: Partial<Theme["color"]>;
  gradient?: Partial<Theme["gradient"]>;
  card?: Partial<Theme["card"]>;
};

export function resolveTheme(meta?: { theme?: DeepPartialTheme }): Theme {
  if (!meta?.theme) return DEFAULT_THEME;

  const t = meta.theme;
  return {
    font: { ...DEFAULT_THEME.font, ...t.font },
    color: { ...DEFAULT_THEME.color, ...t.color },
    gradient: { ...DEFAULT_THEME.gradient, ...t.gradient },
    card: { ...DEFAULT_THEME.card, ...t.card },
  };
}
