import neopixel
import board
from metar_map.pattern_builder import LEDPattern, LEDColor
import threading
import time


class LEDController:
    def __init__(self, num_leds: int, gpio_pin=board.D18, brightness: float = 0.25):
        self.num_leds = num_leds
        self._led_patterns: dict[int, list[LEDPattern]] = {}
        self._lock = threading.Lock()
        self._stop_event = threading.Event()

        # NeoPixel object
        self.strip = neopixel.NeoPixel(
            pin=gpio_pin,
            n=num_leds,
            brightness=brightness,  # 0.0-1.0
            auto_write=False,  # we control when to show
        )

        self._thread = threading.Thread(target=self._run_loop, daemon=True)
        self._thread.start()

    def _set_led(self, led_index: int, color: tuple[int, int, int]):
        self.strip[led_index] = color
        self.strip.show()

    def update_patterns(self, led_index: int, patterns: list[LEDPattern]):
        with self._lock:
            self._led_patterns[led_index] = patterns.copy()

    def stop(self):
        self._stop_event.set()
        self._thread.join()
        self.clear_all()

    def clear_all(self):
        for i in range(self.num_leds):
            self.strip[i] = (0, 0, 0)
        self.strip.show()

    def _run_loop(self):
        last_states: dict[int, dict] = {}

        while not self._stop_event.is_set():
            now = time.monotonic()
            with self._lock:
                # Always iterate over all LED indices
                for led_index in range(self.num_leds):
                    patterns = self._led_patterns.get(led_index)
                    if not patterns:
                        # No pattern assigned, turn off LED
                        self._set_led(led_index, LEDColor.OFF.rgb)
                        continue

                    # Initialize state if missing
                    if led_index not in last_states:
                        last_states[led_index] = {
                            "pattern_index": 0,
                            "pattern_end": now + patterns[0].total_duration_s,
                            "led_on": True,
                            "next_blink": (
                                now + patterns[0].blink_speed_s
                                if patterns[0].blink
                                else None
                            ),
                        }

                    state = last_states[led_index]
                    pattern = patterns[state["pattern_index"]]

                    # Blink logic
                    if (
                        pattern.blink
                        and state["next_blink"]
                        and now >= state["next_blink"]
                    ):
                        state["led_on"] = not state["led_on"]
                        state["next_blink"] = now + pattern.blink_speed_s

                    # Set LED
                    self._set_led(
                        led_index,
                        pattern.color.rgb if state["led_on"] else LEDColor.OFF.rgb,
                    )

                    # Move to next pattern if duration expired
                    if now >= state["pattern_end"]:
                        state["pattern_index"] = (state["pattern_index"] + 1) % len(
                            patterns
                        )
                        next_pattern = patterns[state["pattern_index"]]
                        state["pattern_end"] = now + next_pattern.total_duration_s
                        state["led_on"] = True
                        state["next_blink"] = (
                            now + next_pattern.blink_speed_s
                            if next_pattern.blink
                            else None
                        )

            time.sleep(0.05)
