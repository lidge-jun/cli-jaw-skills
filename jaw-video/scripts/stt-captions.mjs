#!/usr/bin/env node
/**
 * Progrok-first STT/caption helper.
 *
 * Outputs:
 * - transcript.raw.json
 * - transcript.normalized.json
 * - captions.srt
 * - captions.vtt
 * - captions.remotion.json
 * - qa-report.md
 */
import { execFileSync } from "node:child_process";
import { existsSync, mkdirSync, readFileSync, writeFileSync } from "node:fs";
import { basename, extname, join, resolve } from "node:path";
import { parseArgs } from "node:util";

const { values } = parseArgs({
  options: {
    input: { type: "string" },
    transcript: { type: "string" },
    "source-audio": { type: "string" },
    output: { type: "string", short: "o", default: "/tmp/video-stt" },
    language: { type: "string" },
    diarize: { type: "boolean", default: false },
    multichannel: { type: "boolean", default: false },
    "word-timestamps": { type: "boolean", default: true },
    keyterm: { type: "string", multiple: true, default: [] },
    endpoint: { type: "string", default: "http://127.0.0.1:18645/v1/stt" },
    "max-cue-duration": { type: "string", default: "3.2" },
    "max-words-per-cue": { type: "string", default: "7" },
  },
});

function usage() {
  console.error(`Usage:
  node stt-captions.mjs --input input.mp4 --output /tmp/video-stt --language ko --diarize --word-timestamps
  node stt-captions.mjs --transcript transcript.raw.json --source-audio audio.wav --output /tmp/video-stt`);
}

if (!values.input && !values.transcript) {
  usage();
  process.exit(1);
}

const outputDir = resolve(values.output);
mkdirSync(outputDir, { recursive: true });

const maxCueDuration = Number(values["max-cue-duration"]) || 3.2;
const maxWordsPerCue = Number(values["max-words-per-cue"]) || 7;

function run(cmd, args, opts = {}) {
  try {
    return execFileSync(cmd, args, {
      encoding: "utf8",
      stdio: ["ignore", "pipe", "pipe"],
      ...opts,
    }).trim();
  } catch (error) {
    const stdout = typeof error?.stdout === "string" ? error.stdout : "";
    const stderr = typeof error?.stderr === "string" ? error.stderr : "";
    throw new Error(`${cmd} ${args.join(" ")} failed\n${stdout}\n${stderr}`.trim());
  }
}

function extractAudio(inputPath) {
  const audioPath = join(outputDir, "audio.wav");
  run("ffmpeg", [
    "-hide_banner", "-loglevel", "error", "-y",
    "-i", inputPath,
    "-vn",
    "-ac", values.multichannel ? "2" : "1",
    "-ar", "16000",
    "-c:a", "pcm_s16le",
    audioPath,
  ]);
  return audioPath;
}

function callProgrokStt(audioPath) {
  const args = ["-sS", "--fail", "--max-time", "180", values.endpoint, "-F", `file=@${audioPath}`];
  if (values.language) args.push("-F", `language=${values.language}`);
  if (values.diarize) args.push("-F", "diarize=true");
  if (values.multichannel) args.push("-F", "multichannel=true");
  if (values["word-timestamps"] !== false) args.push("-F", "word_timestamps=true");
  for (const term of values.keyterm || []) {
    if (String(term).trim()) args.push("-F", `keyterm=${term}`);
  }
  const raw = run("curl", args);
  return JSON.parse(raw);
}

function asNumber(value, fallback = 0) {
  const n = Number(value);
  return Number.isFinite(n) ? n : fallback;
}

function cleanText(text) {
  return String(text ?? "").replace(/\s+/g, " ").trim();
}

function normalizeWord(word) {
  return {
    start: asNumber(word.start ?? word.startSec ?? word.begin ?? word.offset, 0),
    end: asNumber(word.end ?? word.endSec ?? word.finish, 0),
    text: cleanText(word.text ?? word.word ?? word.token),
  };
}

function segmentWords(words, duration) {
  const normalized = words.map(normalizeWord).filter((w) => w.text && w.end > w.start);
  if (normalized.length === 0) return [];

  const cues = [];
  let current = [];
  for (const word of normalized) {
    const next = [...current, word];
    const start = next[0].start;
    const end = next[next.length - 1].end;
    const sentenceBreak = /[.!?。！？]$/.test(word.text);
    if (
      current.length > 0 &&
      (next.length > maxWordsPerCue || end - start > maxCueDuration)
    ) {
      cues.push(wordsToCue(current));
      current = [word];
    } else {
      current = next;
    }
    if (sentenceBreak && current.length > 0) {
      cues.push(wordsToCue(current));
      current = [];
    }
  }
  if (current.length > 0) cues.push(wordsToCue(current));

  return cues.map((cue, index) => ({
    ...cue,
    end: duration ? Math.min(cue.end, duration) : cue.end,
    id: `cue-${String(index + 1).padStart(3, "0")}`,
  }));
}

function wordsToCue(words) {
  return {
    start: words[0].start,
    end: words[words.length - 1].end,
    text: words.map((w) => w.text).join(" "),
    words,
  };
}

function normalizeCue(cue, index, duration) {
  const words = Array.isArray(cue.words) ? cue.words.map(normalizeWord).filter((w) => w.text) : undefined;
  const start = asNumber(cue.start ?? cue.startSec ?? cue.from, words?.[0]?.start ?? 0);
  const end = asNumber(cue.end ?? cue.endSec ?? cue.to, words?.at(-1)?.end ?? Math.min(start + 2.5, duration || start + 2.5));
  return {
    id: cleanText(cue.id) || `cue-${String(index + 1).padStart(3, "0")}`,
    start,
    end,
    text: cleanText(cue.text ?? cue.caption ?? cue.transcript),
    speaker: cue.speaker ? cleanText(cue.speaker) : undefined,
    style: cue.style ? cleanText(cue.style) : undefined,
    words,
  };
}

function normalizeTranscript(raw, sourceAudio, sourceMedia) {
  const duration = asNumber(raw.duration ?? raw.durationSec, 0);
  let entries = [];

  if (Array.isArray(raw.entries)) {
    entries = raw.entries.map((cue, i) => normalizeCue(cue, i, duration));
  } else if (Array.isArray(raw.segments)) {
    entries = raw.segments.map((cue, i) => normalizeCue(cue, i, duration));
  } else if (Array.isArray(raw.captions)) {
    entries = raw.captions.map((cue, i) => normalizeCue(cue, i, duration));
  } else if (Array.isArray(raw.words)) {
    entries = segmentWords(raw.words, duration);
  } else if (raw.text) {
    entries = [{
      id: "cue-001",
      start: 0,
      end: duration || 3,
      text: cleanText(raw.text),
    }];
  }

  entries = entries
    .filter((cue) => cue.text && cue.end > cue.start)
    .sort((a, b) => a.start - b.start)
    .map((cue, index) => ({ ...cue, id: cue.id || `cue-${String(index + 1).padStart(3, "0")}` }));

  return {
    language: raw.language || values.language || "unknown",
    sourceAudio,
    sourceMedia,
    duration: duration || (entries.length ? entries.at(-1).end : 0),
    text: cleanText(raw.text || entries.map((cue) => cue.text).join(" ")),
    segments: entries,
  };
}

function fmtTime(seconds, separator) {
  const totalMs = Math.max(0, Math.round(seconds * 1000));
  const ms = totalMs % 1000;
  const totalSec = Math.floor(totalMs / 1000);
  const s = totalSec % 60;
  const totalMin = Math.floor(totalSec / 60);
  const m = totalMin % 60;
  const h = Math.floor(totalMin / 60);
  return `${String(h).padStart(2, "0")}:${String(m).padStart(2, "0")}:${String(s).padStart(2, "0")}${separator}${String(ms).padStart(3, "0")}`;
}

function writeSrt(entries) {
  return entries.map((cue, i) => [
    String(i + 1),
    `${fmtTime(cue.start, ",")} --> ${fmtTime(cue.end, ",")}`,
    cue.speaker ? `${cue.speaker}: ${cue.text}` : cue.text,
    "",
  ].join("\n")).join("\n");
}

function writeVtt(entries) {
  return `WEBVTT\n\n${entries.map((cue) => [
    `${fmtTime(cue.start, ".")} --> ${fmtTime(cue.end, ".")}`,
    cue.speaker ? `${cue.speaker}: ${cue.text}` : cue.text,
    "",
  ].join("\n")).join("\n")}`;
}

function validateEntries(entries, duration) {
  const errors = [];
  const warnings = [];
  let previousEnd = 0;
  entries.forEach((cue, index) => {
    if (cue.start < 0) errors.push(`cue ${index + 1}: starts before 0`);
    if (cue.end <= cue.start) errors.push(`cue ${index + 1}: end must be after start`);
    if (duration && cue.end > duration + 0.25) warnings.push(`cue ${index + 1}: ends after reported duration`);
    if (index > 0 && cue.start < previousEnd - 0.03) warnings.push(`cue ${index + 1}: overlaps previous cue`);
    if (cue.text.length > 84) warnings.push(`cue ${index + 1}: long caption (${cue.text.length} chars)`);
    previousEnd = Math.max(previousEnd, cue.end);
  });
  return { valid: errors.length === 0, errors, warnings };
}

function writeQaReport(normalized, validation, paths) {
  const lines = [
    "# STT Caption QA",
    "",
    `- language: ${normalized.language}`,
    `- duration: ${normalized.duration.toFixed(2)}s`,
    `- cues: ${normalized.segments.length}`,
    `- valid: ${validation.valid}`,
    `- raw: ${paths.raw}`,
    `- normalized: ${paths.normalized}`,
    `- remotion: ${paths.remotion}`,
    `- srt: ${paths.srt}`,
    `- vtt: ${paths.vtt}`,
    "",
    "## Warnings",
    "",
    ...(validation.warnings.length ? validation.warnings.map((w) => `- ${w}`) : ["- none"]),
    "",
    "## Errors",
    "",
    ...(validation.errors.length ? validation.errors.map((e) => `- ${e}`) : ["- none"]),
  ];
  return `${lines.join("\n")}\n`;
}

async function main() {
  const sourceMedia = values.input ? resolve(values.input) : undefined;
  const sourceAudio = values["source-audio"]
    ? resolve(values["source-audio"])
    : sourceMedia
      ? extractAudio(sourceMedia)
      : undefined;

  let raw;
  if (values.transcript) {
    raw = JSON.parse(readFileSync(resolve(values.transcript), "utf8"));
  } else {
    if (!sourceAudio || !existsSync(sourceAudio)) throw new Error("Audio source missing after extraction");
    raw = callProgrokStt(sourceAudio);
  }

  const normalized = normalizeTranscript(raw, sourceAudio, sourceMedia);
  const validation = validateEntries(normalized.segments, normalized.duration);
  const remotion = {
    language: normalized.language,
    sourceAudio: normalized.sourceAudio,
    sourceMedia: normalized.sourceMedia,
    entries: normalized.segments,
  };

  const stem = sourceMedia
    ? basename(sourceMedia, extname(sourceMedia))
    : values.transcript
      ? basename(values.transcript, extname(values.transcript))
      : "captions";

  const paths = {
    raw: join(outputDir, "transcript.raw.json"),
    normalized: join(outputDir, "transcript.normalized.json"),
    remotion: join(outputDir, "captions.remotion.json"),
    srt: join(outputDir, `${stem}.srt`),
    vtt: join(outputDir, `${stem}.vtt`),
    qa: join(outputDir, "qa-report.md"),
  };

  writeFileSync(paths.raw, JSON.stringify(raw, null, 2));
  writeFileSync(paths.normalized, JSON.stringify(normalized, null, 2));
  writeFileSync(paths.remotion, JSON.stringify(remotion, null, 2));
  writeFileSync(paths.srt, writeSrt(normalized.segments));
  writeFileSync(paths.vtt, writeVtt(normalized.segments));
  writeFileSync(paths.qa, writeQaReport(normalized, validation, paths));

  const result = {
    status: validation.valid ? "succeeded" : "failed",
    outputDir,
    sourceAudio,
    cueCount: normalized.segments.length,
    duration: normalized.duration,
    paths,
    validation,
  };

  console.log(JSON.stringify(result, null, 2));
  process.exit(validation.valid ? 0 : 1);
}

main().catch((error) => {
  console.error(`[stt-captions] ${error.message}`);
  process.exit(1);
});
