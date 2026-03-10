"""EOS backend service — reads EOS diagnostic firmware variables."""

from automation.backend_adapter.common import read_variable

_EOS_VARIABLES = [
    "TestFw_EosDiagVoltage",
    "TestFw_EosPinState",
    "TestFw_EosErrorsWithLow",
    "TestFw_EosErrorsWithHigh",
]


def read_eos_values(suite_id: str) -> dict:
    """Return a dict mapping each EOS variable name to its firmware value.

    Args:
        suite_id: Suite identifier (used for logging; not sent to hardware).

    Returns:
        Dict with keys matching ``_EOS_VARIABLES``; values are None when
        the debugger is not connected or the read fails.
    """
    return {var: read_variable(var) for var in _EOS_VARIABLES}
