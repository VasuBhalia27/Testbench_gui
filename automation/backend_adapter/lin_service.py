"""LIN backend service — reads LIN firmware variables."""

from automation.backend_adapter.common import read_variable

_LIN_VARIABLES = [
    "TestFw_LinFrameStatus",
]


def read_lin_values(suite_id: str) -> dict:
    """Return a dict mapping each LIN variable name to its firmware value.

    Args:
        suite_id: Suite identifier (used for logging; not sent to hardware).

    Returns:
        Dict with keys matching ``_LIN_VARIABLES``; values are None when
        the debugger is not connected or the read fails.
    """
    return {var: read_variable(var) for var in _LIN_VARIABLES}
