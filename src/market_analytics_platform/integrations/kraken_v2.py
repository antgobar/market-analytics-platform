import asyncio
import json
import logging
from typing import Self

import httpx
from websockets.asyncio.client import ClientConnection

from market_analytics_platform.models import Event
from market_analytics_platform.store import Store
from market_analytics_platform.websocket import WebsocketClient

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

_WS_URL = "wss://ws.kraken.com/v2"
_INSTRUMENTS_URL = "https://api.kraken.com/0/public/AssetPairs"
_SYMBOLS = [
    "BTC/USD",
    # "ETH/USD",
    # "XRP/USD",
]


class KrakenV2:
    def __init__(self: Self, store: Store) -> None:
        self.url = _WS_URL
        self.instruments_url = _INSTRUMENTS_URL
        self.store = store
        self.ws: ClientConnection | None = None
        self.client = WebsocketClient(self.url)

    async def subscribe(self, symbols: list[str]) -> None:
        await self.client.send(
            {
                "method": "subscribe",
                "params": {"channel": "ticker", "symbol": symbols},
            }
        )

    def handle_message(self: Self, message: str) -> Event | None:
        data = None
        try:
            data = json.loads(message)
        except json.JSONDecodeError:
            logger.error("Failed to decode message: %s", message)
        if data is None:
            return None

        return Event(
            integration="kraken_v2",
            payload=message,
            channel="ticker",
            instrument_id=data["params"]["symbol"],
        )

    async def read(self: Self) -> None:
        await self.subscribe(_SYMBOLS)
        logger.info("Subscribed to Kraken V2 instruments: %s", _SYMBOLS)
        async for raw_message in self.client.receive():
            logger.info("Received message, time: %s", asyncio.get_event_loop().time())
            print(raw_message)
            # event = self.handle_message(raw_message)
            # if event is not None:
            #     self.store.save(event)

    def _load_symbols(self: Self) -> list[str]:
        response = httpx.get(self.instruments_url)
        if response.status_code != 200:
            raise GetKrakenV2InstrumentsError("Failed to retrieve Kraken instruments")
        data = response.json()
        if data.get("error"):
            raise GetKrakenV2InstrumentsError("Kraken instrument retrieval failed")

        return [item["wsname"] for item in data["result"].values() if "wsname" in item]


class GetKrakenV2InstrumentsError(Exception): ...
