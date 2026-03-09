// tts-providers/gemini.mjs — Gemini TTS (Cloud, default)
import { createRequire } from "module";
import { dirname, join } from "path";
import { fileURLToPath } from "url";
import { writeFileSync, unlinkSync, readFileSync } from "fs";
import { execSync } from "child_process";

const __dirname = dirname(fileURLToPath(import.meta.url));
const remotionDir = join(__dirname, "..", "..", "remotion-project");
const require = createRequire(join(remotionDir, "package.json"));
const { GoogleGenAI } = require("@google/genai");

export const PROVIDER_ID = "gemini";
export const DEFAULT_VOICE = "Kore";
export const AUDIO_EXT = ".m4a";
export const VOICES = [
  "Kore", "Charon", "Puck", "Zephyr", "Fenrir", "Leda", "Orus", "Aoede",
  "Achernar", "Achird", "Algenib", "Algieba", "Alnilam", "Autonoe",
  "Callirrhoe", "Despina", "Enceladus", "Erinome", "Gacrux", "Iapetus",
  "Laomedeia", "Pulcherrima", "Rasalgethi", "Sadachbia", "Schedar",
  "Umbriel", "Vindemiatrix", "Zubenelgenubi",
];

export async function generate(text, outputPath, { voice = "Kore", tonePrompt, speed = 1.2 } = {}) {
  let ai;
  if (process.env.GOOGLE_APPLICATION_CREDENTIALS || process.env.GOOGLE_CLOUD_PROJECT) {
    // Vertex AI path (service account / ADC)
    const project = process.env.GOOGLE_CLOUD_PROJECT || (() => {
      try { return JSON.parse(readFileSync(process.env.GOOGLE_APPLICATION_CREDENTIALS, "utf-8")).project_id; }
      catch { throw new Error("Cannot determine project_id from GOOGLE_APPLICATION_CREDENTIALS"); }
    })();
    const location = process.env.GOOGLE_CLOUD_LOCATION || "us-central1";
    ai = new GoogleGenAI({ vertexai: true, project, location });
    console.log(`  [TTS] Using Vertex AI (project=${project}, location=${location})`);
  } else {
    const apiKey = process.env.GEMINI_API_KEY;
    if (!apiKey) throw new Error("GEMINI_API_KEY not set and no Vertex AI credentials found");
    ai = new GoogleGenAI({ apiKey });
    console.log(`  [TTS] Using Gemini API key`);
  }
  const config = {
    responseModalities: ["AUDIO"],
    speechConfig: { voiceConfig: { prebuiltVoiceConfig: { voiceName: voice } } },
    temperature: 0.5,
    maxOutputTokens: 8192,
  };

  // tonePrompt → prepend as speaking direction (systemInstruction breaks TTS mode)
  const spokenText = tonePrompt
    ? `Say the following in a ${tonePrompt}: ${text}`
    : text;

  const response = await ai.models.generateContent({
    model: "gemini-2.5-flash-preview-tts",
    contents: [{ role: "user", parts: [{ text: spokenText }] }],
    config,
  });

  const audioPart = response.candidates?.[0]?.content?.parts?.find(p => p.inlineData);
  if (!audioPart) throw new Error("No audio data in TTS response");

  const audioData = Buffer.from(audioPart.inlineData.data, "base64");
  const rawPath = outputPath + ".raw.pcm";
  writeFileSync(rawPath, audioData);

  const mimeType = audioPart.inlineData.mimeType || "";
  const extraArgs = mimeType.includes("pcm") || mimeType.includes("L16")
    ? "-f s16le -ar 24000 -ac 1" : "";

  try {
    execSync(`ffmpeg -y ${extraArgs} -i "${rawPath}" -c:a aac -b:a 128k "${outputPath}" 2>/dev/null`);
    unlinkSync(rawPath);
  } catch { console.warn(`  ffmpeg failed, raw kept at ${rawPath}`); }

  // speed != 1.0 → ffmpeg atempo post-processing
  if (speed && Math.abs(speed - 1.0) > 0.01) {
    const tmpSpeed = outputPath + ".speed.m4a";
    execSync(`ffmpeg -y -i "${outputPath}" -filter:a "atempo=${speed}" -c:a aac -b:a 128k "${tmpSpeed}" 2>/dev/null`);
    execSync(`mv "${tmpSpeed}" "${outputPath}"`);
  }

  return { outputPath, duration: probeDuration(outputPath) };
}

function probeDuration(filePath) {
  try {
    const out = execSync(`ffprobe -v quiet -print_format json -show_format "${filePath}"`, { encoding: "utf-8" });
    return parseFloat(JSON.parse(out).format?.duration || "0");
  } catch { return 0; }
}
