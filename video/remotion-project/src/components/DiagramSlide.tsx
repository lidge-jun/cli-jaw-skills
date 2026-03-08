import React from "react";
import { AbsoluteFill, Img, spring, useCurrentFrame, useVideoConfig, interpolate } from "remotion";
import type { Theme } from "../theme";

type Props = {
  src?: string;
  alt?: string;
  title?: string;
  caption?: string;
  fit?: "cover" | "contain" | "fill";
  designTheme: Theme;
};

export const DiagramSlide: React.FC<Props> = ({
  src,
  title,
  caption,
  fit = "contain",
  designTheme: t,
}) => {
  const frame = useCurrentFrame();
  const { fps, durationInFrames } = useVideoConfig();

  const titleProgress = spring({ frame, fps, config: { damping: 100 } });
  const imageProgress = spring({ frame: Math.max(0, frame - 8), fps, config: { damping: 80, mass: 0.9 } });
  const captionProgress = spring({ frame: Math.max(0, frame - 16), fps, config: { damping: 120 } });

  const exitFade = interpolate(frame, [durationInFrames - 10, durationInFrames], [1, 0], {
    extrapolateLeft: "clamp",
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
      <AbsoluteFill style={{
        padding: "0 56px",
        flexDirection: "column",
        justifyContent: "center",
        alignItems: "center",
        opacity: exitFade,
      }}>
        {title && (
          <div
            style={{
              fontSize: 44,
              fontWeight: 700,
              color: t.color.accent,
              fontFamily: t.font.display,
              marginBottom: 30,
              opacity: titleProgress,
              transform: `translateY(${interpolate(titleProgress, [0, 1], [30, 0])}px)`,
              textAlign: "center",
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
                boxShadow: `0 8px 32px ${t.color.bg}80`,
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
      </AbsoluteFill>
    </AbsoluteFill>
  );
};
