# SmartBU Automation Framework

A clean, headless automation framework for the SmartBU embedded test system.

## Architecture Overview

```
automation/
├── contracts/                    # Test contract definitions
│   └── led.yaml                 # Defines stable test contracts for LED tests
├── backend_adapter/             # Backend integration layer
│   ├── __init__.py
│   └── led_service.py           # Adapter to call backend LED DID logic
├── tests/                       # Test case implementations
│   ├── __init__.py
│   └── led_tests.py            # LED test cases
├── core/                        # Core automation logic
│   ├── __init__.py
│   └── orchestrator.py         # Orchestrates all test execution
├── reports/                     # Report generation
│   ├── __init__.py
│   ├── excel_report.py         # Excel report generator
│   └── pdf_report.py           # PDF report generator
├── run_all_tests.py            # Main entry point
└── __init__.py
```

## Key Design Principles

### 1. Automation Independence
- **NO UI imports** (no tkinter, PyQt, etc.)
- **NO direct hardware calls** (no VISA, Trace32, CAN/LIN drivers)
- **Tests depend ONLY on backend adapter**

### 2. Stable Contracts
All automation depends on stable output variable names confirmed with backend team:
- `TestFw_LedVoltage` - LED voltage measurement

These variable names are GUARANTEED STABLE and will not change.

### 3. Backend Adapter Pattern
```python
# Backend adapter returns stable dictionaries:
backend_result = read_led_voltage("TC_LED_01")
# Returns: {"TestFw_LedVoltage": 3.25}

# Backend team can replace implementation without breaking tests:
# - Originally: mock values
# - Later: real VISA/Trace32 calls
# - Later: CAN/LIN protocol
```

### 4. Test Result Structure
All tests return consistent dictionaries:
```python
{
    "TestCaseID": "TC_LED_01",
    "TestName": "LED Voltage Verification (LED Connected)",
    "MeasuredValue": 3.25,
    "Expected": "2.76 V to 3.83 V",
    "Status": "PASS",  # or "FAIL"
    "Details": "Voltage is within acceptable range"
}
```

## Usage

### Run All Tests (One-Button Automation)
```bash
python automation/run_all_tests.py
```

**Output:**
- Console: Test summary with pass/fail status
- Excel report: `SmartBU_TestResults_YYYYMMDD_HHMMSS.xlsx`
- PDF report: `SmartBU_TestResults_YYYYMMDD_HHMMSS.pdf`
- Exit code: 0 (all passed) or 1 (any failed)

### From UI (Example)
```python
import subprocess
result = subprocess.run(["python", "automation/run_all_tests.py"])
if result.returncode == 0:
    print("All tests passed!")
else:
    print("Some tests failed - check reports")
```

## Extending to New Test Types

To add a new test type (e.g., BAT, LIN), follow this pattern:

### 1. Create Contract (`contracts/bat.yaml`)
```yaml
bat_tests:
  - test_id: "TC_BAT_001"
    test_name: "Battery Voltage Test"
    output_variables:
      TestFw_BatteryVoltage:
        type: "float"
        unit: "V"
    acceptance_criteria:
      min_voltage: 10.0
      max_voltage: 14.0
```

### 2. Create Backend Adapter (`backend_adapter/bat_service.py`)
```python
def read_battery_voltage(test_id: str) -> dict:
    # Backend implements actual hardware interaction
    return {"TestFw_BatteryVoltage": 12.5}
```

### 3. Create Test Cases (`tests/bat_tests.py`)
```python
class BATTestSuite:
    @staticmethod
    def tc_bat_001() -> Dict[str, Any]:
        # Call adapter and validate
        result = read_battery_voltage("TC_BAT_001")
        voltage = result["TestFw_BatteryVoltage"]
        status = "PASS" if 10.0 <= voltage <= 14.0 else "FAIL"
        return {"TestCaseID": "TC_BAT_001", ...}

def execute_all_bat_tests() -> list:
    return [BATTestSuite.tc_bat_001(), ...]
```

### 4. Add to Orchestrator (`core/orchestrator.py`)
```python
def run_all_tests(self) -> List[Dict[str, Any]]:
    led_results = execute_all_led_tests()
    self.all_results.extend(led_results)
    
    bat_results = execute_all_bat_tests()  # Add this
    self.all_results.extend(bat_results)
    
    return self.all_results
```

## Dependencies

### Core Requirements
- Python 3.7+
- PyYAML (for contract files)

### Optional (for Reports)
- `openpyxl` - for Excel report generation
  ```bash
  pip install openpyxl
  ```
- `reportlab` - for PDF report generation
  ```bash
  pip install reportlab
  ```

Install all with:
```bash
pip install pyyaml openpyxl reportlab
```

## Testing the Framework

### Test LED Module
```python
from tests.led_tests import execute_all_led_tests
results = execute_all_led_tests()
for result in results:
    print(f"{result['TestCaseID']}: {result['Status']}")
```

### Test Backend Adapter
```python
from backend_adapter.led_service import read_led_voltage
data = read_led_voltage("TC_LED_01")
print(f"LED Voltage: {data['TestFw_LedVoltage']}")
```

### Test Orchestrator
```python
from core.orchestrator import orchestrate_tests
test_data = orchestrate_tests()
print(test_data["summary"])
```

## File Locations

- **Output directory:** `automation/reports/output/`
- **Current working directory:** `automation/` root (when called via `python run_all_tests.py`)

## Future Roadmap

- [ ] Add BAT tests
- [ ] Add LIN tests
- [ ] Add database logging for historical results
- [ ] Add email report distribution
- [ ] Add performance metrics tracking
- [ ] Add real-time test execution dashboard

## Notes for Backend Team

### Stable Output Variables
The following output variables are used by automation and will NOT change:
- `TestFw_LedVoltage` (float, volts)

When adding new tests, ensure:
1. Define expected output variable names in contract YAML
2. Implement backend adapter to return these variables
3. Do NOT change variable names after confirmation
4. Automation will only ever read these documented variables

### Backend Adapter Interface
Each adapter must implement:
```python
def read_<test_type>_<measure>(test_id: str) -> dict:
    """
    Return dictionary with stable output variables.
    """
```

This allows backend implementation to evolve (mock → real hardware) 
without breaking automation.

## Support

For issues or questions about the automation framework, contact the automation team.
