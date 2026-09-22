from collections.abc import AsyncGenerator
from dataclasses import dataclass
from typing import Protocol


@dataclass
class Event:
    integration: str
    payload: dict
    channel: str
    instrument_id: str


class Store(Protocol):
    def save(self, event: Event) -> None: ...


class WebsocketClient(Protocol):
    async def send(self, message: dict) -> None: ...
    async def receive(self) -> AsyncGenerator[str]: ...
