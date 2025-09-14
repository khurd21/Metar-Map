import threading
import time
from typing import Any

import neopixel  # type: ignore
import board  # type: ignore

from metar_map.pattern_builder import LEDPattern, LEDColor


class LEDController:
    def __init__(self, num_leds: int, gpio_pin=board.D18, brightness: float = 0.25):  # type: ignore
        self.num_leds = num_leds
        self._led_patterns: dict[int, list[LEDPattern]] = {}
        self._lock = threading.Lock()
        self._stop_event = threading.Event()

        self.strip = neopixel.NeoPixel(
            pin=gpio_pin,  # type: ignore
            n=num_leds,
            brightness=brightness,
            auto_write=False,
        )

        self._thread = threading.Thread(target=self._run_loop, daemon=True)
        self._thread.start()

    def _set_led(self, led_index: int, color: tuple[int, int, int]):
        r, g, b = color
        self.strip[led_index] = (g, r, b)
        self.strip.show()

    def update_patterns(self, led_index: int, patterns: list[LEDPattern]):
        with self._lock:
            self._led_patterns[led_index] = patterns.copy()
            # Reset last_states for this LED so pattern_index is always valid
            if hasattr(self, "_last_states"):
                self._last_states.pop(led_index, None)

    def stop(self):
        self._stop_event.set()
        self._thread.join()
        self.clear_all()

    def clear_all(self):
        for i in range(self.num_leds):
            self._set_led(i, LEDColor.OFF.rgb)
        self.strip.show()

    def _run_loop(self):
        self._last_states: dict[int, dict[str, Any]] = {}
        while not self._stop_event.is_set():
            now = time.monotonic()
            with self._lock:
                for led_index in range(self.num_leds):
                    patterns = self._led_patterns.get(led_index)
                    if not patterns:
                        self._set_led(led_index, LEDColor.OFF.rgb)
                        continue

                    if led_index not in self._last_states:
                        self._last_states[led_index] = {
                            "pattern_index": 0,
                            "pattern_end": now + patterns[0].total_duration_s,
                            "led_on": True,
                            "next_blink": (
                                now + patterns[0].blink_speed_s
                                if patterns[0].blink
                                else None
                            ),
                        }

                    state = self._last_states[led_index]
                    # Ensure pattern_index is always valid
                    if state["pattern_index"] >= len(patterns):
                        state["pattern_index"] = 0
                        state["pattern_end"] = now + patterns[0].total_duration_s
                        state["led_on"] = True
                        state["next_blink"] = (
                            now + patterns[0].blink_speed_s
                            if patterns[0].blink
                            else None
                        )

                    pattern = patterns[int(state["pattern_index"])]

                    if (
                        pattern.blink
                        and state["next_blink"]
                        and now >= state["next_blink"]
                    ):
                        state["led_on"] = not state["led_on"]
                        state["next_blink"] = now + pattern.blink_speed_s

                    self._set_led(
                        led_index,
                        pattern.color.rgb if state["led_on"] else LEDColor.OFF.rgb,
                    )

                    if now >= state["pattern_end"]:
                        state["pattern_index"] = (state["pattern_index"] + 1) % len(
                            patterns
                        )
                        next_pattern = patterns[int(state["pattern_index"])]
                        state["pattern_end"] = now + next_pattern.total_duration_s
                        state["led_on"] = True
                        state["next_blink"] = (
                            now + next_pattern.blink_speed_s
                            if next_pattern.blink
                            else None
                        )

            time.sleep(0.05)


if __name__ == "__main__":

    NUM_LEDS = 10
    controller = LEDController(num_leds=NUM_LEDS, brightness=0.2)

    # Define three patterns: solid RED, blinking WHITE, solid GREEN
    solid_red = LEDPattern(color=LEDColor.RED, total_duration_s=2, blink=False)
    blink_white = LEDPattern(
        color=LEDColor.WHITE, total_duration_s=2, blink=True, blink_speed_s=0.3
    )
    solid_green = LEDPattern(color=LEDColor.GREEN, total_duration_s=2, blink=False)
    patterns1 = [solid_red, blink_white, solid_green]

    blink_blue = LEDPattern(color=LEDColor.BLUE, total_duration_s=5, blink=True)
    blink_pink = LEDPattern(color=LEDColor.PINK, total_duration_s=5, blink=True)
    patterns2 = [blink_blue, blink_pink]

    try:
        while True:
            for i in range(NUM_LEDS):
                controller.update_patterns(i, patterns1)
            time.sleep(60)
            for i in range(NUM_LEDS):
                controller.update_patterns(i, patterns2)
            time.sleep(60)
    except KeyboardInterrupt:
        print("\nStopping LED controller...")
        controller.stop()
        print("Done.")
