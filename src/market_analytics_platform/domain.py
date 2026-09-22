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


class Integration(Protocol):
    integration_name: str

    def __init__(
        self,
        store: Store,
        websocket_client: WebsocketClient,
        instruments_url: str,
    ) -> None: ...


class LoadedIntegration(Protocol):
    async def read(self) -> None: ...
