"""Sensor platform for Xiaomi Mi Robot Vacuum-Mop 1C diagnostic data."""
from __future__ import annotations

import logging

from homeassistant.components.sensor import (
    SensorEntity,
    SensorEntityDescription,
    SensorDeviceClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import PERCENTAGE, UnitOfTime
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity import EntityCategory
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

SENSOR_DESCRIPTIONS: tuple[SensorEntityDescription, ...] = (
    SensorEntityDescription(
        key="battery",
        translation_key="battery",
        name="Battery",
        native_unit_of_measurement=PERCENTAGE,
        device_class=SensorDeviceClass.BATTERY,
        icon="mdi:battery",
    ),
    SensorEntityDescription(
        key="main_brush_life_level",
        translation_key="main_brush_life_level",
        name="Main Brush Life",
        native_unit_of_measurement=PERCENTAGE,
        entity_category=EntityCategory.DIAGNOSTIC,
        icon="mdi:brush",
    ),
    SensorEntityDescription(
        key="main_brush_time_left",
        translation_key="main_brush_time_left",
        name="Main Brush Time Left",
        native_unit_of_measurement=UnitOfTime.HOURS,
        entity_category=EntityCategory.DIAGNOSTIC,
        icon="mdi:brush",
    ),
    SensorEntityDescription(
        key="side_brush_life_level",
        translation_key="side_brush_life_level",
        name="Side Brush Life",
        native_unit_of_measurement=PERCENTAGE,
        entity_category=EntityCategory.DIAGNOSTIC,
        icon="mdi:brush",
    ),
    SensorEntityDescription(
        key="side_brush_time_left",
        translation_key="side_brush_time_left",
        name="Side Brush Time Left",
        native_unit_of_measurement=UnitOfTime.HOURS,
        entity_category=EntityCategory.DIAGNOSTIC,
        icon="mdi:brush",
    ),
    SensorEntityDescription(
        key="filter_life_level",
        translation_key="filter_life_level",
        name="Filter Life",
        native_unit_of_measurement=PERCENTAGE,
        entity_category=EntityCategory.DIAGNOSTIC,
        icon="mdi:air-filter",
    ),
    SensorEntityDescription(
        key="filter_left_time",
        translation_key="filter_left_time",
        name="Filter Time Left",
        native_unit_of_measurement=UnitOfTime.HOURS,
        entity_category=EntityCategory.DIAGNOSTIC,
        icon="mdi:air-filter",
    ),
    SensorEntityDescription(
        key="total_cleaning_count",
        translation_key="total_cleaning_count",
        name="Total Cleaning Count",
        entity_category=EntityCategory.DIAGNOSTIC,
        icon="mdi:counter",
    ),
    SensorEntityDescription(
        key="total_cleaning_area",
        translation_key="total_cleaning_area",
        name="Total Cleaning Area",
        entity_category=EntityCategory.DIAGNOSTIC,
        icon="mdi:texture-box",
    ),
    SensorEntityDescription(
        key="cleaning_area",
        translation_key="cleaning_area",
        name="Current Cleaning Area",
        icon="mdi:texture-box",
    ),
    SensorEntityDescription(
        key="cleaning_time",
        translation_key="cleaning_time",
        name="Current Cleaning Time",
        icon="mdi:timer-outline",
    ),
    SensorEntityDescription(
        key="status",
        translation_key="vacuum_error",
        name="Last Error",
        entity_category=EntityCategory.DIAGNOSTIC,
        icon="mdi:alert-circle-outline",
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up sensor entities from a config entry."""
    unique_id = entry.unique_id or entry.entry_id
    entities = [
        DreameVacuumSensor(entry, unique_id, description)
        for description in SENSOR_DESCRIPTIONS
    ]
    async_add_entities(entities)


class DreameVacuumSensor(SensorEntity):
    """Sensor entity for Xiaomi Mi Robot Vacuum-Mop 1C consumable/diagnostic data."""

    _attr_has_entity_name = True

    def __init__(
        self,
        entry: ConfigEntry,
        unique_id: str,
        description: SensorEntityDescription,
    ) -> None:
        """Initialize the sensor."""
        self.entity_description = description
        self._entry = entry
        self._attr_unique_id = f"{unique_id}_{description.key}"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, unique_id)},
        )

    async def async_update(self) -> None:
        """Update sensor value from shared state data."""
        state_key = f"{self._entry.entry_id}_state"
        state_data = self.hass.data.get(DOMAIN, {}).get(state_key, {})
        value = state_data.get(self.entity_description.key)
        self._attr_native_value = value
