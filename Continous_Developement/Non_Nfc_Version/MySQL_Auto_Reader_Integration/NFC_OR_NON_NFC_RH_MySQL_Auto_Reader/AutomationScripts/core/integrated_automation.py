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
        self._automation_lock = threading.Lock()  # prevents race-condition double-start
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
        with self._automation_lock:
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

            # Capture the 2D scan code entered by the operator before the run starts
            scan_code = getattr(self.gui, "scan_code", None)
            scan_code = scan_code.get().strip() if scan_code is not None else ""
            if scan_code:
                self._log(f"2D Scan Code: {scan_code}")
            else:
                self._log("2D Scan Code: (not entered)")

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

            # On subsequent runs a new PCB has been inserted into the fixture.
            # The SWD probe loses its link to the old board; Trace32 then crashes
            # when trying SYStem.Up on the new board — exactly the failure that
            # forces testers to unplug/replug the debugger USB cable.
            # Fix: shut Trace32 down cleanly (SYStem.Down + QUIT + taskkill +
            # 4 s USB-driver release window) so the probe fully resets.
            # verify_setup then sees dbg='' and does a full relaunch automatically —
            # the software equivalent of replugging the debugger cable.
            if not self.is_first_run:
                self._log("New PCB in fixture — restarting Trace32 for clean probe connection...")
                try:
                    t32.QuitTrace32(status_label=None)
                except Exception:
                    pass

            # Hardware setup verification
            verifier = hardware_setup.HardwareSetupVerifier(
                status_callback=self._log,
                gui_root=self.gui.root,
            )
            # After QuitTrace32, dbg is '' so already_connected is False and
            # verify_setup will perform a full Trace32 relaunch.
            # On first run, dbg may already be set from a manual connect.
            already_connected = bool(getattr(t32, 'dbg', None))
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
                self.adapter,
                status_callback=self._log,
                power_cycle_callback=self._motor_ocp_recovery,
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

            # Generate HTML test report from the actual hardware measurements.
            # pcb_count is the sequential number for this PCB (1-based).
            # gui.pass_count + gui.fail_count = total runs BEFORE this one
            # (set_result_indicator hasn't fired yet on the main thread).
            pcb_count = self.gui.pass_count + self.gui.fail_count + 1
            try:
                from AutomationScripts.report_generator import generate_report, results_from_run
                report_path = generate_report(
                    run_results=results,
                    pcb_count=pcb_count,
                    all_passed=all_passed,
                    scan_code=scan_code,
                )
                self._log(f"HTML Report saved: {report_path}")
                # Sync GUI counters to match the HTML report exactly
                try:
                    results_by_sheet = results_from_run(results)
                    rpt_pass = sum(
                        1 for rows in results_by_sheet.values()
                        for r in rows if (r.get("Status") or "").upper().strip() == "PASS"
                    )
                    rpt_fail = sum(
                        1 for rows in results_by_sheet.values()
                        for r in rows if (r.get("Status") or "").upper().strip() == "FAIL"
                    )
                    self.gui.root.after(0, lambda p=rpt_pass, f=rpt_fail: self.gui.update_test_item_counts(p, f))
                except Exception:
                    pass
            except Exception as _exc:
                self._log(f"⚠ Report generation failed: {_exc}")
            # Insert overall result into MySQL database
            try:
                from AutomationScripts.mysql_logger import insert_test_result
                from datetime import datetime
                insert_test_result(
                    model=scan_code if scan_code else "UNKNOWN",
                    scan_code=scan_code if scan_code else "UNKNOWN",
                    all_passed=all_passed,
                    timestamp=datetime.now(),
                )
                self._log("MySQL: test result inserted into database.")
            except ImportError as _db_imp:
                self._log(f"\u26a0 MySQL: {_db_imp}")
            except Exception as _db_exc:
                self._log(f"\u26a0 MySQL insert failed: {_db_exc}")
            # Close the T32 debugger automatically after report is saved
            try:
                self._log("Closing debugger...")
                t32.QuitTrace32(status_label=None)
                self._log("Debugger closed.")
            except Exception as _e:
                self._log(f"Note: Debugger close: {_e}")

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

    def _motor_ocp_recovery(self) -> None:
        """Recover from PSU over-current protection triggered by the motor test.

        Turns the supply OFF to reset the OCP latch, then powers back ON and
        restarts the target firmware so that subsequent tests can continue.
        """
        self._log("MOTOR OCP: turning supply OFF to clear over-current protection...")
        self.power_off_supply()
        self._log("MOTOR OCP: waiting 3 seconds for PSU to reset...")
        time.sleep(3)
        self._log("MOTOR OCP: turning supply ON...")
        self.power_on_supply()
        self._log("MOTOR OCP: waiting 4 seconds for supply and PCB to stabilise...")
        time.sleep(4)
        self._log("MOTOR OCP: resetting target (SYStem.Up)...")
        try:
            t32.ResetTarget(status_label=None)
            self._log("MOTOR OCP: target reset complete")
            time.sleep(1)
            t32.RunCode(exec_label=None)
            self._log("MOTOR OCP: code execution started")
            self._log("MOTOR OCP: waiting 5 seconds for firmware to initialise...")
            time.sleep(5)
        except Exception as _e:
            self._log(f"MOTOR OCP: recovery reset failed — {_e}")

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
        pass_count = 0
        fail_count = 0
        for name, result in results.items():
            if isinstance(result, dict):
                passed = bool(result.get('pass', False))
            else:
                passed = bool(result)

            icon   = "\u2705" if passed else "\u274c"
            status = "PASS" if passed else "FAIL"
            self._log(f"  {icon} {name}: {status}")

            if passed:
                pass_count += 1
            else:
                fail_count += 1
                all_passed = False

        # Update the GUI counters with individual test item counts
        self.gui.root.after(0, lambda p=pass_count, f=fail_count: self.gui.update_test_item_counts(p, f))

        return all_passed
