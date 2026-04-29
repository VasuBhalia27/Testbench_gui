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
import Functional.trace32 as t32
from AutomationScripts.core import path_utils
from AutomationScripts.core.timing_profile import TIMING


class HardwareSetupVerificationError(Exception):
    """Raised when hardware setup fails."""
    pass


class HardwareSetupVerifier:
    """Orchestrates automated hardware setup and verification."""

    def __init__(self, status_callback: Optional[Callable[[str], None]] = None, gui_root=None):
        """
        Initialize the verifier.

        :param status_callback: Optional callable to report progress.
                                Receives messages like "Connecting to Trace32..."
        :param gui_root: tkinter root window — used to bring the GUI back to
                         the front after the Trace32 debugger window appears.
        """
        self.status_callback = status_callback or (lambda msg: None)
        self.repo_path = path_utils.smartbu_repo_path()
        self.gui_root = gui_root

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

        # Bring the GUI window back to the front now that the T32 window has appeared
        if self.gui_root is not None:
            def _lift():
                try:
                    self.gui_root.attributes("-topmost", True)
                    self.gui_root.lift()
                    self.gui_root.focus_force()
                    self.gui_root.after(800, lambda: self.gui_root.attributes("-topmost", False))
                except Exception:
                    pass
            self.gui_root.after(0, _lift)

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
        _lockup_reset_done = False
        start = time.time()
        while time.time() - start < timeout:
            # --- Cortex-M0+ lockup detection ---------------------------------
            # When the PSoC4 boots into "running (locked up)" state (ARM lockup
            # caused by a HardFault-on-HardFault or a reset glitch on PCB swap),
            # TestFw_IsEcuSleeping is never updated and the poll times out.
            # Detect the lockup via STATE.RUN() and recover with SYStem.Up once.
            try:
                run_state = str(t32.dbg.fnc("STATE.RUN()")).lower()
                if "locked" in run_state:
                    if not _lockup_reset_done:
                        self._log(
                            "WARNING: target is in 'running (locked up)' state "
                            "(ARM Cortex-M0+ lockup detected). "
                            "Issuing SYStem.Up to perform hardware MCU reset..."
                        )
                        try:
                            t32.dbg.cmd("SYStem.Up")
                        except Exception:
                            pass
                        time.sleep(2.0)   # wait for MCU power-on reset to complete
                        try:
                            t32.dbg.cmd("Go")
                        except Exception:
                            pass
                        _lockup_reset_done = True
                        start = time.time()  # reset verification timeout after recovery
                        time.sleep(0.5)
                        continue
                    else:
                        raise HardwareSetupVerificationError(
                            "Target remains in 'running (locked up)' state after "
                            "SYStem.Up recovery — check PCB power and SWD connection"
                        )
            except HardwareSetupVerificationError:
                raise
            except Exception:
                pass
            # -----------------------------------------------------------------
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
        max_attempts = 2
        _skip = skip_connect  # local copy so we can change it per-attempt
        for attempt in range(1, max_attempts + 1):
            try:
                # Only connect (re-launch T32) when _skip is False.
                # IMPORTANT: on a timeout retry we do NOT re-launch T32.
                # Killing and restarting t32marm.exe requires a 2–5 s USB driver
                # release delay; if that delay is too short, ConnectToTraceUDP
                # fails with "Connection to Trace32 Failed".
                # The lockup recovery (SYStem.Up) inside run_code_and_verify()
                # handles the target reset without touching the T32 process.
                if not _skip:
                    self.connect_trace32(preset)
                self.run_code_and_verify()
                self._log("Hardware setup verified successfully!")
                return True
            except HardwareSetupVerificationError as e:
                err_str = str(e)
                is_timeout = "Timeout" in err_str or "timed out" in err_str.lower()
                if attempt < max_attempts:
                    if is_timeout:
                        self._log(
                            f"Hardware setup attempt {attempt} timed out — "
                            "target did not reach running state. Retrying once..."
                        )
                        # Keep the existing T32 session — do NOT re-launch.
                        _skip = True
                    else:
                        self._log(
                            f"Hardware setup attempt {attempt} failed: {e} — retrying once..."
                        )
                        # Connection-level failure: allow T32 re-launch on retry.
                        _skip = False
                else:
                    self._log(f"Hardware setup failed after {max_attempts} attempts: {e}")
                    if is_timeout:
                        self._log(
                            "Timeout hint: If this happens consistently, check:\n"
                            "  1) PCB power and hardware connections\n"
                            "  2) Debugger cable (USB/JTAG) and Trace32 connection\n"
                            "  3) ELF/firmware file — ensure it matches the flashed software\n"
                            "  If it only happens occasionally it is likely a transient "
                            "hardware issue — click Start to retry."
                        )
                    return False
