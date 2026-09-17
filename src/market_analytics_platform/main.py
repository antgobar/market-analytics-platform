import asyncio
import json
import logging
from collections.abc import Callable
from pathlib import Path
from typing import Any, Self

from websockets.asyncio.client import ClientConnection, connect

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

WS_URL = "wss://futures.kraken.com/ws/v1"
OUTPUT_PATH = Path("cached_messages.json")
TOTAL_MESSAGES = 100
SYMBOLS = [
    "PI_XBTUSD",
    # "PI_ETHUSD",
    # "PI_XRPUSD",
    # "FI_ETHUSD_210625",
    # "FI_XBTUSD_210625",
]

Message = dict[str, Any] | None
Flusher = Callable[[list[Message]], None]
OnReceive = Callable[[str], Message]


class KrakenClient:
    def __init__(
        self: Self, url: str, on_receive: OnReceive, flush: Flusher, limit: int
    ) -> None:
        self.url = url
        self.on_receive = on_receive
        self.flush = flush
        self.limit = limit

    def consume(self: Self, limit: int) -> None:
        try:
            asyncio.run(self.collect_messages(limit))
        except KeyboardInterrupt:
            print("interrupted")

    @staticmethod
    async def subscribe(ws: ClientConnection, symbols: list[str]):
        await ws.send(
            json.dumps(
                {
                    "event": "subscribe",
                    "feed": "ticker",
                    "product_ids": symbols,
                }
            )
        )
        await ws.send(json.dumps({"event": "subscribe", "feed": "heartbeat"}))

    async def collect_messages(self: Self, symbols: list[str]) -> list[Message]:
        messages: list[Message] = []
        try:
            print("starting...")
            async with connect(self.url) as ws:
                await self.subscribe(ws, symbols)

                async for raw_message in ws:
                    message = self.on_receive(raw_message)

                    messages.append(message)
                    logger.info("Message count: %d", len(messages))
                    if len(messages) >= self.limit:
                        logger.info("Reached message limit of %d.", self.limit)
                        break
        finally:
            self.flush(messages)
            print("exiting...")
        return messages


def on_receive(message: str) -> Message:
    try:
        return json.loads(message)
    except json.JSONDecodeError:
        logger.warning("Failed to decode message: %s", message)


def main() -> None:
    client = KrakenClient(
        WS_URL,
        on_receive=on_receive,
        flush=lambda messages: OUTPUT_PATH.write_text(
            json.dumps(messages),
        ),
        limit=TOTAL_MESSAGES,
    )
    client.consume(SYMBOLS)


if __name__ == "__main__":
    main()
