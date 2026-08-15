import React from "react";
import {
  AbsoluteFill,
  spring,
  useCurrentFrame,
  useVideoConfig,
  interpolate,
} from "remotion";
import type { Theme } from "../theme";
import type { AnimationConfig } from "../timeline/schema";
import { useEntranceAnimation } from "./useAnimation";

type QuoteProps = {
  quote: string;
  author?: string;
  source?: string;
  designTheme: Theme;
  animation?: AnimationConfig;
};

export const QuoteSlide: React.FC<QuoteProps> = ({
  quote,
  author,
  source,
  designTheme: t,
  animation,
}) => {
  const frame = useCurrentFrame();
  const { fps, durationInFrames } = useVideoConfig();

  const entrance = useEntranceAnimation(animation);

  // Staggered entrances — quote mark leads, text follows, author trails
  const glyphProgress = spring({
    frame,
    fps,
    config: { damping: 80, mass: 1.2 },
  });
  const quoteProgress = spring({
    frame: Math.max(0, frame - 10),
    fps,
    config: { damping: 120, mass: 0.9 },
  });
  const authorProgress = spring({
    frame: Math.max(0, frame - 24),
    fps,
    config: { damping: 100 },
  });
  const lineProgress = spring({
    frame: Math.max(0, frame - 6),
    fps,
    config: { damping: 60 },
  });

  const exitFade = interpolate(
    frame,
    [durationInFrames - 12, durationInFrames],
    [1, 0],
    { extrapolateLeft: "clamp", extrapolateRight: "clamp" },
  );

  // Glow — positioned bottom-left for asymmetry (not center)
  const glowDrift = interpolate(frame, [0, durationInFrames], [0, 8], {
    extrapolateRight: "clamp",
  });

  return (
    <AbsoluteFill
      style={{
        background: t.gradient.slide,
        fontFamily: t.font.body,
        overflow: "hidden",
      }}
    >
      {/* Glow orb — bottom-left, not center */}
      <div
        style={{
          position: "absolute",
          bottom: `${15 + glowDrift * 0.3}%`,
          left: `${5 + glowDrift * 0.5}%`,
          width: 400,
          height: 400,
          borderRadius: "50%",
          background: `radial-gradient(circle, ${t.color.accent}10 0%, transparent 70%)`,
          opacity: exitFade * 0.6,
          filter: "blur(60px)",
        }}
      />

      <AbsoluteFill
        style={{
          padding: "60px 80px",
          opacity: exitFade * entrance.opacity,
          transform: entrance.transform,
        }}
      >
        {/* Giant quote glyph — hero element, 200px, top-left anchor */}
        <div
          style={{
            position: "absolute",
            top: 40,
            left: 60,
            fontSize: 240,
            color: `${t.color.accent}15`,
            fontFamily: "Georgia, serif",
            lineHeight: 1,
            opacity: interpolate(glyphProgress, [0, 1], [0, 1]),
            transform: `scale(${interpolate(glyphProgress, [0, 1], [0.6, 1])})`,
            transformOrigin: "top left",
          }}
        >
          &ldquo;
        </div>

        {/* Vertical accent line — left edge, grows down */}
        <div
          style={{
            position: "absolute",
            left: 60,
            top: 280,
            width: 3,
            height: interpolate(lineProgress, [0, 1], [0, 200]),
            backgroundColor: t.color.accent,
            borderRadius: 2,
          }}
        />

        {/* Quote text — offset right, not centered */}
        <div
          style={{
            position: "absolute",
            top: "28%",
            left: 120,
            right: 80,
            opacity: quoteProgress,
            transform: `translateY(${interpolate(quoteProgress, [0, 1], [30, 0])}px)`,
          }}
        >
          <div
            style={{
              fontSize: 38,
              fontWeight: 400,
              color: t.color.text,
              fontStyle: "italic",
              lineHeight: 1.65,
              letterSpacing: "0.01em",
            }}
          >
            {quote}
          </div>
        </div>

        {/* Author — bottom-right aligned for asymmetry */}
        {(author || source) && (
          <div
            style={{
              position: "absolute",
              bottom: 80,
              right: 80,
              opacity: authorProgress,
              transform: `translateX(${interpolate(authorProgress, [0, 1], [20, 0])}px)`,
              textAlign: "right",
            }}
          >
            {author && (
              <div
                style={{
                  fontSize: 22,
                  color: t.color.text,
                  fontWeight: 700,
                  fontFamily: t.font.display,
                  letterSpacing: "-0.01em",
                }}
              >
                {author}
              </div>
            )}
            {source && (
              <div
                style={{
                  fontSize: 16,
                  color: t.color.textMuted,
                  fontWeight: 300,
                  marginTop: 6,
                  letterSpacing: "0.06em",
                  textTransform: "uppercase" as const,
                }}
              >
                {source}
              </div>
            )}
          </div>
        )}
      </AbsoluteFill>
    </AbsoluteFill>
  );
};
