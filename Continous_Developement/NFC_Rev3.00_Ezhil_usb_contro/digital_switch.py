"""
Digital Switch helper for NFC_Rev3.00.

This module provides a minimal generic digital switch controller for
MCP2221A GPIO loads.
"""

import importlib
import os
import time


class DigitalSwitchController:
    """Generic MCP2221A digital switch controller."""

    def __init__(self):
        os.environ["BLINKA_MCP2221"] = "1"
        self._state = False
        self._use_blinka = False
        self._pin = None
        self._mcp = None

        try:
            board = importlib.import_module("board")
            digitalio = importlib.import_module("digitalio")
            self._pin = digitalio.DigitalInOut(board.G0)
            self._pin.direction = digitalio.Direction.OUTPUT
            self._pin.value = False
            self._use_blinka = True
            self._log_source = "Blinka"
        except Exception as blinka_exc:
            try:
                mcp_module = importlib.import_module("MCP2221.MCP2221")
                MCP2221Class = mcp_module.MCP2221
                mcp = MCP2221Class()
                mcp.InitGP(0, mcp_module.TYPE.OUTPUT, False)
                self._mcp = mcp
                self._use_blinka = False
                self._log_source = "MCP2221"
            except Exception as mcp_exc:
                details = str(mcp_exc)
                if 'list index out of range' in details or 'Device not found' in details:
                    raise RuntimeError(
                        "Failed to initialize digital switch controller: MCP2221A device not found. "
                        "Please connect the MCP2221A and try again."
                    ) from mcp_exc
                raise RuntimeError(
                    "Failed to initialize digital switch controller. "
                    f"Blinka error: {blinka_exc}; MCP2221 fallback error: {mcp_exc}. "
                    "Install adafruit-blinka and hidapi, or MCP2221, and ensure your MCP2221A device is connected."
                ) from mcp_exc

    def turn_on(self):
        try:
            if not self._state:
                if self._use_blinka:
                    self._pin.value = True
                else:
                    self._mcp.WriteGP(0, 1)
                self._state = True
        except Exception as exc:
            raise RuntimeError(f"Failed to turn ON digital switch: {exc}") from exc

    def turn_off(self):
        try:
            if self._state:
                if self._use_blinka:
                    self._pin.value = False
                else:
                    self._mcp.WriteGP(0, 0)
                self._state = False
        except Exception as exc:
            raise RuntimeError(f"Failed to turn OFF digital switch: {exc}") from exc

    def get_state(self):
        return self._state

    def restart_sequence(self, delay_s: float = 5.0):
        self.turn_off()
        time.sleep(delay_s)
        self.turn_on()


def run_digital_switch():
    controller = DigitalSwitchController()
    controller.restart_sequence()
    return controller.get_state()
