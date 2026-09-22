import json

import websockets

from market_analytics_platform.domain import Store, WebsocketClient
from market_analytics_platform.integrations.base import BaseIntegration


class Coinbase(BaseIntegration):
    integration_name = "coinbase"

    def __init__(
        self, store: Store, websocket_client: WebsocketClient, instruments_url: str
    ) -> None:
        self.store = store
        self.websocket_client = websocket_client
        self.instruments_url = instruments_url

    async def main(url: str):
        async with websockets.connect(url) as ws:
            subscribe = {
                "type": "subscribe",
                "product_ids": ["BTC-USD"],
                "channel": "ticker",
            }

            await ws.send(json.dumps(subscribe))

            async for message in ws:
                data = json.loads(message)
                print()
                print(data)
