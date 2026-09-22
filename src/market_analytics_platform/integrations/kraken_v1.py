import asyncio
import json
import logging
from typing import Self

import httpx

from market_analytics_platform.domain import Event, Store, WebsocketClient

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

_INSTRUMENT_IDS = [
    "PI_XBTUSD",
    "PI_ETHUSD",
    "PI_XRPUSD",
    "PF_BRETTUSD",
    "FI_ETHUSD_210625",
    "FI_XBTUSD_210625",
]


class KrakenV1:
    integration_name = "kraken_v1"

    def __init__(
        self: Self,
        store: Store,
        websocket_client: WebsocketClient,
        instruments_url: str,
    ) -> None:
        self.instruments_url = instruments_url
        self.store = store
        self.client = websocket_client

    async def subscribe(self, channel: str, instrument_ids: list[str]) -> None:
        await self.client.send(
            {"event": "subscribe", "feed": channel, "product_ids": instrument_ids}
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
            integration=self.integration_name,
            payload=message,
            channel=data["feed"],
            instrument_id=data["product_id"],
        )

    async def read(self: Self) -> None:
        await self.subscribe("ticker", _INSTRUMENT_IDS)
        logger.info("Subscribed to Kraken V1 instruments: %s", _INSTRUMENT_IDS)
        async for raw_message in self.client.receive():
            logger.info("Received message, time: %s", asyncio.get_event_loop().time())
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
