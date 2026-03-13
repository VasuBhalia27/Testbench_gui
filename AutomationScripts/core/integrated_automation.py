"""Integrated automation orchestration for gui_main TAB 1.

This module coordinates the full automation workflow when embedded in the
main GUI, handling tab locking/unlocking and reset logic for multiple runs.
"""

import threading
import time
from typing import Callable, Optional

from AutomationScripts.core import hardware_setup, test_sequences, trace32_adapter
from Functional import trace32 as t32
try:
    from Functional.power_supply import OwonP4305
    _PSU_AVAILABLE = True
except ImportError:
    OwonP4305 = None
    _PSU_AVAILABLE = False


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
        self.psu: OwonP4305 = None  # power supply instance
        self.consecutive_bat_zero_count = 0  # tracks successive 0.0 mV battery failures

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

            # Power cycle the external supply: OFF first, then ON.
            # This guarantees a clean start regardless of the supply's previous state.
            self._log("Power cycling supply: turning OFF...")
            self.power_off_supply()
            self._log("Supply OFF — waiting 2 seconds...")
            time.sleep(2)
            self._log("Powering supply ON...")
            self.power_on_supply()
            self._log("Supply ON — waiting 2 seconds for voltage to stabilise...")
            time.sleep(2)

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

            # On the very first power-on debug session the firmware sets
            # TestFw_IsEcuSleeping = 0 early in its startup routine, but the
            # peripheral hardware (ADCs, sensors, CAN/LIN buses) needs several
            # more seconds to complete initialisation.  Subsequent runs already
            # have this extra time because of the ResetTarget + Go + 2 s settle
            # in the non-first-run path.  Adding an equivalent delay here makes
            # the first run behave consistently with all further runs.
            if self.is_first_run:
                self._log("Waiting 10 seconds for firmware peripheral initialisation...")
                time.sleep(10)

            # Initialize adapter once on first run, then reuse for all subsequent runs
            if self.adapter is None:
                self.adapter = trace32_adapter.Trace32Interface()
            
            runner = test_sequences.TestSequenceRunner(
                self.adapter, status_callback=self._log
            )

            self._log("\nExecuting functional test sequence...")
            results = runner.run_for_variant(variant)

            # Detect the 0.0 mV early-stop condition: run_for_variant returns
            # only {'battery': False} when voltage is 0.0 mV.
            bat_zero_stop = (list(results.keys()) == ['battery'] and not results.get('battery', True))

            if bat_zero_stop:
                self.consecutive_bat_zero_count += 1
                self._log(
                    f"BAT: zero-voltage failure count: {self.consecutive_bat_zero_count}/2"
                )
                if self.consecutive_bat_zero_count >= 2:
                    self._log(
                        "\n⚠ Battery voltage is 0.0 mV on 2 consecutive runs.\n"
                        "   Please close the application and restart it,\n"
                        "   then allow more time for the supply to stabilise."
                    )
                    self.consecutive_bat_zero_count = 0
                    self.gui.root.after(0, self.gui.show_restart_warning)
            else:
                self.consecutive_bat_zero_count = 0

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

    def power_on_supply(self) -> None:
        """Connect to the OWON P4305 and enable its output."""
        if not _PSU_AVAILABLE:
            self._log("⚠ PSU: pyserial not installed — skipping power-on")
            return
        try:
            if self.psu is None:
                self.psu = OwonP4305()
                self.psu.connect()
            self.psu.output_on()
            self._log("PSU: output ON")
        except Exception as e:
            self._log(f"⚠ PSU power-on failed: {e}")

    def power_off_supply(self) -> None:
        """Disable the OWON P4305 output and close the connection."""
        if not _PSU_AVAILABLE:
            return
        try:
            if self.psu is None:
                self.psu = OwonP4305()
                self.psu.connect()
            self.psu.output_off()
            self._log("PSU: output OFF")
        except Exception as e:
            self._log(f"⚠ PSU output-off failed: {e}")
        try:
            if self.psu is not None:
                self.psu.disconnect()
        except Exception:
            pass
        self.psu = None

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
