"""
Excel Report Writer for SmartBU Test Results

Generates production-ready Excel reports with:
- Master template structure (Test Case ID, Feature, Test Name, etc.)
- Observed Result column (populated from test execution)
- Status column (PASS/FAIL)
- Remarks column (detailed explanation of results)
- Professional formatting and alignment
- Per-feature worksheets with consistent formatting
"""

import os
import re
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any

from openpyxl import Workbook, load_workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter


class SmartBUExcelReportWriter:
    """Generates comprehensive Excel reports matching the master template."""
    
    # Define exact column structure matching requirements
    HEADERS = [
        "S. No.",
        "Test Case ID",
        "Test Case Name",
        "Pre Action",
        "Test Steps",
        "Expected Result",
        "Post Action",
        "Observed Result",
        "Status",
        "Remark"
    ]

    COLUMN_WIDTHS = {
        "S. No.": 6,
        "Test Case ID": 16,
        "Test Case Name": 40,
        "Pre Action": 30,
        "Test Steps": 40,
        "Expected Result": 28,
        "Post Action": 20,
        "Observed Result": 20,
        "Status": 12,
        "Remark": 45
    }
    
    # Color scheme - production ready
    COLORS = {
        "header_bg": "1F4E78",      # Dark blue
        "header_fg": "FFFFFF",      # White
        "pass_bg": "70AD47",        # Green
        "pass_fg": "FFFFFF",        # White
        "fail_bg": "E74C3C",        # Red
        "fail_fg": "FFFFFF",        # White
        "summary_header": "2E75B6"  # Medium blue
    }
    
    # SKIPPED color
    SKIPPED_BG = "D9D9D9"
    SKIPPED_FG = "000000"
    
    def __init__(self):
        self.out_dir = Path(__file__).parent.parent / "reports" / "output"
        self.out_dir.mkdir(parents=True, exist_ok=True)
    
    def write_report(self, test_results: List[Dict[str, Any]]) -> str:
        """
        Write test results to Excel file with production-ready formatting.
        
        Structure:
        - Summary sheet (first)
        - Per-feature sheets (alphabetically sorted)
        
        Args:
            test_results: List of test result dictionaries from comprehensive executor
        
        Returns:
            Path to generated Excel file
        """
        # Create workbook
        wb = Workbook()
        wb.remove(wb.active)  # Remove default sheet
        
        # Define styles
        header_fill = PatternFill(start_color=self.COLORS["header_bg"], 
                                  end_color=self.COLORS["header_bg"], 
                                  fill_type="solid")
        header_font = Font(bold=True, color=self.COLORS["header_fg"], size=12)
        
        pass_fill = PatternFill(start_color=self.COLORS["pass_bg"], 
                               end_color=self.COLORS["pass_bg"], 
                               fill_type="solid")
        pass_font = Font(bold=True, color=self.COLORS["pass_fg"], size=10)
        
        fail_fill = PatternFill(start_color=self.COLORS["fail_bg"], 
                               end_color=self.COLORS["fail_bg"], 
                               fill_type="solid")
        fail_font = Font(bold=True, color=self.COLORS["fail_fg"], size=10)
        
        center_align = Alignment(horizontal="center", vertical="center", wrap_text=True)
        left_align = Alignment(horizontal="left", vertical="top", wrap_text=True)
        
        thin_border = Border(
            left=Side(style='thin', color="000000"),
            right=Side(style='thin', color="000000"),
            top=Side(style='thin', color="000000"),
            bottom=Side(style='thin', color="000000")
        )
        
        # Calculate summary statistics
        total_tests = len(test_results)
        passed_tests = sum(1 for r in test_results if r.get("Status") == "PASS")
        failed_tests = total_tests - passed_tests
        pass_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        now = datetime.now().astimezone()
        
        # ==== CREATE SUMMARY SHEET ====
        ws_summary = wb.create_sheet("Summary", 0)
        
        # Title
        ws_summary["A1"] = "SmartBU Comprehensive Test Report"
        ws_summary["A1"].font = Font(bold=True, size=16, color=self.COLORS["header_fg"])
        ws_summary["A1"].fill = PatternFill(start_color=self.COLORS["summary_header"], 
                                            end_color=self.COLORS["summary_header"], 
                                            fill_type="solid")
        ws_summary.merge_cells("A1:F1")
        ws_summary["A1"].alignment = center_align
        ws_summary.row_dimensions[1].height = 25
        
        # Summary table
        summary_items = [
            ("Total Tests:", total_tests),
            ("Passed Tests:", passed_tests),
            ("Failed Tests:", failed_tests),
            ("Pass Rate:", f"{pass_rate:.1f}%"),
            ("Test Date:", now.strftime("%Y-%m-%d %H:%M:%S")),
            ("Timezone:", now.strftime("%Z"))
        ]
        
        row = 3
        for label, value in summary_items:
            ws_summary[f"A{row}"] = label
            ws_summary[f"B{row}"] = value
            ws_summary[f"A{row}"].font = Font(bold=True, size=11)
            ws_summary[f"A{row}"].fill = PatternFill(start_color="E7E6E6", 
                                                      end_color="E7E6E6", 
                                                      fill_type="solid")
            ws_summary[f"B{row}"].font = Font(size=11)
            ws_summary[f"A{row}"].alignment = left_align
            ws_summary[f"B{row}"].alignment = left_align
            row += 1
        
        ws_summary.column_dimensions["A"].width = 20
        ws_summary.column_dimensions["B"].width = 30
        
        # ==== GROUP BY FEATURE (canonical names) AND CREATE PER-FEATURE SHEETS ====
        features_dict = {}
        for result in test_results:
            raw_feature = result.get("Feature", "Other")
            feature = self._canonical_feature_name(raw_feature)
            if feature not in features_dict:
                features_dict[feature] = []
            features_dict[feature].append(result)
        
        # Create sheet for each feature in a sensible order (summary-first, then expected features)
        preferred_order = ["Battery", "Capacitive Sensor", "EOS", "LED", "LIN", "Motor", "Strain Gauge", "CAN", "NFC", "Other"]
        remaining = sorted([f for f in features_dict.keys() if f not in preferred_order])
        ordered_features = [f for f in preferred_order if f in features_dict] + remaining

        # Create sheet for each feature (in ordered_features)
        # Track seen TestCaseIDs to avoid duplicates in final report
        seen_ids = {}
        for feature in ordered_features:
            feature_results = features_dict[feature]
            ws = wb.create_sheet(feature)
            
            # Add headers row with formatting
            for col_num, header in enumerate(self.HEADERS, 1):
                cell = ws.cell(row=1, column=col_num)
                cell.value = header
                cell.fill = header_fill
                cell.font = header_font
                cell.alignment = center_align
                cell.border = thin_border
            
            ws.row_dimensions[1].height = 20
            
            # Set column widths
            for col_num, header in enumerate(self.HEADERS, 1):
                col_letter = get_column_letter(col_num)
                ws.column_dimensions[col_letter].width = self.COLUMN_WIDTHS[header]
            
            # Add test results rows
            row_num = 2
            # Per-feature index used for synthetic TestCaseID when missing
            feature_index = 1
            for result in feature_results:
                # Determine observed value from multiple possible keys
                observed_raw = None
                for k in ("ObservedResult", "Observed", "MeasuredStr", "MeasuredValue", "Measured", "Value"):
                    if k in result and result[k] not in (None, ""):
                        observed_raw = result[k]
                        break

                # If measured value is numeric but no formatted string provided, use numeric
                if observed_raw is None and "MeasuredValue" in result and result.get("MeasuredValue") is not None:
                    observed_raw = result.get("MeasuredValue")

                # Format observed result based on feature type
                observed_formatted = self._format_observed_result(feature, observed_raw)

                # Determine expected value from common keys
                expected_val = result.get("Expected") or result.get("ExpectedResult") or ""

                # Determine remarks: prefer explicit Remarks, else use Details or auto message
                remarks = result.get("Remarks") or result.get("Details") or result.get("Log") or ""
                if not remarks and observed_raw is not None and expected_val:
                    # Add a simple remark if value outside range was computed by test (some tests include that in Details)
                    pass

                # Ensure TestCaseID is present and unique in the spreadsheet
                original_id = (result.get("TestCaseID") or "").strip()
                if not original_id:
                    base_id = f"TC_{feature.upper().replace(' ', '')}_{feature_index:03d}"
                    feature_index += 1
                else:
                    base_id = original_id

                # If we've already used this ID, append a numeric suffix to make it unique
                if base_id in seen_ids:
                    seen_ids[base_id] += 1
                    test_id = f"{base_id}_{seen_ids[base_id]}"
                else:
                    seen_ids[base_id] = 1
                    test_id = base_id

                # Map fields into the testcase template columns
                pre_action = result.get("PreAction") or result.get("Pre Action") or result.get("Pre") or ""
                test_steps = result.get("TestSteps") or result.get("Test Steps") or result.get("Steps") or ""
                post_action = result.get("PostAction") or result.get("Post Action") or result.get("Post") or ""

                row_data = [
                    row_num - 1,          # S. No.
                    test_id,
                    result.get("TestName", ""),
                    pre_action,
                    test_steps,
                    expected_val,
                    post_action,
                    observed_formatted,
                    result.get("Status", "FAIL"),
                    remarks
                ]
                
                # Append row
                ws.append(row_data)
                
                # Format each cell in row
                for col_num, value in enumerate(row_data, 1):
                    cell = ws.cell(row=row_num, column=col_num)
                    cell.border = thin_border
                    cell.font = Font(size=10)
                    
                    # Column-specific formatting for the template
                    if col_num == 1:  # S. No. - center
                        cell.alignment = center_align
                    elif col_num == 2:  # Test Case ID - center
                        cell.alignment = center_align
                    elif col_num == 3:  # Test Case Name - left
                        cell.alignment = left_align
                    elif col_num in (4, 5, 6, 7, 10):  # Pre Action, Test Steps, Expected, Post Action, Remark - left
                        cell.alignment = left_align
                    elif col_num == 8:  # Observed Result - center
                        cell.alignment = center_align
                    elif col_num == 9:  # Status - center with color
                        cell.alignment = center_align
                        if value == "PASS":
                            cell.fill = pass_fill
                            cell.font = pass_font
                        elif value == "FAIL":
                            cell.fill = fail_fill
                            cell.font = fail_font
                        elif value == "SKIPPED":
                            cell.fill = PatternFill(start_color=self.SKIPPED_BG, end_color=self.SKIPPED_BG, fill_type="solid")
                            cell.font = Font(bold=True, color=self.SKIPPED_FG, size=10)
                    
                    ws.row_dimensions[row_num].height = 18
                row_num += 1

        # (No per-test detailed sheets: all test cases for a feature are listed
        #  in the corresponding per-feature sheet as requested.)
        
        # Save workbook with timezone-aware filename
        filename = f"SmartBU_TestResults_{now.strftime('%Y%m%d_%H%M%S%z')}.xlsx"
        filepath = self.out_dir / filename
        
        wb.save(filepath)
        
        # Print summary
        print(f"\n[REPORT] Excel report generated: {filepath}")
        print(f"   Total tests: {total_tests}")
        print(f"   Passed: {passed_tests}")
        print(f"   Failed: {failed_tests}")
        print(f"   Pass Rate: {pass_rate:.1f}%")
        print(f"   Features: {', '.join(sorted(features_dict.keys()))}")
        
        return str(filepath)
    
    def _format_observed_result(self, feature: str, observed: Any) -> str:
        """Format observed result based on feature type and data type."""
        if observed is None or observed == "N/A":
            return "N/A"
        
        try:
            observed_str = str(observed)
            
            # Handle LED measurements (convert to millivolts if needed)
            if "LED" in feature.upper():
                # Check if already has unit
                if "mV" in observed_str or "mv" in observed_str:
                    match = re.search(r"([-+]?[0-9]*\.?[0-9]+)\s*m?V", observed_str, re.I)
                    if match:
                        return f"{int(round(float(match.group(1))))}" if "m" not in observed_str.lower() else match.group(1)
                else:
                    # Try to parse as float and convert
                    num = float(re.findall(r"[-+]?[0-9]*\.?[0-9]+", observed_str)[0])
                    if 0 < num < 10:  # Likely in volts, convert to mV
                        return f"{int(round(num * 1000))}"
                    return f"{num:.0f}"
            
            # Handle numeric values
            try:
                num_val = float(observed_str.split()[0])
                if "." in observed_str:
                    return f"{num_val:.2f}".rstrip('0').rstrip('.')
                else:
                    return f"{num_val:.0f}"
            except (ValueError, IndexError):
                return observed_str
        
        except Exception:
            return str(observed)

    def _canonical_feature_name(self, raw: str) -> str:
        """Map variant/raw feature names to canonical sheet names."""
        if not raw:
            return "Other"
        s = str(raw).strip().lower()
        if "led" in s:
            return "LED"
        if "bat" in s or "battery" in s:
            return "Battery"
        if "motor" in s:
            return "Motor"
        if "eos" in s:
            return "EOS"
        if "sg" in s or "strain" in s:
            return "Strain Gauge"
        if "capa" in s or "cap" in s or "capacitive" in s:
            return "Capacitive Sensor"
        if "lin" in s:
            return "LIN"
        if "can" in s:
            return "CAN"
        if "nfc" in s:
            return "NFC"
        return raw



def create_from_comprehensive_executor():
    """Helper function to run tests and generate report."""
    from comprehensive_test_executor import SmartBUTestExecutor
    
    executor = SmartBUTestExecutor()
    results = executor.run_all_tests()
    
    writer = SmartBUExcelReportWriter()
    excel_file = writer.write_report(executor.get_results_as_dicts())
    
    return excel_file


if __name__ == "__main__":
    create_from_comprehensive_executor()
