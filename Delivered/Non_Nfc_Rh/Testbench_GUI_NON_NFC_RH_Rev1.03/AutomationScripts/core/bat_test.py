"""Battery-specific test logic.

The battery monitor test reads the ``TestFw_AiBatRef`` variable and waits
for it to stabilise after triggering the appropriate DID.  A stable voltage
in the range 8000-16000 mV is considered a pass.
"""

import time
from typing import Any, Callable, Optional

from AutomationScripts.core.trace32_adapter import Trace32Interface
from AutomationScripts.core.timing_profile import TIMING
from Functional.trace32 import TestFunctionCmd


class BatTest:
    """Standalone battery monitor test implementation."""

    @staticmethod
    def run(
        adapter: Trace32Interface,
        status_callback: Optional[Callable[[str], None]] = None,
        timeout: float = 5.0,
    ) -> bool:
        """Execute one battery test case.

        :param adapter: trace32 adapter to use for communication
        :param status_callback: optional logger for progress
        :param timeout: maximum number of seconds to wait for a stable reading
        :return: ``True`` if the final voltage lies within the pass range
                 (8000--16000 mV), ``False`` otherwise.
        """
        passed, _ = BatTest.run_with_voltage(adapter, status_callback, timeout)
        return passed

    @staticmethod
    def run_with_voltage(
        adapter: Trace32Interface,
        status_callback: Optional[Callable[[str], None]] = None,
        timeout: float = 5.0,
    ) -> tuple:
        """Execute one battery test case and return both pass/fail and the measured voltage.

        :param adapter: trace32 adapter to use for communication
        :param status_callback: optional logger for progress
        :param timeout: maximum number of seconds to wait for a stable reading
        :return: tuple ``(passed: bool, voltage: float)`` where *voltage* is 0.0
                 if the reading could not be obtained.
        """
        log = status_callback or (lambda msg: None)

        # Clear previous reading to reduce stale-value false PASS when measurement is not refreshed.
        try:
            adapter.set_variable("TestFw_AiBatRef", 0)
        except Exception:
            pass

        log("BAT: triggering measurement DID")
        adapter.send_did(TestFunctionCmd.TESTFW_GUI_CMD_BATT_MONITOR_e)

        log(f"BAT: waiting {TIMING.bat_initial_wait:.1f} seconds for initial stabilisation")
        time.sleep(TIMING.bat_initial_wait)

        voltage = BatTest._wait_for_stable_voltage(adapter, timeout=timeout)
        if voltage is None:
            log("BAT: voltage never stabilised within timeout")
            return False, 0.0

        log(f"BAT: final voltage = {voltage} mV")
        passed = 8000 <= voltage <= 16000
        log(f"BAT result: {'✓ PASS' if passed else '✗ FAIL'}")
        return passed, voltage

    @staticmethod
    def _wait_for_stable_voltage(
        adapter: Trace32Interface,
        timeout: float = 5.0,
        poll_interval: float = TIMING.stable_poll_interval,
    ) -> Optional[float]:
        """Poll ``TestFw_AiBatRef`` until a stable reading appears.

        Stability is defined as two consecutive identical values.  Returns the
        stable value or ``None`` if the timeout elapses first.
        """
        start = time.time()
        last = None
        stable_count = 0

        while time.time() - start < timeout:
            try:
                raw = adapter.read_variable("TestFw_AiBatRef")
                val = float(raw)
            except Exception:
                val = None

            # 0.0 means the ADC has not produced a real reading yet;
            # skip it so it is never mistaken for a stable voltage.
            if val is not None and val != 0.0:
                if last is not None and abs(val - last) < 1e-3:
                    stable_count += 1
                else:
                    stable_count = 0
                last = val
                if stable_count >= 1:
                    return val

            time.sleep(poll_interval)

        return None
