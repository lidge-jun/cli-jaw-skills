import React from "react";
import {
  AbsoluteFill,
  Img,
  spring,
  useCurrentFrame,
  useVideoConfig,
  interpolate,
} from "remotion";
import type { Theme } from "../theme";
import type { AnimationConfig } from "../timeline/schema";
import { useEntranceAnimation } from "./useAnimation";

type Props = {
  src?: string;
  alt?: string;
  title?: string;
  caption?: string;
  fit?: "cover" | "contain" | "fill";
  designTheme: Theme;
  animation?: AnimationConfig;
};

export const DiagramSlide: React.FC<Props> = ({
  src,
  title,
  caption,
  fit = "contain",
  designTheme: t,
  animation,
}) => {
  const frame = useCurrentFrame();
  const { fps, durationInFrames } = useVideoConfig();

  const entrance = useEntranceAnimation(animation);

  const cardProgress = spring({
    frame: Math.max(0, frame - 4),
    fps,
    config: { damping: 80 },
  });
  const titleProgress = spring({ frame, fps, config: { damping: 100 } });
  const imageProgress = spring({
    frame: Math.max(0, frame - 8),
    fps,
    config: { damping: 80, mass: 0.9 },
  });
  const captionProgress = spring({
    frame: Math.max(0, frame - 16),
    fps,
    config: { damping: 120 },
  });

  const exitFade = interpolate(
    frame,
    [durationInFrames - 10, durationInFrames],
    [1, 0],
    { extrapolateLeft: "clamp", extrapolateRight: "clamp" },
  );

  // Glow
  const glowDrift = interpolate(frame, [0, durationInFrames], [0, 10], {
    extrapolateRight: "clamp",
  });
  const glowPulse = interpolate(
    Math.sin(frame * 0.04),
    [-1, 1],
    [0.3, 0.7],
  );

  return (
    <AbsoluteFill
      style={{
        background: t.gradient.slide,
        fontFamily: t.font.body,
        overflow: "hidden",
      }}
    >
      {/* Background glow */}
      <div
        style={{
          position: "absolute",
          bottom: `${15 + glowDrift * 0.3}%`,
          left: `${30 + glowDrift * 0.5}%`,
          width: 300,
          height: 300,
          borderRadius: "50%",
          background: `radial-gradient(circle, ${t.color.accent}10 0%, transparent 70%)`,
          opacity: glowPulse * exitFade,
          filter: "blur(50px)",
        }}
      />

      {/* Surface card */}
      <AbsoluteFill
        style={{
          padding: "40px 48px",
          justifyContent: "center",
          alignItems: "center",
          opacity: exitFade * entrance.opacity,
          transform: entrance.transform,
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
            padding: "40px 48px",
            opacity: cardProgress,
            transform: `translateY(${interpolate(cardProgress, [0, 1], [20, 0])}px)`,
            display: "flex",
            flexDirection: "column",
            alignItems: "center",
            width: "100%",
          }}
        >
          {title && (
            <div
              style={{
                fontSize: 44,
                fontWeight: 900,
                color: t.color.text,
                fontFamily: t.font.display,
                marginBottom: 30,
                opacity: titleProgress,
                transform: `translateY(${interpolate(titleProgress, [0, 1], [30, 0])}px)`,
                letterSpacing: "-0.02em",
              }}
            >
              {title}
            </div>
          )}
          {src && (
            <div
              style={{
                display: "flex",
                justifyContent: "center",
                alignItems: "center",
                width: "100%",
                opacity: imageProgress,
                transform: `scale(${interpolate(imageProgress, [0, 1], [0.9, 1])})`,
              }}
            >
              <Img
                src={src}
                style={{
                  maxWidth: "90%",
                  maxHeight: "65%",
                  objectFit: fit,
                  borderRadius: 12,
                }}
              />
            </div>
          )}
          {caption && (
            <div
              style={{
                fontSize: 24,
                color: t.color.textMuted,
                marginTop: 24,
                textAlign: "center",
                fontStyle: "italic",
                opacity: captionProgress,
                transform: `translateY(${interpolate(captionProgress, [0, 1], [15, 0])}px)`,
              }}
            >
              {caption}
            </div>
          )}
        </div>
      </AbsoluteFill>
    </AbsoluteFill>
  );
};
