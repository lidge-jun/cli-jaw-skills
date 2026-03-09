import React from "react";
import {
  AbsoluteFill,
  spring,
  useCurrentFrame,
  useVideoConfig,
  interpolate,
  staticFile,
} from "remotion";
import { Gif } from "@remotion/gif";
import type { Theme } from "../theme";
import type { AnimationConfig } from "../timeline/schema";
import { useEntranceAnimation } from "./useAnimation";

type GifSlideProps = {
  src: string;
  title?: string;
  caption?: string;
  fit?: "cover" | "contain";
  designTheme: Theme;
  animation?: AnimationConfig;
};

export const GifSlide: React.FC<GifSlideProps> = ({
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

  const exitFade = interpolate(
    frame,
    [durationInFrames - 10, durationInFrames],
    [1, 0],
    { extrapolateLeft: "clamp", extrapolateRight: "clamp" },
  );

  const isLocal = !src.startsWith("http://") && !src.startsWith("https://");
  const gifSrc = isLocal ? staticFile(src) : src;

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
            padding: "32px",
            opacity: cardProgress,
            transform: `translateY(${interpolate(cardProgress, [0, 1], [20, 0])}px)`,
            width: "100%",
            display: "flex",
            flexDirection: "column",
            alignItems: "center",
          }}
        >
          {title && (
            <div
              style={{
                fontSize: 40,
                fontWeight: 900,
                color: t.color.text,
                fontFamily: t.font.display,
                marginBottom: 20,
                opacity: titleProgress,
                letterSpacing: "-0.02em",
              }}
            >
              {title}
            </div>
          )}
          <div
            style={{
              width: "80%",
              display: "flex",
              justifyContent: "center",
            }}
          >
            <Gif
              src={gifSrc}
              width={800}
              fit={fit}
              style={{ borderRadius: 12 }}
            />
          </div>
          {caption && (
            <div
              style={{
                fontSize: 22,
                color: t.color.textMuted,
                marginTop: 16,
                textAlign: "center",
                fontStyle: "italic",
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
