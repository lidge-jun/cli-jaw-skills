import React from "react";
import {
  TitleSlide,
  ContentSlide,
  CodeSlide,
  DiagramSlide,
  StatSlide,
  QuoteSlide,
  ComparisonSlide,
  VideoSlide,
  GifSlide,
  LottieSlide,
  ChartSlide,
  Caption,
} from "../components";
import type { TimelineElement } from "./schema";
import type { Theme } from "../theme";

type Props = {
  element: TimelineElement;
  theme: Theme;
};

export const ElementRouter: React.FC<Props> = ({ element, theme }) => {
  const p = element.props as Record<string, unknown>;
  const anim = element.animation;

  switch (element.type) {
    case "title":
      return (
        <TitleSlide
          title={String(p.title || "")}
          subtitle={p.subtitle ? String(p.subtitle) : undefined}
          designTheme={theme}
          animation={anim}
        />
      );
    case "content":
      return (
        <ContentSlide
          header={String(p.header || "")}
          content={p.content ? String(p.content) : undefined}
          bulletPoints={
            Array.isArray(p.bulletPoints)
              ? p.bulletPoints.map(String)
              : undefined
          }
          designTheme={theme}
          animation={anim}
        />
      );
    case "code":
      return (
        <CodeSlide
          code={String(p.code || "")}
          language={p.language ? String(p.language) : undefined}
          title={p.title ? String(p.title) : undefined}
          designTheme={theme}
          animation={anim}
        />
      );
    case "diagram":
    case "image":
      return (
        <DiagramSlide
          src={p.src ? String(p.src) : undefined}
          title={p.title ? String(p.title) : undefined}
          caption={p.caption ? String(p.caption) : undefined}
          fit={(p.fit as "cover" | "contain" | "fill") || "contain"}
          designTheme={theme}
          animation={anim}
        />
      );
    case "stat":
      return (
        <StatSlide
          stats={
            Array.isArray(p.stats)
              ? (p.stats as Array<{
                  value: number;
                  label: string;
                  prefix?: string;
                  suffix?: string;
                  decimals?: number;
                  trend?: "up" | "down" | "neutral";
                }>)
              : []
          }
          title={p.title ? String(p.title) : undefined}
          designTheme={theme}
          animation={anim}
        />
      );
    case "quote":
      return (
        <QuoteSlide
          quote={String(p.quote || "")}
          author={p.author ? String(p.author) : undefined}
          source={p.source ? String(p.source) : undefined}
          designTheme={theme}
          animation={anim}
        />
      );
    case "comparison":
      return (
        <ComparisonSlide
          title={p.title ? String(p.title) : undefined}
          left={
            p.left as { label: string; items: string[]; accent?: string }
          }
          right={
            p.right as { label: string; items: string[]; accent?: string }
          }
          designTheme={theme}
          animation={anim}
        />
      );
    case "video":
      return (
        <VideoSlide
          src={String(p.src || "")}
          title={p.title ? String(p.title) : undefined}
          caption={p.caption ? String(p.caption) : undefined}
          loop={p.loop === true}
          startFrom={typeof p.startFrom === "number" ? p.startFrom : undefined}
          playbackRate={typeof p.playbackRate === "number" ? p.playbackRate : undefined}
          fit={(p.fit as "cover" | "contain") || "contain"}
          designTheme={theme}
          animation={anim}
        />
      );
    case "gif":
      return (
        <GifSlide
          src={String(p.src || "")}
          title={p.title ? String(p.title) : undefined}
          caption={p.caption ? String(p.caption) : undefined}
          fit={(p.fit as "cover" | "contain") || "contain"}
          designTheme={theme}
          animation={anim}
        />
      );
    case "lottie":
      return (
        <LottieSlide
          src={String(p.src || "")}
          title={p.title ? String(p.title) : undefined}
          caption={p.caption ? String(p.caption) : undefined}
          loop={p.loop === true}
          playbackRate={typeof p.playbackRate === "number" ? p.playbackRate : 1}
          designTheme={theme}
          animation={anim}
        />
      );
    case "chart":
      return (
        <ChartSlide
          chartType={(p.chartType as "bar" | "pie" | "line") || "bar"}
          data={
            p.data as {
              labels: string[];
              datasets: Array<{
                label: string;
                data: number[];
                color?: string;
              }>;
            }
          }
          title={p.title ? String(p.title) : undefined}
          showLegend={p.showLegend !== false}
          designTheme={theme}
          animation={anim}
        />
      );
    default:
      return (
        <TitleSlide
          title={`Unknown type: ${element.type}`}
          designTheme={theme}
        />
      );
  }
};
