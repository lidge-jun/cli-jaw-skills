import React from "react";
import {
  AbsoluteFill,
  spring,
  useCurrentFrame,
  useVideoConfig,
  interpolate,
} from "remotion";
import type { Theme } from "../theme";
import type { AnimationConfig } from "../timeline/schema";
import { useEntranceAnimation } from "./useAnimation";

type ChartType = "bar" | "pie" | "line";

type ChartData = {
  labels: string[];
  datasets: Array<{
    label: string;
    data: number[];
    color?: string;
  }>;
};

type ChartSlideProps = {
  chartType: ChartType;
  data: ChartData;
  title?: string;
  showLegend?: boolean;
  designTheme: Theme;
  animation?: AnimationConfig;
};

export const ChartSlide: React.FC<ChartSlideProps> = ({
  chartType,
  data,
  title,
  showLegend = true,
  designTheme: t,
  animation,
}) => {
  const frame = useCurrentFrame();
  const { fps, durationInFrames } = useVideoConfig();

  const entrance = useEntranceAnimation(animation);

  const titleProgress = spring({ frame, fps, config: { damping: 100 } });
  const cardProgress = spring({
    frame: Math.max(0, frame - 4),
    fps,
    config: { damping: 80 },
  });

  const exitFade = interpolate(
    frame,
    [durationInFrames - 10, durationInFrames],
    [1, 0],
    { extrapolateLeft: "clamp", extrapolateRight: "clamp" },
  );

  const defaultColors = [
    "#22D3EE",
    "#A78BFA",
    "#34D399",
    "#FB923C",
    "#F87171",
    "#FBBF24",
  ];

  const dataset = data.datasets[0];
  if (!dataset) return null;
  const maxValue = Math.max(...dataset.data, 1);

  const chartWidth = 1000;
  const chartHeight = 480;

  const renderBarChart = () => {
    const barCount = dataset.data.length;
    const barGap = 16;
    const barWidth = Math.max(
      12,
      (chartWidth - barGap * (barCount + 1)) / barCount,
    );

    return (
      <svg width={chartWidth} height={chartHeight + 40} viewBox={`0 0 ${chartWidth} ${chartHeight + 40}`}>
        {/* Grid lines */}
        {[0, 0.25, 0.5, 0.75, 1].map((pct, i) => (
          <line
            key={i}
            x1={0}
            y1={chartHeight * (1 - pct)}
            x2={chartWidth}
            y2={chartHeight * (1 - pct)}
            stroke={`${t.color.textMuted}20`}
            strokeWidth={1}
          />
        ))}
        {dataset.data.map((value, i) => {
          const delay = 10 + i * 6;
          const barProgress = spring({
            frame: Math.max(0, frame - delay),
            fps,
            config: { damping: 15, stiffness: 200 },
          });
          const barHeight = interpolate(
            barProgress,
            [0, 1],
            [0, (value / maxValue) * chartHeight],
          );
          const x = barGap + i * (barWidth + barGap);
          const color = dataset.color || defaultColors[i % defaultColors.length];

          return (
            <g key={i}>
              <rect
                x={x}
                y={chartHeight - barHeight}
                width={barWidth}
                height={barHeight}
                rx={4}
                fill={color}
                opacity={0.9}
              />
              <text
                x={x + barWidth / 2}
                y={chartHeight + 28}
                textAnchor="middle"
                fontSize={24}
                fill={t.color.textMuted}
                fontFamily={t.font.body}
                fontWeight={400}
                opacity={barProgress}
              >
                {data.labels[i] || ""}
              </text>
            </g>
          );
        })}
      </svg>
    );
  };

  const renderPieChart = () => {
    const total = dataset.data.reduce((s, v) => s + v, 0) || 1;
    const sweepProgress = spring({
      frame: Math.max(0, frame - 10),
      fps,
      config: { damping: 200 },
    });
    const totalAngle = interpolate(sweepProgress, [0, 1], [0, 360]);
    const cx = 200;
    const cy = 200;
    const r = 160;

    let cumAngle = -90;
    const slices = dataset.data.map((value, i) => {
      const sliceAngle = (value / total) * totalAngle;
      const startAngle = cumAngle;
      cumAngle += sliceAngle;
      const endAngle = cumAngle;

      const startRad = (startAngle * Math.PI) / 180;
      const endRad = (endAngle * Math.PI) / 180;

      const x1 = cx + r * Math.cos(startRad);
      const y1 = cy + r * Math.sin(startRad);
      const x2 = cx + r * Math.cos(endRad);
      const y2 = cy + r * Math.sin(endRad);

      const largeArc = sliceAngle > 180 ? 1 : 0;
      const d = `M ${cx} ${cy} L ${x1} ${y1} A ${r} ${r} 0 ${largeArc} 1 ${x2} ${y2} Z`;
      const color = defaultColors[i % defaultColors.length];

      return <path key={i} d={d} fill={color} opacity={0.85} />;
    });

    return (
      <svg width={400} height={400} viewBox="0 0 400 400">
        {slices}
      </svg>
    );
  };

  const renderLineChart = () => {
    const lineProgress = spring({
      frame: Math.max(0, frame - 10),
      fps,
      config: { damping: 200 },
    });
    const pointCount = dataset.data.length;
    const stepX = chartWidth / Math.max(pointCount - 1, 1);

    const points = dataset.data.map((value, i) => ({
      x: i * stepX,
      y: chartHeight - (value / maxValue) * chartHeight,
    }));

    const pathData = points
      .map((p, i) => `${i === 0 ? "M" : "L"} ${p.x} ${p.y}`)
      .join(" ");

    // Approximate path length
    let pathLength = 0;
    for (let i = 1; i < points.length; i++) {
      const dx = points[i].x - points[i - 1].x;
      const dy = points[i].y - points[i - 1].y;
      pathLength += Math.sqrt(dx * dx + dy * dy);
    }

    const color = dataset.color || defaultColors[0];

    return (
      <svg width={chartWidth} height={chartHeight + 40} viewBox={`0 0 ${chartWidth} ${chartHeight + 40}`}>
        {/* Grid */}
        {[0, 0.25, 0.5, 0.75, 1].map((pct, i) => (
          <line
            key={i}
            x1={0}
            y1={chartHeight * (1 - pct)}
            x2={chartWidth}
            y2={chartHeight * (1 - pct)}
            stroke={`${t.color.textMuted}20`}
            strokeWidth={1}
          />
        ))}
        <path
          d={pathData}
          fill="none"
          stroke={color}
          strokeWidth={3}
          strokeLinecap="round"
          strokeLinejoin="round"
          strokeDasharray={pathLength}
          strokeDashoffset={pathLength * (1 - lineProgress)}
        />
        {/* Dots */}
        {points.map((p, i) => {
          const dotDelay = 10 + i * 4;
          const dotProg = spring({
            frame: Math.max(0, frame - dotDelay),
            fps,
            config: { damping: 15, stiffness: 200 },
          });
          return (
            <circle
              key={i}
              cx={p.x}
              cy={p.y}
              r={5 * dotProg}
              fill={color}
              opacity={dotProg}
            />
          );
        })}
        {/* Labels */}
        {data.labels.map((label, i) => (
          <text
            key={i}
            x={i * stepX}
            y={chartHeight + 28}
            textAnchor="middle"
            fontSize={24}
            fill={t.color.textMuted}
            fontFamily={t.font.body}
            fontWeight={400}
          >
            {label}
          </text>
        ))}
      </svg>
    );
  };

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
            padding: "40px 48px",
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
                marginBottom: 28,
                opacity: titleProgress,
                letterSpacing: "-0.02em",
              }}
            >
              {title}
            </div>
          )}
          {chartType === "bar" && renderBarChart()}
          {chartType === "pie" && renderPieChart()}
          {chartType === "line" && renderLineChart()}
          {showLegend && data.datasets.length > 1 && (
            <div
              style={{
                display: "flex",
                gap: 24,
                marginTop: 20,
                flexWrap: "wrap",
                justifyContent: "center",
              }}
            >
              {data.labels.map((label, i) => (
                <div
                  key={i}
                  style={{
                    display: "flex",
                    alignItems: "center",
                    gap: 8,
                    fontSize: 20,
                    fontWeight: 400,
                    color: t.color.textMuted,
                  }}
                >
                  <div
                    style={{
                      width: 10,
                      height: 10,
                      borderRadius: "50%",
                      backgroundColor:
                        defaultColors[i % defaultColors.length],
                    }}
                  />
                  {label}
                </div>
              ))}
            </div>
          )}
        </div>
      </AbsoluteFill>
    </AbsoluteFill>
  );
};
