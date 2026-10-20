# Jordan Prayer Times (Awqaf) for Home Assistant

Official prayer times from the Jordanian Ministry of Awqaf
([awqaf.gov.jo/ar/Pages/PrayerTime](https://www.awqaf.gov.jo/ar/Pages/PrayerTime)), per city, working **offline**.

- All times are bundled inside the integration — no internet needed.
- On **1 January** a GitHub Action scrapes the full year from the ministry site (retrying daily through
  January if it's published late, plus a monthly check for corrections). New times are published as a
  GitHub release, so Home Assistant shows an update via HACS.
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

## Auto-install updates

The sensors already pull new times from GitHub on their own. To also auto-install HACS releases:

```yaml
automation:
  - alias: Auto-update Jordan prayer times
    triggers:
      - trigger: state
        entity_id: update.jordan_prayer_times_awqaf_update
        to: "on"
    actions:
      - action: update.install
        target:
          entity_id: update.jordan_prayer_times_awqaf_update
```

## Notes

The site only lists times from *today* until 31 December (its date search is broken server-side),
which is why the full-year scrape runs on 1 January. 2026 was first scraped on 20 Oct, so
1 Jan – 19 Oct 2026 falls back to the 2027 times once those are available.
