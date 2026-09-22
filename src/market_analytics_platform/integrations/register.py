import logging

from market_analytics_platform.config import IntegrationsConfig
from market_analytics_platform.domain import (
    Store,
    WebsocketClient,
)
from market_analytics_platform.integrations.base import BaseIntegration

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def register_integrations(
    integrations_config: IntegrationsConfig,
    integrations: list[BaseIntegration],
    store: Store,
    websocket_cls: type[WebsocketClient],
) -> list[BaseIntegration]:
    registered_integrations = []
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
        registered_integrations.append(integration_client)
    return registered_integrations


class MissingIntegrationConfigError(Exception):
    def __init__(self, integration_name: str):
        self.integration_name = integration_name
        super().__init__(f"Missing configuration for integration: {integration_name}")
