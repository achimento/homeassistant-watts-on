"""Coordinator for The Watts On integration."""

from __future__ import annotations
from datetime import timedelta
import logging

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from homeassistant.config_entries import ConfigEntry

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


class WattsOnUpdateCoordinator(DataUpdateCoordinator):
    """Manages fetching data from the Watts On API."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry, api_client, update_interval: int = 1800):
        """
        Initialize coordinator.

        :param hass: HomeAssistant instance
        :param entry: ConfigEntry for this integration
        :param api_client: Your custom API client instance
        :param update_interval: Refresh interval in seconds (default 30 min)
        """
        super().__init__(
            hass,
            _LOGGER,
            name="Watts On Coordinator",
            update_interval=timedelta(seconds=update_interval),
        )
        self.api = api_client
        self.entry = entry

    async def _async_update_data(self):
        """Fetch data from the API and persist updated tokens if needed."""
        try:
            # Fetch whatever main payload your integration needs
            data = await self.hass.async_add_executor_job(self.api.fetch_data)
            _LOGGER.error("Watts On data: %s", data)

            # Check if tokens changed (refreshed / re-logged in)
            stored_tokens = self.entry.data.get("tokens")
            if self.api.tokens and self.api.tokens != stored_tokens:
                _LOGGER.debug("Updating config entry with refreshed tokens")
                self.hass.config_entries.async_update_entry(
                    self.entry,
                    data={**self.entry.data, "tokens": self.api.tokens},
                )

            return data

        except Exception as err:
            _LOGGER.error("Error fetching Watts On data: %s", err)
            raise UpdateFailed(err)
