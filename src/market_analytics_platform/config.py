import json
from pathlib import Path

from market_analytics_platform.domain import Config, IntegrationConfig


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
