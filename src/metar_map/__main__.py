import time
from metar_map.client import MetarClient
from metar_map.pattern_builder import LEDPatternBuilder
from metar_map.led_controller import LEDController
from metar_map.config import load_config
from metar_map.logger import Logger

if __name__ == "__main__":
    config = load_config()
    icao_codes: list[str] = config.get("icao_codes", [])
    refresh_time: int = int(config.get("refresh_time", 1800))
    client = MetarClient()
    builder = LEDPatternBuilder()
    controller = LEDController(num_leds=len(icao_codes))
    logger = Logger()
    logger.info(f"Metar Map started up with the following settings:")
    logger.info(f"{config}")
    try:
        while True:
            metar_data = client.get_metar(icao_codes)
            for i, data in enumerate(metar_data):
                logger.debug("----------------------------------------")
                logger.debug(f"Index: {i}")
                if data.flight_category is None:
                    logger.warning(
                        f"Flight category for `{data.icao}` was None. Skipping..."
                    )
                    continue
                patterns = builder.build_led_patterns(
                    flight_category=data.flight_category,
                    lightning=data.lightning,
                    snow=bool(data.snow),
                )
                controller.update_patterns(i, patterns)
                logger.debug(f"ICAO: {data.icao}")
                logger.debug(f"Flight Category: {data.flight_category}")
                for pattern in patterns:
                    logger.debug(str(pattern))

            time.sleep(refresh_time)

    except KeyboardInterrupt:
        logger.info("\nStopping LED controller...")
        controller.stop()
        logger.info("Done.")
