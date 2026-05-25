#!/usr/bin/env node
import { execFileSync } from "node:child_process";
import { existsSync, mkdirSync, copyFileSync, lstatSync, symlinkSync, unlinkSync } from "node:fs";
import { resolve, dirname, join } from "node:path";
import { fileURLToPath } from "node:url";
import { homedir } from "node:os";

const __dirname = dirname(fileURLToPath(import.meta.url));
const PROJECT_DIR = resolve(__dirname, "..", "remotion-project");
const SHARED_DIR = join(homedir(), ".jaw-shared", "remotion");
const SHARED_MODULES = join(SHARED_DIR, "node_modules");
const LOCAL_MODULES = join(PROJECT_DIR, "node_modules");

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

function ensureSharedModules() {
  mkdirSync(SHARED_DIR, { recursive: true });

  const sharedPkg = join(SHARED_DIR, "package.json");
  const localPkg = join(PROJECT_DIR, "package.json");
  copyFileSync(localPkg, sharedPkg);

  const pnpmConfig = join(PROJECT_DIR, ".npmrc");
  if (existsSync(pnpmConfig)) copyFileSync(pnpmConfig, join(SHARED_DIR, ".npmrc"));

  console.log("[Remotion bootstrap] installing to shared location ~/.jaw-shared/remotion ...");
  const install = run("pnpm", ["install"], { cwd: SHARED_DIR, stdio: "inherit" });
  if (!install.ok) {
    console.error("[Remotion bootstrap] pnpm install failed at shared location");
    process.exit(1);
  }
}

function ensureSymlink() {
  if (existsSync(LOCAL_MODULES)) {
    const stat = lstatSync(LOCAL_MODULES);
    if (stat.isSymbolicLink()) return;
    console.log("[Remotion bootstrap] removing local node_modules in favor of shared symlink...");
    execFileSync("rm", ["-rf", LOCAL_MODULES]);
  }
  symlinkSync(SHARED_MODULES, LOCAL_MODULES);
  console.log("[Remotion bootstrap] symlinked node_modules → ~/.jaw-shared/remotion/node_modules");
}

if (isDisabled()) {
  console.log("[Remotion bootstrap] skipped (REMOTION_RUNTIME_BOOTSTRAP disabled)");
  process.exit(0);
}

// Install to shared location if needed
if (!existsSync(SHARED_MODULES)) {
  ensureSharedModules();
}

// Ensure local symlink points to shared modules
ensureSymlink();

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
