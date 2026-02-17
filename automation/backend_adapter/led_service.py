"""
Backend LED Service Adapter

Provides a clean interface to backend LED test functionality.
Backend team has implemented hardware communication via Trace32 debugger.
Automation ONLY depends on the stable output variables returned.

Returns:
    Dictionary with stable variable names like:
    {
        "TestFw_LedVoltage": <float>
    }
"""

import sys
import time
from pathlib import Path

# Global Trace32 connection handle
_trace32_dbg = None
_trace32_connected = False


def _ensure_trace32_connected() -> bool:
    """
    Ensure Trace32 debugger is connected.
    
    Returns:
        True if connected, False otherwise
    """
    global _trace32_dbg, _trace32_connected
    
    if _trace32_connected and _trace32_dbg is not None:
        return True
    
    try:
        import lauterbach.trace32.rcl as t32
        
        # Try to connect to Trace32
        _trace32_dbg = t32.connect(
            node='localhost',
            port=20006,
            protocol='UDP',
            packlen=1024,
            timeout=5.0
        )
        
        if _trace32_dbg is not None:
            _trace32_connected = True
            print("[OK] Connected to Trace32 debugger")
            return True
        else:
            print("[Warning] Trace32 connection returned None")
            return False
    
    except Exception as e:
        print(f"[Warning] Could not connect to Trace32: {e}")
        _trace32_connected = False
        return False


def _read_variable_value(variable_name: str) -> float:
    """
    Read a test variable value from Trace32 debugger.
    
    Args:
        variable_name: Name of the variable (e.g., "TestFw_LedVoltage")
    
    Returns:
        float: The variable value, or None if read failed
    """
    global _trace32_dbg
    
    if not _trace32_connected or _trace32_dbg is None:
        return None
    
    try:
        # Use Trace32 fnc() to read variable value
        value = _trace32_dbg.fnc(f"Var.VALUE({variable_name})")
        
        if value is not None:
            # Convert to float and return
            return float(value)
    except Exception as e:
        print(f"[Warning] Could not read {variable_name} from Trace32: {e}")
    
    return None


def _set_test_command(did: int) -> bool:
    """
    Set the test command DID in the firmware.
    
    Args:
        did: DID command value (e.g., 101 for LED test)
    
    Returns:
        True if successful, False otherwise
    """
    global _trace32_dbg
    
    if not _trace32_connected or _trace32_dbg is None:
        return False
    
    try:
        # Set TestFw_GuiCmd to the DID value
        _trace32_dbg.cmd(f'Var.set TestFw_GuiCmd = {did}')
        time.sleep(0.5)  # Wait for backend to process command
        return True
    except Exception as e:
        print(f"[Warning] Could not set DID {did}: {e}")
        return False


def read_led_voltage(test_id: str) -> dict:
    """
    Read LED voltage from backend via Trace32 debugger.
    
    This function:
    1. Connects to Trace32 (if not already connected)
    2. Sets the test command DID (101 for LED test)
    3. Waits for firmware to measure voltage
    4. Reads TestFw_LedVoltage from debugger memory
    5. Falls back to mock data if Trace32 unavailable
    
    Args:
        test_id: Test case ID (e.g., "TC_LED_01")
    
    Returns:
        Dictionary with stable output variables:
        {
            "TestFw_LedVoltage": float  # voltage in volts
        }
    """
    # DID 101 is for LED voltage measurement
    DID_LED_TEST = 101
    
    # Try to connect to Trace32
    if not _trace32_connected:
        _ensure_trace32_connected()
    
    # If connected, use real backend
    if _trace32_connected and _trace32_dbg is not None:
        try:
            # Send DID command to firmware
            if _set_test_command(DID_LED_TEST):
                # Read the measured voltage
                voltage = _read_variable_value("TestFw_LedVoltage")
                
                if voltage is not None:
                    # Convert from mV to V (backend provides in mV based on VARIABLE_UNITS_MAP)
                    voltage = voltage / 1000.0
                    
                    print(f"[OK] Read real voltage for {test_id}: {voltage:.3f} V from Trace32")
                    return {
                        "TestFw_LedVoltage": voltage
                    }
        except Exception as e:
            print(f"[ERROR] Real backend read failed: {e}")
            raise Exception(f"Failed to read LED voltage from Trace32: {e}")
    
    # No fallback - require real hardware connection
    raise Exception(f"Trace32 not connected. Cannot measure LED voltage for {test_id}")


def get_backend_status() -> dict:
    """
    Get current backend (Trace32) status.
    
    Returns:
        Dictionary with status information:
        {
            "hardware_connected": bool,
            "debugger_running": bool,
            "trace32_available": bool
        }
    """
    global _trace32_connected
    
    return {
        "hardware_connected": _trace32_connected,
        "debugger_running": _trace32_connected,
        "trace32_available": _trace32_connected
    }


def disconnect_backend():
    """
    Disconnect from Trace32 debugger.
    """
    global _trace32_dbg, _trace32_connected
    
    if _trace32_dbg is not None:
        try:
            # Trace32 connections don't need explicit disconnect
            _trace32_dbg = None
            _trace32_connected = False
            print("[OK] Trace32 connection closed")
        except Exception as e:
            print(f"[Warning] Error closing Trace32: {e}")


