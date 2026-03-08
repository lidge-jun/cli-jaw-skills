import React from "react";
import { AbsoluteFill, spring, useCurrentFrame, useVideoConfig, interpolate } from "remotion";
import type { Theme } from "../theme";

type Props = {
  title: string;
  subtitle?: string;
  designTheme: Theme;
};

export const TitleSlide: React.FC<Props> = ({
  title,
  subtitle,
  designTheme: t,
}) => {
  const frame = useCurrentFrame();
  const { fps, durationInFrames } = useVideoConfig();

  // Staggered entrance
  const titleProgress = spring({ frame, fps, config: { damping: 120, mass: 0.8 } });
  const subtitleProgress = spring({ frame: Math.max(0, frame - 12), fps, config: { damping: 100 } });
  const accentProgress = spring({ frame: Math.max(0, frame - 20), fps, config: { damping: 80 } });

  // Continuous subtle drift for life
  const bgDrift = interpolate(frame, [0, durationInFrames], [0, 15], { extrapolateRight: "clamp" });
  const glowPulse = interpolate(
    Math.sin(frame * 0.05),
    [-1, 1],
    [0.6, 1],
  );

  // Exit fade
  const exitFade = interpolate(frame, [durationInFrames - 12, durationInFrames], [1, 0], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  // Title slide-up + fade
  const titleY = interpolate(titleProgress, [0, 1], [60, 0]);
  const titleOpacity = titleProgress;

  // Subtitle slide-up from further
  const subtitleY = interpolate(subtitleProgress, [0, 1], [40, 0]);

  return (
    <AbsoluteFill
      style={{
        background: t.gradient.hero,
        fontFamily: t.font.display,
        overflow: "hidden",
      }}
    >
      {/* Animated glow orb */}
      <div style={{
        position: "absolute",
        top: `${30 + bgDrift * 0.3}%`,
        left: `${20 + bgDrift * 0.5}%`,
        width: 400,
        height: 400,
        borderRadius: "50%",
        background: `radial-gradient(circle, ${t.color.accent}15 0%, transparent 70%)`,
        opacity: glowPulse * exitFade,
        filter: "blur(40px)",
      }} />

      {/* Main content area - fills screen */}
      <AbsoluteFill style={{
        justifyContent: "center",
        alignItems: "flex-start",
        padding: "0 60px",
        opacity: exitFade,
      }}>
        <div
          style={{
            transform: `translateY(${titleY}px)`,
            opacity: titleOpacity,
            color: t.color.text,
            fontSize: 64,
            fontWeight: 800,
            lineHeight: 1.15,
            letterSpacing: "-0.02em",
            maxWidth: "90%",
            whiteSpace: "pre-line",
          }}
        >
          {title}
        </div>

        {/* Accent line — expands from left */}
        <div style={{
          width: interpolate(accentProgress, [0, 1], [0, 180]),
          height: 3,
          backgroundColor: t.color.accent,
          marginTop: 32,
          marginBottom: 32,
          borderRadius: 2,
          opacity: accentProgress,
        }} />

        {subtitle && (
          <div
            style={{
              opacity: subtitleProgress,
              transform: `translateY(${subtitleY}px)`,
              color: t.color.textMuted,
              fontSize: 26,
              fontWeight: 400,
              fontFamily: t.font.body,
              letterSpacing: "0.06em",
              textTransform: "uppercase" as const,
              maxWidth: "80%",
              lineHeight: 1.5,
            }}
          >
            {subtitle}
          </div>
        )}
      </AbsoluteFill>
    </AbsoluteFill>
  );
};
