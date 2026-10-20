from datetime import datetime, time, timedelta

from homeassistant.components.sensor import SensorDeviceClass, SensorEntity
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.util import dt as dt_util

from .times import DOMAIN, PRAYERS, lookup

TZ = dt_util.get_time_zone("Asia/Amman")
SCAN_INTERVAL = timedelta(minutes=1)


def day_times(data, day):
    times, year = lookup(data, day)
    if not times:
        return None, None
    return [datetime.combine(day, time.fromisoformat(t), TZ) for t in times], year


async def async_setup_entry(hass, entry, async_add_entities):
    async_add_entities([PrayerSensor(entry, p) for p in PRAYERS] + [NextPrayerSensor(entry)], True)


class PrayerSensor(SensorEntity):
    _attr_device_class = SensorDeviceClass.TIMESTAMP
    _attr_has_entity_name = True

    def __init__(self, entry, key):
        self._data = entry.runtime_data
        self._key = key
        self._attr_translation_key = key
        self._attr_unique_id = f"{entry.entry_id}_{key}"
        self._attr_device_info = DeviceInfo(identifiers={(DOMAIN, entry.entry_id)}, name=entry.title)

    async def async_update(self):
        today = datetime.now(TZ).date()
        times, year = day_times(self._data, today)
        self._attr_native_value = times[PRAYERS.index(self._key)] if times else None
        self._attr_extra_state_attributes = {"data_year": year, "fallback": year != today.year}


class NextPrayerSensor(PrayerSensor):
    def __init__(self, entry):
        super().__init__(entry, "next_prayer")

    async def async_update(self):
        now = datetime.now(TZ)
        for day in (now.date(), now.date() + timedelta(days=1)):
            times, year = day_times(self._data, day)
            for name, at in zip(PRAYERS, times or []):
                if name != "sunrise" and at > now:
                    self._attr_native_value = at
                    self._attr_extra_state_attributes = {"prayer": name, "data_year": year, "fallback": year != day.year}
                    return
        self._attr_native_value = None
