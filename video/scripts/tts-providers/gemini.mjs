// tts-providers/gemini.mjs — Gemini TTS (Cloud, default)
import { createRequire } from "module";
import { dirname, join } from "path";
import { fileURLToPath } from "url";
import { writeFileSync, unlinkSync } from "fs";
import { execSync } from "child_process";

const __dirname = dirname(fileURLToPath(import.meta.url));
const remotionDir = join(__dirname, "..", "..", "remotion-project");
const require = createRequire(join(remotionDir, "package.json"));
const { GoogleGenAI } = require("@google/genai");

export const PROVIDER_ID = "gemini";
export const DEFAULT_VOICE = "Kore";
export const AUDIO_EXT = ".m4a";
export const VOICES = [
  "Kore","Charon","Puck","Zephyr","Fenrir","Leda","Orus","Aoede",
  "Achernar","Achird","Algenib","Algieba","Alnilam","Autonoe",
  "Callirrhoe","Despina","Enceladus","Erinome","Gacrux","Iapetus",
  "Laomedeia","Pulcherrima","Rasalgethi","Sadachbia","Schedar",
  "Umbriel","Vindemiatrix","Zubenelgenubi",
];

export async function generate(text, outputPath, { voice = "Kore", tonePrompt, speed = 1.2 } = {}) {
  const apiKey = process.env.GEMINI_API_KEY;
  if (!apiKey) throw new Error("GEMINI_API_KEY not set");

  const ai = new GoogleGenAI({ apiKey });
  const config = {
    responseModalities: ["AUDIO"],
    speechConfig: { voiceConfig: { prebuiltVoiceConfig: { voiceName: voice } } },
    temperature: 0.5,
    maxOutputTokens: 8192,
  };

  // tonePrompt → system instruction for tone/emotion control
  if (tonePrompt) {
    config.systemInstruction = tonePrompt;
  }

  const response = await ai.models.generateContent({
    model: "gemini-2.5-flash-preview-tts",
    contents: [{ parts: [{ text }] }],
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
