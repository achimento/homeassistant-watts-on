"""Sensor platform for Watts On integration."""

from __future__ import annotations
import logging
from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, WATER_SENSOR_TYPES, HEATING_SENSOR_TYPES
from .coordinator import WattsOnUpdateCoordinator

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Watts On sensors based on a config entry."""

    coordinator: WattsOnUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]["coordinator"]

    sensors = []

    # Add water sensors
    for description in WATER_SENSOR_TYPES:
        sensors.append(WattsOnSensor(coordinator, description))

    # Add heating sensors
    for description in HEATING_SENSOR_TYPES:
        sensors.append(WattsOnSensor(coordinator, description))

    async_add_entities(sensors, True)


class WattsOnSensor(CoordinatorEntity, SensorEntity):
    """Representation of a Watts On sensor."""

    def __init__(self, name: str, coordinator: WattsOnUpdateCoordinator, description):
        """Initialize the sensor."""
        super().__init__(coordinator)
        self.entity_description = description
        self._attr_name = f"{name} {description.name}"
        self._attr_unique_id = (
            f"{name.lower()}-{description.sensor_type}-{description.key}"
        )

    @property
    def native_value(self):
        """Return the current sensor value from the coordinator data."""
        data = self.coordinator.data
        if not data:
            return None
        section = data.get(self.entity_description.sensor_type, {})

        # For 'statistics' sensor, choose a representative numeric value
        if self.entity_description.key == "statistics":
            series = section.get("statistics")
            if series and isinstance(series, list):
                return series[-1]["value"] if series else 0.0
            return 0.0

        # For other sensors, use the extracted summary number directly
        return section.get(self.entity_description.key)

    @property
    def extra_state_attributes(self):
        """Return extra attributes for statistics sensors."""
        data = self.coordinator.data
        if not data:
            return None

        section = data.get(self.entity_description.sensor_type, {})
        attrs = {}

        # Only attach the detailed series on the "statistics" sensor
        if self.entity_description.key == "statistics":
            series = section.get("statistics")
            if series:
                attrs["statistics"] = series

        # Always include the other summary statistics as attributes for convenience
        for key in ("yesterday", "week", "month", "year"):
            if key in section:
                attrs[key] = section[key]

        return attrs or None

    @property
    def device_class(self):
        return self.entity_description.device_class

    @property
    def state_class(self):
        return self.entity_description.state_class

    @property
    def native_unit_of_measurement(self):
        return self.entity_description.native_unit_of_measurement

    @property
    def icon(self):
        return self.entity_description.icon

    @property
    def available(self) -> bool:
        return self.coordinator.last_update_success
