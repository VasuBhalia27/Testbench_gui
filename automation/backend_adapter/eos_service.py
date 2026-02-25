"""
EOS backend adapter
"""
from .common import read_variable


def read_eos_values(test_id: str) -> dict:
    keys = [
        "TestFw_EosDiagVoltage",
        "TestFw_EosPinState",
        "TestFw_EosErrorsWithLow",
        "TestFw_EosErrorsWithHigh",
    ]
    res = {}
    for k in keys:
        v = read_variable(k)
        res[k] = (float(v) if v is not None else None)
    return res
