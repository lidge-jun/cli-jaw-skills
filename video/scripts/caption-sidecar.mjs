import { writeFileSync } from "node:fs";

export function asNumber(value, fallback = 0) {
  const n = Number(value);
  return Number.isFinite(n) ? n : fallback;
}

export function cleanText(text) {
  return String(text ?? "").replace(/\s+/g, " ").trim();
}

export function formatTimestamp(seconds, separator = ",") {
  const totalMs = Math.max(0, Math.round(asNumber(seconds) * 1000));
  const ms = totalMs % 1000;
  const totalSec = Math.floor(totalMs / 1000);
  const s = totalSec % 60;
  const totalMin = Math.floor(totalSec / 60);
  const m = totalMin % 60;
  const h = Math.floor(totalMin / 60);
  return `${String(h).padStart(2, "0")}:${String(m).padStart(2, "0")}:${String(s).padStart(2, "0")}${separator}${String(ms).padStart(3, "0")}`;
}

export function writeSrt(entries) {
  return entries.map((cue, i) => [
    String(i + 1),
    `${formatTimestamp(cue.start, ",")} --> ${formatTimestamp(cue.end, ",")}`,
    cue.speaker ? `${cue.speaker}: ${cue.text}` : cue.text,
    "",
  ].join("\n")).join("\n");
}

export function writeVtt(entries) {
  return [
    "WEBVTT",
    "",
    ...entries.map((cue) => [
      `${formatTimestamp(cue.start, ".")} --> ${formatTimestamp(cue.end, ".")}`,
      cue.speaker ? `${cue.speaker}: ${cue.text}` : cue.text,
      "",
    ].join("\n")),
  ].join("\n");
}

export function normalizeCaptionEntry(cue, index = 0) {
  const start = asNumber(cue.start ?? cue.startSec, 0);
  const end = asNumber(cue.end ?? cue.endSec, start);
  const entry = {
    id: cleanText(cue.id) || `cue-${String(index + 1).padStart(3, "0")}`,
    start,
    end,
    text: cleanText(cue.text ?? cue.caption ?? cue.narration),
  };
  for (const key of [
    "speaker",
    "style",
    "elementId",
    "localStart",
    "localEnd",
    "draftElementDurationSec",
  ]) {
    if (cue[key] !== undefined && cue[key] !== null && cue[key] !== "") {
      entry[key] = typeof cue[key] === "number" ? cue[key] : cue[key];
    }
  }
  if (Array.isArray(cue.words)) entry.words = cue.words;
  return entry;
}

export function computeElementStarts(elements) {
  const starts = [];
  let cursor = 0;
  for (let i = 0; i < elements.length; i++) {
    starts.push(cursor);
    const nextTransition = i < elements.length - 1
      ? asNumber(elements[i + 1]?.transition?.durationSec, 0.5)
      : 0;
    cursor += asNumber(elements[i]?.durationSec, 0) - nextTransition;
  }
  return starts;
}

function clamp(value, min, max) {
  return Math.min(Math.max(value, min), max);
}

export function alignCaptionEntriesToTimeline(entries, elements, options = {}) {
  const scaleLocalTime = options.scaleLocalTime !== false;
  const starts = computeElementStarts(elements);
  const elementIndex = new Map(elements.map((el, index) => [String(el.id ?? `cut-${index}`), { el, index }]));
  const warnings = [];

  const aligned = entries.map((raw, index) => {
    const cue = normalizeCaptionEntry(raw, index);
    if (!cue.elementId) return cue;

    const match = elementIndex.get(String(cue.elementId));
    if (!match) {
      warnings.push(`cue ${cue.id}: missing elementId ${cue.elementId}; preserved absolute timing`);
      return cue;
    }

    const finalDuration = Math.max(0.001, asNumber(match.el.durationSec, 0.001));
    const draftDuration = asNumber(cue.draftElementDurationSec, 0);
    const scale = scaleLocalTime && draftDuration > 0 ? finalDuration / draftDuration : 1;
    const localStart = asNumber(cue.localStart, Math.max(0, cue.start - starts[match.index]));
    const localEnd = asNumber(cue.localEnd, Math.max(localStart + 0.1, cue.end - starts[match.index]));
    const start = starts[match.index] + clamp(localStart * scale, 0, finalDuration);
    const end = starts[match.index] + clamp(localEnd * scale, 0.1, finalDuration);

    return {
      ...cue,
      start: Number(start.toFixed(3)),
      end: Number(Math.max(start + 0.1, end).toFixed(3)),
    };
  }).sort((a, b) => a.start - b.start);

  const validation = validateCaptionEntries(aligned);
  return {
    entries: aligned,
    warnings: [...warnings, ...validation.warnings],
    valid: validation.valid,
  };
}

export function validateCaptionEntries(entries, duration = 0) {
  const warnings = [];
  const errors = [];
  let previousEnd = 0;
  entries.forEach((cue, index) => {
    if (!cleanText(cue.text)) errors.push(`cue ${index + 1}: empty text`);
    if (!Number.isFinite(cue.start) || cue.start < 0) errors.push(`cue ${index + 1}: invalid start`);
    if (!Number.isFinite(cue.end) || cue.end <= cue.start) errors.push(`cue ${index + 1}: end must be after start`);
    if (cue.start < previousEnd - 0.05) warnings.push(`cue ${index + 1}: overlaps previous cue`);
    if (duration && cue.end > duration + 0.25) warnings.push(`cue ${index + 1}: ends after duration`);
    previousEnd = Math.max(previousEnd, cue.end);
  });
  return { valid: errors.length === 0, errors, warnings };
}

export function writeCaptionFiles(outputPaths, track) {
  writeFileSync(outputPaths.remotion, JSON.stringify(track, null, 2));
  writeFileSync(outputPaths.srt, writeSrt(track.entries));
  writeFileSync(outputPaths.vtt, writeVtt(track.entries));
}
