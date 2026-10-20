import voluptuous as vol
from homeassistant.config_entries import ConfigFlow

from .times import DATA_DIR, DOMAIN, read_json


class JoPrayerTimesFlow(ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input=None):
        cities = await self.hass.async_add_executor_job(read_json, DATA_DIR / "cities.json")
        if user_input is not None:
            await self.async_set_unique_id(user_input["city"])
            self._abort_if_unique_id_configured()
            return self.async_create_entry(title=cities[user_input["city"]], data=user_input)
        return self.async_show_form(
            step_id="user", data_schema=vol.Schema({vol.Required("city", default="1"): vol.In(cities)})
        )
