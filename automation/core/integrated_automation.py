"""Integrated automation orchestration for gui_main TAB 1.

This module coordinates the full automation workflow when embedded in the
main GUI, handling tab locking/unlocking and reset logic for multiple runs.
"""

import threading
import time
from typing import Callable, Optional

from automation.core import hardware_setup, test_sequences, trace32_adapter
from Functional import trace32 as t32


class IntegratedAutomationRunner:
    """Handles automation workflow integrated with gui_main."""

    def __init__(
        self,
        gui_automation,
        lock_tabs_callback: Callable[[], None],
        unlock_tabs_callback: Callable[[], None],
    ):
        """
        Initialize the runner.

        :param gui_automation: the AutomationGUI instance
        :param lock_tabs_callback: function to disable other tabs
        :param unlock_tabs_callback: function to enable other tabs
        """
        self.gui = gui_automation
        self.lock_tabs = lock_tabs_callback
        self.unlock_tabs = unlock_tabs_callback
        self.is_first_run = True
        self.is_running = False
        self.adapter = None  # Trace32 adapter persists across runs

    def start_automation(self, variant: int) -> None:
        """
        Start the automation sequence in a background thread.

        :param variant: 1 for Non-NFC, 2 for NFC
        """
        if self.is_running:
            return

        self.is_running = True
        thread = threading.Thread(target=self._run_automation_thread, args=(variant,))
        thread.daemon = True
        thread.start()

    def _run_automation_thread(self, variant: int) -> None:
        """Background thread that orchestrates the full automation."""
        try:
            self._log("Starting automation sequence...")

            # If not first run, reset target and go before hardware setup
            if not self.is_first_run:
                self._log("\nResetting target from previous run...")
                try:
                    t32.ResetTarget(status_label=None)
                    self._log("Target reset complete")
                    time.sleep(1)
                except Exception as e:
                    self._log(f"⚠ Reset target failed: {e}")

                self._log("Running code (Go)...")
                try:
                    t32.RunCode(exec_label=None)
                    self._log("Code execution started")
                    time.sleep(2)  # give it time to settle
                except Exception as e:
                    self._log(f"⚠ Go command failed: {e}")

            # Hardware setup verification
            verifier = hardware_setup.HardwareSetupVerifier(
                status_callback=self._log
            )
            # determine whether a Trace32 connection already exists (persisted from previous run or manual connect)
            already_connected = bool(getattr(t32, 'dbg', None))
            if already_connected:
                self._log("Using existing Trace32 connection")
            else:
                self._log("No Trace32 connection detected; will connect now")
            success = verifier.verify_setup(variant, skip_connect=already_connected)

            if not success:
                self._log("\n✗ HARDWARE SETUP FAILED")
                self.is_running = False
                self.unlock_tabs()
                self.gui.reset_for_new_run()
                return

            self._log("\n✓ HARDWARE SETUP COMPLETE")

            # Initialize adapter once on first run, then reuse for all subsequent runs
            if self.adapter is None:
                self.adapter = trace32_adapter.Trace32Interface()
            
            runner = test_sequences.TestSequenceRunner(
                self.adapter, status_callback=self._log
            )

            self._log("\nExecuting functional test sequence...")
            results = runner.run_for_variant(variant)

            # Log results; helper covers both simple booleans and nested dict
            # results.  The return value indicates overall pass status.
            all_passed = self._log_results(results)

            if all_passed:
                self._log("\n✓✓ ALL TESTS PASSED ✓✓")
            else:
                self._log("\n✗ Some tests failed - review results above")

            self.is_first_run = False

        except Exception as e:
            self._log(f"\n✗ AUTOMATION ERROR: {e}")
        finally:
            self._log("\nAutomation complete. Click 'Start' to run again.")
            self.is_running = False
            self.unlock_tabs()
            self.gui.reset_for_new_run()

    def _log(self, message: str) -> None:
        """Log a message to the GUI status area."""
        self.gui.append_status(message)

    def _log_results(self, results: dict) -> bool:
        """Log results dictionary and return overall pass/fail.

        The ``results`` mapping may contain plain boolean values or more
        detailed dictionaries that include a ``'pass'`` key.  This helper
        handles both formats so that callers (such as ``_run_automation_thread``)
        don't need to duplicate the logic.  The GUI logging is performed via
        :meth:`_log` and the method returns ``True`` only if every individual
        test reported a passing status.
        """
        all_passed = True
        for name, result in results.items():
            if isinstance(result, dict):
                passed = bool(result.get('pass', False))
            else:
                passed = bool(result)

            status = "PASS" if passed else "FAIL"
            self._log(f"  {name}: {status}")

            if not passed:
                all_passed = False

        return all_passed
