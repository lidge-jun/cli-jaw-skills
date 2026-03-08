#!/usr/bin/env node
import { execFileSync } from "node:child_process";
import { existsSync } from "node:fs";
import { resolve, dirname } from "node:path";
import { fileURLToPath } from "node:url";

const __dirname = dirname(fileURLToPath(import.meta.url));
const PROJECT_DIR = resolve(__dirname, "..", "remotion-project");

function isDisabled() {
  const raw = String(process.env.REMOTION_RUNTIME_BOOTSTRAP ?? "1").trim().toLowerCase();
  return raw === "0" || raw === "false" || raw === "off" || raw === "no";
}

function run(cmd, args, opts = {}) {
  try {
    const output = execFileSync(cmd, args, {
      encoding: "utf8",
      stdio: ["ignore", "pipe", "pipe"],
      cwd: PROJECT_DIR,
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

// Install deps if needed
if (!existsSync(resolve(PROJECT_DIR, "node_modules"))) {
  console.log("[Remotion bootstrap] installing dependencies...");
  const install = run("pnpm", ["install"], { stdio: "inherit" });
  if (!install.ok) {
    console.error("[Remotion bootstrap] pnpm install failed");
    process.exit(1);
  }
}

// Check local CLI
const localCli = run("pnpm", ["exec", "remotion", "--help"]);
if (!localCli.ok) {
  console.error("[Remotion bootstrap] failed: local Remotion CLI is not available.");
  if (localCli.output) console.error(localCli.output);
  process.exit(1);
}

// Ensure browser
const ensureLocal = run("pnpm", ["exec", "remotion", "browser", "ensure"]);
if (ensureLocal.ok) {
  console.log("[Remotion bootstrap] browser runtime is ready.");
  process.exit(0);
}

console.error("[Remotion bootstrap] failed: could not ensure browser runtime.");
if (ensureLocal.output) console.error(ensureLocal.output);
process.exit(1);
