import React from "react";
import { useVideoConfig, Audio, Sequence, staticFile } from "remotion";
import { TransitionSeries, linearTiming } from "@remotion/transitions";
import { fade } from "@remotion/transitions/fade";
import { slide } from "@remotion/transitions/slide";
import { ElementRouter } from "./element-router";
import type { Timeline, TransitionConfig } from "./schema";
import { resolveTheme } from "../theme";

function resolveTransition(config: TransitionConfig) {
  switch (config.type) {
    case "slide":
      return slide({ direction: config.direction || "from-right" });
    case "fade":
    default:
      return fade();
  }
}

type Props = {
  timeline: Timeline;
};

export const TimelineRenderer: React.FC<Props> = ({ timeline }) => {
  const { fps } = useVideoConfig();
  const theme = resolveTheme(timeline.meta);

  return (
    <>
      <TransitionSeries>
        {timeline.elements.map((el, i) => {
          const durationInFrames = Math.round(el.durationSec * fps);
          const transitionFrames = el.transition && el.transition.type !== "none"
            ? Math.round((el.transition.durationSec ?? 0.5) * fps)
            : 0;

          return (
            <React.Fragment key={i}>
              <TransitionSeries.Sequence durationInFrames={durationInFrames}>
                <ElementRouter element={el} theme={theme} />
              </TransitionSeries.Sequence>
              {transitionFrames > 0 && el.transition && (
                <TransitionSeries.Transition
                  presentation={resolveTransition(el.transition)}
                  timing={linearTiming({ durationInFrames: transitionFrames })}
                />
              )}
            </React.Fragment>
          );
        })}
      </TransitionSeries>
      {timeline.audio?.map((a, i) => {
        if (!a.src) return null;
        const startFrame = Math.round((a.startSec ?? 0) * fps);
        const isLocal = !a.src.startsWith("http://") && !a.src.startsWith("https://");
        return (
          <Sequence key={`audio-${i}`} from={startFrame} layout="none">
            <Audio
              src={isLocal ? staticFile(a.src) : a.src}
              volume={a.volume ?? 1.0}
            />
          </Sequence>
        );
      })}
    </>
  );
};
