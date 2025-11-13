"""Constants for the Watts On integration."""

from __future__ import annotations
from typing import Final
from homeassistant.components.sensor import SensorStateClass, SensorDeviceClass
from homeassistant.const import UnitOfEnergy, UnitOfVolume
from .model import WattsOnSensorDescription

DOMAIN = "watts-on"
DEFAULT_NAME = "Watts On"

# -----------------------------
# Water sensors
# -----------------------------
WATER_SENSOR_TYPES: Final[tuple[WattsOnSensorDescription, ...]] = (
    WattsOnSensorDescription(
        sensor_type="water",
        key="statistics",
        name="Water statistics",
        entity_registry_enabled_default=True,
        native_unit_of_measurement=UnitOfVolume.CUBIC_METERS,
        suggested_display_precision=3,
        device_class=SensorDeviceClass.WATER,
        icon="mdi:water",
        state_class=SensorStateClass.MEASUREMENT,
    ),
)

EXTRA_WATER_SENSOR_TYPES: Final[tuple[WattsOnSensorDescription, ...]] = (
    WattsOnSensorDescription(
        sensor_type="water",
        key="statistics_day",
        name="Water statistics day",
        entity_registry_enabled_default=True,
        native_unit_of_measurement=UnitOfVolume.CUBIC_METERS,
        suggested_display_precision=3,
        device_class=SensorDeviceClass.WATER,
        icon="mdi:water",
        state_class=SensorStateClass.MEASUREMENT,
    ),
    WattsOnSensorDescription(
        sensor_type="water",
        key="statistics_week",
        name="Water statistics week",
        entity_registry_enabled_default=True,
        native_unit_of_measurement=UnitOfVolume.CUBIC_METERS,
        suggested_display_precision=3,
        device_class=SensorDeviceClass.WATER,
        icon="mdi:water",
        state_class=SensorStateClass.MEASUREMENT,
    ),
    WattsOnSensorDescription(
        sensor_type="water",
        key="statistics_month",
        name="Water statistics month",
        entity_registry_enabled_default=True,
        native_unit_of_measurement=UnitOfVolume.CUBIC_METERS,
        suggested_display_precision=3,
        device_class=SensorDeviceClass.WATER,
        icon="mdi:water",
        state_class=SensorStateClass.MEASUREMENT,
    ),
    WattsOnSensorDescription(
        sensor_type="water",
        key="statistics_year",
        name="Water statistics year",
        entity_registry_enabled_default=True,
        native_unit_of_measurement=UnitOfVolume.CUBIC_METERS,
        suggested_display_precision=3,
        device_class=SensorDeviceClass.WATER,
        icon="mdi:water",
        state_class=SensorStateClass.MEASUREMENT,
    ),
)

# -----------------------------
# Heating sensors
# -----------------------------
HEATING_SENSOR_TYPES: Final[tuple[WattsOnSensorDescription, ...]] = (
    WattsOnSensorDescription(
        sensor_type="heating",
        key="statistics",
        name="Heating statistics",
        entity_registry_enabled_default=True,
        native_unit_of_measurement=UnitOfEnergy.MEGA_WATT_HOUR,
        suggested_display_precision=3,
        device_class=SensorDeviceClass.ENERGY,
        icon="mdi:heat-wave",
        state_class=SensorStateClass.MEASUREMENT,
    ),
)

EXTRA_HEATING_SENSOR_TYPES: Final[tuple[WattsOnSensorDescription, ...]] = (
    WattsOnSensorDescription(
        sensor_type="heating",
        key="statistics_day",
        name="Heating statistics day",
        entity_registry_enabled_default=True,
        native_unit_of_measurement=UnitOfEnergy.MEGA_WATT_HOUR,
        suggested_display_precision=3,
        device_class=SensorDeviceClass.ENERGY,
        icon="mdi:heat-wave",
        state_class=SensorStateClass.MEASUREMENT,
    ),
    WattsOnSensorDescription(
        sensor_type="heating",
        key="statistics_week",
        name="Heating statistics week",
        entity_registry_enabled_default=True,
        native_unit_of_measurement=UnitOfEnergy.MEGA_WATT_HOUR,
        suggested_display_precision=3,
        device_class=SensorDeviceClass.ENERGY,
        icon="mdi:heat-wave",
        state_class=SensorStateClass.MEASUREMENT,
    ),
    WattsOnSensorDescription(
        sensor_type="heating",
        key="statistics_month",
        name="Heating statistics month",
        entity_registry_enabled_default=True,
        native_unit_of_measurement=UnitOfEnergy.MEGA_WATT_HOUR,
        suggested_display_precision=3,
        device_class=SensorDeviceClass.ENERGY,
        icon="mdi:heat-wave",
        state_class=SensorStateClass.MEASUREMENT,
    ),
    WattsOnSensorDescription(
        sensor_type="heating",
        key="statistics_year",
        name="Heating statistics year",
        entity_registry_enabled_default=True,
        native_unit_of_measurement=UnitOfEnergy.MEGA_WATT_HOUR,
        suggested_display_precision=3,
        device_class=SensorDeviceClass.ENERGY,
        icon="mdi:heat-wave",
        state_class=SensorStateClass.MEASUREMENT,
    ),
)
