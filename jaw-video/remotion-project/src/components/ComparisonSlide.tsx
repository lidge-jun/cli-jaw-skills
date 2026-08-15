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

type ComparisonSide = {
  label: string;
  items: string[];
  accent?: string;
};

type ComparisonProps = {
  title?: string;
  left: ComparisonSide;
  right: ComparisonSide;
  designTheme: Theme;
  animation?: AnimationConfig;
};

export const ComparisonSlide: React.FC<ComparisonProps> = ({
  title,
  left,
  right,
  designTheme: t,
  animation,
}) => {
  const frame = useCurrentFrame();
  const { fps, durationInFrames } = useVideoConfig();

  const entrance = useEntranceAnimation(animation);

  const titleProgress = spring({ frame, fps, config: { damping: 100 } });
  const leftProgress = spring({
    frame: Math.max(0, frame - 8),
    fps,
    config: { damping: 80 },
  });
  const rightProgress = spring({
    frame: Math.max(0, frame - 14),
    fps,
    config: { damping: 80 },
  });

  const exitFade = interpolate(
    frame,
    [durationInFrames - 10, durationInFrames],
    [1, 0],
    { extrapolateLeft: "clamp", extrapolateRight: "clamp" },
  );

  const renderSide = (
    side: ComparisonSide,
    progress: number,
    fromDirection: number,
  ) => {
    const accent = side.accent || t.color.accent;
    // Left side items get numbered squares, right side gets dash bars
    const isLeft = fromDirection < 0;
    return (
      <div
        style={{
          background: t.card.background,
          border: `1px solid ${accent}20`,
          borderRadius: isLeft ? 20 : 16,
          boxShadow: t.card.shadow,
          backdropFilter: `blur(${t.card.blur}px)`,
          WebkitBackdropFilter: `blur(${t.card.blur}px)`,
          padding: isLeft ? "40px 36px" : "36px 32px",
          flex: 1,
          opacity: progress,
          transform: `translateX(${interpolate(progress, [0, 1], [fromDirection * 40, 0])}px)`,
        }}
      >
        <div
          style={{
            fontSize: 26,
            fontWeight: 900,
            color: t.color.text,
            fontFamily: t.font.display,
            marginBottom: 24,
            borderBottom: `2px solid ${accent}30`,
            paddingBottom: 12,
            letterSpacing: "-0.02em",
          }}
        >
          <span style={{ color: accent, marginRight: 8 }}>{isLeft ? "◀" : "▶"}</span>
          {side.label}
        </div>
        <div style={{ display: "flex", flexDirection: "column", gap: 16 }}>
          {side.items.map((item, i) => {
            const itemDelay = 20 + i * 5;
            const itemProg = spring({
              frame: Math.max(0, frame - itemDelay),
              fps,
              config: { damping: 15, stiffness: 200 },
            });
            return (
              <div
                key={i}
                style={{
                  fontSize: 24,
                  color: t.color.text,
                  opacity: itemProg,
                  transform: `translateY(${interpolate(itemProg, [0, 1], [15, 0])}px)`,
                  display: "flex",
                  alignItems: "flex-start",
                  gap: 12,
                  lineHeight: 1.5,
                }}
              >
                {/* Left: numbered square / Right: horizontal accent bar */}
                {isLeft ? (
                  <span
                    style={{
                      width: 24,
                      height: 24,
                      borderRadius: 6,
                      backgroundColor: `${accent}18`,
                      border: `1px solid ${accent}30`,
                      color: accent,
                      fontSize: 13,
                      fontWeight: 700,
                      display: "flex",
                      alignItems: "center",
                      justifyContent: "center",
                      flexShrink: 0,
                      marginTop: 4,
                      fontVariantNumeric: "tabular-nums",
                    }}
                  >
                    {i + 1}
                  </span>
                ) : (
                  <span
                    style={{
                      width: 16,
                      height: 3,
                      borderRadius: 2,
                      backgroundColor: accent,
                      opacity: itemProg,
                      marginTop: 12,
                      flexShrink: 0,
                    }}
                  />
                )}
                <span style={{ fontWeight: 400 }}>{item}</span>
              </div>
            );
          })}
        </div>
      </div>
    );
  };

  return (
    <AbsoluteFill
      style={{
        background: t.gradient.slide,
        fontFamily: t.font.body,
        overflow: "hidden",
      }}
    >
      <AbsoluteFill
        style={{
          padding: "40px 48px",
          flexDirection: "column",
          justifyContent: "center",
          opacity: exitFade,
        }}
      >
        {title && (
          <div
            style={{
              fontSize: 42,
              fontWeight: 900,
              color: t.color.text,
              fontFamily: t.font.display,
              marginBottom: 36,
              opacity: titleProgress,
              transform: `translateY(${interpolate(titleProgress, [0, 1], [30, 0])}px)`,
              letterSpacing: "-0.02em",
            }}
          >
            {title}
          </div>
        )}
        <div style={{ display: "flex", gap: 24 }}>
          {renderSide(left, leftProgress, -1)}
          {renderSide(right, rightProgress, 1)}
        </div>
      </AbsoluteFill>
    </AbsoluteFill>
  );
};
