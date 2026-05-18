"""
Digital Switch helper for NFC_Rev3.00.

This module provides a minimal generic digital switch controller for
MCP2221A GPIO loads.
"""

import os
import time


class DigitalSwitchController:
    """Generic MCP2221A digital switch controller."""

    def __init__(self):
        os.environ["BLINKA_MCP2221"] = "1"
        try:
            import board
            import digitalio

            self.pin = digitalio.DigitalInOut(board.G0)
            self.pin.direction = digitalio.Direction.OUTPUT
            self.pin.value = False
            self._state = False
        except (AttributeError, RuntimeError, OSError) as exc:
            raise RuntimeError(
                f"Failed to initialize MCP2221A digital switch: {exc}. "
                "Ensure the device is connected and BLINKA_MCP2221=1 is set."
            )

    def turn_on(self):
        try:
            if not self._state:
                self.pin.value = True
                self._state = True
        except (RuntimeError, OSError) as exc:
            raise RuntimeError(f"Failed to turn ON digital switch: {exc}")

    def turn_off(self):
        try:
            if self._state:
                self.pin.value = False
                self._state = False
        except (RuntimeError, OSError) as exc:
            raise RuntimeError(f"Failed to turn OFF digital switch: {exc}")

    def get_state(self):
        return self._state

    def restart_sequence(self, delay_s: float = 0.2):
        self.turn_off()
        time.sleep(delay_s)
        self.turn_on()


def run_digital_switch():
    controller = DigitalSwitchController()
    controller.restart_sequence()
    return controller.get_state()
