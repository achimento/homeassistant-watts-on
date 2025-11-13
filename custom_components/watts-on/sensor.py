"""Sensor platform for Watts On integration."""

from __future__ import annotations
from typing import Any
import logging
from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, DEFAULT_NAME, WATER_SENSOR_TYPES, EXTRA_WATER_SENSOR_TYPES, HEATING_SENSOR_TYPES, EXTRA_HEATING_SENSOR_TYPES
from .model import WattsOnSensorDescription
from .coordinator import WattsOnUpdateCoordinator

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(
    hass: HomeAssistant,
    config: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Watts On sensors based on a config entry."""

    coordinator: WattsOnUpdateCoordinator = hass.data[DOMAIN][config.entry_id]["coordinator"]

    sensors = []

    # Combine base and extra sensors - EXTRA is in case we want to have a flag for grouped sensors
    all_water_sensors = WATER_SENSOR_TYPES + EXTRA_WATER_SENSOR_TYPES
    all_heating_sensors = HEATING_SENSOR_TYPES + EXTRA_HEATING_SENSOR_TYPES

    # Add water sensors
    for description in all_water_sensors:
        sensors.append(WattsOnSensor(DEFAULT_NAME, coordinator, description))

    # Add heating sensors
    for description in all_heating_sensors:
        sensors.append(WattsOnSensor(DEFAULT_NAME, coordinator, description))

    async_add_entities(sensors, True)


class WattsOnSensor(CoordinatorEntity, SensorEntity):
    """Representation of a Watts On sensor."""
    entity_description: WattsOnSensorDescription

    def __init__(self, name: str, coordinator: WattsOnUpdateCoordinator, description):
        """Initialize the sensor."""
        super().__init__(coordinator)
        self.entity_description = description
        self._attrs: dict[str, Any] = {}
        self._attr_name = f"{name} {description.name}"
        self._attr_unique_id = f"{name.lower()}-{description.sensor_type}-{description.key}"

    @property
    def native_value(self):
        """Return the current sensor value from the coordinator data."""
        data = self.coordinator.data
        if not data:
            return None

        section = data.get(self.entity_description.sensor_type, {})
        key = self.entity_description.key

        # For statistics sensors with a series, return last value
        if key == "statistics":
            series = section.get("statistics")
            if series and isinstance(series, list) and len(series) > 0:
                return series[-1]["value"]
            return 0.0

        # For other summary statistics (day/week/month/year), ensure numeric
        val = section.get(key)
        if isinstance(val, list):
            # Sometimes your code returns a list, take last value if exists
            if len(val) > 0 and isinstance(val[-1], dict):
                return val[-1].get("value", 0.0)
            return 0.0
        if val is None:
            return 0.0
        return float(val)


    @property
    def extra_state_attributes(self):
        """Return extra attributes for statistics sensors."""
        data = self.coordinator.data
        if not data:
            return None

        section = data.get(self.entity_description.sensor_type, {})

        # Only attach full series to the main statistics sensor
        if self.entity_description.key == "statistics":
            series = section.get("statistics")
            if series:
                self._attrs["statistics"] = series

        # Always attach day/week/month/year values if available
        for key in ("statistics_day", "statistics_week", "statistics_month", "statistics_year"):
            if key in section:
                self._attrs[key] = section[key]

        return self._attrs

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
