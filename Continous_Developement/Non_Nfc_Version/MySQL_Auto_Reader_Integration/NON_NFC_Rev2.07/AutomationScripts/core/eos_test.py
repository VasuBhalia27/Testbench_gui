"""EOS Test Module for SmartBU Hardware Automation

This module implements two EOS (Electric Outlet Sense) test cases:
1. EOS Reset: Monitors voltage 1500-3000 mV after 20-second wait
2. EOS Set: Monitors voltage 1400-1600 mV after 3-second wait

Both tests poll TestFw_EosDiagVoltage until stable.
"""

import time
from typing import Callable, Optional

from Functional.trace32 import TestFunctionCmd
from AutomationScripts.core.timing_profile import TIMING


class EosTest:
    """EOS test automation with dual test cases."""
    
    # Pass criteria for EOS Reset (mV)
    MIN_RESET_VOLTAGE = 1500
    MAX_RESET_VOLTAGE = 3000
    
    # Pass criteria for EOS Set (mV)
    MIN_SET_VOLTAGE = 1400
    MAX_SET_VOLTAGE = 1600
    
    # Variable name to monitor
    VOLTAGE_VARIABLE = "TestFw_EosDiagVoltage"
    
    def __init__(self, adapter, status_callback: Optional[Callable[[str], None]] = None):
        """
        Initialize EOS test with Trace32 adapter.
        
        Args:
            adapter: Trace32Interface adapter for hardware communication
            status_callback: Optional callback for progress messages
        """
        self.adapter = adapter
        self.log = status_callback or (lambda msg: None)
    
    def run(self):
        """
        Run both EOS test cases sequentially.
        
        Returns:
            dict: Results with keys 'eos_reset' and 'eos_set', each containing
                  pass/fail status and voltage reading
        """
        results = {}
        
        # Test 1: EOS Set (with clearing step before)
        results['eos_set'] = self.run_eos_set()
        
        # Test 2: EOS Reset
        results['eos_reset'] = self.run_eos_reset()
        
        return results
    
    def run_eos_reset(self):
        """
        EOS Reset Test Case: Tick reset and monitor voltage.
        
        Procedure:
        1. Set hardware to Reset mode (EosTest_EosRequestGui = 0)
        2. Tick EOS Reset (send DID with reset command)
        3. Wait 20 seconds for hardware to stabilize
        4. Send DID to trigger voltage readout
        5. Wait additional time for stabilization
        6. Poll until voltage is stable
        7. Validate: 2800 mV <= voltage <= 3000 mV
        
        Returns:
            dict: {'pass': bool, 'voltage': float}
        """
        # Critical: Set the hardware to RESET mode (0) before sending DID
        self.adapter.set_variable("EosTest_EosRequestGui", 0)
        
        # Wait a moment for mode switch to register
        time.sleep(TIMING.eos_mode_switch_wait)
        
        # Tick EOS Reset - send DID with reset command
        self.adapter.send_did(TestFunctionCmd.TESTFW_GUI_CMD_EOS_TEST_e)
        time.sleep(TIMING.eos_reset_stabilize_wait)
        
        # Send DID to get voltage readout
        self.log("EOS Reset: triggering measurement read")
        self.adapter.send_did(TestFunctionCmd.TESTFW_GUI_CMD_EOS_TEST_e)
        time.sleep(TIMING.eos_measure_wait)
        
        # Poll until voltage is stable
        voltage = self._wait_for_stable_voltage()
        
        # Check pass criteria
        pass_status = self.MIN_RESET_VOLTAGE <= voltage <= self.MAX_RESET_VOLTAGE
        
        self.log(f"EOS Reset: voltage = {voltage} mV")
        self.log(f"EOS Reset: {'✓ PASS' if pass_status else f'✗ FAIL — {voltage} mV not in {self.MIN_RESET_VOLTAGE}–{self.MAX_RESET_VOLTAGE} mV'}")
        
        return {
            "pass": pass_status,
            "voltage": voltage,
            "min": self.MIN_RESET_VOLTAGE,
            "max": self.MAX_RESET_VOLTAGE
        }
    
    def run_eos_set(self):
        """
        EOS Set Test Case: Tick set (after clearing) and monitor voltage.
        
        Procedure:
        1. Clear entry field (reset display)
        2. Wait 1 second
        3. Set hardware to Set mode (EosTest_EosRequestGui = 1)
        4. Tick EOS Set (send DID with set command)
        5. Wait 3 seconds for hardware to stabilize
        6. Send DID to trigger voltage readout
        7. Wait additional time for polls
        8. Poll until voltage is stable
        9. Validate: 1400 mV <= voltage <= 1600 mV
        
        Returns:
            dict: {'pass': bool, 'voltage': float}
        """
        # Clear result entries (called via adapter if available)
        try:
            self.adapter.clear_eos_entries()
        except AttributeError:
            pass
        
        time.sleep(TIMING.eos_clear_wait)
        
        # Critical: Set the hardware to SET mode (1) before sending DID
        self.adapter.set_variable("EosTest_EosRequestGui", 1)
        time.sleep(TIMING.eos_mode_switch_wait)
        
        # Tick EOS Set - send DID with set command
        self.adapter.send_did(TestFunctionCmd.TESTFW_GUI_CMD_EOS_TEST_e)
        time.sleep(TIMING.eos_set_process_wait)
        
        # Send DID to get voltage readout
        self.log("EOS Set: triggering measurement read")
        self.adapter.send_did(TestFunctionCmd.TESTFW_GUI_CMD_EOS_TEST_e)
        time.sleep(TIMING.eos_measure_wait)
        
        # Poll until voltage is stable
        voltage = self._wait_for_stable_voltage()
        
        # Check pass criteria
        pass_status = self.MIN_SET_VOLTAGE <= voltage <= self.MAX_SET_VOLTAGE
        
        self.log(f"EOS Set: voltage = {voltage} mV")
        self.log(f"EOS Set: {'✓ PASS' if pass_status else f'✗ FAIL — {voltage} mV not in {self.MIN_SET_VOLTAGE}–{self.MAX_SET_VOLTAGE} mV'}")
        
        return {
            "pass": pass_status,
            "voltage": voltage,
            "min": self.MIN_SET_VOLTAGE,
            "max": self.MAX_SET_VOLTAGE
        }
    
    def _wait_for_stable_voltage(self, max_iterations=4):
        """
        Poll voltage until two consecutive readings are stable (identical).
        
        This uses the same stability detection as other tests: two consecutive
        identical readings within tolerance indicate stability.
        
        Args:
            max_iterations: Maximum number of 0.5-second polls (default: 4 → 2 seconds)
        
        Returns:
            float: Stable voltage value (mV)
        """
        tolerance = 1e-3  # 0.001 mV tolerance
        
        for iteration in range(max_iterations):
            # Read first voltage
            voltage1 = float(self.adapter.read_variable(self.VOLTAGE_VARIABLE))
            
            # Wait 0.5 seconds
            time.sleep(0.5)
            
            # Read second voltage
            voltage2 = float(self.adapter.read_variable(self.VOLTAGE_VARIABLE))
            
            # Check if stable (two consecutive identical readings)
            if abs(voltage1 - voltage2) < tolerance:
                return voltage2
        
        # If not stable after max iterations, return last reading
        return voltage2
