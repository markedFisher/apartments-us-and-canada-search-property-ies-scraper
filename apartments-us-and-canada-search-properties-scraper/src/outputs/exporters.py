import csv
import json
from pathlib import Path
from typing import Any, Dict, Iterable, List, Tuple

from slugify import slugify

def _flatten_record(rec: Dict[str, Any]) -> Dict[str, Any]:
    """Flatten selected nested fields for CSV export."""
    flat = dict(rec)
    # nested simple objects
    for field in ["monthlyRent", "bedrooms", "bathrooms", "squareFeet", "location"]:
        obj = flat.get(field) or {}
        if isinstance(obj, dict):
            for k, v in obj.items():
                flat[f"{field}.{k}"] = v
    # counts: keep
    # arrays: keep JSON string for CSV
    for arr_field in ["amenities", "fees", "petFees", "parkingFees", "models", "rentals", "carouselCollection"]:
        if arr_field in flat and isinstance(flat[arr_field], list):
            flat[arr_field] = json.dumps(flat[arr_field], ensure_ascii=False)
    return flat

def export_json(records: List[Dict[str, Any]], path: str) -> None:
    with open(path, "w", encoding="utf-8") as f:
        json.dump(records, f, ensure_ascii=False, indent=2)

def export_csv(records: List[Dict[str, Any]], path: str) -> None:
    if not records:
        Path(path).write_text("", encoding="utf-8")
        return
    flattened = [_flatten_record(r) for r in records]
    # Collect fields across all records
    fieldnames: List[str] = []
    for rec in flattened:
        for k in rec.keys():
            if k not in fieldnames:
                fieldnames.append(k)

    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(flattened)