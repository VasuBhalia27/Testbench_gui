"""NFC backend service — reads NFC firmware variables."""

from AutomationScripts.backend_adapter.common import read_variable

_NFC_VARIABLES = [
    "TestFw_IsNfcDetectedCard",
]


def read_nfc_values(suite_id: str) -> dict:
    """Return a dict mapping each NFC variable name to its firmware value.

    Args:
        suite_id: Suite identifier (used for logging; not sent to hardware).

    Returns:
        Dict with keys matching ``_NFC_VARIABLES``; values are None when
        the debugger is not connected or the read fails.
    """
    return {var: read_variable(var) for var in _NFC_VARIABLES}
