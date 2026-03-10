from automation.backend_adapter.motor_service import read_motor_values

# Per-variable threshold definitions.
# Each entry: (test_case_id, human_name, validator_fn, expected_description)
_THRESHOLDS = {
    "TestFw_MotorCoupledVoltage":   ("TC_MOTOR_01", "Motor Coupled Voltage",   lambda v: v > 0,   "> 0 mV"),
    "TestFw_MotorDecoupledVoltage": ("TC_MOTOR_01", "Motor Decoupled Voltage", lambda v: v > 0,   "> 0 mV"),
    "TestFw_MotorCurrentValue":     ("TC_MOTOR_01", "Motor Current",           lambda v: v > 0,   "> 0 mA"),
    "TestFw_MotorLoadError":        ("TC_MOTOR_01", "Motor Load Error",        lambda v: v == 0,  "0 (no error)"),
}


def run_suite():
    results = []
    data = read_motor_values("motor_suite")
    for var, val in data.items():
        tc_id, tc_name, validator, expected = _THRESHOLDS.get(
            var, ("TC_MOTOR_01", var, lambda v: v is not None, "not None")
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
