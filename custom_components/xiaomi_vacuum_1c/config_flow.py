"""Config flow for Xiaomi Mi Robot Vacuum-Mop 1C."""
from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol

from homeassistant.config_entries import ConfigFlow, ConfigFlowResult

from .const import CONF_HOST, CONF_TOKEN, DOMAIN
from .miio import DreameVacuum, DeviceException

_LOGGER = logging.getLogger(__name__)

DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_HOST): str,
        vol.Required(CONF_TOKEN): vol.All(str, vol.Length(min=32, max=32)),
    }
)


class XiaomiVacuum1CConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Xiaomi Mi Robot Vacuum-Mop 1C."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}

        if user_input is not None:
            host = user_input[CONF_HOST]
            token = user_input[CONF_TOKEN]

            # Prevent duplicate entries for the same host
            await self.async_set_unique_id(host)
            self._abort_if_unique_id_configured()

            # Test the connection
            try:
                vacuum = DreameVacuum(host, token)
                await self.hass.async_add_executor_job(vacuum.status)
            except DeviceException:
                errors["base"] = "cannot_connect"
            except Exception:
                _LOGGER.exception("Unexpected error during setup")
                errors["base"] = "unknown"
            else:
                return self.async_create_entry(
                    title="Xiaomi Mi Robot Vacuum-Mop 1C",
                    data=user_input,
                )

        return self.async_show_form(
            step_id="user",
            data_schema=DATA_SCHEMA,
            errors=errors,
        )
