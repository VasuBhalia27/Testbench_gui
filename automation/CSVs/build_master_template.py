"""
Tool to build Master Excel Template from CSV test cases

Converts CSVs into a production-ready Excel template with:
- All test cases from each feature
- Columns: S.No, Test Case ID, Feature, Test Name, Pre-Action, Test Steps, 
          Expected Result, Post-Action, Observed Result, Status, Remarks
- Proper formatting and alignment
"""

import csv
import os
from pathlib import Path
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

def read_csv_with_proper_parsing(csv_path):
    """Read CSV safely, handling various encodings and formats."""
    try:
        with open(csv_path, 'r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            rows = []
            for row in reader:
                # Skip empty rows
                if not any(row.values()):
                    continue
                rows.append(row)
            return rows
    except Exception as e:
        print(f"Error reading {csv_path}: {e}")
        return []

def build_master_template():
    """Build master Excel template from all CSVs."""
    csv_dir = Path(__file__).parent  # automation/CSVs
    
    # Feature mapping: CSV filename -> Feature name
    features = {
        'LED.csv': 'LED',
        'Battery.csv': 'Battery',
        'Motor.csv': 'Motor',
        'EOS.csv': 'EOS',
        'SG.csv': 'Strain Gauge',  # SG.csv contains Strain Gauge tests
        'CAPA.csv': 'Capacitive Sensor',
        'NFC.csv': 'NFC',
        'CAN.csv': 'CAN',
        'LIN.csv': 'LIN'
    }
    
    wb = Workbook()
    ws = wb.active
    ws.title = "Test Results"
    
    # Define styles
    header_fill = PatternFill(start_color="1F4E78", end_color="1F4E78", fill_type="solid")
    header_font = Font(bold=True, color="FFFFFF", size=11)
    data_font = Font(size=10)
    center_align = Alignment(horizontal="center", vertical="top", wrap_text=True)
    left_align = Alignment(horizontal="left", vertical="top", wrap_text=True)
    thin_border = Border(
        left=Side(style='thin'),
        right=Side(style='thin'),
        top=Side(style='thin'),
        bottom=Side(style='thin')
    )
    
    # Headers
    headers = [
        "S.No",
        "Test Case ID",
        "Feature",
        "Test Case Name",
        "Pre-Action",
        "Test Steps",
        "Expected Result",
        "Post Action",
        "Observed Result",
        "Status",
        "Remarks"
    ]
    
    ws.append(headers)
    
    # Format header row
    for col_num, header in enumerate(headers, 1):
        cell = ws.cell(row=1, column=col_num)
        cell.fill = header_fill
        cell.font = header_font
        cell.alignment = center_align
        cell.border = thin_border
    
    # Set column widths
    col_widths = [6, 15, 18, 30, 25, 30, 30, 20, 25, 12, 25]
    for col_num, width in enumerate(col_widths, 1):
        ws.column_dimensions[get_column_letter(col_num)].width = width
    
    # Add test cases from each CSV
    row_num = 2
    serial_no = 1
    
    for csv_file, feature_name in features.items():
        csv_path = csv_dir / csv_file
        
        if not csv_path.exists():
            print(f"Warning: {csv_file} not found")
            continue
        
        print(f"Processing {csv_file}...")
        rows = read_csv_with_proper_parsing(csv_path)
        
        for record in rows:
            # Extract data from CSV columns
            test_case_id = record.get('Test Case ID', '').strip()
            test_name = record.get('Test Case Name', '').strip()
            pre_action = record.get('Pre Action', '').strip()
            test_steps = record.get('Test Steps', '').strip()
            expected = record.get('Expected Result', '').strip()
            post_action = record.get('Post Action', '').strip()
            
            if not test_case_id:  # Skip if no test case ID
                continue
            
            # Data for the row
            row_data = [
                serial_no,
                test_case_id,
                feature_name,
                test_name,
                pre_action,
                test_steps,
                expected,
                post_action,
                "",  # Observed Result (empty for now)
                "",  # Status (empty for now)
                ""   # Remarks (empty for now)
            ]
            
            ws.append(row_data)
            
            # Format data row
            for col_num, value in enumerate(row_data, 1):
                cell = ws.cell(row=row_num, column=col_num)
                cell.font = data_font
                cell.border = thin_border
                
                # Apply alignment based on column
                if col_num == 10:  # Status column - center
                    cell.alignment = center_align
                else:
                    cell.alignment = left_align
                
                # Observed Result and Status should have conditional formatting
                if col_num in [9, 10, 11]:  # Observed Result, Status, Remarks
                    cell.fill = PatternFill(start_color="FFF2CC", end_color="FFF2CC", fill_type="solid")
            
            row_num += 1
            serial_no += 1
    
    # Save the workbook
    output_path = csv_dir.parent / "config" / "SmartBU_Master_Template.xlsx"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    wb.save(output_path)
    
    print(f"\n[OK] Master template created: {output_path}")
    print(f"   Total test cases: {serial_no - 1}")
    
    return output_path

if __name__ == "__main__":
    build_master_template()
