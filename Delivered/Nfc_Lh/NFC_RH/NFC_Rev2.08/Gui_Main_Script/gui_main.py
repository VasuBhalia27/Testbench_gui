import sys
from pathlib import Path
import tkinter as tk
from tkinter import ttk, Button, PhotoImage
import ctypes

# Allow running this script from Gui_Main_Script while importing sibling
# top-level packages such as Functional and AutomationScripts.
_REPO_ROOT = Path(__file__).resolve().parent.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

#from Functional.power_supply import *
from Functional.trace32 import *
from tkinter import filedialog
from tkinter import messagebox

# Automation framework imports
from AutomationScripts.core import gui_automation, integrated_automation

# Manual test report generator
from ManualTest.manual_report import save_manual_report as _save_manual_report

# Software revision — shown in window title and embedded in report filename/header
_SW_REVISION = "NFC_Rev2.08"
     
class  ToolBar:
    def __init__(self, parent, tab, tab_frame, canvas, images, relative_to_assets, run_code_callback, pause_code_callback):
        
        self.parent = parent
        self.tab = tab
        self.tab_frame = tab_frame
        self.canvas = canvas
        self.images = images
        self.relative_to_assets = relative_to_assets
        self.run_code_callback = run_code_callback
        self.pause_code_callback = pause_code_callback
        
        self.gui_for_toolbar()
        
    def gui_for_toolbar(self):
        
        self.code_exec_stat_lab = tk.Label(self.tab, text="Code Execution status: Not running")
        self.code_exec_stat_lab.config(bg = "#DFDFDF")
        self.code_exec_stat_lab.place(x=750, y=10)
        
        self.images[f"{self.tab}tab6_toptoolbar"] = PhotoImage(file=self.relative_to_assets("top_toolbar.png", "tab6")) #tool bar
        self.canvas.create_image(179, 19, image=self.images[f"{self.tab}tab6_toptoolbar"]) 
        
        self.canvas.create_text(
        168.0,
        28.0,
        anchor="nw",
        text=" Run code",
        fill="#6E6E6E",
        font=("Inter SemiBold", 11 * -1)
        )
        
        self.canvas.create_text(
            80.0,
            28.0,
            anchor="nw",
            text="Pause code",
            fill="#6E6E6E",
            font=("Inter SemiBold", 11 * -1)
        )
        self.images[f"{self.tab}tab6_toolbar_pausebutton1"] = PhotoImage(file=self.relative_to_assets("toolbar_pausebutton.png", "tab6"))
        self.toolbar_pausebutton = Button(self.tab, image=self.images[f"{self.tab}tab6_toolbar_pausebutton1"], command=lambda: self.pause_code_callback(self.code_exec_stat_lab),  bd = 0)
        self.toolbar_pausebutton.place(x=100, y=5, width=22.99, height=22.99)
        
                
        self.images[f"{self.tab}toolbar_playbutton1"] = PhotoImage(file=self.relative_to_assets("set_or_get_voltage.png", "tab2"))
        self.toolbar_playbutton = Button(self.tab, image=images[f"{self.tab}toolbar_playbutton1"], command=lambda: self.run_code_callback(self.code_exec_stat_lab), bd = 0)
        self.toolbar_playbutton.place(x=182, y=5, width=26, height=26)
        
        self.images[f"{self.tab}toolbar_exitbutton1"] = PhotoImage(file=self.relative_to_assets("toolbar_exitbutton.png", "tab2"))
        self.toolbar_exitbutton = Button(self.tab, image=self.images[f"{self.tab}toolbar_exitbutton1"], command=lambda: print("Exit ... "), bd = 0)
        self.toolbar_exitbutton.place(x=261, y=8, width=15, height=15)

        self.canvas.create_text(
            260.0,
            28.0,
            anchor="nw",
            text="Exit",
            fill="#FF0202",
            font=("Inter SemiBold", 11 * -1)
        )

def browse_repo_path():
    folder_path = filedialog.askdirectory(mustexist=False)
    if folder_path:
        repo_path_entry.delete(0, "end")
        repo_path_entry.insert(0, folder_path)
        repo_path_entry.xview_moveto(1)   # scroll so long paths stay visible



# ===================================================================================================================
# ========== Initializations ========================================================================================

# Define global image reference dictionary to prevent garbage collection
images = {}

# Base Paths
OUTPUT_PATH = _REPO_ROOT
DEFAULT_SMARTBU_PATH = (_REPO_ROOT / "SmartBU") if (_REPO_ROOT / "SmartBU").exists() else _REPO_ROOT
ASSETS_PATH_TAB1 = OUTPUT_PATH / Path(r"assets_GC\Page_1(Welcome_page)\assets\frame0")
ASSETS_PATH_TAB2 = OUTPUT_PATH / Path(r"assets_GC\Page_2(Settings)\assets\frame0")
ASSETS_PATH_TAB3 = OUTPUT_PATH / Path(r"assets_GC\Page_3(Led)\assets\frame0")
ASSETS_PATH_TAB4 = OUTPUT_PATH / Path(r"assets_GC\Page_4(BattMon)\assets\frame0")
ASSETS_PATH_TAB5 = OUTPUT_PATH / Path(r"assets_GC\Page_5(Motor)\assets\frame0")
ASSETS_PATH_TAB6 = OUTPUT_PATH / Path(r"assets_GC\Page_6(Eos)\assets\frame0")
ASSETS_PATH_TAB7 = OUTPUT_PATH / Path(r"assets_GC\Page_7(Sg)\assets\frame0")
ASSETS_PATH_TAB8 = OUTPUT_PATH / Path(r"assets_GC\Page_8(Capa)\assets\frame0")
ASSETS_PATH_TAB9 = OUTPUT_PATH / Path(r"assets_GC\Page_9(Nfc)\assets\frame0")
ASSETS_PATH_TAB_NFC_SELF = ASSETS_PATH_TAB9  # reuse NFC assets for the NFC SELF tab
ASSETS_PATH_TAB10 = OUTPUT_PATH / Path(r"assets_GC\Page_10(CAN)\assets\frame0")
ASSETS_PATH_TAB11 = OUTPUT_PATH / Path(r"assets_GC\Page_11(Lin)\assets\frame0")
ASSETS_PATH_TAB12 = OUTPUT_PATH / Path(r"assets_GC\Page_12(Auto)\assets\frame0")

def relative_to_assets(path: str, tab: str) -> Path:
    if tab == "tab1":
        return ASSETS_PATH_TAB1 / Path(path)
    elif tab == "tab2":
        return ASSETS_PATH_TAB2 / Path(path)
    elif tab == "tab3":
        return ASSETS_PATH_TAB3 / Path(path)
    elif tab == "tab4":
        return ASSETS_PATH_TAB4 / Path(path)
    elif tab == "tab5":
        return ASSETS_PATH_TAB5 / Path(path)
    elif tab == "tab6":
        return ASSETS_PATH_TAB6 / Path(path)
    elif tab == "tab7":
        return ASSETS_PATH_TAB7 / Path(path)
    elif tab == "tab8":
        return ASSETS_PATH_TAB8 / Path(path)
    elif tab == "tab9":
        return ASSETS_PATH_TAB9 / Path(path)
    elif tab == "tab_nfc_self":
        return ASSETS_PATH_TAB_NFC_SELF / Path(path)
    elif tab == "tab10":
        return ASSETS_PATH_TAB10 / Path(path)
    elif tab == "tab11":
        return ASSETS_PATH_TAB11 / Path(path)
    elif tab == "tab12":
        return ASSETS_PATH_TAB12 / Path(path)
    else:
        raise Exception

# Create the main window
window = tk.Tk()
window.title(f"SmartBU Testbench GUI  —  {_SW_REVISION}")


window.geometry("973x670")
window.configure(bg="#DFDFDF")

# Create notebook (tab container)
notebook = ttk.Notebook(window)
notebook.pack(fill="both", expand=True)

entrybox_style = ttk.Style()
entrybox_style.theme_use('clam')
entrybox_style.configure('Background_grey.TEntry',
    fieldbackground='#DFDFDF',
    foreground="#2C2C2C",
    insertcolor='#FFFFFF'
)


# ===================================================================================================================
# ========== Dimensionsing ==========================================================================================

tablet1_X = 243
tablet1_Y = 192

# ===================================================================================================================
# ========== TAB 1 (Automation) ======================================================================================

tab1 = ttk.Frame(notebook)
notebook.add(tab1, text="Automation")

tab1_frame = tk.Frame(tab1, bg="#DFDFDF")
tab1_frame.pack(fill="both", expand=True)

# Create and embed the automation GUI in TAB 1
automation_gui = gui_automation.AutomationGUI(parent_widget=tab1_frame)

# Callbacks to lock/unlock other tabs
def lock_other_tabs():
    """Disable all tabs except TAB 1 during automation."""
    for idx in range(1, notebook.index("end")):
        try:
            notebook.tab(idx, state="disabled")
        except:
            pass

def unlock_other_tabs():
    """Re-enable all tabs after automation completes."""
    for idx in range(1, notebook.index("end")):
        try:
            notebook.tab(idx, state="normal")
        except:
            pass

# Create and attach the automation runner
automation_runner = integrated_automation.IntegratedAutomationRunner(
    gui_automation=automation_gui,
    lock_tabs_callback=lock_other_tabs,
    unlock_tabs_callback=unlock_other_tabs,
)
automation_gui.set_automation_runner(automation_runner)

# ===================================================================================================================
# ===================================================================================================================
# ========== TAB 2 (Settings) =======================================================================================

def preset_realwithdebinfo(selected_preset):
    if selected_preset.get() == 1:
        selected_preset.set(1)
    else:
        selected_preset.set(0)

def preset_minsizerel(selected_preset):
    if selected_preset.get() == 2:
        selected_preset.set(2)
    else:
        selected_preset.set(0)

tab2 = ttk.Frame(notebook)
notebook.add(tab2, text="Settings")

# Select the second tab (Settings) by default on startup
notebook.select(tab2)

tab2_frame = tk.Frame(tab2, bg="#DFDFDF")
tab2_frame.pack(fill="both", expand=True)

canvas2 = tk.Canvas(
    tab2_frame,
    bg="#DFDFDF",
    height=651,
    width=973,
    bd=0,
    highlightthickness=0,
    relief="ridge"
)
canvas2.place(x=0, y=0)

def update_tab_visibility():
    # value 1 = Non-Nfc, value 2 = Nfc
    selection = selected_preset.get()
    
    if selection == 1:
        notebook.add(tab3, text="LED")
        notebook.add(tab4, text="BAT")
        notebook.add(tab5, text="MOT")
        notebook.add(tab6, text="EOS")
        notebook.add(tab7, text="SG")
        notebook.add(tab8, text="CAP")
        notebook.add(tab11, text="LIN")
        # Hide NFC, NFC SELF and CAN tabs (NFC-variant only)
        notebook.hide(tab9)
        notebook.hide(tab_nfc_self)
        notebook.hide(tab10)
    elif selection == 2:
        # Show NFC, NFC SELF and CAN
        notebook.add(tab3, text="LED")
        notebook.add(tab4, text="BAT")
        notebook.add(tab5, text="MOT")
        notebook.add(tab6, text="EOS")
        notebook.add(tab7, text="SG")
        notebook.add(tab8, text="CAP")
        # We use add() to bring them back if they were hidden
        notebook.add(tab9, text="NFC")
        notebook.add(tab_nfc_self, text="NFC SELF")
        notebook.add(tab10, text="CAN")
        notebook.add(tab11, text="LIN")

# ===================================================================================================================
# ========== Tile-1 =================================================================================================
images["minibea_logo_2"] = PhotoImage(file=relative_to_assets("minebea_logo_2.png", "tab2"))
canvas2.create_image(145.0, 37.0, image=images["minibea_logo_2"])

images["tile1_tab2"] = PhotoImage(file=relative_to_assets("Tile.png", "tab2")) 
canvas2.create_image(245, 265, image=images["tile1_tab2"])

# --- Group 1: Path Selection ---
canvas2.create_rectangle(55.0, 65.0, 750.0, 135.0, outline="#F39C12", width=1) 
canvas2.create_text(60.0, 65.0, anchor="nw", text=" Path Setting ", fill="#F39C12", font=("Inter SemiBold", 10))

canvas2.create_text(61.0, 100.0, anchor="nw", text="Select ELF path:  ", fill="#FFFFFF", font=("Inter SemiBold", 15 * -1))
repo_path_entry = ttk.Entry(tab2, style ='Background_grey.TEntry')
repo_path_entry.insert(0, DEFAULT_SMARTBU_PATH.as_posix())
repo_path_entry.place(x=200.0, y=95.0, width=400.0, height=30.0)
#Brouse button
repo_browse_button = ttk.Button(tab2, text="Browse", command=browse_repo_path) #browse button to get repo path
repo_browse_button.place(x=650, y=95, width=80, height=30)

# --- Group 2: Version Control ---
canvas2.create_rectangle(55.0, 150.0, 550.0, 230.0, outline="#F39C12", width=1)
canvas2.create_text(60.0, 155.0, anchor="nw", text=" Variant Setting ", fill="#F39C12", font=("Inter SemiBold", 10))

#Non-Nfc version selection
selected_preset = tk.IntVar(value=2)
selected_preset_relwithdeb = tk.Checkbutton(tab2, text="Non-Nfc Version", variable=selected_preset, onvalue=1, offvalue=0, command=lambda: [preset_realwithdebinfo(selected_preset), update_tab_visibility()])
selected_preset_relwithdeb.place(x=61, y=180)
#Nfc version selection
selected_preset_minsizerel = tk.Checkbutton(
    tab2, 
    text="Nfc Version", 
    variable=selected_preset, 
    onvalue=2, 
    offvalue=0, 
    command=lambda: [preset_minsizerel(selected_preset), update_tab_visibility()]
)
selected_preset_minsizerel.place(x=450, y=180)

# --- Group 3: Debugger ---
canvas2.create_rectangle(55.0, 240.0, 550.0, 380.0, outline="#F39C12", width=1)
canvas2.create_text(60.0, 240.0, anchor="nw", text=" Debugger Setting ", fill="#F39C12", font=("Inter SemiBold", 10))
#Connect Trace32 Button
canvas2.create_text(61.0, 270.0, anchor="nw", text="Connect Trace32", fill="#FFFFFF", font=("Inter SemiBold", 15 * -1))
images["tab2_connect_trace32"] = PhotoImage(file=relative_to_assets("tab_testrun_button.png", "tab2"))
def _on_connect_trace32():
    deflash_warning_lbl.config(text="")
    deflash_progress["value"] = 0
    window.update_idletasks()

    if code_status_label:
        code_status_label.config(text="Status: Flashing in progress", fg="blue")

    def update_progress(percent):
        deflash_progress["value"] = percent
        window.update_idletasks()

    try:
        Trace32ConnectApp(repo_path_entry, selected_preset, code_status_label, progress_callback=update_progress)
        deflash_progress["value"] = 100
        window.update_idletasks()
    except Exception:
        if code_status_label:
            code_status_label.config(text="Status: Flashing ERROR", fg="#C0392B")

connect_trace32 = Button(tab2, image=images["tab2_connect_trace32"], 
                         command=_on_connect_trace32, 
                         bd = 0)
connect_trace32.place(x=200, y=260, width=34, height=34)

# Start Code (Go) Button
canvas2.create_text(61.0, 315.0, anchor="nw", text="Start Code (Go)", fill="#FFFFFF", font=("Inter SemiBold", 15 * -1))
images["tab2_go_button"] = PhotoImage(file=relative_to_assets("tab_testrun_button.png", "tab2"))
go_button = Button(tab2, image=images["tab2_go_button"], command=lambda: RunCode(code_status_label), bd=0)
go_button.place(x=200, y=305, width=34, height=34)

#Disconnect Trace32 Button
canvas2.create_text(350, 270.0, anchor="nw", text="Disconnect Trace32", fill="#FFFFFF", font=("Inter SemiBold", 15 * -1))
images["tab2_disconnect_trace32"] = PhotoImage(file=relative_to_assets("tab_testrun_button.png", "tab2"))
def _on_disconnect_trace32():
    df_result = None
    deflash_warning_lbl.config(text="De-flash in progress, don't close     GUI window")
    deflash_progress["value"] = 100
    window.update_idletasks()
    
    def update_progress(percent):
        deflash_progress["value"] = max(0, min(100, 100 - percent))
        window.update_idletasks()
    
    try:
        code_status_label.config(text="Status: De-flashing...", fg="blue")
        df_result = DeflashPcb(code_status_label, progress_callback=update_progress)
        if df_result and df_result.get("pass"):
            code_status_label.config(text="Status: De-flash PASS", fg="#27AE60")
        else:
            code_status_label.config(text="Status: De-flash FAILED", fg="#C0392B")
    except Exception as exc:
        df_result = {
            "pass": False,
            "duration": 0.0,
            "addrs": [],
            "blank_fail": [],
            "detail": str(exc) or "De-flash failed",
        }
        code_status_label.config(text=f"Status: De-flash ERROR", fg="#C0392B")
    finally:
        deflash_progress["value"] = 0
        deflash_warning_lbl.config(text="De-flash Done")

    _collect_and_save_all_manual_tests(deflash_result=df_result)
    QuitTrace32(code_status_label)
    # Keep "De-flash Done" visible in notification area
    manual_scan_entry.delete(0, tk.END)
    manual_scan_entry.focus_set()
    automation_gui.scan_code.set("")
    automation_gui.root.after(100, automation_gui.scan_entry.focus_set)
disconnect_trace32 = Button(tab2, image=images["tab2_disconnect_trace32"],
                            command=_on_disconnect_trace32,
                            bd = 0)
disconnect_trace32.place(x=500, y=260, width=34, height=34)

# Reset Target Button
canvas2.create_text(350.0, 315.0, anchor="nw", text="Reset Target", fill="#FFFFFF", font=("Inter SemiBold", 15 * -1))
# Button Image and Placement
images["tab2_reset_target"] = PhotoImage(file=relative_to_assets("tab_testrun_button.png", "tab2"))
reset_target_btn = Button(tab2, image=images["tab2_reset_target"], 
                          command=lambda: ResetTarget(code_status_label), 
                          bd=0)
reset_target_btn.place(x=500, y=305, width=34, height=34)

# Label to show status
code_status_label = tk.Label(tab2, text="Status: none", bg="#DFDFDF", font=("Inter", 10))
code_status_label.place(x=250, y=350)

# --- Group 4: CANoe ---
canvas2.create_rectangle(55.0, 390.0, 550.0, 480.0, outline="#F39C12", width=1)
canvas2.create_text(60.0, 395.0, anchor="nw", text=" CANoe Setting", fill="#F39C12", font=("Inter SemiBold", 10))

# CANoe disable option
canoe_input_condition = tk.IntVar (value=1)

canvas2.create_text(180.0, 422.0, anchor="nw", text="IsCanoeDisable", fill="#FFFFFF", font=("Inter SemiBold", 15 * -1))
tab2_entry_1 = ttk.Entry(tab2_frame, style ='Background_grey.TEntry')
# Check the default variable value (if 1, set "1(Yes)", else "0(No)")
initial_text = "1(Yes)" if canoe_input_condition.get() == 1 else "0(No)"
tab2_entry_1.insert(0, initial_text)
tab2_entry_1.place(x=290.0, y=422.0, width=45.0, height=20.0)

canoe_output_variables = ["TestFw_GuiCanDependencyDisable"]
canoe_entries = [tab2_entry_1]

def update_canoe_entry_text():
    tab2_entry_1.delete(0, tk.END)
    if canoe_input_condition.get() == 1:
        tab2_entry_1.insert(1, "1(Yes)")
    else:
        tab2_entry_1.insert(0, "0(No)")

canoe_disable_cb = tk.Checkbutton(
    tab2, 
    text="CANoe_Disable", 
    variable=canoe_input_condition, 
    onvalue=1, 
    offvalue=0, 
    command=lambda: [CANoe_Disable(canoe_input_condition),
                     SendDIDGetVal_multiple_entry(canoe_output_variables, canoe_entries, 0) ,update_canoe_entry_text()])
canoe_disable_cb.place(x=61, y=420)
#CANoe enable option
canoe_enable_cb = tk.Checkbutton(
    tab2, 
    text="CANoe_Enable", 
    variable=canoe_input_condition, 
    onvalue=2, 
    offvalue=0, 
    command=lambda: [CANoe_Enable(canoe_input_condition), 
                    SendDIDGetVal_multiple_entry(canoe_output_variables, canoe_entries, 0), update_canoe_entry_text()])
canoe_enable_cb.place(x=440, y=420)

# --- 2D Scan entry (top-right of Settings tab) ---
canvas2.create_text(425.0, 24.0, anchor="nw", text="2D Scan:", fill="#FFFFFF", font=("Inter SemiBold", 15, "bold"))
_scan_vcmd = (window.register(lambda s: len(s) <= 20), "%P")
manual_scan_entry = tk.Entry(tab2, font=("Courier", 14, "bold"), bg="#DFDFDF", fg="#2C2C2C", insertbackground="#2C2C2C", relief="solid", bd=1, validate="key", validatecommand=_scan_vcmd)
manual_scan_entry.place(x=525.0, y=20.0, width=225.0, height=30.0)
window.after(300, manual_scan_entry.focus_set)

# --- Manual PASS / FAIL counter widget (right of Variant Setting) ---
_manual_pass_lbl = tk.Label(
    tab2, text="PASS\n0",
    font=("Arial", 18, "bold"),
    fg="#FFFFFF", bg="#27AE60",
    width=6, height=3, relief="flat",
)
_manual_pass_lbl.place(x=555, y=153)

_manual_fail_lbl = tk.Label(
    tab2, text="FAIL\n0",
    font=("Arial", 18, "bold"),
    fg="#FFFFFF", bg="#C62828",
    width=6, height=3, relief="flat",
)
_manual_fail_lbl.place(x=655, y=153)

def _reset_manual_counts():
    global _manual_pass_count, _manual_fail_count
    _manual_pass_count = 0
    _manual_fail_count = 0
    _manual_pass_lbl.config(text="PASS\n0")
    _manual_fail_lbl.config(text="FAIL\n0")

tk.Button(
    tab2, text="Reset Count",
    font=("Arial", 9, "bold"),
    fg="#FFFFFF", bg="#555555",
    activebackground="#333333", activeforeground="#FFFFFF",
    relief="flat", cursor="hand2",
    command=_reset_manual_counts,
).place(x=555, y=253, width=195, height=26)

deflash_progress = ttk.Progressbar(tab2, mode="determinate", maximum=100)
deflash_progress.place(x=555, y=285, width=195, height=10)
deflash_progress["value"] = 0

deflash_warning_lbl = tk.Label(
    tab2,
    text="",
    fg="#FFFFFF",
    bg="#E74C3C",
    font=("Arial", 9, "bold"),
    anchor="nw",
    justify="left",
    wraplength=240,
)
deflash_warning_lbl.place(x=555, y=315, width=198, height=50)

window.after(1000, lambda: poll_target_state(running_status, window))

canvas2.create_text(
    260.0,
    20.0,
    anchor="nw",
    text="U-Shin India",
    fill="#FFFFFF",
    font=("Inter BoldItalic", 24 * -1)
)

# --- Shared PASS/FAIL helpers (used by all test tabs) ---
def _set_pf(lbl, passed):
    if passed:
        lbl.config(text="✓ PASS", bg="#27AE60", fg="#FFFFFF")
    else:
        lbl.config(text="✗ FAIL", bg="#C0392B", fg="#FFFFFF")

def _set_overall(lbl, results):
    if all(results):
        lbl.config(text="OVERALL: PASS", bg="#27AE60", fg="#FFFFFF")
    else:
        lbl.config(text="OVERALL: FAIL", bg="#C0392B", fg="#FFFFFF")

def _reset_pf_labels(overall_lbl, *field_labels):
    overall_lbl.config(text="", bg="#DFDFDF", fg="#000000")
    for lbl in field_labels:
        lbl.config(text="", bg="#DFDFDF", fg="#000000")

def _parse_num(entry):
    """Return int from entry text (handles '1234 mV', '0x52', '1 bool', etc.)"""
    try:
        return int(entry.get().strip().split()[0], 0)
    except (ValueError, TypeError, IndexError):
        return None

# Create ManualTest/reports/ once at application startup
_REPORTS_DIR = _REPO_ROOT / "ManualTest" / "reports"
_REPORTS_DIR.mkdir(parents=True, exist_ok=True)

# Manual test PCB pass/fail counters — incremented in _collect_and_save_all_manual_tests()
_manual_pass_count = 0
_manual_fail_count = 0

# ===================================================================================================================
# ========== TAB 3 (LED Test) =======================================================================================

tab3 = ttk.Frame(notebook)
notebook.add(tab3, text="LED ")

tab3_frame = tk.Frame(tab3, bg="#DFDFDF")
tab3_frame.pack(fill="both", expand=True)

canvas3 = tk.Canvas(
    tab3_frame,
    bg="#DFDFDF",
    height=651,
    width=973,
    bd=0,
    highlightthickness=0,
    relief="ridge"
    
)
canvas3.place(x=0, y=0)

# ===================================================================================================================
# ========== Tile-1 =================================================================================================
images["minibea_logo_3"] = PhotoImage(file=relative_to_assets("minebea_logo_3.png", "tab3"))
canvas3.create_image(145.0, 37.0, image=images["minibea_logo_3"])

images["tile_tab3"] = PhotoImage(file=relative_to_assets("Tile.png", "tab3")) 
canvas3.create_image(tablet1_X, tablet1_Y, image=images["tile_tab3"])

# Checkboxes
led_input_condition = tk.IntVar(value=2)

led_on_cb = tk.Checkbutton(tab3, text="Led_On", variable=led_input_condition, onvalue=1, offvalue=0,
    command=lambda: [led_on(led_input_condition), led_entries.__setitem__(0, tab3_entry_led_on)])
led_on_cb.place(x=73, y=150, width=85, height=32)

led_off_cb = tk.Checkbutton(tab3, text="Led_Off", variable=led_input_condition, onvalue=2, offvalue=0,
    command=lambda: [led_off(led_input_condition), led_entries.__setitem__(0, tab3_entry_led_off)])
led_off_cb.place(x=300, y=150, width=85, height=32)

# Entries
canvas3.create_text(73.0, 113.0, anchor="nw", text="LED Test", fill="#FFFFFF", font=("Inter SemiBold", 20 * -1))

canvas3.create_text(73.0, 210.0, anchor="nw", text="Led_On Voltage", fill="#FFFFFF", font=("Inter SemiBold", 15 * -1))
tab3_entry_led_on = ttk.Entry(tab3_frame, style='Background_grey.TEntry')
tab3_entry_led_on.place(x=300.0, y=200.0, width=85.0, height=32.0)

canvas3.create_text(73.0, 250.0, anchor="nw", text="Led_Off Voltage", fill="#FFFFFF", font=("Inter SemiBold", 15 * -1))
tab3_entry_led_off = ttk.Entry(tab3_frame, style='Background_grey.TEntry')
tab3_entry_led_off.place(x=300.0, y=240.0, width=85.0, height=32.0)

tab3_entry_1 = tab3_entry_led_on  # backward-compat alias

# Execution
led_output_variables = ["TestFw_LedVoltage"]
led_entries = [tab3_entry_led_off]  # default: Led_Off selected (value=2)

tab3_lbl_voltage_on = tk.Label(tab3_frame, text="", width=6, font=("Inter SemiBold", 10), relief="flat")
tab3_lbl_voltage_on.place(x=394, y=206, height=20)
tab3_lbl_voltage_off = tk.Label(tab3_frame, text="", width=6, font=("Inter SemiBold", 10), relief="flat")
tab3_lbl_voltage_off.place(x=394, y=246, height=20)
tab3_lbl_overall = tk.Label(tab3_frame, text="", width=14, font=("Inter SemiBold", 12), relief="ridge")
tab3_lbl_overall.place(x=430, y=110, height=26)

def _evaluate_led_results():
    if led_input_condition.get() == 2:  # Led_Off: 0–10 mV expected
        v = _parse_num(tab3_entry_led_off)
        passed = v is not None and 0 <= v <= 10
        _set_pf(tab3_lbl_voltage_off, passed)
    else:  # Led_On: voltage should be > 0
        v = _parse_num(tab3_entry_led_on)
        passed = v is not None and v > 0
        _set_pf(tab3_lbl_voltage_on, passed)
    results = []
    if tab3_entry_led_on.get().strip():
        vn = _parse_num(tab3_entry_led_on)
        results.append(vn is not None and vn > 0)
    if tab3_entry_led_off.get().strip():
        vn = _parse_num(tab3_entry_led_off)
        results.append(vn is not None and 0 <= vn <= 10)
    if results:
        _set_overall(tab3_lbl_overall, results)

images["tab3_led_run"] = PhotoImage(file=relative_to_assets("tab_testrun_button.png", "tab3"))
tab3_run_btn = Button(tab3, image=images["tab3_led_run"],
                        command=lambda: [SendDIDGetVal_multiple_entry(led_output_variables, led_entries, TestFunctionCmd.TESTFW_GUI_CMD_LED_TEST_e), tab3_frame.after(200, _evaluate_led_results)],
                        bd = 0)
tab3_run_btn.place(x=225, y=106, width=34, height=34)

reset_entries = ttk.Button(tab3, text="Reset Results", command=lambda: [clear_entries([tab3_entry_led_on, tab3_entry_led_off]), _reset_pf_labels(tab3_lbl_overall, tab3_lbl_voltage_on, tab3_lbl_voltage_off)])
reset_entries.place(x=300, y=110, width=85, height=32)

canvas3.create_text(
    260.0,
    20.0,
    anchor="nw",
    text="U-Shin India",
    fill="#FFFFFF",
    font=("Inter BoldItalic", 24 * -1)
)
# ===================================================================================================================
# ===================================================================================================================
# ========== TAB 4 (Battery Monitor) ===============================================================================

tab4 = ttk.Frame(notebook)
notebook.add(tab4, text="Battery Monitor")

tab4_frame = tk.Frame(tab4, bg="#DFDFDF")
tab4_frame.pack(fill="both", expand=True)

canvas4 = tk.Canvas(
    tab4_frame,
    bg="#DFDFDF",
    height=651,
    width=973,
    bd=0,
    highlightthickness=0,
    relief="ridge"
)
canvas4.place(x=0, y=0)

# ===================================================================================================================
# ========== Tile-1 (Battery Monitor) =================================================================================
images["minibea_logo_4"] = PhotoImage(file=relative_to_assets("minebea_logo_4.png", "tab4"))
canvas4.create_image(145.0, 37.0, image=images["minibea_logo_4"])

images["tile_tab4"] = PhotoImage(file=relative_to_assets("Tile.png", "tab4")) 
canvas4.create_image(tablet1_X, tablet1_Y, image=images["tile_tab4"])

# Entries
canvas4.create_text(73.0, 113.0, anchor="nw", text="BAT Test", fill="#FFFFFF", font=("Inter SemiBold", 20 * -1))

canvas4.create_text(73.0, 168.0, anchor="nw", text="AiBatRef", fill="#FFFFFF", font=("Inter SemiBold", 15 * -1))
tab4_entry_1 = ttk.Entry(tab4_frame, style ='Background_grey.TEntry')
tab4_entry_1.place(x=300.0, y=168.0, width=85.0, height=32.0)

# Execution
batmot_output_variables = ["TestFw_AiBatRef"]
batmon_entries = [tab4_entry_1]

tab4_lbl_voltage = tk.Label(tab4_frame, text="", width=6, font=("Inter SemiBold", 10), relief="flat")
tab4_lbl_voltage.place(x=394, y=174, height=20)
tab4_lbl_overall = tk.Label(tab4_frame, text="", width=14, font=("Inter SemiBold", 12), relief="ridge")
tab4_lbl_overall.place(x=430, y=110, height=26)

def _evaluate_bat_results():
    v = _parse_num(tab4_entry_1)
    passed = v is not None and 8000 <= v <= 16000
    _set_pf(tab4_lbl_voltage, passed)
    _set_overall(tab4_lbl_overall, [passed])

images["tab4_motor_run"] = PhotoImage(file=relative_to_assets("tab_testrun_button.png", "tab4"))
tab4_run_btn = Button(tab4, image=images["tab4_motor_run"],
                        command=lambda: [SendDIDGetVal_multiple_entry(batmot_output_variables, batmon_entries, TestFunctionCmd.TESTFW_GUI_CMD_BATT_MONITOR_e), tab4_frame.after(200, _evaluate_bat_results)],
                        bd = 0)
tab4_run_btn.place(x=225, y=106, width=34, height=34)

reset_entries = ttk.Button(tab4, text="Reset Results", command=lambda: [clear_entries(batmon_entries), _reset_pf_labels(tab4_lbl_overall, tab4_lbl_voltage)])
reset_entries.place(x=300, y=106, width=85, height=32)

canvas4.create_text(
    260.0,
    20.0,
    anchor="nw",
    text="U-Shin India",
    fill="#FFFFFF",
    font=("Inter BoldItalic", 24 * -1)
)

# ===================================================================================================================
# ===================================================================================================================
# ========== TAB 5 (Motor Test) ================================================================================
tab5 = ttk.Frame(notebook)
notebook.add(tab5, text="Motor ")

tab5_frame = tk.Frame(tab5, bg="#DFDFDF")
tab5_frame.pack(fill="both", expand=True)

canvas5 = tk.Canvas(
    tab5_frame,
    bg="#DFDFDF",
    height=651,
    width=973,
    bd=0,
    highlightthickness=0,
    relief="ridge"
)
canvas5.place(x=0, y=0)
# ===================================================================================================================
# ========== Tile-1 =================================================================================================
images["minibea_logo_5"] = PhotoImage(file=relative_to_assets("minebea_logo_5.png", "tab5"))
canvas5.create_image(145.0, 37.0, image=images["minibea_logo_4"])

images["tile1_tab5"] = PhotoImage(file=relative_to_assets("Tile.png", "tab5")) 
canvas5.create_image(245, 245, image=images["tile1_tab5"])

placement_y_coord = 168


# Checkboxes
selected_motor_state = tk.IntVar(value=2)

# Entries
canvas5.create_text(73.0, 85.0, anchor="nw", text="Motor Test", fill="#FFFFFF", font=("Inter SemiBold", 20 * -1))
canvas5.create_text(73.0, placement_y_coord+35, anchor="nw", text="MotorVoltage", fill="#FFFFFF", font=("Inter SemiBold", 15 * -1))
tab5_entry1 = ttk.Entry(tab5_frame, style = 'Background_grey.TEntry')
tab5_entry1.place(x=306, y=placement_y_coord+35, width=85, height=32)


canvas5.create_text(73.0, placement_y_coord + 35*2, anchor="nw", text="MotorCurrentValue", fill="#FFFFFF", font=("Inter SemiBold", 15 * -1))
tab5_entry2 = ttk.Entry(tab5_frame, style = 'Background_grey.TEntry')
tab5_entry2.place(x=306, y=placement_y_coord + 35*2, width=85, height=32)

canvas5.create_text(73.0, placement_y_coord + 35*3, anchor="nw", text="MotorLoadError", fill="#FFFFFF", font=("Inter SemiBold", 15 * -1))
tab5_entry3 = ttk.Entry(tab5_frame, style = 'Background_grey.TEntry')
tab5_entry3.place(x=306, y=placement_y_coord + 35*3, width=85, height=32)

# Execution
motor_output_variables = ["TestFw_MotorVoltage", "TestFw_MotorCurrentValue", "TestFw_MotorLoadError"]
motor_entries = [tab5_entry1, tab5_entry2, tab5_entry3]

tab5_lbl_voltage = tk.Label(tab5_frame, text="", width=6, font=("Inter SemiBold", 10), relief="flat")
tab5_lbl_voltage.place(x=400, y=placement_y_coord+41, height=20)
tab5_lbl_current = tk.Label(tab5_frame, text="", width=6, font=("Inter SemiBold", 10), relief="flat")
tab5_lbl_current.place(x=400, y=placement_y_coord+76, height=20)
tab5_lbl_loaderr = tk.Label(tab5_frame, text="", width=6, font=("Inter SemiBold", 10), relief="flat")
tab5_lbl_loaderr.place(x=400, y=placement_y_coord+111, height=20)
tab5_lbl_overall = tk.Label(tab5_frame, text="", width=14, font=("Inter SemiBold", 12), relief="ridge")
tab5_lbl_overall.place(x=460, y=150, height=26)

def _evaluate_mot_results():
    v_volt = _parse_num(tab5_entry1)
    v_curr = _parse_num(tab5_entry2)
    v_err  = _parse_num(tab5_entry3)
    p_volt    = v_volt is not None and v_volt > 0
    p_current = v_curr is not None and v_curr > 0
    p_loaderr = v_err  is not None and v_err  == 0
    _set_pf(tab5_lbl_voltage,  p_volt)
    _set_pf(tab5_lbl_current,  p_current)
    _set_pf(tab5_lbl_loaderr,  p_loaderr)
    _set_overall(tab5_lbl_overall, [p_volt, p_current, p_loaderr])

motor_decouple_couple_cb = tk.Checkbutton(
    tab5, 
    text="DecoupleCouple", 
    variable=selected_motor_state, 
    onvalue=1, 
    offvalue=0, 
    command=lambda: [
    motor_decouple_couple(selected_motor_state),
    SendDIDGetVal_multiple_entry(motor_output_variables, motor_entries, TestFunctionCmd.TESTFW_GUI_CMD_MOTOR_TEST_e),
    # Schedule the reset after 1000ms (1 second)
    window.after(1000, lambda: auto_reset_motor_checkbox(selected_motor_state)),
    tab5_frame.after(200, _evaluate_mot_results)
    ]
)
motor_decouple_couple_cb.place(x=73.0, y=150, width=125.0, height=32.0)

#motor_no_req_cb = tk.Checkbutton(
    #tab5, 
    #text="No Req", 
    #variable=selected_motor_state, 
    #onvalue=2, 
    #offvalue=0, 
    #command=lambda: [
    #motor_no_req(selected_motor_state),
    #SendDIDGetVal_multiple_entry(motor_output_variables, motor_entries, TestFunctionCmd.TESTFW_GUI_CMD_MOTOR_TEST_e)
    #]
#)
#motor_no_req_cb.place(x=306, y=150, width=85, height=32)

reset_entries = ttk.Button(tab5, text="Reset Results", command=lambda: [clear_entries(motor_entries), _reset_pf_labels(tab5_lbl_overall, tab5_lbl_voltage, tab5_lbl_current, tab5_lbl_loaderr)])
reset_entries.place(x=306, y=150, width=85, height=32)

canvas5.create_text(
    260.0,
    20.0,
    anchor="nw",
    text="U-Shin India",
    fill="#FFFFFF",
    font=("Inter BoldItalic", 24 * -1)
)

# ===================================================================================================================
# ===================================================================================================================
# ========== TAB 6 (EOS Tests) ============================================================================
tab6 = ttk.Frame(notebook)
notebook.add(tab6, text="EOS ")

tab6_frame = tk.Frame(tab6, bg="#DFDFDF")
tab6_frame.pack(fill="both", expand=True)

canvas6 = tk.Canvas(
    tab6_frame,
    bg="#DFDFDF",
    height=651,
    width=973,
    bd=0,
    highlightthickness=0,
    relief="ridge"
)
canvas6.place(x=0, y=0)

# ---------- EOS Test ----------
images["minibea_logo_6"] = PhotoImage(file=relative_to_assets("minebea_logo_6.png", "tab6"))
canvas6.create_image(145.0, 37.0, image=images["minibea_logo_6"])

images["tile_tab6"] = PhotoImage(file=relative_to_assets("Tile.png", "tab6")) 
canvas6.create_image((tablet1_X + 0), (tablet1_Y + 10), image=images["tile_tab6"])

# Entries
canvas6.create_text(73.0, 113.0, anchor="nw", text="EOS Test", fill="#FFFFFF", font=("Inter SemiBold", 20 * -1))
canvas6.create_text(73.0, placement_y_coord+35*1, anchor="nw", text="EOS Set Voltage", fill="#FFFFFF", font=("Inter SemiBold", 15 * -1))
tab6_entry_eos_set = ttk.Entry(tab6_frame, style='Background_grey.TEntry')
tab6_entry_eos_set.place(x=225, y=placement_y_coord+35*1, width=125, height=32)

canvas6.create_text(73.0, placement_y_coord+35*2, anchor="nw", text="EOS Reset Voltage", fill="#FFFFFF", font=("Inter SemiBold", 15 * -1))
tab6_entry_eos_reset = ttk.Entry(tab6_frame, style='Background_grey.TEntry')
tab6_entry_eos_reset.place(x=225, y=placement_y_coord+35*2, width=125, height=32)

tab6_entry1 = tab6_entry_eos_set  # backward-compat alias

eos_value = tk.IntVar(value=2)

# Execution
eos_output_variables = ["TestFw_EosDiagVoltage"]
eos_entries = [tab6_entry_eos_reset]  # default: EOS Reset selected (value=2)

tab6_lbl_voltage_set = tk.Label(tab6_frame, text="", width=6, font=("Inter SemiBold", 10), relief="flat")
tab6_lbl_voltage_set.place(x=360, y=placement_y_coord+35*1+6, height=20)
tab6_lbl_voltage_reset = tk.Label(tab6_frame, text="", width=6, font=("Inter SemiBold", 10), relief="flat")
tab6_lbl_voltage_reset.place(x=360, y=placement_y_coord+35*2+6, height=20)
tab6_lbl_overall = tk.Label(tab6_frame, text="", width=14, font=("Inter SemiBold", 12), relief="ridge")
tab6_lbl_overall.place(x=430, y=110, height=26)

def _evaluate_eos_results():
    if eos_value.get() == 1:  # EOS Set: 1400–1600 mV
        v = _parse_num(tab6_entry_eos_set)
        passed = v is not None and 1400 <= v <= 1600
        _set_pf(tab6_lbl_voltage_set, passed)
    else:  # EOS Reset: 1500–3000 mV
        v = _parse_num(tab6_entry_eos_reset)
        passed = v is not None and 1500 <= v <= 3000
        _set_pf(tab6_lbl_voltage_reset, passed)
    results = []
    if tab6_entry_eos_set.get().strip():
        vn = _parse_num(tab6_entry_eos_set)
        results.append(vn is not None and 1400 <= vn <= 1600)
    if tab6_entry_eos_reset.get().strip():
        vn = _parse_num(tab6_entry_eos_reset)
        results.append(vn is not None and 1500 <= vn <= 3000)
    if results:
        _set_overall(tab6_lbl_overall, results)

eos_set_cb = tk.Checkbutton(
    tab6,
    text="EOS Set",
    variable=eos_value,
    onvalue=1,
    offvalue=0,
    command=lambda: [
    eos_set(eos_value),
    eos_entries.__setitem__(0, tab6_entry_eos_set),
    SendDIDGetVal_multiple_entry(eos_output_variables, eos_entries, TestFunctionCmd.TESTFW_GUI_CMD_EOS_TEST_e),
    tab6_frame.after(200, _evaluate_eos_results)
    ]
)
eos_set_cb.place(x=73.0, y=150, width=125.0, height=32.0)

eos_reset_cb = tk.Checkbutton(
    tab6,
    text="EOS Reset",
    variable=eos_value,
    onvalue=2,
    offvalue=0,
    command=lambda: [
        eos_reset(eos_value),
        eos_entries.__setitem__(0, tab6_entry_eos_reset),
        window.after(0, lambda: [SendDIDGetVal_multiple_entry(
            eos_output_variables,
            eos_entries,
            TestFunctionCmd.TESTFW_GUI_CMD_EOS_TEST_e
        ), tab6_frame.after(200, _evaluate_eos_results)])
    ]
)
eos_reset_cb.place(x=225.0, y=150, width=125.0, height=32.0)

#images["tab6_eos_run"] = PhotoImage(file=relative_to_assets("tab_testrun_button.png", "tab6"))
#tab6_run_btn = Button(tab6, image=images["tab6_eos_run"], command=lambda: SendDIDGetVal_multiple_entry(eos_output_variables, eos_entries, TestFunctionCmd.TESTFW_GUI_CMD_EOS_TEST_e), bd = 0)
#tab6_run_btn.place(x=225, y=106, width=34, height=34)

reset_entries = ttk.Button(tab6, text="Reset Results", command=lambda: [clear_entries([tab6_entry_eos_set, tab6_entry_eos_reset]), _reset_pf_labels(tab6_lbl_overall, tab6_lbl_voltage_set, tab6_lbl_voltage_reset)])
reset_entries.place(x=225, y=110, width=125, height=32)

canvas6.create_text(
    260.0,
    20.0,
    anchor="nw",
    text="U-Shin India",
    fill="#FFFFFF",
    font=("Inter BoldItalic", 24 * -1)
)

# ===================================================================================================================
# ===================================================================================================================
# ========== TAB 7 (SG tests) =======================================================================================

tab7 = ttk.Frame(notebook)
notebook.add(tab7, text="Strain Gauge")

tab7_frame = tk.Frame(tab7, bg="#DFDFDF")
tab7_frame.pack(fill="both", expand=True)

canvas7 = tk.Canvas(
    tab7_frame,
    bg="#DFDFDF",
    height=651,
    width=973,
    bd=0,
    highlightthickness=0,
    relief="ridge"
)
canvas7.place(x=0, y=0)
# ===================================================================================================================
# ========== Tile-1 =================================================================================================
images["minibea_logo_7"] = PhotoImage(file=relative_to_assets("minebea_logo_7.png", "tab7"))
canvas7.create_image(145.0, 37.0, image=images["minibea_logo_7"])

images["tile1_tab7"] = PhotoImage(file=relative_to_assets("Tile.png", "tab7")) 
canvas7.create_image(245, 245, image=images["tile1_tab7"])


offset_top = 150  # offset from top of the frame/window

SgValue = tk.IntVar(value=2)
continuous_read = tk.BooleanVar(value=False)

# Entries
canvas7.create_text(34.0, 75.0, anchor="nw", text="Sg Test", fill="#FFFFFF", font=("Inter SemiBold", 20 * -1))

canvas7.create_text(34.0, 156 + 0*40, anchor="nw",text="DoPwrSg", fill="#FFFFFF", font=("Inter SemiBold", 12 * -1))
tab7_entry_1 = ttk.Entry(tab7_frame, style='Background_grey.TEntry')
tab7_entry_1.place(x=225.0, y=offset_top + 0*40, width=115, height=32)

canvas7.create_text(34.0, 156 + 1*40, anchor="nw",text="Sg1PlusOpamp", fill="#FFFFFF", font=("Inter SemiBold", 12 * -1))
tab7_entry2 = ttk.Entry(tab7_frame, style='Background_grey.TEntry')
tab7_entry2.place(x=225.0, y=offset_top + 1*40, width=115, height=32)

canvas7.create_text(34.0, 156 + 2*40, anchor="nw",text="Sg1MinusOpamp", fill="#FFFFFF", font=("Inter SemiBold", 12 * -1))
tab7_entry3 = ttk.Entry(tab7_frame, style='Background_grey.TEntry')
tab7_entry3.place(x=225.0, y=offset_top + 2*40, width=115, height=32)

canvas7.create_text(34.0, 156 + 3*40, anchor="nw",text="Sg1Opamp", fill="#FFFFFF", font=("Inter SemiBold", 12 * -1))
tab7_entry4 = ttk.Entry(tab7_frame, style='Background_grey.TEntry')
tab7_entry4.place(x=225.0, y=offset_top + 3*40, width=115, height=32)

canvas7.create_text(435.0, 156 + 1*40, anchor="nw",text="Sg2PlusOpamp", fill="#FFFFFF", font=("Inter SemiBold", 12 * -1))
tab7_entry6 = ttk.Entry(tab7_frame, style='Background_grey.TEntry')
tab7_entry6.place(x=570.0, y=offset_top + 1*40, width=115.0, height=32.0)

canvas7.create_text(435.0, 156 + 2*40, anchor="nw",text="Sg2MinusOpamp", fill="#FFFFFF", font=("Inter SemiBold", 12 * -1))
tab7_entry7 = ttk.Entry(tab7_frame, style='Background_grey.TEntry')
tab7_entry7.place(x=570.0, y=offset_top + 2*40, width=115, height=32)

canvas7.create_text(435.0, 156 + 3*40, anchor="nw",text="Sg2Opamp", fill="#FFFFFF", font=("Inter SemiBold", 12 * -1))
tab7_entry8 = ttk.Entry(tab7_frame, style='Background_grey.TEntry')
tab7_entry8.place(x=570.0, y=offset_top + 3*40, width=115, height=32)

def auto_refresh_sg_values():
    """Automatically refresh SG values every 2 seconds"""
    try:
        # Only refresh if Trace32 is connected and we're on the SG tab
        current_tab = notebook.tab(notebook.select(), "text")
        if current_tab == "Strain Gauge" and dbg and not isinstance(dbg, str):
            # Read all SG values
            read_sg_values_with_delay(sg_output_variables, sg_entries)
    except:
        pass
    finally:
        # Schedule next refresh
        window.after(2000, auto_refresh_sg_values)

# Start auto-refresh
window.after(2000, auto_refresh_sg_values)

# Add this checkbox near your other SG controls
continuous_read_cb = tk.Checkbutton(
    tab7, 
    text="Continuous Read", 
    variable=continuous_read,
    command=lambda: toggle_continuous_read(continuous_read.get())
)
continuous_read_cb.place(x=365, y=75, width=115, height=32)

# Add this function
def toggle_continuous_read(enabled):
    if enabled:
        start_continuous_read()
    else:
        stop_continuous_read()

def start_continuous_read():
    """Start continuous reading of SG values"""
    def read_loop():
        if continuous_read.get():
            # Read values
            read_sg_values_with_delay(sg_output_variables, sg_entries)
            # Schedule next read
            window.after(1000, read_loop)
    
    read_loop()

def stop_continuous_read():
    """Stop continuous reading"""
    pass  # Just stop the loop by not rescheduling


# Execution
sg_output_variables = ["TestFw_DoPwrSg", "TestFw_Sg1PlusOpamp", "TestFw_Sg1MinusOpamp", "TestFw_Sg1Opamp", "TestFw_Sg2PlusOpamp", "TestFw_Sg2MinusOpamp", "TestFw_Sg2Opamp"]
sg_entries = [tab7_entry_1, tab7_entry2, tab7_entry3, tab7_entry4, tab7_entry6, tab7_entry7, tab7_entry8]

tab7_lbl_pwrsg   = tk.Label(tab7_frame, text="", width=6, font=("Inter SemiBold", 10), relief="flat")
tab7_lbl_pwrsg.place(x=350, y=offset_top+6, height=20)
tab7_lbl_sg1plus = tk.Label(tab7_frame, text="", width=6, font=("Inter SemiBold", 10), relief="flat")
tab7_lbl_sg1plus.place(x=350, y=offset_top+46, height=20)
tab7_lbl_sg1min  = tk.Label(tab7_frame, text="", width=6, font=("Inter SemiBold", 10), relief="flat")
tab7_lbl_sg1min.place(x=350, y=offset_top+86, height=20)
tab7_lbl_sg1     = tk.Label(tab7_frame, text="", width=6, font=("Inter SemiBold", 10), relief="flat")
tab7_lbl_sg1.place(x=350, y=offset_top+126, height=20)
tab7_lbl_sg2plus = tk.Label(tab7_frame, text="", width=6, font=("Inter SemiBold", 10), relief="flat")
tab7_lbl_sg2plus.place(x=695, y=offset_top+46, height=20)
tab7_lbl_sg2min  = tk.Label(tab7_frame, text="", width=6, font=("Inter SemiBold", 10), relief="flat")
tab7_lbl_sg2min.place(x=695, y=offset_top+86, height=20)
tab7_lbl_sg2     = tk.Label(tab7_frame, text="", width=6, font=("Inter SemiBold", 10), relief="flat")
tab7_lbl_sg2.place(x=695, y=offset_top+126, height=20)
tab7_lbl_overall = tk.Label(tab7_frame, text="", width=14, font=("Inter SemiBold", 12), relief="ridge")
tab7_lbl_overall.place(x=490, y=110, height=26)

sg_pf_labels = [tab7_lbl_pwrsg, tab7_lbl_sg1plus, tab7_lbl_sg1min, tab7_lbl_sg1, tab7_lbl_sg2plus, tab7_lbl_sg2min, tab7_lbl_sg2]

def _evaluate_sg_results():
    results = []
    for entry, lbl in zip(sg_entries, sg_pf_labels):
        v = _parse_num(entry)
        passed = v is not None and v != 0
        _set_pf(lbl, passed)
        results.append(passed)
    _set_overall(tab7_lbl_overall, results)

sg_results_cb = tk.Checkbutton(
    tab7, 
    text="Sg Results", 
    variable=SgValue, 
    onvalue=1, 
    offvalue=0, 
    command=lambda: [
    sg_results(SgValue),
    SendDIDGetVal_multiple_entry(sg_output_variables, sg_entries, TestFunctionCmd.TEST_GUI_CMD_SG_TEST_e),
        # Schedule the reset after 1000ms (1 second)
    #window.after(1000, lambda: auto_reset_sg_checkbox(SgValue))
    tab7_frame.after(200, _evaluate_sg_results)
    ]
)
sg_results_cb.place(x=225, y=75, width=115, height=32)

sg_reset_entries = ttk.Button(tab7, text="Reset Results", command=lambda: [clear_entries(sg_entries), _reset_pf_labels(tab7_lbl_overall, *sg_pf_labels)]) #browse button to get repo path
sg_reset_entries.place(x=510, y=75, width=115, height=32)

running_status = tk.Label(tab7_frame, text="Running Status: None")
running_status.config(bg = "#DFDFDF")
running_status.place(x = 20, y = 550)

canvas7.create_text(
    260.0,
    20.0,
    anchor="nw",
    text="U-Shin India",
    fill="#FFFFFF",
    font=("Inter BoldItalic", 24 * -1)
)

# ===================================================================================================================
# ========== TAB 8 (Capa Test) ======================================================================================

tab8 = ttk.Frame(notebook)
notebook.add(tab8, text="Capa Sensor")

tab8_frame = tk.Frame(tab8, bg="#DFDFDF")
tab8_frame.pack(fill="both", expand=True)

canvas8 = tk.Canvas(
    tab8_frame,
    bg="#DFDFDF",
    height=651,
    width=973,
    bd=0,
    highlightthickness=0,
    relief="ridge"
)
canvas8.place(x=0, y=0)

# ===================================================================================================================
# ========== Tile-1 =================================================================================================
images["minibea_logo_8"] = PhotoImage(file=relative_to_assets("minebea_logo_8.png", "tab8"))
canvas8.create_image(145.0, 37.0, image=images["minibea_logo_8"])

images["tile1_tab8"] = PhotoImage(file=relative_to_assets("Tile.png", "tab8")) 
canvas8.create_image(245, 230, image=images["tile1_tab8"])

# Variables
CapaValue = tk.IntVar(value=2)
continuous_read_capa = tk.BooleanVar(value=False)

# Entries
canvas8.create_text(73.0, 113.0, anchor="nw", text="Capa Test", fill="#FFFFFF", font=("Inter SemiBold", 20 * -1))

canvas8.create_text(73.0, 168.0, anchor="nw", text="CapaApproach", fill="#FFFFFF", font=("Inter SemiBold", 15 * -1))
tab8_entry_1 = ttk.Entry(tab8_frame, style='Background_grey.TEntry')
tab8_entry_1.place(x=350.0, y=168.0, width=115, height=32)

canvas8.create_text(73.0, 214.0, anchor="nw", text="CapaLock", fill="#FFFFFF", font=("Inter SemiBold", 15 * -1))
tab8_entry_2 = ttk.Entry(tab8_frame, style='Background_grey.TEntry')
tab8_entry_2.place(x=350.0, y=214.0, width=115, height=32)

canvas8.create_text(73.0, 260.0, anchor="nw", text="CapaUnlock", fill="#FFFFFF", font=("Inter SemiBold", 15 * -1))
tab8_entry3 = ttk.Entry(tab8_frame, style='Background_grey.TEntry')
tab8_entry3.place(x=350.0, y=260.0, width=115, height=32)

canvas8.create_text(73.0, 306.0, anchor="nw", text="CapaApproachRawValue", fill="#FFFFFF", font=("Inter SemiBold", 15 * -1))
tab8_entry4 = ttk.Entry(tab8_frame, style='Background_grey.TEntry')
tab8_entry4.place(x=350.0, y=306.0, width=115, height=32)

canvas8.create_text(73.0, 352.0, anchor="nw", text="CapaLockRawValue", fill="#FFFFFF", font=("Inter SemiBold", 15 * -1))
tab8_entry5 = ttk.Entry(tab8_frame, style='Background_grey.TEntry')
tab8_entry5.place(x=350.0, y=352.0, width=115, height=32)

canvas8.create_text(73.0, 398.0, anchor="nw", text="CapaUnlockRawValue", fill="#FFFFFF", font=("Inter SemiBold", 15 * -1))
tab8_entry6 = ttk.Entry(tab8_frame, style='Background_grey.TEntry')
tab8_entry6.place(x=350.0, y=398.0, width=115, height=32)

# Output variables and entries
capa_output_variables = [
    "TestFw_CapaApproach", 
    "TestFw_CapaLock", 
    "TestFw_CapaUnlock", 
    "TestFw_CapaApproachSensorValue", 
    "TestFw_CapaLockSensorValue", 
    "TestFw_CapaUnlockSensorValue"
]
capa_entries = [tab8_entry_1, tab8_entry_2, tab8_entry3, tab8_entry4, tab8_entry5, tab8_entry6]

# Auto-refresh function
def auto_refresh_capa_values():
    """Automatically refresh CAPA values every 2 seconds"""
    try:
        # Only refresh if Trace32 is connected and we're on the CAPA tab
        current_tab = notebook.tab(notebook.select(), "text")
        if current_tab == "Capa Sensor" and dbg and not isinstance(dbg, str):
            # Read all CAPA values
            read_capa_values_with_delay(capa_output_variables, capa_entries)
    except:
        pass
    finally:
        # Schedule next refresh
        window.after(2000, auto_refresh_capa_values)

# Start auto-refresh
window.after(2000, auto_refresh_capa_values)

# Continuous Read checkbox
continuous_read_capa_cb = tk.Checkbutton(
    tab8, 
    text="Continuous Read", 
    variable=continuous_read_capa,
    command=lambda: toggle_continuous_read_capa(continuous_read_capa.get())
)
continuous_read_capa_cb.place(x=350, y=110, width=115, height=32)

def toggle_continuous_read_capa(enabled):
    if enabled:
        start_continuous_read_capa()
    else:
        pass  # Stop by not rescheduling

def start_continuous_read_capa():
    """Start continuous reading of CAPA values"""
    def read_loop():
        if continuous_read_capa.get():
            # Read values
            read_capa_values_with_delay(capa_output_variables, capa_entries)
            # Schedule next read
            window.after(1000, read_loop)
    
    read_loop()

tab8_lbl_approach   = tk.Label(tab8_frame, text="", width=6, font=("Inter SemiBold", 10), relief="flat")
tab8_lbl_approach.place(x=475, y=174, height=20)
tab8_lbl_lock       = tk.Label(tab8_frame, text="", width=6, font=("Inter SemiBold", 10), relief="flat")
tab8_lbl_lock.place(x=475, y=220, height=20)
tab8_lbl_unlock     = tk.Label(tab8_frame, text="", width=6, font=("Inter SemiBold", 10), relief="flat")
tab8_lbl_unlock.place(x=475, y=266, height=20)
tab8_lbl_app_raw    = tk.Label(tab8_frame, text="", width=6, font=("Inter SemiBold", 10), relief="flat")
tab8_lbl_app_raw.place(x=475, y=312, height=20)
tab8_lbl_lock_raw   = tk.Label(tab8_frame, text="", width=6, font=("Inter SemiBold", 10), relief="flat")
tab8_lbl_lock_raw.place(x=475, y=358, height=20)
tab8_lbl_unlock_raw = tk.Label(tab8_frame, text="", width=6, font=("Inter SemiBold", 10), relief="flat")
tab8_lbl_unlock_raw.place(x=475, y=404, height=20)
tab8_lbl_overall    = tk.Label(tab8_frame, text="", width=14, font=("Inter SemiBold", 12), relief="ridge")
tab8_lbl_overall.place(x=480, y=65, height=26)

capa_pf_labels = [tab8_lbl_approach, tab8_lbl_lock, tab8_lbl_unlock, tab8_lbl_app_raw, tab8_lbl_lock_raw, tab8_lbl_unlock_raw]

def _evaluate_capa_results():
    # capa_entries order: [approach_bool, lock_bool, unlock_bool, approach_raw, lock_raw, unlock_raw]
    thresholds = [
        lambda v: v == 1,       # CapaApproach bool
        lambda v: v == 1,       # CapaLock bool
        lambda v: v == 1,       # CapaUnlock bool
        lambda v: v > 8900,     # CapaApproachRawValue
        lambda v: v > 8900,     # CapaLockRawValue
        lambda v: v > 8900,     # CapaUnlockRawValue
    ]
    results = []
    for entry, lbl, check in zip(capa_entries, capa_pf_labels, thresholds):
        v = _parse_num(entry)
        passed = v is not None and check(v)
        _set_pf(lbl, passed)
        results.append(passed)
    _set_overall(tab8_lbl_overall, results)

# Run button
images["tile1_run_capa"] = PhotoImage(file=relative_to_assets("tab_testrun_button.png", "tab8"))
run_test_btn = Button(
    tab8, 
    image=images["tile1_run_capa"], 
    command=lambda: [read_capa_values_with_delay(capa_output_variables, capa_entries), tab8_frame.after(200, _evaluate_capa_results)],
    bd=0
)
run_test_btn.place(x=225, y=106, width=34, height=34)

# Reset button
reset_entries = ttk.Button(tab8, text="Reset Results", command=lambda: [clear_entries(capa_entries), _reset_pf_labels(tab8_lbl_overall, *capa_pf_labels)])
reset_entries.place(x=350, y=65, width=115, height=32)

canvas8.create_text(
    260.0,
    20.0,
    anchor="nw",
    text="U-Shin India",
    fill="#FFFFFF",
    font=("Inter BoldItalic", 24 * -1)
)

# ===================================================================================================================
# ===================================================================================================================
# ========== TAB 9 (NFC Test) =======================================================================================

tab9 = ttk.Frame(notebook)
notebook.add(tab9, text="NFC")

tab9_frame = tk.Frame(tab9, bg="#DFDFDF")
tab9_frame.pack(fill="both", expand=True)

canvas9 = tk.Canvas(
    tab9_frame,
    bg="#DFDFDF",
    height=651,
    width=973,
    bd=0,
    highlightthickness=0,
    relief="ridge"
)
canvas9.place(x=0, y=0)

# ===================================================================================================================
# ========== Tile-1 =================================================================================================
images["minibea_logo_9"] = PhotoImage(file=relative_to_assets("minebea_logo_9.png", "tab9"))
canvas9.create_image(145.0, 37.0, image=images["minibea_logo_9"])


images["tile_tab9"] = PhotoImage(file=relative_to_assets("Tile.png", "tab9")) 
canvas9.create_image(tablet1_X, tablet1_Y +10, image=images["tile_tab9"])

canvas9.create_text(73.0, 113.0, anchor="nw", text="NFC Test", fill="#FFFFFF", font=("Inter SemiBold", 20 * -1))

# --- Section A: Transceiver SPI Diagnostics (no antenna or card required) ---
canvas9.create_text(73.0, 148.0, anchor="nw", text="Transceiver SPI Diagnostics", fill="#F39C12", font=("Inter SemiBold", 13 * -1))
canvas9.create_text(73.0, 174.0, anchor="nw", text="SpiError", fill="#FFFFFF", font=("Inter SemiBold", 12 * -1))
tab9_spi_err = ttk.Entry(tab9_frame, style='Background_grey.TEntry')
tab9_spi_err.place(x=200.0, y=172.0, width=95.0, height=20.0)

canvas9.create_text(73.0, 204.0, anchor="nw", text="HwVersion", fill="#FFFFFF", font=("Inter SemiBold", 12 * -1))
tab9_hw_ver = ttk.Entry(tab9_frame, style='Background_grey.TEntry')
tab9_hw_ver.place(x=200.0, y=202.0, width=95.0, height=20.0)

canvas9.create_text(73.0, 234.0, anchor="nw", text="RomVersion", fill="#FFFFFF", font=("Inter SemiBold", 12 * -1))
tab9_rom_ver = ttk.Entry(tab9_frame, style='Background_grey.TEntry')
tab9_rom_ver.place(x=200.0, y=232.0, width=95.0, height=20.0)

canvas9.create_text(73.0, 264.0, anchor="nw", text="FwVersion", fill="#FFFFFF", font=("Inter SemiBold", 12 * -1))
tab9_fw_ver = ttk.Entry(tab9_frame, style='Background_grey.TEntry')
tab9_fw_ver.place(x=200.0, y=262.0, width=95.0, height=20.0)

canvas9.create_text(73.0, 294.0, anchor="nw", text="SPI Comm w/ Transceiver", fill="#FFFFFF", font=("Inter SemiBold", 12 * -1))
tab9_lbl_spi_comm = tk.Label(tab9_frame, text="", width=10, font=("Inter SemiBold", 10), relief="flat", bg="#DFDFDF")
tab9_lbl_spi_comm.place(x=305, y=292, height=20)

# --- Section B: Card Detection (requires NFC antenna + card) ---
canvas9.create_text(73.0, 330.0, anchor="nw", text="Card Detection (requires antenna + card)", fill="#F39C12", font=("Inter SemiBold", 13 * -1))
canvas9.create_text(73.0, 356.0, anchor="nw", text="IsNfcDetectedCard", fill="#FFFFFF", font=("Inter SemiBold", 12 * -1))
tab9_entry_1 = ttk.Entry(tab9_frame, style='Background_grey.TEntry')
tab9_entry_1.place(x=250.0, y=354.0, width=95.0, height=20.0)

nfc_output_variables = [
    "TestFw_IsNfcDetectedCard",
    "TestFw_NfcSpiError",
    "TestFw_NfcHwVersion",
    "TestFw_NfcRomVersion",
    "TestFw_NfcFwVersion",
]
nfc_entries = [tab9_entry_1, tab9_spi_err, tab9_hw_ver, tab9_rom_ver, tab9_fw_ver]

# SPI-only diagnostic variables (no antenna or card required)
nfc_spi_diag_variables = [
    "TestFw_NfcSpiError",
    "TestFw_NfcHwVersion",
    "TestFw_NfcRomVersion",
    "TestFw_NfcFwVersion",
]
nfc_spi_diag_entries = [tab9_spi_err, tab9_hw_ver, tab9_rom_ver, tab9_fw_ver]

# PASS/FAIL indicator labels for each diagnostic field
tab9_lbl_spi_err  = tk.Label(tab9_frame, text="", width=6, font=("Inter SemiBold", 10), relief="flat")
tab9_lbl_spi_err.place(x=305, y=172, height=20)
tab9_lbl_hw_ver   = tk.Label(tab9_frame, text="", width=6, font=("Inter SemiBold", 10), relief="flat")
tab9_lbl_hw_ver.place(x=305, y=202, height=20)
tab9_lbl_rom_ver  = tk.Label(tab9_frame, text="", width=6, font=("Inter SemiBold", 10), relief="flat")
tab9_lbl_rom_ver.place(x=305, y=232, height=20)
tab9_lbl_fw_ver   = tk.Label(tab9_frame, text="", width=6, font=("Inter SemiBold", 10), relief="flat")
tab9_lbl_fw_ver.place(x=305, y=262, height=20)
tab9_lbl_overall  = tk.Label(tab9_frame, text="", width=14, font=("Inter SemiBold", 12), relief="ridge")
tab9_lbl_overall.place(x=480, y=172, height=26)

nfc_diag_labels = [tab9_lbl_spi_err, tab9_lbl_hw_ver, tab9_lbl_rom_ver, tab9_lbl_fw_ver, tab9_lbl_spi_comm]

def _set_result_label(lbl, passed):
    if passed:
        lbl.config(text="PASS", bg="#27AE60", fg="#FFFFFF")
    else:
        lbl.config(text="FAIL", bg="#C0392B", fg="#FFFFFF")

def run_nfc_test():
    SendCmdToDbg("Var.set TestFw_KeepEcuAwake = 1")
    SendDIDGetVal_multiple_entry(nfc_output_variables, nfc_entries, TestFunctionCmd.TEST_GUI_CMD_NFC_TEST_e)
    # Allow GUI to update entry values before reading them
    tab9_frame.after(200, _evaluate_nfc_results)

def _evaluate_nfc_results():
    results = []

    # SpiError: PASS if value starts with "0" (formatted as "0 bool")
    spi_val = tab9_spi_err.get().strip()
    spi_pass = spi_val.startswith("0")
    tab9_spi_err.delete(0, tk.END)
    tab9_spi_err.insert(0, "OK" if spi_pass else "Error")
    _set_result_label(tab9_lbl_spi_err, spi_pass)
    results.append(spi_pass)

    # HwVersion: PASS if non-zero hex (e.g. "0x3e")
    hw_val = tab9_hw_ver.get().strip()
    try:
        hw_pass = int(hw_val, 0) != 0
    except (ValueError, TypeError):
        hw_pass = False
    _set_result_label(tab9_lbl_hw_ver, hw_pass)
    results.append(hw_pass)

    # RomVersion: PASS if non-zero hex
    rom_val = tab9_rom_ver.get().strip()
    try:
        rom_pass = int(rom_val, 0) != 0
    except (ValueError, TypeError):
        rom_pass = False
    _set_result_label(tab9_lbl_rom_ver, rom_pass)
    results.append(rom_pass)

    # FwVersion: PASS if non-zero hex
    fw_val = tab9_fw_ver.get().strip()
    try:
        fw_pass = int(fw_val, 0) != 0
    except (ValueError, TypeError):
        fw_pass = False
    _set_result_label(tab9_lbl_fw_ver, fw_pass)
    results.append(fw_pass)

    # SPI Comm w/ Transceiver: ACTIVE when HwVersion and RomVersion are both non-zero
    spi_comm_ok = hw_pass and rom_pass
    if spi_comm_ok:
        tab9_lbl_spi_comm.config(text="ACTIVE", bg="#27AE60", fg="#FFFFFF")
    else:
        tab9_lbl_spi_comm.config(text="NO LINK", bg="#C0392B", fg="#FFFFFF")

    # IsNfcDetectedCard: reformat "0 bool" -> "No", "1 bool" -> "Yes"
    card_val = tab9_entry_1.get().strip()
    tab9_entry_1.delete(0, tk.END)
    tab9_entry_1.insert(0, "Yes" if card_val.startswith("1") else "No")

    # Overall result
    if all(results):
        tab9_lbl_overall.config(text="OVERALL: PASS", bg="#27AE60", fg="#FFFFFF")
    else:
        tab9_lbl_overall.config(text="OVERALL: FAIL", bg="#C0392B", fg="#FFFFFF")

def _reset_nfc_results():
    clear_entries(nfc_entries)
    for lbl in nfc_diag_labels:
        lbl.config(text="", bg="#DFDFDF", fg="#000000")
    tab9_lbl_overall.config(text="", bg="#DFDFDF", fg="#000000")

images["tab9_nfc_run"] = PhotoImage(file=relative_to_assets("tab_testrun_button.png", "tab9"))
run_test_btn = Button(tab9, image=images["tab9_nfc_run"], command=run_nfc_test, bd = 0)
run_test_btn.place(x=325, y=106, width=34, height=34)

reset_entries = ttk.Button(tab9, text="Reset Results", command=_reset_nfc_results)
reset_entries.place(x=500, y=110, width=85, height=32)

canvas9.create_text(
    260.0,
    20.0,
    anchor="nw",
    text="U-Shin India",
    fill="#FFFFFF",
    font=("Inter BoldItalic", 24 * -1)
)
# ===================================================================================================================
# ===================================================================================================================
# ========== TAB NFC SELF (NFC SPI Self-Test + LED Output Check) =====================================================

tab_nfc_self = ttk.Frame(notebook)
notebook.add(tab_nfc_self, text="NFC SELF")

tab_nfc_self_frame = tk.Frame(tab_nfc_self, bg="#DFDFDF")
tab_nfc_self_frame.pack(fill="both", expand=True)

canvas_nfc_self = tk.Canvas(
    tab_nfc_self_frame,
    bg="#DFDFDF",
    height=651,
    width=973,
    bd=0,
    highlightthickness=0,
    relief="ridge"
)
canvas_nfc_self.place(x=0, y=0)

images["nfc_self_logo"] = PhotoImage(file=relative_to_assets("minebea_logo_9.png", "tab_nfc_self"))
canvas_nfc_self.create_image(145.0, 37.0, image=images["nfc_self_logo"])

images["nfc_self_tile"] = PhotoImage(file=relative_to_assets("Tile.png", "tab_nfc_self"))
canvas_nfc_self.create_image(tablet1_X, tablet1_Y + 10, image=images["nfc_self_tile"])

canvas_nfc_self.create_text(
    260.0, 20.0, anchor="nw",
    text="U-Shin India", fill="#FFFFFF",
    font=("Inter BoldItalic", 24 * -1)
)
canvas_nfc_self.create_text(73.0, 113.0, anchor="nw", text="NFC Self-Test", fill="#FFFFFF", font=("Inter SemiBold", 20 * -1))

# --- Section A: NFC SPI Self-Test (no antenna or card required) ---
# PASS = SpiError is 0 AND TargetID (HwVersion) is non-zero (device responded)
canvas_nfc_self.create_text(73.0, 148.0, anchor="nw", text="NFC SPI Self-Test  (no antenna / card required)", fill="#F39C12", font=("Inter SemiBold", 13 * -1))

canvas_nfc_self.create_text(73.0, 174.0, anchor="nw", text="SpiError", fill="#FFFFFF", font=("Inter SemiBold", 12 * -1))
tab9_st_spi_err = ttk.Entry(tab_nfc_self_frame, style='Background_grey.TEntry')
tab9_st_spi_err.place(x=200.0, y=172.0, width=95.0, height=20.0)
tab9_lbl_st_spi_err = tk.Label(tab_nfc_self_frame, text="", width=6, font=("Inter SemiBold", 10), relief="flat", bg="#DFDFDF")
tab9_lbl_st_spi_err.place(x=305, y=172, height=20)

canvas_nfc_self.create_text(73.0, 204.0, anchor="nw", text="Target ID", fill="#FFFFFF", font=("Inter SemiBold", 12 * -1))
tab9_st_hw_ver = ttk.Entry(tab_nfc_self_frame, style='Background_grey.TEntry')
tab9_st_hw_ver.place(x=200.0, y=202.0, width=95.0, height=20.0)
tab9_lbl_st_hw_ver = tk.Label(tab_nfc_self_frame, text="", width=6, font=("Inter SemiBold", 10), relief="flat", bg="#DFDFDF")
tab9_lbl_st_hw_ver.place(x=305, y=202, height=20)

tab9_lbl_st_overall = tk.Label(tab_nfc_self_frame, text="", width=16, font=("Inter SemiBold", 12), relief="ridge", bg="#DFDFDF")
tab9_lbl_st_overall.place(x=480, y=172, height=26)

# --- Section B: Output Check — LED ON ---
canvas_nfc_self.create_text(73.0, 248.0, anchor="nw", text="Output Check — LED ON (mV)", fill="#F39C12", font=("Inter SemiBold", 13 * -1))
canvas_nfc_self.create_text(73.0, 274.0, anchor="nw", text="LedVoltage", fill="#FFFFFF", font=("Inter SemiBold", 12 * -1))
tab9_st_led_v = ttk.Entry(tab_nfc_self_frame, style='Background_grey.TEntry')
tab9_st_led_v.place(x=200.0, y=272.0, width=95.0, height=20.0)
tab9_lbl_st_led = tk.Label(tab_nfc_self_frame, text="", width=6, font=("Inter SemiBold", 10), relief="flat", bg="#DFDFDF")
tab9_lbl_st_led.place(x=305, y=272, height=20)

# Only SpiError + Target ID (HwVersion) are read — sufficient to prove SPI link
nfc_spi_st_variables = [
    "TestFw_NfcSpiError",
    "TestFw_NfcHwVersion",
]
nfc_spi_st_entries = [tab9_st_spi_err, tab9_st_hw_ver]

def run_nfc_spi_self_test():
    SendCmdToDbg("Var.set TestFw_KeepEcuAwake = 1")
    SendDIDGetVal_multiple_entry(nfc_spi_st_variables, nfc_spi_st_entries, TestFunctionCmd.TEST_GUI_CMD_NFC_SPI_DIAG_e)
    tab_nfc_self_frame.after(200, _evaluate_nfc_spi_self_test_results)

def _evaluate_nfc_spi_self_test_results():
    # SpiError: PASS if value starts with "0"
    spi_val = tab9_st_spi_err.get().strip()
    spi_pass = spi_val.startswith("0")
    tab9_st_spi_err.delete(0, tk.END)
    tab9_st_spi_err.insert(0, "OK" if spi_pass else "Error")
    _set_result_label(tab9_lbl_st_spi_err, spi_pass)

    # Target ID (HwVersion): PASS if non-zero — device responded over SPI
    hw_val = tab9_st_hw_ver.get().strip()
    try:
        hw_pass = int(hw_val, 0) != 0
    except (ValueError, TypeError):
        hw_pass = False
    _set_result_label(tab9_lbl_st_hw_ver, hw_pass)

    spi_all_pass = spi_pass and hw_pass

    if spi_all_pass:
        _run_nfc_led_output_check()
    else:
        tab9_st_led_v.delete(0, tk.END)
        tab9_st_led_v.insert(0, "N/A")
        tab9_lbl_st_led.config(text="SKIP", bg="#F39C12", fg="#FFFFFF")
        tab9_lbl_st_overall.config(text="OVERALL: FAIL", bg="#C0392B", fg="#FFFFFF")

def _run_nfc_led_output_check():
    SendCmdToDbg("Var.set LedTest_LedCanLinRequest = 1")
    tab_nfc_self_frame.after(1500, _read_led_for_nfc_output_check)

def _read_led_for_nfc_output_check():
    SendDIDGetVal_multiple_entry(["TestFw_LedVoltage"], [tab9_st_led_v], TestFunctionCmd.TESTFW_GUI_CMD_LED_TEST_e)
    tab_nfc_self_frame.after(300, _evaluate_nfc_led_output_check)

def _evaluate_nfc_led_output_check():
    led_val = tab9_st_led_v.get().strip()
    try:
        voltage = float(led_val.split()[0])
        led_pass = voltage > 0
    except (ValueError, TypeError, IndexError):
        led_pass = False
    _set_result_label(tab9_lbl_st_led, led_pass)
    SendCmdToDbg("Var.set LedTest_LedCanLinRequest = 0")
    if led_pass:
        tab9_lbl_st_overall.config(text="OVERALL: PASS", bg="#27AE60", fg="#FFFFFF")
    else:
        tab9_lbl_st_overall.config(text="OVERALL: FAIL", bg="#C0392B", fg="#FFFFFF")

def _reset_nfc_spi_self_test_results():
    for e in nfc_spi_st_entries:
        e.delete(0, tk.END)
    tab9_st_led_v.delete(0, tk.END)
    for lbl in [tab9_lbl_st_spi_err, tab9_lbl_st_hw_ver, tab9_lbl_st_led]:
        lbl.config(text="", bg="#DFDFDF", fg="#000000")
    tab9_lbl_st_overall.config(text="", bg="#DFDFDF", fg="#000000")

images["nfc_self_run_btn"] = PhotoImage(file=relative_to_assets("tab_testrun_button.png", "tab_nfc_self"))
spi_self_test_btn = Button(tab_nfc_self, image=images["nfc_self_run_btn"], command=run_nfc_spi_self_test, bd=0)
spi_self_test_btn.place(x=325, y=106, width=34, height=34)

reset_spi_st_btn = ttk.Button(tab_nfc_self, text="Reset Results", command=_reset_nfc_spi_self_test_results)
reset_spi_st_btn.place(x=500, y=110, width=85, height=32)

# ===================================================================================================================
# ===================================================================================================================
# ========== TAB 10 (CAN) =======================================================================================

tab10 = ttk.Frame(notebook)
notebook.add(tab10, text="CAN")

tab10_frame = tk.Frame(tab10, bg="#DFDFDF")
tab10_frame.pack(fill="both", expand=True)

canvas10 = tk.Canvas(
    tab10_frame,
    bg="#DFDFDF",
    height=651,
    width=973,
    bd=0,
    highlightthickness=0,
    relief="ridge"
)
canvas10.place(x=0, y=0)

# ===================================================================================================================
# ========== Tile-1 =================================================================================================
images["minibea_logo_10"] = PhotoImage(file=relative_to_assets("minebea_logo_10.png", "tab10"))
canvas10.create_image(145.0, 37.0, image=images["minibea_logo_10"])

images["tile1_tab10"] = PhotoImage(file=relative_to_assets("Tile.png", "tab10")) 
canvas10.create_image(tablet1_X, tablet1_Y +10, image=images["tile1_tab10"])

canvas10.create_text(61.0, 110.0, anchor="nw", text="CAN Test", fill="#FFFFFF", font=("Inter SemiBold", 20 * -1))
canvas10.create_text(61.0, 138.0, anchor="nw", text="Tx Bytes (0-255 / 0x00-0xFF)", fill="#FFFFFF", font=("Inter SemiBold", 15 * -1))

can_tx_entries = []
can_tx_start_y = 172.0
can_tx_row_gap = 58.0
can_tx_defaults = [11, 22, 33, 44, 55, 66, 77, 88]
for idx in range(8):
    x_pos = 61.0 + (idx % 4) * 85.0
    y_pos = can_tx_start_y + (idx // 4) * can_tx_row_gap
    canvas10.create_text(x_pos, y_pos - 14.0, anchor="nw", text=f"B{idx}", fill="#FFFFFF", font=("Inter SemiBold", 11 * -1))
    entry = ttk.Entry(tab10_frame, style='Background_grey.TEntry')
    entry.place(x=x_pos, y=y_pos, width=70.0, height=24.0)
    entry.insert(0, str(can_tx_defaults[idx]))
    can_tx_entries.append(entry)

canvas10.create_text(420.0, 146.0, anchor="nw", text="Local Loopback", fill="#FFFFFF", font=("Inter SemiBold", 12 * -1))
can_loopback_var = tk.BooleanVar(value=True)
can_loopback_chk = ttk.Checkbutton(tab10_frame, variable=can_loopback_var)
can_loopback_chk.place(x=560.0, y=144.0, width=24.0, height=24.0)

canvas10.create_text(420.0, 178.0, anchor="nw", text="Keep ECU Awake", fill="#FFFFFF", font=("Inter SemiBold", 12 * -1))
can_keep_awake_var = tk.BooleanVar(value=False)
can_keep_awake_chk = ttk.Checkbutton(tab10_frame, variable=can_keep_awake_var)
can_keep_awake_chk.place(x=560.0, y=176.0, width=24.0, height=24.0)

canvas10.create_text(420.0, 210.0, anchor="nw", text="TxMessageId", fill="#FFFFFF", font=("Inter SemiBold", 12 * -1))
tab10_tx_msgid = ttk.Entry(tab10_frame, style='Background_grey.TEntry')
tab10_tx_msgid.place(x=560.0, y=208.0, width=110.0, height=24.0)
tab10_tx_msgid.insert(0, "0x796")
tab10_tx_msgid.configure(state="disabled")

canvas10.create_text(61.0, 268.0, anchor="nw", text="Rx Status", fill="#FFFFFF", font=("Inter SemiBold", 15 * -1))
canvas10.create_text(61.0, 300.0, anchor="nw", text="CanRxDataValid (1 Yes / 0 No)", fill="#FFFFFF", font=("Inter SemiBold", 12 * -1))
tab10_rx_valid = ttk.Entry(tab10_frame, style='Background_grey.TEntry')
tab10_rx_valid.place(x=250.0, y=298.0, width=90.0, height=24.0)

canvas10.create_text(420.0, 300.0, anchor="nw", text="RxMessageId", fill="#FFFFFF", font=("Inter SemiBold", 12 * -1))
tab10_rx_msgid = ttk.Entry(tab10_frame, style='Background_grey.TEntry')
tab10_rx_msgid.place(x=520.0, y=298.0, width=110.0, height=24.0)

canvas10.create_text(61.0, 340.0, anchor="nw", text="Rx Bytes", fill="#FFFFFF", font=("Inter SemiBold", 12 * -1))
can_rx_entries = []
can_rx_start_y = 366.0
can_rx_row_gap = 50.0
for idx in range(8):
    x_pos = 61.0 + (idx % 4) * 85.0
    y_pos = can_rx_start_y + (idx // 4) * can_rx_row_gap
    canvas10.create_text(x_pos, y_pos - 12.0, anchor="nw", text=f"B{idx}", fill="#FFFFFF", font=("Inter SemiBold", 10 * -1))
    entry = ttk.Entry(tab10_frame, style='Background_grey.TEntry')
    entry.place(x=x_pos, y=y_pos, width=70.0, height=24.0)
    can_rx_entries.append(entry)

canvas10.create_text(420.0, 340.0, anchor="nw", text="COM Active", fill="#FFFFFF", font=("Inter SemiBold", 12 * -1))
tab10_com_active = ttk.Entry(tab10_frame, style='Background_grey.TEntry')
tab10_com_active.place(x=560.0, y=338.0, width=120.0, height=24.0)

can_output_variables = [
    "TestFw_CanRxDataValid",
    "TestFw_CanRxMessageId",
    "TestFw_CanRxBytes.dummy_byte0_U8",
    "TestFw_CanRxBytes.dummy_byte1_U8",
    "TestFw_CanRxBytes.dummy_byte2_U8",
    "TestFw_CanRxBytes.dummy_byte3_U8",
    "TestFw_CanRxBytes.dummy_byte4_U8",
    "TestFw_CanRxBytes.dummy_byte5_U8",
    "TestFw_CanRxBytes.dummy_byte6_U8",
    "TestFw_CanRxBytes.dummy_byte7_U8",
    "TestFw_CanIsActiveState",
]
can_entries = [tab10_rx_valid, tab10_rx_msgid] + can_rx_entries + [tab10_com_active]

def _parse_u8_from_entry(entry_widget, field_name):
    text = entry_widget.get().strip()
    try:
        value = int(text, 0)
    except ValueError:
        raise ValueError(f"Invalid value for {field_name}: '{text}'")

    if value < 0 or value > 255:
        raise ValueError(f"{field_name} out of range: {value} (expected 0..255)")

    return value

tab10_lbl_rx_valid = tk.Label(tab10_frame, text="", width=5, font=("Inter SemiBold", 10), relief="flat")
tab10_lbl_rx_valid.place(x=345, y=300, height=20)
tab10_lbl_active   = tk.Label(tab10_frame, text="", width=6, font=("Inter SemiBold", 10), relief="flat")
tab10_lbl_active.place(x=690, y=340, height=20)
tab10_lbl_overall  = tk.Label(tab10_frame, text="", width=14, font=("Inter SemiBold", 12), relief="ridge")
tab10_lbl_overall.place(x=600, y=110, height=26)

can_pf_labels = [tab10_lbl_rx_valid, tab10_lbl_active]

def _evaluate_can_results():
    v_rx    = _parse_num(tab10_rx_valid)
    v_act   = _parse_num(tab10_com_active)
    p_rx    = v_rx    is not None and v_rx    == 1
    p_act   = v_act   is not None and v_act   == 1
    _set_pf(tab10_lbl_rx_valid, p_rx)
    if can_loopback_var.get():
        # In loopback mode only RxDataValid matters; suppress bus-level indicators
        _set_pf(tab10_lbl_active, True)
        _set_overall(tab10_lbl_overall, [p_rx])
    else:
        _set_pf(tab10_lbl_active, p_act)
        _set_overall(tab10_lbl_overall, [p_rx, p_act])

def run_can_test():
    try:
        loopback_value = 1 if can_loopback_var.get() else 0
        SendCmdToDbg(f"Var.set TestFw_CanGuiLocalLoopbackEnable = {loopback_value}")

        keep_awake_value = 1 if can_keep_awake_var.get() else 0
        SendCmdToDbg(f"Var.set TestFw_KeepEcuAwake = {keep_awake_value}")

        for idx, entry in enumerate(can_tx_entries):
            value = _parse_u8_from_entry(entry, f"CAN Tx Byte {idx}")
            SendCmdToDbg(f"Var.set DummyBytes.dummy_byte{idx}_U8 = {value}")

        SendDIDGetVal_multiple_entry(can_output_variables, can_entries, TestFunctionCmd.TEST_GUI_CMD_CAN_TEST_e)
        tab10_frame.after(200, _evaluate_can_results)
    except Exception as exc:
        messagebox.showerror("CAN Test", str(exc))

images["tab10_can_run"] = PhotoImage(file=relative_to_assets("tab_testrun_button.png", "tab10"))
run_test_btn = Button(tab10, image=images["tab10_can_run"], command=run_can_test, bd = 0)
run_test_btn.place(x=225, y=106, width=34, height=34)

reset_entries = ttk.Button(tab10, text="Reset Results", command=lambda: [clear_entries(can_entries + can_tx_entries), _reset_pf_labels(tab10_lbl_overall, *can_pf_labels)])
reset_entries.place(x=500, y=110, width=85, height=32)

canvas10.create_text(
    260.0,
    20.0,
    anchor="nw",
    text="U-Shin India",
    fill="#FFFFFF",
    font=("Inter BoldItalic", 24 * -1)
)

# ===================================================================================================================
# ===================================================================================================================
# ========== TAB 11 (LIN) =======================================================================================

tab11 = ttk.Frame(notebook)
notebook.add(tab11, text="LIN")

tab11_frame = tk.Frame(tab11, bg="#DFDFDF")
tab11_frame.pack(fill="both", expand=True)

canvas11 = tk.Canvas(
    tab11_frame,
    bg="#DFDFDF",
    height=651,
    width=973,
    bd=0,
    highlightthickness=0,
    relief="ridge"
)
canvas11.place(x=0, y=0)

# ===================================================================================================================
# ========== Tile-1 =================================================================================================
images["minibea_logo_11"] = PhotoImage(file=relative_to_assets("minebea_logo_11.png", "tab11"))
canvas11.create_image(145.0, 37.0, image=images["minibea_logo_11"])

images["tile1_tab11"] = PhotoImage(file=relative_to_assets("Tile.png", "tab11")) 
canvas11.create_image(tablet1_X, tablet1_Y +10, image=images["tile1_tab11"])

CapaApproachSensorRawCount = tk.IntVar(value=1)

canvas11.create_text(61.0, 110.0, anchor="nw", text="LIN Test (v2)", fill="#FFFFFF", font=("Inter SemiBold", 20 * -1))
canvas11.create_text(61.0, 138.0, anchor="nw", text="Tx Bytes (0-255 / 0x00-0xFF)", fill="#FFFFFF", font=("Inter SemiBold", 15 * -1))
canvas11.create_text(460.0, 138.0, anchor="nw", text="LinTxPid (Hex)", fill="#FFFFFF", font=("Inter SemiBold", 12 * -1))
tab11_tx_msgid = ttk.Entry(tab11_frame, style='Background_grey.TEntry')
tab11_tx_msgid.place(x=600.0, y=136.0, width=110.0, height=24.0)
tab11_tx_msgid.insert(0, "0x3A")

lin_tx_entries = []
lin_tx_start_y = 172.0
lin_tx_row_gap = 58.0
lin_tx_defaults = [44, 55, 66, 77, 11, 22, 33, 44]
for idx in range(8):
    x_pos = 61.0 + (idx % 4) * 85.0
    y_pos = lin_tx_start_y + (idx // 4) * lin_tx_row_gap
    canvas11.create_text(x_pos, y_pos - 14.0, anchor="nw", text=f"B{idx}", fill="#FFFFFF", font=("Inter SemiBold", 11 * -1))
    entry = ttk.Entry(tab11_frame, style='Background_grey.TEntry')
    entry.place(x=x_pos, y=y_pos, width=70.0, height=24.0)
    entry.insert(0, str(lin_tx_defaults[idx]))
    lin_tx_entries.append(entry)

canvas11.create_text(61.0, 268.0, anchor="nw", text="Rx Status", fill="#FFFFFF", font=("Inter SemiBold", 15 * -1))
canvas11.create_text(61.0, 300.0, anchor="nw", text="LinRxDataValid", fill="#FFFFFF", font=("Inter SemiBold", 12 * -1))
tab11_rx_valid = ttk.Entry(tab11_frame, style='Background_grey.TEntry')
tab11_rx_valid.place(x=210.0, y=298.0, width=90.0, height=24.0)

canvas11.create_text(390.0, 300.0, anchor="nw", text="LinRxPid", fill="#FFFFFF", font=("Inter SemiBold", 12 * -1))
tab11_rx_pid = ttk.Entry(tab11_frame, style='Background_grey.TEntry')
tab11_rx_pid.place(x=500.0, y=298.0, width=110.0, height=24.0)


canvas11.create_text(61.0, 340.0, anchor="nw", text="Rx Bytes", fill="#FFFFFF", font=("Inter SemiBold", 12 * -1))
lin_rx_entries = []
lin_rx_start_y = 366.0
lin_rx_row_gap = 50.0
for idx in range(8):
    x_pos = 61.0 + (idx % 4) * 85.0
    y_pos = lin_rx_start_y + (idx // 4) * lin_rx_row_gap
    canvas11.create_text(x_pos, y_pos - 12.0, anchor="nw", text=f"B{idx}", fill="#FFFFFF", font=("Inter SemiBold", 10 * -1))
    entry = ttk.Entry(tab11_frame, style='Background_grey.TEntry')
    entry.place(x=x_pos, y=y_pos, width=70.0, height=24.0)
    lin_rx_entries.append(entry)

lin_output_variables = [
    "TestFw_LinRxDataValid",
    "TestFw_LinRxPid",
    "TestFw_LinRxData_aU8[0]",
    "TestFw_LinRxData_aU8[1]",
    "TestFw_LinRxData_aU8[2]",
    "TestFw_LinRxData_aU8[3]",
    "TestFw_LinRxData_aU8[4]",
    "TestFw_LinRxData_aU8[5]",
    "TestFw_LinRxData_aU8[6]",
    "TestFw_LinRxData_aU8[7]",
]
lin_entry_list = [tab11_rx_valid, tab11_rx_pid] + lin_rx_entries

tab11_lbl_rx_valid = tk.Label(tab11_frame, text="", width=6, font=("Inter SemiBold", 10), relief="flat")
tab11_lbl_rx_valid.place(x=305, y=300, height=20)
tab11_lbl_overall  = tk.Label(tab11_frame, text="", width=14, font=("Inter SemiBold", 12), relief="ridge")
tab11_lbl_overall.place(x=530, y=110, height=26)

lin_pf_labels = [tab11_lbl_rx_valid]

def _evaluate_lin_results():
    v_rx = _parse_num(tab11_rx_valid)
    p_rx = v_rx is not None and v_rx == 1
    # Also require at least one Rx byte to be non-zero (all-zero = no real data received)
    any_byte_nonzero = any(_parse_num(e) not in (None, 0) for e in lin_rx_entries)
    p_rx = p_rx and any_byte_nonzero
    _set_pf(tab11_lbl_rx_valid, p_rx)
    _set_overall(tab11_lbl_overall, [p_rx])

def run_lin_test():
    try:
        msg_id_text = tab11_tx_msgid.get().strip()
        try:
            msg_id_value = int(msg_id_text, 0)
        except ValueError:
            raise ValueError(f"Invalid LinTxPid: '{msg_id_text}'")
        if msg_id_value < 0 or msg_id_value > 0xFF:
            raise ValueError(f"LinTxPid out of range: {msg_id_value} (expected 0x00..0xFF)")
        SendCmdToDbg(f"Var.set TestFw_LinTxPid = {msg_id_value}")

        for idx, entry in enumerate(lin_tx_entries):
            value = _parse_u8_from_entry(entry, f"LIN Tx Byte {idx}")
            SendCmdToDbg(f"Var.set TestFw_LinTxByte{idx} = {value}")

        SendDIDGetVal_multiple_entry(lin_output_variables, lin_entry_list, TestFunctionCmd.TEST_GUI_CMD_LIN_e)
        tab11_frame.after(200, _evaluate_lin_results)
    except Exception as exc:
        messagebox.showerror("LIN Test", str(exc))

images["tab11_lin_run"] = PhotoImage(file=relative_to_assets("tab_testrun_button.png", "tab11"))
tab11_run_btn = Button(
    tab11, 
    image=images["tab11_lin_run"], 
    command=run_lin_test,
    bd = 0
)
tab11_run_btn.place(x=225, y=106.0, width=34, height=34)

canvas11.create_text(266.0, 110.0, anchor="nw", text="Transmit", fill="#FFFFFF", font=("Inter SemiBold", 15 * -1))

reset_entries = ttk.Button(tab11, text="Reset Results", command=lambda: [clear_entries(lin_entry_list + lin_tx_entries), _reset_pf_labels(tab11_lbl_overall, *lin_pf_labels)])
reset_entries.place(x=350, y=110, width=115, height=32)

canvas11.create_text(
    260.0,
    20.0,
    anchor="nw",
    text="U-Shin India",
    fill="#FFFFFF",
    font=("Inter BoldItalic", 24 * -1)
)
# ===================================================================================================================
# ===================================================================================================================
# ========== TAB 12 (AUTO) =======================================================================================

# ─── Combined manual test report (all tabs → one HTML on Disconnect) ──────────
def _collect_and_save_all_manual_tests(deflash_result=None):
    """Collect current entry values from every manual-test tab and save one report."""
    sections = []

    # ── LED ───────────────────────────────────────────────────────────────────
    led_fields = []
    v_on = tab3_entry_led_on.get().strip()
    if v_on:
        vn = _parse_num(tab3_entry_led_on)
        led_fields.append(("Led_On Voltage", v_on, vn is not None and vn > 0))
    v_off = tab3_entry_led_off.get().strip()
    if v_off:
        vn = _parse_num(tab3_entry_led_off)
        led_fields.append(("Led_Off Voltage", v_off, vn is not None and 0 <= vn <= 10))
    if led_fields:
        sections.append({"name": "LED Test", "fields": led_fields, "overall": all(f[2] for f in led_fields)})

    # ── BAT ───────────────────────────────────────────────────────────────────
    v_bat = tab4_entry_1.get().strip()
    if v_bat:
        vn = _parse_num(tab4_entry_1)
        p = vn is not None and 8000 <= vn <= 16000
        sections.append({"name": "BAT Test", "fields": [("AiBatRef", v_bat, p)], "overall": p})

    # ── MOTOR ─────────────────────────────────────────────────────────────────
    if tab5_entry1.get().strip():
        vn = _parse_num(tab5_entry1); cn = _parse_num(tab5_entry2); en = _parse_num(tab5_entry3)
        p_v = vn is not None and vn > 0
        p_c = cn is not None and cn > 0
        p_e = en is not None and en == 0
        fields = [("MotorVoltage", tab5_entry1.get().strip(), p_v),
                  ("MotorCurrentValue", tab5_entry2.get().strip(), p_c),
                  ("MotorLoadError", tab5_entry3.get().strip(), p_e)]
        sections.append({"name": "Motor Test", "fields": fields, "overall": all([p_v, p_c, p_e])})

    # ── EOS ───────────────────────────────────────────────────────────────────
    eos_fields = []
    v_set = tab6_entry_eos_set.get().strip()
    if v_set:
        vn = _parse_num(tab6_entry_eos_set)
        eos_fields.append(("EOS Set Voltage", v_set, vn is not None and 1400 <= vn <= 1600))
    v_reset = tab6_entry_eos_reset.get().strip()
    if v_reset:
        vn = _parse_num(tab6_entry_eos_reset)
        eos_fields.append(("EOS Reset Voltage", v_reset, vn is not None and 1500 <= vn <= 3000))
    if eos_fields:
        sections.append({"name": "EOS Test", "fields": eos_fields, "overall": all(f[2] for f in eos_fields)})

    # ── SG ────────────────────────────────────────────────────────────────────
    if tab7_entry_1.get().strip():
        sg_names = ["DoPwrSg","Sg1PlusOpamp","Sg1MinusOpamp","Sg1Opamp","Sg2PlusOpamp","Sg2MinusOpamp","Sg2Opamp"]
        fields = []
        for nm, e in zip(sg_names, sg_entries):
            vn = _parse_num(e)
            fields.append((nm, e.get().strip(), vn is not None and vn != 0))
        sections.append({"name": "SG Test", "fields": fields, "overall": all(f[2] for f in fields)})

    # ── CAPA ──────────────────────────────────────────────────────────────────
    if tab8_entry_1.get().strip():
        capa_names   = ["CapaApproach","CapaLock","CapaUnlock","CapaApproachRawValue","CapaLockRawValue","CapaUnlockRawValue"]
        capa_checks  = [lambda v: v==1, lambda v: v==1, lambda v: v==1,
                        lambda v: v>8900, lambda v: v>8900, lambda v: v>8900]
        fields = []
        for nm, e, chk in zip(capa_names, capa_entries, capa_checks):
            vn = _parse_num(e)
            fields.append((nm, e.get().strip(), vn is not None and chk(vn)))
        sections.append({"name": "CAPA Test", "fields": fields, "overall": all(f[2] for f in fields)})

    # ── NFC ───────────────────────────────────────────────────────────────────
    if tab9_spi_err.get().strip():
        spi_v = tab9_spi_err.get().strip(); hw_v = tab9_hw_ver.get().strip()
        rom_v = tab9_rom_ver.get().strip();  fw_v = tab9_fw_ver.get().strip()
        card_v = tab9_entry_1.get().strip()
        p_spi = spi_v in ("OK", "0")
        p_hw  = hw_v  not in ("", "0", "0x0")
        p_rom = rom_v not in ("", "0", "0x0")
        p_fw  = fw_v  not in ("", "0", "0x0")
        p_card = card_v == "Yes"
        fields = [("SpiError", spi_v, p_spi), ("HwVersion", hw_v, p_hw),
                  ("RomVersion", rom_v, p_rom), ("FwVersion", fw_v, p_fw),
                  ("IsNfcDetectedCard", card_v, p_card)]
        sections.append({"name": "NFC Test", "fields": fields, "overall": all([p_spi, p_hw, p_rom, p_fw])})

    # ── NFC SELF ──────────────────────────────────────────────────────────────
    if tab9_st_spi_err.get().strip():
        spi_v = tab9_st_spi_err.get().strip(); hw_v = tab9_st_hw_ver.get().strip()
        led_v = tab9_st_led_v.get().strip()
        p_spi = spi_v in ("OK", "0")
        p_hw  = hw_v  not in ("", "0", "0x0")
        try:    p_led = float(led_v.split()[0]) > 0
        except: p_led = led_v not in ("", "N/A", "SKIP")
        fields = [("SpiError", spi_v, p_spi), ("TargetID", hw_v, p_hw), ("LedVoltage", led_v, p_led)]
        sections.append({"name": "NFC Self-Test", "fields": fields, "overall": all([p_spi, p_hw, p_led])})

    # ── CAN ───────────────────────────────────────────────────────────────────
    if tab10_rx_valid.get().strip():
        vn = _parse_num(tab10_rx_valid); an = _parse_num(tab10_com_active)
        p_rx  = vn is not None and vn == 1
        p_act = True if can_loopback_var.get() else (an is not None and an == 1)
        rx_fields = [(f"RxByte{i}", e.get().strip(), True) for i, e in enumerate(can_rx_entries)]
        fields = [("CanRxDataValid", tab10_rx_valid.get().strip(), p_rx),
                  ("CanIsActiveState", tab10_com_active.get().strip(), p_act)] + rx_fields
        sections.append({"name": "CAN Test", "fields": fields, "overall": all([p_rx, p_act])})

    # ── LIN ───────────────────────────────────────────────────────────────────
    if tab11_rx_valid.get().strip():
        vn = _parse_num(tab11_rx_valid)
        any_nz = any(_parse_num(e) not in (None, 0) for e in lin_rx_entries)
        p_rx   = vn is not None and vn == 1 and any_nz
        rx_fields = [(f"RxByte{i}", e.get().strip(), True) for i, e in enumerate(lin_rx_entries)]
        fields = [("LinRxDataValid", tab11_rx_valid.get().strip(), p_rx),
                  ("LinRxPid", tab11_rx_pid.get().strip(), True)] + rx_fields
        sections.append({"name": "LIN Test", "fields": fields, "overall": p_rx})

    manual_sections = list(sections)
    if deflash_result is not None:
        if manual_sections:
            df_pass = bool(deflash_result.get("pass", False))
            df_addrs = deflash_result.get("addrs", [])
            df_detail = deflash_result.get("detail", "") or "Blank-check completed"
            df_fields = [
                ("Result", "PASS" if df_pass else "FAIL", df_pass),
                ("Checked addresses", ", ".join(df_addrs) if df_addrs else "N/A", True),
                ("Detail", df_detail, True),
            ]
            sections.append({
                "name": "De-flash",
                "fields": df_fields,
                "overall": df_pass,
            })
        else:
            code_status_label.config(text="No manual test results to save.")
            return

    if not sections:
        code_status_label.config(text="No manual test results to save.")
        return

    overall_ok = all(s["overall"] for s in sections)
    global _manual_pass_count, _manual_fail_count
    if overall_ok:
        _manual_pass_count += 1
        _manual_pass_lbl.config(text=f"PASS\n{_manual_pass_count}")
    else:
        _manual_fail_count += 1
        _manual_fail_lbl.config(text=f"FAIL\n{_manual_fail_count}")

    scan_code = manual_scan_entry.get().strip()
    pcb_count = _manual_pass_count + _manual_fail_count
    try:
        path = _save_manual_report(sections, _REPORTS_DIR, _SW_REVISION,
                                   scan_code=scan_code, pcb_count=pcb_count)
        code_status_label.config(text=f"Manual report saved: {Path(path).name}")
    except Exception as exc:
        code_status_label.config(text=f"Manual report save failed: {exc}")


# Initialize visibility based on default selection (0)
update_tab_visibility()
# ==================================================================================================================
# ========== EXIT ==================================================================================================

# Create a global variable to hold the ID
poll_id = None

def poll_target_state(label, window):
    global poll_id
    try:
        running_status = dbg.fnc("Var.VALUE(TestFw_IsEcuSleeping)")
        # ... your existing logic ...
        
        # Save the ID returned by .after()
        poll_id = window.after(1000, lambda: poll_target_state(label, window))

    except Exception as e:
        poll_id = window.after(1000, lambda: poll_target_state(label, window))

def on_closing():
    if messagebox.askokcancel("Quit", "Do you want to quit and disconnect Trace32?"):
        # Stop the polling loop if it exists
        try:
            window.after_cancel(poll_id)
        except:
            pass
        QuitTrace32() # Ensure this function kills the process (see step 3)
        window.destroy()

#window = tk.Tk()
window.protocol("WM_DELETE_WINDOW", on_closing) # This line catches the 'X' button click

# Update the poll call to capture the ID
def start_polling():
    global poll_id
    poll_id = window.after(1000, lambda: poll_target_state(running_status, window))

start_polling()

window.resizable(True, True)
window.mainloop()
