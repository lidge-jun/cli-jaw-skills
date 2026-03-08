import React from "react";
import { Composition, getInputProps } from "remotion";
import { PRESETS } from "./presets";
import { TimelineRenderer } from "./timeline/renderer";
import { computeTiming } from "./timeline/schema";
import type { Timeline, PresetKey } from "./timeline/schema";

const defaultTimeline: Timeline = {
  meta: { title: "Default", preset: "Landscape-1080p", totalDurationSec: 5 },
  elements: [
    {
      type: "title",
      durationSec: 5,
      props: { title: "Hello from cli-jaw", subtitle: "Remotion Video Pipeline" },
      transition: { type: "fade", durationSec: 0.5 },
    },
  ],
  audio: [],
};

export const RemotionRoot: React.FC = () => {
  const props = getInputProps() as { timeline?: Timeline };

  const timeline = props.timeline || defaultTimeline;
  const presetKey = (timeline.meta?.preset || "Landscape-1080p") as PresetKey;
  const preset = PRESETS[presetKey] || PRESETS["Landscape-1080p"];
  const fps = timeline.meta?.fps || preset.fps;

  // Auto-calculate duration from elements (accounting for transition overlaps)
  const { totalDurationSec: computed } = computeTiming(timeline.elements);
  const totalDurationSec = timeline.meta?.totalDurationSec || computed || 5;
  const durationInFrames = Math.round(totalDurationSec * fps);

  return (
    <Composition
      id="TimelineVideo"
      component={() => <TimelineRenderer timeline={timeline} />}
      durationInFrames={durationInFrames}
      fps={fps}
      width={preset.width}
      height={preset.height}
      defaultProps={{}}
    />
  );
};
