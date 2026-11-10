"""
Download YouTube audio (yt-dlp) and transcribe with faster-whisper, for a list of videos.

Setup on the GPU machine:
    pip install yt-dlp faster-whisper nvidia-cublas-cu12 nvidia-cudnn-cu12
    # ffmpeg must be on PATH.

Run:
    python batch_transcribe.py                       # all videos in tattvabodham_urls.txt
    python batch_transcribe.py --only Class-01 Class-02
    python batch_transcribe.py --lang ta --model large-v3

Input : tattvabodham_urls.txt  (label<TAB>url per line)
Output: audio/<label>.mp3, transcripts/<label>.txt and transcripts/<label>.srt
Re-running skips anything already downloaded / transcribed, so it is safe to resume.
"""

import argparse
import subprocess
import sys
from pathlib import Path

DEFAULT_PROMPT = ("இது தத்வ போதம் வகுப்பு. ஆத்மா, அனாத்மா, சாதன சதுஷ்டய சம்பத்தி, "
                  "விவேகம், வைராக்யம், moksha, Vedanta, Acharya.")


def format_timestamp(seconds: float) -> str:
    ms = int(round(seconds * 1000))
    h, ms = divmod(ms, 3600_000)
    m, ms = divmod(ms, 60_000)
    s, ms = divmod(ms, 1000)
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


def read_urls(path: Path) -> list[tuple[str, str]]:
    items = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        label, url = line.split("\t") if "\t" in line else line.rsplit(None, 1)
        items.append((label.strip(), url.strip()))
    return items


def download(label: str, url: str, audio_dir: Path) -> Path | None:
    mp3 = audio_dir / f"{label}.mp3"
    if mp3.exists():
        return mp3
    cmd = [sys.executable, "-m", "yt_dlp", "-x", "--audio-format", "mp3",
           "-o", str(audio_dir / f"{label}.%(ext)s"), url]
    if subprocess.run(cmd).returncode != 0 or not mp3.exists():
        print(f"  !! download failed: {label}", file=sys.stderr)
        return None
    return mp3


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--urls", default="tattvabodham_urls.txt")
    ap.add_argument("--only", nargs="*", help="Only these labels")
    ap.add_argument("--model", default="large-v3")
    ap.add_argument("--lang", default="ta", help="Language code, or 'auto'")
    ap.add_argument("--device", default="auto", choices=["auto", "cuda", "cpu"])
    ap.add_argument("--prompt", default=DEFAULT_PROMPT)
    ap.add_argument("--audio-dir", default="audio")
    ap.add_argument("--out-dir", default="transcripts")
    args = ap.parse_args()

    audio_dir, out_dir = Path(args.audio_dir), Path(args.out_dir)
    audio_dir.mkdir(exist_ok=True)
    out_dir.mkdir(exist_ok=True)

    items = read_urls(Path(args.urls))
    if args.only:
        items = [i for i in items if i[0] in args.only]

    from faster_whisper import WhisperModel

    device = args.device
    if device == "auto":
        try:
            import ctranslate2
            device = "cuda" if ctranslate2.get_cuda_device_count() > 0 else "cpu"
        except Exception:
            device = "cpu"
    compute = "float16" if device == "cuda" else "int8"
    print(f"Loading {args.model} on {device}/{compute} ...")
    model = WhisperModel(args.model, device=device, compute_type=compute)
    lang = None if args.lang.lower() == "auto" else args.lang

    failed = []
    for n, (label, url) in enumerate(items, 1):
        print(f"\n=== [{n}/{len(items)}] {label} ===")
        txt, srt = out_dir / f"{label}.txt", out_dir / f"{label}.srt"
        if txt.exists() and srt.exists():
            print("  already transcribed, skipping")
            continue
        mp3 = download(label, url, audio_dir)
        if mp3 is None:
            failed.append(label)
            continue

        segments, info = model.transcribe(
            str(mp3), language=lang, initial_prompt=args.prompt or None,
            beam_size=5, vad_filter=True,
            vad_parameters=dict(min_silence_duration_ms=500),
            condition_on_previous_text=False,  # avoids repetition loops on long lectures
        )
        print(f"  language={info.language} ({info.language_probability:.2f}), {info.duration/60:.1f} min")

        lines, blocks = [], []
        for i, seg in enumerate(segments, 1):
            t = seg.text.strip()
            lines.append(t)
            blocks.append(f"{i}\n{format_timestamp(seg.start)} --> {format_timestamp(seg.end)}\n{t}\n")
        txt.write_text("\n".join(lines) + "\n", encoding="utf-8")
        srt.write_text("\n".join(blocks), encoding="utf-8")
        print(f"  saved {txt}")

    if failed:
        print("\nFailed downloads:", ", ".join(failed))
        return 1
    print("\nAll done.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
