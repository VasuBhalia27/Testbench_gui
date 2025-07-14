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
    elif tab == "tab2":
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

images["tab1_image_3"] = PhotoImage(file=relative_to_assets("image_3.png", "tab1"))
canvas1.create_image(281.0, 77.0, image=images["tab1_image_3"])

images["tab1_image_1"] = PhotoImage(file=relative_to_assets("image_1.png", "tab1"))
canvas1.create_image(283.0, 417.0, image=images["tab1_image_1"])

canvas1.create_text(199.0, 271.0, anchor="nw", text="Select Version",
                   fill="#FFFFFF", font=("Inter", -24))

images["tab1_image_2"] = PhotoImage(file=relative_to_assets("image_2.png", "tab1"))
canvas1.create_image(797.0, 325.0, image=images["tab1_image_2"])

# Buttons in Tab 1
images["btn1"] = PhotoImage(file=relative_to_assets("button_1.png", "tab1"))
btn1 = Button(tab1, image=images["btn1"], command=lambda: print("button_1 clicked"), bd=0)
btn1.place(x=176, y=320, width=213, height=37)

images["btn2"] = PhotoImage(file=relative_to_assets("button_2.png", "tab1"))
btn2 = Button(tab1, image=images["btn2"], command=lambda: print("button_2 clicked"), bd=0)
btn2.place(x=176, y=380, width=213, height=37)

images["btn3"] = PhotoImage(file=relative_to_assets("button_3.png", "tab1"))
btn3 = Button(tab1, image=images["btn3"], command=lambda: print("button_3 clicked"), bd=0)
btn3.place(x=176, y=440, width=213, height=37)

images["btn4"] = PhotoImage(file=relative_to_assets("button_4.png", "tab1"))
btn4 = Button(tab1, image=images["btn4"], command=lambda: print("button_4 clicked"), bd=0)
btn4.place(x=176, y=500, width=213, height=37)


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

# Load and place image for Tab 2

# ===================================================================================================================
# ========== Tile-1 =================================================================================================

images["tab2_image_1"] = PhotoImage(file=relative_to_assets("Tile.png", "tab2")) 
canvas2.create_image(tablet1_X, tablet1_Y, image=images["tab2_image_1"])

canvas2.create_text(73.0, 113.0, anchor="nw", text="Unlock Capacitor", fill="#FFFFFF", font=("Inter SemiBold", 20 * -1))
canvas2.create_text(73.0, 168.0, anchor="nw", text="Unlock 100pF Capacitor", fill="#FFFFFF", font=("Inter SemiBold", 15 * -1))
canvas2.create_text(73.0, 214.0, anchor="nw", text="Lock 100pF Capacitor", fill="#FFFFFF", font=("Inter SemiBold", 15 * -1))

entry_2 = ttk.Entry(tab2_frame, style ='Background_grey.TEntry')
entry_2.place(x=306.0, y=168.0, width=95.0, height=20.0)


entry_3 = ttk.Entry(tab2_frame, style = 'Background_grey.TEntry')
entry_3.place(x=306.0, y=214.0, width=95.0, height=20.0)

images["tablet_1_run_test"] = PhotoImage(file=relative_to_assets("tab_testrun_button.png", "tab2"))
setvoltage = Button(tab2, image=images["tablet_1_run_test"], command=lambda: print("tab_testrun_button 1 ..."), bd = 0)
setvoltage.place(x=368, y=106, width=34, height=34)

# ===================================================================================================================
# ========== Tile-2 =================================================================================================

images["tab2_image_6"] = PhotoImage(file=relative_to_assets("Tile.png", "tab2")) 
canvas2.create_image((tablet1_X + 475), (tablet1_Y + 0), image=images["tab2_image_6"])

canvas2.create_text(560.0, 113.0, anchor="nw", text="Proximity Capacitor", fill="#FFFFFF", font=("Inter SemiBold", 20 * -1))
canvas2.create_text(560.0, 168.0, anchor="nw", text="Unlock 100pF Capacitor", fill="#FFFFFF", font=("Inter SemiBold", 15 * -1))
canvas2.create_text(560.0, 214.0, anchor="nw", text="Lock 100pF Capacitor", fill="#FFFFFF", font=("Inter SemiBold", 15 * -1))


entry_4 = ttk.Entry(tab2_frame, style = 'Background_grey.TEntry')
entry_4.place(x=780.0, y=168.0, width=95.0, height=20.0)


entry_5 = ttk.Entry(tab2_frame, style = 'Background_grey.TEntry')
entry_5.place(x=780.0, y=214.0, width=95.0, height=20.0)

images["tablet_2_run_test"] = PhotoImage(file=relative_to_assets("tab_testrun_button.png", "tab2"))
setvoltage = Button(tab2, image=images["tablet_2_run_test"], command=lambda: print("tab_testrun_button 1 ..."), bd = 0)
setvoltage.place(x=840 , y=106, width=34, height=34)

# ===================================================================================================================
# ========== Tile-3 =================================================================================================

images["tab2_image_9"] = PhotoImage(file=relative_to_assets("Tile.png", "tab2")) 
canvas2.create_image((tablet1_X + 0), (tablet1_Y + 235), image=images["tab2_image_9"])

canvas2.create_text(73.0, 348.0, anchor="nw", text="Lock Capacitor", fill="#FFFFFF", font=("Inter SemiBold", 20 * -1))
canvas2.create_text(73.0, 403.0, anchor="nw", text="Unlock 100pF Capacitor", fill="#FFFFFF", font=("Inter SemiBold", 15 * -1))
canvas2.create_text(73.0, 449.0, anchor="nw", text="Lock 100pF Capacitor", fill="#FFFFFF", font=("Inter SemiBold", 15 * -1))


entry_6 = ttk.Entry(tab2_frame, style = 'Background_grey.TEntry')
entry_6.place(x=306.0, y=403.0, width=95.0, height=20.0)


entry_7 = ttk.Entry(tab2_frame, style = 'Background_grey.TEntry')
entry_7.place(x=306.0, y=449.0, width=95.0, height=20.0)

images["tablet_3_run_test"] = PhotoImage(file=relative_to_assets("tab_testrun_button.png", "tab2"))
setvoltage = Button(tab2, image=images["tablet_3_run_test"], command=lambda: print("tab_testrun_button 1 ..."), bd = 0)
setvoltage.place(x=368, y=341, width=34, height=34)

# ===================================================================================================================
# ========== Footerbar ==============================================================================================

images["tab2_image_10"] = PhotoImage(file=relative_to_assets("footer_bar.png", "tab2")) #Footer bar
canvas2.create_image(500, 606, image=images["tab2_image_10"])

canvas2.create_text(
    22.0,
    580.0,
    anchor="nw",
    text="Set power supply voltage",
    fill="#282828",
    font=("Inter Bold", 16 * -1)
)

entry_8 = ttk.Entry(tab2_frame, style = 'Background_grey.TEntry')
entry_8.place(x=306.0, y=580.0, width=95.0, height=20.0)

images["setvoltage"] = PhotoImage(file=relative_to_assets("setvoltage.png", "tab2"))
setvoltage = Button(tab2, image=images["setvoltage"], command=lambda: print("setvoltage..."), bd = 0)
setvoltage.place(x=413, y=576, width=25, height=26)

canvas2.create_text(
    22.0,
    613.0,
    anchor="nw",
    text="Get power supply voltage",
    fill="#282828",
    font=("Inter SemiBold", 16 * -1)
)

entry_8 = ttk.Entry(tab2_frame, style = 'Background_grey.TEntry')
entry_8.place(x=306.0, y=613.0, width=95.0, height=20.0)

images["setvoltage1"] = PhotoImage(file=relative_to_assets("setvoltage.png", "tab2"))
setvoltage = Button(tab2, image=images["setvoltage1"], command=lambda: print("setvoltage..."), bd = 0)
setvoltage.place(x=413, y=610, width=25, height=26)

# ===================================================================================================================
# ========== Toolbar ================================================================================================

images["tab2_image_11"] = PhotoImage(file=relative_to_assets("top_toolbar.png", "tab2")) #tool bar
canvas2.create_image(179, 19, image=images["tab2_image_11"])

images["toolbar_playbutton1"] = PhotoImage(file=relative_to_assets("setvoltage.png", "tab2"))
setvoltage1 = Button(tab2, image=images["toolbar_playbutton1"], command=lambda: print("setvoltage..."), bd = 0)
setvoltage1.place(x=182, y=5, width=26, height=26)

canvas2.create_text(
    168.0,
    28.0,
    anchor="nw",
    text=" Run code",
    fill="#6E6E6E",
    font=("Inter SemiBold", 11 * -1)
)



images["toolbar_pausebutton"] = PhotoImage(file=relative_to_assets("toolbar_pausebutton.png", "tab2"))
btn5 = Button(tab2, image=images["toolbar_pausebutton"], command=lambda: print("button_5 clicked"), bd = 0)
btn5.place(x=100, y=5, width=22.99, height=22.99)

canvas2.create_text(
    80.0,
    28.0,
    anchor="nw",
    text="Pause code",
    fill="#6E6E6E",
    font=("Inter SemiBold", 11 * -1)
)


images["toolbar_exitbutton"] = PhotoImage(file=relative_to_assets("toolbar_exitbutton.png", "tab2"))
btn5 = Button(tab2, image=images["toolbar_exitbutton"], command=lambda: print("button_6 clicked"), bd = 0)
btn5.place(x=261, y=8, width=15, height=15)

canvas2.create_text(
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
