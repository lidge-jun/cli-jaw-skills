#!/usr/bin/env node
/**
 * Ensure Remotion runtime is available.
 * Checks ~/.remotion/node_modules (shared installation).
 * Run setup-remotion.sh if not installed.
 */
import { execFileSync } from "node:child_process";
import { existsSync, lstatSync, symlinkSync, unlinkSync } from "node:fs";
import { resolve, dirname, join } from "node:path";
import { fileURLToPath } from "node:url";
import { homedir } from "node:os";

const __dirname = dirname(fileURLToPath(import.meta.url));
const REMOTION_HOME = join(homedir(), ".remotion");
const PROJECT_DIR = resolve(__dirname, "..", "remotion-project");
const PROJECT_NM = join(PROJECT_DIR, "node_modules");
const SHARED_NM = join(REMOTION_HOME, "node_modules");

function isDisabled() {
  const raw = String(process.env.REMOTION_RUNTIME_BOOTSTRAP ?? "1").trim().toLowerCase();
  return raw === "0" || raw === "false" || raw === "off" || raw === "no";
}

function run(cmd, args, opts = {}) {
  try {
    const output = execFileSync(cmd, args, {
      encoding: "utf8",
      stdio: ["ignore", "pipe", "pipe"],
      ...opts,
    });
    return { ok: true, output: output.trim() };
  } catch (error) {
    const stdout = typeof error?.stdout === "string" ? error.stdout : "";
    const stderr = typeof error?.stderr === "string" ? error.stderr : "";
    return { ok: false, output: `${stdout}\n${stderr}`.trim() };
  }
}

if (isDisabled()) {
  console.log("[Remotion bootstrap] skipped (REMOTION_RUNTIME_BOOTSTRAP disabled)");
  process.exit(0);
}

// Check ~/.remotion/node_modules
if (!existsSync(join(SHARED_NM, "remotion"))) {
  console.error("[Remotion bootstrap] ~/.remotion not found.");
  console.error("  Run: setup-remotion.sh");
  process.exit(1);
}

// Symlink remotion-project/node_modules → ~/.remotion/node_modules
// Webpack resolves from project dir — NODE_PATH alone is insufficient
try {
  if (existsSync(PROJECT_NM)) {
    const stat = lstatSync(PROJECT_NM);
    if (stat.isSymbolicLink()) {
      // Already a symlink — ok
    } else {
      // Real dir (leftover local install) — replace with symlink
      console.log("[Remotion bootstrap] replacing local node_modules with symlink to ~/.remotion");
      execFileSync("rm", ["-rf", PROJECT_NM]);
      symlinkSync(SHARED_NM, PROJECT_NM);
    }
  } else {
    symlinkSync(SHARED_NM, PROJECT_NM);
  }
} catch (e) {
  console.error("[Remotion bootstrap] failed to create node_modules symlink:", e.message);
  process.exit(1);
}

// Check remotion CLI from ~/.remotion
const localCli = run("npx", ["remotion", "--help"], { cwd: REMOTION_HOME });
if (!localCli.ok) {
  console.error("[Remotion bootstrap] failed: Remotion CLI not available in ~/.remotion");
  if (localCli.output) console.error(localCli.output);
  process.exit(1);
}

// Ensure browser
const ensureBrowser = run("npx", ["remotion", "browser", "ensure"], { cwd: REMOTION_HOME });
if (ensureBrowser.ok) {
  console.log("[Remotion bootstrap] browser runtime is ready.");
  process.exit(0);
}

console.error("[Remotion bootstrap] failed: could not ensure browser runtime.");
if (ensureBrowser.output) console.error(ensureBrowser.output);
process.exit(1);
