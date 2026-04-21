"""
LED Test Cases

Test cases for LED voltage verification.
Depends ONLY on the backend adapter, which returns stable output variables.
"""

from AutomationScripts.backend_adapter.led_service import read_led_voltage
from typing import Dict, Any


class LEDTestSuite:
    """
    Collection of LED-related test cases.
    Each test returns a structured result dictionary.
    """
    
    @staticmethod
    def tc_led_01() -> Dict[str, Any]:
        """
        Test Case: TC_LED_01 - LED Voltage Verification (LED Connected)
        
        Verify LED voltage when Non-Driver PCB is connected to the PC.
        Expected range: 2.76 V to 3.83 V
        
        Returns:
            Dictionary with test result:
            {
                "TestCaseID": "TC_LED_01",
                "TestName": "LED Voltage Verification (LED Connected)",
                "MeasuredValue": <float>,
                "Expected": "2.76 V to 3.83 V",
                "Status": "PASS" | "FAIL",
                "Details": "..."
            }
        """
        test_id = "TC_LED_01"
        test_name = "LED Voltage Verification (LED Connected)"
        
        # Acceptance criteria
        min_voltage = 2.76
        max_voltage = 3.83
        
        try:
            # Read from backend adapter (returns stable output variables)
            backend_result = read_led_voltage(test_id)
            measured_voltage = backend_result["TestFw_LedVoltage"]
            
            # Validate against acceptance criteria
            if min_voltage <= measured_voltage <= max_voltage:
                status = "PASS"
                details = f"Voltage {measured_voltage:.3f} V is within acceptable range"
            else:
                status = "FAIL"
                details = f"Voltage {measured_voltage:.3f} V is outside acceptable range [{min_voltage}, {max_voltage}]"
            
            return {
                "TestCaseID": test_id,
                "TestName": test_name,
                "MeasuredValue": measured_voltage,
                "Expected": f"{min_voltage} V to {max_voltage} V",
                "Status": status,
                "Details": details
            }
        
        except Exception as e:
            return {
                "TestCaseID": test_id,
                "TestName": test_name,
                "MeasuredValue": None,
                "Expected": f"{min_voltage} V to {max_voltage} V",
                "Status": "FAIL",
                "Details": f"Error: {str(e)}"
            }
    
    @staticmethod
    def tc_led_03() -> Dict[str, Any]:
        """
        Test Case: TC_LED_03 - LED Voltage Verification (LED Not Connected)
        
        Verify LED voltage when Non-Driver PCB is not connected.
        Expected range: 0.0 V to 0.1 V (near zero — no current path)
        
        Returns:
            Dictionary with test result
        """
        test_id = "TC_LED_03"
        test_name = "LED Voltage Verification (LED Not Connected)"
        
        # Acceptance criteria: disconnected LED has no current path so voltage
        # should be at or near 0.
        min_voltage = 0.0
        max_voltage = 0.1
        
        try:
            backend_result = read_led_voltage(test_id)
            measured_voltage = backend_result["TestFw_LedVoltage"]
            
            if min_voltage <= measured_voltage <= max_voltage:
                status = "PASS"
                details = f"Voltage {measured_voltage:.3f} V is within acceptable range"
            else:
                status = "FAIL"
                details = f"Voltage {measured_voltage:.3f} V is outside acceptable range [{min_voltage}, {max_voltage}]"
            
            return {
                "TestCaseID": test_id,
                "TestName": test_name,
                "MeasuredValue": measured_voltage,
                "Expected": f"{min_voltage} V to {max_voltage} V",
                "Status": status,
                "Details": details
            }
        
        except Exception as e:
            return {
                "TestCaseID": test_id,
                "TestName": test_name,
                "MeasuredValue": None,
                "Expected": f"{min_voltage} V to {max_voltage} V",
                "Status": "FAIL",
                "Details": f"Error: {str(e)}"
            }
    
    @staticmethod
    def tc_led_03_shorted() -> Dict[str, Any]:
        """
        Test Case: TC_LED_03_SHORTED - LED Voltage Verification (Connection Shorted)
        
        Verify LED voltage when LED connection is shorted.
        Expected range: 0.0 V to 0.1 V (shorted connection pulls line to ground)
        
        Returns:
            Dictionary with test result
        """
        test_id = "TC_LED_03_SHORTED"
        test_name = "LED Voltage Verification (Connection Shorted)"
        
        # Acceptance criteria: a shorted LED connection clamps the line close
        # to 0 V.
        min_voltage = 0.0
        max_voltage = 0.1
        
        try:
            backend_result = read_led_voltage(test_id)
            measured_voltage = backend_result["TestFw_LedVoltage"]
            
            if min_voltage <= measured_voltage <= max_voltage:
                status = "PASS"
                details = f"Voltage {measured_voltage:.3f} V is within acceptable range"
            else:
                status = "FAIL"
                details = f"Voltage {measured_voltage:.3f} V is outside acceptable range [{min_voltage}, {max_voltage}]"
            
            return {
                "TestCaseID": test_id,
                "TestName": test_name,
                "MeasuredValue": measured_voltage,
                "Expected": f"{min_voltage} V to {max_voltage} V",
                "Status": status,
                "Details": details
            }
        
        except Exception as e:
            return {
                "TestCaseID": test_id,
                "TestName": test_name,
                "MeasuredValue": None,
                "Expected": f"{min_voltage} V to {max_voltage} V",
                "Status": "FAIL",
                "Details": f"Error: {str(e)}"
            }


def execute_all_led_tests() -> list:
    """
    Execute all LED test cases.
    
    Returns:
        List of test result dictionaries
    """
    test_suite = LEDTestSuite()
    results = [
        test_suite.tc_led_01(),
        test_suite.tc_led_03(),
        test_suite.tc_led_03_shorted(),
    ]
    return results
