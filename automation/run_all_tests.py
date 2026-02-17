#!/usr/bin/env python3
"""
SmartBU Automated Test Suite - Main Entry Point

This is the one-button automation entry point.
Can be called from UI via: subprocess.run(["python", "automation/run_all_tests.py"])

Execution steps:
1. Run all tests via orchestrator
2. Generate Excel report
3. Generate PDF report
4. Print output file paths
5. Exit with appropriate status code
"""

import sys
import os
from pathlib import Path

# Add parent directory to path so imports work
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

from core.orchestrator import orchestrate_tests
from reports.excel_report import generate_excel_report
from reports.pdf_report import generate_pdf_report


def main():
    """
    Main automation entry point.
    
    Returns:
        0 if all tests passed
        1 if any test failed
    """
    print("=" * 70)
    print("SmartBU Automated Test Suite")
    print("=" * 70)
    print()
    
    # Create output directory for reports
    reports_dir = os.path.join(current_dir, "reports", "output")
    os.makedirs(reports_dir, exist_ok=True)
    
    try:
        # Step 1: Run all tests
        print("Running tests...")
        print("-" * 70)
        test_data = orchestrate_tests()
        results = test_data["results"]
        summary = test_data["summary"]
        
        # Step 2: Print results summary
        print_summary(results, summary)
        
        # Step 3: Generate Excel report
        print("\nGenerating Excel report...")
        excel_path = generate_excel_report(results, reports_dir)
        print(f"[OK] Excel report: {excel_path}")
        
        # Step 4: Generate PDF report
        print("Generating PDF report...")
        pdf_path = generate_pdf_report(results, reports_dir)
        print(f"[OK] PDF report: {pdf_path}")
        
        # Step 5: Print output summary
        print("\n" + "=" * 70)
        print("TEST EXECUTION COMPLETE")
        print("=" * 70)
        print(f"\nTotal Tests:  {summary['total_tests']}")
        print(f"Passed:       {summary['passed']}")
        print(f"Failed:       {summary['failed']}")
        print(f"\nReports saved to: {reports_dir}")
        print(f"  Excel: {os.path.basename(excel_path)}")
        print(f"  PDF:   {os.path.basename(pdf_path)}")
        
        # Step 6: Determine exit code
        if summary["failed"] == 0:
            print("\n[OK] All tests passed!")
            return 0
        else:
            print(f"\n[FAILED] {summary['failed']} test(s) failed!")
            return 1
    
    except Exception as e:
        print(f"\n[ERROR] {str(e)}", file=sys.stderr)
        import traceback
        traceback.print_exc(file=sys.stderr)
        return 2


def print_summary(results, summary):
    """
    Print a detailed summary of test results.
    
    Args:
        results: List of test result dictionaries
        summary: Summary statistics dictionary
    """
    print(f"Executed: {summary['total_tests']} tests")
    print(f"Status:   {summary['passed']} passed, {summary['failed']} failed")
    print()
    
    for result in results:
        status_marker = "[PASS]" if result["Status"] == "PASS" else "[FAIL]"
        print(f"  {status_marker} | {result['TestCaseID']}: {result['TestName']}")
        if result.get("Details"):
            print(f"          {result['Details']}")


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
