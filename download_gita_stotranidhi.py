"""
Download every Bhagavad Gita (Sanskrit / Devanagari) page listed in
https://stotranidhi.com/hi/category/bhagavad-gita-hi/ and save each as a .txt file.

stotranidhi.com blocks the default fetcher (403), so we send a browser User-Agent.
Verse text lives in <p> tags inside div.entry-content; we drop the breadcrumb,
navigation and donation boilerplate and split each verse at the danda (।) for
readability.

Run:
    ./venv/Scripts/python.exe download_gita_stotranidhi.py
Output: BG-Chanting/Gita-Sanskrit-stotranidhi/*.txt
"""

import re
import sys
import time
from pathlib import Path

import requests
from bs4 import BeautifulSoup

CATEGORY = "https://stotranidhi.com/hi/category/bhagavad-gita-hi/"
OUTDIR = Path("BG-Chanting/Gita-Sanskrit-stotranidhi")
HEADERS = {
    "User-Agent": ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                   "(KHTML, like Gecko) Chrome/124.0 Safari/537.36"),
    "Accept-Language": "en-US,en;q=0.9",
}
# Once a paragraph matches one of these, the rest of the page is nav / footer / ads.
STOP_MARKERS = (
    "पश्यतु ।", "पश्यतु।",              # "... सम्पूर्ण श्रीमद्भगवद्गीता पश्यतु ।" style footer link
    "Support this Dharma", "Buy Prabhata Stotranidhi",
    "Did you see any mistake", "Chant other stotras in",
    "मा तदुपरि", "మా తదుపరి",
)
# Paragraphs to drop but keep scanning past.
SKIP_MARKERS = ("English (IAST)", "Read in ", "→")

# Devanagari range; a paragraph that is mostly outside this (Telugu/Kannada/Tamil) is UI chrome.
_DEVA = re.compile(r"[ऀ-ॿ]")
_LETTER = re.compile(r"[^\s\W\d]", re.UNICODE)


def _mostly_non_devanagari(t: str) -> bool:
    letters = _LETTER.findall(t)
    if len(letters) < 8:
        return False
    deva = len(_DEVA.findall(t))
    return deva / len(letters) < 0.5


def fetch(url: str) -> str:
    r = requests.get(url, headers=HEADERS, timeout=30)
    r.raise_for_status()
    r.encoding = "utf-8"
    return r.text


def find_chapter_links(cat_html: str) -> list[str]:
    soup = BeautifulSoup(cat_html, "html.parser")
    links: dict[str, None] = {}
    for a in soup.select("a[href]"):
        href = a["href"].split("#")[0]
        if re.search(r"stotranidhi\.com/hi/[a-z0-9/-]*(bhagavadgita|bhagavad-gita)[a-z0-9/-]*-in-sanskrit/$", href):
            links.setdefault(href, None)
    return list(links)


def slug_to_name(url: str) -> str:
    slug = url.rstrip("/").rsplit("/", 1)[-1]
    m = re.search(r"chapter-0*(\d+)", slug)
    if m:
        return f"BG-Chapter-{int(m.group(1)):02d}"
    if "dhyanam" in slug:
        return "BG-00-Dhyanam"
    if "saptashloki" in slug:
        return "BG-Saptashloki"
    if "mahathmyam" in slug or "mahatmyam" in slug:
        return "BG-Mahatmyam"
    return slug


def extract(html: str) -> tuple[str, str]:
    soup = BeautifulSoup(html, "html.parser")
    h1 = soup.select_one("h1.entry-title, h1")
    title = h1.get_text(strip=True) if h1 else ""
    content = soup.select_one("div.entry-content")
    if content is None:
        return title, ""

    out: list[str] = []
    for p in content.find_all("p"):
        t = re.sub(r"\s+", " ", p.get_text(" ", strip=True)).strip()
        if not t:
            continue
        if any(m in t for m in STOP_MARKERS):
            break                         # nav / donation / footer boilerplate
        if t.startswith("स्तोत्रनिधि") or "<<" in t or ">>" in t:
            continue                      # breadcrumb / prev-next nav
        if any(m in t for m in SKIP_MARKERS) or _mostly_non_devanagari(t):
            continue                      # language switcher / other-script chrome
        t = re.sub(r"\s*।\s*", " ।\n", t)         # break at half-verse
        t = re.sub(r"\s*॥\s*", " ॥ ", t).strip()  # normalise full stop spacing
        out.append(t)
    return title, "\n\n".join(out)


def main() -> int:
    OUTDIR.mkdir(parents=True, exist_ok=True)
    print(f"Fetching category index: {CATEGORY}")
    links = find_chapter_links(fetch(CATEGORY))
    print(f"Found {len(links)} pages\n")

    # order: numbered chapters first, then the extras
    def sort_key(u: str):
        m = re.search(r"chapter-0*(\d+)", u)
        return (0, int(m.group(1))) if m else (1, u)

    manifest = []
    for i, url in enumerate(sorted(links, key=sort_key), 1):
        name = slug_to_name(url)
        try:
            title, body = extract(fetch(url))
        except requests.HTTPError as e:
            print(f"[{i}/{len(links)}] FAIL {name}: {e}")
            continue
        if "॥" not in body and "।" not in body:
            print(f"[{i}/{len(links)}] SKIP index/empty {name} ({url})")
            continue
        header = f"{title}\n\nस्रोत: {url}\n\n"
        path = OUTDIR / f"{name}.txt"
        path.write_text(header + body + "\n", encoding="utf-8")
        n_verses = body.count("॥")
        print(f"[{i}/{len(links)}] saved {path.name}  ({len(body)} chars, ~{n_verses} dandas)")
        manifest.append(f"{name}\t{url}")
        time.sleep(1)  # be polite

    (OUTDIR / "_manifest.txt").write_text("\n".join(manifest) + "\n", encoding="utf-8")
    print(f"\nDone. {len(manifest)} files in {OUTDIR}/")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
