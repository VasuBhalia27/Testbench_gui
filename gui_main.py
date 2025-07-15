from pathlib import Path
import tkinter as tk
from tkinter import ttk, Button, PhotoImage
import ctypes

# ===================================================================================================================
# ========== Initializations ========================================================================================

try:
    ctypes.windll.shcore.SetProcessDpiAwareness(1)
except Exception:
    ctypes.windll.user32.SetProcessDPIAware()


# Define global image reference dictionary to prevent garbage collection
images = {}

# Base Paths
OUTPUT_PATH = Path(__file__).parent
ASSETS_PATH_TAB1 = OUTPUT_PATH / Path(r"Elements\Page_1(Welcome_page)\assets\frame0")
ASSETS_PATH_TAB2 = OUTPUT_PATH / Path(r"Elements\Page_2(Capa)\assets\frame0")



def relative_to_assets(path: str, tab: str) -> Path:
    if tab == "tab1":
        return ASSETS_PATH_TAB1 / Path(path)
    elif tab == "tab2" or "tab3":
        return ASSETS_PATH_TAB2 / Path(path)

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
    foreground='#FFFFFF',
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

canvas1.create_text(78.0, 168.0, anchor="nw", text="Welcome to the Test Bench",
                   fill="#0066B3", font=("Inter", -32))

images["minibea_logo"] = PhotoImage(file=relative_to_assets("image_3.png", "tab1"))
canvas1.create_image(281.0, 77.0, image=images["minibea_logo"])

images["version_tile"] = PhotoImage(file=relative_to_assets("image_1.png", "tab1"))
canvas1.create_image(283.0, 417.0, image=images["version_tile"])

canvas1.create_text(199.0, 271.0, anchor="nw", text="Select Version",
                   fill="#FFFFFF", font=("Inter", -24))

images["photo_with_hand"] = PhotoImage(file=relative_to_assets("image_2.png", "tab1"))
canvas1.create_image(797.0, 325.0, image=images["photo_with_hand"])

# Buttons in Tab 1
images["version1"] = PhotoImage(file=relative_to_assets("button_1.png", "tab1"))
btn1_tab1 = Button(tab1, image=images["version1"], command=lambda: print("version1"), bd=0)
btn1_tab1.place(x=176, y=320, width=213, height=37)

images["version2"] = PhotoImage(file=relative_to_assets("button_2.png", "tab1"))
btn2_tab2 = Button(tab1, image=images["version2"], command=lambda: print("version2"), bd=0)
btn2_tab2.place(x=176, y=380, width=213, height=37)

images["version3"] = PhotoImage(file=relative_to_assets("button_3.png", "tab1"))
btn3_tab3 = Button(tab1, image=images["version3"], command=lambda: print("version3"), bd=0)
btn3_tab3.place(x=176, y=440, width=213, height=37)

images["version4"] = PhotoImage(file=relative_to_assets("button_4.png", "tab1"))
btn4_tab4 = Button(tab1, image=images["version4"], command=lambda: print("version4"), bd=0)
btn4_tab4.place(x=176, y=500, width=213, height=37)


# ===================================================================================================================
# ========== TAB 2 ==================================================================================================



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

images["tile_tab2"] = PhotoImage(file=relative_to_assets("Tile.png", "tab2")) 
canvas2.create_image(tablet1_X, tablet1_Y, image=images["tile_tab2"])

canvas2.create_text(73.0, 113.0, anchor="nw", text="Unlock Capacitor", fill="#FFFFFF", font=("Inter SemiBold", 20 * -1))
canvas2.create_text(73.0, 168.0, anchor="nw", text="Unlock 100pF Capacitor", fill="#FFFFFF", font=("Inter SemiBold", 15 * -1))
canvas2.create_text(73.0, 214.0, anchor="nw", text="Lock 100pF Capacitor", fill="#FFFFFF", font=("Inter SemiBold", 15 * -1))

tab2_entry_1 = ttk.Entry(tab2_frame, style ='Background_grey.TEntry')
tab2_entry_1.place(x=306.0, y=168.0, width=95.0, height=20.0)


tab2_entry_2 = ttk.Entry(tab2_frame, style = 'Background_grey.TEntry')
tab2_entry_2.place(x=306.0, y=214.0, width=95.0, height=20.0)

images["tile1_run_test"] = PhotoImage(file=relative_to_assets("tab_testrun_button.png", "tab2"))
run_test_tile1 = Button(tab2, image=images["tile1_run_test"], command=lambda: print("tile one capa run test ..."), bd = 0)
run_test_tile1.place(x=368, y=106, width=34, height=34)

# ===================================================================================================================
# ========== Tile-2 =================================================================================================

images["tile2_tab2"] = PhotoImage(file=relative_to_assets("Tile.png", "tab2")) 
canvas2.create_image((tablet1_X + 475), (tablet1_Y + 0), image=images["tile2_tab2"])

canvas2.create_text(560.0, 113.0, anchor="nw", text="Proximity Capacitor", fill="#FFFFFF", font=("Inter SemiBold", 20 * -1))
canvas2.create_text(560.0, 168.0, anchor="nw", text="Unlock 100pF Capacitor", fill="#FFFFFF", font=("Inter SemiBold", 15 * -1))
canvas2.create_text(560.0, 214.0, anchor="nw", text="Lock 100pF Capacitor", fill="#FFFFFF", font=("Inter SemiBold", 15 * -1))


tab2_entry3 = ttk.Entry(tab2_frame, style = 'Background_grey.TEntry')
tab2_entry3.place(x=780.0, y=168.0, width=95.0, height=20.0)


tab2_entry4 = ttk.Entry(tab2_frame, style = 'Background_grey.TEntry')
tab2_entry4.place(x=780.0, y=214.0, width=95.0, height=20.0)

images["tile2_run_test"] = PhotoImage(file=relative_to_assets("tab_testrun_button.png", "tab2"))
run_test_tile2 = Button(tab2, image=images["tile2_run_test"], command=lambda: print("tile two capa run test ..."), bd = 0)
run_test_tile2.place(x=840 , y=106, width=34, height=34)

# ===================================================================================================================
# ========== Tile-3 =================================================================================================

images["tile3_tab2"] = PhotoImage(file=relative_to_assets("Tile.png", "tab2")) 
canvas2.create_image((tablet1_X + 0), (tablet1_Y + 235), image=images["tile3_tab2"])

canvas2.create_text(73.0, 348.0, anchor="nw", text="Lock Capacitor", fill="#FFFFFF", font=("Inter SemiBold", 20 * -1))
canvas2.create_text(73.0, 403.0, anchor="nw", text="Unlock 100pF Capacitor", fill="#FFFFFF", font=("Inter SemiBold", 15 * -1))
canvas2.create_text(73.0, 449.0, anchor="nw", text="Lock 100pF Capacitor", fill="#FFFFFF", font=("Inter SemiBold", 15 * -1))


tab2_entry5 = ttk.Entry(tab2_frame, style = 'Background_grey.TEntry')
tab2_entry5.place(x=306.0, y=403.0, width=95.0, height=20.0)


tab2_entry6 = ttk.Entry(tab2_frame, style = 'Background_grey.TEntry')
tab2_entry6.place(x=306.0, y=449.0, width=95.0, height=20.0)

images["tile3_run_test"] = PhotoImage(file=relative_to_assets("tab_testrun_button.png", "tab2"))
run_test_tile3 = Button(tab2, image=images["tile3_run_test"], command=lambda: print("tile three capa run test ..."), bd = 0)
run_test_tile3.place(x=368, y=341, width=34, height=34)

# ===================================================================================================================
# ========== Footerbar ==============================================================================================

images["tab2_footerbar"] = PhotoImage(file=relative_to_assets("footer_bar.png", "tab2")) #Footer bar
canvas2.create_image(500, 606, image=images["tab2_footerbar"])

canvas2.create_text(
    22.0,
    580.0,
    anchor="nw",
    text="Set power supply voltage",
    fill="#282828",
    font=("Inter Bold", 16 * -1)
)

tab2_entry7 = ttk.Entry(tab2_frame, style = 'Background_grey.TEntry')
tab2_entry7.place(x=306.0, y=580.0, width=95.0, height=20.0)

images["set_voltage_button"] = PhotoImage(file=relative_to_assets("set_or_get_voltage.png", "tab2"))
tab2_setvoltage = Button(tab2, image=images["set_voltage_button"], command=lambda: print("setvoltage..."), bd = 0)
tab2_setvoltage.place(x=413, y=576, width=25, height=26)

canvas2.create_text(
    22.0,
    613.0,
    anchor="nw",
    text="Get power supply voltage",
    fill="#282828",
    font=("Inter SemiBold", 16 * -1)
)

tab2_entry8 = ttk.Entry(tab2_frame, style = 'Background_grey.TEntry')
tab2_entry8.place(x=306.0, y=613.0, width=95.0, height=20.0)

images["get_voltage_button"] = PhotoImage(file=relative_to_assets("set_or_get_voltage.png", "tab2"))
tab2_getvoltage = Button(tab2, image=images["get_voltage_button"], command=lambda: print("getvoltage..."), bd = 0)
tab2_getvoltage.place(x=413, y=610, width=25, height=26)

# ===================================================================================================================
# ========== Toolbar ================================================================================================

images["tab2_toptoolbar"] = PhotoImage(file=relative_to_assets("top_toolbar.png", "tab2")) #tool bar
canvas2.create_image(179, 19, image=images["tab2_toptoolbar"])

images["toolbar_playbutton1"] = PhotoImage(file=relative_to_assets("set_or_get_voltage.png", "tab2"))
toolbar_playbutton = Button(tab2, image=images["toolbar_playbutton1"], command=lambda: print("Run code ..."), bd = 0)
toolbar_playbutton.place(x=182, y=5, width=26, height=26)

canvas2.create_text(
    168.0,
    28.0,
    anchor="nw",
    text=" Run code",
    fill="#6E6E6E",
    font=("Inter SemiBold", 11 * -1)
)



images["toolbar_pausebutton1"] = PhotoImage(file=relative_to_assets("toolbar_pausebutton.png", "tab2"))
toolbar_pausebutton1 = Button(tab2, image=images["toolbar_pausebutton1"], command=lambda: print("pause code ... "), bd = 0)
toolbar_pausebutton1.place(x=100, y=5, width=22.99, height=22.99)

canvas2.create_text(
    80.0,
    28.0,
    anchor="nw",
    text="Pause code",
    fill="#6E6E6E",
    font=("Inter SemiBold", 11 * -1)
)


images["toolbar_exitbutton1"] = PhotoImage(file=relative_to_assets("toolbar_exitbutton.png", "tab2"))
toolbar_exitbutton1 = Button(tab2, image=images["toolbar_exitbutton1"], command=lambda: print("Exit ... "), bd = 0)
toolbar_exitbutton1.place(x=261, y=8, width=15, height=15)

canvas2.create_text(
    260.0,
    28.0,
    anchor="nw",
    text="Exit",
    fill="#FF0202",
    font=("Inter SemiBold", 11 * -1)
)



# ===================================================================================================================
# ===================================================================================================================
# ========== TAB 3 (SG tests) =======================================================================================



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

# ===================================================================================================================
# ========== Tile-1 =================================================================================================

images["tile_tab3"] = PhotoImage(file=relative_to_assets("Tile.png", "tab3")) 
canvas3.create_image(tablet1_X, tablet1_Y, image=images["tile_tab3"])

canvas3.create_text(73.0, 113.0, anchor="nw", text="DO_DAC_SG0 Test", fill="#FFFFFF", font=("Inter SemiBold", 20 * -1))
canvas3.create_text(73.0, 168.0, anchor="nw", text="Set Op Amp (1200ohm)", fill="#FFFFFF", font=("Inter SemiBold", 15 * -1))


tab3_entry_1 = ttk.Entry(tab3_frame, style ='Background_grey.TEntry')
tab3_entry_1.place(x=306.0, y=168.0, width=95.0, height=20.0)

images["tab3_tile1_run_test"] = PhotoImage(file=relative_to_assets("tab_testrun_button.png", "tab3"))
tab3_run_test_tile1 = Button(tab3, image=images["tab3_tile1_run_test"], command=lambda: print("tile one capa run test ..."), bd = 0)
tab3_run_test_tile1.place(x=368, y=106, width=34, height=34)

# ===================================================================================================================
# ========== Tile-2 =================================================================================================

images["tile2_tab3"] = PhotoImage(file=relative_to_assets("Tile.png", "tab3")) 
canvas3.create_image((tablet1_X + 475), (tablet1_Y + 0), image=images["tile2_tab3"])

canvas3.create_text(560.0, 113.0, anchor="nw", text="DO_DAC1_SG1 Test", fill="#FFFFFF", font=("Inter SemiBold", 20 * -1))
canvas3.create_text(560.0, 168.0, anchor="nw", text="Set Op Amp (1200ohm)", fill="#FFFFFF", font=("Inter SemiBold", 15 * -1))



tab3_entry3 = ttk.Entry(tab3_frame, style = 'Background_grey.TEntry')
tab3_entry3.place(x=780.0, y=168.0, width=95.0, height=20.0)


images["tab3_tile2_run_test"] = PhotoImage(file=relative_to_assets("tab_testrun_button.png", "tab3"))
tab3_run_test_tile2 = Button(tab3, image=images["tab3_tile2_run_test"], command=lambda: print("tile two capa run test ..."), bd = 0)
tab3_run_test_tile2.place(x=840 , y=106, width=34, height=34)

# ===================================================================================================================
# ========== Tile-3 =================================================================================================

images["tile3_tab3"] = PhotoImage(file=relative_to_assets("Tile.png", "tab3")) 
canvas3.create_image((tablet1_X + 0), (tablet1_Y + 235), image=images["tile3_tab3"])

canvas3.create_text(73.0, 348.0, anchor="nw", text="DO_DAC2_SG2 Test", fill="#FFFFFF", font=("Inter SemiBold", 20 * -1))
canvas3.create_text(73.0, 403.0, anchor="nw", text="Set Op Amp (1200ohm)", fill="#FFFFFF", font=("Inter SemiBold", 15 * -1))


tab3_entry5 = ttk.Entry(tab3_frame, style = 'Background_grey.TEntry')
tab3_entry5.place(x=306.0, y=403.0, width=95.0, height=20.0)


images["tab3_tile3_run_test"] = PhotoImage(file=relative_to_assets("tab_testrun_button.png", "tab3"))
tab3_run_test_tile3 = Button(tab3, image=images["tab3_tile3_run_test"], command=lambda: print("tile three capa run test ..."), bd = 0)
tab3_run_test_tile3.place(x=368, y=341, width=34, height=34)

# ===================================================================================================================
# ========== Tile-4 =================================================================================================

images["tile4_tab3"] = PhotoImage(file=relative_to_assets("Tile.png", "tab3")) 
canvas3.create_image((tablet1_X + 475), (tablet1_Y + 235), image=images["tile4_tab3"])

canvas3.create_text(73.0 + 475, 348.0, anchor="nw", text="DO_DAC3_SG3 Test", fill="#FFFFFF", font=("Inter SemiBold", 20 * -1))
canvas3.create_text(73.0 + 475, 403.0, anchor="nw", text="Set Op Amp (1200ohm)", fill="#FFFFFF", font=("Inter SemiBold", 15 * -1))


tab3_entry5 = ttk.Entry(tab3_frame, style = 'Background_grey.TEntry')
tab3_entry5.place(x=306+475, y=403.0, width=95.0, height=20.0)


images["tab3_tile4_run_test"] = PhotoImage(file=relative_to_assets("tab_testrun_button.png", "tab3"))
tab3_run_test_tile4 = Button(tab3, image=images["tab3_tile4_run_test"], command=lambda: print("tile four capa run test ..."), bd = 0)
tab3_run_test_tile4.place(x=368+475, y=341, width=34, height=34)


# ===================================================================================================================
# ========== Footerbar ==============================================================================================

images["tab3_footerbar"] = PhotoImage(file=relative_to_assets("footer_bar.png", "tab3")) #Footer bar
canvas3.create_image(500, 606, image=images["tab3_footerbar"])

canvas3.create_text(
    22.0,
    580.0,
    anchor="nw",
    text="Set power supply voltage",
    fill="#282828",
    font=("Inter Bold", 16 * -1)
)

tab3_entry7 = ttk.Entry(tab3_frame, style = 'Background_grey.TEntry')
tab3_entry7.place(x=306.0, y=580.0, width=95.0, height=20.0)

images["tab3_set_voltage_button"] = PhotoImage(file=relative_to_assets("set_or_get_voltage.png", "tab3"))
tab3_setvoltage = Button(tab3, image=images["tab3_set_voltage_button"], command=lambda: print("setvoltage..."), bd = 0)
tab3_setvoltage.place(x=413, y=576, width=25, height=26)

canvas3.create_text(
    22.0,
    613.0,
    anchor="nw",
    text="Get power supply voltage",
    fill="#282828",
    font=("Inter SemiBold", 16 * -1)
)

tab3_entry8 = ttk.Entry(tab3_frame, style = 'Background_grey.TEntry')
tab3_entry8.place(x=306.0, y=613.0, width=95.0, height=20.0)

images["tab3_get_voltage_button"] = PhotoImage(file=relative_to_assets("set_or_get_voltage.png", "tab3"))
tab3_getvoltage = Button(tab3, image=images["tab3_get_voltage_button"], command=lambda: print("getvoltage..."), bd = 0)
tab3_getvoltage.place(x=413, y=610, width=25, height=26)

# ===================================================================================================================
# ========== Toolbar ================================================================================================

images["tab3_toptoolbar"] = PhotoImage(file=relative_to_assets("top_toolbar.png", "tab3")) #tool bar
canvas3.create_image(179, 19, image=images["tab3_toptoolbar"])

images["tab3_toolbar_playbutton1"] = PhotoImage(file=relative_to_assets("set_or_get_voltage.png", "tab3"))
tab3_toolbar_playbutton1 = Button(tab3, image=images["tab3_toolbar_playbutton1"], command=lambda: print("Run code ..."), bd = 0)
tab3_toolbar_playbutton1.place(x=182, y=5, width=26, height=26)

canvas3.create_text(
    168.0,
    28.0,
    anchor="nw",
    text=" Run code",
    fill="#6E6E6E",
    font=("Inter SemiBold", 11 * -1)
)



images["tab3_toolbar_pausebutton1"] = PhotoImage(file=relative_to_assets("toolbar_pausebutton.png", "tab3"))
tab3_toolbar_pausebutton1 = Button(tab3, image=images["tab3_toolbar_pausebutton1"], command=lambda: print("pause code ... "), bd = 0)
tab3_toolbar_pausebutton1.place(x=100, y=5, width=22.99, height=22.99)

canvas3.create_text(
    80.0,
    28.0,
    anchor="nw",
    text="Pause code",
    fill="#6E6E6E",
    font=("Inter SemiBold", 11 * -1)
)


images["tab3_toolbar_exitbutton1"] = PhotoImage(file=relative_to_assets("toolbar_exitbutton.png", "tab3"))
tab3_toolbar_exitbutton1 = Button(tab3, image=images["toolbar_exitbutton1"], command=lambda: print("Exit ... "), bd = 0)
tab3_toolbar_exitbutton1.place(x=261, y=8, width=15, height=15)

canvas3.create_text(
    260.0,
    28.0,
    anchor="nw",
    text="Exit",
    fill="#FF0202",
    font=("Inter SemiBold", 11 * -1)
)

# ===================================================================================================================
# ===================================================================================================================
# ========== TAB 4 (V-BATT/Motor/EOS) ===============================================================================



tab4 = ttk.Frame(notebook)
notebook.add(tab4, text="V-BATT/Motor/EOS")

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
# ========== Tile-1 =================================================================================================

images["tile_tab4"] = PhotoImage(file=relative_to_assets("Tile.png", "tab4")) 
canvas4.create_image(tablet1_X, tablet1_Y, image=images["tile_tab4"])

canvas4.create_text(73.0, 113.0, anchor="nw", text="Voltage Check (DID 101)", fill="#FFFFFF", font=("Inter SemiBold", 20 * -1))
canvas4.create_text(73.0, 168.0, anchor="nw", text="Set Power Supply", fill="#FFFFFF", font=("Inter SemiBold", 15 * -1))
canvas4.create_text(73.0, 214.0, anchor="nw", text="Get Voltage", fill="#FFFFFF", font=("Inter SemiBold", 15 * -1))

tab4_entry_1 = ttk.Entry(tab4_frame, style ='Background_grey.TEntry')
tab4_entry_1.place(x=306.0, y=168.0, width=95.0, height=20.0)

tab4_entry_2 = ttk.Entry(tab4_frame, style ='Background_grey.TEntry')
tab4_entry_2.place(x=306.0, y=214.0, width=95.0, height=20.0)

images["tab4_tile1_run_test"] = PhotoImage(file=relative_to_assets("tab_testrun_button.png", "tab4"))
tab4_run_test_tile1 = Button(tab4, image=images["tab4_tile1_run_test"], command=lambda: print("tile one capa run test ..."), bd = 0)
tab4_run_test_tile1.place(x=368, y=106, width=34, height=34)

# ===================================================================================================================
# ========== Tile-2 =================================================================================================

images["tile2_tab4"] = PhotoImage(file=relative_to_assets("Tile.png", "tab4")) 
canvas4.create_image((tablet1_X + 475), (tablet1_Y + 0), image=images["tile2_tab4"])

canvas4.create_text(560.0, 113.0, anchor="nw", text="BATT Monitor (DID 102)", fill="#FFFFFF", font=("Inter SemiBold", 20 * -1))
canvas4.create_text(560.0, 168.0, anchor="nw", text="Set Power Supply", fill="#FFFFFF", font=("Inter SemiBold", 15 * -1))
canvas4.create_text(560.0, 214.0, anchor="nw", text="Get Voltage", fill="#FFFFFF", font=("Inter SemiBold", 15 * -1))


tab4_entry3 = ttk.Entry(tab4_frame, style = 'Background_grey.TEntry')
tab4_entry3.place(x=780.0, y=168.0, width=95.0, height=20.0)

tab4_entry4 = ttk.Entry(tab4_frame, style = 'Background_grey.TEntry')
tab4_entry4.place(x=780.0, y=214.0, width=95.0, height=20.0)


images["tab4_tile2_run_test"] = PhotoImage(file=relative_to_assets("tab_testrun_button.png", "tab4"))
tab4_run_test_tile2 = Button(tab4, image=images["tab4_tile2_run_test"], command=lambda: print("tile two capa run test ..."), bd = 0)
tab4_run_test_tile2.place(x=840 , y=106, width=34, height=34)

# ===================================================================================================================
# ========== Tile-3 =================================================================================================

images["tile3_tab4"] = PhotoImage(file=relative_to_assets("Tile.png", "tab4")) 
canvas4.create_image((tablet1_X + 0), (tablet1_Y + 235), image=images["tile3_tab4"])

canvas4.create_text(73.0, 348.0, anchor="nw", text="EOS Test (DID 105)", fill="#FFFFFF", font=("Inter SemiBold", 20 * -1))
canvas4.create_text(73.0, 403.0, anchor="nw", text="Set Power Supply", fill="#FFFFFF", font=("Inter SemiBold", 15 * -1))
canvas4.create_text(73.0, 449.0, anchor="nw", text="Get Voltage", fill="#FFFFFF", font=("Inter SemiBold", 15 * -1))


tab4_entry5 = ttk.Entry(tab4_frame, style = 'Background_grey.TEntry')
tab4_entry5.place(x=306.0, y=403.0, width=95.0, height=20.0)

tab4_entry6 = ttk.Entry(tab4_frame, style = 'Background_grey.TEntry')
tab4_entry6.place(x=306.0, y=449.0, width=95.0, height=20.0)


images["tab4_tile3_run_test"] = PhotoImage(file=relative_to_assets("tab_testrun_button.png", "tab4"))
tab4_run_test_tile3 = Button(tab4, image=images["tab4_tile3_run_test"], command=lambda: print("tile three capa run test ..."), bd = 0)
tab4_run_test_tile3.place(x=368, y=341, width=34, height=34)

# ===================================================================================================================
# ========== Tile-4 =================================================================================================

images["tile4_tab4"] = PhotoImage(file=relative_to_assets("Tile.png", "tab4")) 
canvas4.create_image((tablet1_X + 475), (tablet1_Y + 235), image=images["tile4_tab4"])

canvas4.create_text(73.0 + 475, 348.0, anchor="nw", text="Motor Test (DID 104)", fill="#FFFFFF", font=("Inter SemiBold", 20 * -1))
canvas4.create_text(73.0 + 475, 403.0, anchor="nw", text="Set Power Supply", fill="#FFFFFF", font=("Inter SemiBold", 15 * -1))
canvas4.create_text(73.0 + 475, 438.0, anchor="nw", text="Duty Forward/Reverse", fill="#FFFFFF", font=("Inter SemiBold", 15 * -1))
canvas4.create_text(73.0 + 475, 473.0, anchor="nw", text="Get Voltage", fill="#FFFFFF", font=("Inter SemiBold", 15 * -1))

tab4_entry7 = ttk.Entry(tab4_frame, style = 'Background_grey.TEntry')
tab4_entry7.place(x=306+475, y=403.0, width=95.0, height=20.0)

tab4_entry8 = ttk.Entry(tab4_frame, style = 'Background_grey.TEntry')
tab4_entry8.place(x=306+475, y=438.0, width=95.0, height=20.0)

tab4_entry9 = ttk.Entry(tab4_frame, style = 'Background_grey.TEntry')
tab4_entry9.place(x=306+475, y=473.0, width=95.0, height=20.0)




images["tab4_tile4_run_test"] = PhotoImage(file=relative_to_assets("tab_testrun_button.png", "tab4"))
tab4_run_test_tile4 = Button(tab4, image=images["tab4_tile4_run_test"], command=lambda: print("tile four capa run test ..."), bd = 0)
tab4_run_test_tile4.place(x=368+475, y=341, width=34, height=34)


# ===================================================================================================================
# ========== Footerbar ==============================================================================================

images["tab4_footerbar"] = PhotoImage(file=relative_to_assets("footer_bar.png", "tab4")) #Footer bar
canvas4.create_image(500, 606, image=images["tab4_footerbar"])

canvas4.create_text(
    22.0,
    580.0,
    anchor="nw",
    text="Set power supply voltage",
    fill="#282828",
    font=("Inter Bold", 16 * -1)
)

tab4_entry7 = ttk.Entry(tab4_frame, style = 'Background_grey.TEntry')
tab4_entry7.place(x=306.0, y=580.0, width=95.0, height=20.0)

images["tab4_set_voltage_button"] = PhotoImage(file=relative_to_assets("set_or_get_voltage.png", "tab4"))
tab4_setvoltage = Button(tab4, image=images["tab4_set_voltage_button"], command=lambda: print("setvoltage..."), bd = 0)
tab4_setvoltage.place(x=413, y=576, width=25, height=26)

canvas4.create_text(
    22.0,
    613.0,
    anchor="nw",
    text="Get power supply voltage",
    fill="#282828",
    font=("Inter SemiBold", 16 * -1)
)

tab4_entry8 = ttk.Entry(tab4_frame, style = 'Background_grey.TEntry')
tab4_entry8.place(x=306.0, y=613.0, width=95.0, height=20.0)

images["tab4_get_voltage_button"] = PhotoImage(file=relative_to_assets("set_or_get_voltage.png", "tab4"))
tab4_getvoltage = Button(tab4, image=images["tab4_get_voltage_button"], command=lambda: print("getvoltage..."), bd = 0)
tab4_getvoltage.place(x=413, y=610, width=25, height=26)

# ===================================================================================================================
# ========== Toolbar ================================================================================================

images["tab4_toptoolbar"] = PhotoImage(file=relative_to_assets("top_toolbar.png", "tab4")) #tool bar
canvas4.create_image(179, 19, image=images["tab4_toptoolbar"])

images["tab4_toolbar_playbutton1"] = PhotoImage(file=relative_to_assets("set_or_get_voltage.png", "tab4"))
tab4_toolbar_playbutton1 = Button(tab4, image=images["tab4_toolbar_playbutton1"], command=lambda: print("Run code ..."), bd = 0)
tab4_toolbar_playbutton1.place(x=182, y=5, width=26, height=26)

canvas4.create_text(
    168.0,
    28.0,
    anchor="nw",
    text=" Run code",
    fill="#6E6E6E",
    font=("Inter SemiBold", 11 * -1)
)



images["tab4_toolbar_pausebutton1"] = PhotoImage(file=relative_to_assets("toolbar_pausebutton.png", "tab4"))
tab4_toolbar_pausebutton1 = Button(tab4, image=images["tab4_toolbar_pausebutton1"], command=lambda: print("pause code ... "), bd = 0)
tab4_toolbar_pausebutton1.place(x=100, y=5, width=22.99, height=22.99)

canvas4.create_text(
    80.0,
    28.0,
    anchor="nw",
    text="Pause code",
    fill="#6E6E6E",
    font=("Inter SemiBold", 11 * -1)
)


images["tab4_toolbar_exitbutton1"] = PhotoImage(file=relative_to_assets("toolbar_exitbutton.png", "tab4"))
tab4_toolbar_exitbutton1 = Button(tab4, image=images["toolbar_exitbutton1"], command=lambda: print("Exit ... "), bd = 0)
tab4_toolbar_exitbutton1.place(x=261, y=8, width=15, height=15)

canvas4.create_text(
    260.0,
    28.0,
    anchor="nw",
    text="Exit",
    fill="#FF0202",
    font=("Inter SemiBold", 11 * -1)
)





# ===================================================================================================================
# ========== EXIT ==================================================================================================


window.resizable(False, False)
window.mainloop()
