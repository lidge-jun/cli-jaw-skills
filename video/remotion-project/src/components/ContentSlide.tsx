import React from "react";
import {
  AbsoluteFill,
  spring,
  useCurrentFrame,
  useVideoConfig,
  interpolate,
} from "remotion";
import type { Theme } from "../theme";

type Props = {
  header: string;
  content?: string;
  bulletPoints?: string[];
  designTheme: Theme;
};

export const ContentSlide: React.FC<Props> = ({
  header,
  content,
  bulletPoints,
  designTheme: t,
}) => {
  const frame = useCurrentFrame();
  const { fps, durationInFrames } = useVideoConfig();

  // Staggered header entrance
  const headerProgress = spring({ frame, fps, config: { damping: 100, mass: 0.8 } });
  const headerY = interpolate(headerProgress, [0, 1], [50, 0]);

  // Content paragraph
  const contentProgress = spring({ frame: Math.max(0, frame - 10), fps, config: { damping: 120 } });

  // Exit fade
  const exitFade = interpolate(frame, [durationInFrames - 10, durationInFrames], [1, 0], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  // Accent bar animation (grows from top)
  const accentBarHeight = interpolate(headerProgress, [0, 1], [0, 100]);

  return (
    <AbsoluteFill
      style={{
        background: t.gradient.slide,
        fontFamily: t.font.body,
        overflow: "hidden",
      }}
    >
      {/* Left accent bar */}
      <div style={{
        position: "absolute",
        left: 0,
        top: "20%",
        width: 4,
        height: `${accentBarHeight * 0.6}%`,
        backgroundColor: t.color.accent,
        opacity: exitFade * 0.8,
      }} />

      {/* Main content - uses full height with proper spacing */}
      <AbsoluteFill style={{
        padding: "0 56px",
        flexDirection: "column",
        justifyContent: "center",
        opacity: exitFade,
      }}>
        {/* Header */}
        <div
          style={{
            fontSize: 48,
            fontWeight: 700,
            color: t.color.accent,
            transform: `translateY(${headerY}px)`,
            opacity: headerProgress,
            fontFamily: t.font.display,
            lineHeight: 1.2,
            marginBottom: 20,
          }}
        >
          {header}
        </div>

        {/* Divider line */}
        <div style={{
          width: interpolate(headerProgress, [0, 1], [0, 160]),
          height: 2,
          backgroundColor: `${t.color.accent}40`,
          marginBottom: 32,
        }} />

        {/* Content paragraph */}
        {content && (
          <div
            style={{
              fontSize: 28,
              color: t.color.text,
              lineHeight: 1.7,
              opacity: contentProgress,
              transform: `translateY(${interpolate(contentProgress, [0, 1], [20, 0])}px)`,
              marginBottom: 32,
              maxWidth: "95%",
            }}
          >
            {content}
          </div>
        )}

        {/* Bullet points with staggered slide-in */}
        {bulletPoints && (
          <div style={{ display: "flex", flexDirection: "column", gap: 28, marginTop: content ? 0 : 8 }}>
            {bulletPoints.map((point, i) => {
              const delay = (content ? 18 : 10) + i * 6;
              const itemProgress = spring({
                frame: Math.max(0, frame - delay),
                fps,
                config: { damping: 100, stiffness: 120 },
              });
              const itemX = interpolate(itemProgress, [0, 1], [40, 0]);


              return (
                <div
                  key={i}
                  style={{
                    fontSize: 30,
                    color: t.color.text,
                    opacity: itemProgress,
                    transform: `translateX(${itemX}px)`,
                    display: "flex",
                    alignItems: "flex-start",
                    gap: 16,
                    lineHeight: 1.5,
                  }}
                >
                  {/* Animated accent indicator */}
                  <span style={{
                    width: 4,
                    height: interpolate(itemProgress, [0, 1], [0, 28]),
                    backgroundColor: t.color.accent,
                    borderRadius: 2,
                    marginTop: 4,
                    flexShrink: 0,
                  }} />
                  <span>{point}</span>
                </div>
              );
            })}
          </div>
        )}
      </AbsoluteFill>
    </AbsoluteFill>
  );
};
