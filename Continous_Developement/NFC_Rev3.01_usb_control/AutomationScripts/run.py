"""Entry point for performing automated actions via the GUI.

This script demonstrates how the automation GUI and adapter are used
together.  It can be executed from the workspace root::

    python -m automation.run

The script will:
1. Display the variant selector
2. Automatically locate the SmartBU path
3. Run hardware setup verification (connect, wait for breakpoint, go, verify running)
4. Report progress in the automation GUI
5. If successful, the system is ready for test automation

All operations happen automatically once the user selects a variant; no manual
interaction with debugger buttons is required.
"""

import os

from AutomationScripts.core import gui_automation, hardware_setup
from AutomationScripts.core.relay_control import RelayController


def main():
    gui = gui_automation.AutomationGUI()
    
    # Show a prompt for user to select variant
    gui.append_status("Select a variant and close this window to begin hardware setup...")
    
    # Run the GUI (blocks until user closes it)
    variant = gui.run()
    
    # Clear the status for setup phase
    gui = gui_automation.AutomationGUI()
    
    # Run hardware setup verification with status callback to the new GUI
    verifier = hardware_setup.HardwareSetupVerifier(
        status_callback=gui.append_status
    )
    
    success = verifier.verify_setup(variant)
    
    if success:
        gui.append_status("\n✓ HARDWARE SETUP COMPLETE - Ready for automation testing")

        # Perform the first set of functional tests (LED), reporting progress
        from AutomationScripts.core import test_sequences, trace32_adapter

        relay_controller = None
        relay_port = os.getenv("USB_RELAY_PORT")
        if relay_port:
            relay_baud = int(os.getenv("USB_RELAY_BAUD", "9600"))
            try:
                relay_controller = RelayController(port=relay_port, baudrate=relay_baud)
                relay_controller.connect()
                gui.append_status(f"External USB relay attached on {relay_port}")
            except Exception as exc:
                gui.append_status(f"Warning: external USB relay init failed: {exc}")

        adapter = trace32_adapter.Trace32Interface()
        if relay_controller is not None:
            adapter.attach_relay_controller(relay_controller)

        runner = test_sequences.TestSequenceRunner(
            adapter,
            status_callback=gui.append_status,
            relay_controller=relay_controller,
        )

        gui.append_status("\nExecuting functional test sequence...")
        results = runner.run_for_variant(variant)
        for name, passed in results.items():
            gui.append_status(f"{name}: {'PASS' if passed else 'FAIL'}")

        if relay_controller is not None:
            try:
                relay_controller.disconnect()
                gui.append_status("External USB relay disconnected")
            except Exception as exc:
                gui.append_status(f"Warning: failed to disconnect USB relay: {exc}")
    else:
        gui.append_status("\n✗ HARDWARE SETUP FAILED - Please check hardware and Trace32")
    
    # Show the result window briefly (keep it open until user closes)
    gui.root.mainloop()


if __name__ == "__main__":
    main()
