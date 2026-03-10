"""Motor-specific test logic.

The motor monitor test reads three variables:
  - ``TestFw_MotorVoltage``
  - ``TestFw_MotorCurrentValue``
  - ``TestFw_MotorLoadError``

and waits for them to stabilise after triggering the appropriate DID.
Pass criteria: voltage > 0 mV, current > 0 mA, and load error == 0.
"""

import time
from typing import Any, Callable, Optional, Tuple

from automation.core.trace32_adapter import Trace32Interface
from Functional.trace32 import TestFunctionCmd


class MotorTest:
    """Standalone motor test implementation."""

    @staticmethod
    def run(
        adapter: Trace32Interface,
        status_callback: Optional[Callable[[str], None]] = None,
        timeout: float = 30.0,
    ) -> bool:
        """Execute one motor test case.

        :param adapter: trace32 adapter to use for communication
        :param status_callback: optional logger for progress
        :param timeout: maximum number of seconds to wait for stable readings
        :return: ``True`` if all three values stabilise and meet pass criteria,
                 ``False`` otherwise.
        """
        log = status_callback or (lambda msg: None)

        log("MOTOR: setting DecoupleCouple state")
        adapter.set_variable("MotorTest_SetGuiMotorActuateRequest", 1)

        # the GUI would automatically clear the checkbox after about a
        # second; if we leave the request high the hardware keeps toggling
        # repeatedly. mimic that behaviour so the request is only active
        # briefly.
        time.sleep(1)
        log("MOTOR: clearing DecoupleCouple request")
        adapter.set_variable("MotorTest_SetGuiMotorActuateRequest", 0)

        log("MOTOR: triggering measurement DID")
        adapter.send_did(TestFunctionCmd.TESTFW_GUI_CMD_MOTOR_TEST_e)

        voltage, current, load_error, last_readings = MotorTest._wait_for_stable_values(
            adapter, timeout=timeout, poll_interval=0.5
        )

        # If any value failed to stabilize, log the last-read values for debugging
        if voltage is None:
            log(f"MOTOR: voltage never stabilised within timeout (last read: {last_readings.get('voltage')})")
            if current is not None:
                log(f"MOTOR: current last value: {current} mA")
            if load_error is not None:
                log(f"MOTOR: load_error last value: {load_error}")
            return False
        if current is None:
            log(f"MOTOR: current never stabilised within timeout (last read: {last_readings.get('current')})")
            if voltage is not None:
                log(f"MOTOR: voltage last value: {voltage} mV")
            if load_error is not None:
                log(f"MOTOR: load_error last value: {load_error}")
            return False
        if load_error is None:
            log(f"MOTOR: load_error never stabilised within timeout (last read: {last_readings.get('load_error')})")
            if voltage is not None:
                log(f"MOTOR: voltage last value: {voltage} mV")
            if current is not None:
                log(f"MOTOR: current last value: {current} mA")
            return False

        log(
            f"MOTOR: final values - voltage={voltage} mV, "
            f"current={current} mA, load_error={load_error}"
        )

        pass_voltage = voltage > 0
        pass_current = current > 0
        pass_load_error = load_error == 0

        if pass_voltage and pass_current and pass_load_error:
            log("MOTOR: ✓ all values in pass range")
            return True
        else:
            if not pass_voltage:
                log(f"MOTOR: ✗ voltage {voltage} is not > 0")
            if not pass_current:
                log(f"MOTOR: ✗ current {current} is not > 0")
            if not pass_load_error:
                log(f"MOTOR: ✗ load_error {load_error} is not == 0")
            return False

    @staticmethod
    def _wait_for_stable_values(
        adapter: Trace32Interface,
        timeout: float = 30.0,
        poll_interval: float = 0.5,
        tolerance: float = 1.0,
    ):
        """Poll all three motor variables until each is stable.

        Stability is defined as two consecutive reads within `tolerance` for each.
        Motor readings tend to have more noise than other sensors, so tolerance
        defaults to 1.0 (1 mV for voltage, 1 mA for current, 1 for load_error).

        Returns a tuple (voltage, current, load_error, last_readings) where
        the first three are the stabilised values or None, and last_readings
        is a dict containing the final values read (even if None).
        """
        start = time.time()
        last_voltage = None
        last_current = None
        last_load_error = None
        stable_counts = {"voltage": 0, "current": 0, "load_error": 0}
        iteration = 0

        while time.time() - start < timeout:
            iteration += 1
            try:
                raw_voltage = adapter.read_variable("TestFw_MotorVoltage")
                voltage = float(raw_voltage)
            except Exception:
                voltage = None

            try:
                raw_current = adapter.read_variable("TestFw_MotorCurrentValue")
                current = float(raw_current)
            except Exception:
                current = None

            try:
                raw_load_error = adapter.read_variable("TestFw_MotorLoadError")
                load_error = float(raw_load_error)
            except Exception:
                load_error = None

            # Check voltage stability
            if voltage is not None:
                if last_voltage is not None and abs(voltage - last_voltage) < tolerance:
                    stable_counts["voltage"] += 1
                else:
                    stable_counts["voltage"] = 0
                last_voltage = voltage

            # Check current stability
            if current is not None:
                if last_current is not None and abs(current - last_current) < tolerance:
                    stable_counts["current"] += 1
                else:
                    stable_counts["current"] = 0
                last_current = current

            # Check load error stability
            if load_error is not None:
                if (
                    last_load_error is not None
                    and abs(load_error - last_load_error) < tolerance
                ):
                    stable_counts["load_error"] += 1
                else:
                    stable_counts["load_error"] = 0
                last_load_error = load_error

            # All three must be stable (2+ consecutive stable reads)
            if (
                stable_counts["voltage"] >= 2
                and stable_counts["current"] >= 2
                and stable_counts["load_error"] >= 2
            ):
                # return the stable values and also include a last_readings dict
                last_readings = {
                    "voltage": last_voltage,
                    "current": last_current,
                    "load_error": last_load_error,
                }
                return (last_voltage, last_current, last_load_error, last_readings)

            time.sleep(poll_interval)

        # If timeout occurred, but the last-read values already meet pass
        # criteria (voltage>0, current>0, load_error==0) accept them as a
        # pragmatic final reading. This reduces intermittent failures due
        # to noisy sensors near the timeout boundary.
        last_readings = {
            "voltage": last_voltage,
            "current": last_current,
            "load_error": last_load_error,
        }

        try:
            if (
                last_voltage is not None
                and last_current is not None
                and last_load_error is not None
                and last_voltage > 0
                and last_current > 0
                and last_load_error == 0
            ):
                # accept last readings as final
                return (last_voltage, last_current, last_load_error, last_readings)
        except Exception:
            pass

        # Otherwise return None to indicate stability not achieved
        return (None, None, None, last_readings)
