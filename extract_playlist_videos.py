import csv
import re
import sys
from yt_dlp import YoutubeDL

INVALID_FILENAME_CHARS = r'[\\/:*?"<>|]'


def sanitize_filename(name):
    return re.sub(INVALID_FILENAME_CHARS, "_", name).strip()


def get_playlist_info(playlist_url):
    ydl_opts = {
        "extract_flat": True,
        "skip_download": True,
        "quiet": True,
    }
    with YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(playlist_url, download=False)

    heading = info.get("title") or "playlist"

    videos = []
    for entry in info.get("entries", []):
        if entry is None:
            continue
        video_id = entry.get("id")
        videos.append({
            "video_id": video_id,
            "title": entry.get("title"),
            "url": entry.get("url") or f"https://www.youtube.com/watch?v={video_id}",
        })
    return heading, videos


def save_as_csv(heading, videos):
    filename = f"{sanitize_filename(heading)}.txt"
    with open(filename, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["title", "url"])
        for video in videos:
            writer.writerow([video["title"], video["url"]])
    return filename


def main():
    if len(sys.argv) < 2:
        print("Usage: python extract_playlist_videos.py <playlist_url>")
        sys.exit(1)

    playlist_url = sys.argv[1]
    heading, videos = get_playlist_info(playlist_url)
    filename = save_as_csv(heading, videos)

    print(f"Playlist: {heading}")
    print(f"Total videos: {len(videos)}")
    print(f"Saved to {filename}")


if __name__ == "__main__":
    main()
