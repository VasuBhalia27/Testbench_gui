"""
Capa backend adapter
"""
from .common import read_variable


def read_capa_values(test_id: str) -> dict:
    keys = [
        "TestFw_CapaApproach",
        "TestFw_CapaLock",
        "TestFw_CapaUnlock",
        "TestFw_CapaApproachSensorValue",
        "TestFw_CapaLockSensorValue",
        "TestFw_CapaUnlockSensorValue",
    ]
    res = {}
    for k in keys:
        v = read_variable(k)
        res[k] = (float(v) if v is not None else None)
    return res
