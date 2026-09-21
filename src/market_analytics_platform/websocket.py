import json
import logging
from collections.abc import AsyncGenerator
from typing import Any, Self

from websockets.asyncio.client import ClientConnection, connect

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class WebsocketClient:
    def __init__(self: Self, url: str) -> None:
        self.url = url
        self.ws: ClientConnection | None = None

    async def connect(self: Self) -> None:
        self.ws = await connect(self.url)
        logger.info("WebsocketClient connected to URL: %s", self.url)

    async def send(self: Self, payload: dict[str, Any]) -> None:
        if self.ws is None:
            await self.connect()
        await self.ws.send(json.dumps(payload))

    async def receive(self: Self) -> AsyncGenerator[str]:
        if self.ws is None:
            await self.connect()
        try:
            async for message in self.ws:
                yield message

        finally:
            if self.ws is not None:
                await self.ws.close()
