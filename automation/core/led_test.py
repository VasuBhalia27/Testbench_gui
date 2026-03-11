"""LED-specific test logic extracted into its own module.

Separating each functional test into a dedicated file makes debugging and
maintenance easier: failures are localized, and collaborators can work on
individual tests without risk of interfering with others.

This module provides a single helper class, :class:`LedTest`, which encapsu-
lates both the on/off procedures and the voltage-stability polling logic.
"""

import time
from typing import Any, Callable, Optional

from automation.core.trace32_adapter import Trace32Interface
from Functional.trace32 import TestFunctionCmd


class LedTest:
    """Standalone LED test implementation."""

    @staticmethod
    def run(
        adapter: Trace32Interface,
        on: bool,
        status_callback: Optional[Callable[[str], None]] = None,
        timeout: float = 5.0,
    ) -> bool:
        """Execute one LED test case.

        :param adapter: trace32 adapter to use for communication
        :param on: ``True`` for "LED on", ``False`` for "LED off"
        :param status_callback: optional logger for progress
        :param timeout: maximum number of seconds to wait for a stable reading
        :return: ``True`` if the final voltage lies within the expected pass
                 range, ``False`` otherwise.
        """
        log = status_callback or (lambda msg: None)

        log(f"LED {'ON' if on else 'OFF'}: setting request")
        adapter.set_variable("LedTest_LedCanLinRequest", 1 if on else 0)

        log("LED: waiting 3 seconds for voltage to stabilise")
        time.sleep(3)

        log("LED: triggering measurement DID")
        adapter.send_did(TestFunctionCmd.TESTFW_GUI_CMD_LED_TEST_e)

        voltage = LedTest._wait_for_stable_voltage(adapter, timeout=timeout)
        if voltage is None:
            log("LED: voltage never stabilised within timeout")
            return False

        log(f"LED: final voltage = {voltage} mV")
        if on:
            return 2400 <= voltage <= 2600
        else:
            return voltage <= 10.0

    @staticmethod
    def _wait_for_stable_voltage(
        adapter: Trace32Interface,
        timeout: float = 2.0,
        poll_interval: float = 0.5,
    ) -> Optional[float]:
        """Poll ``TestFw_LedVoltage`` until a stable reading appears.

        Stability is defined as two consecutive identical values.  Returns the
        stable value or ``None`` if the timeout elapses first.
        """
        start = time.time()
        last = None
        stable_count = 0

        while time.time() - start < timeout:
            try:
                raw = adapter.read_variable("TestFw_LedVoltage")
                val = float(raw)
            except Exception:
                val = None

            if val is not None:
                if last is not None and abs(val - last) < 50.0:
                    stable_count += 1
                else:
                    stable_count = 0
                last = val
                if stable_count >= 1:
                    return val

            time.sleep(poll_interval)

        return None
