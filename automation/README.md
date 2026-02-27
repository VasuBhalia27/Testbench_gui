# SmartBU Automation

This folder contains all automation code for the SmartBU project.

## Principles

1. **Isolation** – Automation lives entirely within this directory. No modifications are made to the existing project files (`gui_main.py`, `Functional/*`, etc.).
2. **Resilience** – Tests should rely on well-defined interfaces and wrappers so that changes to the backend or GUI have minimal impact. The automation code should adapt through abstraction layers rather than by editing production code.
3. **Modularity** – Separate logic (wrappers/adapters) from test definitions. Use `automation/core` for interface classes and `automation/tests` for test suites.
4. **Mocking & Stubbing** – External dependencies (Trace32 connection, file system, GUI widgets) are mocked to allow tests to run in CI without hardware or GUI.

## Getting started

1. Install dependencies (e.g., `pytest`) in the project virtual environment.
2. Write adapters in `automation/core` that import from `Functional.trace32` and expose simplified methods.
3. Create tests in `automation/tests` that use `pytest` and monkeypatch fixtures to simulate trace32 and GUI behavior.

## Automation GUI

The automation interface is a minimal Tkinter window that allows a tester
or script to choose the handle type (Non‑NFC or NFC).  It does **not** show
the ELF path, which is determined automatically via
:func:`automation.core.path_utils.smartbu_repo_path`.

Use the GUI as follows:

```python
from automation.core.gui_automation import AutomationGUI

gui = AutomationGUI()
variant = gui.run()  # blocks until the user closes the window
print(f"selected variant {variant}")
```

Tests for the GUI are already included in `automation/tests`.

## Hardware Setup Verification

Once the user selects a variant, the automation performs **silent hardware setup verification**:

1. Automatically connects to Trace32 with the chosen variant
2. Waits for "stopped at breakpoint" status
3. Waits 1 second
4. Executes "Go" command
5. Verifies "running" status

All these steps happen in the background with progress shown in the automation GUI.
If verification succeeds, the hardware is ready for testing. If it fails, a clear
error message explains what went wrong.

Use it programmatically:

```python
from automation.core.hardware_setup import HardwareSetupVerifier

def on_status(msg):
    print(f"[Setup] {msg}")

verifier = HardwareSetupVerifier(status_callback=on_status)
success = verifier.verify_setup(preset=1)  # 1=Non-NFC, 2=NFC

if success:
    print("Hardware ready for testing")
else:
    print("Hardware setup failed")
```

## Running the full automation workflow

```bash
cd d:/Project/Testbench_gui_Charan
python -m automation.run
```

This launches the variant selector. Once you choose a variant and close the window,
the hardware setup verification begins automatically and its progress is displayed.

## Recommended commands

```bash
cd d:/Project/Testbench_gui_Charan
python -m pytest automation/tests -v
```

## LED test sequence

After successful hardware setup the automation workflow automatically
executes the functional test sequence appropriate for the chosen variant
(Non‑NFC or NFC).  Currently only the LED verification is implemented;
additional routines will be invoked later depending on the variant.  The
sequence is documented in :mod:`automation.core.test_sequences` and the
results are written to the status window.  In brief:

* Issue the appropriate debugger variable to toggle the LED state.
* Pause five seconds to allow the voltage to settle.
* Fire the ``TESTFW_GUI_CMD_LED_TEST_e`` DID and poll
  ``TestFw_LedVoltage`` for a stable value.
* Evaluate success using 2400–2600 mV for the "on" case and exactly 0 mV
  for the "off" case.

Further test routines (battery, motor, etc.) will be added in follow‑up
commits.  Each function’s logic is kept in its own module (e.g.
``automation/core/led_test.py``) so problems can be debugged by running a
single file instead of the entire suite.

## Notes

- Avoid touching the main application logic. If a bug needs fixing in production code, create an issue and coordinate with the development team.
- Keep test data and helpers in this folder.
- Hardware setup is completely automated and invisible to the user
- Status progress is reported via callbacks, making it easy to integrate with any UI or logging system
