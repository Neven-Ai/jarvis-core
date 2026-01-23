"""Lutron Device Monitor."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any

from homeassistant.components.persistent_notification import (
    async_create as async_notify_create,
)

from .leap_client import LeapClient

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant

_LOGGER = logging.getLogger(__name__)


class LutronMonitor:
    """Monitor for Lutron devices."""

    def __init__(self, hass: HomeAssistant, client: LeapClient) -> None:
        """Initialize Monitor."""
        self.hass = hass
        self.client = client
        self.devices: dict[str, dict] = {}
        self.device_status: dict[str, bool] = {}

    async def start(self) -> None:
        """Start monitoring."""
        # 1. Fetch all devices
        await self._fetch_devices()

        # 2. Subscribe to status
        # We try to subscribe to the global device status if possible
        # Or individual devices.
        # Based on LEAP, usually subscribing to /device/status works for some systems
        await self.client.subscribe("/device/status", self._handle_status_update)

    async def _fetch_devices(self) -> None:
        """Fetch all devices from the processor."""
        _LOGGER.debug("Fetching Lutron devices...")
        try:
            response = await self.client.request("ReadRequest", "/device")
            if response and "Body" in response:
                # Body usually contains "Devices" list
                dev_list = response["Body"].get("Devices", [])
                for dev in dev_list:
                    href = dev.get("Href")
                    if href:
                        self.devices[href] = dev
                        _LOGGER.debug("Found device: %s (%s)", dev.get("Name"), href)
        except Exception as err:
            _LOGGER.error("Error fetching devices: %s", err)

    def _handle_status_update(self, msg: dict) -> None:
        """Handle incoming status update."""
        # This needs to be adapted based on actual JSON structure
        # Expected: Body -> DeviceStatus -> DeviceHref, Status...
        body = msg.get("Body", {})
        status_obj = body.get("DeviceStatus")  # This might be a list or object

        if not status_obj:
            return

        # Simplified handling for single object
        # In reality, might be a list or wrapped differently.
        # But we assume the client extracts the relevant part or we handle dict here.
        if isinstance(status_obj, list):
            for s in status_obj:
                self._process_single_status(s)
        else:
            self._process_single_status(status_obj)

    def _process_single_status(self, status_obj: dict) -> None:
        """Process a single device status object."""
        href = status_obj.get("Device", {}).get("Href")
        if not href:
            return

        # Heuristic for status (will be refined after verification)
        # We look for ANY field that might indicate status.
        # Common fields: Status, LinkStatus, ConnectionStatus, Availability
        _LOGGER.info("Received status update for %s: %s", href, status_obj)

        is_online = True
        status_val = (
            status_obj.get("Status")
            or status_obj.get("LinkStatus")
            or status_obj.get("Connectivity")
            or status_obj.get("DeviceStatus")
        )

        # If we found a status field and it looks negative, mark offline
        if status_val and str(status_val).lower() in [
            "disconnected",
            "offline",
            "unreachable",
            "lost",
        ]:
            is_online = False

        self._update_status(href, is_online, status_obj)

    def _update_status(self, href: str, is_online: bool, status_data: dict) -> None:
        """Update device status."""
        prev = self.device_status.get(href)
        # Only notify on change
        if prev != is_online:
            self.device_status[href] = is_online
            self._notify_change(href, is_online, status_data)

    def _notify_change(self, href: str, is_online: bool, status_data: dict) -> None:
        """Notify change."""
        device = self.devices.get(href, {})
        name = device.get("Name", f"Device {href}")

        _LOGGER.info(
            "Lutron Device %s (%s) is now %s",
            name,
            href,
            "Online" if is_online else "Offline",
        )

        self.hass.bus.async_fire(
            "lutron_device_status_changed",
            {
                "href": href,
                "name": name,
                "online": is_online,
                "raw_status": status_data,
            },
        )

        if not is_online:
            async_notify_create(
                self.hass,
                title="Dispositivo Lutron Offline",
                message=f"Il dispositivo {name} ({href}) risulta offline.",
                notification_id=f"lutron_offline_{href.replace('/', '_')}",
            )
