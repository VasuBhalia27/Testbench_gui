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

from automation.core.trace32_adapter import Trace32Interface

# individual sequence modules
from automation.core.led_test import LedTest
from automation.core.bat_test import BatTest
from automation.core.motor_test import MotorTest
from automation.core.eos_test import EosTest
from automation.core.sg_test import SgTest
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
    """

    def __init__(
        self,
        adapter: Trace32Interface,
        status_callback: Optional[Callable[[str], None]] = None,
    ):
        self.adapter = adapter
        self._log = status_callback or (lambda msg: None)

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

    def run_motor_test(self, timeout: float = 2.0) -> bool:
        """Run the motor test sequence using ``MotorTest``."""
        return MotorTest.run(
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
        # the LED tests run in both variants
        results['led_on'] = self.run_led_test(on=True)
        results['led_off'] = self.run_led_test(on=False)

        # battery test should always run immediately after LEDs
        results['battery'] = self.run_battery_test()

        # motor test should always run immediately after battery
        results['motor'] = self.run_motor_test()

        # EOS test should always run immediately after motor (both reset and set cases)
        eos_results = self.run_eos_test()
        results['eos_reset'] = eos_results['eos_reset']
        results['eos_set'] = eos_results['eos_set']

        # Strain gauge (SG) tests follow EOS.  They are split into two cases
        # corresponding to the two bridges on the board; each returns its own
        # pass/fail dictionary so that the runner and GUI can report them
        # individually.
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
