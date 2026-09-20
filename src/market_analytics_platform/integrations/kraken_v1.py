import asyncio
import logging
from collections.abc import Callable
from typing import Any, Self

import httpx

from market_analytics_platform.websocket import WebsocketClient

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

_WS_URL = "wss://futures.kraken.com/ws/v1"
_SYMBOLS = [
    "PI_XBTUSD",
    # "PI_ETHUSD",
    # "PI_XRPUSD",
    # "PF_BRETTUSD",
    # "FI_ETHUSD_210625",
    # "FI_XBTUSD_210625",
]

OnMessage = Callable[[str], Any]


class KrakenV1:
    def __init__(self: Self, on_message: OnMessage) -> None:
        self.url = _WS_URL
        self.on_message = on_message
        self.client = WebsocketClient(self.url)

    async def subscribe(self, symbols: list[str]) -> None:
        await self.client.send(
            {"event": "subscribe", "feed": "ticker", "product_ids": symbols}
        )

    async def read(self: Self) -> None:
        await self.subscribe(_SYMBOLS)
        print("starting...")
        async for raw_message in self.client.receive():
            logger.info("Received message, time: %s", asyncio.get_event_loop().time())
            self.on_message(raw_message)


class GetKrakenV1InstrumentsError(Exception): ...


def _load_symbols() -> list[str]:
    _kraken_instruments_url = (
        "https://futures.kraken.com/derivatives/api/v3/instruments"
    )
    response = httpx.get(_kraken_instruments_url)
    if response.status_code != 200:
        raise GetKrakenV1InstrumentsError("Failed to retrieve Kraken instruments")
    data = response.json()
    if data.get("result") != "success":
        raise GetKrakenV1InstrumentsError("Kraken instrument retrieval failed")

    return [item["symbol"] for item in data["instruments"]]
