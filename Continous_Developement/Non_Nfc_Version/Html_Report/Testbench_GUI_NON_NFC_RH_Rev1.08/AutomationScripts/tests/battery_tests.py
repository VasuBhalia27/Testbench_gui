from AutomationScripts.backend_adapter.battery_service import read_battery_values

# Per-variable threshold definitions.
# Each entry: (test_case_id, human_name, validator_fn, expected_description)
_THRESHOLDS = {
    "TestFw_BatRefStatus": (
        "TC_BAT_01", "Battery Reference Status",
        lambda v: v is not None, "present"
    ),
    "TestFw_AiBatRef": (
        "TC_BAT_01", "Battery AI Reference Voltage (12 V supply)",
        lambda v: 11500 <= v <= 12500, "11500–12500 mV"
    ),
}


def run_suite():
    results = []
    data = read_battery_values("battery_suite")
    for var, val in data.items():
        tc_id, tc_name, validator, expected = _THRESHOLDS.get(
            var, ("TC_BAT_01", var, lambda v: v is not None, "not None")
        )
        measured = float(val) if val is not None else None
        measured_str = f"{measured:.4f}" if measured is not None else "N/A"
        if measured is None:
            status = "FAIL"
            details = "No reading from target (backend unavailable or read error)"
        elif validator(measured):
            status = "PASS"
            details = f"Value {measured_str} satisfies criteria '{expected}'"
        else:
            status = "FAIL"
            details = f"Value {measured_str} does not satisfy criteria '{expected}'"
        results.append({
            "TestCaseID": tc_id,
            "TestName": tc_name,
            "MeasuredValue": measured,
            "MeasuredStr": measured_str,
            "Expected": expected,
            "Status": status,
            "Details": details,
        })
    return results


def execute_all_battery_tests() -> list:
    """Execute all battery tab tests."""
    return run_suite()
