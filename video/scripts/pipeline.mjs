#!/usr/bin/env node
/**
 * CLI pipeline for video rendering.
 * Usage: node pipeline.mjs --timeline <path> [--preset Landscape-1080p] [--output ./out] [--async] [--status <path>]
 */
import { parseArgs } from "node:util";
import { readFileSync, writeFileSync, mkdirSync, existsSync, openSync } from "node:fs";
import { resolve, dirname, join } from "node:path";
import { execFileSync, spawnSync, spawn } from "node:child_process";
import { fileURLToPath } from "node:url";
import { validateVideoArtifact } from "./validate-artifact.mjs";
import { getPreset } from "./presets.mjs";

const __dirname = dirname(fileURLToPath(import.meta.url));
const REMOTION_PROJECT = resolve(__dirname, "..", "remotion-project");

const { values } = parseArgs({
  options: {
    timeline: { type: "string" },
    preset: { type: "string" },
    output: { type: "string", default: "./out" },
    async: { type: "boolean", default: false },
    status: { type: "string" },
    "skip-tts": { type: "boolean", default: false },
  },
  strict: false,
});

// --status: check render result
if (values.status) {
  const statusPath = resolve(values.status);
  if (existsSync(statusPath)) {
    console.log(readFileSync(statusPath, "utf8"));
  } else {
    console.log(JSON.stringify({ status: "rendering" }));
  }
  process.exit(0);
}

if (!values.timeline) {
  console.error("Usage: node pipeline.mjs --timeline <path> [--preset Landscape-1080p] [--output ./out] [--async] [--skip-tts]");
  process.exit(1);
}

const startTime = Date.now();

// ── Status writer ─────────────────────────────────────────
function writeStatus(outputDir, status, extra = {}) {
  const resultPath = join(outputDir, "render-result.json");
  writeFileSync(resultPath, JSON.stringify({ status, ...extra, updatedAt: Date.now() }, null, 2));
}

async function run() {
  // 1. Parse timeline
  console.log("Loading timeline:", values.timeline);
  const timelinePath = resolve(values.timeline);
  let timeline;
  try {
    timeline = JSON.parse(readFileSync(timelinePath, "utf8"));
  } catch (e) {
    console.error("Failed to parse timeline:", e.message);
    process.exit(1);
  }
  console.log("Timeline parsed:", timeline.meta?.title || "untitled");

  // 1.5 Preset SOT: timeline.meta.preset is the source of truth.
  // CLI --preset is an override.
  if (values.preset && values.preset !== timeline.meta.preset) {
    console.warn(`CLI preset "${values.preset}" overrides timeline preset "${timeline.meta.preset}"`);
    timeline.meta.preset = values.preset;
  }

  // Resolve output dir early (for status writes)
  const outputDir = resolve(values.output);
  mkdirSync(outputDir, { recursive: true });

  // ── Gate 0.5: TTS auto-generation ──────────────────────
  const hasNarration = timeline.elements?.some((el) => el.narration?.trim());
  let effectiveTimeline = timeline;

  if (hasNarration && !values["skip-tts"]) {
    console.log("[pipeline] narration detected → running TTS batch...");
    writeStatus(outputDir, "tts_generating");

    // Write draft timeline to temp location
    const draftPath = join(outputDir, "timeline.draft.json");
    writeFileSync(draftPath, JSON.stringify(timeline, null, 2));

    const ttsScript = resolve(__dirname, "tts.mjs");
    const ttsArgs = ["--batch", draftPath];
    if (timeline.meta?.ttsVoice) ttsArgs.push("--voice", timeline.meta.ttsVoice);
    if (timeline.meta?.ttsProvider) ttsArgs.push("--provider", timeline.meta.ttsProvider);

    const ttsResult = spawnSync("node", [ttsScript, ...ttsArgs], {
      stdio: "inherit",
      cwd: __dirname,
      env: process.env,
    });

    if (ttsResult.status !== 0) {
      console.error("[pipeline] TTS generation failed");
      writeStatus(outputDir, "failed", { phase: "tts", exitCode: ttsResult.status });
      process.exit(1);
    }

    // Load timeline.final.json (output of tts.mjs batch mode)
    const finalPath = draftPath.replace(/\.draft\.json$/, ".final.json");
    if (existsSync(finalPath)) {
      effectiveTimeline = JSON.parse(readFileSync(finalPath, "utf8"));
      console.log("[pipeline] using TTS-enriched timeline");
    } else {
      console.warn("[pipeline] timeline.final.json not found, using original");
    }
  } else if (hasNarration && values["skip-tts"]) {
    console.log("[pipeline] narration detected but --skip-tts flag set, skipping TTS");
    // Strip narration fields for render
    effectiveTimeline = structuredClone(timeline);
    effectiveTimeline.elements.forEach((el) => { delete el.narration; delete el.voiceControl; });
  }

  // ── Auto-calculate audioStartSec via computeTiming ──────
  if (effectiveTimeline.audio?.length > 0 && effectiveTimeline.elements?.length > 0) {
    // Compute timing from elements (accounting for transition overlaps)
    const elements = effectiveTimeline.elements;
    const starts = [];
    let cursor = 0;
    for (let i = 0; i < elements.length; i++) {
      starts.push(cursor);
      const transitionDur = i < elements.length - 1
        ? (elements[i + 1]?.transition?.durationSec ?? 0.5)
        : 0;
      cursor += elements[i].durationSec - transitionDur;
    }

    // Assign audioStartSec to TTS audio entries matching elementId
    for (const audio of effectiveTimeline.audio) {
      if (audio.elementId) {
        const elIdx = elements.findIndex((el) => el.id === audio.elementId);
        if (elIdx >= 0) {
          audio.startSec = starts[elIdx];
        }
      }
    }
  }

  // 2. Ensure remotion runtime
  console.log("Ensuring Remotion runtime...");
  try {
    execFileSync("node", [resolve(__dirname, "ensure-remotion.mjs")], {
      stdio: "inherit",
    });
  } catch {
    console.error("Remotion bootstrap failed");
    process.exit(1);
  }

  // 3. Resolve output path
  const compositionId = "TimelineVideo";
  const outputPath = join(outputDir, `${compositionId}.mp4`);

  // 4. Render
  writeStatus(outputDir, "rendering");
  console.log("Rendering video...");
  const renderArgs = [
    "exec", "remotion", "render",
    "src/index.ts", compositionId,
    "--props", JSON.stringify({ timeline: effectiveTimeline }),
    "--output", outputPath,
  ];

  if (values.async) {
    // Non-blocking: spawn detached, but monitor exit to write final status
    const logPath = join(outputDir, "render.log");
    const logFd = openSync(logPath, "w");
    const child = spawn("pnpm", renderArgs, {
      cwd: REMOTION_PROJECT,
      detached: true,
      stdio: ["ignore", logFd, logFd],
    });

    // Monitor child exit in a detached event handler
    child.on("exit", (code) => {
      if (code === 0) {
        // Run validation (Gate 3)
        try {
          const preset = getPreset(effectiveTimeline.meta?.preset || "Landscape-1080p");
          const validation = validateVideoArtifact(outputPath, preset);
          if (validation.valid) {
            writeStatus(outputDir, "succeeded", {
              outputPath, compositionId,
              preset: effectiveTimeline.meta?.preset,
              ...validation,
              renderMs: Date.now() - startTime,
            });
          } else {
            writeStatus(outputDir, "failed", { phase: "validation", errors: validation.errors });
          }
        } catch (e) {
          writeStatus(outputDir, "failed", { phase: "validation", error: e.message });
        }
      } else {
        writeStatus(outputDir, "failed", { phase: "render", exitCode: code });
      }
    });

    child.unref();
    console.log(JSON.stringify({
      status: "rendering",
      pid: child.pid,
      logPath,
      outputPath,
      resultPath: join(outputDir, "render-result.json"),
      startedAt: Date.now(),
    }));
    // Don't exit immediately — let the event loop handle the child exit
    // The parent will exit after the child exit handler fires
    return;
  }

  // Blocking (default)
  const renderResult = spawnSync("pnpm", renderArgs, {
    stdio: "inherit",
    cwd: REMOTION_PROJECT,
  });

  if (renderResult.status !== 0) {
    console.error("Render failed (exit:", renderResult.status, ")");
    writeStatus(outputDir, "failed", { phase: "render", exitCode: renderResult.status });
    process.exit(1);
  }
  console.log("Render complete");

  // 5. Validate artifact (Gate 3) — preset from timeline SOT
  console.log("Validating artifact...");
  const preset = getPreset(effectiveTimeline.meta?.preset || timeline.meta?.preset);
  const validation = validateVideoArtifact(outputPath, preset);

  if (!validation.valid) {
    console.error("Artifact validation failed:", validation.errors);
    writeStatus(outputDir, "failed", { phase: "validation", errors: validation.errors });
    process.exit(1);
  }

  // 6. Write result
  const resultJson = {
    status: "succeeded",
    outputPath,
    compositionId,
    preset: effectiveTimeline.meta?.preset || timeline.meta?.preset,
    ...validation,
    renderMs: Date.now() - startTime,
  };

  writeStatus(outputDir, "succeeded", resultJson);
  console.log("Render success:", JSON.stringify(resultJson, null, 2));
  console.log("Output:", outputPath);
}

run().catch((e) => {
  console.error("Pipeline error:", e);
  process.exit(1);
});
