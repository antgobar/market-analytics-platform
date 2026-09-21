import json
from dataclasses import dataclass
from pathlib import Path

IntegrationName = str


@dataclass
class IntegrationConfig:
    ws_url: str
    resource_url: str


Integrations = dict[IntegrationName, IntegrationConfig]


@dataclass
class Config:
    integrations: Integrations


def load_config(path: Path) -> Config:
    with Path.open(path) as f:
        config = json.load(f)

    cfg = {}
    for name, conf in config.get("integrations", {}).items():
        cfg[name] = IntegrationConfig(
            ws_url=conf["ws_url"],
            resource_url=conf["resource_url"],
        )

    return Config(integrations=cfg)
