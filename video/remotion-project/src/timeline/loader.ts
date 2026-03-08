import { readFileSync } from "node:fs";
import { validateTimeline } from "./schema";
import type { Timeline } from "./schema";

export function loadTimeline(filePath: string): Timeline {
  const raw = readFileSync(filePath, "utf8");
  const data = JSON.parse(raw);
  const result = validateTimeline(data);

  if (!result.valid || !result.timeline) {
    throw new Error(`Invalid timeline: ${result.errors.join(", ")}`);
  }

  return result.timeline;
}
