"""USB relay board helper for controlling external CAPA/reset hardware.

This module provides a small adapter around a serial-based USB relay board.
It is intentionally generic: the command templates can be configured to match
hardware that understands text-based relay commands.
"""

import time
from typing import Optional

try:
    import serial
except ImportError as exc:
    serial = None
    _SERIAL_IMPORT_ERROR = exc


class USBRelayError(Exception):
    """Raised when relay hardware cannot be controlled."""


class USBRelayController:
    """Interface to a serial-controlled USB relay board."""

    def __init__(
        self,
        port: str,
        baudrate: int = 9600,
        timeout: float = 1.0,
        close_cmd_template: str = "RELAY {relay} ON",
        open_cmd_template: str = "RELAY {relay} OFF",
        line_ending: str = "\r\n",
        relay_short_capa: int = 1,
        relay_reset_switch: int = 2,
    ):
        if serial is None:
            raise ImportError(
                "pyserial is required for USB relay support. "
                "Install it with `pip install pyserial`."
            )

        self.port = port
        self.baudrate = baudrate
        self.timeout = timeout
        self.close_cmd_template = close_cmd_template
        self.open_cmd_template = open_cmd_template
        self.line_ending = line_ending
        self.relay_short_capa = relay_short_capa
        self.relay_reset_switch = relay_reset_switch
        self._serial: Optional[serial.Serial] = None

    def open(self) -> None:
        """Open the serial port to the relay board."""
        if self._serial is not None and self._serial.is_open:
            return

        try:
            self._serial = serial.Serial(
                port=self.port,
                baudrate=self.baudrate,
                timeout=self.timeout,
                write_timeout=self.timeout,
            )
        except Exception as exc:
            raise USBRelayError(f"Unable to open USB relay port {self.port}: {exc}")

        # Give the relay board a moment to wake up.
        time.sleep(0.1)

    def close(self) -> None:
        """Close the serial connection to the relay board."""
        if self._serial is None:
            return

        try:
            if self._serial.is_open:
                self._serial.close()
        except Exception as exc:
            raise USBRelayError(f"Failed to close USB relay port: {exc}")
        finally:
            self._serial = None

    def _ensure_open(self) -> None:
        if self._serial is None or not self._serial.is_open:
            self.open()

    def _format_command(self, template: str, relay: int) -> str:
        return template.format(relay=relay).strip()

    def send_command(self, command: str) -> None:
        """Send a raw command string to the relay board."""
        self._ensure_open()
        payload = command
        if self.line_ending and not payload.endswith(self.line_ending):
            payload = payload + self.line_ending

        try:
            self._serial.write(payload.encode("utf-8"))
            self._serial.flush()
        except Exception as exc:
            raise USBRelayError(f"Failed to send relay command: {exc}")

    def activate_relay(self, relay: int) -> None:
        """Activate (close) the specified relay."""
        cmd = self._format_command(self.close_cmd_template, relay)
        self.send_command(cmd)

    def deactivate_relay(self, relay: int) -> None:
        """Deactivate (open) the specified relay."""
        cmd = self._format_command(self.open_cmd_template, relay)
        self.send_command(cmd)

    def pulse_relay(self, relay: int, duration: float = 0.2) -> None:
        """Pulse a relay closed for the given duration in seconds."""
        self.activate_relay(relay)
        time.sleep(duration)
        self.deactivate_relay(relay)

    def short_capa(self, duration: float = 1.0) -> None:
        """Short the CAPA test path using the configured relay."""
        self.pulse_relay(self.relay_short_capa, duration)

    def reset_switch(self, duration: float = 0.2) -> None:
        """Reset the CAPA switch by pulsing the configured relay."""
        self.pulse_relay(self.relay_reset_switch, duration)
