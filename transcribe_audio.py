"""
Transcribe a local audio file (e.g. Gita chanting MP3) to text using faster-whisper.

Why this exists: YouTube captions are disabled for some chanting videos, so we
download the audio and run speech-to-text locally instead.

Setup (one time, inside the project venv):
    ./venv/Scripts/python.exe -m pip install faster-whisper
    # ffmpeg must be on PATH (it already is on this machine).

Get the audio from YouTube (run in the terminal with `! ` prefix):
    yt-dlp -x --audio-format mp3 -o "BG-Chanting/BG-Ch01-chant.%(ext)s" "https://youtu.be/MZKmsJubvSo"

Run:
    ./venv/Scripts/python.exe transcribe_audio.py "BG-Chanting/BG-Ch01-chant.mp3"
    ./venv/Scripts/python.exe transcribe_audio.py "BG-Chanting/BG-Ch01-chant.mp3" --model large-v3 --lang sa

Output: writes <audio>.txt (plain text) and <audio>.srt (timestamped) next to the audio file.

Notes on quality:
    - Sanskrit ("sa") is a low-resource language for Whisper. `large-v3` is markedly
      better than smaller models for chanting; use it if you have the RAM/time.
    - Chanting (elongated vowels, svara, repeated phrases) is hard for ASR. Expect to
      hand-correct the output against the written text. It is a starting point, not final.
    - First run downloads the model weights (large-v3 ~3 GB) to the HuggingFace cache.
"""

import argparse
import sys
from pathlib import Path


def format_timestamp(seconds: float) -> str:
    ms = int(round(seconds * 1000))
    h, ms = divmod(ms, 3600_000)
    m, ms = divmod(ms, 60_000)
    s, ms = divmod(ms, 1000)
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("audio", help="Path to the audio file (mp3, wav, m4a, ...)")
    parser.add_argument("--model", default="large-v3",
                        help="Whisper model size: tiny, base, small, medium, large-v3 (default: large-v3)")
    parser.add_argument("--lang", default="sa",
                        help="Language code (default: sa = Sanskrit). Use 'hi' to compare, or omit-style 'auto'.")
    parser.add_argument("--device", default="cpu", choices=["cpu", "cuda"],
                        help="Compute device (default: cpu)")
    parser.add_argument("--compute-type", default="int8",
                        help="cpu: int8 (default) or float32; cuda: float16")
    parser.add_argument("--prompt",
                        default="श्रीमद्भगवद्गीता। अथ प्रथमोऽध्यायः। अर्जुनविषादयोगः।",
                        help="Initial prompt to bias the model toward Devanagari Sanskrit spelling")
    parser.add_argument("--out", default=None,
                        help="Output basename (without extension). Default: same as audio file.")
    args = parser.parse_args()

    audio_path = Path(args.audio)
    if not audio_path.exists():
        print(f"ERROR: audio file not found: {audio_path}", file=sys.stderr)
        return 1

    try:
        from faster_whisper import WhisperModel
    except ImportError:
        print("ERROR: faster-whisper is not installed.\n"
              "  ./venv/Scripts/python.exe -m pip install faster-whisper", file=sys.stderr)
        return 1

    out_base = Path(args.out) if args.out else audio_path.with_suffix("")
    txt_path = out_base.with_suffix(".txt")
    srt_path = out_base.with_suffix(".srt")

    print(f"Loading model '{args.model}' ({args.device}/{args.compute_type})... "
          f"first run downloads weights, please wait.")
    model = WhisperModel(args.model, device=args.device, compute_type=args.compute_type)

    lang = None if args.lang.lower() == "auto" else args.lang
    print(f"Transcribing {audio_path.name} (language={lang or 'auto-detect'})...")
    segments, info = model.transcribe(
        str(audio_path),
        language=lang,
        initial_prompt=args.prompt or None,
        beam_size=5,
        vad_filter=True,
        vad_parameters=dict(min_silence_duration_ms=500),
        condition_on_previous_text=True,
    )
    print(f"Detected language: {info.language} (p={info.language_probability:.2f}), "
          f"duration: {info.duration:.1f}s")

    lines = []
    srt_blocks = []
    for i, seg in enumerate(segments, 1):
        text = seg.text.strip()
        lines.append(text)
        srt_blocks.append(
            f"{i}\n{format_timestamp(seg.start)} --> {format_timestamp(seg.end)}\n{text}\n"
        )
        print(f"[{format_timestamp(seg.start)}] {text}")

    txt_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    srt_path.write_text("\n".join(srt_blocks), encoding="utf-8")
    print(f"\nSaved:\n  {txt_path}\n  {srt_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
