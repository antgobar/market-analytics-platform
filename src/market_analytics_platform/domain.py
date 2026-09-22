from collections.abc import AsyncGenerator
from typing import Protocol

from market_analytics_platform.models import Event


class Store(Protocol):
    def save(self, event: Event) -> None: ...


class WebsocketClient(Protocol):
    async def send(self, message: dict) -> None: ...
    async def receive(self) -> AsyncGenerator[str]: ...
