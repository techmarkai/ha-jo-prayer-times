"""Jordan prayer times from the Ministry of Awqaf, bundled for offline use and refreshed from GitHub."""
import logging
from datetime import timedelta
from pathlib import Path

import aiohttp
from homeassistant.components.frontend import add_extra_js_url
from homeassistant.components.http import StaticPathConfig
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.event import async_track_time_interval
from homeassistant.helpers.storage import Store
from homeassistant.loader import async_get_integration

from .times import DATA_DIR, DOMAIN, read_json

_LOGGER = logging.getLogger(__name__)
RAW = "https://raw.githubusercontent.com/techmarkai/ha-jo-prayer-times/main/custom_components/jo_prayer_times/data/{}.json"

CONFIG_SCHEMA = cv.config_entry_only_config_schema(DOMAIN)
CARD_URL = f"/{DOMAIN}"


async def async_setup(hass: HomeAssistant, config) -> bool:
    """Serve the Lovelace card so it works without installing anything else."""
    await hass.http.async_register_static_paths(
        [StaticPathConfig(CARD_URL, str(Path(__file__).parent / "www"), False)]
    )
    # Version in the URL so browsers fetch the new card after each update instead of a cached copy.
    version = (await async_get_integration(hass, DOMAIN)).version
    add_extra_js_url(hass, f"{CARD_URL}/jo-prayer-card.js?v={version}")
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    city = entry.data["city"]
    store = Store(hass, 1, f"{DOMAIN}_{city}")
    bundled = await hass.async_add_executor_job(read_json, DATA_DIR / f"{city}.json")
    data = {**bundled, **(await store.async_load() or {})}
    entry.runtime_data = data

    async def refresh(_now=None):
        try:
            async with async_get_clientsession(hass).get(
                RAW.format(city), timeout=aiohttp.ClientTimeout(total=30)
            ) as resp:
                resp.raise_for_status()
                fresh = await resp.json(content_type=None)
        except (aiohttp.ClientError, TimeoutError, ValueError) as err:
            _LOGGER.debug("Offline or GitHub unreachable, using local data: %s", err)
            return
        data.update({k: v for k, v in fresh.items() if isinstance(v, list) and len(v) == 6})
        await store.async_save(data)

    entry.async_create_background_task(hass, refresh(), f"{DOMAIN}_refresh")
    entry.async_on_unload(async_track_time_interval(hass, refresh, timedelta(hours=12)))
    await hass.config_entries.async_forward_entry_setups(entry, ["sensor"])
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    return await hass.config_entries.async_unload_platforms(entry, ["sensor"])
