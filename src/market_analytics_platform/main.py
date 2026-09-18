import json

from market_analytics_platform.integrations.kraken import (
    OUTPUT_PATH,
    SYMBOLS,
    TOTAL_MESSAGES,
    KrakenClient,
    on_receive,
)


def main() -> None:
    client = KrakenClient(
        on_receive=on_receive,
        flush=lambda messages: OUTPUT_PATH.write_text(
            json.dumps(messages),
        ),
        limit=TOTAL_MESSAGES,
    )
    client.consume(SYMBOLS)


if __name__ == "__main__":
    main()
