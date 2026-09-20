import logging
from typing import Any

from market_analytics_platform.integrations.kraken_v1 import (
    KrakenV1,
)
from market_analytics_platform.integrations.kraken_v2 import (
    KrakenV2,
)
from market_analytics_platform.store import Store

logging.basicConfig(level=logging.INFO)

logger = logging.getLogger(__name__)


def main() -> None:
    store = Store()

    def kraken_on_message(message: str) -> Any:
        store.save_event("kraken", message)

    client_v1 = KrakenV1(on_message=kraken_on_message)
    client_v2 = KrakenV2(on_message=kraken_on_message)
    try:
        client_v1.read()
        client_v2.read()
    finally:
        store.close()
        print(store.get_summary())


if __name__ == "__main__":
    main()
