import React from "react";
import { AbsoluteFill, interpolate, useCurrentFrame, useVideoConfig } from "remotion";
import type { Theme } from "../theme";

type Props = {
  text: string;
  speaker?: string;
  placement?: "bottom-center" | "bottom-left" | "top-center";
  captionStyle?: "default" | "speaker" | "emphasis" | "minimal";
  fontSize?: number;
  fontFamily?: string;
  backgroundColor?: string;
  durationInFrames?: number;
  designTheme?: Theme;
};

export const Caption: React.FC<Props> = ({
  text,
  speaker,
  placement = "bottom-center",
  captionStyle = "default",
  fontSize = 24,
  fontFamily,
  backgroundColor,
  durationInFrames: cueDurationInFrames,
  designTheme: t,
}) => {
  const frame = useCurrentFrame();
  const config = useVideoConfig();
  const durationInFrames = cueDurationInFrames || config.durationInFrames;

  const fadeIn = interpolate(frame, [0, 8], [0, 1], { extrapolateRight: "clamp" });
  const fadeOut = interpolate(frame, [durationInFrames - 8, durationInFrames], [1, 0], {
    extrapolateLeft: "clamp",
  });
  const opacity = Math.min(fadeIn, fadeOut);
  const isTop = placement === "top-center";
  const isLeft = placement === "bottom-left";
  const isMinimal = captionStyle === "minimal";
  const isEmphasis = captionStyle === "emphasis";

  return (
    <AbsoluteFill
      style={{
        justifyContent: isTop ? "flex-start" : "flex-end",
        alignItems: isLeft ? "flex-start" : "center",
        padding: isTop ? "48px 72px" : "0 72px 72px",
      }}
    >
      <div
        style={{
          backgroundColor: isMinimal ? "transparent" : backgroundColor || "rgba(0, 0, 0, 0.75)",
          color: "#FFFFFF",
          fontSize: isEmphasis ? fontSize + 6 : fontSize,
          fontWeight: isEmphasis ? 700 : 500,
          fontFamily: fontFamily || t?.font.body || "'Outfit', sans-serif",
          padding: isMinimal ? "0" : "12px 28px",
          borderRadius: 8,
          opacity,
          textAlign: isLeft ? "left" : "center",
          maxWidth: isLeft ? "72%" : "82%",
          lineHeight: 1.25,
          whiteSpace: "pre-line",
          textShadow: isMinimal ? "0 2px 10px rgba(0,0,0,0.75)" : "none",
          boxShadow: isMinimal ? "none" : "0 18px 60px rgba(0,0,0,0.32)",
        }}
      >
        {speaker && captionStyle === "speaker" && (
          <div
            style={{
              color: t?.color.accent || "#22D3EE",
              fontSize: Math.max(14, fontSize * 0.48),
              letterSpacing: 1.6,
              textTransform: "uppercase",
              marginBottom: 5,
            }}
          >
            {speaker}
          </div>
        )}
        {text}
      </div>
    </AbsoluteFill>
  );
};
