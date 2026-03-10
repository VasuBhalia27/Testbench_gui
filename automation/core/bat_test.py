"""Battery-specific test logic.

The battery monitor test reads the ``TestFw_AiBatRef`` variable and waits
for it to stabilise after triggering the appropriate DID.  A stable voltage
in the range 11900-12100 mV is considered a pass.
"""

import time
from typing import Any, Callable, Optional

from automation.core.trace32_adapter import Trace32Interface
from Functional.trace32 import TestFunctionCmd


class BatTest:
    """Standalone battery monitor test implementation."""

    @staticmethod
    def run(
        adapter: Trace32Interface,
        status_callback: Optional[Callable[[str], None]] = None,
        timeout: float = 30.0,
    ) -> bool:
        """Execute one battery test case.

        :param adapter: trace32 adapter to use for communication
        :param status_callback: optional logger for progress
        :param timeout: maximum number of seconds to wait for a stable reading
        :return: ``True`` if the final voltage lies within the pass range
                 (11900--12100 mV), ``False`` otherwise.
        """
        log = status_callback or (lambda msg: None)

        log("BAT: triggering measurement DID")
        adapter.send_did(TestFunctionCmd.TESTFW_GUI_CMD_BATT_MONITOR_e)

        log("BAT: waiting 1 second for initial stabilisation")
        time.sleep(1)

        voltage = BatTest._wait_for_stable_voltage(adapter, timeout=timeout)
        if voltage is None:
            log("BAT: voltage never stabilised within timeout")
            return False

        log(f"BAT: final voltage = {voltage} mV")
        return 11900 <= voltage <= 12100

    @staticmethod
    def _wait_for_stable_voltage(
        adapter: Trace32Interface,
        timeout: float = 30.0,
        poll_interval: float = 0.5,
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

            if val is not None:
                if last is not None and abs(val - last) < 1e-3:
                    stable_count += 1
                else:
                    stable_count = 0
                last = val
                if stable_count >= 2:
                    return val

            time.sleep(poll_interval)

        return None
