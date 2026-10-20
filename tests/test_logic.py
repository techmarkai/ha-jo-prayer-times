"""Run: python tests/test_logic.py"""
import importlib.util
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, ROOT / path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


scrape = load("scrape", "scraper/scrape.py")
times = load("times", "custom_components/jo_prayer_times/times.py")

# 12h site format -> 24h (real row from 20/10/2026 Amman, and a summer row)
assert scrape.to_24h(["05:21:00", "06:37:00", "12:22:00", "03:33:00", "06:05:00", "07:20:00"]) == \
    ["05:21", "06:37", "12:22", "15:33", "18:05", "19:20"]
assert scrape.to_24h(["03:40:00", "05:20:00", "12:40:00", "04:20:00", "07:50:00", "09:20:00"])[3:] == \
    ["16:20", "19:50", "21:20"]

# Fallback: missing year uses previous year's same day, Feb 29 -> Feb 28
data = {"2026-01-05": ["a"] * 6, "2027-03-01": ["b"] * 6, "2028-02-28": ["c"] * 6}
assert times.lookup(data, date(2026, 1, 5)) == (["a"] * 6, 2026)
assert times.lookup(data, date(2027, 1, 5)) == (["a"] * 6, 2026)
assert times.lookup(data, date(2026, 3, 1)) == (["b"] * 6, 2027)  # before first scrape -> next year
assert times.lookup(data, date(2028, 2, 29)) == (["c"] * 6, 2028)
assert times.lookup(data, date(2030, 7, 7)) == (None, None)

# Bundled data sanity: every city file has rows of 6 ordered HH:MM times
for f in (ROOT / "custom_components/jo_prayer_times/data").glob("*.json"):
    if f.name != "cities.json":
        for day, row in times.read_json(f).items():
            assert len(row) == 6 and row == sorted(row), (f.name, day, row)

print("ok")
sys.exit(0)
