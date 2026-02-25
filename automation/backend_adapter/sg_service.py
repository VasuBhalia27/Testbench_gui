"""
Strain Gauge (SG) backend adapter
"""
from .common import read_variable


def read_sg_values(test_id: str) -> dict:
    keys = [
        "TestFw_DoPwrSg",
        "TestFw_Sg1PlusOpamp",
        "TestFw_Sg1MinusOpamp",
        "TestFw_Sg1Opamp",
        "TestFw_Sg1Dac",
        "TestFw_Sg2PlusOpamp",
        "TestFw_Sg2MinusOpamp",
        "TestFw_Sg2Opamp",
        "TestFw_Sg2Dac",
    ]
    res = {}
    for k in keys:
        v = read_variable(k)
        res[k] = (float(v) if v is not None else None)
    return res
