"""Simple front‑end for automation use.

This module provides a pared‑down Tkinter interface that mirrors the
variant‑selection portion of the real application.  It automatically
locates the SmartBU repository (so no path entry is shown) and allows the
user to choose between Non‑NFC and NFC variants.  Additional controls can
be added later as required.

The GUI does **not** modify any production code and lives entirely in the
`automation` package.  External automation scripts should import
:class:`AutomationGUI` and call ``run`` to display the window; the
``variant`` property contains the current selection (1=Non‑NFC, 2=NFC).

Usage example::

    from AutomationScripts.core.gui_automation import AutomationGUI

    gui = AutomationGUI()
    gui.run()            # this call blocks until user closes the window
    print(gui.variant)   # 1 or 2

"""

import tkinter as tk
from tkinter import ttk
import time


class AutomationGUI:
    def __init__(self, parent_widget=None, lock_callback=None, unlock_callback=None):
        """
        Initialize the automation GUI.

        :param parent_widget: if provided, embed GUI within this widget (TAB 1);
                              otherwise create standalone window.
        :param lock_callback: optional callable to lock other tabs during automation.
        :param unlock_callback: optional callable to unlock tabs after automation.
        """
        self.parent_widget = parent_widget
        self.lock_callback = lock_callback or (lambda: None)
        self.unlock_callback = unlock_callback or (lambda: None)
        self.started = False
        self.automation_runner = None  # will be set by integrated setup
        
        # Timer tracking
        self.timer_start_time = None
        self.timer_id = None

        if parent_widget is None:
            # Standalone window mode (not used in integrated setup)
            self.root = tk.Tk()
            self.root.title("SmartBU Test Automation")
            self.root.geometry("500x450")
        else:
            # Embedded mode: build UI directly in parent widget
            self.root = parent_widget

        # create the variant variable now that a root exists
        self.variant = tk.IntVar(master=self.root, value=0)  # start unchecked; user must select

        # build the interface into whichever container we've chosen
        self._build_ui(self.root)

    def _build_ui(self, container):
        """Construct the GUI layout."""
        # Welcome header
        header = ttk.Label(container, text="SmartBU Test Automation",
                           font=(None, 16, "bold"))
        header.pack(pady=10)

        welcome = ttk.Label(container,
                            text="Welcome to SmartBU Test Automation\n"
                                 "Click 'Start' to begin the setup and test sequence.",
                            font=(None, 10), justify="center")
        welcome.pack(pady=5)

        # Button row: Start and End side by side
        btn_frame = ttk.Frame(container)
        btn_frame.pack(pady=10)

        self.start_button = ttk.Button(btn_frame, text="Start",
                                       command=self._on_start)
        self.start_button.pack(side="left", padx=8)

        self.end_button = ttk.Button(btn_frame, text="End",
                                     command=self._on_end)
        self.end_button.pack(side="left", padx=8)

        # Create a main area that will hold control_frame above status_frame.
        # Using grid inside this area ensures the control frame stays above the
        # expanding status area regardless of widget sizes.
        self.main_area = ttk.Frame(container)
        self.main_area.pack(padx=20, pady=10, fill="both", expand=True)

        # Control frame: variant selection + timer (side by side, initially hidden)
        # Make the frame a child of main_area so it becomes visible when gridded there.
        self.control_frame = ttk.Frame(self.main_area)

        # Variant selection frame (left side)
        self.variant_frame = ttk.Labelframe(self.control_frame,
                                           text="Handle Type Selection")
        self.variant_frame.pack(side="left", padx=(0, 20), fill="x", expand=False)

        self.non_nfc_cb = ttk.Checkbutton(self.variant_frame,
                                          text="Non‑Driver (without NFC)",
                                          variable=self.variant,
                                          onvalue=1, offvalue=0,
                                          command=lambda: self._sync(1))
        self.non_nfc_cb.grid(row=0, column=0, sticky="w", padx=5, pady=5)

        self.nfc_cb = ttk.Checkbutton(self.variant_frame,
                                      text="Driver (with NFC)",
                                      variable=self.variant,
                                      onvalue=2, offvalue=0,
                                      command=lambda: self._sync(2))
        self.nfc_cb.grid(row=1, column=0, sticky="w", padx=5, pady=5)

        # ensure checkbutton visual state reflects variable (start unchecked)
        if self.variant.get() == 1:
            self.non_nfc_cb.state(["selected"])
        else:
            self.non_nfc_cb.state(["!selected"])
        if self.variant.get() == 2:
            self.nfc_cb.state(["selected"])
        else:
            self.nfc_cb.state(["!selected"])

        # Timer label (right side of control frame)
        self.timer_label = ttk.Label(self.control_frame,
                                     text="Time Elapsed: 00:00",
                                     font=(None, 12, "bold"))
        self.timer_label.pack(side="left", padx=10)

        # Status/progress display frame (placed in main_area grid row 1)
        self.status_frame = ttk.Labelframe(self.main_area, text="Automation Progress")
        self.status_frame.grid(row=1, column=0, sticky="nsew")

        self.status_text = tk.Text(self.status_frame, height=10, width=50,
                       state="disabled", wrap="word")
        self.status_text.pack(side="left", fill="both", expand=True, padx=5, pady=5)

        scrollbar = ttk.Scrollbar(self.status_frame, command=self.status_text.yview)
        scrollbar.pack(side="right", fill="y")
        self.status_text.config(yscrollcommand=scrollbar.set)

        # Configure grid so the status_frame expands while control_frame stays above
        self.main_area.columnconfigure(0, weight=1)
        self.main_area.rowconfigure(1, weight=1)

        # Initially control_frame is not gridded; it will be shown on Start

    def _on_end(self) -> None:
        """Handle End button click.

        Disconnects from Trace32 (kills the debugger process) and resets the
        GUI back to a clean state so the operator can immediately plug in the
        next PCB and click Start without restarting the application.
        """
        # If automation is still running, stop it gracefully first
        if self.automation_runner is not None and getattr(self.automation_runner, 'is_running', False):
            self.append_status("\nEnd requested — waiting for current run to finish...")
            # signal the runner to stop after the current step
            self.automation_runner.is_running = False

        # Close the Trace32 debugger connection
        try:
            from Functional import trace32 as t32
            if t32.dbg and hasattr(t32.dbg, 'cmd'):
                self.append_status("Closing Trace32 debugger...")
                t32.QuitTrace32(status_label=None)
                self.append_status("Trace32 closed.")
            else:
                self.append_status("Trace32 not connected — nothing to close.")
        except Exception as e:
            self.append_status(f"Note: Trace32 close: {e}")

        # Reset the automation runner so the next run starts fresh
        if self.automation_runner is not None:
            self.automation_runner.is_first_run = True
            self.automation_runner.adapter = None
            self.automation_runner.psu = None

        # Stop timer and reset GUI
        self._stop_timer()
        self.timer_label.config(text="Time Elapsed: 00:00")
        self.timer_start_time = None
        self.started = False
        self.start_button.config(state="normal")
        self.variant.set(0)
        self.non_nfc_cb.state(["!selected"])
        self.nfc_cb.state(["!selected"])
        self.append_status("\nReady for next PCB. Click 'Start' to begin.")

    def _on_start(self):
        """Handle Start button click."""
        self.started = True
        self.start_button.config(state="disabled")
        # Grid control_frame into main_area row 0 so it appears above status
        try:
            self.control_frame.grid(in_=self.main_area, row=0, column=0, sticky="ew", pady=(0,5))
        except Exception:
            # fallback to packing into container if grid fails
            self.control_frame.pack(padx=20, pady=10, fill="x")
        self.lock_callback()  # lock other tabs
        # Clear old status text when Start is clicked
        self.status_text.config(state="normal")
        self.status_text.delete(1.0, tk.END)
        self.status_text.config(state="disabled")
        # Reset timer
        self._reset_timer()
        self.append_status("✓ Please select a variant to proceed...")

    def _sync(self, value: int) -> None:
        """Keep the pair of checkbuttons mutually exclusive."""
        if value == 1:
            # user clicked non‑NFC
            self.variant.set(1)
        elif value == 2:
            self.variant.set(2)
        # update widget states so they appear checked/unchecked
        self.non_nfc_cb.state(["!selected"] if self.variant.get() != 1 else ["selected"])
        self.nfc_cb.state(["!selected"] if self.variant.get() != 2 else ["selected"])
        # Only trigger automation if user explicitly started the flow
        if getattr(self, "started", False):
            # Start timer when user selects a variant
            self._start_timer()
            self.root.after(100, self._start_automation)

    def _start_automation(self):
        """Called after variant selection; triggers the automation flow."""
        if self.automation_runner is not None:
            variant = self.variant.get()
            self.append_status(f"\nVariant selected: {variant}")
            self.automation_runner.start_automation(variant)

    def append_status(self, message: str) -> None:
        """Append a message to the status text area."""
        self.status_text.config(state="normal")
        self.status_text.insert("end", message + "\n")
        self.status_text.see("end")  # auto‑scroll to bottom
        self.status_text.config(state="disabled")
        if self.parent_widget is not None:
            self.root.update()  # refresh GUI immediately

    def reset_for_new_run(self) -> None:
        """Reset GUI to allow another automation run."""
        self.started = False
        self.start_button.config(state="normal")
        # keep control_frame visible so handle selection and timer remain
        # available for the user after a run completes
        self._stop_timer()
        # Status text is now cleared only when Start button is clicked,
        # not here, so it persists after automation completes
        # reset variant to unchecked state
        self.variant.set(0)
        self.non_nfc_cb.state(["!selected"])
        self.nfc_cb.state(["!selected"])

    def _reset_timer(self) -> None:
        """Reset timer to 00:00."""
        self._stop_timer()
        self.timer_start_time = None
        self.timer_label.config(text="Time Elapsed: 00:00")

    def _start_timer(self) -> None:
        """Start the elapsed time timer."""
        if self.timer_start_time is None:
            self.timer_start_time = time.time()
            self._update_timer()

    def _update_timer(self) -> None:
        """Update the timer display (MM:SS format)."""
        if self.timer_start_time is not None:
            elapsed = int(time.time() - self.timer_start_time)
            minutes = elapsed // 60
            seconds = elapsed % 60
            self.timer_label.config(text=f"Time Elapsed: {minutes:02d}:{seconds:02d}")
            # Schedule next update in 100ms
            self.timer_id = self.root.after(100, self._update_timer)

    def _stop_timer(self) -> None:
        """Stop the timer from updating."""
        if self.timer_id is not None:
            self.root.after_cancel(self.timer_id)
            self.timer_id = None

    def set_automation_runner(self, runner) -> None:
        """Set the automation runner instance."""
        self.automation_runner = runner

    def run(self) -> int:
        """Run the GUI event loop; returns the selected variant when closed.
        
        Only used in standalone mode (not integrated with gui_main).
        """
        self.root.mainloop()
        return self.variant.get()


# allow the module to be executed directly for manual testing
if __name__ == "__main__":
    # ensure the project root (parent of `automation/core`) is on sys.path
    # so that imports like "AutomationScripts.core.integrated_automation" succeed
    import os, sys

    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    if root not in sys.path:
        sys.path.insert(0, root)

    # simple entry point so developers can launch the automation GUI by
    # running this file without needing the full application.
    gui = AutomationGUI()

    # when running standalone we still want the automation flow to work;
    # create an IntegratedAutomationRunner exactly as gui_main does.  use
    # no‑op lock/unlock callbacks since there are no other tabs to disable.
    try:
        from AutomationScripts.core import integrated_automation
    except ImportError:  # pragma: no cover - just in case
        print("Warning: cannot import integrated_automation; automation will not run")
        runner = None
    else:
        runner = integrated_automation.IntegratedAutomationRunner(
            gui_automation=gui,
            lock_tabs_callback=lambda: None,
            unlock_tabs_callback=lambda: None,
        )
        gui.set_automation_runner(runner)

    variant = gui.run()
    print(f"GUI closed, variant selected = {variant}")


