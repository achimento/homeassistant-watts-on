"""Constants for the Watts On integration."""

from __future__ import annotations
from typing import Final
from homeassistant.components.sensor import SensorStateClass, SensorDeviceClass
from homeassistant.const import UnitOfEnergy, UnitOfVolume
from .model import WattsOnSensorDescription

DOMAIN = "watts-on"
DEFAULT_NAME = "Watts On"

# Helper to create repeating sensor types
def _create_statistics_sensors(sensor_type: str, unit, icon: str) -> tuple[WattsOnSensorDescription, ...]:
    """Create daily, weekly, monthly, yearly and statistics sensors."""
    keys = ["statistics", "yesterday", "week", "month", "year"]
    names = ["Statistics", "Yesterday", "Week", "Month", "Year"]

    return tuple(
        WattsOnSensorDescription(
            sensor_type=sensor_type,
            key=key,
            name=f"{sensor_type.capitalize()} {name}" if key != "statistics" else f"{sensor_type.capitalize()} Statistics",
            entity_registry_enabled_default=True,
            native_unit_of_measurement=unit,
            suggested_display_precision=3,
            device_class=SensorDeviceClass.WATER if sensor_type == "water" else SensorDeviceClass.ENERGY,
            icon=icon,
            state_class=SensorStateClass.MEASUREMENT,
        )
        for key, name in zip(keys, names)
    )

# Water sensors
WATER_SENSOR_TYPES: Final[tuple[WattsOnSensorDescription, ...]] = _create_statistics_sensors(
    "water", UnitOfVolume.CUBIC_METERS, "mdi:water"
)

# Heating sensors
HEATING_SENSOR_TYPES: Final[tuple[WattsOnSensorDescription, ...]] = _create_statistics_sensors(
    "heating", UnitOfEnergy.MEGA_WATT_HOUR, "mdi:heat-wave"
)
