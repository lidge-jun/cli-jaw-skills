import React from "react";
import { useVideoConfig, Audio, Sequence, staticFile, interpolate } from "remotion";
import { TransitionSeries, linearTiming, springTiming } from "@remotion/transitions";
import { fade } from "@remotion/transitions/fade";
import { slide } from "@remotion/transitions/slide";
import { wipe } from "@remotion/transitions/wipe";
import { flip } from "@remotion/transitions/flip";
import { clockWipe } from "@remotion/transitions/clock-wipe";
import { ElementRouter } from "./element-router";
import type { Timeline, TransitionConfig } from "./schema";
import { resolveTheme } from "../theme";

// eslint-disable-next-line @typescript-eslint/no-explicit-any
function resolvePresentation(config: TransitionConfig, width: number, height: number): any {
  switch (config.type) {
    case "slide":
      return slide({ direction: config.direction || "from-right" });
    case "wipe":
      return wipe({ direction: config.direction || "from-left" });
    case "flip":
      return flip({ direction: config.direction || "from-right" });
    case "clock-wipe":
      return clockWipe({ width, height });
    case "fade":
    default:
      return fade();
  }
}

function resolveTiming(config: TransitionConfig, fps: number) {
  const frames = Math.round((config.durationSec ?? 0.5) * fps);
  if (config.timing === "spring") {
    return springTiming({ config: { damping: 200 }, durationInFrames: frames });
  }
  return linearTiming({ durationInFrames: frames });
}

type Props = {
  timeline: Timeline;
};

export const TimelineRenderer: React.FC<Props> = ({ timeline }) => {
  const { fps, width, height } = useVideoConfig();
  const theme = resolveTheme(timeline.meta);

  return (
    <>
      <TransitionSeries>
        {timeline.elements.map((el, i) => {
          const durationInFrames = Math.round(el.durationSec * fps);
          const hasTransition =
            el.transition && el.transition.type !== "none";
          const transitionFrames = hasTransition
            ? Math.round((el.transition!.durationSec ?? 0.5) * fps)
            : 0;

          return (
            <React.Fragment key={i}>
              <TransitionSeries.Sequence durationInFrames={durationInFrames}>
                <ElementRouter element={el} theme={theme} />
              </TransitionSeries.Sequence>
              {transitionFrames > 0 && el.transition && (
                <TransitionSeries.Transition
                  presentation={resolvePresentation(el.transition, width, height)}
                  timing={resolveTiming(el.transition, fps)}
                />
              )}
            </React.Fragment>
          );
        })}
      </TransitionSeries>

      {/* Audio rendering with fade support */}
      {timeline.audio?.map((a, i) => {
        if (!a.src) return null;
        const startFrame = Math.round((a.startSec ?? 0) * fps);
        const isLocal =
          !a.src.startsWith("http://") && !a.src.startsWith("https://");
        const audioSrc = isLocal ? staticFile(a.src) : a.src;

        const fadeInFrames = a.fadeInSec ? Math.round(a.fadeInSec * fps) : 0;
        const fadeOutFrames = a.fadeOutSec ? Math.round(a.fadeOutSec * fps) : 0;
        const baseVolume = a.volume ?? 1.0;

        return (
          <Sequence key={`audio-${i}`} from={startFrame} layout="none">
            <Audio
              src={audioSrc}
              volume={(f) => {
                let vol = baseVolume;
                if (fadeInFrames > 0 && f < fadeInFrames) {
                  vol *= interpolate(f, [0, fadeInFrames], [0, 1], {
                    extrapolateRight: "clamp",
                  });
                }
                if (fadeOutFrames > 0 && a.durationSec) {
                  const totalFrames = Math.round(a.durationSec * fps);
                  const fadeStart = totalFrames - fadeOutFrames;
                  if (f > fadeStart) {
                    vol *= interpolate(f, [fadeStart, totalFrames], [1, 0], {
                      extrapolateLeft: "clamp",
                    });
                  }
                }
                return vol;
              }}
              loop={a.loop}
              startFrom={a.trimStartSec ? Math.round(a.trimStartSec * fps) : undefined}
            />
          </Sequence>
        );
      })}
    </>
  );
};
