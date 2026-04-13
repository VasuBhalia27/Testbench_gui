"""Test execution logic for SmartBU automation.

This module encapsulates the detailed sequences that the automation
framework will perform on the target hardware.  Each function here should
mirror the behaviour of a human operator clicking checkboxes/buttons
in the ``gui_main`` application.

At the moment we only implement the LED test; further routines will be
added later as the automation coverage expands.
"""

import time
from typing import Callable, Optional

from AutomationScripts.core.trace32_adapter import Trace32Interface

# individual sequence modules
from AutomationScripts.core.led_test import LedTest
from AutomationScripts.core.bat_test import BatTest
from AutomationScripts.core.motor_test import MotorTest
from AutomationScripts.core.eos_test import EosTest
from AutomationScripts.core.sg_test import SgTest
from AutomationScripts.core.capa_test import CapaTest
from AutomationScripts.core.timing_profile import TIMING
from Functional.trace32 import TestFunctionCmd


class TestSequenceError(Exception):
    """Raised when a sequence cannot complete successfully."""
    pass


class TestSequenceRunner:
    """Top level helper that knows how to run individual tests.

    :param adapter: an instance of :class:`Trace32Interface` that will be
                    used to communicate with the debugger.
    :param status_callback: optional callable for progress messages.
                            Receives a single string argument.
    :param power_cycle_callback: optional callable that performs a full PSU
                                 power cycle + target reset + Go.  Called
                                 before CAPA tests to de-saturate the
                                 capacitive sensor circuit.
    """

    def __init__(
        self,
        adapter: Trace32Interface,
        status_callback: Optional[Callable[[str], None]] = None,
        power_cycle_callback: Optional[Callable[[], None]] = None,
    ):
        self.adapter = adapter
        self._log = status_callback or (lambda msg: None)
        self._power_cycle = power_cycle_callback or (lambda: None)

    # ---- LED ----------------------------------------------------------------

    def run_led_test(self, on: bool, timeout: float = 3.0) -> bool:
        """Proxy to :class:`LedTest` which lives in a dedicated module.

        Keeping the implementation in its own file simplifies debugging
        when the LED logic fails; the test module can be executed in
        isolation and developers know exactly where to look.
        """
        return LedTest.run(
            adapter=self.adapter,
            on=on,
            status_callback=self._log,
            timeout=timeout,
        )

    # add stubs for future tests so the runner API is clear
    def run_battery_test(self, timeout: float = 2.0) -> bool:
        """Run the battery monitor sequence using ``BatTest``."""
        return BatTest.run(
            adapter=self.adapter,
            status_callback=self._log,
            timeout=timeout,
        )

    def run_battery_test_with_voltage(self, timeout: float = 2.0):
        """Run the battery monitor sequence and return ``(passed, voltage_mV)``."""
        return BatTest.run_with_voltage(
            adapter=self.adapter,
            status_callback=self._log,
            timeout=timeout,
        )

    def run_motor_test(self, timeout: float = 2.0) -> bool:
        """Run the motor test sequence using ``MotorTest``."""
        return MotorTest.run(
            adapter=self.adapter,
            status_callback=self._log,
            timeout=timeout,
        )

    def run_led_test_with_voltage(self, on: bool, timeout: float = 3.0) -> tuple:
        """Proxy to :meth:`LedTest.run_with_voltage`; returns ``(passed, voltage_mV)``."""
        return LedTest.run_with_voltage(
            adapter=self.adapter,
            on=on,
            status_callback=self._log,
            timeout=timeout,
        )

    def run_motor_test_with_values(self, timeout: float = 2.0) -> tuple:
        """Run the motor test and return ``(passed, voltage_mV, current_mA, load_error)``."""
        return MotorTest.run_with_values(
            adapter=self.adapter,
            status_callback=self._log,
            timeout=timeout,
        )

    def run_eos_test(self) -> dict:
        """Run the EOS test sequence (both Reset and Set cases).
        
        Returns a dict with keys 'eos_reset' and 'eos_set', each containing
        {'pass': bool, 'voltage': float, 'min': float, 'max': float}
        """
        eos = EosTest(self.adapter, status_callback=self._log)
        return eos.run()

    # ... further test methods will be added later

    def run_sg_test(self) -> dict:
        """Run the strain gauge sequence (both SG1 and SG2 cases).

        Returns a dict with keys ``'sg1'`` and ``'sg2'`` mirroring the return
        value of :class:`SgTest.run`.
        """
        sg = SgTest(self.adapter, status_callback=self._log)
        return sg.run()

    def run_capa_test(self) -> dict:
        """Run the capacitive sensor sequence (TC_CAPA_01 and TC_CAPA_02).

        Returns a dict with keys ``'capa1'`` and ``'capa2'``
        mirroring the return value of :class:`CapaTest.run`.
        capa1 requires physical sensor touch; it will fail in fully
        automated runs.
        """
        capa = CapaTest(self.adapter, status_callback=self._log)
        return capa.run()

    # ------------------------------------------------------------------
    def run_for_variant(self, variant: int) -> dict:
        """Execute all applicable tests for the selected variant.

        The returned dictionary maps a logical test name to a boolean
        indicating pass/fail.  Note that some tests (currently EOS) return a
        more detailed dictionary containing the measured voltage and the
        explicit ``'pass'`` flag; callers should guard accordingly (see
        :class:`IntegratedAutomationRunner` which handles both formats).
        Currently only the LED tests are implemented;
        other keys will be added as the automation coverage expands.

        :param variant: 1 for non‑NFC, 2 for NFC
        """
        results = {}

        # --- Battery voltage check (runs first) ----------------------------
        # A reading of 0.0 mV means the supply has not yet stabilised.
        # In that case there is no point running further tests; all hardware
        # functions depend on a healthy supply voltage.
        bat_passed, bat_voltage = self.run_battery_test_with_voltage()
        results['battery'] = {'pass': bat_passed, 'voltage': bat_voltage}

        if bat_voltage == 0.0:
            self._log(
                "BAT: 0.0 mV — ADC not ready yet, waiting "
                f"{TIMING.bat_retry_wait:.1f} s and retrying..."
            )
            time.sleep(TIMING.bat_retry_wait)
            bat_passed, bat_voltage = self.run_battery_test_with_voltage(timeout=2.0)
            results['battery'] = {'pass': bat_passed, 'voltage': bat_voltage}

        if bat_voltage == 0.0:
            self._log(
                "BAT: \u2717 voltage is 0.0 mV \u2014 supply has not yet stabilised.\n"
                "     Please wait for the voltage to stabilise and try again."
            )
            return results

        # CAPA tests run immediately after battery (before other tests so that
        # the capacitive sensors are measured while nothing else is active).
        capa_results = self.run_capa_test()
        results['capa1'] = capa_results['capa1']
        results['capa2'] = capa_results['capa2']

        # the LED tests run in both variants
        led_on_passed, led_on_v   = self.run_led_test_with_voltage(on=True)
        led_off_passed, led_off_v = self.run_led_test_with_voltage(on=False)
        results['led_on']  = {'pass': led_on_passed,  'voltage': led_on_v}
        results['led_off'] = {'pass': led_off_passed, 'voltage': led_off_v}

        # motor test
        mot_passed, mot_v, mot_i, mot_e = self.run_motor_test_with_values()
        results['motor'] = {'pass': mot_passed, 'voltage': mot_v,
                            'current': mot_i, 'load_error': mot_e}

        # EOS test (both reset and set cases)
        eos_results = self.run_eos_test()
        results['eos_reset'] = eos_results['eos_reset']
        results['eos_set'] = eos_results['eos_set']

        # Strain gauge (SG) tests follow EOS.
        sg_results = self.run_sg_test()
        results['sg1'] = sg_results['sg1']
        results['sg2'] = sg_results['sg2']

        # placeholder logic for other tests; vary by variant
        if variant == 2:
            # NFC test: trigger the NFC DID and check whether a card is detected.
            self._log("NFC: sending test command")
            self.adapter.send_did(TestFunctionCmd.TEST_GUI_CMD_NFC_TEST_e)
            time.sleep(2)
            try:
                nfc_val = self.adapter.read_variable("TestFw_IsNfcDetectedCard")
                results['nfc'] = (nfc_val is not None and int(float(str(nfc_val))) == 1)
            except Exception:
                results['nfc'] = False
                self._log("NFC: variable read failed")

            # CAN test: trigger the CAN DID and verify frames were transferred.
            self._log("CAN: sending test command")
            self.adapter.send_did(TestFunctionCmd.TEST_GUI_CMD_CAN_TEST_e)
            time.sleep(2)
            try:
                can_val = self.adapter.read_variable("DummyBytes")
                results['can'] = (can_val is not None and float(str(can_val)) > 0)
            except Exception:
                results['can'] = False
                self._log("CAN: variable read failed")

        # the remaining tests will eventually be added here
        return results
