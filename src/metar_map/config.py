import importlib.resources as resources
import os
from typing import Any, Optional

import yaml


def load_config(config_path: Optional[str] = None) -> dict[str, Any]:
    if config_path is None:
        config_path = str(resources.files("metar_map.static").joinpath("config.yaml"))
    if not os.path.isfile(config_path):
        raise FileNotFoundError(f"Config file not found: {config_path}")
    with open(config_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)
