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

import json
import os
import tkinter as tk
from tkinter import ttk, PhotoImage, messagebox
import time
import threading
from pathlib import Path

_ASSETS_DIR = Path(__file__).parent.parent.parent / "assets_GC" / "Page_12(Auto)" / "assets" / "frame0"
_SETTINGS_FILE = Path(__file__).parent.parent.parent / "AutomationScripts" / "automation_gui_settings.json"


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
        self._start_automation_id = None  # after-callback ID for pending _start_automation

        if parent_widget is None:
            # Standalone window mode (not used in integrated setup)
            self.root = tk.Tk()
            self.root.title("NFC LH Rev 1.04 Automation")
            self.root.geometry("500x450")
        else:
            # Embedded mode: build UI directly in parent widget
            self.root = parent_widget

        # create the variant variable now that a root exists
        self.variant = tk.IntVar(master=self.root, value=0)  # start unchecked; user must select
        # CAN/LIN enable toggle: 0 = OFF (disabled), 1 = ON (enabled)
        self.canlin_enabled = tk.IntVar(master=self.root, value=0)
        self.waiting_for_canlin = False  # True when hw init done and awaiting user CAN/LIN pick
        env_psu_type = os.getenv("PSU_TYPE", "").strip().lower()
        env_psu_automation = os.getenv("PSU_AUTOMATION", "").strip().lower()
        saved_psu_type = self._load_saved_psu_type()
        saved_psu_automation = self._load_saved_psu_automation()
        if env_psu_type in ("owon", "kikusui"):
            selected_psu_type = env_psu_type
        elif saved_psu_type in ("owon", "kikusui"):
            selected_psu_type = saved_psu_type
        else:
            selected_psu_type = "kikusui"
        if env_psu_automation in ("0", "false", "off", "no"):
            selected_psu_automation = 0
        elif env_psu_automation in ("1", "true", "on", "yes"):
            selected_psu_automation = 1
        else:
            selected_psu_automation = 1 if saved_psu_automation else 0
        self.psu_type = tk.StringVar(master=self.root, value=selected_psu_type.upper())
        self.psu_automation_enabled = tk.IntVar(master=self.root, value=selected_psu_automation)

        # Persistent PCB-level pass/fail counters (survive GUI restarts)
        saved_counts = self._load_pcb_counts()
        self.pass_count = saved_counts[0]
        self.fail_count = saved_counts[1]

        # build the interface into whichever container we've chosen
        self._build_ui(self.root)

    def _build_ui(self, container):
        """Construct the GUI layout."""
        # ---- Top section: two-column layout ----
        # Left panel: logo + Test Result Status box
        # Right panel: header text + welcome + buttons + PSU
        top_section = tk.Frame(container, bg="#DFDFDF")
        top_section.pack(fill="x", padx=0, pady=(4, 4))

        # --- LEFT PANEL ---
        left_panel = tk.Frame(top_section, bg="#DFDFDF", width=320)
        left_panel.pack(side="left", fill="y", padx=(8, 0))
        left_panel.pack_propagate(False)  # keep fixed width

        # Company logo
        try:
            self._logo_image = PhotoImage(file=str(_ASSETS_DIR / "minebea_logo_12.png"))
            logo_label = tk.Label(left_panel, image=self._logo_image, bg="#DFDFDF")
            logo_label.pack(anchor="w", padx=6, pady=(4, 6))
        except Exception:
            self._logo_image = None  # logo file missing — skip silently

        # Test Result Status box occupies the rest of the left panel
        self.result_frame = tk.Frame(left_panel, bg="#DFDFDF", bd=2, relief="groove")
        self.result_frame.pack(fill="both", expand=True, padx=6, pady=(0, 6))

        self.result_title = ttk.Label(
            self.result_frame,
            text="Test Result Status",
            font=(None, 13, "bold"),
        )
        self.result_title.pack(anchor="w", padx=10, pady=(8, 4))

        self.result_row = tk.Frame(self.result_frame, bg="#DFDFDF")
        self.result_row.pack(anchor="w", padx=10, pady=(0, 8))

        self.result_indicator = tk.Label(
            self.result_row,
            text="",
            font=("Arial", 44, "bold"),
            fg="#FFFFFF",
            bg="#DFDFDF",
            width=6,
            relief="flat",
        )
        self.result_indicator.pack(side="left", padx=(0, 4), pady=4)

        self.result_status_text = ttk.Label(self.result_row, text="")

        # --- FAR RIGHT PANEL: Pass/Fail Counters ---
        counter_panel = tk.Frame(top_section, bg="#DFDFDF")
        counter_panel.pack(side="right", fill="y", padx=(0, 8), pady=4)

        # Top row: PASS and FAIL boxes
        counter_boxes = tk.Frame(counter_panel, bg="#DFDFDF")
        counter_boxes.pack(side="top")

        self.pass_counter_label = tk.Label(
            counter_boxes, text=f"PASS\n{self.pass_count}",
            font=("Arial", 18, "bold"),
            fg="#FFFFFF", bg="#27AE60",
            width=6, height=3,
            relief="flat",
        )
        self.pass_counter_label.pack(side="left", padx=4, pady=4)

        self.fail_counter_label = tk.Label(
            counter_boxes, text=f"FAIL\n{self.fail_count}",
            font=("Arial", 18, "bold"),
            fg="#FFFFFF", bg="#C62828",
            width=6, height=3,
            relief="flat",
        )
        self.fail_counter_label.pack(side="left", padx=4, pady=4)

        # Bottom row: Reset Count button
        tk.Button(
            counter_panel,
            text="Reset Count",
            font=("Arial", 9, "bold"),
            fg="#FFFFFF", bg="#555555",
            activebackground="#333333", activeforeground="#FFFFFF",
            relief="flat", cursor="hand2",
            command=self._reset_pcb_counts,
        ).pack(side="top", fill="x", padx=4, pady=(0, 4))

        # --- RIGHT PANEL ---
        right_panel = tk.Frame(top_section, bg="#DFDFDF")
        right_panel.pack(side="left", fill="both", expand=True, padx=(10, 8))

        # Welcome header
        header = ttk.Label(right_panel, text="NFC LH Rev 1.04 Automation",
                           font=(None, 16, "bold"))
        header.pack(pady=(10, 4))

        welcome = ttk.Label(right_panel,
                            text="Welcome to NFC LH Rev 1.04 Automation\n"
                                 "Click 'Start' to begin the setup and test sequence.",
                            font=(None, 10), justify="center")
        welcome.pack(pady=(0, 6))

        # Button row: Start / End / Power Supply
        btn_frame = ttk.Frame(right_panel)
        btn_frame.pack(pady=(0, 8))

        self.start_button = ttk.Button(btn_frame, text="Start",
                                       command=self._on_start)
        self.start_button.pack(side="left", padx=8)

        self.end_button = ttk.Button(btn_frame, text="End",
                                     command=self._on_end)
        self.end_button.pack(side="left", padx=8)

        # Power Supply frame — always visible so it can be changed before Start.
        self.psu_frame = ttk.Labelframe(btn_frame, text="Power Supply")
        self.psu_frame.pack(side="left", padx=(16, 0))

        self.psu_type_cb = ttk.Combobox(
            self.psu_frame,
            textvariable=self.psu_type,
            values=("OWON", "KIKUSUI"),
            state="readonly",
            width=12,
        )
        self.psu_type_cb.grid(row=0, column=0, sticky="w", padx=5, pady=5)

        self.psu_automation_cb = ttk.Checkbutton(
            self.psu_frame,
            text="Automation ON",
            variable=self.psu_automation_enabled,
            onvalue=1,
            offvalue=0,
        )
        self.psu_automation_cb.grid(row=1, column=0, sticky="w", padx=5, pady=5)

        # Create a main area that will hold control_frame above status_frame.
        # Using grid inside this area ensures the control frame stays above the
        # expanding status area regardless of widget sizes.
        self.main_area = ttk.Frame(container)
        self.main_area.pack(padx=20, pady=10, fill="both", expand=True)

        # Control frame: variant selection + timer (side by side, initially hidden)
        # Make the frame a child of main_area so it becomes visible when gridded there.
        self.control_frame = ttk.Frame(self.main_area)

        # Handle Type Selection frame (left side — first)
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

        # CAN/LIN Setting frame (right side — second)
        self.canlin_frame = ttk.Labelframe(self.control_frame, text="CAN/LIN Setting")
        self.canlin_frame.pack(side="left", padx=(0, 20), fill="x", expand=False)

        self.canlin_off_cb = ttk.Checkbutton(
            self.canlin_frame,
            text="CAN/LIN OFF",
            variable=self.canlin_enabled,
            onvalue=0, offvalue=1,
            command=lambda: self._sync_canlin(0),
        )
        self.canlin_off_cb.grid(row=0, column=0, sticky="w", padx=5, pady=5)

        self.canlin_on_cb = ttk.Checkbutton(
            self.canlin_frame,
            text="CAN/LIN ON",
            variable=self.canlin_enabled,
            onvalue=1, offvalue=0,
            command=lambda: self._sync_canlin(1),
        )
        self.canlin_on_cb.grid(row=1, column=0, sticky="w", padx=5, pady=5)

        # initial visual state: both unchecked
        self.canlin_off_cb.state(["!selected"])
        self.canlin_on_cb.state(["!selected"])

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
            self.append_status("Closing Trace32 debugger (force cleanup if needed)...")
            # Always call QuitTrace32: it performs process-level cleanup in
            # addition to protocol-level disconnect, which is needed when
            # PowerView is hung and no valid dbg object exists.
            t32.QuitTrace32(status_label=None)
            self.append_status("Trace32 closed.")
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
        self.psu_type_cb.config(state="readonly")
        self.psu_automation_cb.config(state="normal")
        self.variant.set(0)
        self.non_nfc_cb.state(["!selected"])
        self.nfc_cb.state(["!selected"])
        self.canlin_enabled.set(0)
        self.canlin_off_cb.state(["!selected"])
        self.canlin_on_cb.state(["!selected"])
        self.waiting_for_canlin = False
        self.clear_result_indicator()
        self.append_status("\nReady for next PCB. Click 'Start' to begin.")

    def _on_start(self):
        """Handle Start button click."""
        self.started = True
        self.waiting_for_canlin = False
        self.clear_result_indicator()
        selected_psu = self.psu_type.get().strip().lower()
        if selected_psu not in ("owon", "kikusui"):
            selected_psu = "owon"
        psu_automation_enabled = 1 if self.psu_automation_enabled.get() else 0
        os.environ["PSU_TYPE"] = selected_psu
        os.environ["PSU_AUTOMATION"] = str(psu_automation_enabled)
        self._save_psu_type(selected_psu)
        self.start_button.config(state="disabled")
        self.psu_type_cb.config(state="disabled")
        self.psu_automation_cb.config(state="disabled")
        # Grid control_frame into main_area row 0 so it appears above status
        try:
            self.control_frame.grid(in_=self.main_area, row=0, column=0, sticky="ew", pady=(0,5))
        except Exception:
            # fallback to packing into container if grid fails
            self.control_frame.pack(padx=20, pady=10, fill="x")
        # Clear old status text when Start is clicked
        self.status_text.config(state="normal")
        self.status_text.delete(1.0, tk.END)
        self.status_text.config(state="disabled")
        # Reset timer
        self._reset_timer()
        # Pre-select Driver (variant 2) so operator can confirm or change it
        self._sync(2)
        self.append_status(f"Power Supply selected: {selected_psu.upper()}")
        self.append_status(
            "Power Supply automation: "
            f"{'ENABLED' if psu_automation_enabled == 1 else 'DISABLED'}"
        )
        self.append_status("Step 1: Driver (NFC) pre-selected. Change to Non-Driver if needed...")

    def _sync_canlin(self, value: int) -> None:
        """Keep the CAN/LIN OFF/ON checkbuttons mutually exclusive.

        CAN/LIN OFF: reads TestFw_GuiCanDependencyDisable immediately and
                     signals the automation thread to continue.
        CAN/LIN ON:  resets the debugger target first (SYStem.Up + Go), then
                     re-reads TestFw_GuiCanDependencyDisable so the log shows
                     the post-reset firmware value before signalling the thread.
                     The reset runs in a background thread to keep the GUI responsive.
        """
        self.canlin_enabled.set(value)
        self.canlin_off_cb.state(["selected"] if value == 0 else ["!selected"])
        self.canlin_on_cb.state(["selected"] if value == 1 else ["!selected"])

        if not getattr(self, "waiting_for_canlin", False):
            return

        canlin_label = "ON" if value == 1 else "OFF"
        self.append_status(f"\nCAN/LIN setting selected: {canlin_label}")

        def _signal_thread():
            """Optionally reset the target, apply the CAN/LIN value, read it back, then fire the event."""
            try:
                from Functional import trace32 as t32
                # Determine the value to write:
                #   CAN/LIN ON  (value=1) -> TestFw_GuiCanDependencyDisable = 0
                #   CAN/LIN OFF (value=0) -> TestFw_GuiCanDependencyDisable = 1
                can_dep_value = 0 if value == 1 else 1
                if value == 1:
                    # Reset target so firmware re-initialises cleanly
                    self.append_status("Resetting debugger target...")
                    t32.ResetTarget(status_label=None)
                    self.append_status("Target reset complete")
                    time.sleep(1)
                    t32.RunCode(exec_label=None)
                    self.append_status("Code execution started")
                    time.sleep(2)  # allow firmware to initialise
                # Set the variable to the user-selected value
                if t32.dbg and hasattr(t32.dbg, 'cmd'):
                    t32.dbg.cmd(f"Var.set TestFw_GuiCanDependencyDisable = {can_dep_value}")
                    # Read back to confirm
                    raw = t32.dbg.fnc("Var.VALUE(TestFw_GuiCanDependencyDisable)")
                    self.append_status(
                        f"TestFw_GuiCanDependencyDisable = {int(float(str(raw)))} (set by CAN/LIN {canlin_label} selection)"
                    )
                else:
                    self.append_status("TestFw_GuiCanDependencyDisable: Trace32 not connected")
            except Exception as e:
                self.append_status(f"TestFw_GuiCanDependencyDisable: could not apply \u2014 {e}")
            finally:
                self.waiting_for_canlin = False
                if self.automation_runner is not None and hasattr(self.automation_runner, "_canlin_event"):
                    self.automation_runner._canlin_event.set()

        threading.Thread(target=_signal_thread, daemon=True).start()

    def _sync(self, value: int) -> None:
        """Keep the pair of checkbuttons mutually exclusive."""
        if value == 1:
            self.variant.set(1)
        elif value == 2:
            self.variant.set(2)
        # update widget states so they appear checked/unchecked
        self.non_nfc_cb.state(["!selected"] if self.variant.get() != 1 else ["selected"])
        self.nfc_cb.state(["!selected"] if self.variant.get() != 2 else ["selected"])
        # Only trigger automation if user explicitly started the flow
        if getattr(self, "started", False):
            # Lock other tabs, start timer, then launch automation.
            # Cancel any previously scheduled _start_automation so only the
            # most recent variant selection takes effect.
            if self._start_automation_id is not None:
                try:
                    self.root.after_cancel(self._start_automation_id)
                except Exception:
                    pass
                self._start_automation_id = None
            self.lock_callback()
            self._start_timer()
            self._start_automation_id = self.root.after(100, self._start_automation)

    def set_testing_indicator(self) -> None:
        """Show 'Testing...' in result indicator while test is in progress."""
        self.result_indicator.config(
            text="Testing...",
            fg="#FFFFFF",
            bg="#E67E22",
            font=("Arial", 20, "bold"),
            width=8,
        )
        self.result_status_text.config(text="")

    def _start_automation(self):
        """Called after variant selection; triggers the automation flow."""
        self._start_automation_id = None
        # Guard: do not start a second run if one is already in progress
        if self.automation_runner is not None and getattr(self.automation_runner, 'is_running', False):
            return
        if self.automation_runner is not None:
            variant = self.variant.get()
            self.append_status(f"\nVariant selected: {variant}")
            self.append_status("Starting automation — CAN/LIN selection will be prompted after hardware initialisation.")
            self.set_testing_indicator()
            self.automation_runner.start_automation(variant)

    def prompt_canlin_selection(self) -> None:
        """Called by IntegratedAutomationRunner (via root.after) once hardware
        initialisation is complete. Pre-selects CAN/LIN OFF and shows the prompt.
        """
        self.waiting_for_canlin = True
        # Pre-select CAN/LIN OFF so the operator can just confirm or change it
        self._sync_canlin(0)
        self.append_status("\nStep 2: CAN/LIN OFF pre-selected. Change to ON if needed...")

    def append_status(self, message: str) -> None:
        """Append a message to the status text area."""
        self.status_text.config(state="normal")
        self.status_text.insert("end", message + "\n")
        self.status_text.see("end")  # auto‑scroll to bottom
        self.status_text.config(state="disabled")
        if self.parent_widget is not None:
            self.root.update()  # refresh GUI immediately

    def show_restart_warning(self) -> None:
        """Show a warning dialog when battery voltage is 0.0 mV on two consecutive runs.

        After the user dismisses the dialog the debugger is closed and the
        application window is destroyed automatically.
        """
        messagebox.showwarning(
            title="Battery Voltage Not Detected",
            message=(
                "Battery voltage has read 0.0 mV on two consecutive runs.\n\n"
                "The supply voltage has not stabilised yet.\n\n"
                "Please follow these steps:\n"
                "  1. Wait for the supply voltage to stabilise.\n"
                "  2. Check all hardware connections.\n"
                "  3. Click OK — the debugger will be closed automatically.\n"
                "  4. The application will close automatically.\n"
                "  5. Restart the application and try again."
            )
        )
        # Step 3: close the Trace32 debugger connection
        self.append_status("\nClosing Trace32 debugger before exit...")
        try:
            from Functional import trace32 as t32
            if t32.dbg and hasattr(t32.dbg, 'cmd'):
                t32.QuitTrace32(status_label=None)
                self.append_status("Trace32 closed.")
        except Exception as e:
            self.append_status(f"Note: Trace32 close: {e}")

        # Step 4: destroy the top-level window (closes the application)
        self.append_status("Closing application window...")
        try:
            self.root.winfo_toplevel().destroy()
        except Exception:
            pass

    def reset_for_new_run(self) -> None:
        """Reset GUI to allow another automation run."""
        self.started = False
        self.start_button.config(state="normal")
        self.psu_type_cb.config(state="readonly")
        self.psu_automation_cb.config(state="normal")
        # keep control_frame visible so handle selection and timer remain
        # available for the user after a run completes
        self._stop_timer()  # freezes display at final time; clears timer_start_time to stop rescheduling
        # Status text is now cleared only when Start button is clicked,
        # not here, so it persists after automation completes
        # reset variant to unchecked state
        self.variant.set(0)
        self.non_nfc_cb.state(["!selected"])
        self.nfc_cb.state(["!selected"])
        self.canlin_enabled.set(0)
        self.canlin_off_cb.state(["!selected"])
        self.canlin_on_cb.state(["!selected"])
        self.waiting_for_canlin = False

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
        """Stop the timer from updating (display stays frozen at last value)."""
        if self.timer_id is not None:
            self.root.after_cancel(self.timer_id)
            self.timer_id = None
        # Clear start time so any already-queued _update_timer callback
        # exits without rescheduling itself (race-condition guard).
        self.timer_start_time = None

    def set_result_indicator(self, all_passed: bool) -> None:
        """Set the Test Result Status box and increment the persistent PCB counter."""
        if all_passed:
            self.result_indicator.config(
                text="PASS", fg="#FFFFFF", bg="#27AE60",
                font=("Arial", 44, "bold"),
                width=6,
            )
            self.result_status_text.config(text="")
            self.pass_count += 1
        else:
            self.result_indicator.config(
                text="FAIL", fg="#FFFFFF", bg="#C62828",
                font=("Arial", 44, "bold"),
                width=6,
            )
            self.result_status_text.config(text="")
            self.fail_count += 1
        self.pass_counter_label.config(text=f"PASS\n{self.pass_count}")
        self.fail_counter_label.config(text=f"FAIL\n{self.fail_count}")
        self._save_pcb_counts()

    def update_test_item_counts(self, pass_n: int, fail_n: int) -> None:
        """No-op: PCB counters are now maintained by set_result_indicator.
        Kept for API compatibility with integrated_automation."""
        pass

    def clear_result_indicator(self) -> None:
        """Clear the result box for the next test run. PCB counters are NOT reset."""
        self.result_indicator.config(text="", bg="#DFDFDF", fg="#FFFFFF", font=("Arial", 44, "bold"), width=6)
        self.result_status_text.config(text="")

    def set_automation_runner(self, runner) -> None:
        """Set the automation runner instance."""
        self.automation_runner = runner

    def _load_pcb_counts(self):
        """Load persistent PCB pass/fail counts from the settings file."""
        try:
            if not _SETTINGS_FILE.exists():
                return (0, 0)
            data = json.loads(_SETTINGS_FILE.read_text(encoding="utf-8"))
            p = int(data.get("pcb_pass_count", 0))
            f = int(data.get("pcb_fail_count", 0))
            return (max(p, 0), max(f, 0))
        except Exception:
            return (0, 0)

    def _save_pcb_counts(self) -> None:
        """Persist current PCB pass/fail counts to the settings file."""
        try:
            _SETTINGS_FILE.parent.mkdir(parents=True, exist_ok=True)
            data = {}
            if _SETTINGS_FILE.exists():
                try:
                    data = json.loads(_SETTINGS_FILE.read_text(encoding="utf-8"))
                except Exception:
                    data = {}
            data["pcb_pass_count"] = self.pass_count
            data["pcb_fail_count"] = self.fail_count
            _SETTINGS_FILE.write_text(json.dumps(data, indent=2), encoding="utf-8")
        except Exception:
            pass

    def _reset_pcb_counts(self) -> None:
        """Reset PCB pass/fail counters to zero and persist immediately."""
        self.pass_count = 0
        self.fail_count = 0
        self.pass_counter_label.config(text="PASS\n0")
        self.fail_counter_label.config(text="FAIL\n0")
        self._save_pcb_counts()

    def _load_saved_psu_type(self) -> str:
        """Load persisted PSU type from local settings file."""
        try:
            if not _SETTINGS_FILE.exists():
                return ""
            data = json.loads(_SETTINGS_FILE.read_text(encoding="utf-8"))
            value = str(data.get("psu_type", "")).strip().lower()
            if value in ("owon", "kikusui"):
                return value
            # Tolerate common typos (e.g. "kikusi", "kikusu")
            if value.startswith("kik"):
                return "kikusui"
            if value.startswith("owo"):
                return "owon"
        except Exception:
            pass
        return ""

    def _load_saved_psu_automation(self) -> bool:
        """Load persisted PSU automation state from local settings file."""
        try:
            if not _SETTINGS_FILE.exists():
                return True
            data = json.loads(_SETTINGS_FILE.read_text(encoding="utf-8"))
            value = data.get("psu_automation", True)
            if isinstance(value, bool):
                return value
            if str(value).strip().lower() in ("1", "true", "on", "yes"):
                return True
            if str(value).strip().lower() in ("0", "false", "off", "no"):
                return False
        except Exception:
            pass
        return True

    def _save_psu_type(self, psu_type: str) -> None:
        """Persist selected PSU type for future app launches."""
        try:
            _SETTINGS_FILE.parent.mkdir(parents=True, exist_ok=True)
            data = {}
            if _SETTINGS_FILE.exists():
                try:
                    data = json.loads(_SETTINGS_FILE.read_text(encoding="utf-8"))
                except Exception:
                    data = {}
            data["psu_type"] = psu_type
            data["psu_automation"] = bool(self.psu_automation_enabled.get())
            _SETTINGS_FILE.write_text(
                json.dumps(data, indent=2),
                encoding="utf-8",
            )
        except Exception as exc:
            self.append_status(f"Note: could not persist PSU selection ({exc})")

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


