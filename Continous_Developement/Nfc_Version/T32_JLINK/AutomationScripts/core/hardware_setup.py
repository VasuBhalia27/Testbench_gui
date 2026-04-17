"""Hardware setup verification workflow.

This module orchestrates the automated hardware setup process:
1. Connect to Trace32 with the chosen variant
2. Wait for "stopped at breakpoint" status
3. Wait 1 second
4. Run the code ("Go")
5. Verify "running" status is reached

The workflow is invisible to the user (no buttons shown in automation GUI);
status is reported via callbacks.
"""

import time
from typing import Callable, Optional
from Functional import debugger as t32
from AutomationScripts.core import path_utils
from AutomationScripts.core.timing_profile import TIMING


class HardwareSetupVerificationError(Exception):
    """Raised when hardware setup fails."""
    pass


class HardwareSetupVerifier:
    """Orchestrates automated hardware setup and verification."""

    def __init__(self, status_callback: Optional[Callable[[str], None]] = None):
        """
        Initialize the verifier.

        :param status_callback: Optional callable to report progress.
                                Receives messages like "Connecting to Trace32..."
        """
        self.status_callback = status_callback or (lambda msg: None)
        self.repo_path = path_utils.smartbu_repo_path()

    def _log(self, message: str) -> None:
        """Log a status message via callback."""
        self.status_callback(message)

    def connect_trace32(self, preset: int, timeout: float = 30.0) -> None:
        """
        Connect to Trace32 and wait for "stopped at breakpoint" status.

        :param preset: 1 = Non-NFC, 2 = NFC
        :param timeout: max seconds to wait for breakpoint status
        :raises HardwareSetupVerificationError: if connection fails or timeout
        """
        self._log("Connecting to Trace32...")

        # Create a dummy entry object to mimic GUI
        class DummyEntry:
            def __init__(self, path):
                self._path = path
            def get(self):
                return self._path

        dummy_sel = type("Sel", (), {"get": lambda self: preset})()
        dummy_entry = DummyEntry(self.repo_path)

        try:
            t32.Trace32ConnectApp(dummy_entry, dummy_sel, status_label=None)
        except Exception as e:
            # Best-effort cleanup so the next Start attempt is not blocked by
            # a half-started or hung PowerView process.
            try:
                t32.QuitTrace32(status_label=None)
            except Exception:
                pass
            raise HardwareSetupVerificationError(f"Failed to launch Trace32: {e}")

        self._log("Waiting for breakpoint...")
        start = time.time()
        while time.time() - start < timeout:
            if t32.dbg and hasattr(t32.dbg, 'fnc'):
                # poll a simple variable to confirm connection is alive
                try:
                    t32.dbg.fnc("Var.VALUE(TestFw_IsEcuSleeping)")
                    self._log("Connected: stopped at breakpoint")
                    return
                except Exception:
                    pass
            time.sleep(0.5)

        # Timeout usually means PowerView did not fully start/respond.
        # Force cleanup so End/next Start can recover quickly.
        try:
            t32.QuitTrace32(status_label=None)
        except Exception:
            pass
        raise HardwareSetupVerificationError("Timeout waiting for Trace32 breakpoint")

    def run_code_and_verify(self, timeout: float = 10.0) -> None:
        """
        Wait 1 second, then start code execution and verify "running" status.

        :param timeout: max seconds to wait for running status
        :raises HardwareSetupVerificationError: if verification fails
        """
        self._log(f"Waiting {TIMING.before_go_wait:.1f} seconds before Go...")
        time.sleep(TIMING.before_go_wait)

        self._log("Executing Go command...")
        try:
            t32.RunCode(exec_label=None)
        except Exception as e:
            raise HardwareSetupVerificationError(f"Failed to run code: {e}")

        self._log("Verifying running status...")
        start = time.time()
        while time.time() - start < timeout:
            try:
                # Poll the sleeping flag.  The ECU must be AWAKE (value == 0)
                # before we declare the setup verified.  Accepting any response
                # without checking the value would allow a sleeping ECU to pass.
                status = t32.dbg.fnc("Var.VALUE(TestFw_IsEcuSleeping)")
                if status is not None and int(float(str(status))) == 0:
                    self._log("Running: target is executing (TestFw_IsEcuSleeping = 0)")
                    return
            except Exception:
                pass
            time.sleep(0.5)

        raise HardwareSetupVerificationError("Timeout verifying running status")

    def verify_setup(self, preset: int, skip_connect: bool = False) -> bool:
        """
        Perform complete hardware setup verification.

        :param preset: 1 = Non-NFC, 2 = NFC
        :param skip_connect: if True, skip Trace32 connection (reuse existing connection)
                            Used for subsequent runs to avoid redundant connection setup.
        :return: True if fully verified, False otherwise
        """
        try:
            # Only connect on first run; reuse connection for subsequent runs
            if not skip_connect:
                self.connect_trace32(preset)
            self.run_code_and_verify()
            self._log("Hardware setup verified successfully!")
            return True
        except HardwareSetupVerificationError as e:
            self._log(f"Hardware setup failed: {e}")
            return False
