"""OWON P4305 programmable DC power supply driver.

The P4305 connects to the PC via USB and enumerates as a USB Test and
Measurement Device (USBTMC / IVI class) - visible in Device Manager under
"USB Test and Measurement Devices".  It does NOT appear as a COM port.

Communication: PyVISA (USBTMC transport), SCPI text commands.

Supported commands used here:
  :SYST:REMOTE   - take the supply out of local (front-panel) mode
  :SYST:LOCAL    - return control to the front panel
  OUT ON / OUT OFF - enable / disable the output
  VOLT <V>       - set output voltage  (e.g. "VOLT 12.000")
  CURR <A>       - set current limit   (e.g. "CURR 2.000")
  *IDN?          - identification query used during auto-detection

Auto-detection:
  find_owon_resource() lists all VISA USB resources and returns the first
  whose *IDN? response contains an OWON-related keyword.
  Pass an explicit VISA resource string (e.g.
  "USB0::0x5345::0x1234::P4305::INSTR") to the constructor to bypass
  auto-detection.

Usage example::

    from Functional.power_supply import OwonP4305

    psu = OwonP4305()          # auto-detect via USBTMC
    psu.connect()
    psu.set_voltage(12.0)
    psu.set_current(2.0)
    psu.output_on()
    ...
    psu.output_off()
    psu.disconnect()

    # or as a context manager:
    with OwonP4305() as psu:
        psu.set_voltage(12.0)
        psu.set_current(2.0)
        psu.output_on()
"""

import time
from typing import Optional

import pyvisa

# Timeout in milliseconds for VISA read/write operations
_VISA_TIMEOUT_MS = 3000

# OWON USB Vendor ID (0x5345).  The P4305 does not respond to *IDN? so we
# match directly on the VID embedded in the VISA resource string, e.g.
# "USB0::0x5345::0x1235::24150974::INSTR".
_OWON_VID = "0x5345"


def find_owon_resource() -> Optional[str]:
    """Scan all VISA USB resources and return the first OWON device found.

    Matches by OWON's USB Vendor ID (0x5345) embedded in the resource string.
    The OWON P4305 does not respond to *IDN? so no query is performed.

    Returns the VISA resource string (e.g.
    ``"USB0::0x5345::0x1235::24150974::INSTR"``) or ``None`` if no OWON
    device is connected.
    """
    try:
        rm = pyvisa.ResourceManager()
        resources = rm.list_resources("USB?*INSTR")
    except Exception:
        return None

    for resource in resources:
        if _OWON_VID.lower() in resource.lower():
            return resource

    return None


class OwonP4305:
    """Driver for the OWON P4305 single-channel programmable DC supply.

    :param resource: explicit VISA resource string
                     (e.g. ``"USB0::0x5345::0x1234::P4305::INSTR"``).
                     If ``None``, :func:`find_owon_resource` is used to
                     auto-detect via USBTMC.
    """

    def __init__(self, resource: Optional[str] = None):
        self._resource = resource
        self._inst: Optional[pyvisa.resources.Resource] = None
        self._rm:   Optional[pyvisa.ResourceManager]    = None

    # ------------------------------------------------------------------
    # Connection management
    # ------------------------------------------------------------------

    def connect(self) -> None:
        """Open the VISA connection and switch the supply to remote mode."""
        resource = self._resource or find_owon_resource()
        if resource is None:
            raise RuntimeError(
                "OWON P4305 not found on any USBTMC/USB resource.\n"
                "Check that the USB cable is connected and the device appears\n"
                "under 'USB Test and Measurement Devices' in Device Manager.\n"
                "Alternatively pass the resource string explicitly:\n"
                "  OwonP4305(resource='USB0::0x5345::0x1234::P4305::INSTR')"
            )
        self._rm   = pyvisa.ResourceManager()
        self._inst = self._rm.open_resource(resource)
        self._inst.timeout = _VISA_TIMEOUT_MS
        self._inst.write_termination = '\n'
        self._inst.read_termination  = '\n'
        time.sleep(0.2)   # allow the USBTMC driver to settle
        self._send(":SYST:REMOTE")

    def disconnect(self) -> None:
        """Return the supply to local (front-panel) mode and close the connection."""
        if self._inst is not None:
            try:
                self._send(":SYST:LOCAL")
            except Exception:
                pass
            try:
                self._inst.close()
            except Exception:
                pass
        if self._rm is not None:
            try:
                self._rm.close()
            except Exception:
                pass
        self._inst = None
        self._rm   = None

    # ------------------------------------------------------------------
    # Output control
    # ------------------------------------------------------------------

    def output_on(self) -> None:
        """Enable the DC output."""
        self._send("OUTP ON")

    def output_off(self) -> None:
        """Disable the DC output."""
        self._send("OUTP OFF")

    # ------------------------------------------------------------------
    # Parameter setting
    # ------------------------------------------------------------------

    def set_voltage(self, volts: float) -> None:
        """Set the output voltage in Volts."""
        self._send(f"VOLT {volts:.3f}")

    def set_current(self, amps: float) -> None:
        """Set the current limit in Amps."""
        self._send(f"CURR {amps:.3f}")

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _send(self, cmd: str) -> None:
        """Write a SCPI command string via VISA."""
        if self._inst is None:
            raise RuntimeError("Power supply not connected - call connect() first.")
        self._inst.write(cmd)
        time.sleep(0.05)   # brief pause so the supply can process the command

    # ------------------------------------------------------------------
    # Context manager support
    # ------------------------------------------------------------------

    def __enter__(self) -> "OwonP4305":
        self.connect()
        return self

    def __exit__(self, *_) -> None:
        self.disconnect()
