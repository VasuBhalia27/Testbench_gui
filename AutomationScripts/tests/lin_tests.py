from AutomationScripts.backend_adapter.lin_service import read_lin_values


def run_suite():
    results = []
    data = read_lin_values("lin_suite")
    for var, val in data.items():
        measured = float(val) if val is not None else None
        measured_str = f"{measured:.4f}" if measured is not None else "N/A"
        status = "PASS" if measured is not None else "FAIL"
        details = "" if status == "PASS" else "Backend unavailable or read error"
        results.append({
            "TestCaseID": "TC_LIN_01",
            "TestName": "LIN basic read",
            "MeasuredValue": measured,
            "MeasuredStr": measured_str,
            "Expected": "",
            "Status": status,
            "Details": details,
        })
    return results
