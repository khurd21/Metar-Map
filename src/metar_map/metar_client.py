"""
A client for getting metar station data.
"""


class MetarClient:
    """Client for gathering weather data from a METAR station."""

    def __init__(self):
        self.base_url: str = ""
        self.metar_endpoint: str = ""
