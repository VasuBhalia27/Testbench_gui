"""Motor backend service — reads motor-related firmware variables."""

from automation.backend_adapter.common import read_variable

_MOTOR_VARIABLES = [
    "TestFw_MotorCoupledVoltage",
    "TestFw_MotorDecoupledVoltage",
    "TestFw_MotorCurrentValue",
    "TestFw_MotorLoadError",
]


def read_motor_values(suite_id: str) -> dict:
    """Return a dict mapping each motor variable name to its firmware value.

    Args:
        suite_id: Suite identifier (used for logging; not sent to hardware).

    Returns:
        Dict with keys matching ``_MOTOR_VARIABLES``; values are None when
        the debugger is not connected or the read fails.
    """
    return {var: read_variable(var) for var in _MOTOR_VARIABLES}
