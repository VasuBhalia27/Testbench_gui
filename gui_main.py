from pathlib import Path
import tkinter as tk
from tkinter import ttk, Button, PhotoImage
from Functional.power_supply import *
from Functional.trace32 import *



# try:
#     ctypes.windll.shcore.SetProcessDpiAwareness(1)
# except Exception:
#     ctypes.windll.user32.SetProcessDPIAware()


# ===================================================================================================================
# ========== function/classes definations ===========================================================================

class PlacementManager():

    def __init__(self):
        self.x_offset = 0
        self.y_offset = 0
        self.x_interelement_spacing = 0
        self.y_interelement_spacing = 0

        

    def y_interelement_spacing_ret(self, number_of_element = 1, adjustment = 0):

        if number_of_element != 0:
            
            if number_of_element == 1:
                self.number_of_element = number_of_element
                self.adjustment = adjustment

                return self.adjustment + self.y_offset
            
            else: 
                self.number_of_element = number_of_element - 1
                self.adjustment = adjustment

                return self.y_interelement_spacing * self.number_of_element + self.adjustment + self.y_offset
        
        else:
            raise ValueError("value of number_of_element cannot be zero")



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
        
class ToolBar:
    def __init__(self, tab, tab_frame, canvas, images, relative_to_assets):

        self.tab = tab
        self.tab_frame = tab_frame
        self.canvas = canvas
        self.images = images
        self.relative_to_assets = relative_to_assets

        
        self.gui_for_toolbar()
        
    def gui_for_toolbar(self):
        
        
        self.images[f"{self.tab}tab6_toptoolbar"] = PhotoImage(file=self.relative_to_assets("top_toolbar.png", "tab6")) #tool bar
        self.canvas.create_image(179, 19, image=self.images[f"{self.tab}tab6_toptoolbar"]) 

        self.images[f"{self.tab}minebea_logo"] = PhotoImage(file=self.relative_to_assets("minebea_logo.png", "tab1")) #minebea logo
        self.canvas.create_image(135, 37, image=self.images[f"{self.tab}minebea_logo"])

        self.canvas.create_text(800.0,23.0,anchor="nw",text="U-shin India",fill="#0066B3",font=("Inter BoldItalic", 24 * -1)
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

def relative_to_assets(path: str, tab: str) -> Path:
    if tab == "tab1":
        return ASSETS_PATH_TAB1 / Path(path)
    elif tab == "tab2":
        return ASSETS_PATH_TAB2 / Path(path)
    elif tab == "tab3":
        return ASSETS_PATH_TAB3 / Path(path)
    elif tab == "tab4":
        return ASSETS_PATH_TAB4 / Path(path)
    elif tab == "tab4a":
        return ASSETS_PATH_TAB4 / Path(path)
    elif tab == "tab4b":
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
canvas1.create_image(256, 436, image=images["version_tile"])

canvas1.create_text(71.0, 300.0, anchor="nw", text="Setup", fill="#525252", font=("Inter", -24))

images["photo_with_hand"] = PhotoImage(file=relative_to_assets("image.png", "tab1"))
canvas1.create_image(746.0, 349.0, image=images["photo_with_hand"])

# Buttons in Tab 1
x_offset_tab1_btns = 71
y_offset_tab1_btns = 360

x_interelement_spacing = 0
y_text_widget_spacing = 70

images["connect_to_trace"] = PhotoImage(file=relative_to_assets("connect_to_trace.png", "tab1"))
btn1_tab1 = Button(tab1, image=images["connect_to_trace"], command=lambda: Trace32ConnectApp(trace_connection_status), bd=0)
btn1_tab1.place(x=x_offset_tab1_btns, y=y_offset_tab1_btns + y_text_widget_spacing*0, width=355.32, height=37)
trace_connection_status = tk.Label(tab1, text="Not Connected")
trace_connection_status.config(bg="#797979", fg = "red")
trace_connection_status.place(x=x_offset_tab1_btns + 262, y = y_offset_tab1_btns + 8)


images["add_elf_path"] = PhotoImage(file=relative_to_assets("add_elf_path.png", "tab1"))
btn2_tab2 = Button(tab1, image=images["add_elf_path"], command=lambda: print("version2"), bd=0)
btn2_tab2.place(x=x_offset_tab1_btns, y=y_offset_tab1_btns + y_text_widget_spacing * 1, width=355.32, height=37)
elf_path_status = tk.Label(tab1, text="ELF not found")
elf_path_status.config(bg="#797979", fg = "red")
elf_path_status.place(x=x_offset_tab1_btns + 262, y = (y_offset_tab1_btns + 8) + y_text_widget_spacing *1)  


images["connect_to_pwrsply"] = PhotoImage(file=relative_to_assets("connect_to_pwrsply.png", "tab1"))
btn3_tab3 = Button(tab1, image=images["connect_to_pwrsply"], command=lambda: print("version3"), bd=0)
btn3_tab3.place(x=x_offset_tab1_btns, y=y_offset_tab1_btns + y_text_widget_spacing*2, width=355.32, height=37)
pwrsply_connection_status = tk.Label(tab1, text="Not Connected")
pwrsply_connection_status.config(bg="#797979", fg = "red")
pwrsply_connection_status.place(x=x_offset_tab1_btns + 262, y = (y_offset_tab1_btns + 8) + y_text_widget_spacing * 2) 


canvas1.create_text(
    334.0,
    23.0,
    anchor="nw",
    text="U-shin India",
    fill="#0066B3",
    font=("Inter BoldItalic", 24 * -1)
)


# ===================================================================================================================
# ========== TAB 2 ==================================================================================================

pm_tab2 = PlacementManager()
pm_tab2.x_offset = 73
pm_tab2.y_offset = 150
pm_tab2.x_interelement_spacing = 277
pm_tab2.y_interelement_spacing = 60


# ===================================================================================================================
# ========== Page Constructors ======================================================================================

tab2 = ttk.Frame(notebook)
notebook.add(tab2, text="Capa Sensor Tests")

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

# images["tile_tab2"] = PhotoImage(file=relative_to_assets("Tile.png", "tab2")) 
# canvas2.create_image(tablet1_X, tablet1_Y, image=images["tile_tab2"])



canvas2.create_text(pm_tab2.x_offset, pm_tab2.y_interelement_spacing_ret(number_of_element = 1), anchor="nw", text="Capa Test Outputs", fill="#000000", font=("Inter SemiBold", 20 * -1))#heading

canvas2.create_text(pm_tab2.x_offset,  pm_tab2.y_interelement_spacing_ret(number_of_element = 2), anchor="nw", text="TestFw_CapaApproach", fill="#000000", font=("Inter SemiBold", 15 * -1))
tab2_entry_1 = ttk.Entry(tab2_frame, style ='Background_grey.TEntry')
tab2_entry_1.place(x=350.0, y = pm_tab2.y_interelement_spacing_ret(number_of_element = 2), width=95.0, height=20.0)


canvas2.create_text(pm_tab2.x_offset, pm_tab2.y_interelement_spacing_ret(number_of_element = 3), anchor="nw", text="TestFw_CapaLock", fill="#000000", font=("Inter SemiBold", 15 * -1))
tab2_entry_2 = ttk.Entry(tab2_frame, style = 'Background_grey.TEntry')
tab2_entry_2.place(x=350.0, y = pm_tab2.y_interelement_spacing_ret(number_of_element = 3), width=95.0, height=20.0)


canvas2.create_text(pm_tab2.x_offset, pm_tab2.y_interelement_spacing_ret(number_of_element = 4), anchor="nw", text="CapaUnlock", fill="#000000", font=("Inter SemiBold", 15 * -1))
tab2_entry3 = ttk.Entry(tab2_frame, style = 'Background_grey.TEntry')
tab2_entry3.place(x=350.0, y=pm_tab2.y_interelement_spacing_ret(number_of_element = 4), width=95.0, height=20.0)


canvas2.create_text(pm_tab2.x_offset, pm_tab2.y_interelement_spacing_ret(number_of_element = 5), anchor="nw", text="CapaApproachSensorValue", fill="#000000", font=("Inter SemiBold", 15 * -1))
tab2_entry4 = ttk.Entry(tab2_frame, style = 'Background_grey.TEntry')
tab2_entry4.place(x=350.0, y=pm_tab2.y_interelement_spacing_ret(number_of_element = 5), width=95.0, height=20.0)


canvas2.create_text(pm_tab2.x_offset, pm_tab2.y_interelement_spacing_ret(number_of_element = 6), anchor="nw", text="CapaLockSensorValue", fill="#000000", font=("Inter SemiBold", 15 * -1))
tab2_entry5 = ttk.Entry(tab2_frame, style = 'Background_grey.TEntry')
tab2_entry5.place(x=350.0, y=pm_tab2.y_interelement_spacing_ret(number_of_element = 6), width=95.0, height=20.0)


canvas2.create_text(pm_tab2.x_offset, pm_tab2.y_interelement_spacing_ret(number_of_element = 7), anchor="nw", text="CapaUnlockSensorValue", fill="#000000", font=("Inter SemiBold", 15 * -1))
tab2_entry6 = ttk.Entry(tab2_frame, style = 'Background_grey.TEntry')
tab2_entry6.place(x=350.0, y= pm_tab2.y_interelement_spacing_ret(number_of_element = 7), width=95.0, height=20.0)

entry_list = [tab2_entry_1,tab2_entry_2, tab2_entry3, tab2_entry4, tab2_entry5, tab2_entry6]
capa_output_variables = ["TestFw_CapaApproach", "TestFw_CapaLock", "TestFw_CapaUnlock", "TestFw_CapaApproachSensorValue", "TestFw_CapaLockSensorValue", "TestFw_CapaUnlockSensorValue"]

# images["tab3_tile3_run_test"] = PhotoImage(file=relative_to_assets("tab_testrun_button.png", "tab3"))
# tab3_run_test_tile3 = Button(tab3, image=images["tab3_tile3_run_test"], command=lambda: SendDIDGetVal_multiple_entry(sg_output_variables, sg_entries, TestFunctionCmd.TEST_GUI_CMD_SG_TEST_e, True, running_status), bd = 0)
# tab3_run_test_tile3.place(x=450, y=110, width=31.073986053466797, height=31.845783233642578)

images["tile1_run_test"] = PhotoImage(file=relative_to_assets("tab_testrun_button.png", "tab2"))
run_test_tile1 = Button(tab2, image=images["tile1_run_test"], command=lambda: SendDIDGetVal_multiple_entry(capa_output_variables, entry_list, TestFunctionCmd.TEST_GUI_CMD_CAPA_TEST_e), bd = 0)
run_test_tile1.place(x=368, y=pm_tab2.y_interelement_spacing_ret(number_of_element = 1), width=31.073986053466797, height=31.073986053466797)



# ===================================================================================================================
# ========== Footerbar ==============================================================================================



# ===================================================================================================================
# ========== Toolbar ================================================================================================


ToolBar(tab2, tab2_frame, canvas2 , images, relative_to_assets)

# ===================================================================================================================
# ===================================================================================================================
# ========== TAB 3 (SG tests) =======================================================================================

pm_tab3 = PlacementManager()
pm_tab3.x_offset = 73
pm_tab3.y_offset = 150
pm_tab3.x_interelement_spacing = 277
pm_tab3.y_interelement_spacing = 40


# ===================================================================================================================
# ========== Page Constructors ======================================================================================

tab3 = ttk.Frame(notebook)
notebook.add(tab3, text="SG Sensor Tests")

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
x_offset = 150  # offset from top of the frame/window


SG_input_conditon = tk.IntVar(value=0)

motor_couple_cb = tk.Checkbutton(
    tab3,
    text="TestFw_Sg1ToggleGui",
    variable=SG_input_conditon,
    onvalue=1,
    offvalue=0,
    command=lambda: SG_input_1(selected_motor_state)
)
motor_couple_cb.place(x=34, y=110)



motor_decouple_cb = tk.Checkbutton(
    tab3,
    text="TestFw_Sg2ToggleGui",
    variable=SG_input_conditon,
    onvalue=2,
    offvalue=0,
    command=lambda: SG_input_2(selected_motor_state)
)
motor_decouple_cb.place(x=34+150, y=110)



motor_decouple_cb = tk.Checkbutton(
    tab3,
    text="SG no input",
    variable=SG_input_conditon,
    onvalue=3,
    offvalue=0,
    command=lambda: SG_no_input(selected_motor_state)
)
motor_decouple_cb.place(x=34+150+150, y=110)


canvas3.create_text(pm_tab3.x_offset, pm_tab3.y_interelement_spacing_ret(number_of_element = 1), anchor="nw",
    text="DoPwrSg", fill="#000000", font=("Inter SemiBold", 12 * -1))
tab3_entry_1 = ttk.Entry(tab3_frame, style='Background_grey.TEntry')
tab3_entry_1.place(x=180.0, y= pm_tab3.y_interelement_spacing_ret(number_of_element = 1), width=95.0, height=20.0)


canvas3.create_text(pm_tab3.x_offset, pm_tab3.y_interelement_spacing_ret(number_of_element = 2), anchor="nw",
    text="Sg1PlusOpamp", fill="#000000", font=("Inter SemiBold", 12 * -1))
tab3_entry2 = ttk.Entry(tab3_frame, style='Background_grey.TEntry')
tab3_entry2.place(x=180.0, y= pm_tab3.y_interelement_spacing_ret(number_of_element = 2), width=95.0, height=20.0)


canvas3.create_text(pm_tab3.x_offset, pm_tab3.y_interelement_spacing_ret(number_of_element = 3), anchor="nw",
    text="Sg1MinusOpamp", fill="#000000", font=("Inter SemiBold", 12 * -1))
tab3_entry3 = ttk.Entry(tab3_frame, style='Background_grey.TEntry')
tab3_entry3.place(x=180.0, y= pm_tab3.y_interelement_spacing_ret(number_of_element = 3), width=95.0, height=20.0)


canvas3.create_text(pm_tab3.x_offset, pm_tab3.y_interelement_spacing_ret(number_of_element = 4), anchor="nw",
    text="Sg1Opamp", fill="#000000", font=("Inter SemiBold", 12 * -1))
tab3_entry4 = ttk.Entry(tab3_frame, style='Background_grey.TEntry')
tab3_entry4.place(x=180.0, y= pm_tab3.y_interelement_spacing_ret(number_of_element = 4), width=95.0, height=20.0)


canvas3.create_text(pm_tab3.x_offset,pm_tab3.y_interelement_spacing_ret(number_of_element = 5), anchor="nw",
    text="Sg1Dac", fill="#000000", font=("Inter SemiBold", 12 * -1))
tab3_entry5 = ttk.Entry(tab3_frame, style='Background_grey.TEntry')
tab3_entry5.place(x=180.0, y= pm_tab3.y_interelement_spacing_ret(number_of_element = 5), width=95.0, height=20.0)


canvas3.create_text(pm_tab3.x_offset,pm_tab3.y_interelement_spacing_ret(number_of_element = 6), anchor="nw",
    text="Sg2PlusOpamp", fill="#000000", font=("Inter SemiBold", 12 * -1))
tab3_entry6 = ttk.Entry(tab3_frame, style='Background_grey.TEntry')
tab3_entry6.place(x=180.0, y= pm_tab3.y_interelement_spacing_ret(number_of_element = 6), width=95.0, height=20.0)


canvas3.create_text(pm_tab3.x_offset, pm_tab3.y_interelement_spacing_ret(number_of_element = 7), anchor="nw",
    text="Sg2MinusOpamp", fill="#000000", font=("Inter SemiBold", 12 * -1))
tab3_entry7 = ttk.Entry(tab3_frame, style='Background_grey.TEntry')
tab3_entry7.place(x=180.0, y= pm_tab3.y_interelement_spacing_ret(number_of_element = 7), width=95.0, height=20.0)


canvas3.create_text(pm_tab3.x_offset,pm_tab3.y_interelement_spacing_ret(number_of_element = 8), anchor="nw",
    text="Sg2Opamp", fill="#000000", font=("Inter SemiBold", 12 * -1))
tab3_entry8 = ttk.Entry(tab3_frame, style='Background_grey.TEntry')
tab3_entry8.place(x=180.0, y= pm_tab3.y_interelement_spacing_ret(number_of_element = 8), width=95.0, height=20.0)


canvas3.create_text(pm_tab3.x_offset, pm_tab3.y_interelement_spacing_ret(number_of_element = 9), anchor="nw",
    text="Sg2Dac", fill="#000000", font=("Inter SemiBold", 12 * -1))
tab3_entry9 = ttk.Entry(tab3_frame, style='Background_grey.TEntry')
tab3_entry9.place(x=180.0, y= pm_tab3.y_interelement_spacing_ret(number_of_element = 9), width=95.0, height=20.0)


sg_output_variables = ["TestFw_DoPwrSg", "TestFw_Sg1PlusOpamp", "TestFw_Sg1MinusOpamp", "TestFw_Sg1Opamp", "TestFw_Sg1Dac", "TestFw_Sg2PlusOpamp", "TestFw_Sg2MinusOpamp", "TestFw_Sg2Opamp", "TestFw_Sg2Dac"]
sg_entries = [tab3_entry_1, tab3_entry2, tab3_entry3, tab3_entry4,tab3_entry5, tab3_entry6,tab3_entry7, tab3_entry8, tab3_entry9]

images["tab3_tile3_run_test"] = PhotoImage(file=relative_to_assets("tab_testrun_button.png", "tab3"))
tab3_run_test_tile3 = Button(tab3, image=images["tab3_tile3_run_test"], command=lambda: SendDIDGetVal_multiple_entry(sg_output_variables, sg_entries, TestFunctionCmd.TEST_GUI_CMD_SG_TEST_e, True, running_status), bd = 0)
tab3_run_test_tile3.place(x=450, y=110, width=31.073986053466797, height=31.845783233642578)

reset_entries = ttk.Button(tab3, text="Reset Results", command=lambda: clear_entries(sg_entries)) #browse button to get repo path
reset_entries.place(x=500, y=110, width=85, height=32)

running_status = tk.Label(tab3_frame, text="Running Status: None")
running_status.config(bg = "#DFDFDF")
running_status.place(x = 20, y = 610)

# ===================================================================================================================
# ========== Footerbar ==============================================================================================



# ===================================================================================================================
# ========== Toolbar ================================================================================================

ToolBar(tab3, tab3_frame, canvas3 , images, relative_to_assets)

# ===================================================================================================================
# ===================================================================================================================
# ========== TAB 4 (Motor) ==========================================================================================

pm_tab4 = PlacementManager()
pm_tab4.x_offset = 73
pm_tab4.y_offset = 150
pm_tab4.x_interelement_spacing = 277
pm_tab4.y_interelement_spacing = 40


# ===================================================================================================================
# ========== Page Constructors ======================================================================================

tab4 = ttk.Frame(notebook)
notebook.add(tab4, text="Motor")

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
# ========== Tile-2 =================================================================================================


selected_motor_state = tk.IntVar(value=0)

motor_couple_cb = tk.Checkbutton(
    tab4,
    text="Motor Couple",
    variable=selected_motor_state,
    onvalue=1,
    offvalue=0,
    command=lambda: motor_couple(selected_motor_state)
)
motor_couple_cb.place(x=73.0 + 475.0, y=150)



motor_decouple_cb = tk.Checkbutton(
    tab4,
    text="Motor Decouple",
    variable=selected_motor_state,
    onvalue=2,
    offvalue=0,
    command=lambda: motor_decouple(selected_motor_state)
)
motor_decouple_cb.place(x=73.0 + 475.0 + 120, y=150)

canvas4.create_text(pm_tab4.x_offset, pm_tab4.y_interelement_spacing_ret(number_of_element = 1), anchor="nw", text="Motor Test Results (DID 102)", fill="#000000", font=("Inter SemiBold", 20 * -1))

canvas4.create_text(pm_tab4.x_offset, pm_tab4.y_interelement_spacing_ret(number_of_element = 2), anchor="nw", text="MotorCoupledVoltage", fill="#000000", font=("Inter SemiBold", 15 * -1))
tab4_entry3 = ttk.Entry(tab4_frame, style = 'Background_grey.TEntry')
tab4_entry3.place(x=pm_tab4.x_offset + pm_tab4.x_interelement_spacing, y=pm_tab4.y_interelement_spacing_ret(number_of_element = 2), width=95.0, height=20.0)

canvas4.create_text(pm_tab4.x_offset, pm_tab4.y_interelement_spacing_ret(number_of_element = 3), anchor="nw", text="MotorDecoupledVoltage", fill="#000000", font=("Inter SemiBold", 15 * -1))
tab4_entry4 = ttk.Entry(tab4_frame, style = 'Background_grey.TEntry')
tab4_entry4.place(x=pm_tab4.x_offset + pm_tab4.x_interelement_spacing, y=pm_tab4.y_interelement_spacing_ret(number_of_element = 3), width=95.0, height=20.0)

canvas4.create_text(pm_tab4.x_offset, pm_tab4.y_interelement_spacing_ret(number_of_element = 4), anchor="nw", text="MotorCurrentValue", fill="#000000", font=("Inter SemiBold", 15 * -1))
tab4_entry7 = ttk.Entry(tab4_frame, style = 'Background_grey.TEntry')
tab4_entry7.place(x=pm_tab4.x_offset + pm_tab4.x_interelement_spacing, y=pm_tab4.y_interelement_spacing_ret(number_of_element = 4), width=95.0, height=20.0)

canvas4.create_text(pm_tab4.x_offset, pm_tab4.y_interelement_spacing_ret(number_of_element = 5), anchor="nw", text="MotorPwmOut", fill="#000000", font=("Inter SemiBold", 15 * -1))
tab4_entry8 = ttk.Entry(tab4_frame, style = 'Background_grey.TEntry')
tab4_entry8.place(x=pm_tab4.x_offset + pm_tab4.x_interelement_spacing, y=pm_tab4.y_interelement_spacing_ret(number_of_element = 5), width=95.0, height=20.0)

canvas4.create_text(pm_tab4.x_offset, pm_tab4.y_interelement_spacing_ret(number_of_element = 6), anchor="nw", text="PwmMotorDriverIn1", fill="#000000", font=("Inter SemiBold", 15 * -1))
tab4_entry9 = ttk.Entry(tab4_frame, style = 'Background_grey.TEntry')
tab4_entry9.place(x=pm_tab4.x_offset + pm_tab4.x_interelement_spacing, y=pm_tab4.y_interelement_spacing_ret(number_of_element = 6), width=95.0, height=20.0)

canvas4.create_text(pm_tab4.x_offset, pm_tab4.y_interelement_spacing_ret(number_of_element = 7), anchor="nw", text="PwmMotorDriverIn2", fill="#000000", font=("Inter SemiBold", 15 * -1))
tab4_entry10 = ttk.Entry(tab4_frame, style = 'Background_grey.TEntry')
tab4_entry10.place(x=pm_tab4.x_offset + pm_tab4.x_interelement_spacing, y=pm_tab4.y_interelement_spacing_ret(number_of_element = 7), width=95.0, height=20.0)

canvas4.create_text(pm_tab4.x_offset, pm_tab4.y_interelement_spacing_ret(number_of_element = 8), anchor="nw", text="DoMotorNsleep", fill="#000000", font=("Inter SemiBold", 15 * -1))
tab4_entry11 = ttk.Entry(tab4_frame, style = 'Background_grey.TEntry')
tab4_entry11.place(x=pm_tab4.x_offset + pm_tab4.x_interelement_spacing, y=pm_tab4.y_interelement_spacing_ret(number_of_element = 8), width=95.0, height=20.0)

canvas4.create_text(pm_tab4.x_offset, pm_tab4.y_interelement_spacing_ret(number_of_element = 9), anchor="nw", text="DoMotorDiagEnable", fill="#000000", font=("Inter SemiBold", 15 * -1))
tab4_entry12 = ttk.Entry(tab4_frame, style = 'Background_grey.TEntry')
tab4_entry12.place(x=pm_tab4.x_offset + pm_tab4.x_interelement_spacing, y=pm_tab4.y_interelement_spacing_ret(number_of_element = 9), width=95.0, height=20.0)

canvas4.create_text(pm_tab4.x_offset, pm_tab4.y_interelement_spacing_ret(number_of_element = 10), anchor="nw", text="DiMotorNfault", fill="#000000", font=("Inter SemiBold", 15 * -1))
tab4_entry13 = ttk.Entry(tab4_frame, style = 'Background_grey.TEntry')
tab4_entry13.place(x=pm_tab4.x_offset + pm_tab4.x_interelement_spacing, y=pm_tab4.y_interelement_spacing_ret(number_of_element = 10), width=95.0, height=20.0)

canvas4.create_text(pm_tab4.x_offset, pm_tab4.y_interelement_spacing_ret(number_of_element = 11), anchor="nw", text="MotorLoadError", fill="#000000", font=("Inter SemiBold", 15 * -1))
tab4_entry14 = ttk.Entry(tab4_frame, style = 'Background_grey.TEntry')
tab4_entry14.place(x=pm_tab4.x_offset + pm_tab4.x_interelement_spacing, y=pm_tab4.y_interelement_spacing_ret(number_of_element = 11), width=95.0, height=20.0)

motor_output_variables = ["TestFw_MotorCoupledVoltage", "TestFw_MotorDecoupledVoltage", "TestFw_MotorCurrentValue", "TestFw_MotorPwmOut", "TestFw_PwmMotorDriverIn1", "TestFw_PwmMotorDriverIn2", "TestFw_DoMotorNsleep", "TestFw_DoMotorDiagEnable", "TestFw_DiMotorNfault", "TestFw_MotorLoadError"]
motor_entries = [tab4_entry3, tab4_entry4, tab4_entry7, tab4_entry8, tab4_entry9, tab4_entry10, tab4_entry11 , tab4_entry12, tab4_entry13, tab4_entry14]

images["tab4_tile4_run_test"] = PhotoImage(file=relative_to_assets("tab_testrun_button.png", "tab4"))
tab4_run_test_tile4 = Button(tab4, image=images["tab4_tile4_run_test"], command=lambda: SendDIDGetVal_multiple_entry(motor_output_variables, motor_entries, TestFunctionCmd.TESTFW_GUI_CMD_MOTOR_TEST_e), bd = 0)
tab4_run_test_tile4.place(x=pm_tab4.x_offset + pm_tab4.x_interelement_spacing, y=pm_tab4.y_interelement_spacing_ret(number_of_element = 1), width=31.073986053466797, height=31.073986053466797)





# ===================================================================================================================
# ========== Footerbar ==============================================================================================



# ===================================================================================================================
# ========== Toolbar ================================================================================================

ToolBar(tab4, tab4_frame, canvas4 , images, relative_to_assets)

# ===================================================================================================================
# ===================================================================================================================
# ========== TAB 4A (V-BATT) =========================================================================================

pm_tab5 = PlacementManager()
pm_tab5.x_offset = 73
pm_tab5.y_offset = 150
pm_tab5.x_interelement_spacing = 277
pm_tab5.y_interelement_spacing = 40


# ===================================================================================================================
# ========== Page Constructors ======================================================================================

tab4a = ttk.Frame(notebook)
notebook.add(tab4a, text="V-BATT")

tab4a_frame = tk.Frame(tab4a, bg="#DFDFDF")
tab4a_frame.pack(fill="both", expand=True)

canvas4a = tk.Canvas(
    tab4a_frame,
    bg="#DFDFDF",
    height=651,
    width=973,
    bd=0,
    highlightthickness=0,
    relief="ridge"
)
canvas4a.place(x=0, y=0)

# ===================================================================================================================
# ========== Tile-1 =================================================================================================


canvas4a.create_text(73.0, pm_tab5.y_interelement_spacing_ret(number_of_element = 1), anchor="nw", text="VBatt Test", fill="#000000", font=("Inter SemiBold", 20 * -1))
canvas4a.create_text(73.0, pm_tab5.y_interelement_spacing_ret(number_of_element = 2), anchor="nw", text="TestFw_BatRefStatus", fill="#000000", font=("Inter SemiBold", 15 * -1))
canvas4a.create_text(73.0, pm_tab5.y_interelement_spacing_ret(number_of_element = 3), anchor="nw", text="TestFw_AiBatRef", fill="#000000", font=("Inter SemiBold", 15 * -1))

tab4a_entry_1 = ttk.Entry(tab4a_frame, style ='Background_grey.TEntry')
tab4a_entry_1.place(x=306.0, y=pm_tab5.y_interelement_spacing_ret(number_of_element = 2), width=95.0, height=20.0)

tab4a_entry_2 = ttk.Entry(tab4a_frame, style ='Background_grey.TEntry')
tab4a_entry_2.place(x=306.0, y=pm_tab5.y_interelement_spacing_ret(number_of_element = 3), width=95.0, height=20.0)

Vbatt_output_variables = ["TestFw_BatRefStatus", "TestFw_AiBatRef"]
Vbatt_entries = [tab4a_entry_1, tab4a_entry_2]

images["tab4a_tile1_run_test"] = PhotoImage(file=relative_to_assets("tab_testrun_button.png", "tab4a"))
tab4a_run_test_tile1 = Button(tab4a, image=images["tab4a_tile1_run_test"], command=lambda: SendDIDGetVal_multiple_entry(Vbatt_output_variables, Vbatt_entries, TestFunctionCmd.TESTFW_GUI_CMD_BATT_MONITOR_e), bd = 0)
tab4a_run_test_tile1.place(x=368, y=pm_tab5.y_interelement_spacing_ret(number_of_element = 1), width=31.073986053466797, height=31.073986053466797)



# ===================================================================================================================
# ========== Footerbar ==============================================================================================



# ===================================================================================================================
# ========== Toolbar ================================================================================================


ToolBar(tab4a, tab4a_frame, canvas4a , images, relative_to_assets)

# ===================================================================================================================
# ===================================================================================================================
# ========== TAB 4B (EOS) ===========================================================================================

pm_tab6 = PlacementManager()
pm_tab6.x_offset = 73
pm_tab6.y_offset = 150
pm_tab6.x_interelement_spacing = 277
pm_tab6.y_interelement_spacing = 40


# ===================================================================================================================
# ========== Page Constructors ======================================================================================


tab4b = ttk.Frame(notebook)
notebook.add(tab4b, text="EOS")

tab4b_frame = tk.Frame(tab4b, bg="#DFDFDF")
tab4b_frame.pack(fill="both", expand=True)

canvas4b = tk.Canvas(
    tab4b_frame,
    bg="#DFDFDF",
    height=651,
    width=973,
    bd=0,
    highlightthickness=0,
    relief="ridge"
)
canvas4b.place(x=0, y=0)

# ===================================================================================================================
# ========== Tile-3 =================================================================================================


canvas4b.create_text(73.0, pm_tab6.y_interelement_spacing_ret(number_of_element = 1), anchor="nw", text="EOS Test (DID 105)", fill="#000000", font=("Inter SemiBold", 20 * -1))
canvas4b.create_text(73.0, pm_tab6.y_interelement_spacing_ret(number_of_element = 2), anchor="nw", text="EosPinState", fill="#000000", font=("Inter SemiBold", 15 * -1))
canvas4b.create_text(73.0, pm_tab6.y_interelement_spacing_ret(number_of_element = 3), anchor="nw", text="EosErrorsWithLow", fill="#000000", font=("Inter SemiBold", 15 * -1))
canvas4b.create_text(73.0, pm_tab6.y_interelement_spacing_ret(number_of_element = 4), anchor="nw", text="EosErrorsWithHigh", fill="#000000", font=("Inter SemiBold", 15 * -1))


tab4b_entry5 = ttk.Entry(tab4b_frame, style = 'Background_grey.TEntry')
tab4b_entry5.place(x=306.0, y=pm_tab6.y_interelement_spacing_ret(number_of_element = 2), width=95.0, height=20.0)

tab4b_entry6 = ttk.Entry(tab4b_frame, style = 'Background_grey.TEntry')
tab4b_entry6.place(x=306.0, y=pm_tab6.y_interelement_spacing_ret(number_of_element = 3), width=95.0, height=20.0)

tab4b_entry7 = ttk.Entry(tab4b_frame, style = 'Background_grey.TEntry')
tab4b_entry7.place(x=306.0, y=pm_tab6.y_interelement_spacing_ret(number_of_element = 4), width=95.0, height=20.0)

Vbatt_output_variables = ["TestFw_EosPinState", "TestFw_EosErrorsWithLow", "TestFw_EosErrorsWithHigh"]
Vbatt_entries = [tab4b_entry5,tab4b_entry6, tab4b_entry7]

images["tab4b_tile3_run_test"] = PhotoImage(file=relative_to_assets("tab_testrun_button.png", "tab4b"))
tab4b_run_test_tile3 = Button(tab4b, image=images["tab4b_tile3_run_test"], command=lambda: SendDIDGetVal_multiple_entry(Vbatt_output_variables, Vbatt_entries, TestFunctionCmd.TESTFW_GUI_CMD_EOS_TEST_e,"TestFw_EosDiagVoltage"), bd = 0)
tab4b_run_test_tile3.place(x=368, y=pm_tab6.y_interelement_spacing_ret(number_of_element = 1), width=31.073986053466797, height=31.073986053466797)


# ===================================================================================================================
# ========== Footerbar ==============================================================================================



# ===================================================================================================================
# ========== Toolbar ================================================================================================

ToolBar(tab4b, tab4b_frame, canvas4b , images, relative_to_assets)

# ===================================================================================================================
# ===================================================================================================================
# ========== TAB 5 (NFC Test) =======================================================================================

pm_tab7 = PlacementManager()
pm_tab7.x_offset = 73
pm_tab7.y_offset = 150
pm_tab7.x_interelement_spacing = 277
pm_tab7.y_interelement_spacing = 40


# ===================================================================================================================
# ========== Page Constructors ======================================================================================


tab5 = ttk.Frame(notebook)
notebook.add(tab5, text="NFC")

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


canvas5.create_text(73.0, pm_tab6.y_interelement_spacing_ret(number_of_element = 1), anchor="nw", text="NFC Test Result", fill="#000000", font=("Inter SemiBold", 20 * -1))

canvas5.create_text(73.0, pm_tab6.y_interelement_spacing_ret(number_of_element = 2), anchor="nw", text="TestFw_IsNfcDetectedCard", fill="#000000", font=("Inter SemiBold", 15 * -1))
tab5_entry_1 = ttk.Entry(tab5_frame, style ='Background_grey.TEntry')
tab5_entry_1.place(x=306.0, y=pm_tab6.y_interelement_spacing_ret(number_of_element = 2), width=95.0, height=20.0)



images["tab5_tile1_run_test"] = PhotoImage(file=relative_to_assets("tab_testrun_button.png", "tab5"))
tab5_run_test_tile1 = Button(tab5, image=images["tab5_tile1_run_test"], command=lambda: SendDIDGetVal(tab5_entry_1, TestFunctionCmd.TEST_GUI_CMD_NFC_TEST_e,"TestFw_IsNfcDetectedCard"), bd = 0)
tab5_run_test_tile1.place(x=368, y=pm_tab6.y_interelement_spacing_ret(number_of_element = 1), width=31.073986053466797, height=31.073986053466797)




# ===================================================================================================================
# ========== Footerbar ==============================================================================================




# ===================================================================================================================
# ========== Toolbar ================================================================================================

ToolBar(tab5, tab5_frame, canvas5 , images, relative_to_assets)

# ===================================================================================================================
# ===================================================================================================================
# ========== TAB 6 (CAN LIN) ========================================================================================


pm_tab8 = PlacementManager()
pm_tab8.x_offset = 73
pm_tab8.y_offset = 150
pm_tab8.x_interelement_spacing = 277
pm_tab8.y_interelement_spacing = 40


# ===================================================================================================================
# ========== Page Constructors ======================================================================================



tab6 = ttk.Frame(notebook)
notebook.add(tab6, text="CAN/LIN")

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

# ===================================================================================================================
# ========== Tile-1 =================================================================================================


canvas6.create_text(61.0, pm_tab8.y_interelement_spacing_ret(number_of_element = 1), anchor="nw", text="CAN Test", fill="#000000", font=("Inter SemiBold", 20 * -1))


canvas6.create_text(61.0, pm_tab8.y_interelement_spacing_ret(number_of_element = 2), anchor="nw", text="Transmit CAN Message ID", fill="#000000", font=("Inter SemiBold", 15 * -1))
tab6_entry_1 = ttk.Entry(tab6_frame, style ='Background_grey.TEntry')
tab6_entry_1.place(x=61 + pm_tab8.x_interelement_spacing, y=pm_tab8.y_interelement_spacing_ret(number_of_element = 2), width=150.0, height=20.0)

canvas6.create_text(61.0, pm_tab8.y_interelement_spacing_ret(number_of_element = 3), anchor="nw", text="Receive CAN Message ID", fill="#000000", font=("Inter SemiBold", 15 * -1))
tab6_entry_2 = ttk.Entry(tab6_frame, style ='Background_grey.TEntry')
tab6_entry_2.place(x=61 + pm_tab8.x_interelement_spacing, y=pm_tab8.y_interelement_spacing_ret(number_of_element = 3), width=150.0, height=20.0)


canvas6.create_text(61, pm_tab8.y_interelement_spacing_ret(number_of_element = 4), anchor="nw", text="Transmit LIN Message ID", fill="#000000", font=("Inter SemiBold", 15 * -1))
tab6_entry4 = ttk.Entry(tab6_frame, style = 'Background_grey.TEntry')
tab6_entry4.place(x=61 + pm_tab8.x_interelement_spacing, y=pm_tab8.y_interelement_spacing_ret(number_of_element = 4), width=150.0, height=20.0)

canvas6.create_text(61, pm_tab8.y_interelement_spacing_ret(number_of_element = 5), anchor="nw", text="Receive LIN Message ID", fill="#000000", font=("Inter SemiBold", 15 * -1))
tab6_entry5 = ttk.Entry(tab6_frame, style = 'Background_grey.TEntry')
tab6_entry5.place(x=61 + pm_tab8.x_interelement_spacing, y=pm_tab8.y_interelement_spacing_ret(number_of_element = 5), width=150.0, height=20.0)




images["tab6_tile2_run_test"] = PhotoImage(file=relative_to_assets("tab_testrun_button.png", "tab6"))
tab6_run_test_tile2 = Button(tab6, image=images["tab6_tile2_run_test"], command=lambda: print("tile two capa run test ..."), bd = 0)
tab6_run_test_tile2.place(x=368 , y=pm_tab8.y_interelement_spacing_ret(number_of_element = 1), width=31.073986053466797, height=31.073986053466797)


# ===================================================================================================================
# ========== Footerbar ==============================================================================================




# ===================================================================================================================
# ========== Toolbar ================================================================================================

ToolBar(tab6, tab6_frame, canvas6 , images, relative_to_assets)

# ===================================================================================================================
# ========== TAB 7 ==================================================================================================

pm_tab9 = PlacementManager()
pm_tab9.x_offset = 73
pm_tab9.y_offset = 150
pm_tab9.x_interelement_spacing = 277
pm_tab9.y_interelement_spacing = 40




tab7 = ttk.Frame(notebook)
notebook.add(tab7, text="LED Test")

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


canvas7.create_text(73.0, pm_tab9.y_interelement_spacing_ret(number_of_element = 1), anchor="nw", text="LED Test (DID 101)", fill="#000000", font=("Inter SemiBold", 20 * -1))


canvas7.create_text(73.0, pm_tab9.y_interelement_spacing_ret(number_of_element = 2), anchor="nw", text="LedVoltage:", fill="#000000", font=("Inter SemiBold", 15 * -1))
tab7_entry_1 = ttk.Entry(tab7_frame, style ='Background_grey.TEntry')
tab7_entry_1.place(x=306.0, y=pm_tab9.y_interelement_spacing_ret(number_of_element = 2), width=95.0, height=20.0)


images["tile1_run_test_tab7"] = PhotoImage(file=relative_to_assets("tab_testrun_button.png", "tab7"))
run_test_tile1 = Button(tab7, image=images["tile1_run_test_tab7"], command=lambda: SendDIDGetVal(tab7_entry_1, TestFunctionCmd.TESTFW_GUI_CMD_LED_TEST_e, "TestFw_LedVoltage"), bd = 0)
run_test_tile1.place(x=368, y=pm_tab9.y_interelement_spacing_ret(number_of_element = 1), width=31.073986053466797, height=31.073986053466797)



# ===================================================================================================================
# ========== Footerbar ==============================================================================================



# ===================================================================================================================
# ========== Toolbar ================================================================================================

ToolBar(tab7, tab7_frame, canvas7 , images, relative_to_assets)



#GUI End
# window.after(1000, lambda: poll_target_state(running_status, window))

# ==================================================================================================================
# ========== EXIT ==================================================================================================


window.resizable(True, True)
window.mainloop()
