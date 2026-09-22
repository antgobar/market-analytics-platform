import asyncio
import logging
from typing import Protocol

from market_analytics_platform.config import Integrations, load_config
from market_analytics_platform.integrations.kraken_v1 import (
    KrakenV1,
)
from market_analytics_platform.integrations.kraken_v2 import (
    KrakenV2,
)
from market_analytics_platform.store import Store
from market_analytics_platform.websocket import WebsocketClient

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def main() -> None:
    config = load_config("config.json")
    store = Store()
    client_v1 = KrakenV1(
        store,
        websocket_client=WebsocketClient(
            config.integrations[KrakenV1.integration_name].ws_url
        ),
        instruments_url=config.integrations[KrakenV1.integration_name].instruments_url,
    )
    client_v2 = KrakenV2(
        store,
        websocket_client=WebsocketClient(
            config.integrations[KrakenV2.integration_name].ws_url
        ),
        instruments_url=config.integrations[KrakenV2.integration_name].instruments_url,
    )

    async def run():
        try:
            await asyncio.gather(
                client_v1.read(),
                client_v2.read(),
            )
        finally:
            store.close()
            print(store.get_summary())

    try:
        asyncio.run(run())
    except KeyboardInterrupt:
        print("Keyboard interrupt received, shutting down...")


if __name__ == "__main__":
    # run without uv
    main()


class Integration(Protocol):
    integration_name: str

    def __init__(
        self,
        store: Store,
        websocket_client: WebsocketClient,
        instruments_url: str,
    ) -> None: ...


class LoadedIntegration(Protocol):
    async def read(self) -> None: ...


def register_integrations(
    integrations_config: Integrations,
    integrations: list[Integration],
    store: Store,
    websocket_cls: type[WebsocketClient],
) -> list[LoadedIntegration]:
    registered_integrations = []
    for integration in integrations:
        integration_client = integration(
            store=store,
            websocket_client=websocket_cls(
                integrations_config[integration.integration_name].ws_url
            ),
            instruments_url=integrations_config[
                integration.integration_name
            ].instruments_url,
        )
        registered_integrations.append(integration_client)
    return registered_integrations
