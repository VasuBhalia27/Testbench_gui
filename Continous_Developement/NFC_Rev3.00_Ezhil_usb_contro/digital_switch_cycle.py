"""
Standalone digital switch cycle script for MCP2221A.

This file contains its own MCP2221A controller class and requires only
`board` and `digitalio` from Adafruit Blinka.

Usage:
  python digital_switch_cycle.py
"""

import os
import time
import warnings

# Ensure Blinka MCP2221 support is enabled before importing the driver.
os.environ["BLINKA_MCP2221"] = "1"


class DigitalSwitchController:
    """Controls a generic digital switch via MCP2221A GPIO pin G0.

    If Adafruit Blinka or the MCP2221 driver is not available, this class
    will fall back to a software-emulated controller that logs actions but
    allows the GUI/automation to keep running on developer machines.
    """

    def __init__(self):
        # Attempt to import hardware libraries; fall back to an emulated
        # controller if the environment is missing required packages or
        # the device cannot be initialised.
        try:
            import board
            import digitalio
        except ModuleNotFoundError:
            warnings.warn(
                "Adafruit Blinka or MCP2221 support not installed; using emulated digital switch",
                RuntimeWarning,
            )
            self._emulate = True
            self._state = False
            return

        try:
            self._emulate = False
            self.board = board
            self.digitalio = digitalio
            self.pin = self.digitalio.DigitalInOut(self.board.G0)
            self.pin.direction = self.digitalio.Direction.OUTPUT
            self.pin.value = False
            self._state = False
        except Exception as exc:
            warnings.warn(
                f"MCP2221A GPIO initialisation failed ({exc}); falling back to emulated controller",
                RuntimeWarning,
            )
            self._emulate = True
            self._state = False

    def turn_on(self):
        if getattr(self, "_emulate", False):
            # Emulate switch on
            self._state = True
            warnings.warn("Emulated digital switch: turned ON", RuntimeWarning)
            return
        try:
            if not self._state:
                self.pin.value = True
                self._state = True
        except Exception as exc:
            raise RuntimeError(f"Failed to turn ON digital switch: {exc}") from exc

    def turn_off(self):
        if getattr(self, "_emulate", False):
            # Emulate switch off
            self._state = False
            warnings.warn("Emulated digital switch: turned OFF", RuntimeWarning)
            return
        try:
            if self._state:
                self.pin.value = False
                self._state = False
        except Exception as exc:
            raise RuntimeError(f"Failed to turn OFF digital switch: {exc}") from exc

    def get_state(self):
        return self._state

    def restart_sequence(self, delay_s: float = 2.0):
        self.turn_off()
        time.sleep(delay_s)
        self.turn_on()


def main() -> int:
    controller = DigitalSwitchController()

    controller.turn_off()
    controller.turn_on()
    time.sleep(2.0)
    controller.turn_off()

    print("Switch cycle complete")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
