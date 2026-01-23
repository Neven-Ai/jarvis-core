"""Config flow for Lutron LEAP Custom integration."""

from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.const import CONF_HOST, CONF_PORT
from homeassistant.data_entry_flow import FlowResult

_LOGGER = logging.getLogger(__name__)

DOMAIN = "lutron_leap_custom"
CONF_CERT_FILE = "cert_file"
CONF_KEY_FILE = "key_file"
CONF_CA_FILE = "ca_file"

DEFAULT_PORT = 8081


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Lutron LEAP Custom."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}
        if user_input is not None:
            # Here we could validate the connection
            # For now, just create the entry
            return self.async_create_entry(title=user_input[CONF_HOST], data=user_input)

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_HOST): str,
                    vol.Required(CONF_PORT, default=DEFAULT_PORT): int,
                    vol.Required(CONF_CERT_FILE): str,
                    vol.Required(CONF_KEY_FILE): str,
                    vol.Required(CONF_CA_FILE): str,
                }
            ),
            errors=errors,
        )
