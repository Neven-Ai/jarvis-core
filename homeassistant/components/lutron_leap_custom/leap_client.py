"""LEAP Protocol Client for Lutron Integration."""

from __future__ import annotations

import asyncio
import json
import logging
import ssl
from collections.abc import Callable
from typing import Any

_LOGGER = logging.getLogger(__name__)


class LeapClient:
    """Client for Lutron LEAP Protocol."""

    def __init__(
        self,
        host: str,
        port: int,
        cert_file: str,
        key_file: str,
        ca_file: str,
    ) -> None:
        """Initialize LEAP Client."""
        self.host = host
        self.port = port
        self.cert_file = cert_file
        self.key_file = key_file
        self.ca_file = ca_file

        self._reader: asyncio.StreamReader | None = None
        self._writer: asyncio.StreamWriter | None = None
        self._connected = False
        self._subscribers: dict[str, list[Callable[[dict], None]]] = {}
        self._pending_requests: dict[str, asyncio.Future] = {}
        self._task: asyncio.Task | None = None

    async def connect(self) -> None:
        """Connect to the Lutron processor."""
        _LOGGER.debug("Connecting to Lutron Processor at %s:%s", self.host, self.port)

        context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
        context.verify_mode = ssl.CERT_REQUIRED
        context.load_verify_locations(cafile=self.ca_file)
        context.load_cert_chain(certfile=self.cert_file, keyfile=self.key_file)

        # We might need to handle hostname check disabling if cert CN doesn't match IP
        context.check_hostname = False

        try:
            self._reader, self._writer = await asyncio.open_connection(
                self.host, self.port, ssl=context
            )
            self._connected = True
            _LOGGER.info("Connected to Lutron Processor")

            # Start the reader loop
            self._task = asyncio.create_task(self._read_loop())

        except Exception as err:
            _LOGGER.error("Failed to connect to Lutron Processor: %s", err)
            raise

    async def disconnect(self) -> None:
        """Disconnect from the processor."""
        self._connected = False
        if self._task:
            self._task.cancel()

        if self._writer:
            self._writer.close()
            try:
                await self._writer.wait_closed()
            except Exception:
                pass

        self._reader = None
        self._writer = None

    async def request(
        self, communique_type: str, url: str, body: dict | None = None
    ) -> dict:
        """Send a request and wait for a response."""
        if not self._connected or not self._writer:
            raise ConnectionError("Not connected to processor")

        # Create a simple tag/ID mechanism if needed, but for now we rely on the order or assume sync
        # Note: LEAP is async. Responses usually contain a ClientTag if we send one.
        # Let's generate a tag.
        client_tag = f"req_{asyncio.get_running_loop().time()}"

        message = {
            "CommuniqueType": communique_type,
            "Header": {"Url": url, "ClientTag": client_tag},
        }
        if body:
            message["Body"] = body

        # Create a future to wait for the response
        future = asyncio.get_running_loop().create_future()
        self._pending_requests[client_tag] = future

        try:
            data = json.dumps(message).encode("utf-8") + b"\r\n"
            self._writer.write(data)
            await self._writer.drain()

            # Wait for response with timeout
            response = await asyncio.wait_for(future, timeout=10.0)
            return response

        except asyncio.TimeoutError:
            del self._pending_requests[client_tag]
            raise TimeoutError(f"Request to {url} timed out")
        except Exception as err:
            if client_tag in self._pending_requests:
                del self._pending_requests[client_tag]
            raise err

    async def subscribe(self, url: str, callback: Callable[[dict], None]) -> None:
        """Subscribe to an event URL."""
        if url not in self._subscribers:
            self._subscribers[url] = []
        self._subscribers[url].append(callback)

        # Send SubscribeRequest
        # Note: LEAP subscription usually works by sending a SubscribeRequest once
        # and then receiving 'ReadResponse' or similar notifications?
        # Typically CommuneType is "SubscribeRequest"
        try:
            await self.request("SubscribeRequest", url)
            _LOGGER.debug("Subscribed to %s", url)
        except Exception as err:
            _LOGGER.error("Failed to subscribe to %s: %s", url, err)

    async def _read_loop(self) -> None:
        """Read incoming messages."""
        buffer = b""
        while self._connected and self._reader:
            try:
                chunk = await self._reader.read(4096)
                if not chunk:
                    _LOGGER.warning("Connection closed by server")
                    break

                buffer += chunk

                # Split by newline (LEAP messages are newline delimited)
                while b"\n" in buffer:
                    line, buffer = buffer.split(b"\n", 1)
                    if not line.strip():
                        continue

                    await self._handle_message(line)

            except asyncio.CancelledError:
                break
            except Exception as err:
                _LOGGER.error("Error in read loop: %s", err)
                await asyncio.sleep(1)

        self._connected = False
        _LOGGER.info("Read loop terminated")

    async def _handle_message(self, data: bytes) -> None:
        """Process a single JSON message."""
        try:
            msg = json.loads(data)
            header = msg.get("Header", {})
            client_tag = header.get("ClientTag")

            # 1. Check if it's a response to a pending request
            if client_tag and client_tag in self._pending_requests:
                self._pending_requests[client_tag].set_result(msg)
                del self._pending_requests[client_tag]
                return

            # 2. Check if it's a notification/event (usually contained in body or status)
            # Notifications typically look like ReadResponse/ExceptionResponse but unsolicited?
            # Or they match a subscribed URL.
            # We look at the body or the URL in header if present
            # Note: LEAP notifications often don't have a ClientTag but have a specific Url
            # or the body relates to a subscribed resource.

            # Simplistic routing: if we have subscribers and msg has a Body, notify all?
            # Better: Filter by URL logic if possible.
            # LEAP notification header often has "Url"
            msg_url = header.get("Url")
            if msg_url:
                # Direct match
                if msg_url in self._subscribers:
                    for cb in self._subscribers[msg_url]:
                        cb(msg)

                # Partial match logic could go here (e.g. /device/1 vs /device)

        except json.JSONDecodeError:
            _LOGGER.warning("Received invalid JSON: %s", data)
        except Exception as err:
            _LOGGER.error("Error handling message: %s", err)
