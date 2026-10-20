# Jordan Prayer Times (Awqaf) for Home Assistant

Official prayer times from the Jordanian Ministry of Awqaf
([awqaf.gov.jo/ar/Pages/PrayerTime](https://www.awqaf.gov.jo/ar/Pages/PrayerTime)), per city, working **offline**.

- All times are bundled inside the integration — no internet needed.
- A GitHub Action scrapes the ministry site every day and commits any new times.
- When online, the integration also pulls the latest times from this repo every 12 hours.
- **Fallback:** if a year isn't published yet, the same day from the previous year is used
  (e.g. Fajr on 5/1/2027 = Fajr on 5/1/2026). Sensors expose `fallback: true` and `data_year` when this happens.

## Install (HACS)

1. HACS → ⋮ → Custom repositories → add `https://github.com/techmarkai/ha-jo-prayer-times`, type **Integration**.
2. Install **Jordan Prayer Times (Awqaf)**, restart Home Assistant.
3. Settings → Devices & services → Add integration → **Jordan Prayer Times** → pick your city.

Manual: copy `custom_components/jo_prayer_times` into your `config/custom_components/`.

## Entities

Timestamp sensors: Fajr, Sunrise, Dhuhr, Asr, Maghrib, Isha, and Next prayer (attribute `prayer`).

## Cities

Amman/Balqa/Zarqa/Madaba, Irbid, Karak, Tafilah, Ma'an, Aqaba, Northern Jordan Valley, Jerash & Ajloun,
Mafraq, Dhiban, Azraq, Central Jordan Valley, Shoubak & Petra, Dhulail & Hashemiya, Ruwaished.
(Jerusalem is listed on the site but has no data there.)

## Notes

The site only exposes times from *today* until 31 December, so the archive builds up day by day
from the first scrape (20 Oct 2026). Earlier dates fall back to the nearest year available.
