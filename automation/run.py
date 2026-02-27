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

from automation.core import gui_automation, hardware_setup


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
        from automation.core import test_sequences, trace32_adapter

        adapter = trace32_adapter.Trace32Interface()
        runner = test_sequences.TestSequenceRunner(
            adapter, status_callback=gui.append_status
        )

        gui.append_status("\nExecuting functional test sequence...")
        results = runner.run_for_variant(variant)
        for name, passed in results.items():
            gui.append_status(f"{name}: {'PASS' if passed else 'FAIL'}")
    else:
        gui.append_status("\n✗ HARDWARE SETUP FAILED - Please check hardware and Trace32")
    
    # Show the result window briefly (keep it open until user closes)
    gui.root.mainloop()


if __name__ == "__main__":
    main()
