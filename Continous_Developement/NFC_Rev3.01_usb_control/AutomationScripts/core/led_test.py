"""LED-specific test logic extracted into its own module.

Separating each functional test into a dedicated file makes debugging and
maintenance easier: failures are localized, and collaborators can work on
individual tests without risk of interfering with others.

This module provides a single helper class, :class:`LedTest`, which encapsu-
lates both the on/off procedures and the voltage-stability polling logic.
"""

import time
from pathlib import Path
from typing import Any, Callable, Optional
import os
from datetime import datetime

from AutomationScripts.core.trace32_adapter import Trace32Interface
from AutomationScripts.core.timing_profile import TIMING
from Functional.trace32 import TestFunctionCmd

LOG_DIR = Path(__file__).resolve().parents[2]
LED_LOG_PATH = LOG_DIR / "led_debug.log"


class LedTest:
    """Standalone LED test implementation."""

    @staticmethod
    def _read_once(adapter: Trace32Interface) -> Optional[float]:
        try:
            raw = adapter.read_variable("TestFw_LedVoltage")
            if os.getenv("LED_DEBUG", "0") == "1":
                try:
                    LED_LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
                    with open(LED_LOG_PATH, "a", encoding="utf-8") as f:
                        f.write(f"{datetime.utcnow().isoformat()}Z raw_led_voltage: {raw}\n")
                except Exception:
                    pass
            return float(raw)
        except Exception:
            return None

    @staticmethod
    def _measure_voltage(adapter: Trace32Interface, timeout: float) -> Optional[float]:
        """Trigger LED DID and return measured voltage with fallback polling."""
        adapter.send_did(TestFunctionCmd.TESTFW_GUI_CMD_LED_TEST_e)
        time.sleep(0.5)
        voltage = LedTest._read_once(adapter)
        if voltage is None:
            voltage = LedTest._wait_for_stable_voltage(adapter, timeout=timeout)
        return voltage

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

        _wait = TIMING.led_off_stabilize_wait if not on else TIMING.led_stabilize_wait
        log(f"LED: waiting {_wait:.1f} seconds for voltage to stabilise")
        time.sleep(_wait)

        voltage = LedTest._measure_voltage(adapter, timeout=timeout)

        # Retry up to 2 times for transient 0 mV on LED ON runs seen in logs.
        if on and (voltage is None or voltage <= 0):
            log("LED: transient 0 mV on ON path, retrying")
            for _ in range(2):
                time.sleep(1.0)
                voltage = LedTest._measure_voltage(adapter, timeout=timeout)
                if voltage is not None and voltage > 0:
                    break

        if voltage is None:
            log("LED: voltage never stabilised within timeout")
            return False

        log(f"LED: final voltage = {voltage} mV")
        if on:
            return voltage > 0
        else:
            return voltage <= 10.0

    @staticmethod
    def run_with_voltage(
        adapter: Trace32Interface,
        on: bool,
        status_callback: Optional[Callable[[str], None]] = None,
        timeout: float = 5.0,
    ) -> tuple:
        """Like :meth:`run` but also returns the measured voltage.

        :return: tuple ``(passed: bool, voltage_mV: float)``; voltage is 0.0
                 when the reading could not be obtained.
        """
        log = status_callback or (lambda msg: None)

        log(f"LED {'ON' if on else 'OFF'}: setting request")
        adapter.set_variable("LedTest_LedCanLinRequest", 1 if on else 0)

        _wait = TIMING.led_off_stabilize_wait if not on else TIMING.led_stabilize_wait
        log(f"LED: waiting {_wait:.1f} seconds for voltage to stabilise")
        time.sleep(_wait)

        voltage = LedTest._measure_voltage(adapter, timeout=timeout)

        if on and (voltage is None or voltage <= 0):
            log("LED: transient 0 mV on ON path, retrying")
            for _ in range(2):
                time.sleep(1.0)
                voltage = LedTest._measure_voltage(adapter, timeout=timeout)
                if voltage is not None and voltage > 0:
                    break

        if voltage is None:
            log("LED: voltage never stabilised within timeout")
            return False, 0.0

        log(f"LED: final voltage = {voltage} mV")
        if on:
            return voltage > 0, voltage
        else:
            return voltage <= 10.0, voltage

    @staticmethod
    def _wait_for_stable_voltage(
        adapter: Trace32Interface,
        timeout: float = 3.0,
        poll_interval: float = TIMING.stable_poll_interval,
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
                if os.getenv("LED_DEBUG", "0") == "1":
                    try:
                        LED_LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
                        with open(LED_LOG_PATH, "a", encoding="utf-8") as f:
                            f.write(f"{datetime.utcnow().isoformat()}Z poll_raw_led_voltage: {raw}\n")
                    except Exception:
                        pass
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
