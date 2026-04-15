from AutomationScripts.backend_adapter.eos_service import read_eos_values


def run_suite():
    results = []
    data = read_eos_values("eos_suite")
    for var, val in data.items():
        measured = float(val) if val is not None else None
        measured_str = f"{measured:.4f}" if measured is not None else "N/A"
        status = "PASS" if measured is not None else "FAIL"
        details = "" if status == "PASS" else "Backend unavailable or read error"
        results.append({
            "TestCaseID": "TC_EOS_01",
            "TestName": "EOS basic read",
            "MeasuredValue": measured,
            "MeasuredStr": measured_str,
            "Expected": "",
            "Status": status,
            "Details": details,
        })
    return results


def execute_all_eos_tests() -> list:
    """Execute all EOS tab tests."""
    return run_suite()
