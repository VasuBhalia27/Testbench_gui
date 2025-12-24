from pathlib import Path
import tkinter as tk
from tkinter import ttk, Button, PhotoImage
import ctypes
from Functional.power_supply import *
from Functional.trace32 import *
from tkinter import filedialog
from tkinter import messagebox


# try:
#     ctypes.windll.shcore.SetProcessDpiAwareness(1)
# except Exception:
#     ctypes.windll.user32.SetProcessDPIAware()


# ===================================================================================================================
# ========== function/classes definations ===========================================================================

class FooterBar:
    def __init__(self, parent, tab, tab_frame, canvas, images, relative_to_assets, set_voltage_callback, get_voltage_callback):
        self.parent = parent
        self.tab = tab
        self.tab_frame = tab_frame
        self.canvas = canvas
        self.images = images
        self.relative_to_assets = relative_to_assets
        self.set_voltage_callback = set_voltage_callback
        self.get_voltage_callback = get_voltage_callback
        
        self.setup_ui()
    
    def setup_ui(self):
        # Footer bar image
        self.images[f"{self.tab}_footerbar"] = PhotoImage(file=self.relative_to_assets("footer_bar.png", "tab2"))
        self.canvas.create_image(500, 606, image=self.images[f"{self.tab}_footerbar"])

        # Set voltage controls
        self.canvas.create_text(
            22.0,
            580.0,
            anchor="nw",
            text="Set power supply voltage",
            fill="#282828",
            font=("Inter Bold", 16 * -1)
        )

        self.voltage_set_entry = ttk.Entry(self.tab_frame, style='Background_grey.TEntry')
        self.voltage_set_entry.place(x=306.0, y=580.0, width=95.0, height=20.0)

        self.images[f"{self.tab}set_voltage_button"] = PhotoImage(file=self.relative_to_assets("set_or_get_voltage.png", "tab2"))
        self.set_voltage_btn = Button(
            self.tab,
            image=self.images[f"{self.tab}set_voltage_button"],
            command=lambda: self.set_voltage_callback(self.voltage_set_entry),
            bd=0
        )
        self.set_voltage_btn.place(x=413, y=576, width=25, height=26)

        # Get voltage controls
        self.canvas.create_text(
            22.0,
            613.0,
            anchor="nw",
            text="Get power supply voltage",
            fill="#282828",
            font=("Inter SemiBold", 16 * -1)
        )

        self.voltage_get_entry = ttk.Entry(self.tab_frame, style='Background_grey.TEntry')
        self.voltage_get_entry.place(x=306.0, y=613.0, width=95.0, height=20.0)

        self.images[f"{self.tab}get_voltage_button"] = PhotoImage(file=self.relative_to_assets("set_or_get_voltage.png", "tab2"))
        self.get_voltage_btn = Button(
            self.tab,
            image=self.images[f"{self.tab}get_voltage_button"],
            command=lambda: self.get_voltage_callback(self.voltage_get_entry),
            bd=0
        )
        self.get_voltage_btn.place(x=413, y=610, width=25, height=26)

        # Additional entry (tab2_entry9 from original code)
        self.additional_entry = ttk.Entry(self.tab_frame, style='Background_grey.TEntry')
        self.additional_entry.place(x=800.0, y=575.0, width=150.0, height=60.0)
        
    def update_additional_entry(footer_instance, new_value):
        footer_instance.additional_entry.delete(0, tk.END)
        footer_instance.additional_entry.insert(0, new_value)
        
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

usb_addr = Pwrcontrol_init() # power app initialization

# Define global image reference dictionary to prevent garbage collection
images = {}

# Base Paths
OUTPUT_PATH = Path(__file__).parent
ASSETS_PATH_TAB1 = OUTPUT_PATH / Path(r"assets_GC\Page_1(Welcome_page)\assets\frame0")
ASSETS_PATH_TAB2 = OUTPUT_PATH / Path(r"assets_GC\Page_2(Settings)\assets\frame0")
ASSETS_PATH_TAB3 = OUTPUT_PATH / Path(r"assets_GC\Page_3(Led)\assets\frame0")
ASSETS_PATH_TAB4 = OUTPUT_PATH / Path(r"assets_GC\Page_4(BattMon)\assets\frame0")
ASSETS_PATH_TAB5 = OUTPUT_PATH / Path(r"assets_GC\Page_5(Motor)\assets\frame0")
ASSETS_PATH_TAB6 = OUTPUT_PATH / Path(r"assets_GC\Page_6(Eos)\assets\frame0")
ASSETS_PATH_TAB7 = OUTPUT_PATH / Path(r"assets_GC\Page_7(Sg)\assets\frame0")
ASSETS_PATH_TAB8 = OUTPUT_PATH / Path(r"assets_GC\Page_8(Capa)\assets\frame0")
ASSETS_PATH_TAB9 = OUTPUT_PATH / Path(r"assets_GC\Page_9(Nfc)\assets\frame0")
ASSETS_PATH_TAB10 = OUTPUT_PATH / Path(r"assets_GC\Page_10(CAN)\assets\frame0")
ASSETS_PATH_TAB11 = OUTPUT_PATH / Path(r"assets_GC\Page_11(Lin)\assets\frame0")

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
    elif tab == "tab10":
        return ASSETS_PATH_TAB10 / Path(path)
    elif tab == "tab11":
        return ASSETS_PATH_TAB11 / Path(path)
    else:
        raise Exception

# Create the main window
window = tk.Tk()


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
# ========== TAB 1 ==================================================================================================

tab1 = ttk.Frame(notebook)
notebook.add(tab1, text="Versions")

canvas1 = tk.Canvas(tab1, bg="#DFDFDF", height=651, width=973, bd=0, highlightthickness=0, relief="ridge")
canvas1.place(x=0, y=0)


canvas1.create_rectangle(
    0.0,
    0.0,
    528.0,
    75.0,
    fill="#E8E8E8",
    outline="")


images["Welcome_text"] = PhotoImage(file=relative_to_assets("welcome_text.png","tab1"))
image_1 = canvas1.create_image(155.0,165.0,image=images["Welcome_text"])


images["minibea_logo"] = PhotoImage(file=relative_to_assets("minebea_logo.png", "tab1"))
canvas1.create_image(145.0, 37.0, image=images["minibea_logo"])

images["version_tile"] = PhotoImage(file=relative_to_assets("tile.png", "tab1"))
canvas1.create_image(196.0, 427.0, image=images["version_tile"])

canvas1.create_text(112.0, 280.0, anchor="nw", text="Select Version",
                   fill="#FFFFFF", font=("Inter", -24))

images["photo_with_hand"] = PhotoImage(file=relative_to_assets("image.png", "tab1"))
canvas1.create_image(746.0, 349.0, image=images["photo_with_hand"])

# Buttons in Tab 1
images["version1"] = PhotoImage(file=relative_to_assets("version1.png", "tab1"))
btn1_tab1 = Button(tab1, image=images["version1"], command=lambda: print("version1"), bd=0)
btn1_tab1.place(x=89, y=329, width=218, height=44)

images["version2"] = PhotoImage(file=relative_to_assets("version2.png", "tab1"))
btn2_tab1 = Button(tab1, image=images["version2"], command=lambda: print("version2"), bd=0)
btn2_tab1.place(x=89, y=390, width=219, height=45)

images["version3"] = PhotoImage(file=relative_to_assets("version3.png", "tab1"))
btn3_tab1 = Button(tab1, image=images["version3"], command=lambda: print("version3"), bd=0)
btn3_tab1.place(x=89, y=451, width=220, height=45)

images["version4"] = PhotoImage(file=relative_to_assets("version4.png", "tab1"))
btn4_tab1 = Button(tab1, image=images["version4"], command=lambda: print("version4"), bd=0)
btn4_tab1.place(x=89, y=512, width=220, height=45)

canvas1.create_text(
    260.0,
    20.0,
    anchor="nw",
    text="U-Shin India",
    fill="#0066B3",
    font=("Inter BoldItalic", 24 * -1)
)

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

# ===================================================================================================================
# ========== Tile-1 =================================================================================================
images["minibea_logo_2"] = PhotoImage(file=relative_to_assets("minebea_logo_2.png", "tab2"))
canvas2.create_image(145.0, 37.0, image=images["minibea_logo_2"])

images["tile1_tab2"] = PhotoImage(file=relative_to_assets("Tile.png", "tab2")) 
canvas2.create_image(245, 265, image=images["tile1_tab2"])

canvas2.create_text(61.0, 150.0, anchor="nw", text="Connect to Power Supply -->", fill="#FFFFFF", font=("Inter SemiBold", 15 * -1))
canvas2.create_text(61.0, 213.0, anchor="nw", text="Power ON -->", fill="#FFFFFF", font=("Inter SemiBold", 15 * -1))
canvas2.create_text(61.0, 269.0, anchor="nw", text="Power OFF -->", fill="#FFFFFF", font=("Inter SemiBold", 15 * -1))
canvas2.create_text(61.0, 325.0, anchor="nw", text="Connect to Trace32 --> ", fill="#FFFFFF", font=("Inter SemiBold", 15 * -1))
canvas2.create_text(61.0, 381.0, anchor="nw", text="Disconnect to Trace32 --> ", fill="#FFFFFF", font=("Inter SemiBold", 15 * -1))
canvas2.create_text(61.0, 437.0, anchor="nw", text="Select BMW Repository:  ", fill="#FFFFFF", font=("Inter SemiBold", 15 * -1))
canvas2.create_text(61.0, 556.0, anchor="nw", text="Note: Make sure ELF for the selected preset is generated  ", fill="#FF0000", font=("Inter SemiBold", 11 * -1))

images["tab2_tile1_run_test"] = PhotoImage(file=relative_to_assets("tab_testrun_button.png", "tab2"))
connect_to_Psupply = Button(tab2, image=images["tab2_tile1_run_test"], command=lambda: ConnectToPwrSup(usb_addr), bd = 0)
connect_to_Psupply.place(x=261, y=144, width=33, height=33)

images["tab2_tile1_run_test1"] = PhotoImage(file=relative_to_assets("tab_testrun_button.png", "tab2"))
pwr_sup_on = Button(tab2, image=images["tab2_tile1_run_test"], command=PowerSupOn, bd = 0)
pwr_sup_on.place(x=261, y=207, width=33, height=33)

images["tab2_tile1_run_test2"] = PhotoImage(file=relative_to_assets("tab_testrun_button.png", "tab2"))
pwr_sup_off = Button(tab2, image=images["tab2_tile1_run_test"], command=PowerSupOff, bd = 0)
pwr_sup_off.place(x=261, y=263, width=33, height=33)

images["tab2_tile1_run_test3"] = PhotoImage(file=relative_to_assets("tab_testrun_button.png", "tab2"))
connect_trace32 = Button(tab2, image=images["tab2_tile1_run_test"], command=lambda: Trace32ConnectApp(repo_path_entry, selected_preset), bd = 0)
connect_trace32.place(x=261, y=319, width=33, height=33)

images["tab2_tile1_run_test4"] = PhotoImage(file=relative_to_assets("tab_testrun_button.png", "tab2"))
disconnect_trace32 = Button(tab2, image=images["tab2_tile1_run_test"], command=DoNothing, bd = 0)
disconnect_trace32.place(x=261, y=375, width=33, height=33)

repo_path_entry = ttk.Entry(tab2, style ='Background_grey.TEntry')
repo_path_entry.place(x=261.0, y=431.0, width=400.0, height=30.0)
repo_browse_button = ttk.Button(tab2, text="Browse", command=browse_repo_path) #browse button to get repo path
repo_browse_button.place(x=680, y=431, width=70, height=30)

selected_preset = tk.IntVar(value=0)

selected_preset_relwithdeb = tk.Checkbutton(
    tab2,
    text="Realwithdebinfo",
    variable=selected_preset,
    onvalue=1,
    offvalue=0,
    command=lambda: preset_realwithdebinfo(selected_preset)
)
selected_preset_relwithdeb.place(x=61, y=487)

selected_preset_minsizerel = tk.Checkbutton(
    tab2,
    text="Minsizerel",
    variable=selected_preset,
    onvalue=2,
    offvalue=0,
    command=lambda: preset_minsizerel(selected_preset)
)
selected_preset_minsizerel.place(x=61 + 120, y=487)

if (usb_addr == None):
    connect_to_Psupply.config(state="disabled")
    pwr_sup_on.config(state="disabled")
    pwr_sup_off.config(state="disabled")
else:
    connect_to_Psupply.config(state="normal")
    pwr_sup_on.config(state="normal")
    pwr_sup_off.config(state="normal")

window.after(1000, lambda: poll_target_state(running_status, window))

canvas2.create_text(
    260.0,
    20.0,
    anchor="nw",
    text="U-Shin India",
    fill="#FFFFFF",
    font=("Inter BoldItalic", 24 * -1)
)

# ===================================================================================================================
# ========== TAB 3 (LED Test) =======================================================================================

tab3 = ttk.Frame(notebook)
notebook.add(tab3, text="LED Test")

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

# Entries
canvas3.create_text(73.0, 113.0, anchor="nw", text="LED Test (DID 101)", fill="#FFFFFF", font=("Inter SemiBold", 20 * -1))

canvas3.create_text(73.0, 168.0, anchor="nw", text="LedVoltage", fill="#FFFFFF", font=("Inter SemiBold", 15 * -1))
tab3_entry_1 = ttk.Entry(tab3_frame, style ='Background_grey.TEntry')
tab3_entry_1.place(x=306.0, y=168.0, width=95.0, height=20.0)

# Execution
led_output_variables = ["TestFw_LedVoltage"]
led_entries = [tab3_entry_1]

images["tab3_led_run"] = PhotoImage(file=relative_to_assets("tab_testrun_button.png", "tab3"))
# Note: Ensure GetValueVbatt or equivalent is linked if intended
tab3_run_btn = Button(tab3, image=images["tab3_led_run"],
                        command=lambda: SendDIDGetVal_multiple_entry(led_output_variables, led_entries, TestFunctionCmd.TESTFW_GUI_CMD_LED_TEST_e),
                        bd = 0)
tab3_run_btn.place(x=325, y=106, width=34, height=34)

reset_entries = ttk.Button(tab3, text="Reset Results", command=lambda: clear_entries(led_entries))
reset_entries.place(x=500, y=110, width=85, height=32)

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
canvas4.create_text(73.0, 113.0, anchor="nw", text="Battery Monitor (DID 102)", fill="#FFFFFF", font=("Inter SemiBold", 20 * -1))

canvas4.create_text(73.0, 168.0, anchor="nw", text="BatRefStatus", fill="#FFFFFF", font=("Inter SemiBold", 15 * -1))
tab4_entry_1 = ttk.Entry(tab4_frame, style ='Background_grey.TEntry')
tab4_entry_1.place(x=306.0, y=168.0, width=95.0, height=20.0)

canvas4.create_text(73.0, 214.0, anchor="nw", text="AiBatRef", fill="#FFFFFF", font=("Inter SemiBold", 15 * -1))
tab4_entry_2 = ttk.Entry(tab4_frame, style ='Background_grey.TEntry')
tab4_entry_2.place(x=306.0, y=214.0, width=95.0, height=20.0)

# Execution
batmot_output_variables = ["TestFw_BatRefStatus", "TestFw_AiBatRef"]
batmon_entries = [tab4_entry_1, tab4_entry_2]

images["tab4_motor_run"] = PhotoImage(file=relative_to_assets("tab_testrun_button.png", "tab4"))
# Note: Ensure GetValueVbatt or equivalent is linked if intended
tab4_run_btn = Button(tab4, image=images["tab4_motor_run"],
                        command=lambda: SendDIDGetVal_multiple_entry(batmot_output_variables, batmon_entries, TestFunctionCmd.TESTFW_GUI_CMD_BATT_MONITOR_e),
                        bd = 0)
tab4_run_btn.place(x=325, y=106, width=34, height=34)

reset_entries = ttk.Button(tab4, text="Reset Results", command=lambda: clear_entries(batmon_entries))
reset_entries.place(x=500, y=110, width=85, height=32)

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
notebook.add(tab5, text="Motor Test")

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
selected_motor_state = tk.IntVar(value=0)
motor_couple_cb = tk.Checkbutton(tab5, text="Motor Couple", variable=selected_motor_state, onvalue=1, offvalue=0, command=lambda: motor_couple(selected_motor_state))
motor_couple_cb.place(x=73.0, y=150)

motor_decouple_cb = tk.Checkbutton(tab5, text="Motor Decouple", variable=selected_motor_state, onvalue=2, offvalue=0, command=lambda: motor_decouple(selected_motor_state))
motor_decouple_cb.place(x=73.0 + 120, y=150)

# Entries
canvas5.create_text(73.0, 113.0, anchor="nw", text="Motor Test Results (DID 103)", fill="#FFFFFF", font=("Inter SemiBold", 20 * -1))
canvas5.create_text(73.0, placement_y_coord+35, anchor="nw", text="MotorCoupledVoltage", fill="#FFFFFF", font=("Inter SemiBold", 15 * -1))
tab5_entry1 = ttk.Entry(tab5_frame, style = 'Background_grey.TEntry')
tab5_entry1.place(x=306, y=placement_y_coord+35, width=95.0, height=20.0)

canvas5.create_text(73.0, placement_y_coord + 35*2, anchor="nw", text="MotorDecoupledVoltage", fill="#FFFFFF", font=("Inter SemiBold", 15 * -1))
tab5_entry2 = ttk.Entry(tab5_frame, style = 'Background_grey.TEntry')
tab5_entry2.place(x=306, y=placement_y_coord + 35*2, width=95.0, height=20.0)

canvas5.create_text(73.0, placement_y_coord + 35*3, anchor="nw", text="MotorCurrentValue", fill="#FFFFFF", font=("Inter SemiBold", 15 * -1))
tab5_entry3 = ttk.Entry(tab5_frame, style = 'Background_grey.TEntry')
tab5_entry3.place(x=306, y=placement_y_coord + 35*3, width=95.0, height=20.0)

canvas5.create_text(73.0, placement_y_coord + 35*4, anchor="nw", text="MotorLoadError", fill="#FFFFFF", font=("Inter SemiBold", 15 * -1))
tab5_entry4 = ttk.Entry(tab5_frame, style = 'Background_grey.TEntry')
tab5_entry4.place(x=306, y=placement_y_coord + 35*4, width=95.0, height=20.0)

# Execution
motor_output_variables = ["TestFw_MotorCoupledVoltage", "TestFw_MotorDecoupledVoltage", "TestFw_MotorCurrentValue", "TestFw_MotorLoadError"]
motor_entries = [tab5_entry1, tab5_entry2, tab5_entry3, tab5_entry4]

images["tab5_motor_run"] = PhotoImage(file=relative_to_assets("tab_testrun_button.png", "tab5"))
tab5_run_btn = Button(tab5, image=images["tab5_motor_run"], command=lambda: SendDIDGetVal_multiple_entry(motor_output_variables, motor_entries, TestFunctionCmd.TESTFW_GUI_CMD_MOTOR_TEST_e), bd = 0)
tab5_run_btn.place(x=368, y=113, width=34, height=34)

reset_entries = ttk.Button(tab5, text="Reset Results", command=lambda: clear_entries(motor_entries))
reset_entries.place(x=500, y=110, width=85, height=32)

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
notebook.add(tab6, text="EOS Tests")

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
canvas6.create_text(73.0, 113.0, anchor="nw", text="EOS Test (DID 104)", fill="#FFFFFF", font=("Inter SemiBold", 20 * -1))
canvas6.create_text(73.0, placement_y_coord+35*0, anchor="nw", text="TestFw_EosDiagVoltage", fill="#FFFFFF", font=("Inter SemiBold", 15 * -1))
tab6_entry1 = ttk.Entry(tab6_frame, style = 'Background_grey.TEntry')
tab6_entry1.place(x=306, y=placement_y_coord+35*0, width=95.0, height=20.0)

canvas6.create_text(73.0, placement_y_coord+35*1, anchor="nw", text="TestFw_EosPinState", fill="#FFFFFF", font=("Inter SemiBold", 15 * -1))
tab6_entry2 = ttk.Entry(tab6_frame, style = 'Background_grey.TEntry')
tab6_entry2.place(x=306, y=placement_y_coord+35*1, width=95.0, height=20.0)

canvas6.create_text(73.0, placement_y_coord+35*2, anchor="nw", text="TestFw_EosErrorsWithLow", fill="#FFFFFF", font=("Inter SemiBold", 15 * -1))
tab6_entry3 = ttk.Entry(tab6_frame, style = 'Background_grey.TEntry')
tab6_entry3.place(x=306, y=placement_y_coord+35*2, width=95.0, height=20.0)

canvas6.create_text(73.0, placement_y_coord+35*3, anchor="nw", text="TestFw_EosErrorsWithHigh", fill="#FFFFFF", font=("Inter SemiBold", 15 * -1))
tab6_entry4 = ttk.Entry(tab6_frame, style = 'Background_grey.TEntry')
tab6_entry4.place(x=306, y=placement_y_coord+35*3, width=95.0, height=20.0)


# Execution
eos_output_variables = ["TestFw_EosDiagVoltage", "TestFw_EosPinState", "TestFw_EosErrorsWithLow", "TestFw_EosErrorsWithHigh"]
eos_entries = [tab6_entry1, tab6_entry2, tab6_entry3, tab6_entry4]

images["tab6_eos_run"] = PhotoImage(file=relative_to_assets("tab_testrun_button.png", "tab6"))
tab6_run_btn = Button(tab6, image=images["tab6_eos_run"], command=lambda: SendDIDGetVal_multiple_entry(eos_output_variables, eos_entries, TestFunctionCmd.TESTFW_GUI_CMD_EOS_TEST_e), bd = 0)
tab6_run_btn.place(x=325, y=106, width=34, height=34)

reset_entries = ttk.Button(tab6, text="Reset Results", command=lambda: clear_entries(eos_entries))
reset_entries.place(x=500, y=110, width=85, height=32)

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
notebook.add(tab7, text="SG Sensor Tests")

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

SG_input_conditon = tk.IntVar(value=0)

motor_couple_cb = tk.Checkbutton(
    tab7,
    text="TestFw_Sg1ToggleGui",
    variable=SG_input_conditon,
    onvalue=1,
    offvalue=0,
    command=lambda: SG_input_1(selected_motor_state)
)
motor_couple_cb.place(x=34, y=110)

motor_decouple_cb = tk.Checkbutton(
    tab7,
    text="TestFw_Sg2ToggleGui",
    variable=SG_input_conditon,
    onvalue=2,
    offvalue=0,
    command=lambda: SG_input_2(selected_motor_state)
)
motor_decouple_cb.place(x=34+150, y=110)

motor_decouple_cb = tk.Checkbutton(
    tab7,
    text="SG no input",
    variable=SG_input_conditon,
    onvalue=3,
    offvalue=0,
    command=lambda: SG_no_input(selected_motor_state)
)
motor_decouple_cb.place(x=34+150+150, y=110)

# Entries
canvas7.create_text(34.0, 75.0, anchor="nw", text="Sg Test Outputs (DID 106)", fill="#FFFFFF", font=("Inter SemiBold", 20 * -1))

canvas7.create_text(34.0, offset_top + 0*40, anchor="nw",text="DoPwrSg", fill="#FFFFFF", font=("Inter SemiBold", 12 * -1))
tab7_entry_1 = ttk.Entry(tab7_frame, style='Background_grey.TEntry')
tab7_entry_1.place(x=180.0, y=offset_top + 0*40, width=95.0, height=20.0)

canvas7.create_text(34.0, offset_top + 1*40, anchor="nw",text="Sg1PlusOpamp", fill="#FFFFFF", font=("Inter SemiBold", 12 * -1))
tab7_entry2 = ttk.Entry(tab7_frame, style='Background_grey.TEntry')
tab7_entry2.place(x=180.0, y=offset_top + 1*40, width=95.0, height=20.0)

canvas7.create_text(34.0, offset_top + 2*40, anchor="nw",text="Sg1MinusOpamp", fill="#FFFFFF", font=("Inter SemiBold", 12 * -1))
tab7_entry3 = ttk.Entry(tab7_frame, style='Background_grey.TEntry')
tab7_entry3.place(x=180.0, y=offset_top + 2*40, width=95.0, height=20.0)

canvas7.create_text(34.0, offset_top + 3*40, anchor="nw",text="Sg1Opamp", fill="#FFFFFF", font=("Inter SemiBold", 12 * -1))
tab7_entry4 = ttk.Entry(tab7_frame, style='Background_grey.TEntry')
tab7_entry4.place(x=180.0, y=offset_top + 3*40, width=95.0, height=20.0)

canvas7.create_text(34.0, offset_top + 4*40, anchor="nw",text="Sg1Dac", fill="#FFFFFF", font=("Inter SemiBold", 12 * -1))
tab7_entry5 = ttk.Entry(tab7_frame, style='Background_grey.TEntry')
tab7_entry5.place(x=180.0, y=offset_top + 4*40, width=95.0, height=20.0)

canvas7.create_text(34.0, offset_top + 5*40, anchor="nw",text="Sg2PlusOpamp", fill="#FFFFFF", font=("Inter SemiBold", 12 * -1))
tab7_entry6 = ttk.Entry(tab7_frame, style='Background_grey.TEntry')
tab7_entry6.place(x=180.0, y=offset_top + 5*40, width=95.0, height=20.0)

canvas7.create_text(34.0, offset_top + 6*40, anchor="nw",text="Sg2MinusOpamp", fill="#FFFFFF", font=("Inter SemiBold", 12 * -1))
tab7_entry7 = ttk.Entry(tab7_frame, style='Background_grey.TEntry')
tab7_entry7.place(x=180.0, y=offset_top + 6*40, width=95.0, height=20.0)

canvas7.create_text(34.0, offset_top + 7*40, anchor="nw",text="Sg2Opamp", fill="#FFFFFF", font=("Inter SemiBold", 12 * -1))
tab7_entry8 = ttk.Entry(tab7_frame, style='Background_grey.TEntry')
tab7_entry8.place(x=180.0, y=offset_top + 7*40, width=95.0, height=20.0)

canvas7.create_text(34.0, offset_top + 8*40, anchor="nw",text="Sg2Dac", fill="#FFFFFF", font=("Inter SemiBold", 12 * -1))
tab7_entry9 = ttk.Entry(tab7_frame, style='Background_grey.TEntry')
tab7_entry9.place(x=180.0, y=offset_top + 8*40, width=95.0, height=20.0)

# Execution
sg_output_variables = ["TestFw_DoPwrSg", "TestFw_Sg1PlusOpamp", "TestFw_Sg1MinusOpamp", "TestFw_Sg1Opamp", "TestFw_Sg1Dac", "TestFw_Sg2PlusOpamp", "TestFw_Sg2MinusOpamp", "TestFw_Sg2Opamp", "TestFw_Sg2Dac"]
sg_entries = [tab7_entry_1, tab7_entry2, tab7_entry3, tab7_entry4, tab7_entry5, tab7_entry6, tab7_entry7, tab7_entry8, tab7_entry9]

images["tab7_sg_run"] = PhotoImage(file=relative_to_assets("tab_testrun_button.png", "tab7"))
tab7_run_btn = Button(tab7, image=images["tab7_sg_run"], command=lambda: SendDIDGetVal_multiple_entry(sg_output_variables, sg_entries, TestFunctionCmd.TEST_GUI_CMD_SG_TEST_e, True, running_status), bd = 0)
tab7_run_btn.place(x=445, y=110, width=31.073986053466797, height=31.845783233642578)

reset_entries = ttk.Button(tab7, text="Reset Results", command=lambda: clear_entries(sg_entries)) #browse button to get repo path
reset_entries.place(x=500, y=110, width=85, height=32)

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
notebook.add(tab8, text="Capa Sensor Tests")

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

# Entries
canvas8.create_text(73.0, 113.0, anchor="nw", text="Capa Test Outputs (DID 106)", fill="#FFFFFF", font=("Inter SemiBold", 20 * -1))
canvas8.create_text(73.0, 168.0, anchor="nw", text="CapaApproach", fill="#FFFFFF", font=("Inter SemiBold", 15 * -1))
tab8_entry_1 = ttk.Entry(tab8_frame, style ='Background_grey.TEntry')
tab8_entry_1.place(x=350.0, y=168.0, width=95.0, height=20.0)

canvas8.create_text(73.0, 214.0, anchor="nw", text="CapaLock", fill="#FFFFFF", font=("Inter SemiBold", 15 * -1))
tab8_entry_2 = ttk.Entry(tab8_frame, style = 'Background_grey.TEntry')
tab8_entry_2.place(x=350.0, y=214.0, width=95.0, height=20.0)

canvas8.create_text(73.0, 260.0, anchor="nw", text="CapaUnlock", fill="#FFFFFF", font=("Inter SemiBold", 15 * -1))
tab8_entry3 = ttk.Entry(tab8_frame, style = 'Background_grey.TEntry')
tab8_entry3.place(x=350.0, y=260.0, width=95.0, height=20.0)

canvas8.create_text(73.0, 306.0, anchor="nw", text="CapaApproachSensorValue", fill="#FFFFFF", font=("Inter SemiBold", 15 * -1))
tab8_entry4 = ttk.Entry(tab8_frame, style = 'Background_grey.TEntry')
tab8_entry4.place(x=350.0, y=306.0, width=95.0, height=20.0)

canvas8.create_text(73.0, 352.0, anchor="nw", text="CapaLockSensorValue", fill="#FFFFFF", font=("Inter SemiBold", 15 * -1))
tab8_entry5 = ttk.Entry(tab8_frame, style = 'Background_grey.TEntry')
tab8_entry5.place(x=350.0, y=352.0, width=95.0, height=20.0)

canvas8.create_text(73.0, 398.0, anchor="nw", text="CapaUnlockSensorValue", fill="#FFFFFF", font=("Inter SemiBold", 15 * -1))
tab8_entry6 = ttk.Entry(tab8_frame, style = 'Background_grey.TEntry')
tab8_entry6.place(x=350.0, y=398.0, width=95.0, height=20.0)

entry_list = [tab8_entry_1,tab8_entry_2, tab8_entry3, tab8_entry4, tab8_entry5, tab8_entry6]
capa_output_variables = ["TestFw_CapaApproach", "TestFw_CapaLock", "TestFw_CapaUnlock", "TestFw_CapaApproachSensorValue", "TestFw_CapaLockSensorValue", "TestFw_CapaUnlockSensorValue"]

images["tile1_run_capa"] = PhotoImage(file=relative_to_assets("tab_testrun_button.png", "tab8"))
run_test_btn = Button(tab8, image=images["tile1_run_capa"], command=lambda: SendDIDGetVal_multiple_entry(capa_output_variables, entry_list, TestFunctionCmd.TEST_GUI_CMD_CAPA_TEST_e), bd = 0)
run_test_btn.place(x=368, y=106, width=34, height=34)

reset_entries = ttk.Button(tab8, text="Reset Results", command=lambda: clear_entries(entry_list))
reset_entries.place(x=500, y=110, width=85, height=32)

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

canvas9.create_text(73.0, 113.0, anchor="nw", text="NFC Test Outputs (DID 107)", fill="#FFFFFF", font=("Inter SemiBold", 20 * -1))

canvas9.create_text(73.0, 168.0, anchor="nw", text="IsNfcDetectedCard", fill="#FFFFFF", font=("Inter SemiBold", 15 * -1))
tab9_entry_1 = ttk.Entry(tab9_frame, style ='Background_grey.TEntry')
tab9_entry_1.place(x=306.0, y=168.0, width=95.0, height=20.0)

nfc_entries = [tab9_entry_1]
nfc_output_variables = ["TestFw_IsNfcDetectedCard"]

images["tab9_nfc_run"] = PhotoImage(file=relative_to_assets("tab_testrun_button.png", "tab9"))
run_test_btn = Button(tab9, image=images["tab9_nfc_run"], command=lambda: SendDIDGetVal_multiple_entry(nfc_output_variables, nfc_entries, TestFunctionCmd.TEST_GUI_CMD_NFC_TEST_e), bd = 0)
run_test_btn.place(x=325, y=106, width=34, height=34)

reset_entries = ttk.Button(tab9, text="Reset Results", command=lambda: clear_entries(entry_list))
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

canvas10.create_text(61.0, 110.0, anchor="nw", text="CAN Test Outputs (DID 108)", fill="#FFFFFF", font=("Inter SemiBold", 20 * -1))
canvas10.create_text(61.0, 144.0, anchor="nw", text="Transmit CAN Message ID", fill="#FFFFFF", font=("Inter SemiBold", 15 * -1))
tab10_entry_1 = ttk.Entry(tab10_frame, style ='Background_grey.TEntry')
tab10_entry_1.place(x=61.0, y=168.0, width=250.0, height=20.0)

canvas10.create_text(61.0, 207.0, anchor="nw", text="Receive CAN Message ID", fill="#FFFFFF", font=("Inter SemiBold", 15 * -1))
tab10_entry_2 = ttk.Entry(tab10_frame, style ='Background_grey.TEntry')
tab10_entry_2.place(x=61.0, y=230.0, width=250.0, height=20.0)

can_entries = [tab10_entry_1]
can_output_variables = ["DummyBytes"]

images["tab10_can_run"] = PhotoImage(file=relative_to_assets("tab_testrun_button.png", "tab10"))
run_test_btn = Button(tab10, image=images["tab10_can_run"], command=lambda: SendDIDGetVal_multiple_entry(can_output_variables, can_entries, TestFunctionCmd.TEST_GUI_CMD_CAN_TEST_e), bd = 0)
run_test_btn.place(x=225, y=106, width=34, height=34)

reset_entries = ttk.Button(tab10, text="Reset Results", command=lambda: clear_entries(entry_list))
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

canvas11.create_text(61.0, 110.0, anchor="nw", text="LIN Test", fill="#FFFFFF", font=("Inter SemiBold", 20 * -1))
canvas11.create_text(61.0, 144.0, anchor="nw", text="Transmit LIN Message ID", fill="#FFFFFF", font=("Inter SemiBold", 15 * -1))
canvas11.create_text(61.0, 207.0, anchor="nw", text="Receive LIN Message ID", fill="#FFFFFF", font=("Inter SemiBold", 15 * -1))

tab11_entry1 = ttk.Entry(tab11_frame, style = 'Background_grey.TEntry')
tab11_entry1.place(x=61.0, y=168.0, width=250.0, height=20.0)

tab11_entry2 = ttk.Entry(tab11_frame, style = 'Background_grey.TEntry')
tab11_entry2.place(x=61.0, y=230.0, width=250.0, height=20.0)

images["tab11_lin_run"] = PhotoImage(file=relative_to_assets("tab_testrun_button.png", "tab11"))
tab11_run_btn = Button(tab11, image=images["tab11_lin_run"], command=lambda: print("tile two capa run test ..."), bd = 0)
tab11_run_btn.place(x=225, y=106, width=34, height=34)

canvas11.create_text(
    260.0,
    20.0,
    anchor="nw",
    text="U-Shin India",
    fill="#FFFFFF",
    font=("Inter BoldItalic", 24 * -1)
)

# ==================================================================================================================
# ========== EXIT ==================================================================================================
window.resizable(True, True)
window.mainloop()
