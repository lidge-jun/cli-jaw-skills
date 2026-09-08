#!/usr/bin/env node
/**
 * Script-first TTS caption helper.
 *
 * Outputs:
 * - narration.normalized.json
 * - captions.remotion.json
 * - captions.srt
 * - captions.vtt
 * - timeline.draft.json
 * - qa-report.md
 *
 * Optional:
 * - captions.aligned.remotion.json when --align-timeline is provided
 */
import { existsSync, mkdirSync, readFileSync, writeFileSync } from "node:fs";
import { basename, join, resolve } from "node:path";
import { parseArgs } from "node:util";
import {
  alignCaptionEntriesToTimeline,
  cleanCaptionText,
  cleanText,
  computeElementStarts,
  validateCaptionEntries,
  writeCaptionFiles,
} from "./caption-sidecar.mjs";

const { values } = parseArgs({
  options: {
    script: { type: "string" },
    output: { type: "string", short: "o", default: "/tmp/video-tts-captions" },
    timeline: { type: "string" },
    preset: { type: "string" },
    style: { type: "string", default: "bottom-center" },
    "font-size": { type: "string" },
    "caption-max-line-chars": { type: "string", default: "24" },
    "caption-max-lines": { type: "string", default: "2" },
    "words-per-minute": { type: "string", default: "145" },
    "min-cue-duration": { type: "string", default: "1.2" },
    "max-cue-duration": { type: "string", default: "3.8" },
    "align-timeline": { type: "string" },
    captions: { type: "string" },
  },
});

function usage() {
  console.error(`Usage:
  node scripts/tts-captions.mjs --script script.json --output /tmp/video-tts
  node scripts/tts-captions.mjs --script script.json --output /tmp/video-tts --align-timeline /tmp/video-tts/timeline.final.json`);
}

if (!values.script) {
  usage();
  process.exit(1);
}

const scriptPath = resolve(values.script);
if (!existsSync(scriptPath)) {
  throw new Error(`Script not found: ${scriptPath}`);
}

const outputDir = resolve(values.output);
mkdirSync(outputDir, { recursive: true });

const wpm = Number(values["words-per-minute"]) || 145;
const minCueDuration = Number(values["min-cue-duration"]) || 1.2;
const maxCueDuration = Number(values["max-cue-duration"]) || 3.8;
const captionMaxLineChars = Number(values["caption-max-line-chars"]) || 24;
const captionMaxLines = Number(values["caption-max-lines"]) || 2;

const CAPTION_TERM_MAP = [
  [/\bcli\s*jaw\b/gi, "cli-jaw"],
  [/클리\s*조|클리\s*죠|씨엘아이\s*조/gi, "cli-jaw"],
  [/\bprogrok\b/gi, "progrok"],
  [/프로그록|프로\s*그록/gi, "progrok"],
  [/\btts\b/gi, "TTS"],
  [/티\s*티\s*에스|티티에스/gi, "TTS"],
  [/\bstt\b/gi, "STT"],
  [/에스\s*티\s*티|에스티티/gi, "STT"],
  [/\bremotion\b/gi, "Remotion"],
  [/리모션/gi, "Remotion"],
  [/\bffmpeg\b/gi, "FFmpeg"],
  [/에프\s*에프\s*엠펙|에프에프엠펙|에프에프엠페그/gi, "FFmpeg"],
  [/\bffprobe\b/gi, "ffprobe"],
  [/에프\s*에프\s*프로브|에프에프프로브/gi, "ffprobe"],
  [/\bmp4\b/gi, "MP4"],
  [/엠\s*피\s*포|엠피포/gi, "MP4"],
  [/\baac\b/gi, "AAC"],
  [/에이\s*에이\s*씨|에이에이씨/gi, "AAC"],
  [/\boauth\b/gi, "OAuth"],
  [/오\s*어스|오어스/gi, "OAuth"],
];

function clamp(n, min, max) {
  return Math.min(Math.max(n, min), max);
}

function estimateDuration(text) {
  const value = cleanText(text);
  const latinWords = value.split(/\s+/).filter(Boolean).length;
  const cjkChars = (value.match(/[\u3131-\uD79D\u3040-\u30FF\u3400-\u9FFF]/g) || []).length;
  const units = Math.max(latinWords, cjkChars / 2.2, 1);
  return clamp((units / wpm) * 60 + 0.35, minCueDuration, maxCueDuration * 2);
}

function splitNarration(text) {
  const cleaned = cleanText(text);
  const parts = cleaned
    .split(/(?<=[.!?。！？])\s+|(?<=다\.)\s+|(?<=요\.)\s+/u)
    .map(cleanText)
    .filter(Boolean);
  return parts.length ? parts : [cleaned];
}

function applyCaptionTermMap(text) {
  return CAPTION_TERM_MAP.reduce((acc, [pattern, replacement]) => (
    acc.replace(pattern, replacement)
  ), cleanCaptionText(text));
}

function measureCaptionToken(token) {
  const cjk = (token.match(/[\u3131-\uD79D\u3040-\u30FF\u3400-\u9FFF]/g) || []).length;
  const latin = (token.match(/[A-Za-z0-9-]/g) || []).length;
  return cjk * 1.15 + latin * 0.62 + Math.max(0, token.length - cjk - latin) * 0.5;
}

function splitCaptionTokens(text) {
  return cleanCaptionText(text).split(/(\s+)/).filter((part) => part.length > 0);
}

function wrapCaptionLine(line, maxChars) {
  const tokens = splitCaptionTokens(line);
  const lines = [];
  let current = "";
  let currentWidth = 0;
  for (const token of tokens) {
    const normalizedToken = /^\s+$/.test(token) ? " " : token;
    const width = measureCaptionToken(normalizedToken);
    if (current && currentWidth + width > maxChars) {
      lines.push(current.trim());
      current = normalizedToken.trimStart();
      currentWidth = measureCaptionToken(current);
    } else {
      current += normalizedToken;
      currentWidth += width;
    }
  }
  if (current.trim()) lines.push(current.trim());
  return lines.length ? lines : [cleanText(line)];
}

function formatCaptionText(text) {
  const mapped = applyCaptionTermMap(text);
  const explicitLines = mapped.split("\n").flatMap((line) => wrapCaptionLine(line, captionMaxLineChars));
  if (explicitLines.length <= captionMaxLines) return explicitLines.join("\n");

  const merged = explicitLines.join(" ");
  const wrapped = wrapCaptionLine(merged, Math.ceil(measureCaptionToken(merged) / captionMaxLines));
  if (wrapped.length <= captionMaxLines) return wrapped.join("\n");

  const kept = wrapped.slice(0, captionMaxLines);
  kept[kept.length - 1] = [kept.at(-1), ...wrapped.slice(captionMaxLines)].join(" ");
  return kept.join("\n");
}

function normalizeScript(raw) {
  const beats = Array.isArray(raw.beats)
    ? raw.beats
    : Array.isArray(raw.elements)
      ? raw.elements
      : [];
  if (beats.length === 0) {
    throw new Error("script requires a non-empty beats[] or elements[] array");
  }

  const meta = {
    title: cleanText(raw.meta?.title) || cleanText(raw.title) || basename(scriptPath, ".json"),
    preset: values.preset || raw.meta?.preset || "Landscape-720p",
    fps: Number(raw.meta?.fps) || 30,
    ttsProvider: raw.meta?.ttsProvider,
    ttsVoice: raw.meta?.ttsVoice,
    ttsSpeed: raw.meta?.ttsSpeed,
    ttsLanguage: raw.meta?.ttsLanguage,
    theme: raw.meta?.theme,
  };

  const normalizedBeats = beats.map((beat, index) => {
    const id = cleanText(beat.id) || `beat-${String(index + 1).padStart(2, "0")}`;
    const narration = cleanText(beat.narration ?? beat.text ?? beat.caption);
    if (!narration) throw new Error(`beat ${id} requires narration/text`);
    const durationSec = Number(beat.durationSec) > 0 ? Number(beat.durationSec) : estimateDuration(narration);
    const captionText = cleanCaptionText(beat.captionText ?? beat.caption ?? narration);
    return {
      id,
      type: beat.type || "content",
      durationSec: Number(durationSec.toFixed(3)),
      narration,
      props: beat.props || {
        header: cleanText(beat.title) || id,
        body: narration,
      },
      transition: beat.transition || { type: "fade", durationSec: 0.45 },
      voiceControl: beat.voiceControl,
      captionStyle: beat.captionStyle,
      captionText,
      speaker: beat.speaker,
    };
  });

  return { meta, beats: normalizedBeats, captions: raw.meta?.captions || raw.captions || {} };
}

function buildCaptionEntries(beats) {
  const starts = computeElementStarts(beats);
  const entries = [];
  for (const [beatIndex, beat] of beats.entries()) {
    const chunks = splitNarration(beat.captionText || beat.narration);
    const totalChars = chunks.reduce((sum, chunk) => sum + Math.max(cleanText(chunk).length, 1), 0);
    const nextTransition = beatIndex < beats.length - 1
      ? Number(beats[beatIndex + 1]?.transition?.durationSec ?? 0.5)
      : 0;
    const captionDuration = Math.max(0.6, beat.durationSec - nextTransition);
    let localCursor = 0;
    chunks.forEach((chunk, chunkIndex) => {
      const ratio = Math.max(cleanText(chunk).length, 1) / totalChars;
      const localDuration = chunkIndex === chunks.length - 1
        ? captionDuration - localCursor
        : Math.max(0.6, captionDuration * ratio);
      const localStart = localCursor;
      const localEnd = Math.min(captionDuration, localStart + localDuration);
      entries.push({
        id: `${beat.id}-cue-${String(chunkIndex + 1).padStart(2, "0")}`,
        elementId: beat.id,
        localStart: Number(localStart.toFixed(3)),
        localEnd: Number(localEnd.toFixed(3)),
        draftElementDurationSec: beat.durationSec,
        start: Number((starts[beatIndex] + localStart).toFixed(3)),
        end: Number((starts[beatIndex] + localEnd).toFixed(3)),
        text: formatCaptionText(chunk),
        speaker: beat.speaker,
        style: beat.captionStyle,
      });
      localCursor = localEnd;
    });
  }
  return entries;
}

function buildTimeline(normalized, captionFileName) {
  const captions = {
    src: captionFileName,
    style: values.style || normalized.captions.style || "bottom-center",
    fontSize: values["font-size"] ? Number(values["font-size"]) : normalized.captions.fontSize,
    fontFamily: normalized.captions.fontFamily,
    backgroundColor: normalized.captions.backgroundColor,
  };
  Object.keys(captions).forEach((key) => captions[key] === undefined && delete captions[key]);

  return {
    meta: {
      ...normalized.meta,
      captions,
    },
    elements: normalized.beats.map((beat) => {
      const el = {
        id: beat.id,
        type: beat.type,
        durationSec: beat.durationSec,
        props: beat.props,
        narration: beat.narration,
        transition: beat.transition,
      };
      if (beat.voiceControl) el.voiceControl = beat.voiceControl;
      return el;
    }),
    audio: [],
  };
}

function writeQa(path, lines) {
  writeFileSync(path, `${lines.join("\n")}\n`);
}

function writeBaseArtifacts(normalized) {
  const captionFileName = "captions.remotion.json";
  const entries = buildCaptionEntries(normalized.beats);
  const duration = entries.length ? entries.at(-1).end : 0;
  const validation = validateCaptionEntries(entries, duration);
  const track = {
    language: normalized.meta.language || "ko",
    sourceScript: scriptPath,
    sourceRoute: "tts-captions",
    duration,
    entries,
  };
  const timeline = buildTimeline(normalized, captionFileName);
  const timelinePath = values.timeline ? resolve(values.timeline) : join(outputDir, "timeline.draft.json");

  writeFileSync(join(outputDir, "narration.normalized.json"), JSON.stringify(normalized, null, 2));
  writeCaptionFiles({
    remotion: join(outputDir, captionFileName),
    srt: join(outputDir, "captions.srt"),
    vtt: join(outputDir, "captions.vtt"),
  }, track);
  writeFileSync(timelinePath, JSON.stringify(timeline, null, 2));

  return { track, timeline, timelinePath, validation };
}

function alignIfRequested(baseTrack) {
  if (!values["align-timeline"]) return null;
  const finalTimelinePath = resolve(values["align-timeline"]);
  if (!existsSync(finalTimelinePath)) throw new Error(`Alignment timeline not found: ${finalTimelinePath}`);
  const captionsPath = values.captions ? resolve(values.captions) : join(outputDir, "captions.remotion.json");
  const sourceTrack = existsSync(captionsPath)
    ? JSON.parse(readFileSync(captionsPath, "utf8"))
    : baseTrack;
  const finalTimeline = JSON.parse(readFileSync(finalTimelinePath, "utf8"));
  const result = alignCaptionEntriesToTimeline(sourceTrack.entries || [], finalTimeline.elements || []);
  const alignedTrack = {
    ...sourceTrack,
    alignedToTimeline: finalTimelinePath,
    entries: result.entries,
  };
  writeCaptionFiles({
    remotion: join(outputDir, "captions.aligned.remotion.json"),
    srt: join(outputDir, "captions.aligned.srt"),
    vtt: join(outputDir, "captions.aligned.vtt"),
  }, alignedTrack);
  return result;
}

try {
  const raw = JSON.parse(readFileSync(scriptPath, "utf8"));
  const normalized = normalizeScript(raw);
  const { track, timelinePath, validation } = writeBaseArtifacts(normalized);
  const alignment = alignIfRequested(track);
  writeQa(join(outputDir, "qa-report.md"), [
    "# TTS Caption QA",
    "",
    `- source script: ${scriptPath}`,
    `- beats: ${normalized.beats.length}`,
    `- cues: ${track.entries.length}`,
    `- draft duration: ${track.duration.toFixed(2)}s`,
    `- timeline: ${timelinePath}`,
    `- validation: ${validation.valid ? "PASS" : "FAIL"}`,
    `- warnings: ${validation.warnings.length}`,
    ...(validation.warnings.map((warning) => `  - ${warning}`)),
    ...(alignment ? [
      `- alignment: ${alignment.valid ? "PASS" : "FAIL"}`,
      `- alignment warnings: ${alignment.warnings.length}`,
      ...alignment.warnings.map((warning) => `  - ${warning}`),
    ] : []),
  ]);
  console.log(JSON.stringify({
    status: "succeeded",
    outputDir,
    timelinePath,
    cueCount: track.entries.length,
    aligned: Boolean(alignment),
    valid: validation.valid && (!alignment || alignment.valid),
  }, null, 2));
} catch (error) {
  console.error(`[tts-captions] ${error.message}`);
  process.exit(1);
}
