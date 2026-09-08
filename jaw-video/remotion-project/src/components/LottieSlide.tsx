import React, { useState, useEffect, useCallback } from "react";
import {
  AbsoluteFill,
  spring,
  useCurrentFrame,
  useVideoConfig,
  interpolate,
  staticFile,
  delayRender,
  continueRender,
} from "remotion";
import { Lottie, type LottieAnimationData } from "@remotion/lottie";
import type { Theme } from "../theme";
import type { AnimationConfig } from "../timeline/schema";
import { useEntranceAnimation } from "./useAnimation";

type LottieSlideProps = {
  src: string;
  title?: string;
  caption?: string;
  loop?: boolean;
  playbackRate?: number;
  designTheme: Theme;
  animation?: AnimationConfig;
};

export const LottieSlide: React.FC<LottieSlideProps> = ({
  src,
  title,
  caption,
  loop = false,
  playbackRate = 1,
  designTheme: t,
  animation,
}) => {
  const frame = useCurrentFrame();
  const { fps, durationInFrames } = useVideoConfig();

  const entrance = useEntranceAnimation(animation);

  const [handle] = useState(() => delayRender("Loading Lottie animation"));
  const [animationData, setAnimationData] =
    useState<LottieAnimationData | null>(null);

  const isLocal = !src.startsWith("http://") && !src.startsWith("https://");
  const lottieSrc = isLocal ? staticFile(src) : src;

  useEffect(() => {
    fetch(lottieSrc)
      .then((r) => r.json())
      .then((data: LottieAnimationData) => {
        setAnimationData(data);
        continueRender(handle);
      })
      .catch((err) => {
        console.error("Failed to load Lottie:", err);
        continueRender(handle);
      });
  }, [lottieSrc, handle]);

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
          opacity: exitFade,
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
          {animationData && (
            <div
              style={{
                width: "70%",
                display: "flex",
                justifyContent: "center",
              }}
            >
              <Lottie
                animationData={animationData}
                loop={loop}
                playbackRate={playbackRate}
              />
            </div>
          )}
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
