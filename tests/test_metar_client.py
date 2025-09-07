"""
Tests for the MetarClient.
"""

from metar_map.metar_client import MetarClient


def test_metar_client_initialization():
    """Tests the client can be initialized."""
    client = MetarClient()
    assert isinstance(client, MetarClient)
