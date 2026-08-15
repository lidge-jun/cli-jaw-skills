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

type Props = {
  header: string;
  content?: string;
  bulletPoints?: string[];
  designTheme: Theme;
  animation?: AnimationConfig;
};

export const ContentSlide: React.FC<Props> = ({
  header,
  content,
  bulletPoints,
  designTheme: t,
  animation,
}) => {
  const frame = useCurrentFrame();
  const { fps, durationInFrames } = useVideoConfig();

  const entrance = useEntranceAnimation(animation);

  // Staggered entrance timings
  const headerProgress = spring({
    frame,
    fps,
    config: { damping: 100, mass: 0.8 },
  });
  const contentProgress = spring({
    frame: Math.max(0, frame - 8),
    fps,
    config: { damping: 120 },
  });

  // Exit
  const exitFade = interpolate(
    frame,
    [durationInFrames - 10, durationInFrames],
    [1, 0],
    { extrapolateLeft: "clamp", extrapolateRight: "clamp" },
  );

  // Background glow — top-right for asymmetry
  const glowDrift = interpolate(frame, [0, durationInFrames], [0, 12], {
    extrapolateRight: "clamp",
  });
  const glowPulse = interpolate(
    Math.sin(frame * 0.04),
    [-1, 1],
    [0.4, 0.8],
  );

  const hasBullets = bulletPoints && bulletPoints.length > 0;
  const headerY = interpolate(headerProgress, [0, 1], [40, 0]);

  return (
    <AbsoluteFill
      style={{
        background: t.gradient.slide,
        fontFamily: t.font.body,
        overflow: "hidden",
      }}
    >
      {/* Glow orb — top-right */}
      <div
        style={{
          position: "absolute",
          top: `${10 + glowDrift * 0.4}%`,
          right: `${5 + glowDrift * 0.3}%`,
          width: 350,
          height: 350,
          borderRadius: "50%",
          background: `radial-gradient(circle, ${t.color.accent}12 0%, transparent 70%)`,
          opacity: glowPulse * exitFade,
          filter: "blur(50px)",
        }}
      />

      {/* Split layout: left header zone + right content zone */}
      <AbsoluteFill
        style={{
          padding: "48px 56px",
          display: "flex",
          flexDirection: "row",
          gap: 40,
          alignItems: "stretch",
          opacity: exitFade * entrance.opacity,
          transform: entrance.transform,
        }}
      >
        {/* LEFT COLUMN — header + optional paragraph (40% width) */}
        <div
          style={{
            flex: "0 0 38%",
            display: "flex",
            flexDirection: "column",
            justifyContent: "center",
          }}
        >
          {/* Header — 900 black, tight */}
          <div
            style={{
              fontSize: 46,
              fontWeight: 900,
              color: t.color.text,
              fontFamily: t.font.display,
              lineHeight: 1.1,
              letterSpacing: "-0.03em",
              opacity: headerProgress,
              transform: `translateY(${headerY}px)`,
            }}
          >
            {header}
          </div>

          {/* Accent bar — short, below header */}
          <div
            style={{
              width: interpolate(headerProgress, [0, 1], [0, 48]),
              height: 3,
              backgroundColor: t.color.accent,
              marginTop: 20,
              marginBottom: 24,
              borderRadius: 2,
            }}
          />

          {/* Content paragraph — in left column */}
          {content && (
            <div
              style={{
                fontSize: 24,
                fontWeight: 400,
                color: t.color.textMuted,
                lineHeight: 1.7,
                opacity: contentProgress,
                transform: `translateY(${interpolate(contentProgress, [0, 1], [15, 0])}px)`,
              }}
            >
              {content}
            </div>
          )}
        </div>

        {/* RIGHT COLUMN — bullets in card (60% width) */}
        {hasBullets && (
          <div
            style={{
              flex: 1,
              display: "flex",
              alignItems: "center",
            }}
          >
            <div
              style={{
                background: t.card.background,
                border: `1px solid ${t.card.border}`,
                borderRadius: t.card.borderRadius,
                boxShadow: t.card.shadow,
                backdropFilter: `blur(${t.card.blur}px)`,
                WebkitBackdropFilter: `blur(${t.card.blur}px)`,
                padding: "40px 44px",
                width: "100%",
                display: "flex",
                flexDirection: "column",
                gap: 20,
              }}
            >
              {bulletPoints!.map((point, i) => {
                const delay = 10 + i * 6;
                const itemProgress = spring({
                  frame: Math.max(0, frame - delay),
                  fps,
                  config: { damping: 15, stiffness: 200 },
                });
                const itemX = interpolate(itemProgress, [0, 1], [24, 0]);

                return (
                  <div
                    key={i}
                    style={{
                      fontSize: 28,
                      color: t.color.text,
                      fontWeight: 400,
                      opacity: itemProgress,
                      transform: `translateX(${itemX}px)`,
                      display: "flex",
                      alignItems: "center",
                      gap: 16,
                      lineHeight: 1.5,
                    }}
                  >
                    {/* Numbered badge */}
                    <span
                      style={{
                        width: 32,
                        height: 32,
                        borderRadius: 8,
                        backgroundColor: `${t.color.accent}15`,
                        border: `1px solid ${t.color.accent}25`,
                        color: t.color.accent,
                        fontSize: 15,
                        fontWeight: 700,
                        display: "flex",
                        alignItems: "center",
                        justifyContent: "center",
                        flexShrink: 0,
                        fontVariantNumeric: "tabular-nums",
                      }}
                    >
                      {i + 1}
                    </span>
                    <span>{point}</span>
                  </div>
                );
              })}
            </div>
          </div>
        )}

        {/* Fallback: if no bullets, paragraph gets full width */}
        {!hasBullets && content && (
          <div
            style={{
              flex: 1,
              display: "flex",
              alignItems: "center",
            }}
          >
            <div
              style={{
                background: t.card.background,
                border: `1px solid ${t.card.border}`,
                borderRadius: t.card.borderRadius,
                padding: "48px 52px",
                fontSize: 30,
                fontWeight: 400,
                color: t.color.text,
                lineHeight: 1.7,
                opacity: contentProgress,
              }}
            >
              {content}
            </div>
          </div>
        )}
      </AbsoluteFill>
    </AbsoluteFill>
  );
};
