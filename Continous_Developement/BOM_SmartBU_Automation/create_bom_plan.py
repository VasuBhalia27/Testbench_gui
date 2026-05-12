import openpyxl
from openpyxl.styles import (
    PatternFill, Font, Alignment, Border, Side
)
from openpyxl.utils import get_column_letter

wb = openpyxl.Workbook()

# ─────────────────────────────────────────────
# COLOUR PALETTE
# ─────────────────────────────────────────────
C_HEADER_BLUE   = "1F4E79"   # dark navy
C_HEADER_TEXT   = "FFFFFF"
C_STEP_TITLE    = "2E75B6"   # mid blue
C_STEP_TEXT     = "FFFFFF"
C_HAVE_BG       = "E2EFDA"   # light green
C_HAVE_BORDER   = "70AD47"
C_NEED_BG       = "FCE4D6"   # light red/orange
C_NEED_BORDER   = "C55A11"
C_SECTION_BG    = "D6E4F0"   # light blue section headers
C_ALT1          = "F2F7FB"
C_ALT2          = "FFFFFF"
C_WARN_BG       = "FFF2CC"   # yellow warning

def fill(hex_color):
    return PatternFill("solid", fgColor=hex_color)

def font(bold=False, color="000000", size=10):
    return Font(bold=bold, color=color, size=size, name="Calibri")

def border(color="BFBFBF"):
    s = Side(style="thin", color=color)
    return Border(left=s, right=s, top=s, bottom=s)

def thick_bottom(color="000000"):
    thin = Side(style="thin", color="BFBFBF")
    thick = Side(style="medium", color=color)
    return Border(left=thin, right=thin, top=thin, bottom=thick)

def wrap_align(h="left", v="center"):
    return Alignment(horizontal=h, vertical=v, wrap_text=True)

def set_col_width(ws, col_letter, width):
    ws.column_dimensions[col_letter].width = width

def merge_and_format(ws, cell_range, text, bg, fg="FFFFFF", size=11, bold=True, h="center"):
    ws.merge_cells(cell_range)
    cell = ws[cell_range.split(":")[0]]
    cell.value = text
    cell.fill = fill(bg)
    cell.font = Font(bold=bold, color=fg, size=size, name="Calibri")
    cell.alignment = Alignment(horizontal=h, vertical="center", wrap_text=True)
    cell.border = border(bg)

# ═══════════════════════════════════════════════════════════
# SHEET 1 – BOM PREPARATION ROADMAP
# ═══════════════════════════════════════════════════════════
ws1 = wb.active
ws1.title = "BOM Preparation Roadmap"
ws1.sheet_view.showGridLines = False
ws1.row_dimensions[1].height = 40
ws1.row_dimensions[2].height = 20

# Column widths
col_widths = {"A": 6, "B": 35, "C": 50, "D": 30, "E": 25, "F": 20}
for col, w in col_widths.items():
    set_col_width(ws1, col, w)

# ── TITLE ROW ──
merge_and_format(ws1, "A1:F1",
    "SmartBU Automation Fixture – BOM Preparation Roadmap",
    C_HEADER_BLUE, C_HEADER_TEXT, size=14, bold=True)

# ── COLUMN HEADERS ──
headers = ["Step", "Activity", "Details / Action Required",
           "Information Source", "Owner", "Status"]
header_row = 3
for col_idx, h in enumerate(headers, start=1):
    cell = ws1.cell(row=header_row, column=col_idx, value=h)
    cell.fill = fill(C_STEP_TITLE)
    cell.font = font(bold=True, color=C_HEADER_TEXT, size=10)
    cell.alignment = wrap_align("center")
    cell.border = border("1F4E79")
ws1.row_dimensions[header_row].height = 25

# ── DATA ──
steps = [
    # (step, activity, details, source, owner, status)
    ("PHASE 1", "UNDERSTAND THE DUT", "", "", "", ""),
    ("1.1", "Review PCB Assembly Drawings",
     "Open ASSY_TOP.pdf and ASSY_BOTTOM.pdf for all 4 variants:\n"
     "• NFC RH – 132309000037J_ASSY_TOP.pdf\n"
     "• NFC LH – 132309000039K_ASSY_TOP.pdf\n"
     "• nonNFC RH – 132309000037J_ASSY_TOP.pdf\n"
     "• nonNFC LH – 132309000039K_ASSY_TOP.pdf\n"
     "Identify: PCB outline dimensions, connector positions, test pad locations",
     "Gerber_Data\\...\\132309000037\\*.pdf",
     "Engineer", "PENDING"),

    ("1.2", "Extract DUT Component BOM",
     "Open the BOM Excel files for each variant:\n"
     "• 132302500036O_BOM.xlsx  (NFC RH)\n"
     "• 132302500038P_BOM.xlsx  (NFC LH)\n"
     "• 132302500040N_BOM.xlsx  (nonNFC RH)\n"
     "• 132302500041N_BOM.xlsx  (nonNFC LH)\n"
     "Filter for: connectors (J*), test points (TP*), large mechanical parts",
     "Gerber_Data\\...\\132302500036\\*.xlsx",
     "Engineer", "PENDING"),

    ("1.3", "Read PCB Description Documents",
     "Open the 090 description_*.doc files – these contain functional block\n"
     "descriptions and signal lists per connector:\n"
     "• 090 description_C652-10.doc  (RH board)\n"
     "• 090 description_C654-11.doc  (LH board)\n"
     "→ Map each connector pin to its signal name (CAN, LIN, Motor, JTAG, GND, VCC…)",
     "Gerber_Data\\...\\090 description_*.doc",
     "Engineer", "PENDING"),

    ("1.4", "Check PCB Layer Stackup",
     "Open Layer_Stackup.xlsx in each variant folder.\n"
     "Extract: total PCB thickness.\n"
     "→ This value determines minimum pogo pin working stroke.",
     "Gerber_Data\\...\\Layer_Stackup.xlsx",
     "Engineer", "PENDING"),

    ("PHASE 2", "DEFINE TEST CONTACT STRATEGY", "", "", "", ""),
    ("2.1", "List all Test Points & Signals to Contact",
     "From Phase 1 data, create a consolidated table:\n"
     "Ref Des | Signal | Connector/TP | Voltage | Current | Notes\n"
     "Expected signals: VCC (battery), GND, CAN-H, CAN-L, LIN, Motor A/B/C,\n"
     "Hall sensors, JTAG (SWDIO/SWDCLK/RESET/VCC_TARGET), NFC antenna (LH/NFC only)",
     "DUT BOM + Description docs + Test Procedures (LH/RH TP.pdf)",
     "Engineer", "PENDING"),

    ("2.2", "Decide Contact Method per Signal Group",
     "For each signal group decide:\n"
     "• HIGH CURRENT (motor, battery): pogo pin with large tip / screw terminal\n"
     "• SIGNAL (CAN, LIN, JTAG): standard 1mm or 1.27mm pogo\n"
     "• NFC antenna: loop coil or flat copper trace coupling\n"
     "Document the contact method for each group.",
     "Engineering judgement + existing RR_VT fixture reference",
     "Engineer", "PENDING"),

    ("2.3", "Determine Pogo Pin Count",
     "Sum all signals requiring automated contact.\n"
     "Add 20% spare positions for future signals.\n"
     "→ This sets the size of the pogo pin carrier PCB.",
     "Signal table from step 2.1",
     "Engineer", "PENDING"),

    ("PHASE 3", "MECHANICAL DESIGN INPUTS", "", "", "", ""),
    ("3.1", "PCB Outer Dimensions & Fiducials",
     "From assembly PDFs: extract PCB width, height, corner radius.\n"
     "Identify fiducial marks or tooling holes used for alignment.\n"
     "→ Used to design alignment pins / guide posts in the fixture.",
     "ASSY_TOP.pdf / Gerber outline layer",
     "Engineer", "PENDING"),

    ("3.2", "Choose Actuation Method",
     "Select ONE:\n"
     "A) Pneumatic: cylinder + solenoid valve + FRL unit + compressor\n"
     "B) Electric linear actuator: motor driver + ball screw\n"
     "C) Manual lever with sensor feedback (lowest cost)\n"
     "→ Decision drives 30–40% of BOM items.",
     "Project constraints (cost, cycle time, space)",
     "Project Lead", "DECISION NEEDED"),

    ("3.3", "Calculate Actuation Force & Stroke",
     "Force = (number of pogo pins) × (pogo contact force per pin in grams)\n"
     "Typical pogo: 50–150g each. Example: 20 pins × 100g = 2 kg → ~20 N min.\n"
     "Stroke = PCB thickness + pogo overtravel (typically 1–2 mm) + clearance.\n"
     "→ Use this to select cylinder bore or actuator model.",
     "Pogo pin datasheets + Layer_Stackup.xlsx",
     "Engineer", "PENDING"),

    ("3.4", "Design Pogo Pin Carrier PCB / Block",
     "Define:\n"
     "• Grid pitch matching DUT test pad pitch\n"
     "• PCB size and mounting holes\n"
     "• Material (FR4 / PEEK for high-temp applications)\n"
     "Reference: RR_VT fixture uses Harwin test pins on custom carrier board.",
     "Signal table + PCB drawing",
     "PCB Designer", "PENDING"),

    ("PHASE 4", "ELECTRICAL / INSTRUMENTATION", "", "", "", ""),
    ("4.1", "Confirm CAN Interface Hardware",
     "Verify the CAN interface already in use (likely PEAK PCAN-USB or Vector).\n"
     "Confirm part number and add to BOM with quantity.\n"
     "Check if a second channel is needed for LH + RH simultaneous testing.",
     "Existing lab setup / T32_JLINK Config folder",
     "Engineer", "CONFIRM"),

    ("4.2", "Confirm LIN Interface Hardware",
     "Verify LIN master interface (USB-LIN adapter or in-built on CAN tool).\n"
     "Add part number and quantity to BOM.",
     "Existing lab setup",
     "Engineer", "CONFIRM"),

    ("4.3", "Confirm JTAG Debugger",
     "Already documented in T32_JLINK setup.\n"
     "Confirm: Lauterbach TRACE32 or SEGGER J-Link?\n"
     "Check if the existing debugger supports automated (headless) use.\n"
     "Add license dongle if required.",
     "T32_JLINK\\SmartBU\\Debugger_hw.jpg + How_To_Debugg.xlsx",
     "Engineer", "CONFIRM"),

    ("4.4", "Specify Programmable Power Supply",
     "Required specs:\n"
     "• Output voltage range: covers DUT operating voltage (check test procedure)\n"
     "• Current rating: motor stall current × 1.5 safety factor\n"
     "• Remote control interface: USB / LAN / GPIB\n"
     "Suggested: Keysight E36xx or Rohde & Schwarz NGE100 series.",
     "LH_i460_NON_NFC_TP.pdf / RH_i460_NFC_TP.pdf",
     "Engineer", "PENDING"),

    ("4.5", "Relay / Signal Switching Board",
     "For signals not directly in pogo contact (bus enables, load switches):\n"
     "• Determine number of switched channels\n"
     "• Choose relay board (USB HID relay board, or PLC digital output)\n"
     "• Confirm voltage and current rating per channel",
     "Signal table from step 2.1",
     "Engineer", "PENDING"),

    ("4.6", "Barcode / Datamatrix Reader",
     "Already integrated in the project (Barcode_Reader folder).\n"
     "Confirm: reader model, cable interface (USB/RS232), mounting bracket.\n"
     "Add to BOM.",
     "Continous_Developement\\Nfc_Version\\Barcode_Reader",
     "Engineer", "CONFIRM"),

    ("PHASE 5", "SAFETY & SENSORS", "", "", "", ""),
    ("5.1", "DUT Presence Sensor",
     "Sensor to confirm PCB is correctly loaded before power/actuation.\n"
     "Options: optical fork sensor, inductive proximity, mechanical micro-switch.\n"
     "Define: mounting position, cable length, output type (NPN/PNP/digital).",
     "Fixture mechanical drawing",
     "Engineer", "PENDING"),

    ("5.2", "Actuator Position Sensors",
     "Two sensors needed: OPEN position + CLOSED (contacted) position.\n"
     "Type: magnetic reed switch or inductive sensor integrated in actuator.\n"
     "Used by software to confirm safe state before/after actuation.",
     "Actuator datasheet",
     "Engineer", "PENDING"),

    ("5.3", "Emergency Stop Button",
     "Required if fixture has powered actuation.\n"
     "Standard IEC 60947-5-5 mushroom head E-stop, panel mount.\n"
     "Add to BOM with cable and din-rail mount relay module.",
     "Safety requirement",
     "Engineer", "PENDING"),

    ("PHASE 6", "CABLING & WIRING", "", "", "", ""),
    ("6.1", "Create Wiring Diagram",
     "Draw a wiring diagram from:\n"
     "Pogo carrier → breakout board → instruments (CAN, LIN, PSU, JTAG, relays)\n"
     "Define: signal names, wire gauge, shielding (CAN/LIN = twisted pair shielded),\n"
     "connector types at each end.",
     "Signal table + instrument specs",
     "Engineer", "PENDING"),

    ("6.2", "List All Connectors & Cables",
     "For each harness segment list:\n"
     "• Connector type & part number (both ends)\n"
     "• Wire gauge (AWG)\n"
     "• Shielded or unshielded\n"
     "• Length\n"
     "Reference: RR_VT fixture uses DB25 for multi-signal harness.",
     "Wiring diagram from 6.1",
     "Engineer", "PENDING"),

    ("PHASE 7", "ASSEMBLE FINAL BOM", "", "", "", ""),
    ("7.1", "Consolidate All BOM Sections",
     "Combine into one BOM document with columns:\n"
     "Item# | Category | Description | Manufacturer | Part No. | Qty | Unit | Unit Cost | Total Cost | Source | Status\n"
     "Categories: Mechanical, Actuation, Pogo/Contact, Electrical, Instruments, Cables, Safety",
     "All previous phases",
     "Engineer", "PENDING"),

    ("7.2", "Review and Validate BOM",
     "Cross-check BOM against:\n"
     "• Test procedure (all signals covered?)\n"
     "• Existing BOM_SmartBU_Automation.xlsx (avoid duplicates)\n"
     "• RR_VT_PCB_BOM_Rev2.0.xlsx (reference fixture for similar items)\n"
     "Get sign-off from project lead.",
     "All previous sources",
     "Project Lead", "PENDING"),

    ("7.3", "Get Quotations for New Items",
     "For all items marked PENDING procurement:\n"
     "• Request quotes from: Harwin, Farnell, RS Components, Misumi\n"
     "• For custom mechanical parts: get quotes from machine shop\n"
     "• For custom PCB (pogo carrier): get quotes from PCB manufacturer",
     "Final BOM",
     "Procurement", "PENDING"),
]

row = 4
phase_row_indices = []
for item in steps:
    step, activity, details, source, owner, status = item
    is_phase = step.startswith("PHASE")
    ws1.row_dimensions[row].height = 15 if is_phase else 70

    if is_phase:
        phase_row_indices.append(row)
        merge_and_format(ws1, f"A{row}:F{row}",
            f"  ▶  {activity}",
            C_SECTION_BG, "1F4E79", size=10, bold=True, h="left")
        row += 1
        continue

    alt = C_ALT1 if row % 2 == 0 else C_ALT2
    status_colors = {
        "PENDING":        ("FCE4D6", "C55A11"),
        "CONFIRM":        ("FFF2CC", "7F6000"),
        "DECISION NEEDED":("FDEBD0", "9C2A10"),
        "DONE":           ("E2EFDA", "375623"),
    }
    s_bg, s_fg = status_colors.get(status, ("F2F2F2", "595959"))

    for col_idx, val in enumerate([step, activity, details, source, owner, status], start=1):
        c = ws1.cell(row=row, column=col_idx, value=val)
        c.border = border()
        c.alignment = wrap_align()
        if col_idx == 1:   # Step number
            c.fill = fill(C_STEP_TITLE)
            c.font = font(bold=True, color=C_HEADER_TEXT, size=9)
            c.alignment = wrap_align("center")
        elif col_idx == 6:  # Status
            c.fill = fill(s_bg)
            c.font = font(bold=True, color=s_fg, size=9)
            c.alignment = wrap_align("center")
        else:
            c.fill = fill(alt)
            c.font = font(size=9)

    row += 1

# Freeze pane below header
ws1.freeze_panes = "A4"

# ═══════════════════════════════════════════════════════════
# SHEET 2 – HAVE vs NEED TRACKER
# ═══════════════════════════════════════════════════════════
ws2 = wb.create_sheet("Have vs Need")
ws2.sheet_view.showGridLines = False
ws2.row_dimensions[1].height = 40
ws2.row_dimensions[2].height = 20

col_widths2 = {"A": 6, "B": 25, "C": 40, "D": 12, "E": 45, "F": 20, "G": 20}
for col, w in col_widths2.items():
    set_col_width(ws2, col, w)

merge_and_format(ws2, "A1:G1",
    "SmartBU Automation Fixture – What We Have vs What We Need",
    C_HEADER_BLUE, C_HEADER_TEXT, size=14, bold=True)

headers2 = ["#", "Category", "Item / Document", "Status", "Details / Gap", "Action Required", "Priority"]
for col_idx, h in enumerate(headers2, start=1):
    c = ws2.cell(row=3, column=col_idx, value=h)
    c.fill = fill(C_STEP_TITLE)
    c.font = font(bold=True, color=C_HEADER_TEXT, size=10)
    c.alignment = wrap_align("center")
    c.border = border("1F4E79")
ws2.row_dimensions[3].height = 25

HAVE = "HAVE ✓"
PARTIAL = "PARTIAL ~"
NEED = "NEED ✗"

items = [
    # (num, category, item, status, details, action, priority)
    # ─ DOCUMENTS ─
    ("", "── DOCUMENTS ──", "", "", "", "", ""),
    ("1", "Documents", "Manual Fixture Setup Photos\n(Hw_Setups/*.png)",
     HAVE, "6 photos: fixture assembly, sensor PCB connections, motor connections, debugger wiring",
     "None – already documented", "—"),
    ("2", "Documents", "Test Procedures (LH + RH)\nLH_i460_NON_NFC_TP.pdf\nRH_i460_NFC_TP.pdf",
     HAVE, "Full test procedures for both hand sides available",
     "Extract: voltage/current specs, test sequence, signal list", "HIGH"),
    ("3", "Documents", "How_To_Debugg.xlsx",
     HAVE, "Debugging procedure documented", "None", "—"),
    ("4", "Documents", "PCB Gerber data – all 4 variants\n(Gerber_Data/XNF I460 _20251208/)",
     HAVE, "4 PCB variants: NFC LH/RH, nonNFC LH/RH\nAssembly drawings, BOM, drill files, ODB++ included",
     "Open ASSY_TOP.pdf to extract connector positions and test pad coordinates", "HIGH"),
    ("5", "Documents", "DUT Component BOMs\n(132302500036O_BOM.xlsx etc.)",
     HAVE, "4 BOM files – one per PCB variant", "Open and filter for connectors (J*) and test points (TP*)", "HIGH"),
    ("6", "Documents", "PCB Description Documents\n(090 description_C652-10.doc etc.)",
     HAVE, "Functional description per board variant", "Read to extract signal mapping per connector pin", "HIGH"),
    ("7", "Documents", "PCB Layer Stackup\n(Layer_Stackup.xlsx)",
     HAVE, "Available in each variant folder", "Extract total PCB thickness for pogo pin stroke calculation", "MEDIUM"),
    ("8", "Documents", "Automation Scripts\n(T32_JLINK/AutomationScripts/)",
     HAVE, "Existing test automation scripts available",
     "Review to confirm which hardware interfaces are already used", "MEDIUM"),
    ("9", "Documents", "Reference Fixture BOM\n(RR_VT_PCB_BOM_Rev2.0.xlsx)",
     HAVE, "Another fixture BOM available as reference for similar items",
     "Use as reference for pogo pin, connector, and PCB design", "MEDIUM"),
    ("10", "Documents", "Signal-to-Test-Point Mapping Table",
     NEED, "No consolidated table exists yet mapping each DUT signal to its contact point",
     "Create by cross-referencing: 090 description doc + DUT BOM + test procedures", "CRITICAL"),
    ("11", "Documents", "Wiring Diagram (Fixture → Instruments)",
     NEED, "No wiring diagram for automation fixture exists yet",
     "Create after completing signal mapping (step 10)", "HIGH"),
    # ─ MECHANICAL ─
    ("", "── MECHANICAL ──", "", "", "", "", ""),
    ("12", "Mechanical", "PCB Outline Drawing / Dimensions",
     PARTIAL, "Available in Gerber assembly PDFs but not yet extracted as a standalone dimension drawing",
     "Open ASSY_TOP.pdf and extract: width, height, tooling holes, fiducials", "HIGH"),
    ("13", "Mechanical", "Fixture Base Plate",
     NEED, "No base plate drawing or part defined yet",
     "Define: material (aluminium), dimensions, mounting pattern for instruments and actuator", "HIGH"),
    ("14", "Mechanical", "Alignment Pins / Guide Posts",
     NEED, "Manual fixture uses the PCB edge – automation requires precision guide posts",
     "Derive from PCB tooling hole coordinates in drill file", "HIGH"),
    ("15", "Mechanical", "PCB Carrier / Nest (DUT holder)",
     NEED, "No automated PCB nest designed yet",
     "Design custom nest matching PCB outline + actuation direction", "HIGH"),
    ("16", "Mechanical", "Pogo Pin Carrier PCB or Block",
     NEED, "No pogo carrier designed yet\nReference: RR_VT uses Harwin pins on custom PCB",
     "Design after signal mapping is complete (step 10)", "HIGH"),
    ("17", "Mechanical", "Actuator (Pneumatic or Electric)",
     NEED, "Decision not made yet – pneumatic cylinder or electric linear actuator",
     "Make actuation method decision first, then specify model, stroke, bore/force", "CRITICAL"),
    ("18", "Mechanical", "Mounting Hardware\n(screws, standoffs, DIN rail)",
     NEED, "Standard hardware – not yet listed",
     "Add after base plate and PCB carrier are defined", "LOW"),
    # ─ ELECTRICAL / INSTRUMENTS ─
    ("", "── ELECTRICAL / INSTRUMENTS ──", "", "", "", "", ""),
    ("19", "Instruments", "JTAG Debugger (T32 or J-Link)",
     PARTIAL, "Debugger documented in T32_JLINK setup, hardware photo exists",
     "Confirm: exact model number, cable type, add to BOM with quantity", "HIGH"),
    ("20", "Instruments", "CAN Bus Interface (PEAK / Vector)",
     PARTIAL, "Used in existing scripts but part number not confirmed",
     "Confirm model (e.g., PCAN-USB) and add to BOM", "HIGH"),
    ("21", "Instruments", "LIN Bus Interface",
     PARTIAL, "Referenced in automation scripts, hardware not yet specified in BOM",
     "Confirm model and add to BOM", "HIGH"),
    ("22", "Instruments", "Programmable Power Supply",
     NEED, "No PSU specified yet\nMust support remote control (USB/LAN/GPIB)",
     "Extract DUT voltage/current from test procedure, then select PSU model", "HIGH"),
    ("23", "Instruments", "Relay / Signal Switching Board",
     NEED, "No relay board specified yet",
     "After signal mapping: count switched channels, choose relay board", "MEDIUM"),
    ("24", "Instruments", "Barcode / Datamatrix Reader",
     PARTIAL, "Already integrated in software (Barcode_Reader folder) but hardware BOM entry missing",
     "Confirm reader model, add to BOM with mounting bracket", "MEDIUM"),
    # ─ POGO PINS / CONTACT ─
    ("", "── POGO PINS / CONTACT ──", "", "", "", "", ""),
    ("25", "Contact", "Pogo Pin Part Number and Spec",
     NEED, "Not defined yet\nReference: RR_VT uses Harwin-type test pins (A700000008880531, A700000008880563)",
     "After signal mapping: specify per contact type (signal, power, HV)\nCheck Harwin pins already in RR_VT BOM", "HIGH"),
    ("26", "Contact", "Total Pogo Pin Count",
     NEED, "Cannot be determined until signal-to-pad mapping table is complete",
     "Complete step 10, then count all pins + add 20% spare", "HIGH"),
    ("27", "Contact", "Pogo Pin Carrier Board (Gerber)",
     NEED, "No design exists yet", "Design after pogo count and grid pitch are defined", "MEDIUM"),
    # ─ SAFETY ─
    ("", "── SAFETY ──", "", "", "", "", ""),
    ("28", "Safety", "DUT Presence Sensor",
     NEED, "No presence sensor specified",
     "Select: optical fork, inductive proximity, or micro-switch\nAdd to BOM", "MEDIUM"),
    ("29", "Safety", "Actuator Position Sensors (open/closed)",
     NEED, "Required for automated control loop\nTypically 2 sensors per actuator",
     "Select based on actuator type chosen in step 3.2 (item 17)", "MEDIUM"),
    ("30", "Safety", "Emergency Stop Button",
     NEED, "Required if powered actuation is used",
     "Standard IEC 60947-5-5 mushroom head E-stop\nAdd to BOM", "MEDIUM"),
    # ─ CABLING ─
    ("", "── CABLING / WIRING ──", "", "", "", "", ""),
    ("31", "Cabling", "Signal Harness: Pogo Carrier → Instruments",
     NEED, "No harness designed yet",
     "Create after wiring diagram is done (item 11)", "MEDIUM"),
    ("32", "Cabling", "CAN Bus Cable (twisted pair shielded)",
     NEED, "Not yet specified", "Specify wire gauge, length, connector types at both ends", "MEDIUM"),
    ("33", "Cabling", "LIN Bus Cable",
     NEED, "Not yet specified", "Specify wire gauge, length, connector types", "MEDIUM"),
    ("34", "Cabling", "Power Cable (PSU → Pogo Carrier)",
     NEED, "Not yet specified\nCurrent rating depends on DUT motor load",
     "Extract max current from test procedure before specifying wire gauge", "MEDIUM"),
    ("35", "Cabling", "JTAG Ribbon Cable",
     PARTIAL, "Existing manual connection uses ribbon cable\nBOM entry not confirmed",
     "Confirm part number from existing setup, add to BOM", "LOW"),
    # ─ SOFTWARE ─
    ("", "── SOFTWARE ──", "", "", "", "", ""),
    ("36", "Software", "Automation Test Scripts\n(T32_JLINK/AutomationScripts/)",
     HAVE, "Existing scripts available for NFC/nonNFC LH and RH",
     "Review if scripts need updates to support automated fixture I/O (relay, PSU, sensor)", "MEDIUM"),
    ("37", "Software", "Fixture Controller Interface\n(actuator + relay + sensor control)",
     NEED, "No software exists yet for controlling the physical automation fixture hardware",
     "Develop after hardware (actuator, relay, sensors) is defined", "HIGH"),
    ("38", "Software", "MySQL Integration for Results Logging",
     HAVE, "MySQL integration exists in project (MySQL/ folders)",
     "Verify it covers automation fixture results or needs extension", "LOW"),
]

row2 = 4
for item in items:
    num, cat, name, status, details, action, priority = item
    is_section = cat.startswith("──")

    ws2.row_dimensions[row2].height = 15 if is_section else 65

    if is_section:
        merge_and_format(ws2, f"A{row2}:G{row2}",
            f"  {cat}", C_SECTION_BG, "1F4E79", size=10, bold=True, h="left")
        row2 += 1
        continue

    alt = C_ALT1 if row2 % 2 == 0 else C_ALT2

    status_colors = {
        HAVE:    ("E2EFDA", "375623"),
        PARTIAL: ("FFF2CC", "7F6000"),
        NEED:    ("FCE4D6", "C55A11"),
    }
    s_bg, s_fg = status_colors.get(status, ("F2F2F2", "595959"))

    priority_colors = {
        "CRITICAL": ("C00000", "FFFFFF"),
        "HIGH":     ("FF0000", "FFFFFF"),
        "MEDIUM":   ("FF7C00", "FFFFFF"),
        "LOW":      ("70AD47", "FFFFFF"),
        "—":        ("F2F2F2", "595959"),
    }
    p_bg, p_fg = priority_colors.get(priority, ("F2F2F2", "595959"))

    for col_idx, val in enumerate([num, cat, name, status, details, action, priority], start=1):
        c = ws2.cell(row=row2, column=col_idx, value=val)
        c.border = border()
        c.alignment = wrap_align()
        if col_idx == 4:   # Status
            c.fill = fill(s_bg)
            c.font = font(bold=True, color=s_fg, size=9)
            c.alignment = wrap_align("center")
        elif col_idx == 7:  # Priority
            c.fill = fill(p_bg)
            c.font = font(bold=True, color=p_fg, size=9)
            c.alignment = wrap_align("center")
        elif col_idx == 1:
            c.fill = fill(C_STEP_TITLE)
            c.font = font(bold=True, color=C_HEADER_TEXT, size=9)
            c.alignment = wrap_align("center")
        else:
            c.fill = fill(alt)
            c.font = font(size=9)

    row2 += 1

ws2.freeze_panes = "A4"

# ═══════════════════════════════════════════════════════════
# SHEET 3 – LEGEND
# ═══════════════════════════════════════════════════════════
ws3 = wb.create_sheet("Legend")
ws3.sheet_view.showGridLines = False
set_col_width(ws3, "A", 6)
set_col_width(ws3, "B", 25)
set_col_width(ws3, "C", 55)

merge_and_format(ws3, "A1:C1", "Legend / Key", C_HEADER_BLUE, C_HEADER_TEXT, size=13)

legend_items = [
    ("", "STATUS", ""),
    ("✓", "HAVE", "Item or document already available – no procurement needed"),
    ("~", "PARTIAL", "Item partially available – confirm details or add to BOM"),
    ("✗", "NEED", "Item missing – must be sourced, designed, or created"),
    ("", "STEP STATUS", ""),
    ("", "PENDING", "Work not yet started"),
    ("", "CONFIRM", "Item likely exists – verify part number and add to BOM"),
    ("", "DECISION NEEDED", "A design/procurement decision must be made before proceeding"),
    ("", "DONE", "Step completed"),
    ("", "PRIORITY", ""),
    ("", "CRITICAL", "Blocks multiple downstream tasks – address first"),
    ("", "HIGH", "Required before BOM can be submitted"),
    ("", "MEDIUM", "Required before fixture can be built"),
    ("", "LOW", "Can be finalised later in the project"),
]

legend_fills = {
    "HAVE":             ("E2EFDA", "375623"),
    "PARTIAL":          ("FFF2CC", "7F6000"),
    "NEED":             ("FCE4D6", "C55A11"),
    "PENDING":          ("FCE4D6", "C55A11"),
    "CONFIRM":          ("FFF2CC", "7F6000"),
    "DECISION NEEDED":  ("FDEBD0", "9C2A10"),
    "DONE":             ("E2EFDA", "375623"),
    "CRITICAL":         ("C00000", "FFFFFF"),
    "HIGH":             ("FF0000", "FFFFFF"),
    "MEDIUM":           ("FF7C00", "FFFFFF"),
    "LOW":              ("70AD47", "FFFFFF"),
    "STATUS":           (C_SECTION_BG, "1F4E79"),
    "STEP STATUS":      (C_SECTION_BG, "1F4E79"),
    "PRIORITY":         (C_SECTION_BG, "1F4E79"),
}

lr = 3
for sym, label, desc in legend_items:
    is_header = label in ("STATUS", "STEP STATUS", "PRIORITY")
    ws3.row_dimensions[lr].height = 20
    if is_header:
        merge_and_format(ws3, f"A{lr}:C{lr}", f"  {label}", C_SECTION_BG, "1F4E79", size=10, bold=True, h="left")
        lr += 1
        continue
    bg, fg = legend_fills.get(label, ("F2F2F2", "595959"))
    for ci, v in enumerate([sym, label, desc], start=1):
        c = ws3.cell(row=lr, column=ci, value=v)
        c.border = border()
        c.alignment = wrap_align("center" if ci < 3 else "left")
        c.fill = fill(bg)
        c.font = font(bold=(ci == 2), color=fg, size=10)
    lr += 1

# ─────────────────────────────────────────────
# SAVE
# ─────────────────────────────────────────────
out = r"C:\UShin\Testbench_gui_Charan\Continous_Developement\BOM_SmartBU_Automation\BOM_Preparation_Plan.xlsx"
wb.save(out)
print(f"Saved: {out}")
