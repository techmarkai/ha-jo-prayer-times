"""Scrape official prayer times from awqaf.gov.jo into per-city JSON files.

The site's search button is broken server-side (DataBinding error), but grid paging
with empty dates returns the selected city's times from today until Dec 31. Running
daily and merging into existing files builds the full year.
"""
import http.cookiejar
import json
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

URL = "https://www.awqaf.gov.jo/ar/Pages/PrayerTime"
DATA = Path(__file__).resolve().parent.parent / "custom_components" / "jo_prayer_times" / "data"
GRID = "ctl00$MainContent$gvWebparts"
ENGLISH = {
    "1": "Amman, Balqa, Zarqa, Madaba", "2": "Irbid", "3": "Karak", "4": "Tafilah",
    "5": "Ma'an", "6": "Aqaba", "7": "Northern Jordan Valley", "8": "Jerash & Ajloun",
    "9": "Mafraq", "11": "Dhiban", "12": "Azraq", "13": "Central Jordan Valley",
    "14": "Shoubak & Petra", "15": "Dhulail & Hashemiya", "19": "Ruwaished", "33": "Jerusalem",
}


def to_24h(times):
    """Site uses a 12h clock without AM/PM: fajr/sunrise are AM, dhuhr is around noon, the rest PM."""
    out = []
    for i, t in enumerate(times):
        h, m = int(t[:2]), int(t[3:5])
        if (i == 2 and h < 10) or (i > 2 and h < 12):
            h += 12
        out.append(f"{h:02d}:{m:02d}")
    if out != sorted(out):
        raise ValueError(f"times not in order: {times}")
    return out


def parse(html):
    rows = {}
    for i, d in re.findall(r'lbldate_(\d+)">(\d\d/\d\d/\d{4})', html):
        times = [re.search(rf'Labpayr{k}_{i}">([\d:]+)', html)[1] for k in range(1, 7)]
        dd, mm, yyyy = d.split("/")
        rows[f"{yyyy}-{mm}-{dd}"] = to_24h(times)
    return rows


def pages(html):
    return {int(p) for p in re.findall(r"Page\$(\d+)&#39;", html)}


def fetch_city(city):
    op = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(http.cookiejar.CookieJar()))
    op.addheaders = [("User-Agent", "Mozilla/5.0")]
    html = op.open(URL, timeout=60).read().decode()
    if 2 not in pages(html):
        # Single page (late December): no postback available to switch city; earlier runs have it.
        return parse(html) if city == "1" else {}

    def go(page):
        form = dict(re.findall(r'<input type="hidden" name="([^"]+)" id="[^"]*" value="([^"]*)"', html))
        form.update({"ctl00$MainContent$DropCompany": city, "ctl00$MainContent$txtFromDate": "",
                     "ctl00$MainContent$txtToDate": "", "__EVENTTARGET": GRID, "__EVENTARGUMENT": f"Page${page}"})
        return op.open(URL, urllib.parse.urlencode(form).encode(), timeout=120).read().decode()

    html = go(2)  # switches the grid to this city
    html = go(1)
    rows, page = parse(html), 1
    while page + 1 in pages(html):
        page += 1
        html = go(page)
        rows.update(parse(html))
    return rows


def main():
    html = urllib.request.urlopen(urllib.request.Request(URL, headers={"User-Agent": "Mozilla/5.0"}), timeout=60).read().decode()
    options = re.findall(r'<option(?: selected="selected")? value="(\d+)">([^<]+)</option>', html)
    cities = {c: n.strip() for c, n in options if c != "0"}
    DATA.mkdir(parents=True, exist_ok=True)
    failed = 0
    for city, name in cities.items():
        path = DATA / f"{city}.json"
        old = json.loads(path.read_text("utf-8")) if path.exists() else {}
        try:
            new = fetch_city(city)
        except (urllib.error.URLError, ValueError, TimeoutError) as err:
            print(f"{city}: FAILED {err}", file=sys.stderr)
            failed += 1
            continue
        print(f"{city} {ENGLISH.get(city, name)}: {len(new)} days")
        if new:
            path.write_text(json.dumps(dict(sorted({**old, **new}.items())), separators=(",", ":")), "utf-8")
    listing = {c: f"{ENGLISH.get(c, n)} / {n}" for c, n in cities.items() if (DATA / f"{c}.json").exists()}
    (DATA / "cities.json").write_text(json.dumps(listing, ensure_ascii=False, indent=1), "utf-8")
    sys.exit(1 if failed == len(cities) else 0)


if __name__ == "__main__":
    main()
