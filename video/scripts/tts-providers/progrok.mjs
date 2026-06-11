// tts-providers/progrok.mjs — xAI/progrok TTS via local OAuth proxy
import { writeFileSync } from "fs";

export const PROVIDER_ID = "progrok";
export const DEFAULT_VOICE = "eve";
export const AUDIO_EXT = ".mp3";
export const VOICES = ["eve", "ara", "leo", "rex", "sal"];

const DEFAULT_BASE_URL = "http://127.0.0.1:18645/v1";

function normalizeBaseUrl(value) {
  const baseUrl = String(value || DEFAULT_BASE_URL).replace(/\/+$/, "");
  return baseUrl.endsWith("/v1") ? baseUrl : `${baseUrl}/v1`;
}

function buildOutputFormat(outputPath) {
  const lower = outputPath.toLowerCase();
  if (lower.endsWith(".wav")) return { codec: "wav" };
  if (lower.endsWith(".pcm")) return { codec: "pcm" };
  if (lower.endsWith(".mulaw")) return { codec: "mulaw" };
  if (lower.endsWith(".alaw")) return { codec: "alaw" };
  return { codec: "mp3" };
}

export async function generate(text, outputPath, {
  voice = DEFAULT_VOICE,
  speed = 1.0,
  language = process.env.PROGROK_TTS_LANGUAGE || "auto",
  textNormalization = true,
} = {}) {
  const baseUrl = normalizeBaseUrl(process.env.PROGROK_BASE_URL);
  const response = await fetch(`${baseUrl}/tts`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      text,
      voice_id: voice,
      language,
      output_format: buildOutputFormat(outputPath),
      speed,
      text_normalization: textNormalization,
    }),
  });

  if (!response.ok) {
    const body = await response.text().catch(() => "");
    throw new Error(`progrok TTS failed (${response.status}): ${body || response.statusText}`);
  }

  const audio = Buffer.from(await response.arrayBuffer());
  if (audio.length === 0) {
    throw new Error("progrok TTS returned empty audio");
  }
  writeFileSync(outputPath, audio);
  return { outputPath, duration: 0 };
}
