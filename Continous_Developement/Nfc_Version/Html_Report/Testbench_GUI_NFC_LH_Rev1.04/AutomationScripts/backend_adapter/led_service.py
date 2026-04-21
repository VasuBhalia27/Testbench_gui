"""LED backend service — reads LED-related firmware variables."""

from AutomationScripts.backend_adapter.common import read_variable


def read_led_voltage(test_id: str) -> dict:
    """Return a dict mapping variable name to its current firmware value.

    Args:
        test_id: Test case identifier (used for logging; not sent to hardware).

    Returns:
        ``{"TestFw_LedVoltage": <value or None>}``
    """
    return {"TestFw_LedVoltage": read_variable("TestFw_LedVoltage")}
