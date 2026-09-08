// tts-providers/supertone.mjs — Supertone Cloud API + 300-char Korean splitting
import { writeFileSync, unlinkSync } from "fs";
import { execSync } from "child_process";

const BASE = "https://supertoneapi.com";

export const PROVIDER_ID = "supertone";
export const DEFAULT_VOICE = "4653d63d07d5340656b6bc"; // Andrew
export const AUDIO_EXT = ".mp3";
export const VOICES = {
  Andrew:   { id: "4653d63d07d5340656b6bc", styles: ["angry","curious","happy","neutral","sad","shy"] },
  Anna:     { id: "259d4ac1ecf560c0f76e08", styles: ["angry","embarrassed","happy","neutral","painful","sad"] },
  Alphonse: { id: "c3c0898fd41489a8e8919c", styles: ["admiring","angry","anxious","happy","neutral","sad"] },
  Agatha:   { id: "e5f6fb1a53d0add87afb4f", styles: ["happy","neutral","serene"] },
  Audrey:   { id: "1f6b70f879da125bfec245", styles: ["angry","confident","happy","neutral","sad","unfriendly"] },
};

export async function generate(text, outputPath, {
  voice = DEFAULT_VOICE,
  style = "neutral",
  pitch = 0,
  pitchVariance = 1.0,
  speed = 1.2,
} = {}) {
  const apiKey = process.env.SUPERTONE_API_KEY;
  if (!apiKey) throw new Error("SUPERTONE_API_KEY not set");

  const voiceId = voice.length > 10 ? voice : VOICES[voice]?.id || DEFAULT_VOICE;
  const chunks = splitKorean(text, 300);
  const parts = [];

  for (const chunk of chunks) {
    const res = await fetch(`${BASE}/v1/text-to-speech/${voiceId}?output_format=mp3`, {
      method: "POST",
      headers: { "Content-Type": "application/json", "x-sup-api-key": apiKey },
      body: JSON.stringify({
        text: chunk, language: "ko", style, model: "sona_speech_2",
        voice_settings: { pitch_shift: pitch, pitch_variance: pitchVariance, speed },
      }),
    });
    if (!res.ok) throw new Error(`Supertone ${res.status}: ${await res.text()}`);
    parts.push({
      buffer: Buffer.from(await res.arrayBuffer()),
      duration: parseFloat(res.headers.get("X-Audio-Length") || "0"),
    });
    await new Promise(r => setTimeout(r, 200));
  }

  if (parts.length === 1) {
    writeFileSync(outputPath, parts[0].buffer);
    return { outputPath, duration: parts[0].duration || probeDuration(outputPath) };
  }

  // Multi-chunk concat
  const tmpFiles = parts.map((p, i) => {
    const tmp = `${outputPath}.part${i}.mp3`;
    writeFileSync(tmp, p.buffer); return tmp;
  });
  const listFile = `${outputPath}.concat.txt`;
  writeFileSync(listFile, tmpFiles.map(f => `file '${f}'`).join("\n"));
  execSync(`ffmpeg -y -f concat -safe 0 -i "${listFile}" -c copy "${outputPath}" 2>/dev/null`);
  [...tmpFiles, listFile].forEach(f => { try { unlinkSync(f); } catch {} });

  const totalDur = parts.reduce((s, p) => s + p.duration, 0) || probeDuration(outputPath);
  return { outputPath, duration: totalDur };
}

function splitKorean(text, max = 300) {
  if (text.length <= max) return [text];
  const sents = text.split(/(?<=[.?!。]\s?)/);
  const chunks = []; let cur = "";
  for (const s of sents) {
    if ((cur + s).length > max && cur) { chunks.push(cur.trim()); cur = s; }
    else cur += s;
  }
  if (cur.trim()) chunks.push(cur.trim());
  return chunks;
}

function probeDuration(filePath) {
  try {
    const out = execSync(`ffprobe -v quiet -print_format json -show_format "${filePath}"`, { encoding: "utf-8" });
    return parseFloat(JSON.parse(out).format?.duration || "0");
  } catch { return 0; }
}
