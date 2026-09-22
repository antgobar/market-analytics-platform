import logging

from market_analytics_platform.config import IntegrationsConfig
from market_analytics_platform.domain import (
    Integration,
    LoadedIntegration,
    Store,
    WebsocketClient,
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def register_integrations(
    integrations_config: IntegrationsConfig,
    integrations: list[type[Integration]],
    store: Store,
    websocket_cls: type[WebsocketClient],
) -> list[LoadedIntegration]:
    registered_integrations = []
    for integration in integrations:
        integration_config = integrations_config.get(integration.integration_name)
        if not integration_config:
            logger.warning(
                "Integration %s is not configured", integration.integration_name
            )
            continue

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
