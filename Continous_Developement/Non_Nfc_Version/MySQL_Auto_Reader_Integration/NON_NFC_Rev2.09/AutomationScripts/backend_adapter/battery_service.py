"""Battery backend service — reads battery-related firmware variables."""

from AutomationScripts.backend_adapter.common import read_variable

_BATTERY_VARIABLES = [
    "TestFw_BatRefStatus",
    "TestFw_AiBatRef",
]


def read_battery_values(suite_id: str) -> dict:
    """Return a dict mapping each battery variable name to its firmware value.

    Args:
        suite_id: Suite identifier (used for logging; not sent to hardware).

    Returns:
        Dict with keys matching ``_BATTERY_VARIABLES``; values are None when
        the debugger is not connected or the read fails.
    """
    return {var: read_variable(var) for var in _BATTERY_VARIABLES}
