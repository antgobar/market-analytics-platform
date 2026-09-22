import asyncio
import json
import logging

from market_analytics_platform.domain import Event, Store, WebsocketClient
from market_analytics_platform.integrations.base import BaseIntegration

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Coinbase(BaseIntegration):
    integration_name = "coinbase"

    def __init__(
        self, store: Store, websocket_client: WebsocketClient, instruments_url: str
    ) -> None:
        self.store = store
        self.websocket_client = websocket_client
        self.instruments_url = instruments_url
        self.lock = asyncio.Lock()

    async def subscribe(self, channel: str, instrument_ids: list[str]):
        async with self.lock:
            await self.websocket_client.send(
                json.dumps(
                    {
                        "type": "subscribe",
                        "product_ids": instrument_ids,
                        "channel": channel,
                    }
                )
            )
        logger.info(
            "Integration: %s - Subscribed to channel %s instruments: %s",
            self.integration_name,
            channel,
            instrument_ids,
        )

    async def shutdown(self) -> None:
        await self.websocket_client.close()

    async def unsubscribe(self, channel: str, instrument_ids: list[str]) -> None:
        del channel, instrument_ids
        raise NotImplementedError(
            f"Unsubscribe method is not implemented for {self.integration_name} integration"
        )

    def handle_message(self, message: str) -> Event | None:
        data = None
        try:
            data = json.loads(message)
        except json.JSONDecodeError:
            return None
        return Event(
            integration=self.integration_name,
            payload=message,
            channel=data.get("channel", ""),
            instrument_id=data.get("product_id", ""),
        )

    async def run(self) -> None:
        await self.subscribe("ticker", ["BTC-USD", "ETH-USD", "XRP-USD"])
        async for raw_message in self.websocket_client.receive():
            event = self.handle_message(raw_message)
            if event is not None:
                self.store.save(event)
