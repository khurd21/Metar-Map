from enum import Enum, auto
from dataclasses import dataclass
from typing import Any, Optional

from metar_map.config import load_config


class LEDColor(Enum):
    # TODO: Make these (255, 255, 255) RGBs
    GREEN = auto()
    BLUE = auto()
    RED = auto()
    PINK = auto()
    YELLOW = auto()
    WHITE = auto()
    BRIGHT_BLUE = auto()


@dataclass
class LEDPattern:
    color: LEDColor
    total_duration_s: float = 10.0
    blink: bool = False
    blink_speed_s: float = 0.5


def _map_to_led_pattern(config: Any) -> LEDPattern:
    return LEDPattern(
        color=config.get("color"),
        total_duration_s=config.get("duration"),
        blink=config.get("blink"),
        blink_speed_s=config.get("blink_speed"),
    )


class LEDPatternBuilder:
    def __init__(self, config_path: Optional[str] = None):
        self._config = load_config(config_path=config_path)

    def build_led_patterns(
        self, flight_category: str, lightning: bool, snow: bool
    ) -> list[LEDPattern]:
        patterns: list[LEDPattern] = []
        led_patterns = self._config.get("led_patterns", {})
        category_config = led_patterns.get(flight_category)

        if category_config:
            patterns.append(_map_to_led_pattern(category_config))
        if lightning:
            patterns.append(_map_to_led_pattern(led_patterns.get("LIGHTING")))
        if snow:
            patterns.append(_map_to_led_pattern(led_patterns.get("SNOW")))

        return patterns
