from typing import Dict, List
from bs4 import BeautifulSoup

def parse_media(soup: BeautifulSoup) -> Dict:
    images: List[Dict] = []
    for img in soup.find_all("img"):
        src = img.get("data-src") or img.get("src")
        if not src:
            continue
        alt = img.get("alt") or None
        w = img.get("width")
        h = img.get("height")
        try:
            w = int(w) if w else None
            h = int(h) if h else None
        except Exception:
            w = h = None
        images.append({"src": src, "alt": alt, "width": w, "height": h})

    # Count media heuristically
    photo_count = len(images) if images else None
    video_count = len(soup.select("video, source[type*='video']")) or None
    has_3d = bool(soup.find(string=lambda s: s and "3D" in s)) or False

    return {
        "carouselCollection": images[:50],  # cap for CSV practicality
        "imageCount": photo_count,
        "photoCount": photo_count,
        "videoCount": video_count,
        "has3DTour": has_3d,
        "hasVideo": bool(video_count),
        "virtualTourCount": None,
    }