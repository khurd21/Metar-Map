from dataclasses import dataclass
from typing import Optional
import requests

from metar_map.config import load_config


@dataclass
class MetarData:
    icao: Optional[str]
    name: Optional[str]
    metar_type: Optional[str]
    flight_category: Optional[str]
    latitude: Optional[float]
    longitude: Optional[float]
    wind_gust: Optional[int]
    raw: Optional[str]
    snow: Optional[float]

    @property
    def lightning(self) -> bool:
        return self.raw is not None and "LTG" in self.raw.upper()


class MetarClient:
    """Client for gathering weather data from a METAR station."""

    def __init__(self, config_path: Optional[str] = None):
        config = load_config(config_path=config_path)
        self.base_url: str = config.get("base_url", "")
        self.metar_endpoint: str = config.get("endpoints", {}).get("metar", "")

    def get_metar(self, ids: list[str]) -> list[MetarData]:
        """
        Fetch METAR data for the given station IDs.
        """
        try:
            ids_param = ",".join(ids)
            url = f"{self.base_url}{self.metar_endpoint}?ids={ids_param}&format=json"
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            return [
                MetarData(
                    icao=item.get("icaoId"),
                    name=item.get("name"),
                    metar_type=item.get("metarType"),
                    flight_category=item.get("fltCat"),
                    latitude=item.get("lat"),
                    longitude=item.get("lon"),
                    wind_gust=item.get("wgst"),
                    raw=item.get("rawOb"),
                    snow=item.get("snow"),
                )
                for item in response.json()
            ]
        except Exception:
            return []
