import argparse
import csv
import random
import re
import sys
import time
from pathlib import Path
from urllib.parse import urlparse, parse_qs

from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import CouldNotRetrieveTranscript, RequestBlocked

INVALID_FILENAME_CHARS = r'[\\/:*?"<>|]'
LANGUAGES = ["ta", "en"]

# YouTube publishes no official rate limit. A randomized 10-20s gap between
# requests (~3-6 per minute) is a commonly reported safe range for unauthenticated
# transcript fetches; fixed short intervals look bot-like and get IPs blocked.
DEFAULT_MIN_DELAY = 10.0
DEFAULT_MAX_DELAY = 20.0
# Cap on transcript requests per run, to keep each session's volume low.
DEFAULT_MAX_DOWNLOADS = 5


def sanitize_filename(name):
    return re.sub(INVALID_FILENAME_CHARS, "_", name).strip()


def extract_video_id(url):
    parsed = urlparse(url.strip())

    if parsed.hostname in ("youtu.be",):
        return parsed.path.strip("/").split("/")[0]

    if parsed.hostname and "youtube.com" in parsed.hostname:
        if parsed.path == "/watch":
            video_id = parse_qs(parsed.query).get("v", [None])[0]
            if video_id:
                return video_id
        for prefix in ("/live/", "/shorts/", "/embed/"):
            if parsed.path.startswith(prefix):
                return parsed.path[len(prefix):].strip("/").split("/")[0]

    raise ValueError(f"Could not extract video ID from URL: {url}")


def fetch_transcript(ytt_api, video_id):
    transcript = ytt_api.fetch(video_id, languages=LANGUAGES)
    return "\n".join(snippet.text for snippet in transcript)


def main():
    parser = argparse.ArgumentParser(description="Batch-extract YouTube transcripts from a CSV of title,url rows.")
    parser.add_argument("csv_path", help="Path to input CSV file with title,url columns (header row optional)")
    parser.add_argument("outdir", help="Subfolder to save transcripts into (created if missing)")
    parser.add_argument("--min-delay", type=float, default=DEFAULT_MIN_DELAY,
                        help=f"Minimum seconds to wait between requests (default {DEFAULT_MIN_DELAY})")
    parser.add_argument("--max-delay", type=float, default=DEFAULT_MAX_DELAY,
                        help=f"Maximum seconds to wait between requests (default {DEFAULT_MAX_DELAY})")
    parser.add_argument("--max-downloads", type=int, default=DEFAULT_MAX_DOWNLOADS,
                        help=f"Maximum transcripts to fetch in one run (default {DEFAULT_MAX_DOWNLOADS})")
    args = parser.parse_args()
    if args.max_downloads < 1:
        parser.error("--max-downloads must be >= 1")
    if args.max_delay < args.min_delay:
        parser.error("--max-delay must be >= --min-delay")

    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)

    ytt_api = YouTubeTranscriptApi()

    with open(args.csv_path, newline="", encoding="utf-8-sig") as f:
        rows = list(csv.reader(f))

    if rows and [c.strip().lower() for c in rows[0][:2]] == ["title", "url"]:
        rows = rows[1:]

    requests_made = 0
    saved = 0

    for i, row in enumerate(rows, 1):
        title = (row[0] if len(row) > 0 else "").strip()
        url = (row[1] if len(row) > 1 else "").strip()
        if not title or not url:
            print(f"[{i}/{len(rows)}] Skipping row with missing title/url: {row}")
            continue

        out_path = outdir / f"{sanitize_filename(title)}.txt"
        if out_path.exists():
            print(f"[{i}/{len(rows)}] Skipping (already exists): {out_path.name}")
            continue

        try:
            video_id = extract_video_id(url)
        except ValueError as e:
            print(f"[{i}/{len(rows)}] ERROR: {e}")
            continue

        if requests_made >= args.max_downloads:
            print(f"Reached limit of {args.max_downloads} downloads for this run. "
                  f"Re-run later to continue; saved files will be skipped.")
            break

        # Only wait between actual network requests, not for skipped rows.
        if requests_made:
            delay = random.uniform(args.min_delay, args.max_delay)
            print(f"[{i}/{len(rows)}] Waiting {delay:.1f}s before next request...")
            time.sleep(delay)
        requests_made += 1

        try:
            text = fetch_transcript(ytt_api, video_id)
        except RequestBlocked as e:
            print(f"[{i}/{len(rows)}] YouTube is blocking requests from this IP. Stopping to avoid "
                  f"extending the block. Re-run later; already-saved files will be skipped.\n{e}")
            sys.exit(1)
        except CouldNotRetrieveTranscript as e:
            print(f"[{i}/{len(rows)}] ERROR fetching transcript for '{title}' ({video_id}): {e}")
            continue

        out_path.write_text(text, encoding="utf-8")
        saved += 1
        print(f"[{i}/{len(rows)}] Saved: {out_path}")

    print(f"Done: {saved} saved, {requests_made} request(s) made this run.")


if __name__ == "__main__":
    main()
