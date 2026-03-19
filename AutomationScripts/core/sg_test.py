"""Strain gauge (SG) automation tests for SmartBU hardware.

This module implements two related test cases which mirror the behaviour of
clicking the "Sg Results" checkbox in the GUI and reading a set of voltage
values until they stabilise.

The automation sequence is:

1. Trigger the SG results DID.
2. Wait 5 seconds for the hardware to perform the measurement.
3. Poll seven variables repeatedly until each has produced two identical
   consecutive readings (stability).
4. Evaluate pass/fail for the first and second SG groups using the
   documented voltage ranges.

The results dictionary returned by ``run()`` contains two entries, ``'sg1'``
and ``'sg2'``, each of which is itself a dictionary containing a ``'pass'``
boolean along with the measured voltages.
"""

import time
from typing import Callable, Dict, List, Optional, Tuple

from Functional.trace32 import TestFunctionCmd
from AutomationScripts.core.timing_profile import TIMING


class SgTest:
    """Automation logic for the two SG test cases.

    The variables we monitor are:
        - TestFw_DoPwrSg            (used by the GUI but not evaluated for pass)
        - TestFw_Sg1PlusOpamp
        - TestFw_Sg1MinusOpamp
        - TestFw_Sg1Opamp
        - TestFw_Sg2PlusOpamp
        - TestFw_Sg2MinusOpamp
        - TestFw_Sg2Opamp
    """

    # pass ranges
    SG_PLUS_MINUS_MIN = 1600
    SG_PLUS_MINUS_MAX = 4100
    SG_OPAMP_MIN = 200
    SG_OPAMP_MAX = 4600

    VARIABLES = [
        "TestFw_DoPwrSg",
        "TestFw_Sg1PlusOpamp",
        "TestFw_Sg1MinusOpamp",
        "TestFw_Sg1Opamp",
        "TestFw_Sg2PlusOpamp",
        "TestFw_Sg2MinusOpamp",
        "TestFw_Sg2Opamp",
    ]

    def __init__(
        self, adapter, status_callback: Optional[Callable[[str], None]] = None
    ):
        self.adapter = adapter
        self.log = status_callback or (lambda msg: None)

    def run(self) -> Dict[str, Dict[str, float]]:
        """Execute both SG test cases.

        Returns:
            A dictionary with keys ``'sg1'`` and ``'sg2'``; each value is itself
            a dict containing measured voltages and the overall ``'pass'`` flag.
        """
        results: Dict[str, Dict[str, float]] = {}
        results["sg1"] = self.run_sg1()
        results["sg2"] = self.run_sg2()
        return results

    def run_sg1(self) -> Dict[str, float]:
        """First SG group evaluation (plus/minus/opamp)."""
        # clear any existing displayed values
        self.log("SG1: clearing entry field")
        try:
            self.adapter.clear_sg_entries()
        except AttributeError:
            pass

        # mimic GUI: set TestFw_GetSgResults = 1 to tell firmware to generate data
        self.log("SG1: requesting firmware to update SG results")
        self.adapter.set_variable("TestFw_GetSgResults", 1)

        self.log("SG1: triggering results DID")
        self.adapter.send_did(TestFunctionCmd.TEST_GUI_CMD_SG_TEST_e)

        self.log(f"SG1: waiting {TIMING.sg1_measure_wait:.1f} seconds for measurement")
        time.sleep(TIMING.sg1_measure_wait)

        # send DID again before polling in case the firmware uses the DID to
        # latch values into variables (GUI reads immediately after raising flag)
        self.log("SG1: triggering measurement DID")
        self.adapter.send_did(TestFunctionCmd.TEST_GUI_CMD_SG_TEST_e)

        readings = self._wait_for_stable_variables(self.VARIABLES)

        plus = readings.get("TestFw_Sg1PlusOpamp")
        minus = readings.get("TestFw_Sg1MinusOpamp")
        opamp = readings.get("TestFw_Sg1Opamp")

        pass_plus = plus is not None and self.SG_PLUS_MINUS_MIN <= plus <= self.SG_PLUS_MINUS_MAX
        pass_minus = minus is not None and self.SG_PLUS_MINUS_MIN <= minus <= self.SG_PLUS_MINUS_MAX
        pass_opamp = opamp is not None and self.SG_OPAMP_MIN <= opamp <= self.SG_OPAMP_MAX
        pass_status = pass_plus and pass_minus and pass_opamp

        self.log(f"SG1: final values - plus={plus}, minus={minus}, opamp={opamp}")
        if pass_status:
            self.log("SG1: ✓ all values in pass range")
        else:
            # Always log individual status for each value (pass or fail)
            if pass_plus:
                self.log(f"SG1: ✓ plus value {plus} in range ({self.SG_PLUS_MINUS_MIN}-{self.SG_PLUS_MINUS_MAX})")
            else:
                self.log(f"SG1: ✗ plus value {plus} out of range ({self.SG_PLUS_MINUS_MIN}-{self.SG_PLUS_MINUS_MAX})")
            if pass_minus:
                self.log(f"SG1: ✓ minus value {minus} in range ({self.SG_PLUS_MINUS_MIN}-{self.SG_PLUS_MINUS_MAX})")
            else:
                self.log(f"SG1: ✗ minus value {minus} out of range ({self.SG_PLUS_MINUS_MIN}-{self.SG_PLUS_MINUS_MAX})")
            if pass_opamp:
                self.log(f"SG1: ✓ opamp value {opamp} in range ({self.SG_OPAMP_MIN}-{self.SG_OPAMP_MAX})")
            else:
                self.log(f"SG1: ✗ opamp value {opamp} out of range ({self.SG_OPAMP_MIN}-{self.SG_OPAMP_MAX})")

        result = {
            "pass": pass_status,
            "plus": plus,
            "minus": minus,
            "opamp": opamp,
        }
        result.update(readings)  # include all seven readings for completeness
        return result

    def run_sg2(self) -> Dict[str, float]:
        """Second SG group evaluation (plus/minus/opamp)."""
        # Reset firmware flag before clearing to ensure clean state
        self.log("SG2: resetting measurement flag")
        self.adapter.set_variable("TestFw_GetSgResults", 0)
        
        # Wait for flag to take effect
        time.sleep(TIMING.sg2_flag_wait)
        
        # clear any existing displayed values (may have been left by SG1)
        self.log("SG2: clearing entry field")
        try:
            self.adapter.clear_sg_entries()
        except AttributeError:
            pass

        # manual GUI workflow inserts a 2‑second pause after hitting "Reset Results".
        # The firmware may need time to digest the clearing, so mimic that behaviour
        # before proceeding with the next measurement.
        self.log(f"SG2: waiting {TIMING.sg2_reset_wait:.1f} seconds after reset")
        time.sleep(TIMING.sg2_reset_wait)

        self.log("SG2: requesting firmware to update SG results")
        self.adapter.set_variable("TestFw_GetSgResults", 1)

        self.log("SG2: triggering results DID")
        self.adapter.send_did(TestFunctionCmd.TEST_GUI_CMD_SG_TEST_e)

        self.log(f"SG2: waiting {TIMING.sg2_measure_wait:.1f} seconds for measurement")
        time.sleep(TIMING.sg2_measure_wait)

        self.log("SG2: triggering measurement DID")
        self.adapter.send_did(TestFunctionCmd.TEST_GUI_CMD_SG_TEST_e)

        readings = self._wait_for_stable_variables(self.VARIABLES)

        plus = readings.get("TestFw_Sg2PlusOpamp")
        minus = readings.get("TestFw_Sg2MinusOpamp")
        opamp = readings.get("TestFw_Sg2Opamp")

        pass_plus = plus is not None and self.SG_PLUS_MINUS_MIN <= plus <= self.SG_PLUS_MINUS_MAX
        pass_minus = minus is not None and self.SG_PLUS_MINUS_MIN <= minus <= self.SG_PLUS_MINUS_MAX
        pass_opamp = opamp is not None and self.SG_OPAMP_MIN <= opamp <= self.SG_OPAMP_MAX
        pass_status = pass_plus and pass_minus and pass_opamp

        self.log(f"SG2: final values - plus={plus}, minus={minus}, opamp={opamp}")
        if pass_status:
            self.log("SG2: ✓ all values in pass range")
        else:
            # Always log individual status for each value (pass or fail)
            if pass_plus:
                self.log(f"SG2: ✓ plus value {plus} in range ({self.SG_PLUS_MINUS_MIN}-{self.SG_PLUS_MINUS_MAX})")
            else:
                self.log(f"SG2: ✗ plus value {plus} out of range ({self.SG_PLUS_MINUS_MIN}-{self.SG_PLUS_MINUS_MAX})")
            if pass_minus:
                self.log(f"SG2: ✓ minus value {minus} in range ({self.SG_PLUS_MINUS_MIN}-{self.SG_PLUS_MINUS_MAX})")
            else:
                self.log(f"SG2: ✗ minus value {minus} out of range ({self.SG_PLUS_MINUS_MIN}-{self.SG_PLUS_MINUS_MAX})")
            if pass_opamp:
                self.log(f"SG2: ✓ opamp value {opamp} in range ({self.SG_OPAMP_MIN}-{self.SG_OPAMP_MAX})")
            else:
                self.log(f"SG2: ✗ opamp value {opamp} out of range ({self.SG_OPAMP_MIN}-{self.SG_OPAMP_MAX})")

        result = {
            "pass": pass_status,
            "plus": plus,
            "minus": minus,
            "opamp": opamp,
        }
        result.update(readings)
        return result

    def _wait_for_stable_variables(
        self,
        variables: List[str],
        timeout: float = 2.0,
        poll_interval: float = TIMING.stable_poll_interval,
    ) -> Dict[str, Optional[float]]:
        """Poll multiple variables until each produces two identical reads.

        Returns a dictionary mapping variable names to their last observed value.
        If timeout elapses before all variables stabilise, the last observed
        values (which may be ``None``) are returned anyway.
        """
        start = time.time()
        last: Dict[str, Optional[float]] = {var: None for var in variables}
        stable_counts: Dict[str, int] = {var: 0 for var in variables}
        readings: Dict[str, Optional[float]] = {var: None for var in variables}

        while time.time() - start < timeout:
            for var in variables:
                try:
                    raw = self.adapter.read_variable(var)
                    val = float(raw)
                except Exception:
                    val = None

                readings[var] = val
                if val is not None:
                    if last[var] is not None and abs(val - last[var]) < 1e-3:
                        stable_counts[var] += 1
                    else:
                        stable_counts[var] = 0
                    last[var] = val

            if all(stable_counts[var] >= 2 for var in variables):
                return readings

            time.sleep(poll_interval)

        return readings
