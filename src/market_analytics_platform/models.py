from dataclasses import dataclass
from typing import Protocol


@dataclass
class Event:
    integration: str
    payload: dict
    channel: str
    instrument_id: str


class OnMessage(Protocol):
    def __call__(self, message: str) -> Event: ...
