"""Configuration and options flow for Mein Speiseplan."""
from homeassistant import config_entries
import voluptuous as vol
from .const import DOMAIN


class MealPlannerConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input=None):
        if self._async_current_entries():
            return self.async_abort(reason="single_instance_allowed")
        return self.async_create_entry(title="Mein Speiseplan", data={})

    @staticmethod
    def async_get_options_flow(config_entry):
        return MealPlannerOptionsFlow()


class MealPlannerOptionsFlow(config_entries.OptionsFlow):
    """For now, settings are handled by the Speiseplan sidebar panel."""

    async def async_step_init(self, user_input=None):
        if user_input is not None:
            return self.async_create_entry(title="", data={})
        return self.async_show_form(step_id="init", data_schema=vol.Schema({}))
