"""
NFC backend adapter
"""
from .common import read_variable


def read_nfc_values(test_id: str) -> dict:
    v = read_variable("TestFw_IsNfcDetectedCard")
    return {"TestFw_IsNfcDetectedCard": (int(v) if v is not None else None)}
