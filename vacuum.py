"""Vacuum platform for Xiaomi Mi Robot Vacuum-Mop 1C."""
from __future__ import annotations

from datetime import timedelta
from functools import partial
import logging

SCAN_INTERVAL = timedelta(seconds=30)

from homeassistant.components.vacuum import (
    StateVacuumEntity,
    VacuumActivity,
    VacuumEntityFeature,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN, ERROR_CODE_TO_ERROR, SPEED_CODE_TO_NAME, WATER_CODE_TO_NAME
from .miio import DeviceException, DreameVacuum

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up vacuum entity from a config entry."""
    vacuum: DreameVacuum = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([DreameVacuumEntity(entry, vacuum)], update_before_add=True)


class DreameVacuumEntity(StateVacuumEntity):
    """Representation of a Xiaomi Mi Robot Vacuum-Mop 1C (Dreame MC1808)."""

    _attr_has_entity_name = True
    _attr_name = None
    _attr_supported_features = (
        VacuumEntityFeature.STATE
        | VacuumEntityFeature.LOCATE
        | VacuumEntityFeature.RETURN_HOME
        | VacuumEntityFeature.START
        | VacuumEntityFeature.STOP
        | VacuumEntityFeature.PAUSE
        | VacuumEntityFeature.FAN_SPEED
        | VacuumEntityFeature.SEND_COMMAND
    )
    _attr_fan_speed_list = list(SPEED_CODE_TO_NAME.values())
    _attr_translation_key = "dreame_vacuum"

    def __init__(self, entry: ConfigEntry, vacuum: DreameVacuum) -> None:
        """Initialize the vacuum entity."""
        self._vacuum = vacuum
        self._entry = entry
        self._attr_unique_id = entry.unique_id or entry.entry_id
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, self._attr_unique_id)},
            name="Xiaomi Mi Robot Vacuum-Mop 1C",
            manufacturer="Xiaomi / Dreame",
            model="dreame.vacuum.mc1808",
        )
        self._fan_speeds_reverse: dict[str, int] = {v: k for k, v in SPEED_CODE_TO_NAME.items()}
        self._water_level_reverse: dict[str, int] = {v: k for k, v in WATER_CODE_TO_NAME.items()}

    @property
    def extra_state_attributes(self) -> dict | None:
        """Return water level attributes (consumables are separate sensors)."""
        if self._attr_activity is None:
            return None
        return {
            "water_level": self._water_level_name,
            "water_level_list": list(WATER_CODE_TO_NAME.values()),
        }

    async def async_locate(self, **kwargs) -> None:
        """Locate the vacuum cleaner."""
        await self._try_command("Unable to locate: %s", self._vacuum.find)

    async def async_start(self) -> None:
        """Start or resume the cleaning task."""
        await self._try_command("Unable to start: %s", self._vacuum.start)

    async def async_stop(self, **kwargs) -> None:
        """Stop the vacuum cleaner."""
        await self._try_command("Unable to stop: %s", self._vacuum.stop)

    async def async_pause(self) -> None:
        """Pause the cleaning task."""
        await self._try_command("Unable to pause: %s", self._vacuum.stop)

    async def async_return_to_base(self, **kwargs) -> None:
        """Set the vacuum cleaner to return to the dock."""
        await self._try_command("Unable to return home: %s", self._vacuum.return_home)

    async def async_set_fan_speed(self, fan_speed: str, **kwargs) -> None:
        """Set fan speed."""
        if fan_speed in self._fan_speeds_reverse:
            speed = self._fan_speeds_reverse[fan_speed]
        else:
            try:
                speed = int(fan_speed)
            except ValueError:
                _LOGGER.error("Invalid fan speed: %s. Valid: %s", fan_speed, self._attr_fan_speed_list)
                return
        await self._try_command("Unable to set fan speed: %s", self._vacuum.set_fan_speed, speed)

    async def async_send_command(self, command: str, params: dict | None = None, **kwargs) -> None:
        """Send a command to the vacuum."""
        if command == "set_water_level":
            water_level = params.get("water_level") if params else None
            if water_level is None:
                _LOGGER.error("water_level parameter required")
                return
            if water_level in self._water_level_reverse:
                level = self._water_level_reverse[water_level]
            else:
                try:
                    level = int(water_level)
                except ValueError:
                    _LOGGER.error("Invalid water level: %s", water_level)
                    return
            await self._try_command("Unable to set water level: %s", self._vacuum.set_water_level, level)
        elif command == "remote_control_move":
            velocity = int(params.get("velocity", 0)) if params else 0
            rotation = int(params.get("rotation", 0)) if params else 0
            await self._try_command(
                "Unable to send remote control command: %s",
                self._vacuum.remote_start, velocity, rotation,
            )
        elif command == "remote_control_stop":
            await self._try_command("Unable to stop remote control: %s", self._vacuum.remote_stop)
        elif command == "remote_control_exit":
            await self._try_command("Unable to exit remote control: %s", self._vacuum.remote_exit)
        elif command == "set_dnd":
            if not params:
                _LOGGER.error("Parameters required for set_dnd")
                return
            enabled = params.get("enabled", True)
            start_time = params.get("start_time")
            stop_time = params.get("stop_time")
            await self._try_command(
                "Unable to set DND: %s",
                self._vacuum.set_dnd, enabled, start_time, stop_time,
            )
        elif command == "play_sound":
            await self._try_command("Unable to play sound: %s", self._vacuum.play_sound)
        elif command == "set_voice":
            await self._try_command("Unable to set voice: %s", self._vacuum.set_voice)
        else:
            _LOGGER.warning("Unsupported command: %s", command)

    async def async_update(self) -> None:
        """Fetch state from the device."""
        try:
            state = await self.hass.async_add_executor_job(self._vacuum.status)
        except DeviceException as exc:
            _LOGGER.warning("Error fetching vacuum state: %s", exc)
            self._attr_available = False
            return

        self._attr_available = True

        # Map state code to VacuumActivity
        state_map = {
            1: VacuumActivity.CLEANING,
            2: VacuumActivity.IDLE,
            3: VacuumActivity.PAUSED,
            4: VacuumActivity.ERROR,
            5: VacuumActivity.RETURNING,
            6: VacuumActivity.DOCKED,
        }
        self._attr_activity = state_map.get(int(state.status)) if state.status is not None else None
        self._attr_fan_speed = SPEED_CODE_TO_NAME.get(state.fan_speed, "Unknown")
        self._water_level_name = WATER_CODE_TO_NAME.get(state.water_level, "Unknown")

        # Store raw state data for sensor entities
        self.hass.data[DOMAIN].setdefault(f"{self._entry.entry_id}_state", {}).update({
            "battery": state.battery,
            "status": ERROR_CODE_TO_ERROR.get(state.error, "Unknown"),
            "main_brush_time_left": state.brush_left_time,
            "main_brush_life_level": state.brush_life_level,
            "side_brush_time_left": state.brush_left_time2,
            "side_brush_life_level": state.brush_life_level2,
            "filter_life_level": state.filter_life_level,
            "filter_left_time": state.filter_left_time,
            "cleaning_area": state.area,
            "cleaning_time": state.timer,
            "total_cleaning_area": state.total_area,
            "total_cleaning_count": state.total_clean_count,
            "water_box": state.water_box,
            "dnd_enabled": state.dnd_enabled,
            "dnd_start_time": state.dnd_start_time,
            "dnd_stop_time": state.dnd_stop_time,
        })

    async def _try_command(self, mask_error: str, func, *args, **kwargs) -> bool:
        """Call a vacuum command handling error messages."""
        try:
            await self.hass.async_add_executor_job(partial(func, *args, **kwargs))
            return True
        except DeviceException as exc:
            _LOGGER.error(mask_error, exc)
            return False
