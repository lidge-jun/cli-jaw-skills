#!/usr/bin/env node
/**
 * batch.mjs — Batch HTML→PPTX converter
 * Converts multiple HTML slide files into a single PPTX deck.
 *
 * Usage: node batch.mjs slide-01.html slide-02.html --output deck.pptx
 *
 * Ported from claw-empire/slides/generate-pptx.mjs
 */
import PptxGenJS from "pptxgenjs";
import path from "path";
import { createRequire } from "module";

const require = createRequire(import.meta.url);
const html2pptx = require("./html2pptx.cjs");

const args = process.argv.slice(2);
const outputIdx = args.indexOf("--output");
const outputPath = outputIdx >= 0 ? args[outputIdx + 1] : "deck.pptx";
const layoutIdx = args.indexOf("--layout");
const layoutArg = layoutIdx >= 0 ? args[layoutIdx + 1] : "16x9";
const layoutMap = { "16x9": "LAYOUT_16x9", "4x3": "LAYOUT_4x3" };
if (!layoutMap[layoutArg]) {
    console.error("Invalid --layout value. Use 16x9 or 4x3");
    process.exit(1);
}
const skipArgs = new Set();
if (outputIdx >= 0) { skipArgs.add(outputIdx); skipArgs.add(outputIdx + 1); }
if (layoutIdx >= 0) { skipArgs.add(layoutIdx); skipArgs.add(layoutIdx + 1); }
const slides = args.filter((a, i) => !skipArgs.has(i));

if (slides.length === 0) {
    console.error("Usage: node batch.mjs slide-01.html slide-02.html [--output deck.pptx] [--layout 16x9|4x3]");
    process.exit(1);
}

async function main() {
    const pres = new PptxGenJS();
    pres.layout = layoutMap[layoutArg];

    let succeeded = 0;
    let failed = 0;

    for (const slideFile of slides) {
        const filePath = path.resolve(slideFile);
        console.log(`Converting ${slideFile}...`);
        try {
            await html2pptx(filePath, pres);
            console.log(`  ✓ ${slideFile} done`);
            succeeded++;
        } catch (err) {
            console.error(`  ✗ ${slideFile} error: ${err.message}`);
            failed++;
        }
    }

    if (succeeded === 0) {
        console.error("\nAll slides failed. No PPTX generated.");
        process.exit(1);
    }

    await pres.writeFile({ fileName: outputPath });
    console.log(`\nPPTX saved: ${outputPath} (${succeeded}/${slides.length} slides converted)`);
    if (failed > 0) {
        console.error(`Warning: ${failed} slide(s) failed`);
        process.exit(1);
    }
}

main().catch((err) => {
    console.error("Fatal:", err);
    process.exit(1);
});
