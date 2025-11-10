from typing import List, Dict
from bs4 import BeautifulSoup

def parse_amenities(soup: BeautifulSoup) -> List[Dict]:
    """
    Attempts to parse amenities grouped by headings.
    Returns: [{ "title": "Apartment Features", "value": ["Washer/Dryer", "Air Conditioning"] }, ...]
    """
    out = []
    sections = soup.select("section, div")
    for sec in sections:
        h = sec.find(["h2", "h3"])
        if not h:
            continue
        title = h.get_text(" ", strip=True)
        if not title or "amenit" not in title.lower():
            # Some pages use titled lists; keep loose match but ensure we capture obvious amenities sections.
            continue

        values = []
        for li in sec.find_all("li"):
            t = li.get_text(" ", strip=True)
            if t and len(t) < 120:
                values.append(t)

        if values:
            out.append({"title": title, "value": sorted(set(values))})

    # Fallback: compact amenity pills
    if not out:
        pills = [p.get_text(" ", strip=True) for p in soup.select(".amenity, .amenities li, .amenities .pill") if p.get_text(strip=True)]
        if pills:
            out.append({"title": "Amenities", "value": sorted(set(pills))})

    return out