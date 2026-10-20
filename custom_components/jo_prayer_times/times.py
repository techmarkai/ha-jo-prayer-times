"""Constants and lookup logic. No Home Assistant imports so it can be tested standalone."""
import json
from datetime import date
from pathlib import Path

DOMAIN = "jo_prayer_times"
DATA_DIR = Path(__file__).parent / "data"
PRAYERS = ("fajr", "sunrise", "dhuhr", "asr", "maghrib", "isha")
# Same day from the previous years first, then later years (covers months before the first scrape).
OFFSETS = (0, -1, -2, -3, -4, -5, 1, 2, 3)


def read_json(path):
    return json.loads(path.read_text("utf-8")) if path.exists() else {}


def lookup(data, day: date):
    """Return (times, year_used) for day, or (None, None) if no year has that date."""
    for offset in OFFSETS:
        year = day.year + offset
        md = day.strftime("%m-%d")
        if md == "02-29" and f"{year}-02-29" not in data:
            md = "02-28"
        if times := data.get(f"{year}-{md}"):
            return times, year
    return None, None
