"""Adapter layer for SmartBU automation.

This module wraps the functions provided by the existing
`Functional.trace32` module and exposes a stable interface
for automation tests.  The adapter lives in the automation
folder so that production code does not need to change when
we extend tests or restructure the automation logic.

This adapter does NOT control the PCB's on-board USB controller
(highlighted purple in the design). The on-board USB controller
is intentionally managed by the PC GUI (via `Functional.usb_relay`) and
must not be manipulated by the Trace32 debugger process.

It also provides simple helpers which can be monkeypatched in
unit tests to simulate a connected or disconnected debugger.
"""

from typing import Any, List, Optional
import Functional.trace32 as t32

# path helper so tests don't have to hardcode a location
from AutomationScripts.core import path_utils


class Trace32Interface:
    """Facade providing the subset of operations automation cares about."""

    def __init__(self):
        # The underlying debugger connection object (dbg) is maintained by
        # the `Functional.trace32` module as a global variable; we do not
        # replicate it here.  Tests can monkeypatch the module attribute
        # `Functional.trace32.dbg` directly.
        self._relay_controller = None

    # control operations
    def attach_relay_controller(self, relay_controller) -> None:
        """Attach an external relay controller for CAPA hardware operations."""
        self._relay_controller = relay_controller

    def short_capa(self, duration: float = 1.0) -> None:
        """Pulse the CAPA short relay if a controller is attached."""
        if self._relay_controller is None:
            raise RuntimeError("No relay controller attached")
        self._relay_controller.short_capa(duration)

    def reset_capa_switch(self, duration: float = 0.2) -> None:
        """Pulse the CAPA reset relay if a controller is attached."""
        if self._relay_controller is None:
            raise RuntimeError("No relay controller attached")
        self._relay_controller.reset_switch(duration)

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

        In the manual GUI this clears the Entry widgets on the EOS tab.
        In the automation layer there are no live GUI widgets, so this call
        is intentionally a no-op.  If pre-test firmware state needs resetting,
        use :meth:`set_variable` directly (e.g. ``EosTest_EosRequestGui``).
        """
        # t32.clear_entries requires a list of Tkinter Entry widgets which are
        # not available here; passing [] is a deliberate no-op.
        t32.clear_entries([])

    def clear_sg_entries(self) -> None:
        """Clear the SG test result display entries.

        Same as :meth:`clear_eos_entries` but for the Strain Gauge tab.
        In the automation layer there are no live GUI widgets, so this call
        is intentionally a no-op.  If pre-test firmware state needs resetting,
        use :meth:`set_variable` directly (e.g. ``TestFw_GetSgResults``).
        """
        t32.clear_entries([])


# helper for formatting that might be used in assertions
format_value_with_unit = t32.format_value_with_unit
