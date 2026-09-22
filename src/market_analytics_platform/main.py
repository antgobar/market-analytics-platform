import asyncio
import logging

from market_analytics_platform.config import load_config
from market_analytics_platform.integrations.coinbase import Coinbase
from market_analytics_platform.integrations.kraken_v1 import (
    KrakenV1,
)
from market_analytics_platform.integrations.kraken_v2 import (
    KrakenV2,
)
from market_analytics_platform.integrations.register import register_integrations
from market_analytics_platform.store import Store
from market_analytics_platform.websocket import WebsocketClient

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def main() -> None:
    config = load_config("config.json")
    store = Store()
    initial_state = store.get_summary()
    ws_integrations = register_integrations(
        integrations_config=config.integrations,
        integrations=[KrakenV1, KrakenV2, Coinbase],
        store=store,
        websocket_cls=WebsocketClient,
    )

    async def run():
        try:
            await asyncio.gather(*[client.read() for client in ws_integrations])
        finally:
            store.close()
            print("Initial state:", initial_state)
            print(store.get_summary())

    try:
        asyncio.run(run())
    except KeyboardInterrupt:
        print("Keyboard interrupt received, shutting down...")


if __name__ == "__main__":
    # run without uv
    main()
