from AutomationScripts.backend_adapter.sg_service import read_sg_values


def run_suite():
    results = []
    data = read_sg_values("sg_suite")
    for var, val in data.items():
        measured = float(val) if val is not None else None
        measured_str = f"{measured:.4f}" if measured is not None else "N/A"
        status = "PASS" if measured is not None else "FAIL"
        details = "" if status == "PASS" else "Backend unavailable or read error"
        results.append({
            "TestCaseID": "TC_SG_01",
            "TestName": "SG basic read",
            "MeasuredValue": measured,
            "MeasuredStr": measured_str,
            "Expected": "",
            "Status": status,
            "Details": details,
        })
    return results


def execute_all_sg_tests() -> list:
    """Execute all strain gauge tab tests."""
    return run_suite()
