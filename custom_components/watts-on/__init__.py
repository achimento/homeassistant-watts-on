"""The Watts On integration."""

from __future__ import annotations
import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant

from .const import DOMAIN
from .pywatts_on import WattsOnApi
from .coordinator import WattsOnUpdateCoordinator

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[Platform] = [Platform.SENSOR]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Watts On from a config entry."""
    # Load stored tokens if available
    tokens = entry.data.get("tokens")

    # Initialize API client
    api = WattsOnApi(
        username=entry.data["username"],
        password=entry.data["password"],
        water_device_id=entry.data.get("water_device_id"),
        heating_device_id=entry.data.get("heating_device_id"),
        tokens=tokens,
    )

    # Create coordinator
    coordinator = WattsOnUpdateCoordinator(hass, entry, api)
    await coordinator.async_refresh()

    # Ensure refreshed tokens are persisted
    if api.tokens != tokens:
        hass.config_entries.async_update_entry(
            entry,
            data={**entry.data, "tokens": api.tokens},
        )
        _LOGGER.debug("Stored updated tokens in config entry")

    # Store coordinator for platforms
    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = {
        "coordinator": coordinator,
        "api": api,
    }

    # Forward setup to platforms (sensor, switch, etc.)
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id, None)
    return unload_ok
