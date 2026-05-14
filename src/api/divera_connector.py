import asyncio
import logging
import ssl
import certifi
import os
from datetime import timedelta

import aiohttp

from api.alarm_data import AlarmData

from .const import (
    BASE_URL,
    BASE_PULL_URL,
    BASE_VEHICLE_URL,
    CONF_ACCESS_KEY,
    CONF_UCR_ID,
    DOMAIN,
    FALLBACK_POLL_INTERVAL,
    JWT_URL,
    WS_MAX_RECONNECT_DELAY,
    WS_RECONNECT_DELAY,
    WS_URL,
)
_LOGGER = logging.getLogger(__name__)

class DiveraConnector():
    def __init__(self) -> None:
        self.access_key: str = os.getenv(CONF_ACCESS_KEY)
        self.ucr_id: str | None = None
        self._jwt: str | None = None
        self._poll_task: asyncio.Task | None = None
        self._ws_task: asyncio.Task | None = None
        self._ws_connected: bool = False
        self.update_interval: timedelta | None = timedelta(seconds=FALLBACK_POLL_INTERVAL)
        self._sslContext = ssl.create_default_context(cafile=certifi.where())

    # ------------------------------------------------------------------
    # Polling
    # ------------------------------------------------------------------

    async def start_polling(self) -> None:
        """Starts the polling loop."""
        if self._poll_task and not self._poll_task.done():
            return  # läuft bereits
        self._poll_task = asyncio.create_task(self._poll_loop())

    async def stop_polling(self) -> None:
        """Stops the polling loop if it's running."""
        if self._poll_task and not self._poll_task.done():
            self._poll_task.cancel()
            try:
                await self._poll_task
            except asyncio.CancelledError:
                pass  # erwartet
        self._poll_task = None

    async def _poll_loop(self) -> None:
        while True:
            try:
                if self._ws_connected:
                    _LOGGER.debug("DIVERA: WebSocket is connected – skipping polling")
                else:
                    # Poll only if WebSocket is not connected
                    _LOGGER.debug("DIVERA: Polling loop tick – fetching alarm data via REST")
                    alarmData = await self._async_update_alarm_data()                 
                    print("Aktueller Alarm:", alarmData)
                    _LOGGER.debug("DIVERA: Polling loop successfully fetched alarm data - trying to switch to WebSocket if not connected")
                    await self._async_start_websocket()
            except ConfigEntryAuthFailed as auth_err:
                _LOGGER.error("DIVERA: Authentication failed during polling: %s", auth_err)
                await self.stop_polling()
                return
            except Exception as err:
                _LOGGER.warning("Polling error: %s", err)
            _LOGGER.debug("DIVERA: Polling loop sleeping for %d seconds", self.update_interval.total_seconds())
            await asyncio.sleep(self.update_interval.total_seconds())

    # ------------------------------------------------------------------
    # Fallback-Polling Control
    # ------------------------------------------------------------------

    def _set_ws_connected(self, connected: bool) -> None:
        """Set the WebSocket connection status and adjust fallback polling accordingly"""
        if connected == self._ws_connected:
            return
        self._ws_connected = connected
        if connected:
            _LOGGER.info("DIVERA: WebSocket connected – polling ignored in future ticks")
        else:
            _LOGGER.warning(
                "DIVERA: WebSocket not available – switching to fallback polling (%ds interval)",
                FALLBACK_POLL_INTERVAL,
            )
            self.stop_websocket()

    # ------------------------------------------------------------------
    # JWT
    # ------------------------------------------------------------------

    async def async_fetch_jwt(self) -> str:
        """Get a new JWT from the API using the access key"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    JWT_URL,
                    params={"accesskey": self.access_key},
                    timeout=aiohttp.ClientTimeout(total=10),
                    ssl=self._sslContext,
                ) as resp:
                    if resp.status == 401:
                        raise ConfigEntryAuthFailed("Invalid Access Key")
                    if resp.status != 200:
                        raise UpdateFailed(f"JWT fetch failed: HTTP {resp.status}")
                    payload = await resp.json()
        except aiohttp.ClientError as err:
            raise UpdateFailed(f"Connection error during JWT fetch: {err}") from err

        data = payload.get("data", {})
        jwt = data.get("jwt_ws") or data.get("jwt")
        if not jwt:
            raise UpdateFailed("No JWT found in server response")
        self._jwt = jwt
        return jwt

    # ------------------------------------------------------------------
    # WebSocket-Handling (Loop)
    # ------------------------------------------------------------------

    async def _async_start_websocket(self) -> None:
        """WebSocket-Loop as async task."""
        if self._ws_task and not self._ws_task.done():
            return  # läuft bereits
        _LOGGER.debug("DIVERA WebSocket: Starting WebSocket loop task")
        self._ws_task = asyncio.create_task(self._ws_loop())

    def stop_websocket(self) -> None:
        """Stop the WebSocket loop task if it's running."""
        if self._ws_task and not self._ws_task.done():
            self._ws_task.cancel()
            self._ws_task = None

    async def _ws_loop(self) -> None:
        """Main loop to maintain WebSocket connection with automatic reconnection and fallback handling."""
        _LOGGER.debug("DIVERA WebSocket loop started")
        delay = WS_RECONNECT_DELAY
        while True:
            try:
                await self._ws_run_once()
                # Saubere Trennung: in Fallback wechseln und Delay zurücksetzen
                self._set_ws_connected(False)
                delay = WS_RECONNECT_DELAY
            except asyncio.CancelledError:
                _LOGGER.debug("DIVERA stopping WebSocket loop task")
                self._set_ws_connected(False)
                return
            except ConfigEntryAuthFailed:
                _LOGGER.error("DIVERA: Invalid Access Key – WebSocket will not reconnect until the issue is resolved")
                self._set_ws_connected(False)
                return
            except Exception as err:  # noqa: BLE001
                self._set_ws_connected(False)
                _LOGGER.warning(
                    "DIVERA: WebSocket connection error: %s (%s). "
                    "New attempt in %s seconds.",
                    err,
                    type(err).__name__,
                    delay,
                )
                await asyncio.sleep(delay)
                delay = min(delay * 2, WS_MAX_RECONNECT_DELAY)
                continue
            await asyncio.sleep(WS_RECONNECT_DELAY)

    async def _ws_run_once(self) -> None:
        """Run the WebSocket connection once (connect, authenticate, handle messages)."""
        jwt = await self.async_fetch_jwt()
        _LOGGER.debug("DIVERA: Successfully fetched JWT, connecting WebSocket …")

        async with aiohttp.ClientSession() as session:
            async with session.ws_connect(
                WS_URL,
                heartbeat=25,  # Ping alle 25s gegen den 30s-Timeout
                timeout=aiohttp.ClientTimeout(total=None, connect=15),
                ssl=self._sslContext,
            ) as ws:
                # Send authentication message immediately after connecting
                auth_payload: dict = {"jwt": jwt}
                if self.ucr_id:
                    auth_payload["ucr"] = int(self.ucr_id)

                await ws.send_json({"type": "authenticate", "payload": auth_payload})
                _LOGGER.debug("DIVERA: sent authentication message to WebSocket")

                async for msg in ws:
                    if msg.type == aiohttp.WSMsgType.TEXT:
                        await self._handle_ws_message(msg.data, ws)
                    elif msg.type == aiohttp.WSMsgType.ERROR:
                        raise UpdateFailed(f"WebSocket error: {ws.exception()}")
                    elif msg.type in (
                        aiohttp.WSMsgType.CLOSE,
                        aiohttp.WSMsgType.CLOSING,
                        aiohttp.WSMsgType.CLOSED,
                    ):
                        close_code = msg.data
                        close_reason = msg.extra or "no reason provided"
                        _LOGGER.warning(
                            "DIVERA: WebSocket connection closed – Code: %s, Reason: %s",
                            close_code,
                            close_reason,
                        )
                        return

    async def _handle_ws_message(self, raw: str, ws: aiohttp.ClientWebSocketResponse) -> None:
        """Handle incoming WebSocket messages."""
        try:
            data = __import__("json").loads(raw)
        except ValueError:
            _LOGGER.debug("DIVERA: Non-JSON message received: %s", raw)
            return

        msg_type = data.get("type", "")

        if msg_type == "init":
            _LOGGER.info("DIVERA: WebSocket successfully authenticated (init received)")
            self._set_ws_connected(True)

        elif msg_type == "jwtExpired":
            _LOGGER.info("DIVERA: JWT expired – fetching new JWT and re-authenticating")
            try:
                new_jwt = await self.async_fetch_jwt()
                auth_payload: dict = {"jwt": new_jwt}
                if self.ucr_id:
                    auth_payload["ucr"] = int(self.ucr_id)
                await ws.send_json({"type": "authenticate", "payload": auth_payload})
            except Exception as err:  # noqa: BLE001
                _LOGGER.error("DIVERA: JWT renewal failed: %s", err)
                raise

        elif msg_type == "cluster-pull":
            _LOGGER.debug("DIVERA: cluster-pull received – loading new alarm data")
            await self._async_update_alarm_data()

        elif msg_type == "cluster-vehicle":
            _LOGGER.debug("DIVERA: Vehicle status update received: %s", data.get("payload"))

        elif msg_type == "user-status":
            _LOGGER.debug("DIVERA: User status update received: %s", data.get("payload"))

        else:
            _LOGGER.debug("DIVERA: Unknown WS event '%s': %s", msg_type, data)

    # ------------------------------------------------------------------
    # REST Client
    # ------------------------------------------------------------------
    async def _async_rest_client(self, url: str, params: dict = {}) -> dict:
        """Generic async REST client for the Divera API."""
        params["accesskey"] = self.access_key
        if self.ucr_id:
            params["ucr"] = self.ucr_id

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    BASE_URL + url,
                    params=params,
                    timeout=aiohttp.ClientTimeout(total=10),
                    ssl=self._sslContext,
                ) as resp:
                    if resp.status == 401 or resp.status == 403:
                        raise ConfigEntryAuthFailed("Invalid Access Key")
                    if resp.status != 200:
                        raise UpdateFailed(f"API error: HTTP {resp.status}")
                    return await resp.json()
        except aiohttp.ClientError as err:
            raise UpdateFailed(f"Connection error: {err}") from err


    # ------------------------------------------------------------------
    # REST Data Fetching (also used as fallback when WebSocket is not available)
    # ------------------------------------------------------------------
    async def _async_update_alarm_data(self):
        """Fetch current alarm data via REST."""
        payload = await self._async_rest_client(BASE_PULL_URL)
        return self._extract_alarm(payload)

    def _extract_alarm(self, payload: dict):
        """Fetch the most recent active alarm from the API response."""
        items = payload.get("data", {}).get("alarm", {}).get("items", [])

        # items [] (no alarms) or {id: alarm_obj} (Dict)
        if not items or not isinstance(items, dict):
            return None

        alarms = list(items.values())
        _LOGGER.debug("DIVERA: found %d alarm(s)", len(alarms))

        if len(alarms) > 0:
            print("AlarmData:", alarms[0])

        return max(alarms, key=lambda a: a.get("id", 0))

    async def _async_update_vehicle_data(self):
        """Fetch current vehicle status data via REST."""
        payload = await self._async_rest_client(BASE_VEHICLE_URL)
        return payload.get("data", {})
    
    # ------------------------------------------------------------------
    # REST Data Fetching for alarm data
    # ------------------------------------------------------------------
    async def async_fill_alarm_data(self, alarm_data: AlarmData):
        """Fill the AlarmData object with data from the API."""
        vehicle_data = await self._async_update_vehicle_data()
        alarm_data.add_api_data(vehicle_data)
        
        


class UpdateFailed(Exception):
    """Exception raised when an update fails."""
    pass

class ConfigEntryAuthFailed(Exception):
    """Exception raised when configuration entry authentication fails."""
    pass