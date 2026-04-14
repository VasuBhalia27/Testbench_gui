from AutomationScripts.backend_adapter.lin_service import read_lin_values


def run_suite():
    results = []
    data = read_lin_values("lin_suite")
    for var, val in data.items():
        measured = float(val) if val is not None else None
        measured_str = f"{measured:.4f}" if measured is not None else "N/A"
        status = "PASS" if measured == 1.0 else "FAIL"
        details = "" if status == "PASS" else "LIN frame inactive or backend unavailable"
        results.append({
            "TestCaseID": "TC_LIN_01",
            "TestName": "LIN basic read",
            "MeasuredValue": measured,
            "MeasuredStr": measured_str,
            "Expected": "1",
            "Status": status,
            "Details": details,
        })
    return results


def execute_all_lin_tests() -> list:
    """Execute all LIN tab tests."""
    return run_suite()
