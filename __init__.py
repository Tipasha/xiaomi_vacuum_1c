"""Xiaomi Mi Robot Vacuum-Mop 1C integration."""
from __future__ import annotations

import logging

import voluptuous as vol

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.helpers import config_validation as cv

from .const import CONF_HOST, CONF_TOKEN, DOMAIN
from .miio import DreameVacuum

_LOGGER = logging.getLogger(__name__)

PLATFORMS = ["vacuum", "sensor"]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Xiaomi Mi Robot Vacuum-Mop 1C from a config entry."""
    host = entry.data[CONF_HOST]
    token = entry.data[CONF_TOKEN]

    vacuum = DreameVacuum(host, token)

    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = vacuum

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    # Register remote control services (once per domain)
    if not hass.services.has_service(DOMAIN, "remote_control_move"):

        async def _get_vacuum(call: ServiceCall) -> DreameVacuum:
            """Resolve vacuum device from the first config entry."""
            for eid, vac in hass.data[DOMAIN].items():
                if isinstance(vac, DreameVacuum):
                    return vac
            raise ValueError("No vacuum device found")

        async def handle_remote_control_move(call: ServiceCall) -> None:
            """Handle remote_control_move service."""
            vacuum = await _get_vacuum(call)
            velocity = call.data.get("velocity", 0)
            rotation = call.data.get("rotation", 0)
            await hass.async_add_executor_job(vacuum.remote_start, velocity, rotation)

        async def handle_remote_control_stop(call: ServiceCall) -> None:
            """Handle remote_control_stop service."""
            vacuum = await _get_vacuum(call)
            await hass.async_add_executor_job(vacuum.remote_stop)

        async def handle_remote_control_exit(call: ServiceCall) -> None:
            """Handle remote_control_exit service."""
            vacuum = await _get_vacuum(call)
            await hass.async_add_executor_job(vacuum.remote_exit)

        hass.services.async_register(
            DOMAIN,
            "remote_control_move",
            handle_remote_control_move,
            schema=vol.Schema({
                vol.Required("velocity"): vol.All(int, vol.Range(min=-300, max=300)),
                vol.Required("rotation"): vol.All(int, vol.Range(min=-120, max=120)),
            }),
        )
        hass.services.async_register(
            DOMAIN,
            "remote_control_stop",
            handle_remote_control_stop,
            schema=vol.Schema({}),
        )
        hass.services.async_register(
            DOMAIN,
            "remote_control_exit",
            handle_remote_control_exit,
            schema=vol.Schema({}),
        )

        async def handle_set_dnd(call: ServiceCall) -> None:
            """Handle set_dnd service."""
            vacuum = await _get_vacuum(call)
            enabled = call.data.get("enabled", True)
            start_time = call.data.get("start_time")
            stop_time = call.data.get("stop_time")
            await hass.async_add_executor_job(
                vacuum.set_dnd, enabled, start_time, stop_time,
            )

        async def handle_play_sound(call: ServiceCall) -> None:
            """Handle play_sound service."""
            vacuum = await _get_vacuum(call)
            await hass.async_add_executor_job(vacuum.play_sound)

        async def handle_set_voice(call: ServiceCall) -> None:
            """Handle set_voice service."""
            vacuum = await _get_vacuum(call)
            await hass.async_add_executor_job(vacuum.set_voice)

        hass.services.async_register(
            DOMAIN,
            "set_dnd",
            handle_set_dnd,
            schema=vol.Schema({
                vol.Required("enabled"): cv.boolean,
                vol.Optional("start_time"): cv.string,
                vol.Optional("stop_time"): cv.string,
            }),
        )
        hass.services.async_register(
            DOMAIN,
            "play_sound",
            handle_play_sound,
            schema=vol.Schema({}),
        )
        hass.services.async_register(
            DOMAIN,
            "set_voice",
            handle_set_voice,
            schema=vol.Schema({}),
        )

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)
    return unload_ok
