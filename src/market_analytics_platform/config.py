import json
from dataclasses import dataclass
from pathlib import Path

IntegrationName = str


@dataclass
class IntegrationConfig:
    ws_url: str
    instruments_url: str


IntegrationsConfig = dict[IntegrationName, IntegrationConfig]


@dataclass
class Config:
    integrations: IntegrationsConfig


def load_config(path: Path) -> Config:
    with Path.open(path) as f:
        config = json.load(f)

    cfg = {}
    for name, conf in config.get("integrations", {}).items():
        cfg[name] = IntegrationConfig(
            ws_url=conf["ws_url"],
            instruments_url=conf["instruments_url"],
        )

    return Config(integrations=cfg)
