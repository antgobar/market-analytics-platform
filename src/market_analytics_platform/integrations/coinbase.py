import json

from market_analytics_platform.domain import Event, Store, WebsocketClient
from market_analytics_platform.integrations.base import BaseIntegration


class Coinbase(BaseIntegration):
    integration_name = "coinbase"

    def __init__(
        self, store: Store, websocket_client: WebsocketClient, instruments_url: str
    ) -> None:
        self.store = store
        self.websocket_client = websocket_client
        self.instruments_url = instruments_url

    async def subscribe(self, channel: str, instrument_ids: list[str]):
        await self.websocket_client.send(
            json.dumps(
                {
                    "type": "subscribe",
                    "product_ids": instrument_ids,
                    "channel": channel,
                }
            )
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
