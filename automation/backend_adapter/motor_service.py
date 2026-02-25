"""
Motor backend adapter
"""
from .common import read_variable


def read_motor_values(test_id: str) -> dict:
    keys = [
        "TestFw_MotorCoupledVoltage",
        "TestFw_MotorDecoupledVoltage",
        "TestFw_MotorCurrentValue",
        "TestFw_MotorLoadError",
    ]
    res = {}
    for k in keys:
        v = read_variable(k)
        res[k] = (float(v) if v is not None else None)
    return res
