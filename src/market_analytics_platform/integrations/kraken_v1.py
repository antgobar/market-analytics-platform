import asyncio
import json
import logging
from typing import Any, Protocol, Self

import httpx

from market_analytics_platform.models import Event
from market_analytics_platform.websocket import WebsocketClient

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

_WS_URL = "wss://futures.kraken.com/ws/v1"
_INSTRUMENTS_URL = "https://futures.kraken.com/derivatives/api/v3/instruments"
_SYMBOLS = [
    "PI_XBTUSD",
    "PI_ETHUSD",
    "PI_XRPUSD",
    "PF_BRETTUSD",
    "FI_ETHUSD_210625",
    "FI_XBTUSD_210625",
]


class Store(Protocol):
    def save(self, event: Event) -> None: ...


class KrakenV1:
    def __init__(self: Self, store: Any) -> None:
        self.url = _WS_URL
        self.instruments_url = _INSTRUMENTS_URL
        self.store = store
        self.client = WebsocketClient(self.url)

    async def subscribe(self, symbols: list[str]) -> None:
        await self.client.send(
            {"event": "subscribe", "feed": "ticker", "product_ids": symbols}
        )

    def handle_message(self: Self, message: str) -> Event | None:
        data = None
        try:
            data = json.loads(message)
        except json.JSONDecodeError:
            logger.error("Failed to decode message: %s", message)
        if data is None:
            return None

        if data.get("event") == "info":
            logger.info("Received info message: %s", message)
            return None
        if data.get("event") == "subscribed":
            logger.info("Received subscribed message: %s", message)
            return None
        if data.get("event") == "alert":
            logger.info("Received alert message: %s", message)
            return None

        return Event(
            integration="kraken_v1",
            payload=message,
            channel=data["feed"],
            instrument_id=data["product_id"],
        )

    async def read(self: Self) -> None:
        await self.subscribe(_SYMBOLS)
        logger.info("Subscribed to Kraken V1 instruments: %s", _SYMBOLS)
        async for raw_message in self.client.receive():
            logger.info("Received message, time: %s", asyncio.get_event_loop().time())
            # print(raw_message)
            event = self.handle_message(raw_message)
            if event is not None:
                self.store.save(event)

    def valid_instrument_ids(self: Self) -> list[str]:
        response = httpx.get(self.instruments_url)
        if response.status_code != 200:
            raise GetKrakenV1InstrumentsError("Failed to retrieve Kraken instruments")
        data = response.json()
        if data.get("result") != "success" or "instruments" not in data:
            raise GetKrakenV1InstrumentsError("Kraken instrument retrieval failed")

        symbols = [item.get("symbol") for item in data["instruments"]]
        return [s for s in symbols if s is not None]


class GetKrakenV1InstrumentsError(Exception): ...
