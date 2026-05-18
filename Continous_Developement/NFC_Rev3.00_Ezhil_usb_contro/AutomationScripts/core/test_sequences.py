"""Test execution logic for SmartBU automation.

This module encapsulates the detailed sequences that the automation
framework will perform on the target hardware.  Each function here should
mirror the behaviour of a human operator clicking checkboxes/buttons
in the ``gui_main`` application.

At the moment we only implement the LED test; further routines will be
added later as the automation coverage expands.
"""

import time
from typing import Any, Callable, Optional

import Functional.trace32 as _t32_mod
from AutomationScripts.core.trace32_adapter import Trace32Interface

# individual sequence modules
from AutomationScripts.core.led_test import LedTest
from AutomationScripts.core.bat_test import BatTest
from AutomationScripts.core.motor_test import MotorTest, MotorOCPError
from AutomationScripts.core.eos_test import EosTest
from AutomationScripts.core.sg_test import SgTest
from AutomationScripts.core.capa_test import CapaTest
from AutomationScripts.core.timing_profile import TIMING
from Functional.trace32 import TestFunctionCmd

from digital_switch import DigitalSwitchController


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
        self._digital_switch = None

    def _open_digital_switch(self):
        if self._digital_switch is None:
            self._digital_switch = DigitalSwitchController()
            self._log("Digital switch controller initialised and forced OFF")

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

    def run_battery_test_with_voltage(self, timeout: float = 10.0):
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

    @staticmethod
    def _as_number(value: Any) -> Optional[float]:
        """Convert a debugger value to float, returning None on parse failure."""
        if value is None:
            return None
        try:
            return float(str(value).strip())
        except Exception:
            return None

    @staticmethod
    def _as_int(value: Any) -> Optional[int]:
        """Convert a debugger value to int, returning None on parse failure."""
        number = TestSequenceRunner._as_number(value)
        if number is None:
            return None
        try:
            return int(number)
        except Exception:
            return None

    def _run_nfc_spi_self_test_with_logging(self) -> dict:
        """Run NFC SPI self-test and LED output check.

        Sends TEST_GUI_CMD_NFC_SPI_DIAG_e (no antenna or card required).
        If the SPI link is confirmed healthy, turns the LED ON as a visual
        output check, then restores it to OFF.

        Returns a dict with keys:
            pass, spi_pass, led_pass, spi_error, hw_ver, rom_ver, fw_ver,
            led_voltage.
        """
        self._log("NFC SPI self-test: preparing variables")
        self.adapter.set_variable("TestFw_KeepEcuAwake", 1)

        self._log("NFC SPI self-test: sending SPI diagnostic command (no card required)")
        self.adapter.send_did(TestFunctionCmd.TEST_GUI_CMD_NFC_SPI_DIAG_e)
        time.sleep(2)

        spi_error = self.adapter.read_variable("TestFw_NfcSpiError")
        hw_ver    = self.adapter.read_variable("TestFw_NfcHwVersion")
        rom_ver   = self.adapter.read_variable("TestFw_NfcRomVersion")
        fw_ver    = self.adapter.read_variable("TestFw_NfcFwVersion")

        spi_err_int = self._as_int(spi_error)
        hw_ver_int  = self._as_int(hw_ver)
        rom_ver_int = self._as_int(rom_ver)
        fw_ver_int  = self._as_int(fw_ver)

        self._log(
            f"NFC SPI diag: spi_error={spi_err_int}, "
            f"hw=0x{(hw_ver_int or 0):X}, "
            f"rom=0x{(rom_ver_int or 0):X}, "
            f"fw=0x{(fw_ver_int or 0):X}"
        )

        # PASS = SpiError is 0 AND Target ID (HwVersion) is non-zero,
        # which proves the device responded over SPI.
        spi_passed = (
            spi_err_int == 0
            and hw_ver_int not in (None, 0)
        )
        self._log(f"NFC SPI result: {'✓ PASS' if spi_passed else '✗ FAIL'}")

        # Output check: turn LED ON to confirm the output path is functional
        self._log("NFC output check: turning LED ON for output verification")
        led_passed, led_voltage = LedTest.run_with_voltage(
            adapter=self.adapter,
            on=True,
            status_callback=self._log,
            timeout=3.0,
        )
        self._log(
            f"NFC output check (LED ON): voltage={led_voltage:.1f} mV — "
            f"{'✓ PASS' if led_passed else '✗ FAIL'}"
        )

        # Restore LED to OFF after output check
        self._log("NFC output check: restoring LED OFF")
        self.adapter.set_variable("LedTest_LedCanLinRequest", 0)
        time.sleep(0.5)

        return {
            "pass":      spi_passed and led_passed,
            "spi_pass":  spi_passed,
            "led_pass":  led_passed,
            "spi_error": spi_err_int,
            "hw_ver":    hw_ver_int,
            "rom_ver":   rom_ver_int,
            "fw_ver":    fw_ver_int,
            "led_voltage": led_voltage,
        }

    def _run_nfc_test_with_logging(self) -> dict:
        """Run NFC test, log fetched data, and evaluate strict pass/fail."""
        self._log("NFC: preparing test variables")
        self.adapter.set_variable("TestFw_KeepEcuAwake", 1)

        self._log("NFC: sending test command")
        self.adapter.send_did(TestFunctionCmd.TEST_GUI_CMD_NFC_TEST_e)
        time.sleep(2)

        nfc_vars = {
            "detected": self.adapter.read_variable("TestFw_IsNfcDetectedCard"),
            "spi_error": self.adapter.read_variable("TestFw_NfcSpiError"),
            "rx_len": self.adapter.read_variable("TestFw_NfcRxDataLength"),
            "hw_ver": self.adapter.read_variable("TestFw_NfcHwVersion"),
            "rom_ver": self.adapter.read_variable("TestFw_NfcRomVersion"),
            "fw_ver": self.adapter.read_variable("TestFw_NfcFwVersion"),
            "ntsm_state": self.adapter.read_variable("TestFw_NfcNtsmState"),
        }

        self._log(
            "NFC data: "
            f"detected={nfc_vars['detected']}, "
            f"spi_error={nfc_vars['spi_error']}, "
            f"hw=0x{(self._as_int(nfc_vars['hw_ver']) or 0):X}, "
            f"rom=0x{(self._as_int(nfc_vars['rom_ver']) or 0):X}, "
            f"fw=0x{(self._as_int(nfc_vars['fw_ver']) or 0):X}"
        )

        detected = self._as_int(nfc_vars["detected"])
        spi_error = self._as_int(nfc_vars["spi_error"])
        rx_len = self._as_int(nfc_vars["rx_len"])
        hw_ver = self._as_int(nfc_vars["hw_ver"])
        rom_ver = self._as_int(nfc_vars["rom_ver"])
        fw_ver = self._as_int(nfc_vars["fw_ver"])

        # Match manual NFC tab behavior: overall PASS is based on SPI
        # diagnostics, while card-detect is informational only.
        passed = (
            spi_error == 0
            and hw_ver not in (None, 0)
            and rom_ver not in (None, 0)
            and fw_ver not in (None, 0)
        )

        self._log(f"NFC result: {'✓ PASS' if passed else '✗ FAIL'}")
        return {
            "pass": passed,
            "detected": detected,
            "spi_error": spi_error,
            "rx_len": rx_len,
            "hw_ver": hw_ver,
            "rom_ver": rom_ver,
            "fw_ver": fw_ver,
            "ntsm_state": self._as_int(nfc_vars["ntsm_state"]),
        }

    def _run_can_test_with_logging(self) -> dict:
        """Run CAN test with automatic loopback setup and Tx/Rx logging."""
        tx_bytes = [11, 22, 33, 44, 55, 66, 77, 88]

        self._log("CAN: enabling local loopback and awake mode")
        self.adapter.set_variable("TestFw_CanGuiLocalLoopbackEnable", 1)
        self.adapter.set_variable("TestFw_KeepEcuAwake", 1)

        for idx, value in enumerate(tx_bytes):
            self.adapter.set_variable(f"DummyBytes.dummy_byte{idx}_U8", value)
        self._log(f"CAN TX data: msg_id=0x796, bytes={tx_bytes}")

        self._log("CAN: sending test command")
        self.adapter.send_did(TestFunctionCmd.TEST_GUI_CMD_CAN_TEST_e)
        time.sleep(2)

        rx_valid = self._as_int(self.adapter.read_variable("TestFw_CanRxDataValid"))
        rx_msg_id = self._as_int(self.adapter.read_variable("TestFw_CanRxMessageId"))
        rx_bytes = [
            self._as_int(self.adapter.read_variable(f"TestFw_CanRxBytes.dummy_byte{i}_U8"))
            for i in range(8)
        ]
        can_active = self._as_int(self.adapter.read_variable("TestFw_CanIsActiveState"))
        fault_latch = self._as_int(self.adapter.read_variable("TestFw_CanFaultLatch"))

        self._log(
            "CAN RX data: "
            f"valid={rx_valid}, msg_id=0x{(rx_msg_id or 0):X}, bytes={rx_bytes}, "
            f"active={can_active}"
        )

        any_rx_nonzero = any(v not in (None, 0) for v in rx_bytes)
        # Match manual CAN tab loopback behavior: in local loopback mode
        # only RxDataValid is required; bus-level indicators are suppressed.
        passed = (
            rx_valid == 1
            and any_rx_nonzero
        )

        self._log(f"CAN result: {'✓ PASS' if passed else '✗ FAIL'}")
        return {
            "pass": passed,
            "tx_bytes": tx_bytes,
            "rx_valid": rx_valid,
            "rx_msg_id": rx_msg_id,
            "rx_bytes": rx_bytes,
            "can_active": can_active,
            "fault_latch": fault_latch,
        }

    def _run_lin_test_with_logging(self) -> dict:
        """Run LIN test with automatic Tx setup and Tx/Rx logging."""
        tx_pid = 0x3A
        tx_bytes = [44, 55, 66, 77, 11, 22, 33, 44]

        self._log("LIN: setting Tx PID and Tx bytes")
        self.adapter.set_variable("TestFw_LinTxPid", tx_pid)
        for idx, value in enumerate(tx_bytes):
            self.adapter.set_variable(f"TestFw_LinTxByte{idx}", value)
        self._log(f"LIN TX data: msg_id=0x{tx_pid:X}, bytes={tx_bytes}")

        self._log("LIN: sending test command")
        self.adapter.send_did(TestFunctionCmd.TEST_GUI_CMD_LIN_e)
        time.sleep(2)

        rx_valid = self._as_int(self.adapter.read_variable("TestFw_LinRxDataValid"))
        rx_pid = self._as_int(self.adapter.read_variable("TestFw_LinRxPid"))
        rx_bytes = [
            self._as_int(self.adapter.read_variable(f"TestFw_LinRxData_aU8[{i}]"))
            for i in range(8)
        ]

        self._log(
            "LIN RX data: "
            f"valid={rx_valid}, msg_id=0x{(rx_pid or 0):X}, bytes={rx_bytes}"
        )

        any_rx_nonzero = any(v not in (None, 0) for v in rx_bytes)
        passed = (
            rx_valid == 1
            and any_rx_nonzero
            and rx_pid is not None
        )

        self._log(f"LIN result: {'✓ PASS' if passed else '✗ FAIL'}")
        return {
            "pass": passed,
            "tx_pid": tx_pid,
            "tx_bytes": tx_bytes,
            "rx_valid": rx_valid,
            "rx_pid": rx_pid,
            "rx_bytes": rx_bytes,
        }

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

        # Ensure the digital switch is OFF before any automation begins.
        self._open_digital_switch()
        self._digital_switch.turn_off()
        self._log("Digital switch: OFF before battery test")

        # --- Battery voltage check (runs first) ----------------------------
        # A reading of 0.0 mV means the supply has not yet stabilised.
        # In that case there is no point running further tests; all hardware
        # functions depend on a healthy supply voltage.
        bat_passed, bat_voltage = self.run_battery_test_with_voltage(timeout=10.0)
        results['battery'] = {'pass': bat_passed, 'voltage': bat_voltage}

        if bat_voltage == 0.0:
            self._log(
                "BAT: 0.0 mV — performing MCU hardware reset (SYStem.Up) and retrying (attempt 2/2)"
            )
            # Perform a full target hardware reset via Trace32 instead of just
            # waiting.  SYStem.Up drives the RESET pin on the MCU, clears any
            # ADC/NFC initialisation fault that persisted across the first boot,
            # and lets the firmware run a clean power-on sequence.
            try:
                if _t32_mod.dbg and hasattr(_t32_mod.dbg, 'cmd'):
                    _t32_mod.dbg.cmd("Break")          # halt MCU
                    time.sleep(0.5)
                    _t32_mod.dbg.cmd("SYStem.Up")      # full hardware reset of target
                    time.sleep(3.0)                     # wait for MCU power-on reset
                    _t32_mod.dbg.cmd("Go")             # resume firmware execution
                    time.sleep(TIMING.first_run_fw_init_wait)  # wait for TestFw to re-init
            except Exception as exc:
                self._log(f"BAT: MCU reset via SYStem.Up failed ({exc}), continuing anyway")
            bat_passed, bat_voltage = self.run_battery_test_with_voltage(timeout=10.0)
            results['battery'] = {'pass': bat_passed, 'voltage': bat_voltage}

        if bat_voltage == 0.0:
            self._log(
                "BAT: \u2717 voltage is 0.0 mV \u2014 supply has not yet stabilised.\n"
                "     Please wait for the voltage to stabilise and try again."
            )
            return results

        # Turn ON the digital switch before CAPA begins.
        self._log("Digital switch: turning ON before CAPA tests")
        self._digital_switch.turn_on()

        try:
            # CAPA tests run immediately after battery (before other tests so that
            # the capacitive sensors are measured while nothing else is active).
            capa_results = self.run_capa_test()
            results['capa1'] = capa_results['capa1']
            results['capa2'] = capa_results['capa2']
        finally:
            self._log("Digital switch: turning OFF after CAPA tests")
            self._digital_switch.turn_off()

        # the LED tests run in both variants
        led_on_passed, led_on_v   = self.run_led_test_with_voltage(on=True)
        led_off_passed, led_off_v = self.run_led_test_with_voltage(on=False)
        results['led_on']  = {'pass': led_on_passed,  'voltage': led_on_v}
        results['led_off'] = {'pass': led_off_passed, 'voltage': led_off_v}

        # motor test
        try:
            mot_passed, mot_v, mot_i, mot_e = self.run_motor_test_with_values()
            results['motor'] = {'pass': mot_passed, 'voltage': mot_v,
                                'current': mot_i, 'load_error': mot_e}
        except MotorOCPError as _ocp_err:
            self._log(f"MOTOR: \u26a0 {_ocp_err}")
            self._log(
                "MOTOR: PSU over-current triggered — performing power-cycle recovery"
                " before continuing with remaining tests..."
            )
            results['motor'] = {'pass': False, 'voltage': 0.0, 'current': 0.0, 'load_error': -1.0}
            self._power_cycle()
        except Exception as _mot_exc:
            self._log(f"MOTOR: test failed with exception: {_mot_exc}")
            results['motor'] = {'pass': False, 'voltage': 0.0, 'current': 0.0, 'load_error': -1.0}

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
            try:
                results['nfc_spi_self_test'] = self._run_nfc_spi_self_test_with_logging()
            except Exception as exc:
                self._log(f"NFC SPI self-test: failed with exception: {exc}")
                results['nfc_spi_self_test'] = {
                    'pass': False, 'spi_pass': False, 'led_pass': False,
                    'spi_error': None, 'hw_ver': None, 'rom_ver': None,
                    'fw_ver': None, 'led_voltage': 0.0,
                }

            try:
                results['nfc'] = self._run_nfc_test_with_logging()
            except Exception as exc:
                self._log(f"NFC: test failed with exception: {exc}")
                results['nfc'] = {'pass': False}

            try:
                results['can'] = self._run_can_test_with_logging()
            except Exception as exc:
                self._log(f"CAN: test failed with exception: {exc}")
                results['can'] = {'pass': False}

            try:
                results['lin'] = self._run_lin_test_with_logging()
            except Exception as exc:
                self._log(f"LIN: test failed with exception: {exc}")
                results['lin'] = {'pass': False}

        # the remaining tests will eventually be added here
        return results
