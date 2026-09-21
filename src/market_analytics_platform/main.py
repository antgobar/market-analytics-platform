import asyncio
import logging

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
    client_v1 = KrakenV1(store)
    client_v2 = KrakenV2(store)

    async def run():
        try:
            await asyncio.gather(
                # client_v1.read(),
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
