"""
SmartBU Comprehensive Test Executor

Unified test execution framework that:
1. Reads test cases from CSV
2. Maps to backend variables
3. Executes tests with proper validation
4. Generates Excel reports with Observed Result, Status, Remarks
"""

import csv
import time
import os
from pathlib import Path
from typing import List, Dict, Any
from datetime import datetime

# Add project to path
import sys
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from backend_adapter.common import read_variable, ensure_connected, send_test_command, set_variable


class TestResult:
    """Standardized test result structure."""
    
    def __init__(self, test_case_id: str, feature: str, test_name: str, 
                 expected: str, measured_value=None, status: str = "FAIL", 
                 remarks: str = ""):
        self.test_case_id = test_case_id
        self.feature = feature
        self.test_name = test_name
        self.expected = expected
        self.measured_value = measured_value
        self.status = status
        self.remarks = remarks
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for Excel reporting."""
        return {
            "TestCaseID": self.test_case_id,
            "Feature": self.feature,
            "TestName": self.test_name,
            "Expected": self.expected,
            "ObservedResult": str(self.measured_value) if self.measured_value is not None else "N/A",
            "Status": self.status,
            "Remarks": self.remarks
        }


class SmartBUTestExecutor:
    """Executes all SmartBU tests with comprehensive variable reading."""
    
    # DID commands for each feature - matches trace32.py TestFunctionCmd enum
    DID_COMMANDS = {
        "LED": 101,                    # TESTFW_GUI_CMD_LED_TEST_e
        "Battery": 102,                # TESTFW_GUI_CMD_BATT_MONITOR_e
        "Motor": 103,                  # TESTFW_GUI_CMD_MOTOR_TEST_e
        "EOS": 104,                    # TESTFW_GUI_CMD_EOS_TEST_e
        "Strain Gauge": 105,           # TEST_GUI_CMD_SG_TEST_e
        "Capacitive Sensor": 106,      # TEST_GUI_CMD_CAPA_TEST_e
        "NFC": 107,                    # TEST_GUI_CMD_NFC_TEST_e
        "CAN": 108,                    # TEST_GUI_CMD_CAN_TEST_e
        "LIN": 109                     # TEST_GUI_CMD_LIN_e
    }
    
    # Feature-to-variables mapping (MUST match gui_main.py output variables)
    # Maps which variable index should be shown as "observed result" in reports
    FEATURE_DISPLAY_INDEX = {
        "LED": 0,                          # Display TestFw_LedVoltage
        "Battery": 1,                      # Display TestFw_AiBatRef (not BatRefStatus)
        "Motor": 0,                        # Display TestFw_MotorCoupledVoltage
        "EOS": 0,                          # Display TestFw_EosDiagVoltage
        "Strain Gauge": 0,                 # Display TestFw_DoPwrSg
        "Capacitive Sensor": 5,            # Display TestFw_CapaUnlockSensorValue
        "NFC": 0,                          # Display TestFw_IsNfcDetectedCard
        "CAN": 0,                          # Display DummyBytes
        "LIN": 0                           # Display TestFw_LinFrameStatus
    }
    
    # Feature-to-variables mapping (MUST match gui_main.py output variables)
    FEATURE_VARIABLES = {
        "LED": {
            "variables": ["TestFw_LedVoltage"],  # From gui_main.py line 516
            "tests": {
                "TC_LED_01": {
                    "name": "LED Voltage Verification (LED Connected)",
                    "expected": "2400-2600 mV",
                    "validation": lambda v: 2400 <= float(v) <= 2600 if v is not None else False
                },
                "TC_LED_03": {
                    "name": "LED Voltage Verification (LED Not Connected)",
                    "expected": "0-100 mV",
                    "validation": lambda v: 0 <= float(v) <= 100 if v is not None else False
                }
            }
        },
        "Battery": {
            "variables": ["TestFw_BatRefStatus", "TestFw_AiBatRef"],  # From gui_main.py line 578
            "tests": {
                "TC_BAT_01": {
                    "name": "Battery Monitor Voltage (12V)",
                    "expected": "11900-12100 mA (AI_BAT_REF)",
                    "validation": lambda v: 11900 <= float(v[1]) <= 12100 if v is not None and len(v) > 1 else False
                }
            }
        },
        "Motor": {
            "variables": ["TestFw_MotorCoupledVoltage", "TestFw_MotorDecoupledVoltage", 
                         "TestFw_MotorCurrentValue", "TestFw_MotorLoadError"],  # From gui_main.py line 664
            "tests": {
                "TC_MOTOR_01": {
                    "name": "Motor Functionality Test",
                    "expected": "CoupledV>0, DecoupledV>0, Current>0, LoadError=0",
                    "validation": lambda vars: (float(vars[0]) > 0 and float(vars[1]) > 0 and float(vars[2]) > 0 and float(vars[3]) == 0) 
                                               if all(v is not None for v in vars) else False
                }
            }
        },
        "EOS": {
            "variables": ["TestFw_EosDiagVoltage", "TestFw_EosPinState", 
                         "TestFw_EosErrorsWithLow", "TestFw_EosErrorsWithHigh"],  # From gui_main.py line 730
            "tests": {
                "TC_EOS_01": {
                    "name": "EOS Diagnostic Voltage Verification",
                    "expected": "2800-3000 mV, No errors",
                    "validation": lambda vars: (2800 <= float(vars[0]) <= 3000 and float(vars[2]) == 0 and float(vars[3]) == 0) 
                                               if all(v is not None for v in vars) else False
                }
            }
        },
        "Strain Gauge": {
            "variables": ["TestFw_DoPwrSg", "TestFw_Sg1PlusOpamp", "TestFw_Sg1MinusOpamp",
                         "TestFw_Sg1Opamp", "TestFw_Sg1Dac", "TestFw_Sg2PlusOpamp",
                         "TestFw_Sg2MinusOpamp", "TestFw_Sg2Opamp", "TestFw_Sg2Dac"],  # From gui_main.py line 833
            "tests": {
                "TC_SG_01": {
                    "name": "Strain Gauge Power & Output Verification",
                    "expected": "Power=1, All OpAmps non-zero",
                    "validation": lambda vars: (float(vars[0]) == 1 and all(float(v) != 0 for v in vars[1:])) 
                                               if all(v is not None for v in vars) else False
                }
            }
        },
        "Capacitive Sensor": {
            "variables": ["TestFw_CapaApproach", "TestFw_CapaLock", "TestFw_CapaUnlock",
                         "TestFw_CapaApproachSensorValue", "TestFw_CapaLockSensorValue",
                         "TestFw_CapaUnlockSensorValue"],  # From gui_main.py line 911
            "tests": {
                "TC_CAPA_01": {
                    "name": "Capacitive Sensor Unlock Detection",
                    "expected": "RawValue 9120-9200, Status=1",
                    "validation": lambda vars: (9120 <= float(vars[5]) <= 9200 and float(vars[2]) == 1) 
                                               if all(v is not None for v in vars) else False
                }
            }
        },
        "NFC": {
            "variables": ["TestFw_IsNfcDetectedCard"],  # From gui_main.py line 966
            "tests": {
                "TC_NFC_01": {
                    "name": "NFC Card Detection Test",
                    "expected": "NFC IRQ = 1 (Card Detected)",
                    "validation": lambda v: float(v) == 1 if v is not None else False
                }
            }
        },
        "CAN": {
            "variables": ["DummyBytes"],  # From gui_main.py line 1022
            "tests": {
                "TC_CAN_01": {
                    "name": "CAN Message Transmission",
                    "expected": "Frames transmitted/received > 0",
                    "validation": lambda v: float(v) > 0 if v is not None else False
                }
            }
        },
        "LIN": {
            "variables": ["TestFw_LinFrameStatus"],  # From trace32.py VARIABLE_UNITS_MAP
            "tests": {
                "TC_LIN_01": {
                    "name": "LIN Frame Transmission/Reception",
                    "expected": "Status = 1 (Active)",
                    "validation": lambda v: float(v) == 1 if v is not None else False
                }
            }
        }
    }

    # Optional prerequisite variable writes to configure firmware state before sending DID
    FEATURE_PRE_COMMANDS = {
        "LED": {
            "TC_LED_01": [("LedTest_LedCanLinRequest", 1)],
            "TC_LED_03": [("LedTest_LedCanLinRequest", 0)],
        },
        "Motor": {
            "TC_MOTOR_01": [("MotorTest_SetGuiMotorActuateRequest", 2), ("MotorTest_SetGuiMotorFreeWheel", 0)],
        },
        "Strain Gauge": {
            "TC_SG_01": [("TestFw_DoPwrSg", 1), ("TestFw_Sg1ToggleGui", 1), ("TestFw_Sg2ToggleGui", 0)],
        }
    }
    
    def __init__(self):
        self.results: List[TestResult] = []
        self.trace32_connected = False
        # Minimum time to wait after triggering a test (seconds)
        self.TEST_CASE_MIN_DURATION = 10.0
        
        # Detect driver vs non-driver variant from environment
        # TRACE32_PRESET: 1 = non-driver (without NFC), 2 = driver (with NFC)
        preset = int(os.environ.get('TRACE32_PRESET', '1'))
        self.is_driver_variant = (preset == 2)
        
        print(f"[DEBUG] Detected variant: {'DRIVER (with NFC)' if self.is_driver_variant else 'NON-DRIVER (without NFC)'}")
    
    def run_all_tests(self) -> List[TestResult]:
        """Execute all tests for all features."""
        print("=" * 80)
        print("SMARTBU COMPREHENSIVE TEST EXECUTION")
        print(f"Start Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 80)
        
        # Try to connect to Trace32
        self.trace32_connected = ensure_connected()
        if self.trace32_connected:
            print("[OK] Connected to Trace32 Debugger")
        else:
            print("[WARNING] Trace32 not connected (tests will return N/A)")
        
        # Execute tests for each feature
        for feature, config in self.FEATURE_VARIABLES.items():
            # Skip NFC and CAN for non-driver variant
            if not self.is_driver_variant and feature in ["NFC", "CAN"]:
                print(f"\n-> Skipping {feature} (non-driver variant selected)")
                continue
            
            print(f"\n-> Testing {feature}...")
            
            # Get the DID command for this feature
            did_cmd = self.DID_COMMANDS.get(feature)
            
            for test_id, test_config in config["tests"].items():
                try:
                    if not self.trace32_connected:
                        # Create failed result if no connection
                        result = TestResult(
                            test_case_id=test_id,
                            feature=feature,
                            test_name=test_config["name"],
                            expected=test_config["expected"],
                            measured_value=None,
                            status="FAIL",
                            remarks="Trace32 not connected"
                        )
                    else:
                        # STEP 1: Execute any prerequisite variable writes for this test
                        pre_cmds = self.FEATURE_PRE_COMMANDS.get(feature, {}).get(test_id, [])
                        for var_name, val in pre_cmds:
                            try:
                                set_variable(var_name, val)
                            except Exception as e:
                                print(f"[WARNING] Failed to set prereq {var_name}={val}: {e}")

                        # STEP 2: Send DID command to trigger firmware test
                        if did_cmd:
                            send_test_command(did_cmd)
                            # Wait long enough for DUT to complete the test and settle
                            print(f"[DEBUG] Waiting {self.TEST_CASE_MIN_DURATION}s for test to complete...")
                            time.sleep(self.TEST_CASE_MIN_DURATION)
                        
                        # STEP 2: Read variables from Trace32 after test executes
                        var_values = []
                        var_values = []
                        try:
                            for var_name in config["variables"]:
                                val = read_variable(var_name)
                                # Treat sentinel values (65535) as invalid/unavailable
                                if isinstance(val, float) and (val >= 65535.0):
                                    print(f"[DEBUG] Variable {var_name} has sentinel value {val}; treating as unavailable")
                                    val = None
                                var_values.append(val)
                        except Exception as e:
                            # If a symbol is not present in the ELF, mark test as SKIPPED
                            msg = str(e).lower()
                            if "symbol not found" in msg or "functionerror" in msg or "symbolnotfounderror" in msg:
                                result = TestResult(
                                    test_case_id=test_id,
                                    feature=feature,
                                    test_name=test_config["name"],
                                    expected=test_config["expected"],
                                    measured_value=None,
                                    status="SKIPPED",
                                    remarks="Symbol not present in loaded ELF"
                                )
                                self.results.append(result)
                                print(f"  [SKIP] {test_id}: SKIPPED (symbol not in ELF)")
                                continue
                            else:
                                raise
                        
                        # Validate
                        all_available = all(v is not None for v in var_values)
                        if not all_available:
                            result = TestResult(
                                test_case_id=test_id,
                                feature=feature,
                                test_name=test_config["name"],
                                expected=test_config["expected"],
                                measured_value=None,
                                status="FAIL",
                                remarks="One or more variables unavailable"
                            )
                        else:
                            # Run validation
                            passed = test_config["validation"](var_values[0] if len(var_values) == 1 else var_values)
                            
                            # Get the correct variable index to display as observed result
                            display_idx = self.FEATURE_DISPLAY_INDEX.get(feature, 0)
                            observed_val = var_values[display_idx] if display_idx < len(var_values) else var_values[0]
                            
                            result = TestResult(
                                test_case_id=test_id,
                                feature=feature,
                                test_name=test_config["name"],
                                expected=test_config["expected"],
                                measured_value=observed_val,
                                status="PASS" if passed else "FAIL",
                                remarks=f"Value={observed_val}" if passed else f"Value={observed_val} not within expected range"
                            )
                    
                    self.results.append(result)
                    status_icon = "[PASS]" if result.status == "PASS" else "[FAIL]"
                    print(f"  {status_icon} {test_id}: {result.status}")
                
                except Exception as e:
                    result = TestResult(
                        test_case_id=test_id,
                        feature=feature,
                        test_name=test_config["name"],
                        expected=test_config["expected"],
                        measured_value=None,
                        status="FAIL",
                        remarks=f"Error: {str(e)}"
                    )
                    self.results.append(result)
                    print(f"  [FAIL] {test_id}: ERROR - {str(e)}")
        
        # Summary
        print("\n" + "=" * 80)
        total = len(self.results)
        passed = sum(1 for r in self.results if r.status == "PASS")
        failed = total - passed
        print(f"Test Summary: {total} tests, {passed} passed, {failed} failed")
        print("=" * 80)
        
        return self.results
    
    def get_results_as_dicts(self) -> List[Dict[str, Any]]:
        """Get results as dictionaries for Excel reporting."""
        return [r.to_dict() for r in self.results]


def main():
    """Execute all tests and display results."""
    executor = SmartBUTestExecutor()
    results = executor.run_all_tests()
    
    # Display results
    for result in results:
        print(f"\n{result.test_case_id} - {result.test_name}")
        print(f"  Feature: {result.feature}")
        print(f"  Expected: {result.expected}")
        print(f"  Observed: {result.measured_value}")
        print(f"  Status: {result.status}")
        print(f"  Remarks: {result.remarks}")
    
    return results


if __name__ == "__main__":
    main()
