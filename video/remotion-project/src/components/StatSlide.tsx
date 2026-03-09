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

type StatItem = {
  value: number;
  prefix?: string;
  suffix?: string;
  decimals?: number;
  label: string;
  trend?: "up" | "down" | "neutral";
};

type StatProps = {
  stats: StatItem[];
  title?: string;
  designTheme: Theme;
  animation?: AnimationConfig;
};

export const StatSlide: React.FC<StatProps> = ({
  stats,
  title,
  designTheme: t,
  animation,
}) => {
  const frame = useCurrentFrame();
  const { fps, durationInFrames } = useVideoConfig();

  // Guard: empty or malformed stats → render placeholder
  if (!stats || stats.length === 0) {
    return (
      <AbsoluteFill
        style={{
          background: t.gradient.slide,
          fontFamily: t.font.body,
          justifyContent: "center",
          alignItems: "center",
        }}
      >
        <div style={{ color: t.color.textMuted, fontSize: 32 }}>
          No data available
        </div>
      </AbsoluteFill>
    );
  }

  const entrance = useEntranceAnimation(animation);

  const titleProgress = spring({ frame, fps, config: { damping: 100 } });

  const exitFade = interpolate(
    frame,
    [durationInFrames - 10, durationInFrames],
    [1, 0],
    { extrapolateLeft: "clamp", extrapolateRight: "clamp" },
  );

  const glowDrift = interpolate(frame, [0, durationInFrames], [0, 10], {
    extrapolateRight: "clamp",
  });

  const trendArrow = (trend?: "up" | "down" | "neutral") => {
    if (trend === "up") return "↑";
    if (trend === "down") return "↓";
    return "";
  };

  const trendColor = (trend?: "up" | "down" | "neutral") => {
    if (trend === "up") return "#34D399";
    if (trend === "down") return "#F87171";
    return t.color.textMuted;
  };

  // Hero stat is the first one — gets prominence
  const hero = stats[0];
  const supporting = stats.slice(1, 4);

  // Hero count-up
  const heroDelay = 6;
  const heroProg = spring({
    frame: Math.max(0, frame - heroDelay),
    fps,
    config: { damping: 14, stiffness: 180, mass: 0.9 },
  });
  const heroCount = interpolate(heroProg, [0, 1], [0, hero.value]);
  const heroDisplay = hero.decimals != null
    ? heroCount.toFixed(hero.decimals)
    : Math.round(heroCount).toString();

  return (
    <AbsoluteFill
      style={{
        background: t.gradient.slide,
        fontFamily: t.font.body,
        overflow: "hidden",
      }}
    >
      {/* Glow — left side */}
      <div
        style={{
          position: "absolute",
          top: `${30 + glowDrift * 0.3}%`,
          left: `${5 + glowDrift * 0.4}%`,
          width: 400,
          height: 400,
          borderRadius: "50%",
          background: `radial-gradient(circle, ${t.color.accent}10 0%, transparent 70%)`,
          opacity: exitFade * 0.5,
          filter: "blur(50px)",
        }}
      />

      <AbsoluteFill
        style={{
          padding: "48px 56px",
          opacity: exitFade * entrance.opacity,
          transform: entrance.transform,
        }}
      >
        {/* Title — left-aligned */}
        {title && (
          <div
            style={{
              fontSize: 40,
              fontWeight: 900,
              color: t.color.text,
              fontFamily: t.font.display,
              marginBottom: 40,
              opacity: titleProgress,
              transform: `translateY(${interpolate(titleProgress, [0, 1], [30, 0])}px)`,
              letterSpacing: "-0.02em",
            }}
          >
            {title}
          </div>
        )}

        {/* Two-row layout: hero stat top, supporting stats bottom */}
        <div style={{ display: "flex", flexDirection: "column", gap: 24, flex: 1, justifyContent: "center" }}>
          {/* HERO STAT — large, no card, just big number */}
          <div
            style={{
              opacity: heroProg,
              transform: `scale(${interpolate(heroProg, [0, 1], [0.85, 1])})`,
              transformOrigin: "left center",
              marginBottom: 16,
            }}
          >
            <div
              style={{
                fontSize: 96,
                fontWeight: 900,
                color: t.color.text,
                fontFamily: t.font.display,
                lineHeight: 1,
                fontVariantNumeric: "tabular-nums",
                letterSpacing: "-0.03em",
              }}
            >
              {hero.prefix || ""}
              {heroDisplay}
              {hero.suffix || ""}
              {hero.trend && (
                <span style={{ color: trendColor(hero.trend), fontSize: 48, marginLeft: 8 }}>
                  {trendArrow(hero.trend)}
                </span>
              )}
            </div>
            <div
              style={{
                fontSize: 22,
                fontWeight: 300,
                color: t.color.textMuted,
                marginTop: 12,
                letterSpacing: "0.1em",
                textTransform: "uppercase" as const,
              }}
            >
              {hero.label}
            </div>
          </div>

          {/* SUPPORTING STATS — smaller cards in a row */}
          {supporting.length > 0 && (
            <div style={{ display: "flex", gap: 20 }}>
              {supporting.map((stat, i) => {
                const delay = 14 + i * 8;
                const cardProg = spring({
                  frame: Math.max(0, frame - delay),
                  fps,
                  config: { damping: 12, stiffness: 200, mass: 0.8 },
                });
                const countUp = interpolate(cardProg, [0, 1], [0, stat.value]);
                const displayValue = stat.decimals != null
                  ? countUp.toFixed(stat.decimals)
                  : Math.round(countUp).toString();

                return (
                  <div
                    key={i}
                    style={{
                      background: t.card.background,
                      border: `1px solid ${t.card.border}`,
                      borderRadius: 16,
                      boxShadow: t.card.shadow,
                      backdropFilter: `blur(${t.card.blur}px)`,
                      WebkitBackdropFilter: `blur(${t.card.blur}px)`,
                      padding: "28px 32px",
                      flex: 1,
                      opacity: cardProg,
                      transform: `translateY(${interpolate(cardProg, [0, 1], [20, 0])}px)`,
                    }}
                  >
                    <div
                      style={{
                        fontSize: 40,
                        fontWeight: 900,
                        color: t.color.text,
                        fontFamily: t.font.display,
                        lineHeight: 1.1,
                        fontVariantNumeric: "tabular-nums",
                      }}
                    >
                      {stat.prefix || ""}
                      {displayValue}
                      {stat.suffix || ""}
                      {stat.trend && (
                        <span style={{ color: trendColor(stat.trend), fontSize: 24, marginLeft: 4 }}>
                          {trendArrow(stat.trend)}
                        </span>
                      )}
                    </div>
                    <div
                      style={{
                        fontSize: 16,
                        fontWeight: 300,
                        color: t.color.textMuted,
                        marginTop: 10,
                        letterSpacing: "0.1em",
                        textTransform: "uppercase" as const,
                      }}
                    >
                      {stat.label}
                    </div>
                  </div>
                );
              })}
            </div>
          )}
        </div>
      </AbsoluteFill>
    </AbsoluteFill>
  );
};
