"""
Battery backend adapter
"""
from .common import read_variable


def read_battery_values(test_id: str) -> dict:
    """Return battery-related variables.
    Uses `TestFw_AiBatRef` as the primary output (converted from mV to V).
    Firmware provides battery voltage in mV (via DM_GetUBatt__mV__U16()).
    This adapter converts to V for consistency with executor validation.
    """
    val = read_variable("TestFw_AiBatRef")
    # Convert mV to V (firmware provides in mV)
    if val is not None:
        val = val / 1000.0
    return {"TestFw_AiBatRef": (float(val) if val is not None else None)}
