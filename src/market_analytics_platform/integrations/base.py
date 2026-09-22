from abc import ABC, abstractmethod
from typing import Any, ClassVar, Self

from market_analytics_platform.domain import Event, Store, WebsocketClient


class BaseIntegration(ABC):
    integration_name: ClassVar[str]

    def __init__(
        self: Self, store: Store, websocket_client: WebsocketClient, **kwargs: Any
    ) -> None:
        self.store = store
        self.websocket_client = websocket_client

    def __init_subclass__(cls: type[Self], **kwargs):
        super().__init_subclass__(**kwargs)
        if "integration_name" not in cls.__dict__:
            raise TypeError(
                f"Subclass '{cls.__name__}' must define class attribute 'integration_name'"
            )
        if not isinstance(cls.__dict__["integration_name"], str):
            raise TypeError(
                f"Subclass '{cls.__name__}' must define 'integration_name' as a string"
            )

    @abstractmethod
    def handle_message(self: Self, message: str) -> Event | None: ...

    @abstractmethod
    async def subscribe(
        self: Self, channel: str, instrument_ids: list[str]
    ) -> None: ...

    @abstractmethod
    async def unsubscribe(
        self: Self, channel: str, instrument_ids: list[str]
    ) -> None: ...

    @abstractmethod
    async def run(self: Self) -> None: ...

    @abstractmethod
    async def shutdown(self: Self) -> None: ...
