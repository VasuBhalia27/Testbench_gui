"""Capacitive Sensor backend service — reads Capa firmware variables."""

from automation.backend_adapter.common import read_variable

_CAPA_VARIABLES = [
    "TestFw_CapaApproach",
    "TestFw_CapaLock",
    "TestFw_CapaUnlock",
    "TestFw_CapaApproachSensorValue",
    "TestFw_CapaLockSensorValue",
    "TestFw_CapaUnlockSensorValue",
]


def read_capa_values(suite_id: str) -> dict:
    """Return a dict mapping each Capa variable name to its firmware value.

    Args:
        suite_id: Suite identifier (used for logging; not sent to hardware).

    Returns:
        Dict with keys matching ``_CAPA_VARIABLES``; values are None when
        the debugger is not connected or the read fails.
    """
    return {var: read_variable(var) for var in _CAPA_VARIABLES}
