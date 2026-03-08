import { loadFont as loadChakraPetch } from "@remotion/google-fonts/ChakraPetch";
import { loadFont as loadOutfit } from "@remotion/google-fonts/Outfit";
import { loadFont as loadJetBrainsMono } from "@remotion/google-fonts/JetBrainsMono";

const { fontFamily: chakra } = loadChakraPetch("normal", { weights: ["400", "700"], subsets: ["latin"] });
const { fontFamily: outfit } = loadOutfit("normal", { weights: ["400", "700"], subsets: ["latin"] });
const { fontFamily: jetbrains } = loadJetBrainsMono("normal", { weights: ["400"], subsets: ["latin"] });

export interface Theme {
  font: { display: string; body: string; code: string };
  color: { bg: string; surface: string; accent: string; text: string; textMuted: string };
  gradient: { hero: string; slide: string; glow: string };
}

export const DEFAULT_THEME: Theme = {
  font: {
    display: `${chakra}, sans-serif`,
    body: `${outfit}, sans-serif`,
    code: `${jetbrains}, monospace`,
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
};

type DeepPartialTheme = {
  aesthetic?: string;
  font?: Partial<Theme["font"]>;
  color?: Partial<Theme["color"]>;
  gradient?: Partial<Theme["gradient"]>;
};

export function resolveTheme(meta?: { theme?: DeepPartialTheme }): Theme {
  if (!meta?.theme) return DEFAULT_THEME;

  const t = meta.theme;
  return {
    font: { ...DEFAULT_THEME.font, ...t.font },
    color: { ...DEFAULT_THEME.color, ...t.color },
    gradient: { ...DEFAULT_THEME.gradient, ...t.gradient },
  };
}
