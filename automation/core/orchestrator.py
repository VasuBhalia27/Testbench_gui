"""
Test Orchestrator

Runs all test suites and collects results.
Designed to be extensible for future test types (BAT, LIN, etc.).
"""

from typing import List, Dict, Any
from tests.led_tests import execute_all_led_tests
import json


class TestOrchestrator:
    """
    Orchestrates execution of all automated tests.
    Collects and aggregates results from all test suites.
    """
    
    def __init__(self):
        """Initialize the orchestrator."""
        self.all_results = []
        self.test_summary = {
            "total_tests": 0,
            "passed": 0,
            "failed": 0
        }
    
    def run_all_tests(self) -> List[Dict[str, Any]]:
        """
        Execute all test suites.
        
        Returns:
            List of test result dictionaries
        """
        self.all_results = []
        
        # Execute LED tests
        print("Running LED tests...")
        led_results = execute_all_led_tests()
        self.all_results.extend(led_results)
        
        # (Future) Execute BAT tests
        # bat_results = execute_all_bat_tests()
        # self.all_results.extend(bat_results)
        
        # (Future) Execute LIN tests
        # lin_results = execute_all_lin_tests()
        # self.all_results.extend(lin_results)
        
        # Calculate summary
        self._calculate_summary()
        
        return self.all_results
    
    def _calculate_summary(self):
        """Calculate test summary statistics."""
        self.test_summary["total_tests"] = len(self.all_results)
        self.test_summary["passed"] = sum(
            1 for test in self.all_results if test["Status"] == "PASS"
        )
        self.test_summary["failed"] = sum(
            1 for test in self.all_results if test["Status"] == "FAIL"
        )
    
    def get_summary(self) -> Dict[str, Any]:
        """
        Get test summary statistics.
        
        Returns:
            Dictionary with summary:
            {
                "total_tests": int,
                "passed": int,
                "failed": int
            }
        """
        return self.test_summary
    
    def get_results(self) -> List[Dict[str, Any]]:
        """
        Get all test results.
        
        Returns:
            List of test result dictionaries
        """
        return self.all_results
    
    def print_results_summary(self):
        """Print a human-readable summary of test results."""
        print("\n" + "=" * 70)
        print("TEST EXECUTION SUMMARY")
        print("=" * 70)
        print(f"Total Tests:  {self.test_summary['total_tests']}")
        print(f"Passed:       {self.test_summary['passed']}")
        print(f"Failed:       {self.test_summary['failed']}")
        print("=" * 70)
        print("\nDetailed Results:")
        print("-" * 70)
        
        for result in self.all_results:
            status_marker = "✓ PASS" if result["Status"] == "PASS" else "✗ FAIL"
            print(f"\n{status_marker} | {result['TestCaseID']}: {result['TestName']}")
            if result["MeasuredValue"] is not None:
                print(f"    Measured: {result['MeasuredValue']}")
            print(f"    Expected: {result['Expected']}")
            if result.get("Details"):
                print(f"    {result['Details']}")
        
        print("\n" + "=" * 70)


def orchestrate_tests() -> Dict[str, Any]:
    """
    Execute all tests and return results.
    
    Returns:
        Dictionary with:
        {
            "results": List[Dict],
            "summary": Dict
        }
    """
    orchestrator = TestOrchestrator()
    orchestrator.run_all_tests()
    
    return {
        "results": orchestrator.get_results(),
        "summary": orchestrator.get_summary()
    }
