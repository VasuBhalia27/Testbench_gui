"""Programmable DC power supply drivers (OWON + KIKUSUI).

This module supports multiple bench supplies over VISA/SCPI and exposes a
common API used by automation:

- connect()
- disconnect()
- output_on()
- output_off()
- set_voltage(volts)
- set_current(amps)

Select the supply type with environment variable ``PSU_TYPE``:

- ``kikusui`` (default)
- ``owon``

Optional explicit VISA resource env vars:

- ``OWON_PSU_RESOURCE``
- ``KIKUSUI_PSU_RESOURCE``
"""

import os
import time
from typing import Callable, Optional

import pyvisa

# Timeout in milliseconds for VISA read/write operations.
_VISA_TIMEOUT_MS = 3000

# Vendor IDs visible in VISA USB resource strings.
_OWON_VID = "0x5345"
_KIKUSUI_VID = "0x0B3E"


def _list_usb_resources() -> tuple:
    try:
        rm = pyvisa.ResourceManager()
        resources = rm.list_resources("USB?*INSTR")
        rm.close()
        return resources
    except Exception:
        return ()


def _probe_idn(resource: str) -> Optional[str]:
    inst = None
    rm = None
    try:
        rm = pyvisa.ResourceManager()
        inst = rm.open_resource(resource)
        inst.timeout = _VISA_TIMEOUT_MS
        inst.write_termination = "\n"
        inst.read_termination = "\n"
        response = inst.query("*IDN?")
        return response.strip().upper() if response else None
    except Exception:
        return None
    finally:
        try:
            if inst is not None:
                inst.close()
        except Exception:
            pass
        try:
            if rm is not None:
                rm.close()
        except Exception:
            pass


def find_owon_resource() -> Optional[str]:
    """Return first OWON VISA USB resource string, or None if not found."""
    for resource in _list_usb_resources():
        if _OWON_VID in resource.lower():
            return resource
        idn = _probe_idn(resource)
        if idn and "OWON" in idn:
            return resource
    return None


def find_kikusui_resource() -> Optional[str]:
    """Return first KIKUSUI VISA USB resource string, or None if not found."""
    for resource in _list_usb_resources():
        if _KIKUSUI_VID in resource.lower():
            return resource
        idn = _probe_idn(resource)
        if idn and ("KIKUSUI" in idn or "PWR801ML" in idn):
            return resource
    return None


class _ScpiPowerSupply:
    """Shared SCPI/VISA implementation for supported bench supplies."""

    def __init__(
        self,
        name: str,
        resource: Optional[str],
        resolver: Callable[[], Optional[str]],
        remote_cmd: str,
        local_cmd: str,
    ):
        self.name = name
        self._resource = resource
        self._resolver = resolver
        self._remote_cmd = remote_cmd
        self._local_cmd = local_cmd
        self._inst = None
        self._rm = None

    def connect(self) -> None:
        resource = self._resource or self._resolver()
        if resource is None:
            raise RuntimeError(
                f"{self.name} not found on VISA USB resources. "
                "Set resource explicitly via environment variable or constructor."
            )

        self._rm = pyvisa.ResourceManager()
        self._inst = self._rm.open_resource(resource)
        self._inst.timeout = _VISA_TIMEOUT_MS
        self._inst.write_termination = "\n"
        self._inst.read_termination = "\n"
        time.sleep(0.2)
        self._send(self._remote_cmd)

    def disconnect(self) -> None:
        if self._inst is not None:
            try:
                self._send(self._local_cmd)
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
        self._rm = None

    def output_on(self) -> None:
        self._send("OUTP ON")

    def output_off(self) -> None:
        self._send("OUTP OFF")

    def set_voltage(self, volts: float) -> None:
        self._send(f"VOLT {volts:.3f}")

    def set_current(self, amps: float) -> None:
        self._send(f"CURR {amps:.3f}")

    def _send(self, cmd: str) -> None:
        if self._inst is None:
            raise RuntimeError("Power supply not connected - call connect() first.")
        self._inst.write(cmd)
        time.sleep(0.05)


class OwonP4305(_ScpiPowerSupply):
    """OWON P4305 single-channel programmable supply."""

    def __init__(self, resource: Optional[str] = None):
        super().__init__(
            name="OWON P4305",
            resource=resource,
            resolver=find_owon_resource,
            remote_cmd=":SYST:REMOTE",
            local_cmd=":SYST:LOCAL",
        )


class KikusuiPWR801ML(_ScpiPowerSupply):
    """KIKUSUI PWR801ML programmable supply."""

    def __init__(self, resource: Optional[str] = None):
        super().__init__(
            name="KIKUSUI PWR801ML",
            resource=resource,
            resolver=find_kikusui_resource,
            remote_cmd="SYST:REM",
            local_cmd="SYST:LOC",
        )


def create_power_supply():
    """Create a PSU instance based on ``PSU_TYPE`` environment variable.

    If the requested PSU is not physically found on USB/VISA, the function
    automatically tries the other supported model before giving up.  This
    allows the test to continue even when a different supply than configured
    is connected.
    """
    psu_type = os.getenv("PSU_TYPE", "kikusui").strip().lower()

    # Build the preferred supply first, then the alternative.
    if psu_type == "kikusui":
        preferred = KikusuiPWR801ML(resource=os.getenv("KIKUSUI_PSU_RESOURCE", "").strip() or None)
        alternative = OwonP4305(resource=os.getenv("OWON_PSU_RESOURCE", "").strip() or None)
        alt_name = "OWON"
    elif psu_type == "owon":
        preferred = OwonP4305(resource=os.getenv("OWON_PSU_RESOURCE", "").strip() or None)
        alternative = KikusuiPWR801ML(resource=os.getenv("KIKUSUI_PSU_RESOURCE", "").strip() or None)
        alt_name = "KIKUSUI"
    else:
        raise ValueError(
            f"Unsupported PSU_TYPE '{psu_type}'. Use 'owon' or 'kikusui'."
        )

    # Probe preferred supply: if its USB resource is visible, return it.
    if preferred._resource or preferred._resolver() is not None:
        return preferred

    # Preferred not found — try the alternative.
    if alternative._resource or alternative._resolver() is not None:
        print(f"[PSU] {psu_type.upper()} not detected; falling back to {alt_name}.")
        return alternative

    # Neither found: return the preferred instance anyway so the caller can
    # surface a meaningful error message rather than raising here.
    print(f"[PSU] No supported power supply detected on USB. "
          f"Test will continue without PSU control.")
    return preferred
