"""Config flow for The Watts On integration."""

from __future__ import annotations

from typing import Any
import voluptuous as vol
import logging

from homeassistant import config_entries
from homeassistant.data_entry_flow import FlowResult

from .const import DOMAIN, DEFAULT_NAME

_LOGGER = logging.getLogger(__name__)


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Watts On."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        if user_input is not None:
            _LOGGER.debug("User input received: %s", user_input)

            # Create and store the entry
            return self.async_create_entry(
                title=DEFAULT_NAME,
                data=user_input,
            )

        # Schema shown when form is displayed
        data_schema = vol.Schema(
            {
                vol.Required("username"): str,
                vol.Required("password"): str,
                vol.Optional("water_device_id"): str,
                vol.Optional("heating_device_id"): str,
            }
        )

        return self.async_show_form(
            step_id="user",
            data_schema=data_schema,
        )