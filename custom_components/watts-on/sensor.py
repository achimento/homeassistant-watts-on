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
        """Return the current sensor value from the coordinator data (last value of list)."""
        data = self.coordinator.data
        if not data:
            return 0.0

        section = data.get(self.entity_description.sensor_type, {})
        series = section.get(self.entity_description.key, [])

        if isinstance(series, list) and series:
            # Expect each entry to be a dict with 'value'
            last = series[-1]
            return float(last.get("value", 0.0))
        return 0.0

    @property
    def extra_state_attributes(self):
        """Return the full list for this sensor as attributes."""
        data = self.coordinator.data
        if not data:
            return None

        section = data.get(self.entity_description.sensor_type, {})
        series = section.get(self.entity_description.key, [])

        if isinstance(series, list) and series:
            return {self.entity_description.key: series}
        return None

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
