"""CAN backend service — reads CAN firmware variables."""

from automation.backend_adapter.common import read_variable

_CAN_VARIABLES = [
    "DummyBytes",
]


def read_can_values(suite_id: str) -> dict:
    """Return a dict mapping each CAN variable name to its firmware value.

    Args:
        suite_id: Suite identifier (used for logging; not sent to hardware).

    Returns:
        Dict with keys matching ``_CAN_VARIABLES``; values are None when
        the debugger is not connected or the read fails.
    """
    return {var: read_variable(var) for var in _CAN_VARIABLES}
