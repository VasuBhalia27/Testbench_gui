"""
LIN backend adapter
"""
from .common import read_variable


def read_lin_values(test_id: str) -> dict:
    """Read LIN frame status from test firmware.
    Variable: TestFw_LinFrameStatus (firmware test variable for LIN frame transmission/reception).
    Returns the frame status to validate LIN communication.
    """
    v = read_variable("TestFw_LinFrameStatus")
    return {"TestFw_LinFrameStatus": (float(v) if v is not None else None)}
