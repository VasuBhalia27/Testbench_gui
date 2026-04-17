"""Common utilities for the backend adapter layer.

Wraps Functional debugger operations with safe wrappers that handle a
disconnected or uninitialised debugger gracefully.  All public functions
return None / False instead of raising exceptions so that test suites can
report FAIL cleanly without crashing.
"""

from Functional import debugger as t32


def ensure_connected() -> bool:
    """Return True if the Trace32 debugger is currently connected."""
    if not t32.dbg or not hasattr(t32.dbg, 'fnc'):
        return False
    try:
        t32.dbg.fnc("Var.VALUE(TestFw_IsEcuSleeping)")
        return True
    except Exception:
        return False


def read_variable(varname: str):
    """Read a firmware variable by name.

    Returns None when the debugger is not connected or the read fails.
    """
    if not t32.dbg or not hasattr(t32.dbg, 'fnc'):
        return None
    try:
        return t32.dbg.fnc(f"Var.VALUE({varname})")
    except Exception:
        return None


def send_test_command(did: int) -> None:
    """Send a DID command to the firmware via Trace32."""
    if not t32.dbg or not hasattr(t32.dbg, 'fnc'):
        return
    try:
        t32.SendDIDGetVal_multiple_entry([], [], did)
    except Exception:
        pass


def set_variable(varname: str, value) -> None:
    """Write *value* to a firmware variable via Trace32."""
    if not t32.dbg or not hasattr(t32.dbg, 'fnc'):
        return
    try:
        t32.SendCmdToDbg(f"Var.set {varname} = {value}")
    except Exception:
        pass
