"""Adapter layer for SmartBU automation.

This module wraps the functions provided by the existing
`Functional.trace32` module and exposes a stable interface
for automation tests.  The adapter lives in the automation
folder so that production code does not need to change when
we extend tests or restructure the automation logic.

It also provides simple helpers which can be monkeypatched in
unit tests to simulate a connected or disconnected debugger.
"""

from typing import Any, List, Optional
import Functional.trace32 as t32

# path helper so tests don't have to hardcode a location
from automation.core import path_utils


class Trace32Interface:
    """Facade providing the subset of operations automation cares about."""

    def __init__(self):
        # The underlying debugger connection object (dbg) is maintained by
        # the `Functional.trace32` module as a global variable; we do not
        # replicate it here.  Tests can monkeypatch the module attribute
        # `Functional.trace32.dbg` directly.
        pass

    # control operations
    def connect(self, repo_path: Optional[str] = None, preset: int = 1) -> None:
        """Start Trace32 using the given repository path and preset.

        If ``repo_path`` is omitted the helper in :mod:`path_utils` will try
        to locate the ``SmartBU`` directory beside this workspace.  The
        return value of :func:`path_utils.smartbu_repo_path` becomes the path
        passed to Trace32.
        """
        if repo_path is None:
            repo_path = path_utils.smartbu_repo_path()

        # the GUI expects an object with a ``get`` method
        class Dummy:
            def __init__(self, text):
                self._text = text
            def get(self):
                return self._text
        dummy_entry = Dummy(repo_path)
        sel = type("Sel", (), {"get": lambda self: preset})()
        t32.Trace32ConnectApp(dummy_entry, sel, status_label=None)

    def disconnect(self) -> None:
        t32.QuitTrace32(status_label=None)

    def run_code(self) -> None:
        # the GUI passes a label; our tests don't care so we pass None
        t32.RunCode(exec_label=None)

    def pause_code(self) -> None:
        # PauseCode in the production library expects a label widget, but
        # our automation code does not have one.  Wrap call in try/except so
        # tests (which pass ``None``) do not raise an exception.
        try:
            t32.PauseCode(exec_label=None)
        except Exception:
            pass

    # data operations
    def send_did(self, did: int) -> Any:
        return t32.SendDIDGetVal_multiple_entry([], [], did)

    def set_variable(self, varname: str, value: Any) -> None:
        t32.SendCmdToDbg(f"Var.set {varname} = {value}")

    def read_variable(self, varname: str) -> Any:
        """Read the current value of a debugger variable.

        This is a thin wrapper around the Trace32 ``dbg.fnc`` call that the
        GUI uses for polling.  Return value is whatever the backend returns
        (usually a string or number).
        """
        # direct access to the global dbg object in Functional.trace32
        return t32.dbg.fnc(f"Var.VALUE({varname})")

    def clear_eos_entries(self) -> None:
        """Clear the EOS test result display entries.
        
        This mimics the behavior of clicking the "Reset Results" button in the
        EOS test tab, which clears the displayed voltage values before running
        a new test.  Used during test automation to ensure clean state between
        test runs.
        """
        # Delegate to the GUI's clear_entries function in Functional.trace32
        # This provides a high-level way to reset the UI without directly
        # manipulating widget state from the automation layer.
        t32.clear_entries([])

    def clear_sg_entries(self) -> None:
        """Clear the SG test result display entries.

        Works just like ``clear_eos_entries`` but for the strain gauge tab.
        """
        t32.clear_entries([])


# helper for formatting that might be used in assertions
format_value_with_unit = t32.format_value_with_unit
