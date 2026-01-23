"""KNX device presence monitor."""

from __future__ import annotations

import asyncio
import logging
from typing import TYPE_CHECKING

from xknx.management.procedures import nm_individual_address_check
from xknx.telegram.address import IndividualAddress

from homeassistant.components.persistent_notification import (
    async_create as async_notify_create,
)

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant
    from .knx_module import KNXModule

_LOGGER = logging.getLogger(__name__)

# Full scan interval in minutes
FULL_SCAN_INTERVAL = 30
# Retry interval for offline devices in minutes
RETRY_SCAN_INTERVAL = 2
# Delay between individual device checks to avoid bus saturation (seconds)
DEVICE_CHECK_DELAY = 1


class KNXDeviceMonitor:
    """Class to monitor KNX device presence."""

    def __init__(self, knx_module: KNXModule) -> None:
        """Initialize KNX device monitor."""
        self.hass: HomeAssistant = knx_module.hass
        self.knx_module = knx_module
        self._task: asyncio.Task | None = None
        self._online_status: dict[str, bool] = {}
        self._offline_addresses: set[str] = set()

    async def start(self) -> None:
        """Start the monitoring task."""
        if self._task:
            return
        self._task = self.hass.async_create_task(self._run())

    async def stop(self) -> None:
        """Stop the monitoring task."""
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
            self._task = None

    async def _run(self) -> None:
        """Loop for periodic monitoring."""
        cycle_count = 0
        full_scan_cycles = FULL_SCAN_INTERVAL // RETRY_SCAN_INTERVAL

        while True:
            try:
                if self.knx_module.connected and self.knx_module.project.loaded:
                    # Every full_scan_cycles we do a full scan, otherwise only retries
                    is_full_scan = cycle_count % full_scan_cycles == 0
                    await self._scan_devices(full=is_full_scan)
                    cycle_count += 1
            except Exception as err:
                _LOGGER.error("Unexpected error in KNX device monitor: %s", err)

            # Wait for the retry interval
            await asyncio.sleep(RETRY_SCAN_INTERVAL * 60)

    async def _scan_devices(self, full: bool = True) -> None:
        """Scan devices in the project."""
        all_devices = self.knx_module.project.devices
        if not all_devices:
            _LOGGER.debug("No devices found in project to monitor")
            return

        if full:
            addresses_to_check = list(all_devices.keys())
            _LOGGER.debug(
                "Starting FULL KNX device presence scan for %s devices",
                len(addresses_to_check),
            )
        else:
            # Filter to ensure we don't check devices removed from project
            addresses_to_check = [
                addr for addr in self._offline_addresses if addr in all_devices
            ]
            if not addresses_to_check:
                return
            _LOGGER.debug(
                "Starting RETRY KNX device presence scan for %s offline devices",
                len(addresses_to_check),
            )

        for address_str in addresses_to_check:
            if not self.knx_module.connected:
                _LOGGER.debug("KNX disconnected, aborting scan")
                break

            # Re-verify device still exists (it might have been removed during long scans)
            if address_str not in all_devices:
                self._offline_addresses.discard(address_str)
                continue

            device_info = all_devices[address_str]
            try:
                address = IndividualAddress(address_str)
                is_online = await nm_individual_address_check(
                    self.knx_module.xknx, address
                )
                self._update_status(address_str, is_online, device_info)
            except Exception as err:
                _LOGGER.error("Error checking KNX device %s: %s", address_str, err)

            # Delay between devices to avoid saturating the bus
            await asyncio.sleep(DEVICE_CHECK_DELAY)

        _LOGGER.debug(
            "Finished KNX device presence scan (%s)", "Full" if full else "Retry"
        )

    def _update_status(self, address: str, is_online: bool, device_info: dict) -> None:
        """Update device status and notify if changed."""
        prev_status = self._online_status.get(address)

        # Initial status recording
        if prev_status is None:
            self._online_status[address] = is_online
            if not is_online:
                self._offline_addresses.add(address)
                _LOGGER.warning(
                    "KNX Device %s (%s) is OFFLINE on initial scan",
                    device_info.get("name", "Device"),
                    address,
                )
            return

        # Handle status transition
        if prev_status != is_online:
            self._online_status[address] = is_online
            if is_online:
                self._offline_addresses.discard(address)
            else:
                self._offline_addresses.add(address)

            self._notify_change(address, is_online, device_info)

    def _notify_change(self, address: str, is_online: bool, device_info: dict) -> None:
        """Notify user about status change."""
        device_name = f"{device_info.get('manufacturer_name', 'Unknown')} {device_info.get('name', 'Device')}"
        status_text = "online" if is_online else "non raggiungibile"

        _LOGGER.info("KNX Device %s (%s) is now %s", device_name, address, status_text)

        # Fire HA event for automations
        self.hass.bus.async_fire(
            "knx_device_status_changed",
            {"address": address, "name": device_name, "online": is_online},
        )

        # Send persistent notification if unreachable
        if not is_online:
            async_notify_create(
                self.hass,
                title="Dispositivo KNX non raggiungibile",
                message=f"Il dispositivo {device_name} ({address}) non è più raggiungibile sul bus KNX.",
                notification_id=f"knx_device_unreachable_{address.replace('.', '_')}",
            )
