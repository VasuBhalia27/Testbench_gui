from AutomationScripts.backend_adapter.can_service import read_can_values


def run_suite():
    results = []
    data = read_can_values("can_suite")
    for var, val in data.items():
        measured = float(val) if val is not None else None
        measured_str = f"{measured:.4f}" if measured is not None else "N/A"
        status = "PASS" if measured is not None else "FAIL"
        details = "" if status == "PASS" else "Backend unavailable or read error"
        results.append({
            "TestCaseID": "TC_CAN_01",
            "TestName": "CAN basic read",
            "MeasuredValue": measured,
            "MeasuredStr": measured_str,
            "Expected": "",
            "Status": status,
            "Details": details,
        })
    return results


def execute_all_can_tests() -> list:
    """Execute all CAN tab tests."""
    return run_suite()
