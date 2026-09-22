import asyncio
import logging
from typing import Self

from market_analytics_platform.domain import (
    IntegrationName,
    IntegrationsConfig,
    Store,
    WebsocketClient,
)
from market_analytics_platform.integrations.base import BaseIntegration

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Integrations:
    def __init__(self, integrations: dict[IntegrationName, BaseIntegration]):
        self.integrations = integrations

    async def run(self):
        await asyncio.gather(
            *[integration.run() for integration in self.integrations.values()]
        )

    async def shutdown(self: Self) -> None:
        await asyncio.gather(
            *[integration.shutdown() for integration in self.integrations.values()]
        )

    async def subscribe(
        self: Self,
        integration: IntegrationName,
        channel: str,
        instrument_ids: list[str],
    ) -> None:
        if integration not in self.integrations:
            raise IntegrationNotRegisteredError(integration)
        await self.integrations[integration].subscribe(channel, instrument_ids)

    async def unsubscribe(
        self: Self,
        integration: IntegrationName,
        channel: str,
        instrument_ids: list[str],
    ) -> None:
        if integration not in self.integrations:
            raise IntegrationNotRegisteredError(integration)
        await self.integrations[integration].unsubscribe(channel, instrument_ids)


def register_integrations(
    integrations_config: IntegrationsConfig,
    integrations: list[BaseIntegration],
    store: Store,
    websocket_cls: type[WebsocketClient],
) -> Integrations:
    registered_integrations = {}
    for integration in integrations:
        integration_config = integrations_config.get(integration.integration_name)
        if not integration_config:
            raise MissingIntegrationConfigError(integration.integration_name)

        integration_client = integration(
            store=store,
            websocket_client=websocket_cls(
                integrations_config[integration.integration_name].ws_url
            ),
            instruments_url=integrations_config[
                integration.integration_name
            ].instruments_url,
        )
        registered_integrations[integration.integration_name] = integration_client
    return Integrations(integrations=registered_integrations)


class MissingIntegrationConfigError(Exception):
    def __init__(self, integration_name: str):
        self.integration_name = integration_name
        super().__init__(f"Missing configuration for integration: {integration_name}")


class IntegrationNotRegisteredError(Exception):
    def __init__(self, integration_name: str):
        self.integration_name = integration_name
        super().__init__(f"Integration {integration_name} is not registered")
