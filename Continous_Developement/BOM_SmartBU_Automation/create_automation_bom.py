"""
Generate: SmartBU_Automation_Fixture_BOM.xlsx
Covers all subsystems of the automation fixture for XNF I460 SmartBU testing.
Sources used:
  - RR_VT_PCB_BOM_Rev2.0.xlsx   (reference fixture)
  - How_To_Debugg.xlsx           (KIKUSUI PWR401L, Trace32, connections)
  - Connection sheet             (29 test points on 34-pin IDC + DB9)
  - DUT BOM (132302500036O etc.) (Amphenol FCI X600, DUT signals)
  - Hw_Setups photos             (manual fixture layout)
  - config.t32                   (Lauterbach Trace32 USB)
"""

import openpyxl
from openpyxl.styles import PatternFill, Font, Alignment, Border, Side
from openpyxl.utils import get_column_letter

# ─── Helpers ────────────────────────────────────────────────────────────────
def fill(hex_color):
    return PatternFill("solid", fgColor=hex_color)

def font(bold=False, color="000000", size=10, italic=False):
    return Font(bold=bold, color=color, size=size, name="Calibri", italic=italic)

def thin_border(color="BFBFBF"):
    s = Side(style="thin", color=color)
    return Border(left=s, right=s, top=s, bottom=s)

def wrap(h="left", v="center"):
    return Alignment(horizontal=h, vertical=v, wrap_text=True)

def col_w(ws, col, w):
    ws.column_dimensions[get_column_letter(col) if isinstance(col, int) else col].width = w

def merge(ws, rng, text, bg, fg="FFFFFF", sz=11, bold=True, h="center", italic=False):
    ws.merge_cells(rng)
    c = ws[rng.split(":")[0]]
    c.value = text
    c.fill = fill(bg)
    c.font = Font(bold=bold, color=fg, size=sz, name="Calibri", italic=italic)
    c.alignment = Alignment(horizontal=h, vertical="center", wrap_text=True)

# ─── Colours ────────────────────────────────────────────────────────────────
NAVY    = "1F4E79"
BLUE    = "2E75B6"
LBLUE   = "D6E4F0"
WHITE   = "FFFFFF"
ALT1    = "F2F7FB"
ALT2    = "FFFFFF"
GREEN   = "375623"
GBKG    = "E2EFDA"
AMBER   = "7F6000"
ABKG    = "FFF2CC"
RED     = "C00000"
RBKG    = "FCE4D6"
GRAY    = "595959"
GBKG2   = "F2F2F2"

# ─── Workbook ────────────────────────────────────────────────────────────────
wb = openpyxl.Workbook()

# ════════════════════════════════════════════════════════════════════════════
# SHEET 1 — BOM MAIN
# ════════════════════════════════════════════════════════════════════════════
ws = wb.active
ws.title = "Automation Fixture BOM"
ws.sheet_view.showGridLines = False

# Column widths: A=item, B=category, C=qty, D=ref, E=part name,
#                F=description, G=mfr, H=order_no, I=pkg,
#                J=unit_price(INR), K=total, L=lead_time, M=status, N=source, O=notes
widths = [5, 20, 6, 14, 28, 44, 22, 22, 12, 14, 14, 14, 16, 22, 34]
for i, w in enumerate(widths, 1):
    col_w(ws, i, w)

# ── Title block ──
ws.row_dimensions[1].height = 44
ws.row_dimensions[2].height = 16
ws.row_dimensions[3].height = 16
ws.row_dimensions[4].height = 16
ws.row_dimensions[5].height = 16

merge(ws, "A1:O1",
      "BILL OF MATERIALS  —  SmartBU Automation Fixture  (XNF I460 / BMW MAE)",
      NAVY, WHITE, sz=14, bold=True)

meta = [
    ("A2", "Date:", "C2", "11.05.2026"),
    ("A3", "Engineer:", "C3", "TBD"),
    ("A4", "Project:", "C4", "BMW SUPPORT MAE  |  SmartBU (NFC / non-NFC, LH / RH)"),
    ("A5", "Document:", "C5", "SmartBU_Automation_Fixture_BOM_Rev1.0"),
]
for lc, lt, vc, vt in meta:
    c = ws[lc]; c.value = lt; c.font = font(bold=True, size=9)
    c = ws[vc]; c.value = vt; c.font = font(size=9)

# ── Column headers ──
HEADERS = ["Item", "Subsystem", "Qty", "Ref.",
           "Part Name", "Description / Value",
           "Manufacturer", "Ordering No.", "Package / Form",
           "Unit Price\n(INR ~)", "Total\n(INR ~)",
           "Lead Time", "Status",
           "Source / Datasheet", "Notes / Remarks"]
ws.row_dimensions[6].height = 30
for ci, h in enumerate(HEADERS, 1):
    c = ws.cell(row=6, column=ci, value=h)
    c.fill = fill(BLUE)
    c.font = font(bold=True, color=WHITE, size=9)
    c.alignment = wrap("center")
    c.border = thin_border(NAVY)

ws.freeze_panes = "A7"

# ── Status legend colours ──
STATUS_FMT = {
    "CONFIRMED":      (GBKG,  GREEN),
    "TO CONFIRM":     (ABKG,  AMBER),
    "TO PROCURE":     (RBKG,  RED),
    "CUSTOM/3D PRINT": ("EAD1DC", "7C2137"),
    "IN-HOUSE":       (GBKG,  GREEN),
}

# ─── BOM DATA ────────────────────────────────────────────────────────────────
# Columns: item, subsystem, qty, ref, part_name, description,
#          manufacturer, order_no, package, unit_price, lead_time, status, source, notes
BOM = [
    # ── SECTION ──────────────────────────────────────────────────────────────
    ("SEC", "1. TEST INTERFACE BOARD (Fixture PCB)", "", "", "", "", "", "", "", "", "", "", "", ""),

    (1, "Fixture PCB", 1, "PCB1",
     "Automation Fixture PCB",
     "Custom designed test interface PCB. Hosts: 34-pin IDC header, DB9 for motor, "
     "LIN terminal, JTAG header, SG signal conditioning, relay drivers, LED indicator. "
     "Replaces manual probe board from manual setup.",
     "Custom / PCB Fabricator", "N/A – custom design", "THT + SMD",
     0, "2–3 weeks", "TO PROCURE",
     "Based on Connection sheet – 29 test point map",
     "Design files must be created; layout from IDC/DB9 signal table"),

    (2, "Fixture PCB", 1, "X_IDC34",
     "IDC Connector 34-pin (Male, PCB mount)",
     "34-pin IDC box header, 2.54mm pitch, PCB mount. Connects fixture PCB to pogo carrier via ribbon cable.",
     "Wurth Elektronik", "61201421621", "THT",
     220, "1 week", "TO PROCURE",
     "RS / Wurth Elektronik catalogue",
     "PIN 1–29 mapped per Connection sheet table"),

    (3, "Fixture PCB", 1, "X_IDC34_F",
     "IDC Ribbon Cable 34-pin Female (0.5m)",
     "34-way flat ribbon cable assembly with IDC crimp connectors at both ends, 0.5m.",
     "3M / Amphenol", "3365/34 or equivalent", "Cable",
     350, "1 week", "TO PROCURE",
     "RS / Farnell",
     "Connects fixture PCB to pogo carrier block"),

    (4, "Fixture PCB", 1, "X_DB9",
     "DB9 Female Connector (PCB mount, right angle)",
     "DE-9 female, PCB mount, right angle. For DRV_OUT_A / DRV_OUT_B motor signals.",
     "Amphenol / TE Connectivity", "787083-1 or equivalent", "THT",
     120, "1 week", "TO PROCURE",
     "RS Components / Farnell",
     "Motor actuator output lines – same as manual setup"),

    (5, "Fixture PCB", 1, "X_LIN",
     "Terminal Block 3-pin, 5.08mm pitch",
     "3-position screw terminal block for LIN bus connection (LIN, GND, supply).",
     "Wurth Elektronik", "691241510003", "THT",
     90, "1 week", "TO PROCURE",
     "Wurth Elektronik",
     "Same family as RR_VT relay board terminals"),

    (6, "Fixture PCB", 1, "X_JTAG",
     "ARM Cortex Debug Connector 10-pin (2×5, 1.27mm)",
     "10-pin SWD/JTAG header for Lauterbach Trace32. Carries SWD_DATA (TP201), "
     "SWD_CLK (TP202), RESET (TP200), VCC_TARGET, GND.",
     "Samtec / Harwin", "M20-9900542 or FTSH-105-01-L-D-K", "SMD/THT",
     180, "1 week", "TO PROCURE",
     "Harwin / Samtec",
     "Matches Lauterbach 10-pin Mictor adapter on Trace32 CombiProbe"),

    (7, "Fixture PCB", 6, "R1–R6",
     "Resistor 1.2 kΩ, 1%, 1/4W",
     "Signal conditioning resistors for SG1 and SG2 sensor signals.",
     "Yageo", "MFR-25FRF52-1K2", "THT Axial",
     8, "1 week", "TO PROCURE",
     "Connection sheet: SG1/SG2 1.2K ohm",
     "Same value as documented in Connection sheet"),

    (8, "Fixture PCB", 4, "SW1–SW4",
     "DIP Switch 4-position",
     "DIP switch for SG1, SG2, Capa (100pF) signal enable/disable, per Connection sheet.",
     "C&K / TE Connectivity", "SD04H0SK or equivalent", "THT",
     65, "1 week", "TO PROCURE",
     "Connection sheet: DIP switch items",
     "Manually selectable; can be relay-replaced for full automation"),

    (9, "Fixture PCB", 2, "C1–C2",
     "Capacitor 100 pF, 50V, C0G",
     "Capa signal path capacitor per Connection sheet (Cap signal DIP switch 100pF).",
     "Murata", "GCM1555C1H101FA16D", "SMD 0402",
     12, "1 week", "TO PROCURE",
     "Connection sheet: Capa signal",
     ""),

    # ── SECTION ──────────────────────────────────────────────────────────────
    ("SEC", "2. POGO PIN / TEST CONTACT SYSTEM", "", "", "", "", "", "", "", "", "", "", "", ""),

    (10, "Pogo / Needle Bed", 14, "TP_SIG",
     "Test Pin – Signal, 1.5A (Pogo / Spring Probe)",
     "Spring probe test pin, 1.5A max, male, for signal test points: "
     "3V3, 3V8, SG1/SG2, cap signals, LED, EOS, SWD lines (20 signal-grade contacts).",
     "RS Components", "261-5159", "Through-hole pogo",
     385, "2 weeks", "TO PROCURE",
     "RR_VT BOM item #16 – same part",
     "Same pin used in RR_VT fixture. Qty = 14 signal TPs + 2 spare"),

    (11, "Pogo / Needle Bed", 18, "TP_PWR",
     "Test Pin – Power, 3A (Pogo / Spring Probe)",
     "Spring probe test pin, 3A max, male, for power test points: "
     "12V (TP100), GND (TP101/104/106), motor sense, motor diag (10 power contacts).",
     "RS Components", "261-5193", "Through-hole pogo",
     730, "2 weeks", "TO PROCURE",
     "RR_VT BOM item #17 – same part",
     "Qty = 15 power/GND TPs + 3 spare"),

    (12, "Pogo / Needle Bed", 32, "RECEP",
     "Spring-Loaded Test Pin Receptacle",
     "Receptacle to hold pogo pins in carrier block. Press-fit into machined or 3D-printed carrier.",
     "HARWIN", "261-5238", "Press-fit",
     660, "2 weeks", "TO PROCURE",
     "RR_VT BOM item #18 – RS 261-5238",
     "Qty = total 29 used + 3 spare"),

    (13, "Pogo / Needle Bed", 1, "CARRIER",
     "Pogo Pin Carrier Block (Top + Bottom Housing)",
     "Custom machined aluminium or PEEK block. Holds all 29 pogo pins in exact XY positions "
     "matching DUT test pad layout. Based on coordinates from drill file and assembly PDF.",
     "Custom / Machining", "N/A – custom design", "Machined",
     0, "2–3 weeks", "TO PROCURE",
     "DUT assembly drawings ASSY_TOP.pdf",
     "Design requires DUT PCB outline + test pad coordinates from Gerber"),

    (14, "Pogo / Needle Bed", 40, "HW_SCREW",
     "Screws & Nuts, M2/M3 assorted",
     "Hardware for carrier block assembly and alignment pin mounting.",
     "Generic / Misumi", "N/A", "Assorted",
     25, "1 week", "TO PROCURE",
     "RR_VT BOM item #21 – same category",
     ""),

    # ── SECTION ──────────────────────────────────────────────────────────────
    ("SEC", "3. FIXTURE HOUSING & MECHANICAL", "", "", "", "", "", "", "", "", "", "", "", ""),

    (15, "Fixture Housing", 1, "3D_BODY",
     "3D Printed Fixture Housing (Top + Bottom Frame)",
     "Custom 3D printed housing to hold the DUT PCB in the fixture. "
     "White PLA/ABS construction similar to existing manual fixture (see pcb_with_fixture.png). "
     "Includes PCB nest and guide channels for alignment pins.",
     "Custom / 3D Print", "N/A", "FDM 3D Print",
     0, "1 week", "CUSTOM/3D PRINT",
     "Hw_Setups/pcb_with_fixture.png",
     "Adapt from existing white manual fixture design"),

    (16, "Fixture Housing", 4, "ALIGN_PIN",
     "Alignment / Guide Pin, M3×20mm, stainless steel",
     "Precision alignment pins to locate DUT PCB in fixture. Derive position from "
     "PCB tooling holes in drill file (C652-10_Through.drl / C654-11 drill data).",
     "Misumi / RS Components", "STPB3-20 or equivalent", "Stainless",
     45, "1 week", "TO PROCURE",
     "DUT drill files: C652-10_Through.drl",
     "2 used for alignment, 2 spare"),

    (17, "Fixture Housing", 1, "BASE_PLATE",
     "Aluminium Base Plate (300×200×10mm)",
     "Fixture base plate in aluminium 6061. Mounts pogo carrier, fixture housing, "
     "actuator bracket, and cable strain relief.",
     "Custom / Machining", "N/A – custom design", "Machined Al",
     0, "2 weeks", "TO PROCURE",
     "Engineering design required",
     "Dimensions TBD after fixture housing and actuator are sized"),

    (18, "Fixture Housing", 1, "SENSOR_HOLDER",
     "3D Printed Sensor PCB Holder",
     "Holder bracket for sensor PCB, as visible in Hw_Setups/sensor_pcb_holder.png. "
     "Positions sensor PCB correctly relative to DUT.",
     "Custom / 3D Print", "N/A", "FDM 3D Print",
     0, "1 week", "CUSTOM/3D PRINT",
     "Hw_Setups/sensor_pcb_holder.png",
     "Replicate geometry from existing manual holder"),

    # ── SECTION ──────────────────────────────────────────────────────────────
    ("SEC", "4. ACTUATION SYSTEM", "", "", "", "", "", "", "", "", "", "", "", ""),

    (19, "Actuation", 2, "SERVO",
     "Servo Motor – 25 kg.cm, Metal Gear, 180°",
     "Digital servo motor for pressing pogo carrier against DUT PCB. "
     "25 kg.cm torque provides ample contact force for 29 pogo pins "
     "(est. 100g × 29 = 2.9 kg force required). Same spec as RR_VT NFC actuator.",
     "Pro-Range", "OT5325M", "Servo",
     1371, "1 week", "TO PROCURE",
     "RR_VT BOM item #10 – same part",
     "Qty=2: one for pogo actuation + one spare"),

    (20, "Actuation", 1, "SERVO_BRACKET",
     "3D Printed Servo Bracket / Mount",
     "Custom bracket to mount servo motor on base plate and link servo arm to pogo carrier.",
     "Custom / 3D Print", "N/A", "FDM 3D Print",
     0, "1 week", "CUSTOM/3D PRINT",
     "RR_VT BOM item #13 – same concept",
     "Adapt from RR_VT NFC servo bracket design"),

    (21, "Actuation", 1, "LIN_RAIL",
     "Linear Guide Rail (for pogo carrier vertical travel)",
     "Miniature linear guide rail, ~50mm travel. Constrains pogo carrier to vertical "
     "motion for consistent contact with DUT test points.",
     "Misumi / Generic", "Part NA (TBD)", "Linear rail",
     0, "2 weeks", "TO CONFIRM",
     "RR_VT BOM item #11 – same concept",
     "Length and size TBD after carrier block dimensions are set"),

    # ── SECTION ──────────────────────────────────────────────────────────────
    ("SEC", "5. RELAY / SWITCHING BOARD", "", "", "", "", "", "", "", "", "", "", "", ""),

    (22, "Relay Box", 12, "RELAY",
     "Relay – SPDT, 16A, 12V coil",
     "General purpose relay for switching test signals automatically (SG1/SG2 enable, "
     "motor drive enable, cap signals). Same part as RR_VT relay board.",
     "TE Connectivity Potter & Brumfield", "RT314012", "THT",
     473, "1 week", "TO PROCURE",
     "RR_VT BOM item #2 – same part",
     "12 relays: 6 signal channels × 2 for make/break switching"),

    (23, "Relay Box", 10, "TB_4P",
     "Terminal Block 4-pos, 5.08mm pitch",
     "4-position PCB screw terminal blocks for relay I/O wiring.",
     "Wurth Elektronik", "691241510004", "THT",
     207, "1 week", "TO PROCURE",
     "RR_VT BOM item #3 – same part",
     ""),

    (24, "Relay Box", 20, "DIODE",
     "Diode 1N4007, 1A, 1000V (flyback protection)",
     "Flyback diode across each relay coil to protect driver transistors.",
     "Vishay General Semiconductor", "1N4007-E3/54", "THT DO-204AL",
     52, "1 week", "TO PROCURE",
     "RR_VT BOM item #4 – same part",
     "One per relay coil"),

    (25, "Relay Box", 1, "3D_RELAY_BOX",
     "3D Printed Relay Box Enclosure",
     "Custom enclosure for relay PCB, similar to RR_VT relay box.",
     "Custom / 3D Print", "N/A", "FDM 3D Print",
     0, "1 week", "CUSTOM/3D PRINT",
     "RR_VT BOM item #5",
     ""),

    # ── SECTION ──────────────────────────────────────────────────────────────
    ("SEC", "6. EOS (ELECTRONICS ON SETUP) – SIGNAL CONDITIONING", "", "", "", "", "", "", "", "", "", "", "", ""),

    (26, "EOS", 5, "TB_3P",
     "Terminal Block 3-pos, 5.08mm pitch",
     "3-position screw terminals for EOS power distribution (12V, 3.3V, GND).",
     "Weidmuller", "1760520000", "THT",
     102, "1 week", "TO PROCURE",
     "RR_VT BOM item #6 – same part",
     ""),

    (27, "EOS", 3, "DCDC",
     "DC-DC Converter 3.3V, 3.3W (TSR 1-2433)",
     "Non-isolated switching regulator to generate 3.3V for EOS logic from 12V fixture supply. "
     "Provides 3V3 test point reference for TP113.",
     "Traco Power", "TSR 1-2433", "THT SIP3",
     525, "1 week", "TO PROCURE",
     "RR_VT BOM item #7 – same part",
     ""),

    (28, "EOS", 20, "RES_560R",
     "Resistor 560 Ω, 1%, 1/4W",
     "EOS current-limiting and pull-up resistors.",
     "Yageo", "MFR-25FRF52-560R", "THT Axial",
     9, "1 week", "TO PROCURE",
     "RR_VT BOM item #8 – same part",
     ""),

    (29, "EOS", 1, "3D_EOS_BOX",
     "3D Printed EOS Enclosure",
     "Custom enclosure for EOS PCB.",
     "Custom / 3D Print", "N/A", "FDM 3D Print",
     0, "1 week", "CUSTOM/3D PRINT",
     "RR_VT BOM item #9",
     ""),

    # ── SECTION ──────────────────────────────────────────────────────────────
    ("SEC", "7. TEST INSTRUMENTS", "", "", "", "", "", "", "", "", "", "", "", ""),

    (30, "Instruments", 1, "PSU",
     "Programmable DC Power Supply – KIKUSUI PWR401L",
     "40V / 1A programmable DC power supply. Confirmed in use via How_To_Debugg.xlsx. "
     "Remote control via USB (USBTMC / PyVISA). Provides 12V / 3.8V supply to DUT.",
     "Kikusui", "PWR401L", "Bench instrument",
     0, "—", "CONFIRMED",
     "How_To_Debugg.xlsx – KIKUSUI PWR401L SETUP STEPS sheet",
     "Already in use. Add to BOM for traceability. Confirm qty per test station."),

    (31, "Instruments", 1, "TRACE32",
     "JTAG Debugger – Lauterbach Trace32 (CombiProbe / µTrace)",
     "Lauterbach Trace32 USB-connected JTAG/SWD debugger. Confirmed via config.t32 "
     "(PBI=USB). Connects to DUT via 10-pin SWD header (SWD_DATA, SWD_CLK, RESET).",
     "Lauterbach", "LA-3505 CombiProbe or µTrace", "USB instrument",
     0, "—", "CONFIRMED",
     "config.t32: PBI=USB; Hw_Setups/debugger_connection.png",
     "Already in use. Confirm exact model for BOM. One unit per station."),

    (32, "Instruments", 1, "CAN_IF",
     "CAN Bus Interface – PEAK PCAN-USB",
     "USB CAN interface for CAN-H / CAN-L communication with DUT. "
     "DB9 connector visible on fixture PCB (motor/CAN lines). "
     "Connects via DB9 cable to fixture PCB CAN terminals.",
     "PEAK System", "IPEH-002022 (PCAN-USB)", "USB dongle",
     0, "—", "TO CONFIRM",
     "Fixture PCB Connection sheet: DB9 conn; fixture_sensor_pcb_connection1.png",
     "Confirm exact model (PCAN-USB or Vector). Part number to be verified."),

    (33, "Instruments", 1, "LIN_IF",
     "LIN Bus Interface – USB LIN Adapter",
     "USB LIN interface for LIN bus communication with DUT. "
     "LIN connector documented in Connection sheet (item 8).",
     "PEAK / Kvaser", "PLIN-USB or equivalent", "USB dongle",
     0, "—", "TO CONFIRM",
     "Connection sheet: LIN connector (item 8)",
     "Confirm model used in current setup. Add part number."),

    (34, "Instruments", 1, "BARCODE",
     "Barcode / Datamatrix Reader",
     "USB barcode scanner for DUT serial number identification. "
     "Already integrated in automation software (Barcode_Reader folder in project).",
     "TBD (existing unit)", "TBD", "USB HID",
     0, "—", "TO CONFIRM",
     "Continous_Developement/Nfc_Version/Barcode_Reader/",
     "Confirm scanner model from existing lab setup. Add mounting bracket to BOM."),

    # ── SECTION ──────────────────────────────────────────────────────────────
    ("SEC", "8. NFC SUBSYSTEM (NFC variants only)", "", "", "", "", "", "", "", "", "", "", "", ""),

    (35, "NFC", 2, "NFC_SERVO",
     "Servo Motor – 25 kg.cm, Metal Gear (NFC card positioner)",
     "Servo motor to position NFC phone/card reader over DUT NFC antenna. "
     "Only required for NFC LH and NFC RH variants.",
     "Pro-Range", "OT5325M", "Servo",
     1371, "1 week", "TO PROCURE",
     "RR_VT BOM item #10 – same part",
     "Only needed if NFC variants are tested on this fixture"),

    (36, "NFC", 1, "NFC_HOLDER",
     "NFC Card / Smartphone Holder",
     "Clamp holder for NFC reference card or smartphone used in NFC antenna test.",
     "SmallRig", "SmallRig clamp or equivalent", "Mechanical",
     2300, "2 weeks", "TO PROCURE",
     "RR_VT BOM item #12 – same part",
     "Only for NFC variants"),

    (37, "NFC", 1, "3D_NFC_BRACKET",
     "3D Printed NFC Servo Bracket",
     "Custom bracket to mount NFC servo on fixture.",
     "Custom / 3D Print", "N/A", "FDM 3D Print",
     0, "1 week", "CUSTOM/3D PRINT",
     "RR_VT BOM item #13",
     "Only for NFC variants"),

    # ── SECTION ──────────────────────────────────────────────────────────────
    ("SEC", "9. SAFETY", "", "", "", "", "", "", "", "", "", "", "", ""),

    (38, "Safety", 1, "ESTOP",
     "Emergency Stop Button (Mushroom head, panel mount)",
     "IEC 60947-5-5 compliant E-stop. Required for servo-actuated fixture. "
     "Normally closed contact, panel mount.",
     "Schneider / Eaton", "ZB5AS844 or M22-PV/KC11", "Panel mount",
     850, "1 week", "TO PROCURE",
     "Safety requirement for powered actuation",
     "Wire to interrupt servo power supply"),

    (39, "Safety", 1, "PRESENCE_SENSOR",
     "PCB Presence Sensor – Optical Fork Sensor",
     "Detects when DUT PCB is loaded in fixture before actuation. "
     "Prevents pogo contact without DUT present.",
     "Omron / Panasonic", "EE-SX672 or PM-T45", "Through-beam",
     420, "1 week", "TO PROCURE",
     "Safety requirement",
     "NPN output, 5V supply, mount in fixture housing slot"),

    (40, "Safety", 2, "POS_SENSOR",
     "Actuator Position Sensor – Micro Switch / Reed",
     "2 sensors per actuator: OPEN position + CLOSED (contacted) position. "
     "Used by software for safe-state confirmation.",
     "Omron", "SS-5GL2 or equivalent micro-switch", "PCB/bracket mount",
     180, "1 week", "TO PROCURE",
     "Safety requirement for servo actuator feedback",
     "Qty=2 per fixture (open + closed detection)"),

    # ── SECTION ──────────────────────────────────────────────────────────────
    ("SEC", "10. CABLE HARNESS & WIRING", "", "", "", "", "", "", "", "", "", "", "", ""),

    (41, "Harness", 4, "WIRE_24AWG",
     "Wire 24 AWG, multi-colour (per metre)",
     "General purpose fixture wiring for power connections (12V, GND).",
     "Generic", "24AWG hook-up wire", "Single core",
     1950, "1 week", "TO PROCURE",
     "RR_VT BOM item #23 – same spec",
     "Approx. 4m total; colours: red, black, yellow, blue"),

    (42, "Harness", 5, "WIRE_28AWG_SH",
     "Shielded Wire 28 AWG (per metre)",
     "Shielded wire for CAN-H/L and LIN bus lines to reduce noise. "
     "Twisted pair shielded.",
     "Tensility International Corp", "30-01035", "Shielded",
     360, "1 week", "TO PROCURE",
     "RR_VT BOM item #24 – same part",
     "Approx. 5m total for CAN and LIN harness runs"),

    (43, "Harness", 2, "WIRE_30AWG",
     "Wire 30 AWG (per metre)",
     "Fine gauge wire for low-current signal connections (SWD, SG signals).",
     "Jonard Tools", "R30G-0100", "Single core",
     2350, "1 week", "TO PROCURE",
     "RR_VT BOM item #25 – same part",
     "Approx. 2m total for JTAG/SWD harness"),

    (44, "Harness", 2, "HEAT_SHRINK",
     "Heat Shrink Tubing Kit (assorted)",
     "Heat shrink tubing for wire termination protection.",
     "Generic / HellermannTyton", "N/A", "Assorted",
     250, "1 week", "TO PROCURE",
     "General wiring practice",
     ""),

    # ── SECTION ──────────────────────────────────────────────────────────────
    ("SEC", "11. MISCELLANEOUS / HARDWARE", "", "", "", "", "", "", "", "", "", "", "", ""),

    (45, "Misc", 1, "DIN_RAIL",
     "DIN Rail 35mm × 200mm",
     "Standard DIN rail for mounting relay board, EOS board inside fixture cabinet or base plate.",
     "Phoenix Contact / Schneider", "NS 35/7.5", "DIN rail",
     150, "1 week", "TO PROCURE",
     "Standard component",
     ""),

    (46, "Misc", 10, "STANDOFF",
     "PCB Standoffs M3×10mm, nylon",
     "For mounting fixture PCB, relay PCB, EOS PCB to base plate.",
     "Wurth Elektronik / Generic", "N/A", "Nylon",
     30, "1 week", "TO PROCURE",
     "Standard component",
     ""),

    (47, "Misc", 1, "LABEL_SET",
     "Cable Label Set",
     "Self-laminating cable labels for wire identification on all harness cables.",
     "Brady / HellermannTyton", "N/A", "Labels",
     200, "1 week", "TO PROCURE",
     "Good wiring practice",
     ""),

    (48, "Misc", 1, "VELCRO",
     "Velcro Cable Ties (pack of 20)",
     "For cable management inside fixture.",
     "Generic", "N/A", "Accessory",
     80, "1 week", "TO PROCURE",
     "General",
     ""),
]

# ─── Write BOM rows ──────────────────────────────────────────────────────────
row = 7
total_col = 11   # column K = Total

for entry in BOM:
    if entry[0] == "SEC":
        ws.row_dimensions[row].height = 18
        # Merge all columns for section header
        ws.merge_cells(f"A{row}:O{row}")
        c = ws[f"A{row}"]
        c.value = f"  ▶  {entry[1]}"
        c.fill = fill(LBLUE)
        c.font = Font(bold=True, color=NAVY, size=10, name="Calibri")
        c.alignment = Alignment(horizontal="left", vertical="center")
        row += 1
        continue

    item, subsys, qty, ref, pname, desc, mfr, ordno, pkg, uprice, leadtime, status, source, notes = entry

    ws.row_dimensions[row].height = 55
    alt = ALT1 if row % 2 == 0 else ALT2
    s_bg, s_fg = STATUS_FMT.get(status, (GBKG2, GRAY))

    values = [item, subsys, qty, ref, pname, desc, mfr, ordno, pkg,
              uprice,
              f"=C{row}*J{row}" if uprice else 0,
              leadtime, status, source, notes]

    for ci, val in enumerate(values, 1):
        c = ws.cell(row=row, column=ci, value=val)
        c.border = thin_border()
        c.alignment = wrap()

        if ci == 1:   # Item number
            c.fill = fill(BLUE); c.font = font(bold=True, color=WHITE, size=9)
            c.alignment = wrap("center")
        elif ci == 13:  # Status
            c.fill = fill(s_bg); c.font = font(bold=True, color=s_fg, size=9)
            c.alignment = wrap("center")
        elif ci == 3:   # Qty
            c.alignment = wrap("center")
            c.fill = fill(alt); c.font = font(size=9)
        elif ci in (10, 11):  # Prices
            c.fill = fill(alt); c.font = font(size=9)
            c.alignment = wrap("right")
            c.number_format = '#,##0'
        else:
            c.fill = fill(alt); c.font = font(size=9)
    row += 1

# ── Grand total row ──
ws.row_dimensions[row].height = 22
for ci in range(1, 16):
    c = ws.cell(row=row, column=ci)
    c.fill = fill(NAVY); c.border = thin_border(NAVY)
gt_label = ws.cell(row=row, column=1, value="GRAND TOTAL")
gt_label.font = font(bold=True, color=WHITE, size=10)
gt_label.alignment = wrap("center")
ws.merge_cells(f"A{row}:J{row}")

gt_val = ws.cell(row=row, column=11, value=f"=SUM(K7:K{row-1})")
gt_val.font = font(bold=True, color=WHITE, size=10)
gt_val.number_format = '#,##0'
gt_val.alignment = wrap("right")

# ── Notes row below total ──
row += 2
note_text = ("NOTE: Prices shown in INR (approx). Qty marked 0 = custom/in-house item (no purchase cost). "
             "Items marked 'TO CONFIRM' require part number verification from existing lab setup before ordering. "
             "Items marked 'TO PROCURE' are new purchases required for this fixture. "
             "Custom/3D Print items require design files to be created. "
             "DUT variants: C652-10 (RH) and C654-11 (LH) share the same fixture PCB and pogo carrier design.")
ws.merge_cells(f"A{row}:O{row}")
c = ws[f"A{row}"]
c.value = note_text
c.font = font(italic=True, size=8, color="595959")
c.alignment = wrap("left")
ws.row_dimensions[row].height = 45

# ════════════════════════════════════════════════════════════════════════════
# SHEET 2 — SIGNAL / TEST POINT MAP
# ════════════════════════════════════════════════════════════════════════════
ws2 = wb.create_sheet("Test Point Signal Map")
ws2.sheet_view.showGridLines = False

col_w(ws2, "A", 6); col_w(ws2, "B", 8); col_w(ws2, "C", 14); col_w(ws2, "D", 22)
col_w(ws2, "E", 18); col_w(ws2, "F", 16); col_w(ws2, "G", 14); col_w(ws2, "H", 30)

ws2.row_dimensions[1].height = 38
merge(ws2, "A1:H1",
      "SmartBU DUT – Test Point to Fixture Pin Mapping  (from Connection Sheet)",
      NAVY, WHITE, sz=13)

hdr2 = ["#", "IDC Pin\n/ Conn", "Test Point\n(DUT)", "Signal Name",
        "Signal Type", "Pogo Pin Type", "BOM Item #", "Notes"]
ws2.row_dimensions[3].height = 28
for ci, h in enumerate(hdr2, 1):
    c = ws2.cell(row=3, column=ci, value=h)
    c.fill = fill(BLUE); c.font = font(bold=True, color=WHITE, size=9)
    c.alignment = wrap("center"); c.border = thin_border(NAVY)

TP_DATA = [
    (1,  "PIN 1",  "TP100",  "12V Supply",           "Power",   "3A (item 11)", 11, "Main DUT supply voltage"),
    (2,  "PIN 2",  "TP101",  "GND",                   "Power",   "3A (item 11)", 11, "Main ground"),
    (3,  "PIN 3",  "TP113",  "3V3",                   "Power",   "3A (item 11)", 11, "3.3V internal rail"),
    (4,  "PIN 4",  "TP123",  "3V8",                   "Power",   "3A (item 11)", 11, "3.8V regulated rail"),
    (5,  "PIN 5",  "TP307",  "SG Power Switch",       "Signal",  "1.5A (item 10)", 10, "Sensor group power switch"),
    (6,  "PIN 6",  "TP310",  "SG1 Op-Amp Output",    "Signal",  "1.5A (item 10)", 10, "Displacement sensor 1 output"),
    (7,  "PIN 7",  "TP311",  "SG1 IN1+ Input",       "Signal",  "1.5A (item 10)", 10, "SG1 differential + input"),
    (8,  "PIN 8",  "TP312",  "SG1 IN1- Input",       "Signal",  "1.5A (item 10)", 10, "SG1 differential - input"),
    (9,  "PIN 9",  "TP321",  "SG2 Op-Amp Output",    "Signal",  "1.5A (item 10)", 10, "Displacement sensor 2 output"),
    (10, "PIN 10", "TP322",  "SG2 IN2+ Input",       "Signal",  "1.5A (item 10)", 10, "SG2 differential + input"),
    (11, "PIN 11", "TP324",  "SG2 IN2- Input",       "Signal",  "1.5A (item 10)", 10, "SG2 differential - input"),
    (12, "PIN 12", "TP407",  "AI_MOTOR_VISEN",        "Analog",  "1.5A (item 10)", 10, "Motor voltage sense feedback"),
    (13, "DB9",    "DRV_OUT_A", "Actuator Drive A",  "Power",   "3A (item 11)", 11, "Motor H-bridge output A (via DB9)"),
    (14, "DB9",    "DRV_OUT_B", "Actuator Drive B",  "Power",   "3A (item 11)", 11, "Motor H-bridge output B (via DB9)"),
    (15, "PIN 15", "TP414",  "AI_MOTOR_DIAG",         "Signal",  "1.5A (item 10)", 10, "Motor driver diagnostic"),
    (16, "PIN 16", "TP503",  "Cap Unlock Pin",        "Signal",  "1.5A (item 10)", 10, "Capacitive sensor unlock"),
    (17, "PIN 17", "TP505",  "Cap Unlock Reference",  "Signal",  "1.5A (item 10)", 10, "Cap sensor reference"),
    (18, "PIN 18", "TP507",  "Cap Proximity",         "Signal",  "1.5A (item 10)", 10, "Proximity sensor signal"),
    (19, "PIN 19", "TP509",  "Cap Proximity Ref",     "Signal",  "1.5A (item 10)", 10, "Proximity reference"),
    (20, "PIN 20", "TP511",  "Cap Lock",              "Signal",  "1.5A (item 10)", 10, "Cap lock signal"),
    (21, "PIN 21", "TP602",  "LED Out Pin",           "Signal",  "1.5A (item 10)", 10, "LED driver output"),
    (22, "PIN 22", "TP612",  "AI_EOS_DIAG",           "Signal",  "1.5A (item 10)", 10, "EOS diagnostic line"),
    (23, "PIN 23", "TP613",  "EOS_Out",               "Signal",  "1.5A (item 10)", 10, "EOS output"),
    (24, "PIN 24", "TP614",  "IPB GND",               "Power",   "3A (item 11)", 11, "Intelligent power bus ground"),
    (25, "PIN 25", "TP104",  "GND",                   "Power",   "3A (item 11)", 11, "Ground reference"),
    (26, "PIN 26", "TP106",  "GND",                   "Power",   "3A (item 11)", 11, "Ground reference"),
    (27, "PIN 27", "TP201",  "SWD_DATA",              "Debug",   "1.5A (item 10)", 10, "SWD data line (JTAG/SWD)"),
    (28, "PIN 28", "TP202",  "SWD_CLK",               "Debug",   "1.5A (item 10)", 10, "SWD clock line"),
    (29, "PIN 29", "TP200",  "RESET",                 "Debug",   "1.5A (item 10)", 10, "MCU reset signal"),
]

TYPE_COLORS = {
    "Power":  ("FCE4D6", "C55A11"),
    "Signal": ("E2EFDA", "375623"),
    "Analog": ("FFF2CC", "7F6000"),
    "Debug":  ("D6E4F0", "1F4E79"),
}

for r_idx, td in enumerate(TP_DATA, 4):
    ws2.row_dimensions[r_idx].height = 22
    num, pin, tp, signame, sigtype, pogotype, bom_item, notes = td
    bg, fg = TYPE_COLORS.get(sigtype, (GBKG2, GRAY))
    for ci, val in enumerate([num, pin, tp, signame, sigtype, pogotype, bom_item, notes], 1):
        c = ws2.cell(row=r_idx, column=ci, value=val)
        c.border = thin_border()
        c.alignment = wrap("center" if ci <= 3 else "left")
        c.fill = fill(bg if ci >= 4 else ALT1)
        c.font = font(size=9, bold=(ci == 5), color=fg if ci == 5 else "000000")

# Summary stats below table
summary_row = 4 + len(TP_DATA) + 2
merge(ws2, f"A{summary_row}:H{summary_row}",
      f"SUMMARY:  Total test points = {len(TP_DATA)}  |  "
      f"Power/GND contacts = {sum(1 for t in TP_DATA if t[4]=='Power')}  |  "
      f"Signal contacts = {sum(1 for t in TP_DATA if t[4]=='Signal')}  |  "
      f"Analog contacts = {sum(1 for t in TP_DATA if t[4]=='Analog')}  |  "
      f"Debug (SWD/JTAG) contacts = {sum(1 for t in TP_DATA if t[4]=='Debug')}",
      LBLUE, NAVY, sz=10, bold=True, h="left")

# ════════════════════════════════════════════════════════════════════════════
# SHEET 3 — DUT CONNECTOR REFERENCE
# ════════════════════════════════════════════════════════════════════════════
ws3 = wb.create_sheet("DUT Connector Reference")
ws3.sheet_view.showGridLines = False
col_w(ws3, "A", 6); col_w(ws3, "B", 22); col_w(ws3, "C", 20); col_w(ws3, "D", 32)
col_w(ws3, "E", 18); col_w(ws3, "F", 20); col_w(ws3, "G", 20); col_w(ws3, "H", 30)

ws3.row_dimensions[1].height = 38
merge(ws3, "A1:H1",
      "SmartBU DUT – Connector & Key IC Reference (extracted from DUT BOM)",
      NAVY, WHITE, sz=13)

hdr3 = ["#", "PCB Variant", "Ref Des", "Part Name",
        "Manufacturer", "Ordering No.", "Notes", "Relevance to Fixture"]
ws3.row_dimensions[3].height = 22
for ci, h in enumerate(hdr3, 1):
    c = ws3.cell(row=3, column=ci, value=h)
    c.fill = fill(BLUE); c.font = font(bold=True, color=WHITE, size=9)
    c.alignment = wrap("center"); c.border = thin_border(NAVY)

dut_parts = [
    (1,  "All variants",  "X600",  "Flex Connector, 0.50mm Pitch, 17 positions",
     "Amphenol FCI", "F300-1B7H1-11017-E100",
     "Qty=1 per DUT. Only on-board connector.",
     "FPC flex cable needed to connect DUT to fixture PCB. Mating connector required."),
    (2,  "NFC RH/LH",     "U700",  "High Power NFC Frontend IC",
     "NXP Semiconductors", "NCJ3321AHF/00100S",
     "Present only in NFC variants (36O, 38P).",
     "NFC coil must be positioned over U700 antenna for NFC tests"),
    (3,  "All variants",  "U200",  "PSoC 4100S Max Microcontroller",
     "Infineon", "CY8C4148AZE-S595",
     "Main MCU. SWD interface (TP201/202/200) used for Trace32.",
     "JTAG/SWD pogo pins must reliably contact TP200/201/202"),
    (4,  "All variants",  "U201",  "CAN Transceiver (self-supplied, sleep mode)",
     "NXP Semiconductors", "UJA1162ATK/0Z",
     "Integrated supply. CAN-H/L lines routed to DB9.",
     "CAN interface (PCAN-USB) connects via DB9 on fixture PCB"),
    (5,  "All variants",  "U101",  "LIN Transceiver",
     "NXP Semiconductors", "TJA1029TK/20/1J",
     "LIN bus interface on DUT.",
     "LIN connection via 3-pin terminal on fixture PCB"),
    (6,  "All variants",  "U400",  "H-Bridge Motor Driver 40V/5A",
     "MPS", "MPQ6612AGLE-AEC1-Z",
     "Motor driver. DRV_OUT_A/B go to DB9 connector.",
     "High-current pogo pins needed for motor output test points (3A class)"),
    (7,  "All variants",  "U102",  "Synchronous Step-Down Converter",
     "MPS", "MPQ4324GDE-1044-AEC1",
     "DUT internal power supply.",
     "3.8V rail monitored via TP123"),
    (8,  "All variants",  "PCB",   "PC-Board C652-10 (RH) / C654-11 (LH)",
     "MinebeaMitsumi", "132309000037J / 132309000039K",
     "2 PCB variants – same connector/test point layout.",
     "Fixture must accommodate both C652-10 (RH) and C654-11 (LH) PCB outlines"),
]

for r_idx, dp in enumerate(dut_parts, 4):
    ws3.row_dimensions[r_idx].height = 40
    alt = ALT1 if r_idx % 2 == 0 else ALT2
    for ci, val in enumerate(dp, 1):
        c = ws3.cell(row=r_idx, column=ci, value=val)
        c.border = thin_border()
        c.alignment = wrap("center" if ci <= 3 else "left")
        c.fill = fill(alt); c.font = font(size=9)

# ════════════════════════════════════════════════════════════════════════════
# SHEET 4 — LEGEND
# ════════════════════════════════════════════════════════════════════════════
ws4 = wb.create_sheet("Legend")
ws4.sheet_view.showGridLines = False
col_w(ws4, "A", 6); col_w(ws4, "B", 22); col_w(ws4, "C", 55)

ws4.row_dimensions[1].height = 34
merge(ws4, "A1:C1", "Legend", NAVY, WHITE, sz=13)

legend = [
    ("STATUS", "", ""),
    ("CONFIRMED",       "✓", "Item already in use in the lab. Add to BOM for traceability."),
    ("TO CONFIRM",      "~", "Item likely exists; verify exact model/part number before ordering."),
    ("TO PROCURE",      "✗", "New item – must be purchased."),
    ("CUSTOM/3D PRINT", "⬡", "No purchase cost – requires design + in-house fabrication."),
    ("IN-HOUSE",        "◆", "Available in-house; no purchase needed."),
    ("SIGNAL TYPE (Test Point Map)", "", ""),
    ("Power",  "●", "High-current contact: 12V, GND, motor lines → use 3A pogo pins (item 11)"),
    ("Signal", "●", "Logic-level signal contact → use 1.5A pogo pins (item 10)"),
    ("Analog", "●", "Analog measurement contact → use 1.5A pogo pins (item 10)"),
    ("Debug",  "●", "SWD/JTAG debug lines → use 1.5A pogo pins (item 10)"),
]

l_fills = {
    "CONFIRMED":              (GBKG,  GREEN),
    "TO CONFIRM":             (ABKG,  AMBER),
    "TO PROCURE":             (RBKG,  RED),
    "CUSTOM/3D PRINT":        ("EAD1DC", "7C2137"),
    "IN-HOUSE":               (GBKG,  GREEN),
    "Power":                  ("FCE4D6", "C55A11"),
    "Signal":                 ("E2EFDA", "375623"),
    "Analog":                 ("FFF2CC", "7F6000"),
    "Debug":                  ("D6E4F0", "1F4E79"),
    "STATUS":                 (LBLUE,  NAVY),
    "SIGNAL TYPE (Test Point Map)": (LBLUE, NAVY),
}

lr = 3
for lbl, sym, desc in legend:
    is_hdr = lbl in ("STATUS", "SIGNAL TYPE (Test Point Map)")
    ws4.row_dimensions[lr].height = 20 if is_hdr else 22
    if is_hdr:
        ws4.merge_cells(f"A{lr}:C{lr}")
        c = ws4[f"A{lr}"]
        c.value = f"  {lbl}"; c.fill = fill(LBLUE)
        c.font = Font(bold=True, color=NAVY, size=10, name="Calibri")
        c.alignment = Alignment(horizontal="left", vertical="center")
        lr += 1; continue
    bg, fg = l_fills.get(lbl, (GBKG2, GRAY))
    for ci, v in enumerate([sym, lbl, desc], 1):
        c = ws4.cell(row=lr, column=ci, value=v)
        c.border = thin_border(); c.fill = fill(bg)
        c.font = font(bold=(ci == 2), color=fg, size=10)
        c.alignment = wrap("center" if ci < 3 else "left")
    lr += 1

# ─── SAVE ─────────────────────────────────────────────────────────────────────
out = r"C:\UShin\Testbench_gui_Charan\Continous_Developement\BOM_SmartBU_Automation\SmartBU_Automation_Fixture_BOM_Rev1.0.xlsx"
wb.save(out)
print(f"Saved: {out}")
