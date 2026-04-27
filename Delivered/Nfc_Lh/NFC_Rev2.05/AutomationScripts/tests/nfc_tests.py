from AutomationScripts.backend_adapter.nfc_service import read_nfc_values, read_nfc_spi_diag_values
from AutomationScripts.backend_adapter.led_service import read_led_voltage


def _as_int(val):
    if val is None:
        return None
    try:
        return int(float(str(val).strip()))
    except Exception:
        return None


def run_suite():
    results = []
    data = read_nfc_values("nfc_suite")
    for var, val in data.items():
        measured = float(val) if val is not None else None
        measured_str = f"{measured:.4f}" if measured is not None else "N/A"
        status = "PASS" if measured is not None else "FAIL"
        details = "" if status == "PASS" else "Backend unavailable or read error"
        results.append({
            "TestCaseID": "TC_NFC_01",
            "TestName": "NFC basic read",
            "MeasuredValue": measured,
            "MeasuredStr": measured_str,
            "Expected": "",
            "Status": status,
            "Details": details,
        })
    return results


def run_nfc_spi_self_test_suite():
    """TC_NFC_SPI_01 — NFC SPI self-test (no antenna or card required).

    Reads SPI diagnostic variables written by TEST_GUI_CMD_NFC_SPI_DIAG_e.
    Passes when SpiError is 0 and all version registers are non-zero.
    """
    data = read_nfc_spi_diag_values("nfc_spi_self_test")

    spi_err = _as_int(data.get("TestFw_NfcSpiError"))
    hw_ver  = _as_int(data.get("TestFw_NfcHwVersion"))
    rom_ver = _as_int(data.get("TestFw_NfcRomVersion"))
    fw_ver  = _as_int(data.get("TestFw_NfcFwVersion"))

    passed = (
        spi_err == 0
        and hw_ver  not in (None, 0)
        and rom_ver not in (None, 0)
        and fw_ver  not in (None, 0)
    )

    details = (
        f"SpiError={spi_err}, "
        f"HwVer=0x{(hw_ver or 0):X}, "
        f"RomVer=0x{(rom_ver or 0):X}, "
        f"FwVer=0x{(fw_ver or 0):X}"
    )

    return [{
        "TestCaseID":    "TC_NFC_SPI_01",
        "TestName":      "NFC SPI Self-Test (no antenna/card required)",
        "MeasuredValue": spi_err,
        "MeasuredStr":   details,
        "Expected":      "SpiError=0, HwVer!=0, RomVer!=0, FwVer!=0",
        "Status":        "PASS" if passed else "FAIL",
        "Details":       details if not passed else "SPI link verified — transceiver responding",
    }]


def run_nfc_led_output_check_suite():
    """TC_NFC_LED_01 — Output check: LED voltage after NFC SPI self-test.

    After the SPI self-test confirms the NFC transceiver is alive, the
    LED output is exercised to verify the output path is operational.
    Passes when LED voltage is > 0 mV.
    """
    try:
        data = read_led_voltage("TC_NFC_LED_01")
        voltage = data.get("TestFw_LedVoltage")
        if voltage is None:
            raise ValueError("LED voltage not available")
        v = float(voltage)
        passed = v > 0
        return [{
            "TestCaseID":    "TC_NFC_LED_01",
            "TestName":      "NFC Output Check — LED ON",
            "MeasuredValue": v,
            "MeasuredStr":   f"{v:.1f} mV",
            "Expected":      "> 0 mV",
            "Status":        "PASS" if passed else "FAIL",
            "Details":       f"LED voltage: {v:.1f} mV",
        }]
    except Exception as exc:
        return [{
            "TestCaseID":    "TC_NFC_LED_01",
            "TestName":      "NFC Output Check — LED ON",
            "MeasuredValue": None,
            "MeasuredStr":   "N/A",
            "Expected":      "> 0 mV",
            "Status":        "FAIL",
            "Details":       f"Error: {exc}",
        }]


def execute_all_nfc_tests() -> list:
    """Execute all NFC tab tests."""
    return run_suite()
