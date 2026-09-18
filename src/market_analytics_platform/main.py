import json

from market_analytics_platform.integrations.kraken import (
    OUTPUT_PATH,
    SYMBOLS,
    KrakenClient,
    on_message,
)


def main() -> None:
    client = KrakenClient(
        on_message=on_message,
        flush=lambda messages: OUTPUT_PATH.write_text(
            json.dumps(messages),
        ),
    )
    client.consume(SYMBOLS)


if __name__ == "__main__":
    main()
