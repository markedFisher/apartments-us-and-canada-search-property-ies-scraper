import json
import re
from typing import Any, Dict, List, Optional

from bs4 import BeautifulSoup

from .amenities_parser import parse_amenities
from .media_parser import parse_media

def _parse_json_ld(soup: BeautifulSoup) -> Dict[str, Any]:
    out: Dict[str, Any] = {}
    for script in soup.find_all("script", type=lambda t: t and "ld+json" in t):
        text = script.string or script.get_text()
        if not text:
            continue
        try:
            data = json.loads(text)
        except Exception:
            continue

        def step(obj):
            nonlocal out
            if isinstance(obj, dict):
                if obj.get("@type") in {"Apartment", "Place", "Residence", "Organization"}:
                    out.update(obj)
                for v in obj.values():
                    step(v)
            elif isinstance(obj, list):
                for v in obj:
                    step(v)

        step(data)
    return out

def _extract_text(soup: BeautifulSoup, selector: str) -> Optional[str]:
    node = soup.select_one(selector)
    if not node:
        return None
    return " ".join(node.get_text(" ", strip=True).split())

def _parse_numbers(text: str) -> Optional[float]:
    if not text:
        return None
    m = re.search(r"([\d,.]+)", text)
    if not m:
        return None
    try:
        return float(m.group(1).replace(",", ""))
    except Exception:
        return None

def _parse_address(json_ld: Dict[str, Any], soup: BeautifulSoup) -> Dict[str, Any]:
    address = {"fullAddress": None, "listingCity": None, "listingState": None, "listingZip": None, "listingCountry": None}
    adr = json_ld.get("address") or {}
    if isinstance(adr, dict):
        street = " ".join(filter(None, [adr.get("streetAddress")]))
        city = adr.get("addressLocality")
        state = adr.get("addressRegion")
        postal = adr.get("postalCode")
        country = adr.get("addressCountry") or "US"
        parts = [street, city, state, postal, country]
        address["fullAddress"] = " ".join([p for p in parts if p])
        address["listingCity"] = city
        address["listingState"] = state
        address["listingZip"] = postal
        address["listingCountry"] = country

    if not address["fullAddress"]:
        # fallback: page title or meta
        title = _extract_text(soup, "h1, h1 span")
        meta = _extract_text(soup, 'meta[property="og:title"]')
        address["fullAddress"] = title or meta

    return address

def _parse_geo(json_ld: Dict[str, Any]) -> Dict[str, Any]:
    loc = {"location": {"latitude": None, "longitude": None}}
    geo = json_ld.get("geo")
    if isinstance(geo, dict):
        lat = geo.get("latitude")
        lon = geo.get("longitude")
        try:
            loc["location"]["latitude"] = float(lat) if lat is not None else None
            loc["location"]["longitude"] = float(lon) if lon is not None else None
        except Exception:
            pass
    return loc

def _guess_rent_ranges(soup: BeautifulSoup) -> Dict[str, Any]:
    text = soup.get_text(" ", strip=True)
    # Common patterns like "$1,250–$1,600"
    min_rent, max_rent = None, None
    m = re.search(r"\$?\s*([\d,]+)\s*[–-]\s*\$?\s*([\d,]+)\s*(?:/mo|per month|monthly)?", text, re.I)
    if m:
        min_rent = float(m.group(1).replace(",", ""))
        max_rent = float(m.group(2).replace(",", ""))
    else:
        m = re.search(r"\$?\s*([\d,]+)\s*(?:/mo|per month|monthly)", text, re.I)
        if m:
            min_rent = max_rent = float(m.group(1).replace(",", ""))

    return {"monthlyRent": {"min": min_rent, "max": max_rent}, "listingMinRent": min_rent, "listingMaxRent": max_rent}

def _guess_beds_baths(soup: BeautifulSoup) -> Dict[str, Any]:
    text = soup.get_text(" ", strip=True)
    beds = None
    baths = None
    m = re.search(r"(\d+(?:\.\d+)?)\s*beds?", text, re.I)
    if m:
        beds = float(m.group(1))
    m = re.search(r"(\d+(?:\.\d+)?)\s*baths?", text, re.I)
    if m:
        baths = float(m.group(1))
    return {"bedrooms": {"min": beds, "max": beds}, "bathrooms": {"min": baths, "max": baths}}

def normalize_record(record: Dict[str, Any]) -> Dict[str, Any]:
    # Ensure all top-level fields exist for stable schema
    defaults = {
        "url": record.get("url"),
        "fullAddress": None,
        "monthlyRent": {"min": None, "max": None},
        "bedrooms": {"min": None, "max": None},
        "bathrooms": {"min": None, "max": None},
        "squareFeet": {"min": None, "max": None},
        "propertyInformation": [],
        "scores": {"walkScore": None, "transitScore": None, "bikeScore": None, "soundScore": None},
        "fees": [],
        "petFees": [],
        "parkingFees": [],
        "amenities": [],
        "models": [],
        "listingId": None,
        "phoneNumber": None,
        "listingCity": None,
        "listingState": None,
        "listingZip": None,
        "listingCountry": None,
        "listingNeighborhood": None,
        "listingCounty": None,
        "listingDMA": None,
        "listingMinRent": None,
        "listingMaxRent": None,
        "location": {"latitude": None, "longitude": None},
        "rentals": [],
        "carouselCollection": [],
        "imageCount": None,
        "photoCount": None,
        "videoCount": None,
        "has3DTour": False,
        "hasVideo": False,
        "virtualTourCount": None,
        "profileType": None,
        "propertyType": None,
    }
    for k, v in defaults.items():
        record.setdefault(k, v)
    return record

def parse_listing_page(url: str, html: str) -> Dict[str, Any]:
    soup = BeautifulSoup(html, "lxml")
    json_ld = _parse_json_ld(soup)

    out: Dict[str, Any] = {"url": url}

    # Address & geo
    out.update(_parse_address(json_ld, soup))
    out.update(_parse_geo(json_ld))

    # Title/type/phone
    out["propertyType"] = json_ld.get("@type") if isinstance(json_ld, dict) else None
    # Phone sometimes embedded as tel: or visible number
    phone = None
    for a in soup.select('a[href^="tel:"]'):
        phone = a.get("href", "").replace("tel:", "").strip()
        if phone:
            break
    if not phone:
        m = re.search(r"\(?\d{3}\)?[-\s]?\d{3}[-\s]?\d{4}", soup.get_text(" ", strip=True))
        if m:
            phone = m.group(0)
    out["phoneNumber"] = phone

    # Rents/beds/baths/sqft
    out.update(_guess_rent_ranges(soup))
    sqft = None
    m_sq = re.search(r"([\d,]+)\s*(?:sq\.?\s*ft|square\s*feet)", soup.get_text(" ", strip=True), re.I)
    if m_sq:
        sqft = float(m_sq.group(1).replace(",", ""))
    out["squareFeet"] = {"min": sqft, "max": sqft}

    # Listing ID
    m_id = re.search(r"/([a-z0-9]{3,8})/?$", url)
    out["listingId"] = m_id.group(1) if m_id else None

    # Amenities & media
    out["amenities"] = parse_amenities(soup)
    media = parse_media(soup)
    out.update(media)

    # Rentals (basic heuristic)
    rentals: List[dict] = []
    for row in soup.select("table tr"):
        cells = [c.get_text(" ", strip=True) for c in row.find_all(["td", "th"])]
        if len(cells) >= 3 and any("bed" in c.lower() for c in cells) and any("$" in c for c in cells):
            try:
                beds = _parse_numbers(" ".join([c for c in cells if "bed" in c.lower()]))
                baths = _parse_numbers(" ".join([c for c in cells if "bath" in c.lower()]))
                rent = _parse_numbers(" ".join([c for c in cells if "$" in c]))
                sqft_local = _parse_numbers(" ".join([c for c in cells if "sq" in c.lower()]))
                rentals.append(
                    {
                        "Beds": beds,
                        "Baths": baths,
                        "Rent": rent,
                        "Deposit": None,
                        "SquareFeet": sqft_local,
                        "UnitNumber": None,
                        "AvailableDateText": None,
                        "MinLeaseTerm": None,
                        "MaxLeaseTerm": None,
                    }
                )
            except Exception:
                continue
    out["rentals"] = rentals

    return normalize_record(out)