from pathlib import Path
import tkinter as tk
from tkinter import ttk, Button, PhotoImage
import ctypes
from Functional.power_supply import *
from Functional.trace32 import *
from Functional.canoe import *


try:
    ctypes.windll.shcore.SetProcessDpiAwareness(1)
except Exception:
    ctypes.windll.user32.SetProcessDPIAware()


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



# ===================================================================================================================
# ========== Initializations ========================================================================================

usb_addr = Pwrcontrol_init() # power app initialization

# Define global image reference dictionary to prevent garbage collection
images = {}

# Base Paths
OUTPUT_PATH = Path(__file__).parent
ASSETS_PATH_TAB1 = OUTPUT_PATH / Path(r"assets_GC\Page_1(Welcome_page)\assets\frame0")
ASSETS_PATH_TAB2 = OUTPUT_PATH / Path(r"assets_GC\Page_2(Capa)\assets\frame0")
ASSETS_PATH_TAB3 = OUTPUT_PATH / Path(r"assets_GC\Page_3(SG)\assets\frame0")
ASSETS_PATH_TAB4 = OUTPUT_PATH / Path(r"assets_GC\Page_4(EMV)\assets\frame0")
ASSETS_PATH_TAB5 = OUTPUT_PATH / Path(r"assets_GC\Page_5(NFC)\assets\frame0")
ASSETS_PATH_TAB6 = OUTPUT_PATH / Path(r"assets_GC\Page_6(CAN-LIN)\assets\frame0")
ASSETS_PATH_TAB8 = OUTPUT_PATH / Path(r"assets_GC\Page_8(settings)\assets\frame0")

path_to_cfg = r"D:\RestBusSimulationMunich\Handle\Configurations\Handle.cfg"

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
        return ASSETS_PATH_TAB2 / Path(path)
    elif tab == "tab8":
        return ASSETS_PATH_TAB8 / Path(path)
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
# ========== TAB 2 ==================================================================================================



tab2 = ttk.Frame(notebook)
notebook.add(tab2, text="TP Coding Tests")

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

images["tile_tab2"] = PhotoImage(file=relative_to_assets("Tile.png", "tab2")) 
canvas2.create_image(tablet1_X, tablet1_Y, image=images["tile_tab2"])

canvas2.create_text(73.0, 113.0, anchor="nw", text="TP Coding Version Test", fill="#FFFFFF", font=("Inter SemiBold", 20 * -1))
canvas2.create_text(73.0, 168.0, anchor="nw", text="Running Status", fill="#FFFFFF", font=("Inter SemiBold", 15 * -1))
canvas2.create_text(73.0, 214.0, anchor="nw", text="Test Result", fill="#FFFFFF", font=("Inter SemiBold", 15 * -1))

tab2_entry_1 = ttk.Entry(tab2_frame, style ='Background_grey.TEntry')
tab2_entry_1.place(x=196.0, y=168.0, width=200.0, height=20.0)


tab2_entry_2 = ttk.Entry(tab2_frame, style = 'Background_grey.TEntry')
tab2_entry_2.place(x=246.0, y=214.0, width=150.0, height=20.0)

images["tile1_run_test"] = PhotoImage(file=relative_to_assets("tab_testrun_button.png", "tab2"))
run_test_tile1 = Button(tab2, image=images["tile1_run_test"], command=lambda: TP_coding_process_test(tab2_entry_1, tab2_entry_2), bd = 0)
run_test_tile1.place(x=368, y=106, width=34, height=34)

# ===================================================================================================================
# ========== Tile-2 =================================================================================================

images["tile2_tab2"] = PhotoImage(file=relative_to_assets("Tile.png", "tab2")) 
canvas2.create_image((tablet1_X + 475), (tablet1_Y + 0), image=images["tile2_tab2"])

canvas2.create_text(560.0, 113.0, anchor="nw", text="CRC-16 check", fill="#FFFFFF", font=("Inter SemiBold", 20 * -1))
canvas2.create_text(560.0, 168.0, anchor="nw", text="Running Status", fill="#FFFFFF", font=("Inter SemiBold", 15 * -1))
canvas2.create_text(560.0, 214.0, anchor="nw", text="Test Status", fill="#FFFFFF", font=("Inter SemiBold", 15 * -1))


tab2_entry3 = ttk.Entry(tab2_frame, style = 'Background_grey.TEntry')
tab2_entry3.place(x=780.0, y=168.0, width=95.0, height=20.0)


tab2_entry4 = ttk.Entry(tab2_frame, style = 'Background_grey.TEntry')
tab2_entry4.place(x=780.0, y=214.0, width=95.0, height=20.0)

images["tile2_run_test"] = PhotoImage(file=relative_to_assets("tab_testrun_button.png", "tab2"))
run_test_tile2 = Button(tab2, image=images["tile2_run_test"], command=TP_coding_changeableparameter_test, bd = 0)
run_test_tile2.place(x=840 , y=106, width=34, height=34)




# ===================================================================================================================
# ========== Footerbar ==============================================================================================

footer2 = FooterBar(
    parent=window,  # or whatever your root window is
    tab=tab2,
    tab_frame=tab2_frame,
    canvas=canvas2,
    images=images,
    relative_to_assets=relative_to_assets,
    set_voltage_callback=SetVoltage,
    get_voltage_callback=GetVoltage
)

# ===================================================================================================================
# ========== Toolbar ================================================================================================

toolbar = ToolBar(
    parent = window,
    tab = tab2,
    tab_frame = tab2_frame,
    canvas = canvas2,
    images = images,
    relative_to_assets= relative_to_assets,
    run_code_callback = DoNothing,
    pause_code_callback=DoNothing
)



# ===================================================================================================================
# ===================================================================================================================
# ========== TAB 8 (Settings) =======================================================================================


tab8 = ttk.Frame(notebook)
notebook.add(tab8, text="Settings")

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

canvas8.create_text(61.0, 144.0, anchor="nw", text="Connect to Power Supply -->", fill="#000000", font=("Inter SemiBold", 15 * -1))
canvas8.create_text(61.0, 207.0, anchor="nw", text="Power ON -->", fill="#000000", font=("Inter SemiBold", 15 * -1))
canvas8.create_text(61.0, 263.0, anchor="nw", text="Power OFF -->", fill="#000000", font=("Inter SemiBold", 15 * -1))
canvas8.create_text(61.0, 319.0, anchor="nw", text="Connect to Trace32 --> ", fill="#000000", font=("Inter SemiBold", 15 * -1))
canvas8.create_text(61.0, 375.0, anchor="nw", text="Disconnect to Trace32 --> ", fill="#000000", font=("Inter SemiBold", 15 * -1))
canvas8.create_text(61.0, 431.0, anchor="nw", text="enter repository path:  ", fill="#000000", font=("Inter SemiBold", 15 * -1))
canvas8.create_text(61.0, 487.0, anchor="nw", text="connect to Canoe -->  ", fill="#000000", font=("Inter SemiBold", 15 * -1))



images["tab8_tile1_run_test"] = PhotoImage(file=relative_to_assets("tab_testrun_button.png", "tab8"))
if (usb_addr == None):
    connect_to_Psupply = Button(tab8, image=images["tab8_tile1_run_test"], command=DoNothing, bd = 0)
else:
    connect_to_Psupply = Button(tab8, image=images["tab8_tile1_run_test"], command=lambda: ConnectToPwrSup(usb_addr), bd = 0)
connect_to_Psupply.place(x=261, y=144, width=33, height=33)

images["tab8_tile1_run_test1"] = PhotoImage(file=relative_to_assets("tab_testrun_button.png", "tab8"))
pwr_sup_on = Button(tab8, image=images["tab8_tile1_run_test"], command=PowerSupOn, bd = 0)
pwr_sup_on.place(x=261, y=207, width=33, height=33)

images["tab8_tile1_run_test2"] = PhotoImage(file=relative_to_assets("tab_testrun_button.png", "tab8"))
pwr_sup_off = Button(tab8, image=images["tab8_tile1_run_test"], command=PowerSupOff, bd = 0)
pwr_sup_off.place(x=261, y=263, width=33, height=33)

images["tab8_tile1_run_test3"] = PhotoImage(file=relative_to_assets("tab_testrun_button.png", "tab8"))
connect_trace32 = Button(tab8, image=images["tab8_tile1_run_test"], command=Trace32ConnectApp, bd = 0)
connect_trace32.place(x=261, y=319, width=33, height=33)

images["tab8_tile1_run_test4"] = PhotoImage(file=relative_to_assets("tab_testrun_button.png", "tab8"))
disconnect_trace32 = Button(tab8, image=images["tab8_tile1_run_test"], command=QuitTrace32, bd = 0)
disconnect_trace32.place(x=261, y=375, width=33, height=33)

repo_path_entry = ttk.Entry(tab8, style ='Background_grey.TEntry')
repo_path_entry.place(x=261.0, y=431.0, width=400.0, height=20.0)

images["tab8_tile1_run_test5"] = PhotoImage(file=relative_to_assets("tab_testrun_button.png", "tab8"))
disconnect_trace32 = Button(tab8, image=images["tab8_tile1_run_test"], command=lambda: load_and_start_canoe_config(path_to_cfg), bd = 0)
disconnect_trace32.place(x=261, y=487, width=33, height=33)

# ==================================================================================================================
# ========== EXIT ==================================================================================================


window.resizable(False, False)
window.mainloop()
