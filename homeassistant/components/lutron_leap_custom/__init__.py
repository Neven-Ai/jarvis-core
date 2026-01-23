"""Lutron LEAP Custom Component."""

from __future__ import annotations

import logging
import os

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST, CONF_PORT, Platform
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady

from .leap_client import LeapClient
from .monitor import LutronMonitor

_LOGGER = logging.getLogger(__name__)

DOMAIN = "lutron_leap_custom"
PLATFORMS: list[Platform] = [
    Platform.SENSOR
]  # We can expose connectivity as a sensor later

CONF_CERT_FILE = "cert_file"
CONF_KEY_FILE = "key_file"
CONF_CA_FILE = "ca_file"


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up from a config entry."""
    hass.data.setdefault(DOMAIN, {})

    host = entry.data[CONF_HOST]
    port = entry.data[CONF_PORT]
    cert_file = entry.data[CONF_CERT_FILE]
    key_file = entry.data[CONF_KEY_FILE]
    ca_file = entry.data[CONF_CA_FILE]

    # Check if files exist
    for f in [cert_file, key_file, ca_file]:
        if not os.path.exists(f):
            _LOGGER.error("Certificate file not found: %s", f)
            return False

    client = LeapClient(host, port, cert_file, key_file, ca_file)
    monitor = LutronMonitor(hass, client)

    try:
        await client.connect()
    except Exception as err:
        raise ConfigEntryNotReady(f"Failed to connect: {err}") from err

    # Start monitoring
    await monitor.start()

    hass.data[DOMAIN][entry.entry_id] = {"client": client, "monitor": monitor}

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    data = hass.data[DOMAIN].get(entry.entry_id)
    if data:
        client = data["client"]
        await client.disconnect()

    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok
