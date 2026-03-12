"""CAPA (Capacitive Sensor) automation tests for SmartBU hardware.

Follows the same pattern as sg_test.py — polls variables directly via the
adapter until they stabilise, then evaluates against documented pass/fail ranges.

The automation sequence for each test case is:

1. Trigger the CAPA DID to request a firmware measurement.
2. Wait for variables to stabilise using repeated polling (like SG).
3. Evaluate pass/fail against the documented acceptance criteria.

Acceptance Criteria:

TC_CAPA_01 (Unlock Sensor Active — requires physical touch on sensor):
  - TestFw_CapaUnlockSensorValue: 9120-9200
  - TestFw_CapaUnlock:            1
  - TestFw_CapaApproach:          1
  - TestFw_CapaLock:              1

TC_CAPA_02 (Unlock Sensor Inactive — resting state, always runs in automation):
  - TestFw_CapaUnlockSensorValue: <= 9120
  - TestFw_CapaUnlock:            0
  - TestFw_CapaApproach:          0
  - TestFw_CapaLock:              0

NOTE: TC_CAPA_01 requires physical interaction (touching the capacitive sensor).
It will FAIL in fully automated runs unless a mechanical actuator is present.
"""

import time
from typing import Callable, Dict, List, Optional

from Functional.trace32 import TestFunctionCmd


class CapaTest:
    """Automation logic for the two CAPA test cases."""

    VARIABLES = [
        "TestFw_CapaApproach",
        "TestFw_CapaLock",
        "TestFw_CapaUnlock",
        "TestFw_CapaApproachSensorValue",
        "TestFw_CapaLockSensorValue",
        "TestFw_CapaUnlockSensorValue",
    ]

    # TC_CAPA_01 pass criteria
    UNLOCK_SENSOR_MIN = 9120
    UNLOCK_SENSOR_MAX = 9200

    def __init__(
        self, adapter, status_callback: Optional[Callable[[str], None]] = None
    ):
        self.adapter = adapter
        self.log = status_callback or (lambda msg: None)

    def run(self) -> Dict[str, Dict]:
        """Execute both CAPA test cases sequentially.

        Returns:
            A dictionary with keys ``'tc_capa_01'`` and ``'tc_capa_02'``;
            each value contains the test result with a ``'pass'`` flag and
            the measured values.
        """
        results: Dict[str, Dict] = {}
        results["tc_capa_01"] = self.run_tc_capa_01()
        results["tc_capa_02"] = self.run_tc_capa_02()
        return results

    def run_tc_capa_01(self) -> Dict:
        """TC_CAPA_01: CAPA Unlock Active State.

        NOTE: Requires physical touch on capacitive sensor. Will fail in
        automated runs without physical interaction.
        """
        self.log("CAPA1: triggering measurement DID")
        self.adapter.send_did(TestFunctionCmd.TEST_GUI_CMD_CAPA_TEST_e)

        self.log("CAPA1: waiting 2 seconds for measurement")
        time.sleep(2)

        readings = self._wait_for_stable_variables(self.VARIABLES)

        approach = readings.get("TestFw_CapaApproach")
        lock     = readings.get("TestFw_CapaLock")
        unlock   = readings.get("TestFw_CapaUnlock")
        unlock_sensor = readings.get("TestFw_CapaUnlockSensorValue")

        pass_sensor  = unlock_sensor is not None and self.UNLOCK_SENSOR_MIN <= unlock_sensor <= self.UNLOCK_SENSOR_MAX
        pass_unlock  = unlock  is not None and unlock  == 1.0
        pass_approach= approach is not None and approach == 1.0
        pass_lock    = lock    is not None and lock    == 1.0
        pass_status  = pass_sensor and pass_unlock and pass_approach and pass_lock

        self.log(
            f"CAPA1: sensor={unlock_sensor}, unlock={unlock}, "
            f"approach={approach}, lock={lock}"
        )
        if pass_status:
            self.log("CAPA1: ✓ all values in pass range")
        else:
            if not pass_sensor:
                self.log(f"CAPA1: ✗ unlock sensor {unlock_sensor} out of range ({self.UNLOCK_SENSOR_MIN}-{self.UNLOCK_SENSOR_MAX})")
            if not pass_unlock:
                self.log(f"CAPA1: ✗ CapaUnlock {unlock} expected 1")
            if not pass_approach:
                self.log(f"CAPA1: ✗ CapaApproach {approach} expected 1")
            if not pass_lock:
                self.log(f"CAPA1: ✗ CapaLock {lock} expected 1")

        result = {"pass": pass_status}
        result.update(readings)
        return result

    def run_tc_capa_02(self) -> Dict:
        """TC_CAPA_02: CAPA Unlock Inactive State (resting/default)."""
        self.log("CAPA2: triggering measurement DID")
        self.adapter.send_did(TestFunctionCmd.TEST_GUI_CMD_CAPA_TEST_e)

        self.log("CAPA2: waiting 2 seconds for measurement")
        time.sleep(2)

        readings = self._wait_for_stable_variables(self.VARIABLES)

        approach = readings.get("TestFw_CapaApproach")
        lock     = readings.get("TestFw_CapaLock")
        unlock   = readings.get("TestFw_CapaUnlock")
        unlock_sensor = readings.get("TestFw_CapaUnlockSensorValue")

        pass_sensor  = unlock_sensor is not None and unlock_sensor <= self.UNLOCK_SENSOR_MIN
        pass_unlock  = unlock  is not None and unlock  == 0.0
        pass_approach= approach is not None and approach == 0.0
        pass_lock    = lock    is not None and lock    == 0.0
        pass_status  = pass_sensor and pass_unlock and pass_approach and pass_lock

        self.log(
            f"CAPA2: sensor={unlock_sensor}, unlock={unlock}, "
            f"approach={approach}, lock={lock}"
        )
        if pass_status:
            self.log("CAPA2: ✓ all values in pass range")
        else:
            if not pass_sensor:
                self.log(f"CAPA2: ✗ unlock sensor {unlock_sensor} expected <= {self.UNLOCK_SENSOR_MIN}")
            if not pass_unlock:
                self.log(f"CAPA2: ✗ CapaUnlock {unlock} expected 0")
            if not pass_approach:
                self.log(f"CAPA2: ✗ CapaApproach {approach} expected 0")
            if not pass_lock:
                self.log(f"CAPA2: ✗ CapaLock {lock} expected 0")

        result = {"pass": pass_status}
        result.update(readings)
        return result

    def _wait_for_stable_variables(
        self, variables: List[str], timeout: float = 2.0, poll_interval: float = 0.5
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
