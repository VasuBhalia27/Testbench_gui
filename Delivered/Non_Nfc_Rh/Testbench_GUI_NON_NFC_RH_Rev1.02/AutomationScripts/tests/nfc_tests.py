from AutomationScripts.backend_adapter.nfc_service import read_nfc_values


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


def execute_all_nfc_tests() -> list:
    """Execute all NFC tab tests."""
    return run_suite()
