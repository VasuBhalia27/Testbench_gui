"""
SmartBU Automation Welcome Page Module

This module creates the Welcome tab for the SmartBU test automation GUI.
It handles:
- Driver/Non-Driver variant selection
- Auto-detection of ELF path (SmartBU folder)
- Automatic Trace32 connection and code start
- Start Automation Testing workflow
- Test timing and Download Report functionality
- Beautiful UI layout following existing design patterns

Designed to be independently maintained by the backend/automation team.
"""

import tkinter as tk
from tkinter import ttk, Button, PhotoImage, messagebox
import threading
import time
from pathlib import Path
import sys
import os

# Add automation folder to path for imports
ROOT = Path(__file__).parent.parent.parent
# Ensure project root is on sys.path so package imports like `automation.*` work
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
# Also add the automation folder explicitly for direct module import convenience
if str(ROOT / "automation") not in sys.path:
    sys.path.insert(0, str(ROOT / "automation"))

try:
    from backend_adapter.common import find_gui_repo_by_suffix
except Exception as e:
    print(f"Warning: Could not import backend_adapter: {e}")
    find_gui_repo_by_suffix = None


class WelcomePageAutomation:
    """Manages automation Welcome page UI and workflow."""
    
    def __init__(self, tab_frame):
        """
        Initialize the Welcome automation page.
        
        Args:
            tab_frame: tk.Frame container for the tab
        """
        self.tab_frame = tab_frame
        
        # State variables
        self.selected_variant = tk.IntVar(value=1)  # 1=Non-Driver, 2=Driver
        self.elf_path = None
        self.testing_in_progress = False
        self.testing_complete = False
        self.start_time = None
        self.elapsed_time = 0
        
        # UI elements
        self.status_label = None
        self.timer_label = None
        self.start_btn = None
        self.download_btn = None
        
        # Auto-detect ELF path
        self._auto_detect_elf_path()
        
        # Build UI
        self._setup_ui()
    
    def _auto_detect_elf_path(self):
        """Auto-detect SmartBU ELF path including nested Testbench paths.

        Prioritize the more specific nested folder which exists on some systems:
        - ROOT/Testbench_gui_Charan/Testbench_gui_Charan/SmartBU
        - ROOT/Testbench_gui_Charan/SmartBU
        - ROOT/SmartBU
        - ROOT.parent/SmartBU
        If none exist, fall back to the common Testbench path so users can still
        correct the configuration before attempting to run automation.
        """
        try:
            candidates = [
                ROOT / "Testbench_gui_Charan" / "Testbench_gui_Charan" / "SmartBU",
                ROOT / "Testbench_gui_Charan" / "SmartBU",
                ROOT / "SmartBU",
                ROOT.parent / "SmartBU",
            ]

            for p in candidates:
                try:
                    if p.exists():
                        self.elf_path = str(p)
                        return
                except Exception:
                    # Ignore permission or other filesystem errors for a candidate
                    continue

            # If none of the candidates exist, do NOT set a fallback path.
            # Leave elf_path as None so strict validation will prevent automation
            # from proceeding until the user places SmartBU at a valid location.
            self.elf_path = None

        except Exception as e:
            print(f"Warning: ELF path auto-detect error: {e}")
            self.elf_path = None
    
    def _setup_ui(self):
        """Build the Welcome page UI with automation controls."""
        # Set background
        self.tab_frame.config(bg="#DFDFDF")
        
        # Title
        title = tk.Label(
            self.tab_frame,
            text="SmartBU Test Automation",
            font=("Inter Bold", 20),
            bg="#DFDFDF",
            fg="#0066B3"
        )
        title.pack(pady=20)
        
        # === Variant Selection Section ===
        variant_frame = tk.LabelFrame(
            self.tab_frame,
            text="Handle Type Selection",
            font=("Inter SemiBold", 12),
            bg="#DFDFDF",
            fg="#F39C12",
            padx=20,
            pady=15
        )
        variant_frame.pack(padx=20, pady=10, fill="x")
        
        self.non_driver_cb = tk.Checkbutton(
            variant_frame,
            text="Non-Driver (without NFC)",
            variable=self.selected_variant,
            onvalue=1,
            offvalue=0,
            command=self._on_variant_changed,
            font=("Inter", 11),
            bg="#DFDFDF"
        )
        self.non_driver_cb.pack(anchor="w", pady=5)
        
        self.driver_cb = tk.Checkbutton(
            variant_frame,
            text="Driver (with NFC)",
            variable=self.selected_variant,
            onvalue=2,
            offvalue=0,
            command=self._on_variant_changed,
            font=("Inter", 11),
            bg="#DFDFDF"
        )
        self.driver_cb.pack(anchor="w", pady=5)
        
        # === Status Section ===
        status_frame = tk.LabelFrame(
            self.tab_frame,
            text="Automation Status",
            font=("Inter SemiBold", 12),
            bg="#DFDFDF",
            fg="#F39C12",
            padx=20,
            pady=15
        )
        status_frame.pack(padx=20, pady=10, fill="x")
        
        self.status_label = tk.Label(
            status_frame,
            text="Status: Ready",
            bg="#DFDFDF",
            font=("Inter", 11),
            fg="#0066B3"
        )
        self.status_label.pack(anchor="w", pady=5)
        
        # === Test Control Section ===
        control_frame = tk.LabelFrame(
            self.tab_frame,
            text="Test Control",
            font=("Inter SemiBold", 12),
            bg="#DFDFDF",
            fg="#F39C12",
            padx=20,
            pady=15
        )
        control_frame.pack(padx=20, pady=10, fill="x")
        
        # Start button
        self.start_btn = tk.Button(
            control_frame,
            text="Start Automation Testing",
            command=self._start_automation,
            bg="#4CAF50",
            fg="white",
            font=("Inter SemiBold", 12),
            padx=30,
            pady=10,
            cursor="hand2"
        )
        self.start_btn.pack(pady=10)
        
        # Timer
        self.timer_label = tk.Label(
            control_frame,
            text="Time: 00:00:00",
            bg="#DFDFDF",
            font=("Inter SemiBold", 11),
            fg="#FF6B6B"
        )
        self.timer_label.pack(pady=5)
        
        # Download button
        self.download_btn = tk.Button(
            control_frame,
            text="Download Report",
            command=self._download_report,
            bg="#9C9C9C",
            fg="white",
            font=("Inter SemiBold", 12),
            padx=30,
            pady=10,
            cursor="hand2",
            state="disabled"
        )
        self.download_btn.pack(pady=10)

        # Open reports folder button
        self.open_folder_btn = tk.Button(
            control_frame,
            text="Open Reports Folder",
            command=self._open_reports_folder,
            bg="#607D8B",
            fg="white",
            font=("Inter SemiBold", 10),
            padx=20,
            pady=6,
            cursor="hand2"
        )
        self.open_folder_btn.pack(pady=4)
        
        # === ELF Path Display ===
        elf_frame = tk.Frame(self.tab_frame, bg="#DFDFDF")
        elf_frame.pack(padx=20, pady=10, fill="x")
        
        elf_label = tk.Label(
            elf_frame,
            text=f"ELF Path: {self.elf_path}",
            font=("Inter", 9),
            bg="#DFDFDF",
            fg="#666666",
            wraplength=700,
            justify="left"
        )
        elf_label.pack(anchor="w")
    
    def _on_variant_changed(self):
        """Handle variant selection change."""
        variant = self.selected_variant.get()
        if variant == 1:
            self.status_label.config(text="Status: Non-Driver (without NFC) selected")
        elif variant == 2:
            self.status_label.config(text="Status: Driver (with NFC) selected")
    
    def _start_automation(self):
        """Start the automation testing workflow."""
        if self.testing_in_progress:
            messagebox.showwarning("In Progress", "Testing is already running!")
            return
        
        variant = self.selected_variant.get()
        if variant == 0:
            messagebox.showwarning("Selection Required", "Please select Handle Type (Driver or Non-Driver)")
            return
        
        # Disable start button
        self.start_btn.config(state="disabled", bg="#CCCCCC")
        self.testing_in_progress = True
        self.testing_complete = False
        self.start_time = time.time()
        
        # Update status
        variant_name = "Driver" if variant == 2 else "Non-Driver"
        self.status_label.config(text=f"Status: {variant_name} - Testing started...", fg="#FF9800")
        
        # Start timer
        self._update_timer()
        
        # Run automation in background thread
        thread = threading.Thread(
            target=self._run_automation_thread,
            args=(variant,),
            daemon=True
        )
        thread.start()
    
    def _update_timer(self):
        """Update and display the timer."""
        if self.testing_in_progress:
            elapsed = int(time.time() - self.start_time)
            hours = elapsed // 3600
            minutes = (elapsed % 3600) // 60
            seconds = elapsed % 60
            
            time_str = f"Time: {hours:02d}:{minutes:02d}:{seconds:02d}"
            self.timer_label.config(text=time_str)
            
            # Schedule next update
            self.tab_frame.after(1000, self._update_timer)
    
    def _run_automation_thread(self, variant):
        """Run the automation workflow in a background thread."""
        try:
            # Helper function to wait for status label to reach expected state
            def wait_for_status(expected_text, timeout_sec=60):
                """Poll status label until it contains expected_text or timeout."""
                start_time = time.time()
                while time.time() - start_time < timeout_sec:
                    current_text = self.status_label.cget("text")
                    if expected_text in current_text:
                        return True
                    time.sleep(0.2)  # Poll every 200ms
                return False
            
            # Step 0: Validate prerequisites (MANDATORY)
            self.status_label.config(text="Status: Validating prerequisites...", fg="#FF9800")
            
            # Check if ELF path exists - MUST exist before proceeding
            if not self.elf_path:
                raise Exception("ELF path could not be determined")
            
            elf_path_obj = Path(self.elf_path)
            if not elf_path_obj.exists():
                raise Exception(f"ELF path does not exist: {self.elf_path}\n\nPlease ensure SmartBU folder exists at the expected location")
            
            # Step 1: Connect Trace32 using the GUI's existing functions
            # MANDATORY: Trace32 must be connected to proceed
            self.status_label.config(text="Status: Connecting Trace32...", fg="#FF9800")
            
            try:
                # Wrapper to convert repo path to GUI's expected entry widget
                class DummyEntry:
                    def __init__(self, path):
                        self.path = path
                    def get(self):
                        return self.path
                
                # Patch messagebox.showerror BEFORE importing Trace32ConnectApp
                # This ensures any error dialogs called from within are suppressed
                import tkinter.messagebox as msg_box
                original_showerror = msg_box.showerror
                
                def silent_error(*args, **kwargs):
                    """Suppressed error dialog - do nothing"""
                    pass
                
                msg_box.showerror = silent_error
                
                try:
                    # Import and call the GUI's connection function
                    from Functional.trace32 import Trace32ConnectApp

                    dummy_entry = DummyEntry(self.elf_path)
                    # Trace32ConnectApp expects a selected_preset-like object
                    class DummySelectedPreset:
                        def __init__(self, val):
                            self._val = val
                        def get(self):
                            return self._val

                    dummy_preset = DummySelectedPreset(variant)

                    # Call Trace32ConnectApp - pass objects that implement .get()
                    Trace32ConnectApp(dummy_entry, dummy_preset, self.status_label)

                finally:
                    # Always restore original error handler
                    msg_box.showerror = original_showerror
                
                # Wait for the status to show "stopped at breakpoint" (orange)
                if not wait_for_status("stopped at breakpoint", timeout_sec=30):
                    raise Exception("Trace32 connection timeout - status did not change to 'stopped at breakpoint'")
                
                # Step 2: Start Code (Go)
                self.status_label.config(text="Status: Starting code execution...", fg="#FF9800")
                
                from Functional.trace32 import RunCode
                RunCode(self.status_label)
                
                # Wait for the status to show "running" (green)
                if not wait_for_status("running", timeout_sec=30):
                    raise Exception("Code start timeout - status did not change to 'running'")
                
            except Exception as e:
                # Connection FAILED - STOP automation
                error_msg = str(e)
                print(f"[ERROR] Trace32 connection failed: {error_msg}")
                self.status_label.config(
                    text=f"Status: [ABORTED] Trace32 connection failed",
                    fg="#F44336"
                )
                self.testing_in_progress = False
                self.start_btn.config(state="normal", bg="#4CAF50")
                messagebox.showerror(
                    "Connection Failed", 
                    f"Trace32 connection failed. Automation aborted.\n\nError: {error_msg}"
                )
                return  # EXIT - do not proceed with tests
            
            # Step 3: Run all automation tests (ONLY if Trace32 is connected)
            self.status_label.config(text="Status: Running tests...", fg="#FF9800")
            
            # Import test orchestrator - ensure project root is on sys.path
            if str(ROOT) not in sys.path:
                sys.path.insert(0, str(ROOT))
            if str(ROOT / "automation") not in sys.path:
                sys.path.insert(0, str(ROOT / "automation"))
            from automation.core.orchestrator import orchestrate_tests

            # Execute tests (this function handles report generation)
            orchestration_output = orchestrate_tests()
            # orchestration_output is a dict with keys 'results' and 'summary'
            results = orchestration_output.get('results', [])
            
            # Step 4: Mark as complete
            self.testing_complete = True
            self.testing_in_progress = False
            
            # Update UI
            self.status_label.config(text="Status: [OK] Testing Complete!", fg="#4CAF50")
            self.start_btn.config(state="normal", bg="#4CAF50")
            self.download_btn.config(state="normal", bg="#2196F3")  # Enable download
            
        except Exception as e:
            self.testing_in_progress = False
            error_msg = str(e)[:80]
            print(f"[ERROR] Automation failed: {e}")
            self.status_label.config(
                text=f"Status: [ERROR] {error_msg}",
                fg="#F44336"
            )
            self.start_btn.config(state="normal", bg="#4CAF50")
            messagebox.showerror("Automation Error", f"Testing failed:\n{str(e)}")
    
    def _download_report(self):
        """Handle report download action."""
        if not self.testing_complete:
            messagebox.showinfo("Not Ready", "Please complete testing first!")
            return
        
        try:
            # Locate the latest report
            from pathlib import Path
            reports_dir = ROOT / "automation" / "reports" / "output"
            
            if not reports_dir.exists():
                messagebox.showerror("No Reports", "No test reports found!")
                return
            
            # Find the newest Excel report (ignore Excel temporary files starting with ~$)
            candidates = [f for f in reports_dir.glob("*.xlsx") if not f.name.startswith("~$")]
            excel_files = sorted(candidates, key=lambda f: f.stat().st_mtime, reverse=True)

            if not excel_files:
                messagebox.showerror("No Reports", "No Excel reports found!")
                return

            latest_report = excel_files[0]

                # Open the latest report directly (don't create another timestamped copy)
                try:
                    try:
                        os.startfile(str(latest_report))
                    except Exception:
                        import subprocess
                        subprocess.Popen(["cmd", "/c", "start", "", str(latest_report)])
                except Exception as e:
                    messagebox.showerror("Open Failed", f"Failed to open report: {e}")
                    return

                # Ask user if they want to copy the full path to clipboard
                do_copy = messagebox.askyesno(
                    "Success",
                    f"Latest report copied to:\n{new_path.name}\n\nFull path:\n{new_path}\n\nCopy full path to clipboard?"
                )
                if do_copy:
                    try:
                        self.tab_frame.clipboard_clear()
                        self.tab_frame.clipboard_append(str(new_path))
                        messagebox.showinfo("Copied", "Full path copied to clipboard.")
                    except Exception as ce:
                        messagebox.showerror("Copy Failed", f"Failed to copy path: {ce}")
            except Exception as e:
                # If copy/open failed, fallback to opening original and offer copy
                try:
                    os.startfile(str(latest_report))
                except Exception:
                    import subprocess
                    subprocess.Popen(rf'explorer /select,"{latest_report}"')
                do_copy = messagebox.askyesno(
                    "Success",
                    f"Latest report:\n{latest_report.name}\n\nFull path:\n{latest_report}\n\nCopy full path to clipboard?"
                )
                if do_copy:
                    try:
                        self.tab_frame.clipboard_clear()
                        self.tab_frame.clipboard_append(str(latest_report))
                        messagebox.showinfo("Copied", "Full path copied to clipboard.")
                    except Exception as ce:
                        messagebox.showerror("Copy Failed", f"Failed to copy path: {ce}")
            
        except Exception as e:
            messagebox.showerror("Download Error", f"Failed to open report:\n{str(e)}")


    def _open_reports_folder(self):
        """Open the reports output folder in Explorer."""
        try:
            reports_dir = ROOT / "automation" / "reports" / "output"
            if not reports_dir.exists():
                messagebox.showinfo("No Reports", "Reports folder does not exist yet.")
                return

            # Use os.startfile for Windows to open the folder
            try:
                os.startfile(str(reports_dir))
            except Exception:
                # Fallback to explorer
                import subprocess
                subprocess.Popen(["explorer", str(reports_dir)])

        except Exception as e:
            messagebox.showerror("Open Folder Error", f"Failed to open reports folder:\n{e}")


def create_welcome_tab(notebook, images, relative_to_assets):
    """
    Create and integrate the Welcome tab into the notebook.
    
    Args:
        notebook: ttk.Notebook widget
        images: dict to store PhotoImage references
        relative_to_assets: function to resolve asset paths
    
    Returns:
        The Welcome page automation controller instance
    """
    # Create tab frame using ttk
    tab1 = ttk.Frame(notebook)
    notebook.add(tab1, text="Welcome")
    
    # Create inner frame for content
    tab1_frame = tk.Frame(tab1, bg="#DFDFDF")
    tab1_frame.pack(fill="both", expand=True)
    
    # Create automation controller (builds its own UI)
    welcome_automation = WelcomePageAutomation(tab1_frame)
    
    return welcome_automation
