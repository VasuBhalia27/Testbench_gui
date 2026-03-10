"""Strain Gauge backend service — reads SG firmware variables."""

from automation.backend_adapter.common import read_variable

_SG_VARIABLES = [
    "TestFw_DoPwrSg",
    "TestFw_Sg1PlusOpamp",
    "TestFw_Sg1MinusOpamp",
    "TestFw_Sg1Opamp",
    "TestFw_Sg1Dac",
    "TestFw_Sg2PlusOpamp",
    "TestFw_Sg2MinusOpamp",
    "TestFw_Sg2Opamp",
    "TestFw_Sg2Dac",
]


def read_sg_values(suite_id: str) -> dict:
    """Return a dict mapping each SG variable name to its firmware value.

    Args:
        suite_id: Suite identifier (used for logging; not sent to hardware).

    Returns:
        Dict with keys matching ``_SG_VARIABLES``; values are None when
        the debugger is not connected or the read fails.
    """
    return {var: read_variable(var) for var in _SG_VARIABLES}
