#!/usr/bin/env node
/**
 * convert.mjs — Screenshot fallback for complex CSS slides
 * Renders HTML as full-page screenshot and embeds as image in PPTX.
 *
 * Usage: node convert.mjs slide.html [output.pptx]
 *
 * Ported from claw-empire/scripts/convert-slides.mjs
 */
import { chromium } from "playwright";
import PptxGenJS from "pptxgenjs";
import path from "path";

const args = process.argv.slice(2);
const layoutIdx = args.indexOf("--layout");
const layoutArg = layoutIdx >= 0 ? args[layoutIdx + 1] : "16x9";
const layoutMap = { "16x9": "LAYOUT_16x9", "4x3": "LAYOUT_4x3" };
const viewportMap = { "16x9": { width: 960, height: 540 }, "4x3": { width: 960, height: 720 } };
if (!layoutMap[layoutArg]) {
    console.error("Invalid --layout value. Use 16x9 or 4x3");
    process.exit(1);
}
const positionalArgs = args.filter((a, i) => i !== layoutIdx && (layoutIdx < 0 || i !== layoutIdx + 1));
const inputHtml = positionalArgs[0];
const outputPptx = positionalArgs[1] || "output.pptx";

if (!inputHtml) {
    console.error("Usage: node convert.mjs <slide.html> [output.pptx] [--layout 16x9|4x3]");
    process.exit(1);
}

async function main() {
    const pres = new PptxGenJS();
    pres.layout = layoutMap[layoutArg];

    const launchOptions = { headless: true };
    if (process.platform === "darwin") launchOptions.channel = "chrome";

    const browser = await chromium.launch(launchOptions);
    const page = await browser.newPage({ viewport: viewportMap[layoutArg] });

    const filePath = path.resolve(inputHtml);
    await page.goto(`file://${filePath}`, { waitUntil: "networkidle" });

    const screenshot = await page.locator("body").screenshot({ type: "png", scale: "device" });
    const base64 = screenshot.toString("base64");

    const slide = pres.addSlide();
    slide.addImage({ data: `image/png;base64,${base64}`, x: 0, y: 0, w: "100%", h: "100%" });

    await browser.close();
    await pres.writeFile({ fileName: outputPptx });
    console.log(`Screenshot PPTX saved: ${outputPptx}`);
}

main().catch((err) => {
    console.error("Fatal:", err);
    process.exit(1);
});
