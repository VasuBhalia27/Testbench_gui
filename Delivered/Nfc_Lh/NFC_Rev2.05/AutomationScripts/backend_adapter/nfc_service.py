"""NFC backend service — reads NFC firmware variables."""

from AutomationScripts.backend_adapter.common import read_variable

_NFC_VARIABLES = [
    "TestFw_IsNfcDetectedCard",
]

# SPI diagnostic variables for the NFC self-test (no antenna or card required)
_NFC_SPI_DIAG_VARIABLES = [
    "TestFw_NfcSpiError",
    "TestFw_NfcHwVersion",
    "TestFw_NfcRomVersion",
    "TestFw_NfcFwVersion",
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


def read_nfc_spi_diag_values(suite_id: str) -> dict:
    """Read NFC SPI diagnostic variables (no antenna or card required).

    Uses the dedicated SPI self-test path (TEST_GUI_CMD_NFC_SPI_DIAG_e).
    Returns SPI error flag and transceiver version registers so callers can
    verify the SPI link is healthy without needing an NFC antenna or card.

    Args:
        suite_id: Suite identifier (used for logging).

    Returns:
        Dict with keys matching ``_NFC_SPI_DIAG_VARIABLES``; values are None
        when the debugger is not connected or the read fails.
    """
    return {var: read_variable(var) for var in _NFC_SPI_DIAG_VARIABLES}
