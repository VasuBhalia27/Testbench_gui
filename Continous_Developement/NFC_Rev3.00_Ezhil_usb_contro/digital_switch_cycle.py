"""
Standalone digital switch cycle script for MCP2221A.

This file contains its own MCP2221A controller class and requires only
`board` and `digitalio` from Adafruit Blinka.

Usage:
  python digital_switch_cycle.py
"""

import os
import time

# Ensure Blinka MCP2221 support is enabled before importing the driver.
os.environ["BLINKA_MCP2221"] = "1"

import board
import digitalio


class DigitalSwitchController:
    """Controls a generic digital switch via MCP2221A GPIO pin G0."""

    def __init__(self):
        try:
            self.pin = digitalio.DigitalInOut(board.G0)
            self.pin.direction = digitalio.Direction.OUTPUT
            self.pin.value = False
            self._state = False
        except Exception as exc:
            raise RuntimeError(
                f"Failed to initialize MCP2221A GPIO controller: {exc}. "
                "Ensure the MCP2221A is plugged in and Blinka is installed."
            ) from exc

    def turn_on(self):
        try:
            if not self._state:
                self.pin.value = True
                self._state = True
        except Exception as exc:
            raise RuntimeError(f"Failed to turn ON digital switch: {exc}") from exc

    def turn_off(self):
        try:
            if self._state:
                self.pin.value = False
                self._state = False
        except Exception as exc:
            raise RuntimeError(f"Failed to turn OFF digital switch: {exc}") from exc

    def get_state(self):
        return self._state

    def restart_sequence(self, delay_s: float = 5.0):
        self.turn_off()
        time.sleep(delay_s)
        self.turn_on()


def main() -> int:
    controller = DigitalSwitchController()

    controller.turn_off()
    controller.turn_on()
    time.sleep(5.0)
    controller.turn_off()

    print("Switch cycle complete")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
