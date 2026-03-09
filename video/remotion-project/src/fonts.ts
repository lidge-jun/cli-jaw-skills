import { loadFont as loadChakraPetch } from "@remotion/google-fonts/ChakraPetch";
import { loadFont as loadOutfit } from "@remotion/google-fonts/Outfit";
import { loadFont as loadJetBrainsMono } from "@remotion/google-fonts/JetBrainsMono";
import { loadFont as loadNotoSansKR } from "@remotion/google-fonts/NotoSansKR";

// Anti-slop: load ACTUAL weight extremes — 300(thin) to 900(black)
// Without these, CSS font-weight 300/900 is faked by browser synthesis → no real tension
const { fontFamily: chakra } = loadChakraPetch("normal", {
  weights: ["300", "400", "600", "700"],  // Chakra Petch max = 700
  subsets: ["latin"],
});
const { fontFamily: outfit } = loadOutfit("normal", {
  weights: ["300", "400", "700", "900"],  // Outfit supports 100-900
  subsets: ["latin"],
});
const { fontFamily: jetbrains } = loadJetBrainsMono("normal", {
  weights: ["400", "700"],
  subsets: ["latin"],
});
const { fontFamily: notoSansKR } = loadNotoSansKR("normal", {
  weights: ["300", "400", "700", "900"],  // Noto Sans KR supports 100-900
  ignoreTooManyRequestsWarning: true,
} as any);

export const FONTS = {
  // Outfit first — supports 100-900 (real 900 black for hero headings)
  // Chakra Petch for techy accent (caps at 700, fallback for lighter weights)
  display: `${outfit}, ${chakra}, ${notoSansKR}, sans-serif`,
  body: `${notoSansKR}, ${outfit}, sans-serif`,
  code: `${jetbrains}, monospace`,
};

