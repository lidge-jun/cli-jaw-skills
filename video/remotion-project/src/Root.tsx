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
  const captionEntries = timeline.meta?.captions?.entries || timeline.meta?.captions?.track?.entries || [];
  const captionEndSec = captionEntries.reduce((max, cue) => Math.max(max, cue.end || 0), 0);
  const audioEndSec = (timeline.audio || []).reduce((max, audio) => {
    if (!audio.durationSec) return max;
    return Math.max(max, (audio.startSec || 0) + audio.durationSec);
  }, 0);
  const totalDurationSec = Math.max(timeline.meta?.totalDurationSec || 0, computed || 0, captionEndSec, audioEndSec, 5);
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
