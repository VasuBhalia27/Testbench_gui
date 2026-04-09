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

- ``owon`` (default)
- ``kikusui``

Optional explicit VISA resource env vars:

- ``OWON_PSU_RESOURCE``
- ``KIKUSUI_PSU_RESOURCE``

KIKUSUI auto-detection supports multiple models (for example PWR401L,
PWR801ML) and scans USB/TCPIP/ASRL VISA resources.
"""

import os
import re
import time
from typing import Callable, Optional

import pyvisa

# Timeout in milliseconds for VISA read/write operations.
_VISA_TIMEOUT_MS = 3000

# Vendor IDs visible in VISA USB resource strings.
_OWON_VID = "0x5345"
_KIKUSUI_VID = "0x0B3E"


def _list_candidate_resources() -> tuple:
    try:
        rm = pyvisa.ResourceManager()
        patterns = (
            "USB?*INSTR",
            "TCPIP?*INSTR",
            "ASRL?*INSTR",
        )
        merged = []
        for pattern in patterns:
            try:
                merged.extend(rm.list_resources(pattern))
            except Exception:
                pass
        # Preserve order while removing duplicates.
        resources = tuple(dict.fromkeys(merged))
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
    for resource in _list_candidate_resources():
        if _OWON_VID in resource.lower():
            return resource
        idn = _probe_idn(resource)
        if idn and "OWON" in idn:
            return resource
    return None


def find_kikusui_resource() -> Optional[str]:
    """Return first KIKUSUI VISA USB resource string, or None if not found."""
    for resource in _list_candidate_resources():
        if _KIKUSUI_VID in resource.lower():
            return resource
        idn = _probe_idn(resource)
        # Support multiple KIKUSUI PWR models (e.g., PWR401L, PWR801ML).
        if idn and (
            "KIKUSUI" in idn
            or re.search(r"\bPWR\d+[A-Z0-9]*\b", idn) is not None
        ):
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
            detected = ", ".join(_list_candidate_resources()) or "none"
            raise RuntimeError(
                f"{self.name} not found on VISA resources. "
                f"Detected VISA resources: {detected}. "
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


class KikusuiPWR(_ScpiPowerSupply):
    """KIKUSUI PWR-series programmable supply (for example PWR401L/PWR801ML)."""

    def __init__(self, resource: Optional[str] = None):
        super().__init__(
            name="KIKUSUI PWR",
            resource=resource,
            resolver=find_kikusui_resource,
            remote_cmd="SYST:REM",
            local_cmd="SYST:LOC",
        )


# Backward-compatible alias for older imports.
KikusuiPWR401L = KikusuiPWR


def create_power_supply():
    """Create a PSU instance based on ``PSU_TYPE`` environment variable."""
    psu_type = os.getenv("PSU_TYPE", "owon").strip().lower()

    if psu_type == "kikusui":
        resource = os.getenv("KIKUSUI_PSU_RESOURCE", "").strip() or None
        return KikusuiPWR(resource=resource)

    if psu_type == "owon":
        resource = os.getenv("OWON_PSU_RESOURCE", "").strip() or None
        return OwonP4305(resource=resource)

    raise ValueError(
        f"Unsupported PSU_TYPE '{psu_type}'. Use 'owon' or 'kikusui'."
    )
