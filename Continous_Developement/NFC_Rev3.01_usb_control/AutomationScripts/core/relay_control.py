"""Automation-facing wrapper for external USB relay control.

RELAY MAPPING:
  relay_short_capa (ID 1)     → Blue capacitors CAPA test path (pulse 1.0 sec)
  relay_reset_switch (ID 2)   → Red switches logic control (pulse 0.2 sec)

This wrapper exposes high-level methods for CAPA test automation:
  • connect()         → Open serial port to relay board
  • disconnect()      → Close serial port
  • short_capa(dur)   → Pulse relay 1 to short blue capacitors
  • reset_switch(dur) → Pulse relay 2 to reset red switches
"""
from typing import Optional

from Functional.usb_relay import USBRelayController, USBRelayError


class RelayController:
    """High-level relay controller used by automation and GUI helpers."""

    def __init__(
        self,
        port: str,
        baudrate: int = 9600,
        timeout: float = 1.0,
        close_cmd_template: str = "RELAY {relay} ON",
        open_cmd_template: str = "RELAY {relay} OFF",
        relay_short_capa: int = 1,
        relay_reset_switch: int = 2,
    ):
        self._relay = USBRelayController(
            port=port,
            baudrate=baudrate,
            timeout=timeout,
            close_cmd_template=close_cmd_template,
            open_cmd_template=open_cmd_template,
            relay_short_capa=relay_short_capa,
            relay_reset_switch=relay_reset_switch,
        )

    def connect(self) -> None:
        self._relay.open()

    def disconnect(self) -> None:
        self._relay.close()

    def short_capa(self, duration: float = 1.0) -> None:
        self._relay.short_capa(duration)

    def reset_switch(self, duration: float = 0.2) -> None:
        self._relay.reset_switch(duration)

    def pulse_relay(self, relay: int, duration: float = 0.2) -> None:
        self._relay.pulse_relay(relay, duration)

    def send_command(self, command: str) -> None:
        self._relay.send_command(command)

    def is_connected(self) -> bool:
        return self._relay._serial is not None and self._relay._serial.is_open


class RelayUnavailableError(USBRelayError):
    pass
