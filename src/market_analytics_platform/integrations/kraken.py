import asyncio
import json
import logging
from collections.abc import Callable
from typing import Any, Self

import httpx
from websockets.asyncio.client import ClientConnection, connect

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

_WS_URL = "wss://futures.kraken.com/ws/v1"
_SYMBOLS = [
    "PI_XBTUSD",
    "PI_ETHUSD",
    "PI_XRPUSD",
    "PF_BRETTUSD",
    "FI_ETHUSD_210625",
    "FI_XBTUSD_210625",
]

OnMessage = Callable[[str], Any]


class Kraken:
    def __init__(self: Self, on_message: OnMessage) -> None:
        self.url = _WS_URL
        self.on_message = on_message
        self.ws: ClientConnection | None = None
        self._lock = asyncio.Lock()
        self._subscriptions = {}

    async def connect(self: Self) -> None:
        self.ws = await connect(self.url)
        await self.ws.send(json.dumps({"event": "subscribe", "feed": "heartbeat"}))

    async def subscribe(self, symbols: list[str]) -> None:
        if self.ws is None:
            await self.connect()
        await self.ws.send(
            json.dumps({"event": "subscribe", "feed": "ticker", "product_ids": symbols})
        )

    def read(self: Self) -> None:
        try:
            asyncio.run(self._read(_SYMBOLS))
        except KeyboardInterrupt:
            print("interrupted")

    async def _read(self: Self, symbols: list[str]) -> None:
        await self.connect()
        await self.subscribe(symbols)
        try:
            print("starting...")
            async for raw_message in self.ws:
                logger.info(
                    "Received message, time: %s", asyncio.get_event_loop().time()
                )
                self.on_message(raw_message)

        finally:
            await self.ws.close()
            print("exiting...")


class GetKrakenInstrumentsError(Exception): ...


def _load_symbols() -> list[str]:
    _kraken_instruments_url = (
        "https://futures.kraken.com/derivatives/api/v3/instruments"
    )
    response = httpx.get(_kraken_instruments_url)
    if response.status_code != 200:
        raise GetKrakenInstrumentsError("Failed to retrieve Kraken instruments")
    data = response.json()
    if data.get("result") != "success":
        raise GetKrakenInstrumentsError("Kraken instrument retrieval failed")

    return [item["symbol"] for item in data["instruments"]]
