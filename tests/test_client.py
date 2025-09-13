"""
Unit tests for MetarClient and MetarData.
"""

from typing import Any

from unittest.mock import patch, MagicMock

from metar_map.client import MetarClient, MetarData


def test_metar_client_initialization():
    client = MetarClient()
    assert isinstance(client, MetarClient)
    assert hasattr(client, "base_url")
    assert hasattr(client, "metar_endpoint")


def test_metar_data_lightning_property():
    data = MetarData(
        icao="KJFK",
        name="JFK",
        metar_type="METAR",
        flight_category="VFR",
        latitude=40.6413,
        longitude=-73.7781,
        wind_gust=15,
        raw="KJFK 121651Z 18010G20KT LTG DSNT ALQDS",
        snow=None,
    )
    assert data.lightning is True
    data_no_ltg = MetarData(
        icao="KJFK",
        name="JFK",
        metar_type="METAR",
        flight_category="VFR",
        latitude=40.6413,
        longitude=-73.7781,
        wind_gust=15,
        raw="KJFK 121651Z 18010G20KT",
        snow=None,
    )
    assert data_no_ltg.lightning is False
    data_none = MetarData(
        icao="KJFK",
        name="JFK",
        metar_type="METAR",
        flight_category="VFR",
        latitude=40.6413,
        longitude=-73.7781,
        wind_gust=15,
        raw=None,
        snow=None,
    )
    assert data_none.lightning is False


def test_get_metar_makes_request_and_parses_response():
    client = MetarClient()
    mock_json: list[dict[str, Any]] = [
        {
            "icaoId": "KJFK",
            "name": "JFK",
            "metarType": "METAR",
            "fltCat": "VFR",
            "lat": 40.6413,
            "lon": -73.7781,
            "wgst": 15,
            "rawOb": "KJFK 121651Z 18010G20KT LTG DSNT ALQDS",
            "snow": None,
        },
        {
            "icaoId": "KLAX",
            "name": "LAX",
            "metarType": "METAR",
            "fltCat": "IFR",
            "lat": 33.9416,
            "lon": -118.4085,
            "wgst": 10,
            "rawOb": "KLAX 121651Z 25008KT",
            "snow": 0.0,
        },
    ]
    with patch("requests.get") as mock_get:
        mock_response = MagicMock()
        mock_response.json.return_value = mock_json
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        result = client.get_metar(["KJFK", "KLAX"])
        assert isinstance(result, list)
        assert len(result) == 2
        assert all(isinstance(item, MetarData) for item in result)
        assert result[0].icao == "KJFK"
        assert result[1].icao == "KLAX"
        assert result[0].lightning is True
        assert result[1].lightning is False


def test_get_metar_handles_empty_response():
    client = MetarClient()
    with patch("requests.get") as mock_get:
        mock_response = MagicMock()
        mock_response.json.return_value = []
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        result = client.get_metar(["KJFK"])
        assert isinstance(result, list)
        assert result == []


def test_get_metar_raises_for_status():
    client = MetarClient()
    with patch("requests.get") as mock_get:
        mock_response = MagicMock()
        mock_response.raise_for_status.side_effect = Exception("HTTP error")
        mock_get.return_value = mock_response
        result = client.get_metar(["KJFK"])
        assert isinstance(result, list)
        assert result == []
