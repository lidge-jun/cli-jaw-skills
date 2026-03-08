import React from "react";
import { AbsoluteFill, spring, useCurrentFrame, useVideoConfig, interpolate } from "remotion";
import type { Theme } from "../theme";

type Props = {
  code: string;
  language?: string;
  title?: string;
  designTheme: Theme;
};

export const CodeSlide: React.FC<Props> = ({ code, language = "typescript", title, designTheme: t }) => {
  const frame = useCurrentFrame();
  const { fps, durationInFrames } = useVideoConfig();

  const titleProgress = spring({ frame, fps, config: { damping: 100 } });
  const containerProgress = spring({ frame: Math.max(0, frame - 8), fps, config: { damping: 80, mass: 0.9 } });
  const lines = code.split("\n");

  // Exit fade
  const exitFade = interpolate(frame, [durationInFrames - 10, durationInFrames], [1, 0], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  // Container slide-up
  const containerY = interpolate(containerProgress, [0, 1], [40, 0]);

  return (
    <AbsoluteFill
      style={{
        background: t.gradient.slide,
        fontFamily: t.font.body,
        overflow: "hidden",
      }}
    >
      <AbsoluteFill style={{
        padding: "0 40px",
        flexDirection: "column",
        justifyContent: "center",
        opacity: exitFade,
      }}>
        {/* Title */}
        {title && (
          <div
            style={{
              fontSize: 40,
              fontWeight: 700,
              color: t.color.text,
              marginBottom: 28,
              opacity: titleProgress,
              transform: `translateY(${interpolate(titleProgress, [0, 1], [30, 0])}px)`,
              fontFamily: t.font.display,
            }}
          >
            {title}
          </div>
        )}

        {/* Terminal container — fills available space */}
        <div
          style={{
            backgroundColor: `${t.color.bg}ee`,
            borderRadius: 16,
            opacity: containerProgress,
            transform: `translateY(${containerY}px)`,
            overflow: "hidden",
            border: `1px solid ${t.color.accent}25`,
            display: "flex",
            flexDirection: "column",
            boxShadow: `0 8px 32px ${t.color.bg}80`,
          }}
        >
          {/* Terminal chrome bar */}
          <div style={{
            display: "flex",
            alignItems: "center",
            gap: 8,
            padding: "14px 20px",
            borderBottom: `1px solid ${t.color.accent}15`,
            flexShrink: 0,
          }}>
            <div style={{ width: 12, height: 12, borderRadius: "50%", backgroundColor: "#ff5f57" }} />
            <div style={{ width: 12, height: 12, borderRadius: "50%", backgroundColor: "#febc2e" }} />
            <div style={{ width: 12, height: 12, borderRadius: "50%", backgroundColor: "#28c840" }} />
            {language && (
              <span style={{
                marginLeft: "auto",
                fontSize: 13,
                color: t.color.textMuted,
                fontFamily: t.font.code,
                textTransform: "uppercase" as const,
              }}>{language}</span>
            )}
          </div>

          {/* Code body with line numbers — each line animates in */}
          <div style={{ padding: "20px 0", display: "flex", flex: 1 }}>
            {/* Line numbers */}
            <div style={{
              display: "flex",
              flexDirection: "column",
              alignItems: "flex-end",
              paddingRight: 16,
              paddingLeft: 20,
              borderRight: `1px solid ${t.color.accent}12`,
              userSelect: "none" as const,
            }}>
              {lines.map((_, i) => {
                const lineDelay = 12 + i * 2;
                const lineOpacity = spring({
                  frame: Math.max(0, frame - lineDelay),
                  fps,
                  config: { damping: 200 },
                });
                return (
                  <span key={i} style={{
                    fontFamily: t.font.code,
                    fontSize: 20,
                    lineHeight: 1.8,
                    color: t.color.textMuted,
                    opacity: lineOpacity * 0.4,
                  }}>{i + 1}</span>
                );
              })}
            </div>

            {/* Code lines — staggered reveal */}
            <div style={{
              display: "flex",
              flexDirection: "column",
              paddingLeft: 20,
              paddingRight: 28,
              flex: 1,
            }}>
              {lines.map((line, i) => {
                const lineDelay = 12 + i * 2;
                const lineProgress = spring({
                  frame: Math.max(0, frame - lineDelay),
                  fps,
                  config: { damping: 120 },
                });
                const lineX = interpolate(lineProgress, [0, 1], [20, 0]);

                return (
                  <div key={i} style={{
                    fontFamily: t.font.code,
                    fontSize: 20,
                    lineHeight: 1.8,
                    color: t.color.text,
                    whiteSpace: "pre",
                    opacity: lineProgress,
                    transform: `translateX(${lineX}px)`,
                  }}>
                    {line || " "}
                  </div>
                );
              })}
            </div>
          </div>
        </div>
      </AbsoluteFill>
    </AbsoluteFill>
  );
};
