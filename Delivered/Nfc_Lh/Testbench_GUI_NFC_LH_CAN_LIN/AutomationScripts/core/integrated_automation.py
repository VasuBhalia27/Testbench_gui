"""Integrated automation orchestration for gui_main TAB 1.

This module coordinates the full automation workflow when embedded in the
main GUI, handling tab locking/unlocking and reset logic for multiple runs.
"""

import threading
import time
import os
from typing import Callable, Optional

from AutomationScripts.core import hardware_setup, test_sequences, trace32_adapter
from AutomationScripts.core.timing_profile import TIMING
from Functional import trace32 as t32
try:
    from Functional.power_supply import create_power_supply
    _PSU_AVAILABLE = True
except ImportError:
    create_power_supply = None
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
        self.psu = None  # power supply instance
        self.consecutive_bat_zero_count = 0  # tracks successive 0.0 mV battery failures
        self._canlin_event = threading.Event()  # set by GUI when user selects CAN/LIN after hw init

    def start_automation(self, variant: int, canlin_enabled: int = 0) -> None:
        """
        Start the automation sequence in a background thread.

        :param variant: 1 for Non-NFC, 2 for NFC
        :param canlin_enabled: unused — kept for API compatibility; the actual
                               CAN/LIN selection is collected from the user
                               after hardware initialisation completes.
        """
        if self.is_running:
            return

        self.is_running = True
        self._canlin_event.clear()
        thread = threading.Thread(target=self._run_automation_thread, args=(variant,))
        thread.daemon = True
        thread.start()

    def _run_automation_thread(self, variant: int) -> None:
        """Background thread that orchestrates the full automation."""
        try:
            self._log("Starting automation sequence...")

            psu_automation_enabled = self._is_psu_automation_enabled()

            if psu_automation_enabled:
                # Power cycle the external supply: OFF first, then ON.
                # This guarantees a clean start regardless of the supply's previous state.
                self._log("Power cycling supply: turning OFF...")
                self.power_off_supply()
                self._log(f"Supply OFF — waiting {TIMING.supply_off_wait:.1f} seconds...")
                time.sleep(TIMING.supply_off_wait)
                self._log("Powering supply ON...")
                self.power_on_supply()
                self._log(
                    f"Supply ON — waiting {TIMING.supply_on_wait:.1f} seconds for voltage to stabilise..."
                )
                time.sleep(TIMING.supply_on_wait)
            else:
                self._log("PSU automation disabled — skipping automated power OFF/ON sequence")

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
                self.gui.root.after(0, lambda: self.gui.set_result_indicator(False))
                self.is_running = False
                self.unlock_tabs()
                self.gui.root.after(0, self.gui.reset_for_new_run)
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
                self._log(
                    "Waiting "
                    f"{TIMING.first_run_fw_init_wait:.1f} seconds for firmware peripheral initialisation..."
                )
                time.sleep(TIMING.first_run_fw_init_wait)

            # Initialize adapter once on first run, then reuse for all subsequent runs
            if self.adapter is None:
                self.adapter = trace32_adapter.Trace32Interface()

            # Prompt the user to select CAN/LIN setting now that hardware is
            # fully initialised and Trace32 is connected.
            self._canlin_event.clear()
            self.gui.root.after(0, self.gui.prompt_canlin_selection)
            self._log("Waiting for CAN/LIN selection...")
            selected_in_time = self._canlin_event.wait(timeout=120)
            if not selected_in_time:
                self._log("⚠ CAN/LIN selection timed out (120 s) — defaulting to CAN/LIN OFF")

            # Read the value chosen by the user (already applied by _sync_canlin)
            canlin_enabled = self.gui.canlin_enabled.get()
            can_dep_value = 0 if canlin_enabled == 1 else 1
            canlin_label = "ON" if canlin_enabled == 1 else "OFF"
            self._log(f"CAN/LIN confirmed: TestFw_GuiCanDependencyDisable = {can_dep_value} (CAN/LIN {canlin_label})")
            self.adapter.set_variable("TestFw_GuiCanDependencyDisable", can_dep_value)

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
                self._log("Remove PCB and insert the next PCB to test.")
            else:
                self._log("\n✗ Some tests failed - review results above")

            self.gui.root.after(0, lambda: self.gui.set_result_indicator(all_passed))

            # Generate Excel test report from the actual hardware measurements.
            try:
                from AutomationScripts.report_generator import generate_report
                report_path = generate_report(run_results=results)
                self._log(f"Report saved: {report_path}")
            except Exception as _exc:
                self._log(f"⚠ Report generation failed: {_exc}")

            self.is_first_run = False

        except Exception as e:
            self._log(f"\n✗ AUTOMATION ERROR: {e}")
            self.gui.root.after(0, lambda: self.gui.set_result_indicator(False))
        finally:
            # Turn the power supply OFF after every run (pass or fail) so the
            # PCB is de-energised before the operator removes it from the fixture.
            if self._is_psu_automation_enabled():
                self._log("Turning power supply OFF to safe the PCB...")
                self.power_off_supply()
            else:
                self._log("PSU automation disabled — skipping automated power OFF")
            self._log("\nAutomation complete. Click 'Start' to run again.")
            self.is_running = False
            self.unlock_tabs()
            self.gui.root.after(0, self.gui.reset_for_new_run)

    def _log(self, message: str) -> None:
        """Log a message to the GUI status area."""
        self.gui.append_status(message)

    def _capa_power_cycle(self) -> None:
        """Power-cycle the supply and reset the target before CAPA tests.

        The capacitive sensor circuit can saturate during a run.  Cutting
        power and restarting the firmware clears the saturation so that the
        CAPA measurements are valid.  Extended settle times are required for
        the unlock sensor to fully de-saturate.
        """
        self._log("CAPA pre-cycle: turning supply OFF...")
        self.power_off_supply()
        self._log("CAPA pre-cycle: waiting 5 seconds for capacitors to discharge...")
        time.sleep(5)
        self._log("CAPA pre-cycle: turning supply ON...")
        self.power_on_supply()
        self._log("CAPA pre-cycle: waiting 5 seconds for supply to stabilise...")
        time.sleep(5)
        self._log("CAPA pre-cycle: resetting target...")
        try:
            t32.ResetTarget(status_label=None)
            self._log("CAPA pre-cycle: target reset complete")
            time.sleep(1)
            t32.RunCode(exec_label=None)
            self._log("CAPA pre-cycle: code execution started")
            self._log("CAPA pre-cycle: waiting 10 seconds for firmware and sensors to initialise...")
            time.sleep(10)
        except Exception as e:
            self._log(f"CAPA pre-cycle: reset failed — {e}")

    def power_on_supply(self) -> None:
        """Connect to configured PSU backend and enable output."""
        if not self._is_psu_automation_enabled():
            return
        if not _PSU_AVAILABLE:
            self._log("⚠ PSU: required library missing (pyvisa) — skipping power-on")
            return
        try:
            if self.psu is None:
                self.psu = create_power_supply()
                self.psu.connect()
            self.psu.output_on()
            self._log("PSU: output ON")
        except Exception as e:
            self._log(f"⚠ PSU power-on failed: {e}")

    def power_off_supply(self) -> None:
        """Disable configured PSU output and close the connection."""
        if not self._is_psu_automation_enabled():
            return
        if not _PSU_AVAILABLE:
            return
        try:
            if self.psu is None:
                self.psu = create_power_supply()
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

    def _is_psu_automation_enabled(self) -> bool:
        """Read PSU automation toggle from environment (default: enabled)."""
        raw = os.getenv("PSU_AUTOMATION", "1").strip().lower()
        return raw not in ("0", "false", "off", "no")

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

            icon   = "✓" if passed else "✗"
            status = "PASS" if passed else "FAIL"
            self._log(f"  {icon} {name}: {status}")

            if not passed:
                all_passed = False

        return all_passed
