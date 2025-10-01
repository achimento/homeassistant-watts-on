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

    def __init__(self, coordinator: WattsOnUpdateCoordinator, description):
        """Initialize the sensor."""
        super().__init__(coordinator)
        self.entity_description = description
        self._attr_name = description.name
        self._attr_unique_id = f"{description.sensor_type}_{description.key}"
        self._attr_entity_id = f"sensor.watts_on_{description.sensor_type}_{description.key}"

    @property
    def native_value(self):
        """Return the current sensor value from the coordinator data."""
        data = self.coordinator.data
        if not data:
            return None
        # Access the statistics data based on sensor type and key
        return data.get(self.entity_description.sensor_type, {}).get(self.entity_description.key)

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
