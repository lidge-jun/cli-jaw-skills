import React from "react";
import { AbsoluteFill, interpolate, useCurrentFrame, useVideoConfig } from "remotion";
import type { Theme } from "../theme";

type Props = {
  text: string;
  position?: "bottom" | "top";
  designTheme?: Theme;
};

export const Caption: React.FC<Props> = ({ text, position = "bottom", designTheme: t }) => {
  const frame = useCurrentFrame();
  const { durationInFrames } = useVideoConfig();

  const fadeIn = interpolate(frame, [0, 8], [0, 1], { extrapolateRight: "clamp" });
  const fadeOut = interpolate(frame, [durationInFrames - 8, durationInFrames], [1, 0], {
    extrapolateLeft: "clamp",
  });
  const opacity = Math.min(fadeIn, fadeOut);

  return (
    <AbsoluteFill
      style={{
        justifyContent: position === "top" ? "flex-start" : "flex-end",
        alignItems: "center",
        padding: position === "top" ? "40px 60px" : "0 60px 60px",
      }}
    >
      <div
        style={{
          backgroundColor: "rgba(0, 0, 0, 0.75)",
          color: "#FFFFFF",
          fontSize: 28,
          fontWeight: 400,
          fontFamily: t?.font.body || "'Outfit', sans-serif",
          padding: "12px 28px",
          borderRadius: 8,
          opacity,
          textAlign: "center",
          maxWidth: "80%",
        }}
      >
        {text}
      </div>
    </AbsoluteFill>
  );
};
