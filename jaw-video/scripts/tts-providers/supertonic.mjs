// tts-providers/supertonic.mjs — Local ONNX via Python/uv (Phase 11B)
import { execSync } from "child_process";

export const PROVIDER_ID = "supertonic";
export const DEFAULT_VOICE = "M1";
export const AUDIO_EXT = ".wav";
export const VOICES = {
  M1: "Male 1 (default)", M2: "Male 2", M3: "Male 3", M4: "Male 4", M5: "Male 5",
  F1: "Female 1", F2: "Female 2", F3: "Female 3", F4: "Female 4", F5: "Female 5",
};

// Dependency: pip install supertonic (PyPI), uv, ~260MB model on first run
const SUPERTONIC_CWD = process.env.SUPERTONIC_DIR || "/tmp/supertonic_test/py";

export async function generate(text, outputPath, { voice = "M1", speed = 1.2 } = {}) {
  const pyScript = `
import soundfile as sf
from supertonic import TTS
tts = TTS(auto_download=True)
style = tts.get_voice_style(voice_name="${voice}")
wav, dur = tts.synthesize(${JSON.stringify(text)}, voice_style=style, lang="ko")
tts.save_audio(wav, "${outputPath}")
print(f"{dur.item():.4f}")
`;

  execSync(`uv run python3 -c ${JSON.stringify(pyScript)}`, {
    timeout: 120000,
    cwd: SUPERTONIC_CWD,
  });

  // speed != 1.0 → ffmpeg atempo post-processing
  if (speed && Math.abs(speed - 1.0) > 0.01) {
    const tmpSpeed = outputPath + ".speed.wav";
    execSync(`ffmpeg -y -i "${outputPath}" -filter:a "atempo=${speed}" "${tmpSpeed}" 2>/dev/null`);
    execSync(`mv "${tmpSpeed}" "${outputPath}"`);
  }

  const duration = parseFloat(
    execSync(`ffprobe -v quiet -show_entries format=duration -of csv=p=0 "${outputPath}"`,
      { encoding: "utf-8" }).trim()
  );
  return { outputPath, duration };
}
