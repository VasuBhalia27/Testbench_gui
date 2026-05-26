"""
Comprehensive Test Framework for SmartBU

This module runs all test suites and generates detailed Excel/PDF reports
that match the master template structure with:
- Test Case ID mapping
- Observed Results (measured values from Trace32)
- Status (PASS/FAIL with clear criteria)
- Remarks (detailed explanation if failed)
"""

import sys
import time
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from AutomationScripts.tests.led_tests import execute_all_led_tests
from AutomationScripts.tests.battery_tests import execute_all_battery_tests
from AutomationScripts.tests.motor_tests import execute_all_motor_tests
from AutomationScripts.tests.eos_tests import execute_all_eos_tests
from AutomationScripts.tests.sg_tests import execute_all_sg_tests
from AutomationScripts.tests.capa_tests import execute_all_capa_tests
from AutomationScripts.tests.nfc_tests import execute_all_nfc_tests
from AutomationScripts.tests.can_tests import execute_all_can_tests
from AutomationScripts.tests.lin_tests import execute_all_lin_tests


class TestOrchestrator:
    """Orchestrates execution of all feature tests."""
    
    def __init__(self):
        self.results = []
        self.start_time = None
        self.end_time = None
    
    def run_all_tests(self) -> List[Dict[str, Any]]:
        """
        Execute all test suites in order.
        
        Returns:
            List of flattened test results (each row is one test case)
        """
        self.start_time = datetime.now()
        print("=" * 80)
        print("SMARTBU COMPREHENSIVE TEST AUTOMATION")
        print(f"Start Time: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 80)
        
        # Run each feature's test suite
        test_suites = [
            ("LED", execute_all_led_tests),
            ("Battery", execute_all_battery_tests),
            ("Motor", execute_all_motor_tests),
            ("EOS", execute_all_eos_tests),
            ("Strain Gauge", execute_all_sg_tests),
            ("Capacitive Sensor", execute_all_capa_tests),
            ("NFC", execute_all_nfc_tests),
            ("CAN", execute_all_can_tests),
            ("LIN", execute_all_lin_tests),
        ]
        
        total_tests = 0
        passed_tests = 0
        failed_tests = 0
        
        for feature_name, test_func in test_suites:
            try:
                print(f"\n-> Running {feature_name} tests...")
                test_results = test_func()
                
                for result in test_results:
                    # Add feature name if not present
                    if "Feature" not in result:
                        result["Feature"] = feature_name
                    
                    self.results.append(result)
                    total_tests += 1
                    
                    if result.get("Status") == "PASS":
                        passed_tests += 1
                    else:
                        failed_tests += 1
                
                print(f"  [OK] {feature_name}: {len(test_results)} tests")
                
            except Exception as e:
                print(f"  [ERROR] {feature_name} failed: {e}")
                # Add error record
                self.results.append({
                    "Feature": feature_name,
                    "TestCaseID": "ERROR",
                    "TestName": f"{feature_name} Execution Error",
                    "Status": "FAIL",
                    "MeasuredValue": None,
                    "Details": str(e)
                })
                failed_tests += 1
        
        self.end_time = datetime.now()
        duration = (self.end_time - self.start_time).total_seconds()
        
        print("\n" + "=" * 80)
        print(f"TEST EXECUTION COMPLETE")
        print(f"Total Tests:   {total_tests}")
        print(f"Passed:        {passed_tests}")
        print(f"Failed:        {failed_tests}")
        print(f"Duration:      {duration:.1f} seconds")
        print("=" * 80)
        
        return self.results
    
    def get_results(self) -> List[Dict[str, Any]]:
        """Get results in a format suitable for Excel reporting."""
        return self.results


def run_all_test_suites_and_report() -> List[Dict[str, Any]]:
    """
    Main entry point: Run all tests and prepare for reporting.
    
    Returns:
        List of test results ready for Excel/PDF output
    """
    orchestrator = TestOrchestrator()
    results = orchestrator.run_all_tests()
    
    # Import and run report generation
    from reports.excel_report import ExcelReportWriter
    from reports.pdf_report import PDFReportWriter
    
    try:
        # Generate Excel report
        excel_writer = ExcelReportWriter()
        excel_file = excel_writer.write_report(results)
        print(f"\n[REPORT] Excel report: {excel_file}")
    except Exception as e:
        print(f"\n[WARN] Excel report generation failed: {e}")
    
    try:
        # Generate PDF report
        pdf_writer = PDFReportWriter()
        pdf_file = pdf_writer.write_report(results)
        print(f"[REPORT] PDF report: {pdf_file}")
    except Exception as e:
        print(f"[WARN] PDF report generation failed: {e}")
    
    return results


if __name__ == "__main__":
    results = run_all_test_suites_and_report()
    print(f"\nTotal results: {len(results)}")
