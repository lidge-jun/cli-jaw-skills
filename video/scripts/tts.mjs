#!/usr/bin/env node
// TTS generator — multi-provider orchestrator
// Batch:   node tts.mjs --batch timeline.draft.json [--provider supertone]
// Single:  node tts.mjs --text "text" --output out.mp3 [--provider supertonic]
// List:    node tts.mjs --list-voices [--provider supertone]
import { fileURLToPath } from "url";
import { dirname, join, resolve } from "path";
import { writeFileSync, readFileSync, existsSync, mkdirSync } from "fs";
import { createHash } from "crypto";
import { execSync } from "child_process";

const __dirname = dirname(fileURLToPath(import.meta.url));
const remotionDir = join(__dirname, "..", "remotion-project");

async function loadProvider(name) {
  switch (name) {
    case "supertone":  return await import("./tts-providers/supertone.mjs");
    case "supertonic": return await import("./tts-providers/supertonic.mjs");
    case "gemini":
    default:           return await import("./tts-providers/gemini.mjs");
  }
}

// ── CLI args ──────────────────────────────────────────────
const args = process.argv.slice(2);
function getArg(name, fallback) {
  const idx = args.indexOf(`--${name}`);
  return idx !== -1 && args[idx + 1] ? args[idx + 1] : fallback;
}
function hasFlag(name) {
  return args.includes(`--${name}`);
}

const MODE_BATCH = hasFlag("batch");
const MODE_LIST = hasFlag("list-voices");
const text = getArg("text", null);
const textFile = getArg("textFile", null);
const batchFile = getArg("batch", null);
const output = getArg("output", null);
const cliProvider = getArg("provider", null);
const cliVoice = getArg("voice", null);
const concurrency = parseInt(getArg("concurrency", "3"), 10);
const maxRetries = parseInt(getArg("retries", "2"), 10);

// ── List voices mode ─────────────────────────────────────
if (MODE_LIST) {
  const mod = await loadProvider(cliProvider || "gemini");
  console.log(JSON.stringify(mod.VOICES, null, 2));
  process.exit(0);
}

// ── Validate ─────────────────────────────────────────────
if (!MODE_BATCH && !text && !textFile) {
  console.error("Usage:");
  console.error("  Single: node tts.mjs --text 'text' [--provider supertone] [--voice Andrew]");
  console.error("  Single: node tts.mjs --textFile narration.txt [--provider gemini]");
  console.error("  Batch:  node tts.mjs --batch timeline.draft.json [--provider supertone]");
  console.error("  List:   node tts.mjs --list-voices [--provider supertone]");
  process.exit(1);
}

// ── Cache key: sha256(provider|voice|narration|vcParams) ─
function cacheKey(providerName, voiceId, narration, vc = {}) {
  const vcStr = `${vc.style || ""}|${vc.pitch ?? ""}|${vc.pitchVariance ?? ""}|${vc.speed ?? ""}|${vc.tonePrompt || ""}`;
  return createHash("sha256")
    .update(`${providerName}|${voiceId}|${narration}|${vcStr}`)
    .digest("hex")
    .slice(0, 16);
}

// ── Shared: probe duration via ffprobe ───────────────────
function probeDuration(filePath) {
  try {
    const out = execSync(
      `ffprobe -v quiet -print_format json -show_format "${filePath}"`,
      { encoding: "utf-8" },
    );
    return parseFloat(JSON.parse(out).format?.duration || "0");
  } catch {
    return 0;
  }
}

// ══════════════════════════════════════════════════════════
//  SINGLE MODE
// ══════════════════════════════════════════════════════════
if (!MODE_BATCH) {
  const pName = cliProvider || "gemini";
  const mod = await loadProvider(pName);
  const vName = cliVoice || mod.DEFAULT_VOICE;
  let inputText = text;
  if (textFile) inputText = readFileSync(textFile, "utf-8");
  const outPath = resolve(output || `tts_output${mod.AUDIO_EXT}`);
  console.log(`[tts] provider=${pName} voice=${vName}`);
  const { duration: dur } = await mod.generate(inputText, outPath, { voice: vName });
  console.log(`[tts] done → ${outPath} (${dur.toFixed(1)}s)`);
  process.exit(0);
}

// ══════════════════════════════════════════════════════════
//  BATCH MODE — per-cut TTS from timeline.draft.json
// ══════════════════════════════════════════════════════════
const draft = JSON.parse(readFileSync(resolve(batchFile), "utf-8"));
const elements = draft.elements || [];
const ttsDir = join(remotionDir, "public", "tts");
mkdirSync(ttsDir, { recursive: true });

// Resolve provider + defaults
const pName = cliProvider || draft.meta?.ttsProvider || "gemini";
const mod = await loadProvider(pName);
const defaultVoice = cliVoice || draft.meta?.ttsVoice || mod.DEFAULT_VOICE;
const defaultSpeed = draft.meta?.ttsSpeed ?? 1.2;

console.log(`[tts-batch] provider=${pName} voice=${defaultVoice} speed=${defaultSpeed}`);

// Collect cuts that have narration
const cuts = elements
  .map((el, idx) => ({
    idx,
    id: el.id || `cut-${idx}`,
    narration: el.narration,
    durationSec: el.durationSec,
    voiceControl: el.voiceControl,
  }))
  .filter((c) => c.narration && c.narration.trim().length > 0);

if (cuts.length === 0) {
  console.log("[tts-batch] no narration found in any element, skipping TTS");
  const final = structuredClone(draft);
  final.elements.forEach((el) => { delete el.narration; delete el.voiceControl; });
  const finalPath = resolve(batchFile).replace(/\.draft\.json$/, ".final.json");
  writeFileSync(finalPath, JSON.stringify(final, null, 2));
  console.log(`[tts-batch] wrote ${finalPath} (no audio)`);
  process.exit(0);
}

console.log(`[tts-batch] ${cuts.length} cuts with narration`);

// ── Load existing manifest for hash-based cache validation ──
const manifestPath = join(ttsDir, "manifest.json");
let prevManifest = {};
if (existsSync(manifestPath)) {
  try {
    const m = JSON.parse(readFileSync(manifestPath, "utf-8"));
    for (const entry of m.cuts || []) {
      prevManifest[entry.id] = entry.hash;
    }
  } catch { /* ignore corrupt manifest */ }
}

// ── Process a single cut (with hash-based cache check + retry) ──
async function processCut(cut) {
  const vc = cut.voiceControl || {};
  const voiceId = vc.voice || defaultVoice;
  const hash = cacheKey(pName, voiceId, cut.narration, vc);
  const filename = `${cut.id}${mod.AUDIO_EXT}`;
  const filePath = join(ttsDir, filename);

  // Cache hit: file exists AND hash matches (narration + voiceControl unchanged)
  if (existsSync(filePath) && prevManifest[cut.id] === hash) {
    const dur = probeDuration(filePath);
    if (dur > 0) {
      console.log(`  [${cut.id}] cache hit (hash=${hash.slice(0, 8)}) → ${dur.toFixed(1)}s`);
      return { ...cut, src: `tts/${filename}`, actualDuration: dur, cached: true, hash };
    }
  } else if (existsSync(filePath) && prevManifest[cut.id] && prevManifest[cut.id] !== hash) {
    console.log(`  [${cut.id}] params changed (old=${prevManifest[cut.id]?.slice(0, 8)} new=${hash.slice(0, 8)}) → regenerating`);
  }

  // Generate with retry
  let lastErr;
  for (let attempt = 1; attempt <= maxRetries + 1; attempt++) {
    try {
      console.log(`  [${cut.id}] generating (attempt ${attempt})...`);
      const { duration: dur } = await mod.generate(cut.narration, filePath, {
        voice: voiceId,
        tonePrompt: vc.tonePrompt,
        style: vc.style,
        pitch: vc.pitch,
        pitchVariance: vc.pitchVariance,
        speed: vc.speed ?? defaultSpeed,
      });
      console.log(`  [${cut.id}] done → ${dur.toFixed(1)}s`);
      return { ...cut, src: `tts/${filename}`, actualDuration: dur, cached: false, hash };
    } catch (err) {
      lastErr = err;
      console.warn(`  [${cut.id}] attempt ${attempt} failed: ${err.message}`);
      if (attempt <= maxRetries) {
        await new Promise((r) => setTimeout(r, 1000 * attempt));
      }
    }
  }
  throw new Error(`[${cut.id}] all ${maxRetries + 1} attempts failed: ${lastErr?.message}`);
}

// ── Run with concurrency limiter ─────────────────────────
async function runBatch(items, limit, fn) {
  const results = [];
  let i = 0;
  async function worker() {
    while (i < items.length) {
      const idx = i++;
      results[idx] = await fn(items[idx]);
    }
  }
  await Promise.all(Array.from({ length: Math.min(limit, items.length) }, () => worker()));
  return results;
}

const results = await runBatch(cuts, concurrency, processCut);

// ── Build manifest ───────────────────────────────────────
const manifest = {
  provider: pName,
  voice: defaultVoice,
  generatedAt: new Date().toISOString(),
  cuts: results.map((r) => ({
    id: r.id,
    src: r.src,
    hash: r.hash,
    draftDuration: r.durationSec,
    actualDuration: r.actualDuration,
    drift: +(r.actualDuration - r.durationSec).toFixed(2),
    cached: r.cached,
  })),
};

writeFileSync(manifestPath, JSON.stringify(manifest, null, 2));
console.log(`[tts-batch] manifest → ${manifestPath}`);

// ── Duration drift report ────────────────────────────────
const DRIFT_THRESHOLD = 1.5;
let driftWarnings = 0;
for (const c of manifest.cuts) {
  if (Math.abs(c.drift) > DRIFT_THRESHOLD) {
    console.warn(`  ⚠ [${c.id}] drift ${c.drift > 0 ? "+" : ""}${c.drift}s (draft=${c.draftDuration}s actual=${c.actualDuration}s)`);
    driftWarnings++;
  }
}

// ── Build timeline.final.json ────────────────────────────
const final = structuredClone(draft);

// Update element durations from actual TTS durations
for (const r of results) {
  const el = final.elements[r.idx];
  if (el && r.actualDuration > 0) {
    el.durationSec = Math.ceil(r.actualDuration) + 0.5;
  }
  if (el) { delete el.narration; delete el.voiceControl; }
}

// Also remove narration/voiceControl from elements without TTS
for (const el of final.elements) {
  delete el.narration;
  delete el.voiceControl;
}

// Build audio array from TTS results
const audioEntries = results.map((r) => ({
  type: "tts",
  src: r.src,
  elementId: r.id,
  durationSec: r.actualDuration,
}));

// Merge with existing audio (music, sfx, etc.)
final.audio = [...(final.audio || []).filter((a) => a.type !== "tts"), ...audioEntries];

// Remove manual totalDurationSec — Root.tsx uses computeTiming()
delete final.meta?.totalDurationSec;

const finalPath = resolve(batchFile).replace(/\.draft\.json$/, ".final.json");
writeFileSync(finalPath, JSON.stringify(final, null, 2));

console.log(`[tts-batch] timeline.final.json → ${finalPath}`);
console.log(`[tts-batch] ${results.length} cuts processed, ${results.filter((r) => r.cached).length} cached, ${driftWarnings} drift warnings`);
