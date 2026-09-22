import asyncio
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI

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

config = load_config("config.json")
store = Store()
initial_state = store.get_summary()
ws_integrations = register_integrations(
    integrations_config=config.integrations,
    integrations=[KrakenV1, KrakenV2, Coinbase],
    store=store,
    websocket_cls=WebsocketClient,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield


def main() -> None:

    async def run():
        try:
            await ws_integrations.run()
        finally:
            store.close()
            print("Initial state:", initial_state)
            print(store.get_summary())

    try:
        asyncio.run(run())
    except KeyboardInterrupt:
        print("Keyboard interrupt received, shutting down...")
