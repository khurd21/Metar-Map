from metar_map.client import MetarClient
from metar_map.pattern_builder import LEDPatternBuilder

if __name__ == "__main__":
    client = MetarClient()
    builder = LEDPatternBuilder()
    print(f"Base URL: {client.base_url}")
    print(f"METAR Endpoint: {client.metar_endpoint}")
    metar_data = client.get_metar(["PANC", "CYUL", "CRVR"])
    for i, data in enumerate(metar_data):
        print("----------------------------------------")
        print(f"Index: {i}")
        if data.flight_category is None:
            print("Flight category was found to be none.")
            continue
        patterns = builder.build_led_patterns(
            flight_category=data.flight_category,
            lightning=data.lightning,
            snow=bool(data.snow),
        )
        print(f"Flight Category: {data.flight_category}")
        for pattern in patterns:
            print(pattern)
