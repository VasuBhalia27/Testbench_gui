"""
CAN backend adapter
"""
from .common import read_variable


def read_can_values(test_id: str) -> dict:
    v = read_variable("DummyBytes")
    return {"DummyBytes": (int(v) if v is not None else None)}
