import time
from metar_map.client import MetarClient
from metar_map.pattern_builder import LEDPatternBuilder
from metar_map.led_controller import LEDController
from metar_map.config import load_config
from metar_map.logger import Logger

if __name__ == "__main__":
    config = load_config()
    raw_icao_codes: list[str] = config.get("icao_codes", [])
    refresh_time: int = int(config.get("refresh_time", 1800))
    brightness: float = float(config.get("brightness", 0.15))
    led_map = [
        (i, code) for i, code in enumerate(raw_icao_codes) if code and code.strip()
    ]
    filtered_icao_codes = [code for _, code in led_map]
    client = MetarClient()
    builder = LEDPatternBuilder()
    controller = LEDController(num_leds=len(raw_icao_codes), brightness=brightness)
    logger = Logger()
    logger.info(f"Metar Map started up with the following settings:\n{config}")
    try:
        while True:
            metar_data = client.get_metar(filtered_icao_codes)
            metar_lookup = {d.icao: d for d in metar_data if d.icao}
            for led_index, icao in led_map:
                data = metar_lookup.get(icao)
                logger.debug("----------------------------------------")
                logger.debug(f"LED Index: {led_index} ICAO: {icao}")
                if not data:
                    logger.warning(f"No METAR data for `{icao}`. Skipping...")
                    continue
                if data.flight_category is None:
                    logger.warning(
                        f"Flight category for `{data.icao}` was None. Skipping..."
                    )
                    continue
                patterns = builder.build_led_patterns(
                    flight_category=data.flight_category,
                    lightning=data.lightning,
                    snow=bool(data.snow),
                    gusts=bool(data.wind_gust),
                )
                controller.update_patterns(led_index, patterns)
                logger.debug(f"ICAO: {data.icao}")
                logger.debug(f"Flight Category: {data.flight_category}")
                for pattern in patterns:
                    logger.debug(str(pattern))

            time.sleep(refresh_time)

    except KeyboardInterrupt:
        logger.info("\nStopping LED controller...")
        controller.stop()
        logger.info("Done.")
