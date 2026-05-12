"""
Generate: Conveyor_AutoLoader_Fixture_BOM.xlsx
Covers all subsystems of the conveyor-fed automatic PCB test station.

System overview (from reference images):
  - In-line conveyor transport (PCB arrives → stops at station)
  - Pneumatic press (top plate + blue columns) closes onto PCB
  - Pogo-pin / needle bed makes contact with DUT test points
  - Multi-pin connectors plug in automatically (via actuator)
  - Barcode scanner identifies each PCB
  - Functional test runs (T32 / JLink + CAN / LIN / Motor / NFC / SG / EOS)
  - Pass / Fail output → reject gate or light stack
  - MySQL logging + HTML report per unit

Engineer : Charan Singh
Project  : SmartBU In-Line Automated Test Station
Date     : 11.05.2026
Rev      : 1.0
"""

import openpyxl
from openpyxl.styles import PatternFill, Font, Alignment, Border, Side
from openpyxl.utils import get_column_letter

# ─── Helpers ─────────────────────────────────────────────────────────────────
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

# ─── Colours ──────────────────────────────────────────────────────────────────
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

STATUS_FMT = {
    "CONFIRMED":       (GBKG,  GREEN),
    "TO CONFIRM":      (ABKG,  AMBER),
    "TO PROCURE":      (RBKG,  RED),
    "CUSTOM/MACHINED": ("EAD1DC", "7C2137"),
    "IN-HOUSE":        (GBKG,  GREEN),
}

# ─── Workbook ─────────────────────────────────────────────────────────────────
wb = openpyxl.Workbook()

# ═════════════════════════════════════════════════════════════════════════════
# SHEET 1 — BOM MAIN
# ═════════════════════════════════════════════════════════════════════════════
ws = wb.active
ws.title = "Conveyor Fixture BOM"
ws.sheet_view.showGridLines = False

# Column widths: A=item, B=subsystem, C=qty, D=ref, E=part name,
#                F=description, G=manufacturer, H=ordering no., I=package,
#                J=unit price (INR), K=total, L=lead time, M=status,
#                N=source, O=notes
widths = [5, 22, 6, 14, 30, 46, 22, 22, 14, 14, 14, 14, 16, 22, 34]
for i, w in enumerate(widths, 1):
    col_w(ws, i, w)

# ── Title block ───────────────────────────────────────────────────────────────
ws.row_dimensions[1].height = 44
for r in range(2, 7):
    ws.row_dimensions[r].height = 16

merge(ws, "A1:O1",
      "BILL OF MATERIALS  —  Conveyor-Fed In-Line Automatic PCB Test Station  (SmartBU / XNF I460)",
      NAVY, WHITE, sz=14, bold=True)

meta = [
    ("A2", "Date:",        "C2", "11.05.2026"),
    ("A3", "Engineer:",    "C3", "Charan Singh"),
    ("A4", "Project:",     "C4", "SmartBU In-Line Automated Test Station  |  BMW MAE"),
    ("A5", "Document:",    "C5", "Conveyor_AutoLoader_Fixture_BOM_Rev1.0"),
    ("A6", "Variants:",    "C6", "NFC LH  /  NFC RH  /  Non-NFC LH  /  Non-NFC RH"),
]
for lc, lt, vc, vt in meta:
    c = ws[lc]; c.value = lt; c.font = font(bold=True, size=9)
    c = ws[vc]; c.value = vt; c.font = font(size=9)

# ── Column headers ─────────────────────────────────────────────────────────────
HEADERS = [
    "Item", "Subsystem", "Qty", "Ref.",
    "Part Name", "Description / Value",
    "Manufacturer", "Ordering No.", "Package / Form",
    "Unit Price\n(INR ~)", "Total\n(INR ~)",
    "Lead Time", "Status",
    "Source / Datasheet", "Notes / Remarks"
]
ws.row_dimensions[7].height = 30
for ci, h in enumerate(HEADERS, 1):
    c = ws.cell(row=7, column=ci, value=h)
    c.fill = fill(BLUE)
    c.font = font(bold=True, color=WHITE, size=9)
    c.alignment = wrap("center")
    c.border = thin_border(NAVY)

ws.freeze_panes = "A8"

# ─── BOM DATA ─────────────────────────────────────────────────────────────────
# Columns: item, subsystem, qty, ref, part_name, description,
#          manufacturer, order_no, package, unit_price(INR),
#          lead_time, status, source, notes
# (unit_price=0 for existing/confirmed items with no new purchase needed)

BOM = [

    # ══════════════════════════════════════════════════════════════════════════
    ("SEC", "1. CONVEYOR TRANSPORT SYSTEM"),
    # ══════════════════════════════════════════════════════════════════════════

    (1, "Conveyor", 1, "CONV1",
     "Belt Conveyor Module – 600 mm × 200 mm",
     "Single-lane flat belt conveyor module. Width 200 mm (for PCB up to 180 mm wide). "
     "Length ~600 mm per station. Aluminium frame, PVC/PU belt, adjustable speed. "
     "Integrated drive motor (24VDC). Speed 0–15 m/min adjustable.",
     "Dorner / mk North America / Bosch Rexroth",
     "Dorner 2200 Series or mk TKU-040 or equivalent",
     "Module (assembled)",
     85000, "4–6 weeks", "TO PROCURE",
     "Dorner 2200 series: dornerconveyors.com; mk: mktechgroup.com",
     "One module per test station. Include upstream buffer section if multi-station."),

    (2, "Conveyor", 1, "CONV_DRV",
     "Conveyor Drive Controller – 24VDC Motor Driver",
     "DC motor controller for conveyor belt drive. PWM speed control, "
     "direction control, brake output. Compatible with PLC digital I/O start/stop signal.",
     "Cytron / Oriental Motor",
     "MD30C or BLHM230KC or equivalent",
     "DIN rail / PCB",
     4500, "1–2 weeks", "TO PROCURE",
     "cytron.io; orientalmotor.com",
     "Controlled by PLC DO: START / STOP / DIRECTION signals"),

    (3, "Conveyor", 2, "CONV_STOP",
     "Pneumatic PCB Stop Cylinder (Stopper Pin)",
     "Pneumatic stopper pin that rises to halt PCB at test position. "
     "Bore Ø10 mm, stroke 25 mm, double-acting. Stainless steel pin tip. "
     "Retracts to release PCB after test.",
     "Festo / SMC",
     "Festo ADVU-10-25-PA or SMC CJ2B10-25 or equivalent",
     "Pneumatic cylinder",
     3200, "2–3 weeks", "TO PROCURE",
     "festo.com / smcworld.com",
     "Qty=2: one entry stopper + one exit gate. Actuated by 5/2 solenoid valve (item 13)."),

    (4, "Conveyor", 2, "PCB_SENSOR",
     "PCB Presence / Position Sensor – Photoelectric Diffuse",
     "Diffuse-reflective photoelectric sensor to detect PCB arrival at test station. "
     "Detection range 5–100 mm, NPN output, 24VDC. Teaches on dark PCB substrate.",
     "Omron / Sick",
     "Omron E3Z-D61 or Sick WTB4S-3P2361 or equivalent",
     "M18 barrel, IP67",
     2800, "1–2 weeks", "TO PROCURE",
     "omron.com / sick.com",
     "Qty=2: one at entry (PCB-arrived) + one at press station (PCB-centred). NPN, 24V."),

    (5, "Conveyor", 2, "CONV_GUIDE",
     "PCB Side Guide Rail (adjustable width)",
     "Adjustable aluminium side guides to keep PCB centred on conveyor. "
     "Slot-mounted, adjustable up to 250 mm width. UHMW-PE low-friction strip on contact face.",
     "Bosch Rexroth / mk / Custom",
     "Rexroth 3842547712 or equivalent",
     "Extruded Al profile",
     1800, "2–3 weeks", "TO PROCURE",
     "boschrexroth.com",
     "Qty=2 (left + right). Adjust to PCB width at installation."),

    # ══════════════════════════════════════════════════════════════════════════
    ("SEC", "2. PNEUMATIC PRESS (FIXTURE CLOSURE SYSTEM)"),
    # ══════════════════════════════════════════════════════════════════════════

    (6, "Pneumatic Press", 1, "PRESS_CYL",
     "Pneumatic Press Cylinder – Bore Ø80mm, Stroke 80mm",
     "ISO 15552 double-acting round/square bore cylinder. Provides downward closing force "
     "for pogo-pin top plate. Ø80mm bore gives ~500N force at 5 bar. "
     "Stroke 80mm for top plate travel from open to contact position. "
     "As visible in reference images (vertical stroke, blue support columns).",
     "Festo / SMC / Parker",
     "Festo ADVU-80-80-P-A or SMC CDQMB80TF-80 or equivalent",
     "ISO 15552 cylinder",
     8500, "2–3 weeks", "TO PROCURE",
     "festo.com / smcworld.com",
     "Single cylinder at centre of press plate. Adjust stroke via end cushions."),

    (7, "Pneumatic Press", 4, "PRESS_GUIDE",
     "Linear Guide Column – Ø20mm, L=150mm, Hard Chrome Steel",
     "Precision guide columns constraining top plate to pure vertical travel. "
     "Visible in reference images as 4× blue anodised columns. "
     "Hard chrome steel, Ø20mm, length 150mm, with flange bushings.",
     "Misumi / THK",
     "Misumi SGBB20-150 or THK SE20 or equivalent",
     "Linear shaft + bushing",
     2400, "2–3 weeks", "TO PROCURE",
     "misumi-europe.com / thk.com",
     "Qty=4 (one at each corner of press plate). Match to top plate hole pattern."),

    (8, "Pneumatic Press", 1, "PRESS_TOP_PLATE",
     "Top Press Plate – Aluminium 6061, 300×300×20mm",
     "Top plate carries the pogo-pin carrier / needle bed and is driven down by the "
     "pneumatic cylinder. Aluminium 6061-T6 for rigidity. "
     "Mounts cylinder rod end centrally, guide column bushings at 4 corners. "
     "Threaded holes for pogo carrier and connector actuation brackets.",
     "Custom / Machining",
     "N/A – custom design",
     "Machined Al 6061",
     0, "2–3 weeks", "CUSTOM/MACHINED",
     "Engineering design required",
     "Dimensions: approx 300×300×20mm. Confirm after pogo carrier and cylinder are sized."),

    (9, "Pneumatic Press", 1, "PRESS_BASE_PLATE",
     "Base Fixture Plate – Aluminium 6061, 400×350×20mm",
     "Base plate fixed to station frame. Holds PCB nest (tooling pins + stops), "
     "lower pogo receptacle (if bed-of-nails from below), conveyor stopper mounts, "
     "sensor brackets. Threaded grid M6×25mm.",
     "Custom / Machining",
     "N/A – custom design",
     "Machined Al 6061",
     0, "3–4 weeks", "CUSTOM/MACHINED",
     "Engineering design required",
     "Same concept as existing RR_VT base plate. Scale up for conveyor width."),

    (10, "Pneumatic Press", 1, "PRESS_FRAME",
     "Station Frame – Aluminium Profile 40×40mm (welded / bolted)",
     "Structural frame of the test station. Built from 40×40mm Bosch Rexroth "
     "or Misumi aluminium extrusion. Supports conveyor, press cylinder, top plate, "
     "electrical cabinet, and operator HMI. Height ~1.2m, footprint ~600×500mm.",
     "Bosch Rexroth / Misumi",
     "Rexroth 3842505512 (40×40 profile) + corner brackets",
     "Al extrusion system",
     18000, "2–3 weeks", "TO PROCURE",
     "boschrexroth.com / misumi-europe.com",
     "Estimate 8m total profile + connectors + brackets. Size TBD after layout drawing."),

    (11, "Pneumatic Press", 4, "PRESS_ALIGN_PIN",
     "PCB Alignment / Tooling Pin – Ø4mm, Stainless Steel, L=15mm",
     "Precision ground tooling pins to locate PCB in the fixture nest before pressing. "
     "Match PCB tooling hole positions from drill file (C652-10 / C654-11).",
     "Misumi / Standard",
     "Misumi DPAL4-15 or equivalent",
     "Stainless steel",
     320, "1–2 weeks", "TO PROCURE",
     "misumi-europe.com; drill file: C652-10_Through.drl",
     "Qty=4: 2 functional alignment pins + 2 spare. Press-fit into base plate."),

    (12, "Pneumatic Press", 2, "PRESS_SENSOR",
     "Cylinder Position Sensor – Magnetic Reed, 24VDC",
     "Magnetic reed sensors mounted on cylinder barrel to detect OPEN position "
     "and CLOSED (fully pressed) position. NPN output, 24VDC, for PLC input.",
     "Festo / SMC",
     "Festo SME-8M-DS-24V-K-2,5-OE or SMC D-M9N",
     "T-slot mount on cylinder",
     650, "1–2 weeks", "TO PROCURE",
     "festo.com / smcworld.com",
     "Qty=2 per cylinder: top (OPEN) + bottom (CLOSED) positions."),

    # ══════════════════════════════════════════════════════════════════════════
    ("SEC", "3. PNEUMATIC SUPPLY & CONTROL"),
    # ══════════════════════════════════════════════════════════════════════════

    (13, "Pneumatics", 3, "SOL_VALVE",
     "5/2 Solenoid Valve – 24VDC, G1/8",
     "5-port/2-position single solenoid (spring return) valve. 24VDC coil. "
     "Controls press cylinder (item 6) and two PCB stopper cylinders (item 3). "
     "Manifold mounted. Includes LED indicator and manual override.",
     "Festo / SMC / Parker",
     "Festo VUVS-LT20-M52-MD-G18-F7 or SMC VF3130-5DZ1-02",
     "Manifold / sub-base",
     3100, "2–3 weeks", "TO PROCURE",
     "festo.com / smcworld.com",
     "Qty=3: 1× press cylinder + 2× stopper cylinders. "
     "Wire coils to PLC digital outputs (24VDC)."),

    (14, "Pneumatics", 1, "VALVE_MANIFOLD",
     "Solenoid Valve Manifold Block – 3-station, G1/4 supply",
     "3-station sub-base manifold for mounting all 3 solenoid valves. "
     "Common G1/4 supply port, individual exhaust ports. DIN rail mountable.",
     "Festo / SMC",
     "Festo MHA2-MS1H-3/2G-0,9-PI or SMC SS5VF3-30FD-04N-03T",
     "Manifold block",
     4200, "2–3 weeks", "TO PROCURE",
     "festo.com / smcworld.com",
     ""),

    (15, "Pneumatics", 1, "FRL_UNIT",
     "FRL Unit – Filter + Regulator + Lubricator, G1/4, 0–10 bar",
     "Filter-Regulator-Lubricator (FRL) unit at station air supply inlet. "
     "Filters to 25µm, regulates to 5–6 bar for cylinder operation. "
     "With pressure gauge and manual drain.",
     "Festo / SMC / Parker",
     "Festo LFR-D-MINI or SMC AC30-N02DH-Z-A or equivalent",
     "G1/4 port, panel/DIN mount",
     3800, "2–3 weeks", "TO PROCURE",
     "festo.com / smcworld.com",
     "Set working pressure to 5 bar. Ensure shop air supply is 6–8 bar."),

    (16, "Pneumatics", 2, "FLOW_CTRL",
     "Flow Control Valve (Meter-Out) – G1/8, Ø6mm push-in",
     "Adjustable flow control (meter-out type) on each port of press cylinder "
     "to control press/retract speed. Prevents shock loading on pogo pins.",
     "Festo / SMC",
     "Festo GRLA-1/8-QS-6-D or SMC AS1201F-M5-06A",
     "In-line, push-in",
     580, "1–2 weeks", "TO PROCURE",
     "festo.com / smcworld.com",
     "Qty=2: one on each cylinder port (extend + retract). Tune for ~0.5 s close time."),

    (17, "Pneumatics", 1, "PRESS_SENSOR_PA",
     "Pressure Sensor / Switch – 0–10 bar, 24VDC, PNP",
     "Confirms air supply pressure is within range before allowing press to close. "
     "PLC reads pressure OK signal; if below 4 bar, station goes to FAULT state.",
     "Festo / SMC / IFM",
     "IFM PN2094 or Festo SPTW-P10R-G14-VD-M12 or equivalent",
     "G1/4, IO-Link / PNP",
     4500, "2–3 weeks", "TO PROCURE",
     "ifm.com / festo.com",
     "Mount after FRL regulator. Wire to PLC AI or DI (switch output)."),

    (18, "Pneumatics", 5, "TUBING_6MM",
     "Polyurethane Tubing Ø6mm (per metre)",
     "PU tubing for all pneumatic connections from manifold to cylinders and FRL. "
     "Working pressure 8 bar, temperature range -20 to +60°C.",
     "Festo / SMC / Generic",
     "Festo PUN-6X1-SW or SMC TU0604BU or equivalent",
     "Ø6mm OD, coil",
     120, "1 week", "TO PROCURE",
     "festo.com / smcworld.com",
     "Estimate 5m total. Add push-in fittings (Ø6, G1/8 elbow and straight)."),

    (19, "Pneumatics", 10, "PUSH_FIT",
     "Push-In Fitting – Ø6mm, G1/8 straight + elbow assortment",
     "Push-in pneumatic fittings for tubing connections to valves, cylinders, FRL.",
     "Festo / SMC / Generic",
     "Festo QSL-1/8-6 + QS-1/8-6 or equivalent",
     "Push-in G1/8",
     180, "1 week", "TO PROCURE",
     "festo.com / smcworld.com",
     "Assorted pack: 5× straight + 5× elbow."),

    # ══════════════════════════════════════════════════════════════════════════
    ("SEC", "4. POGO-PIN / NEEDLE-BED CONTACT SYSTEM"),
    # ══════════════════════════════════════════════════════════════════════════

    (20, "Pogo / Needle Bed", 14, "TP_SIG",
     "Test Pin – Signal, 1.5A (Pogo / Spring Probe)",
     "Spring probe test pin, 1.5A max, for signal test points: "
     "3V3, 3V8, SG1/SG2, Cap, LED, EOS, SWD (see Test Point Map sheet). "
     "Same part as SmartBU manual fixture BOM item 10.",
     "RS Components",
     "261-5159",
     "Through-hole pogo",
     385, "2 weeks", "TO PROCURE",
     "RR_VT BOM item #16; RS 261-5159",
     "Qty=14 signal pins + 2 spare. Match to IDC34 pin map."),

    (21, "Pogo / Needle Bed", 18, "TP_PWR",
     "Test Pin – Power, 3A (Pogo / Spring Probe)",
     "Spring probe test pin, 3A max, for power test points: "
     "12V (TP100), GND (TP101/104/106), motor sense, motor diag. "
     "Same part as SmartBU manual fixture BOM item 11.",
     "RS Components",
     "261-5193",
     "Through-hole pogo",
     730, "2 weeks", "TO PROCURE",
     "RR_VT BOM item #17; RS 261-5193",
     "Qty=15 power/GND pins + 3 spare."),

    (22, "Pogo / Needle Bed", 32, "RECEP",
     "Spring-Loaded Test Pin Receptacle",
     "Receptacle to hold pogo pins in pogo carrier block. Press-fit into machined or 3D-printed carrier. "
     "Same part as SmartBU manual fixture BOM item 12.",
     "Harwin",
     "261-5238",
     "Press-fit",
     660, "2 weeks", "TO PROCURE",
     "RR_VT BOM item #18; RS 261-5238",
     "Qty=29 used + 3 spare."),

    (23, "Pogo / Needle Bed", 1, "POGO_CARRIER",
     "Pogo Pin Carrier Block (Top + Bottom Housing) – Machined",
     "Custom machined aluminium (Al 6061) or PEEK carrier block. "
     "Holds all 29 pogo pins in exact XY positions matching DUT test pad layout. "
     "Mounted to top press plate. When press closes, carrier descends onto PCB test points. "
     "Based on coordinates from Gerber drill file and assembly PDF.",
     "Custom / CNC Machining",
     "N/A – custom design",
     "Machined Al / PEEK",
     0, "3–4 weeks", "CUSTOM/MACHINED",
     "DUT Gerber: C652-10_Through.drl / C654-11; Assembly: ASSY_TOP.pdf",
     "Design file must be created. XY coordinates from drill file. "
     "PEEK preferred for electrical isolation between pogo pins."),

    (24, "Pogo / Needle Bed", 1, "IDC_HARNESS",
     "IDC Ribbon Cable 34-pin, 0.5m (Pogo Carrier to Fixture PCB)",
     "34-way flat ribbon cable assembly with IDC crimp connectors at both ends. "
     "Connects pogo carrier output to fixture PCB / test interface board. "
     "Flexible enough to accommodate 80mm press travel.",
     "3M / Amphenol",
     "3365/34 or equivalent",
     "Cable assembly",
     350, "1 week", "TO PROCURE",
     "RR_VT BOM item – same concept",
     "Route with cable chain (item 25) to prevent fatigue from cycling."),

    (25, "Pogo / Needle Bed", 1, "CABLE_CHAIN",
     "Cable Drag Chain – 15×15mm inner, L=200mm",
     "Plastic cable drag chain to protect ribbon cable and wiring connected to moving "
     "press plate. Prevents cable fatigue from repeated press cycles. "
     "15×15mm inner clearance, ~200mm length.",
     "Igus / Generic",
     "Igus 10.01.015.0 or equivalent",
     "Drag chain",
     1200, "1–2 weeks", "TO PROCURE",
     "igus.com",
     ""),

    # ══════════════════════════════════════════════════════════════════════════
    ("SEC", "5. CONNECTOR PLUG-IN ACTUATORS (Auto Connector Mating)"),
    # ══════════════════════════════════════════════════════════════════════════

    (26, "Connector Actuator", 3, "CONN_CYL",
     "Miniature Pneumatic Cylinder (Connector Plug-In) – Ø16mm, Stroke 30mm",
     "Small bore double-acting cylinder to drive plug-in connectors onto DUT PCB headers. "
     "As visible in reference image 1 (actuators pressing connector harnesses onto PCB edge connectors). "
     "Ø16mm bore, 30mm stroke. Low-force, precision actuation.",
     "Festo / SMC",
     "Festo ADVU-16-30-P-A or SMC CJPB6-5 or equivalent",
     "Mini pneumatic cylinder",
     1800, "2–3 weeks", "TO PROCURE",
     "festo.com / smcworld.com",
     "Qty=3: for each multi-pin connector on DUT PCB edge "
     "(visible in image: 3× white/beige connectors on PCB). "
     "Requires custom connector holder bracket."),

    (27, "Connector Actuator", 3, "CONN_BRACKET",
     "3D Printed / Machined Connector Holder Bracket",
     "Custom bracket mounted on the pressing frame or top plate. "
     "Holds connector end and aligns it to DUT PCB header. "
     "Driven by connector plug-in cylinder (item 26). "
     "Designed for specific connector type on DUT (Amphenol FCI X600 family).",
     "Custom / 3D Print + Machining",
     "N/A – custom design",
     "3D Print + Al",
     0, "2–3 weeks", "CUSTOM/MACHINED",
     "DUT BOM: 132302500036O Amphenol FCI X600; Hw_Setups photos",
     "One bracket per connector. Confirm connector part numbers from DUT BOM before designing."),

    (28, "Connector Actuator", 3, "SOL_CONN",
     "5/2 Solenoid Valve for Connector Cylinders – 24VDC, G1/8",
     "Dedicated solenoid valve for each connector plug-in cylinder. "
     "Separate from press cylinder valve for independent control sequence. "
     "24VDC coil, PLC controlled.",
     "Festo / SMC",
     "Festo VUVS-LT20-M52-MD-G18-F7 or equivalent",
     "Manifold / sub-base",
     3100, "2–3 weeks", "TO PROCURE",
     "festo.com / smcworld.com",
     "Qty=3. Add to manifold block or use separate manifold. "
     "Sequence: connectors plug in AFTER press plate contacts PCB pogo pins."),

    # ══════════════════════════════════════════════════════════════════════════
    ("SEC", "6. PLC / STATION CONTROL UNIT"),
    # ══════════════════════════════════════════════════════════════════════════

    (29, "PLC", 1, "PLC_UNIT",
     "PLC – Siemens S7-1200 1214C DC/DC/DC (or equivalent)",
     "Programmable Logic Controller for station sequencing state machine: "
     "IDLE → PCB_DETECTED → BARCODE_SCANNED → PRESS_CLOSE → TESTING → PRESS_OPEN → PASS_FAIL_OUT. "
     "14 DI / 10 DO / 2 AI. 24VDC I/O. Ethernet for HMI and PC communication.",
     "Siemens / Omron / Mitsubishi",
     "Siemens 6ES7214-1AG40-0XB0 (S7-1214C) or Omron CP2E-N40DT-D",
     "DIN rail module",
     28000, "2–4 weeks", "TO PROCURE",
     "siemens.com (S7-1200 catalog); omron.com",
     "Program in Siemens TIA Portal (Ladder / FBD). "
     "I/O mapping: 6 DO (valves) + 4 DI (sensors) + 2 DO (light stack) + 2 AI (pressure)."),

    (30, "PLC", 1, "PLC_PSU",
     "24VDC DIN Rail Power Supply – 5A, 120W",
     "SMPS power supply for PLC, sensors, solenoid valves, light stack, and I/O. "
     "Output 24VDC / 5A. DIN rail mount. Input 100–240VAC.",
     "Phoenix Contact / Meanwell / Weidmuller",
     "Phoenix QUINT-PS/1AC/24DC/5 or Meanwell HDR-100-24 or equivalent",
     "DIN rail SMPS",
     6500, "1–2 weeks", "TO PROCURE",
     "phoenixcontact.com / meanwell.com",
     "Separate from PC PSU and test instrument supplies."),

    (31, "PLC", 1, "PLC_ENET",
     "Ethernet Switch – Unmanaged, 5-port, 24VDC",
     "Industrial Ethernet switch to network: PLC, HMI touch panel, and test PC. "
     "24VDC powered, DIN rail mount, RJ45.",
     "Phoenix Contact / Moxa / Weidmuller",
     "Phoenix FL SWITCH 1005 or equivalent",
     "DIN rail, RJ45",
     4200, "1–2 weeks", "TO PROCURE",
     "phoenixcontact.com",
     "5 ports: PLC + HMI + Test PC + spare ×2."),

    (32, "PLC", 1, "IO_TERMINAL",
     "DIN Rail Terminal Block Set (24VDC, GND, signal) – assorted 30pcs",
     "Screw or push-in terminal blocks for all field wiring connections to PLC I/O. "
     "24VDC supply rails, signal channels, PE terminals.",
     "Phoenix Contact / Weidmuller",
     "Phoenix MKDS 1.5/2-5.08 assortment or equivalent",
     "DIN rail terminals",
     2800, "1 week", "TO PROCURE",
     "phoenixcontact.com",
     "Estimate 30 terminals. Colour-coded: blue (GND), red (24V), grey (signal)."),

    # ══════════════════════════════════════════════════════════════════════════
    ("SEC", "7. BARCODE / DATAMATRIX SCANNER"),
    # ══════════════════════════════════════════════════════════════════════════

    (33, "Barcode", 1, "BC_SCANNER",
     "Fixed-Mount 2D Barcode / Datamatrix Scanner",
     "Fixed-mount industrial 2D scanner for reading PCB serial number Datamatrix / QR code "
     "as PCB arrives at station (before press close). USB HID or RS232 output. "
     "Compatible with existing automation software (Barcode_Reader folder). "
     "Read distance 50–200mm, trigger via PLC or software.",
     "Cognex / Honeywell / Zebra / Keyence",
     "Cognex DataMan 150 or Honeywell Vuquest 3320g or Zebra DS4608-SR00007ZZWW",
     "Fixed-mount, USB/RS232",
     18000, "2–3 weeks", "TO PROCURE",
     "cognex.com; honeywell.com; Continous_Developement/Nfc_Version/Barcode_Reader/",
     "Confirm scanner model with existing lab barcode reader. "
     "Existing Python barcode_utils.py (AutomationScripts/core/) handles the read protocol."),

    (34, "Barcode", 1, "BC_BRACKET",
     "Scanner Mounting Bracket (adjustable angle)",
     "Adjustable bracket to mount barcode scanner above conveyor at entry point. "
     "Allows XY and angle adjustment for optimal read position.",
     "Bosch Rexroth / Custom",
     "Rexroth swivel bracket or 3D printed custom",
     "Al bracket",
     1500, "1–2 weeks", "TO PROCURE",
     "rexroth.com / custom design",
     "Mount on station frame profile at entry to test zone. "
     "Position scanner ~100mm above PCB top surface."),

    (35, "Barcode", 1, "BC_LIGHT",
     "Ring LED Illuminator for Scanner (if needed)",
     "Supplemental ring light for scanner if PCB surface reflectivity requires it. "
     "24VDC, diffuse ring pattern, triggers with scanner exposure.",
     "Cognex / Generic",
     "Cognex In-Sight illuminator or equivalent",
     "Ring light",
     4500, "2–3 weeks", "TO CONFIRM",
     "Verify with scanner supplier if built-in illumination is sufficient",
     "Only procure if standalone illumination is needed. Many modern scanners have built-in LEDs."),

    # ══════════════════════════════════════════════════════════════════════════
    ("SEC", "8. TEST INSTRUMENT INTERFACE (EXISTING TOOLS – TRACEABILITY)"),
    # ══════════════════════════════════════════════════════════════════════════

    (36, "Test Instruments", 1, "PSU",
     "Programmable DC Power Supply – KIKUSUI PWR401L",
     "40V / 1A programmable DC power supply. Controlled via USB (USBTMC / PyVISA). "
     "Provides 12V / 3.8V to DUT. Already in use – listed for BOM traceability.",
     "Kikusui",
     "PWR401L",
     "Bench instrument",
     0, "—", "CONFIRMED",
     "How_To_Debugg.xlsx; AutomationScripts/backend_adapter/",
     "Existing unit. Mount inside station cabinet on DIN rail shelf or rack shelf. "
     "USB cable to test PC. Fixture PCB provides supply rails to DUT via IDC34 harness."),

    (37, "Test Instruments", 1, "TRACE32",
     "JTAG Debugger – Lauterbach Trace32 (CombiProbe / µTrace)",
     "USB-connected SWD/JTAG debugger for firmware flash and debug. "
     "Already in use. USB to test PC; 10-pin SWD header to fixture PCB JTAG connector (item 46 below).",
     "Lauterbach",
     "LA-3505 CombiProbe or µTrace",
     "USB instrument",
     0, "—", "CONFIRMED",
     "config.t32: PBI=USB; AutomationScripts/core/trace32_adapter.py",
     "Existing unit. Cable management: include in cable drag chain (item 25)."),

    (38, "Test Instruments", 1, "CAN_IF",
     "CAN Bus Interface – PEAK PCAN-USB",
     "USB CAN adapter for CAN-H / CAN-L communication with DUT. "
     "Confirmed used in backend_adapter/can_service.py.",
     "PEAK System",
     "IPEH-002022 (PCAN-USB)",
     "USB dongle",
     0, "—", "TO CONFIRM",
     "backend_adapter/can_service.py; Connection sheet DB9",
     "Confirm exact model in use. Mount USB hub inside cabinet."),

    (39, "Test Instruments", 1, "LIN_IF",
     "LIN Bus Interface – USB LIN Adapter",
     "USB LIN adapter for LIN bus communication with DUT. "
     "Confirmed used in backend_adapter/lin_service.py.",
     "PEAK / Kvaser",
     "PLIN-USB or equivalent",
     "USB dongle",
     0, "—", "TO CONFIRM",
     "backend_adapter/lin_service.py; Connection sheet item 8",
     "Confirm exact model in use."),

    (40, "Test Instruments", 1, "USB_HUB",
     "Industrial USB 3.0 Hub – 7-port, DIN Rail / Panel",
     "Central USB hub inside station cabinet for: KIKUSUI, Trace32, PCAN-USB, PLIN-USB, "
     "barcode scanner, and Fixture PCB (if USB-controlled relay board). "
     "Industrial grade, metal housing, 24VDC powered.",
     "Silex / Acroname / Generic",
     "Acroname USBHub3+ or equivalent industrial hub",
     "DIN rail / panel",
     8500, "1–2 weeks", "TO PROCURE",
     "acroname.com",
     "Powered hub to avoid PC USB current limitations. "
     "7 ports: PSU + Trace32 + PCAN + PLIN + Barcode + Relay board + spare."),

    # ══════════════════════════════════════════════════════════════════════════
    ("SEC", "9. TEST INTERFACE BOARD (FIXTURE PCB)"),
    # ══════════════════════════════════════════════════════════════════════════

    (41, "Fixture PCB", 1, "PCB1",
     "Automation Fixture PCB (Test Interface Board)",
     "Custom designed PCB. Routes all DUT test points from IDC34 pogo-pin harness to "
     "instrument connectors: KIKUSUI supply, PCAN DB9, PLIN terminal, Trace32 JTAG, "
     "relay-switched SG/Cap signals. Same design as SmartBU manual fixture PCB (already designed).",
     "Custom / PCB Fabricator",
     "N/A – custom design",
     "THT + SMD, FR4",
     0, "2–3 weeks", "CUSTOM/MACHINED",
     "create_automation_bom.py items 1–9; Connection sheet",
     "Design already partially defined in SmartBU manual fixture BOM. "
     "Replicate and adapt for auto-loader station."),

    (42, "Fixture PCB", 12, "RELAY",
     "Relay – SPDT, 16A, 12V coil",
     "General purpose relays for automated switching of SG1/SG2, Cap, DIP signals. "
     "Replaces manual DIP switches in auto-loader fixture.",
     "TE Connectivity Potter & Brumfield",
     "RT314012",
     "THT",
     473, "1 week", "TO PROCURE",
     "RR_VT BOM item #2; SmartBU BOM item 22",
     "12 relays for 6 signal channels with make/break switching."),

    (43, "Fixture PCB", 1, "X_IDC34",
     "IDC Connector 34-pin (Male, PCB mount)",
     "34-pin IDC box header, 2.54mm pitch. Connects fixture PCB to pogo carrier via ribbon cable.",
     "Wurth Elektronik",
     "61201421621",
     "THT",
     220, "1 week", "TO PROCURE",
     "SmartBU BOM item 2",
     ""),

    (44, "Fixture PCB", 1, "X_DB9",
     "DB9 Female Connector (PCB mount, right angle)",
     "DE-9 female for CAN / motor drive lines.",
     "Amphenol / TE Connectivity",
     "787083-1 or equivalent",
     "THT",
     120, "1 week", "TO PROCURE",
     "SmartBU BOM item 4",
     ""),

    (45, "Fixture PCB", 1, "X_LIN",
     "Terminal Block 3-pin, 5.08mm pitch",
     "For LIN bus connection (LIN, GND, supply).",
     "Wurth Elektronik",
     "691241510003",
     "THT",
     90, "1 week", "TO PROCURE",
     "SmartBU BOM item 5",
     ""),

    (46, "Fixture PCB", 1, "X_JTAG",
     "ARM Cortex Debug Connector 10-pin (2×5, 1.27mm)",
     "10-pin SWD/JTAG header for Lauterbach Trace32. SWD_DATA (TP201), SWD_CLK (TP202), RESET (TP200).",
     "Samtec / Harwin",
     "FTSH-105-01-L-D-K",
     "SMD/THT",
     180, "1 week", "TO PROCURE",
     "SmartBU BOM item 6",
     ""),

    (47, "Fixture PCB", 3, "DCDC",
     "DC-DC Converter 3.3V, 3.3W (TSR 1-2433)",
     "Non-isolated switcher, 3.3V from 12V. EOS logic supply.",
     "Traco Power",
     "TSR 1-2433",
     "THT SIP3",
     525, "1 week", "TO PROCURE",
     "SmartBU BOM item 27",
     ""),

    # ══════════════════════════════════════════════════════════════════════════
    ("SEC", "10. TEST PC & HMI"),
    # ══════════════════════════════════════════════════════════════════════════

    (48, "PC / HMI", 1, "TEST_PC",
     "Industrial Mini PC / Panel PC (Test Controller)",
     "Fanless industrial PC running the automation test software. "
     "Min spec: Intel Core i5, 8GB RAM, 256GB SSD, Windows 10/11 IoT, "
     "4× USB3, 1× Ethernet, RS232 (or USB-RS232 adapter). "
     "Runs: gui_main.py, orchestrator.py, T32, PEAK PCAN driver, PyVISA (KIKUSUI), MySQL client.",
     "Advantech / Beckhoff / OnLogic",
     "Advantech UNO-2484G or OnLogic ML100G-11 or equivalent",
     "Fanless industrial PC",
     65000, "3–4 weeks", "TO PROCURE",
     "advantech.com / onlogic.com",
     "If existing laptop/PC is permanently assigned to station, list it here for traceability. "
     "Confirm OS: Windows 10 IoT Enterprise required for long-term production."),

    (49, "PC / HMI", 1, "HMI_PANEL",
     "Touch Panel HMI – 10\" TFT, 24VDC, Modbus TCP / Ethernet",
     "Operator touch panel mounted on station frame at ergonomic height. "
     "Displays: current state (IDLE / TESTING / PASS / FAIL), last 10 results, "
     "barcode of current PCB, and operator actions (Start / Abort / Reset). "
     "Communicates with PLC via Modbus TCP or Ethernet.",
     "Weintek / Beijer / Siemens (SIMATIC HMI)",
     "Weintek MT8102iE or Siemens 6AV2124-0GC01-0AX0 (KTP700)",
     "10\" touch panel, 24VDC",
     32000, "3–4 weeks", "TO PROCURE",
     "weintek.com / siemens.com",
     "Alternative: use a small monitor + USB touch overlay connected to test PC, "
     "driven by gui_main.py (Tkinter full-screen mode). Lower cost option."),

    (50, "PC / HMI", 1, "PC_MONITOR",
     "Monitor – 21.5\" FHD (for Test PC display, engineering use)",
     "Standard monitor for test PC display. Used during development, "
     "commissioning, and debugging. HDMI/DP input.",
     "Generic / Dell / LG",
     "Any 21.5\" FHD 1080p monitor",
     "Desktop monitor",
     12000, "1 week", "TO PROCURE",
     "—",
     ""),

    # ══════════════════════════════════════════════════════════════════════════
    ("SEC", "11. SAFETY SYSTEM"),
    # ══════════════════════════════════════════════════════════════════════════

    (51, "Safety", 1, "LIGHT_CURTAIN",
     "Safety Light Curtain – 300mm height, Type 4 (IEC 61496)",
     "Type 4 safety light curtain protecting the press zone from operator access "
     "while press is closing or closed. Finger detection (14mm resolution). "
     "Dual output OSSD safety relay output. 300mm protective height.",
     "Sick / Keyence / Omron",
     "Sick deTec4 Core or Keyence GL-R08H or Omron F3SG-R 0300P14",
     "Transmitter + Receiver pair",
     35000, "3–4 weeks", "TO PROCURE",
     "sick.com / keyence.com",
     "Mandatory safety requirement for pneumatic press with sufficient force to injure. "
     "Wire OSSD outputs to safety relay (item 52). Press enable only when OSSD=ON."),

    (52, "Safety", 1, "SAFETY_RELAY",
     "Safety Relay Module – 2-channel, 24VDC (EN 954-1 Cat.3 / PLd)",
     "Safety relay for monitoring light curtain OSSD outputs and E-stop. "
     "Dual-channel monitored input. 3× N/O safety contacts output. "
     "Wires in series with press cylinder solenoid valve power.",
     "Pilz / Sick / Schmersal",
     "Pilz PNOZ X3 or Sick UE10-2OS3D0 or equivalent",
     "DIN rail safety relay",
     8500, "2–3 weeks", "TO PROCURE",
     "pilz.com / sick.com",
     ""),

    (53, "Safety", 2, "ESTOP",
     "Emergency Stop Button – Ø40mm Mushroom, Panel Mount, NC",
     "Illuminated E-stop button on operator panel. Normally closed contact. "
     "One at operator panel + one on station rear / maintenance access.",
     "Schneider / Eaton / ABB",
     "Schneider ZB5AS844 + ZB5AV7 (illuminated) or Eaton M22-PV/KC11",
     "Panel mount Ø40mm",
     1200, "1 week", "TO PROCURE",
     "se.com / eaton.com",
     "Qty=2: front operator + rear maintenance. Wire NC contacts in series to safety relay."),

    (54, "Safety", 1, "LIGHT_STACK",
     "Signal Light Stack – 3-colour (Green / Yellow / Red) + Buzzer",
     "Tower light stack indicating station status: "
     "GREEN = PASS, RED = FAIL, YELLOW = BUSY/TESTING, Buzzer on fault. "
     "24VDC, M20 threaded base, DIN rail or bracket mount.",
     "Patlite / Banner / Werma / Eaton",
     "Patlite LR4-302WJBW-RYG or Banner EZ-LIGHT K50 or equivalent",
     "Tower light, 24VDC",
     5500, "1–2 weeks", "TO PROCURE",
     "patlite.com / bannerengineering.com",
     "Wire Green / Yellow / Red to 3 PLC DO outputs."),

    (55, "Safety", 1, "ENCLOSURE_GUARD",
     "Polycarbonate Guard Panel – 400×300×3mm (press zone side guard)",
     "Transparent polycarbonate guard panels on sides of press zone "
     "(where light curtain does not cover). Prevents side access during pressing. "
     "Hinged or fixed, with proximity switch to detect if open.",
     "Generic / RS Components",
     "3mm clear polycarbonate sheet + Al frame",
     "Sheet + frame",
     2200, "1–2 weeks", "TO PROCURE",
     "RS Components / misumi-europe.com",
     ""),

    # ══════════════════════════════════════════════════════════════════════════
    ("SEC", "12. REJECT / SORT SYSTEM"),
    # ══════════════════════════════════════════════════════════════════════════

    (56, "Reject System", 1, "REJECT_GATE",
     "Pneumatic Reject Gate / Deflector Cylinder",
     "Pneumatic actuator to deflect FAIL PCBs off main conveyor into reject tray. "
     "Actuated by PLC DO after FAIL result. Double-acting, Ø16mm bore, 30mm stroke. "
     "Mounted at station exit on conveyor.",
     "Festo / SMC",
     "Festo ADVU-16-30-P-A or equivalent",
     "Mini pneumatic cylinder",
     1800, "2–3 weeks", "TO PROCURE",
     "festo.com / smcworld.com",
     "Actuated by PLC. PASS = stay on main conveyor, FAIL = deflect to reject tray."),

    (57, "Reject System", 1, "REJECT_TRAY",
     "Reject Tray / Bin (for FAIL PCBs)",
     "Metal tray or plastic bin mounted below reject gate to collect failed PCBs. "
     "Approximate size 250×200×80mm.",
     "Generic / Custom",
     "N/A",
     "Sheet metal tray",
     800, "1 week", "TO PROCURE",
     "—",
     "Label clearly: FAIL – DO NOT SHIP."),

    # ══════════════════════════════════════════════════════════════════════════
    ("SEC", "13. ELECTRICAL CABINET & WIRING"),
    # ══════════════════════════════════════════════════════════════════════════

    (58, "Cabinet", 1, "CABINET",
     "Electrical Cabinet – 400×300×200mm, IP54, steel",
     "Steel enclosure for PLC, 24V PSU, safety relay, terminal blocks, USB hub. "
     "IP54, panel-mount. Mounted on station frame rear.",
     "Rittal / ABB / Generic",
     "Rittal AE 1058.500 (400×300×200 IP55) or equivalent",
     "Steel enclosure",
     8500, "2–3 weeks", "TO PROCURE",
     "rittal.com",
     "Size TBD after PLC + DIN rail component layout. Add cable glands (item 63)."),

    (59, "Cabinet", 1, "DIN_RAIL_SET",
     "DIN Rail 35mm – 3× 300mm lengths",
     "For mounting PLC, PSU, safety relay, and terminal blocks inside cabinet.",
     "Phoenix Contact / Schneider",
     "NS 35/7.5, cut to 300mm",
     "DIN rail",
     450, "1 week", "TO PROCURE",
     "phoenixcontact.com",
     ""),

    (60, "Wiring", 10, "WIRE_24AWG",
     "Wire 24 AWG, multi-colour (per metre)",
     "Power wiring inside cabinet (24VDC, GND) and field wiring to sensors/valves.",
     "Generic",
     "24AWG hook-up wire",
     "Single core",
     1950, "1 week", "TO PROCURE",
     "RR_VT BOM – same spec",
     "Estimate 10m total. Colours: red (24V), blue (GND/0V), grey (signal), yellow-green (PE)."),

    (61, "Wiring", 5, "WIRE_SH",
     "Shielded Twisted Pair 2×28 AWG (per metre)",
     "For CAN-H/L and LIN bus runs from instruments to fixture PCB.",
     "Generic",
     "2×28AWG shielded",
     "Cable",
     360, "1 week", "TO PROCURE",
     "RR_VT BOM item #24",
     "Estimate 5m total."),

    (62, "Wiring", 1, "FERRITE_SET",
     "Ferrite Clamps – assorted Ø3–7mm (pack of 10)",
     "Snap-on ferrite cores on USB cables and signal lines to suppress EMI interference.",
     "Würth Elektronik / Fair-Rite",
     "Wurth 74271222 or equivalent",
     "Snap-on clamp",
     350, "1 week", "TO PROCURE",
     "wurth-elektronik.com",
     "Important for CAN/LIN signal integrity in production environment."),

    (63, "Cabinet", 8, "CABLE_GLAND",
     "Cable Gland M20, PG13.5 – IP54 (pack)",
     "Cable entry glands for cabinet. One per cable bundle entering cabinet.",
     "Hummel / Generic",
     "M20×1.5 PG13.5 cable gland",
     "IP54",
     120, "1 week", "TO PROCURE",
     "Standard component",
     ""),

    (64, "Cabinet", 1, "MAINS_SWITCH",
     "Main Power Switch – 2-pole, 16A, panel mount",
     "Main power isolator switch on cabinet door. Isolates all station power. "
     "Lockable (lockout/tagout capable).",
     "Schneider / Eaton / ABB",
     "Schneider GS2DB3 or Eaton T0-2-1/EA/SVB",
     "Panel mount rotary",
     1800, "1 week", "TO PROCURE",
     "se.com / eaton.com",
     ""),

    (65, "Cabinet", 1, "MCB",
     "Miniature Circuit Breaker – 2-pole, 10A, 230VAC (C-curve)",
     "Mains protection for station. Protects against overload on 230VAC mains input.",
     "Schneider / ABB",
     "Schneider A9F74210 or ABB S202-C10",
     "DIN rail MCB",
     850, "1 week", "TO PROCURE",
     "se.com / abb.com",
     ""),

    # ══════════════════════════════════════════════════════════════════════════
    ("SEC", "14. NFC SUBSYSTEM (NFC variants only)"),
    # ══════════════════════════════════════════════════════════════════════════

    (66, "NFC", 2, "NFC_SERVO",
     "Servo Motor – 25 kg.cm, Metal Gear (NFC card positioner)",
     "Servo motor to position NFC reference card/smartphone over DUT NFC antenna. "
     "Required only for NFC LH and NFC RH variants.",
     "Pro-Range",
     "OT5325M",
     "Servo",
     1371, "1 week", "TO PROCURE",
     "RR_VT BOM item #10",
     "Only for NFC variants."),

    (67, "NFC", 1, "NFC_HOLDER",
     "NFC Card / Smartphone Holder",
     "Clamp holder for NFC reference card used in NFC antenna test.",
     "SmallRig",
     "SmallRig clamp or equivalent",
     "Mechanical",
     2300, "2 weeks", "TO PROCURE",
     "RR_VT BOM item #12",
     "Only for NFC variants."),

    # ══════════════════════════════════════════════════════════════════════════
    ("SEC", "15. MISCELLANEOUS / CONSUMABLES"),
    # ══════════════════════════════════════════════════════════════════════════

    (68, "Misc", 10, "STANDOFF_M3",
     "PCB Standoffs M3×10mm (nylon, pack of 10)",
     "For mounting fixture PCB, relay board, EOS board to base plate.",
     "Generic",
     "N/A",
     "Nylon hex standoff",
     30, "1 week", "TO PROCURE",
     "Standard component",
     ""),

    (69, "Misc", 1, "SCREW_KIT",
     "Screw / Nut Kit – M2, M3, M4, M5 assorted",
     "Assorted stainless steel screws and nuts for assembly.",
     "Generic / Misumi",
     "N/A",
     "Assorted",
     450, "1 week", "TO PROCURE",
     "—",
     ""),

    (70, "Misc", 1, "LABEL_KIT",
     "Cable Label Set + Marker",
     "Self-laminating cable labels for all harness wires.",
     "Brady / HellermannTyton",
     "N/A",
     "Labels",
     350, "1 week", "TO PROCURE",
     "—",
     ""),

    (71, "Misc", 1, "CABLE_TIES",
     "Cable Tie Kit – 100mm, 150mm, 200mm (pack of 100 each)",
     "Cable management throughout station.",
     "Generic",
     "N/A",
     "Nylon cable ties",
     250, "1 week", "TO PROCURE",
     "—",
     ""),

    (72, "Misc", 1, "VELCRO_WRAP",
     "Hook-and-Loop Velcro Cable Ties (pack of 20)",
     "Reusable cable ties for cabinet wiring bundles.",
     "Generic",
     "N/A",
     "Accessory",
     120, "1 week", "TO PROCURE",
     "—",
     ""),

    (73, "Misc", 1, "THERMAL_PASTE",
     "Thermal Interface Compound (if servo / actuator drivers need heatsink)",
     "Thermal paste for heatsinking drive electronics if required.",
     "Generic / Dow Corning",
     "DC-340 or equivalent",
     "Tube 30g",
     280, "1 week", "TO PROCURE",
     "—",
     "Only if drive ICs require heatsinking."),
]

# ─── Write BOM rows ──────────────────────────────────────────────────────────
row = 8
for entry in BOM:
    if entry[0] == "SEC":
        ws.row_dimensions[row].height = 18
        ws.merge_cells(f"A{row}:O{row}")
        c = ws[f"A{row}"]
        c.value = f"  ▶  {entry[1]}"
        c.fill = fill(LBLUE)
        c.font = Font(bold=True, color=NAVY, size=10, name="Calibri")
        c.alignment = Alignment(horizontal="left", vertical="center")
        row += 1
        continue

    (item, subsys, qty, ref, pname, desc, mfr,
     ordno, pkg, uprice, leadtime, status, source, notes) = entry

    ws.row_dimensions[row].height = 60
    alt = ALT1 if row % 2 == 0 else ALT2
    s_bg, s_fg = STATUS_FMT.get(status, (GBKG2, GRAY))

    values = [
        item, subsys, qty, ref, pname, desc, mfr, ordno, pkg,
        uprice,
        f"=C{row}*J{row}" if uprice else 0,
        leadtime, status, source, notes
    ]

    for ci, val in enumerate(values, 1):
        c = ws.cell(row=row, column=ci, value=val)
        c.border = thin_border()
        c.alignment = wrap()

        if ci == 1:
            c.fill = fill(BLUE); c.font = font(bold=True, color=WHITE, size=9)
            c.alignment = wrap("center")
        elif ci == 13:
            c.fill = fill(s_bg); c.font = font(bold=True, color=s_fg, size=9)
            c.alignment = wrap("center")
        elif ci == 3:
            c.alignment = wrap("center")
            c.fill = fill(alt); c.font = font(size=9)
        elif ci in (10, 11):
            c.fill = fill(alt); c.font = font(size=9)
            c.alignment = wrap("right")
            c.number_format = '#,##0'
        else:
            c.fill = fill(alt); c.font = font(size=9)
    row += 1

# ── Grand total row ────────────────────────────────────────────────────────────
ws.row_dimensions[row].height = 22
for ci in range(1, 16):
    c = ws.cell(row=row, column=ci)
    c.fill = fill(NAVY); c.border = thin_border(NAVY)

ws.merge_cells(f"A{row}:J{row}")
gt_label = ws[f"A{row}"]
gt_label.value = "GRAND TOTAL (Procurable items only – custom/machined at cost 0)"
gt_label.font = font(bold=True, color=WHITE, size=10)
gt_label.alignment = wrap("center")

gt_val = ws.cell(row=row, column=11, value=f"=SUM(K8:K{row-1})")
gt_val.font = font(bold=True, color=WHITE, size=10)
gt_val.number_format = '#,##0'
gt_val.alignment = wrap("right")

# ── Notes ──────────────────────────────────────────────────────────────────────
row += 2
note_text = (
    "NOTES:  "
    "(1) Prices in INR (approximate). Custom/Machined items show 0 – quote from machining vendor separately.  "
    "(2) 'TO CONFIRM' items require part number verification from existing lab setup before ordering.  "
    "(3) 'CONFIRMED' items are already in use – listed for station-level traceability only.  "
    "(4) Pneumatic system requires shop air: 6–8 bar, min 50 L/min at station.  "
    "(5) Safety light curtain (item 51) is MANDATORY before station can be operated with pneumatic press.  "
    "(6) NFC subsystem (Section 14) only required for NFC LH / NFC RH variants.  "
    "(7) PLC program, HMI screens, and station state machine must be developed (not covered in hardware BOM).  "
    "(8) Test software (gui_main.py, orchestrator.py, barcode_utils.py, MySQL integration) already exists in project."
)
ws.merge_cells(f"A{row}:O{row}")
c = ws[f"A{row}"]
c.value = note_text
c.font = font(italic=True, size=8, color="595959")
c.alignment = wrap("left")
ws.row_dimensions[row].height = 65

# ═════════════════════════════════════════════════════════════════════════════
# SHEET 2 — STATION FLOW / STATE MACHINE DESCRIPTION
# ═════════════════════════════════════════════════════════════════════════════
ws2 = wb.create_sheet("Station Flow and IO Map")
ws2.sheet_view.showGridLines = False

col_w(ws2, "A", 6);  col_w(ws2, "B", 22); col_w(ws2, "C", 30)
col_w(ws2, "D", 30); col_w(ws2, "E", 22); col_w(ws2, "F", 22); col_w(ws2, "G", 30)

ws2.row_dimensions[1].height = 38
merge(ws2, "A1:G1",
      "Station State Machine Flow  &  PLC I/O Map  —  Conveyor-Fed Auto Loader",
      NAVY, WHITE, sz=13)

# ── State machine table ────────────────────────────────────────────────────────
merge(ws2, "A3:G3", "STATION STATE MACHINE", BLUE, WHITE, sz=11)
ws2.row_dimensions[3].height = 22

sm_hdr = ["Step", "State Name", "Entry Condition", "Actions (PLC DO / PC command)",
          "Exit Condition", "Next State", "Notes"]
ws2.row_dimensions[4].height = 26
for ci, h in enumerate(sm_hdr, 1):
    c = ws2.cell(row=4, column=ci, value=h)
    c.fill = fill(BLUE); c.font = font(bold=True, color=WHITE, size=9)
    c.alignment = wrap("center"); c.border = thin_border(NAVY)

STATES = [
    (1,  "IDLE",
     "Station powered on / previous cycle complete",
     "Conveyor running; light stack YELLOW; HMI shows READY",
     "PCB presence sensor (item 4) triggers",
     "PCB_ARRIVING",
     "Conveyor runs continuously in IDLE. Stopper pin (entry) is UP."),

    (2,  "PCB_ARRIVING",
     "Entry PCB sensor detects PCB",
     "Stopper pin (entry) stays UP; conveyor keeps running; "
     "second position sensor waits for PCB-centred",
     "Position sensor (station centre) confirms PCB at test position",
     "PCB_POSITIONED",
     "PCB slides from entry sensor to test position under gravity/belt motion."),

    (3,  "PCB_POSITIONED",
     "Centre position sensor triggered",
     "Raise exit stopper pin (item 3, exit side); "
     "stop conveyor belt (PLC DO → conveyor drive)",
     "Both stoppers confirmed UP by cylinder sensors (item 12)",
     "BARCODE_SCAN",
     "PCB is now clamped between entry + exit stoppers, centred in fixture nest."),

    (4,  "BARCODE_SCAN",
     "PCB clamped at station",
     "Trigger barcode scanner (item 33) via USB; "
     "PC reads barcode string; validate against known serial format",
     "Valid barcode received by PC (timeout 3s → FAULT)",
     "PRESS_CLOSING",
     "Software: barcode_utils.py reads scanner. "
     "MySQL: check if PCB was tested before (re-test flag)."),

    (5,  "PRESS_CLOSING",
     "Valid barcode confirmed",
     "Check light curtain OSSD=ON (safe); "
     "energise press solenoid valve (item 13) DO → press cylinder extends; "
     "wait for CLOSED sensor (item 12)",
     "Cylinder CLOSED position sensor confirms contact; "
     "pressure sensor (item 17) ≥ 4 bar",
     "CONNECTOR_MATING",
     "Light stack: YELLOW flashing. HMI shows PRESSING."),

    (6,  "CONNECTOR_MATING",
     "Press plate on PCB, pogo pins contacting test pads",
     "Energise connector plug-in solenoid valves (item 28) sequentially; "
     "3× connector cylinders extend, mate connectors to PCB headers; "
     "wait 0.5s settle time",
     "All 3 connector cylinder CLOSED sensors confirmed",
     "TESTING",
     "Sequence: Press first, then connectors – prevents connector damage."),

    (7,  "TESTING",
     "All contacts made, all connectors mated",
     "PC: run full test sequence via orchestrator.py "
     "(PSU power ON → Trace32 flash/debug → CAN → LIN → Motor → SG → EOS → LED → NFC); "
     "light stack YELLOW solid; HMI shows TESTING + progress bar",
     "orchestrator.py returns PASS or FAIL result",
     "PRESS_OPENING",
     "Test duration: ~60–120s depending on variant. "
     "MySQL: log start time, barcode, variant."),

    (8,  "PRESS_OPENING",
     "Test sequence complete",
     "De-energise connector solenoid valves → retract connector cylinders; "
     "de-energise press solenoid → press cylinder retracts; "
     "wait for OPEN sensor (item 12) confirmed",
     "Press OPEN sensor confirmed; connector OPEN sensors confirmed",
     "RESULT_OUTPUT",
     "Open connectors first, then press – prevents connector damage on retract."),

    (9,  "RESULT_OUTPUT",
     "Press fully open",
     "PASS: light stack GREEN + short beep; HMI PASS screen; "
     "lower exit stopper pin → start conveyor → PCB exits on main line.  "
     "FAIL: light stack RED + long beep; HMI FAIL screen; "
     "actuate reject gate (item 56) → lower exit stopper → PCB diverted to reject tray.",
     "PCB cleared exit sensor (confirming PCB left station)",
     "LOGGING",
     "MySQL: log end time, result (PASS/FAIL), test details. HTML report generated."),

    (10, "LOGGING",
     "PCB has left station",
     "PC: write test record to MySQL (nfc_or_non_nfc_lh table); "
     "generate HTML report; reset reject gate; lower entry stopper; "
     "reset all outputs",
     "MySQL write confirmed; all outputs reset",
     "IDLE",
     "Station returns to IDLE, ready for next PCB. Conveyor belt restarts."),

    (11, "FAULT",
     "Any: barcode timeout / light curtain breach / pressure low / sensor mismatch",
     "Press retracts (if extended); light stack RED flashing + continuous beep; "
     "HMI FAULT screen with fault code; station stops; "
     "E-stop circuit activates if safety sensor fault",
     "Operator acknowledges fault on HMI; fault condition resolved",
     "IDLE (after reset)",
     "All faults logged to MySQL with fault code. "
     "Fault codes: F01=barcode, F02=light curtain, F03=pressure, F04=sensor."),
]

for r_off, s in enumerate(STATES):
    row_i = 5 + r_off
    ws2.row_dimensions[row_i].height = 65
    alt = ALT1 if row_i % 2 == 0 else ALT2
    for ci, val in enumerate(s, 1):
        c = ws2.cell(row=row_i, column=ci, value=val)
        c.border = thin_border()
        c.alignment = wrap()
        if ci == 1:
            c.fill = fill(BLUE); c.font = font(bold=True, color=WHITE, size=9)
            c.alignment = wrap("center")
        elif ci == 2:
            c.fill = fill(NAVY); c.font = font(bold=True, color=WHITE, size=9)
        else:
            c.fill = fill(alt); c.font = font(size=9)

# ── PLC I/O Map ───────────────────────────────────────────────────────────────
io_start = 5 + len(STATES) + 2
ws2.row_dimensions[io_start - 1].height = 22
merge(ws2, f"A{io_start-1}:G{io_start-1}", "PLC I/O MAPPING", BLUE, WHITE, sz=11)

io_hdr = ["I/O", "Channel", "Signal Name", "Connected Device", "Type", "State 0", "State 1"]
ws2.row_dimensions[io_start].height = 26
for ci, h in enumerate(io_hdr, 1):
    c = ws2.cell(row=io_start, column=ci, value=h)
    c.fill = fill(BLUE); c.font = font(bold=True, color=WHITE, size=9)
    c.alignment = wrap("center"); c.border = thin_border(NAVY)

IO_MAP = [
    ("DI", "DI0.0", "PCB_ENTRY_DETECT",    "Entry photoelectric sensor (item 4)",   "24VDC NPN", "No PCB", "PCB detected"),
    ("DI", "DI0.1", "PCB_POSITION_DETECT",  "Centre position sensor (item 4)",        "24VDC NPN", "No PCB", "PCB at station"),
    ("DI", "DI0.2", "PRESS_OPEN_SENSE",     "Cylinder OPEN reed sensor (item 12)",    "24VDC NPN", "Not open", "Press open"),
    ("DI", "DI0.3", "PRESS_CLOSED_SENSE",   "Cylinder CLOSED reed sensor (item 12)", "24VDC NPN", "Not closed", "Press closed"),
    ("DI", "DI0.4", "LIGHT_CURTAIN_OSSD",   "Safety light curtain OSSD (item 51)",   "24VDC PNP dual", "Breach / off", "Safe / clear"),
    ("DI", "DI0.5", "ESTOP_OK",             "E-stop NC contact (items 53)",           "24VDC NC", "E-stop pressed", "E-stop OK"),
    ("DI", "DI0.6", "AIR_PRESSURE_OK",      "Pressure switch (item 17)",              "24VDC PNP", "Pressure low", "Pressure OK"),
    ("DI", "DI0.7", "PCB_EXIT_DETECT",      "Exit photoelectric sensor",              "24VDC NPN", "No PCB", "PCB present"),
    ("DO", "DO0.0", "PRESS_SOL_VALVE",      "Press cylinder solenoid (item 13)",      "24VDC coil", "Press retract", "Press extend"),
    ("DO", "DO0.1", "STOPPER_ENTRY_SOL",    "Entry stopper solenoid (item 13)",       "24VDC coil", "Stopper down", "Stopper up"),
    ("DO", "DO0.2", "STOPPER_EXIT_SOL",     "Exit stopper solenoid (item 13)",        "24VDC coil", "Stopper down", "Stopper up"),
    ("DO", "DO0.3", "CONN_SOL_1",           "Connector 1 solenoid (item 28)",         "24VDC coil", "Retract", "Extend/mate"),
    ("DO", "DO0.4", "CONN_SOL_2",           "Connector 2 solenoid (item 28)",         "24VDC coil", "Retract", "Extend/mate"),
    ("DO", "DO0.5", "CONN_SOL_3",           "Connector 3 solenoid (item 28)",         "24VDC coil", "Retract", "Extend/mate"),
    ("DO", "DO0.6", "REJECT_GATE_SOL",      "Reject gate cylinder (item 56)",         "24VDC coil", "Gate closed (PASS)", "Gate open (FAIL)"),
    ("DO", "DO0.7", "CONVEYOR_RUN",         "Conveyor drive enable (item 2)",         "24VDC relay", "Conveyor stop", "Conveyor run"),
    ("DO", "DO1.0", "LIGHT_GREEN",          "Light stack green (item 54)",            "24VDC", "Off", "PASS"),
    ("DO", "DO1.1", "LIGHT_YELLOW",         "Light stack yellow (item 54)",           "24VDC", "Off", "BUSY/TESTING"),
    ("DO", "DO1.2", "LIGHT_RED",            "Light stack red (item 54)",              "24VDC", "Off", "FAIL/FAULT"),
    ("DO", "DO1.3", "BUZZER",               "Light stack buzzer (item 54)",           "24VDC", "Silent", "Alert"),
]

for r_off, io in enumerate(IO_MAP):
    row_i = io_start + 1 + r_off
    ws2.row_dimensions[row_i].height = 22
    alt = ALT1 if row_i % 2 == 0 else ALT2
    io_type = io[0]
    row_bg = GBKG if io_type == "DI" else RBKG
    for ci, val in enumerate(io, 1):
        c = ws2.cell(row=row_i, column=ci, value=val)
        c.border = thin_border()
        c.alignment = wrap()
        if ci == 1:
            c.fill = fill(row_bg)
            c.font = font(bold=True, color=GREEN if io_type == "DI" else RED, size=9)
            c.alignment = wrap("center")
        else:
            c.fill = fill(alt); c.font = font(size=9)

# ═════════════════════════════════════════════════════════════════════════════
# SHEET 3 — SYSTEM OVERVIEW DIAGRAM (Text-based)
# ═════════════════════════════════════════════════════════════════════════════
ws3 = wb.create_sheet("System Overview")
ws3.sheet_view.showGridLines = False
col_w(ws3, "A", 100)
ws3.row_dimensions[1].height = 38
merge(ws3, "A1:A1",
      "System Overview — Conveyor-Fed Automatic PCB Test Station",
      NAVY, WHITE, sz=13)

overview_lines = [
    "",
    "  ┌─────────────────────────────────────────────────────────────────────────────────────────────────┐",
    "  │                    CONVEYOR-FED AUTOMATIC PCB TEST STATION — SYSTEM OVERVIEW                    │",
    "  └─────────────────────────────────────────────────────────────────────────────────────────────────┘",
    "",
    "  [UPSTREAM CONVEYOR] ──► [ENTRY STOPPER ↑] ──► [BARCODE SCANNER] ──► [PRESS STATION] ──► [EXIT]",
    "                                                                               │",
    "                                                                    ┌──────────┴──────────┐",
    "                                                                    │  PNEUMATIC PRESS     │",
    "                                                                    │  (Top plate + pogo   │",
    "                                                                    │   pin carrier down)  │",
    "                                                                    │  + Connector plug-in │",
    "                                                                    └──────────┬──────────┘",
    "                                                                               │",
    "                                                                    ┌──────────┴──────────┐",
    "                                                                    │   TEST INSTRUMENTS   │",
    "                                                                    │  • KIKUSUI PWR401L   │",
    "                                                                    │  • Lauterbach Trace32│",
    "                                                                    │  • PCAN-USB (CAN)    │",
    "                                                                    │  • PLIN-USB (LIN)    │",
    "                                                                    └──────────┬──────────┘",
    "                                                                               │",
    "                                                                    ┌──────────┴──────────┐",
    "                                                                    │    TEST PC           │",
    "                                                                    │  orchestrator.py     │",
    "                                                                    │  gui_main.py         │",
    "                                                                    │  MySQL logging       │",
    "                                                                    │  HTML report         │",
    "                                                                    └──────────┬──────────┘",
    "                                                                               │",
    "                                                          PASS ◄───────────────┼───────────────► FAIL",
    "                                                            │                                      │",
    "                                                    [EXIT CONVEYOR]                        [REJECT TRAY]",
    "",
    "  SAFETY LAYER:",
    "  • Type-4 Safety Light Curtain guards press zone entry",
    "  • E-stop buttons (front + rear)",
    "  • Safety relay monitors OSSD + E-stop NC chain",
    "  • Press only closes when OSSD=ON + E-stop OK + air pressure OK",
    "",
    "  PLC STATE MACHINE (Siemens S7-1200):",
    "  IDLE → PCB_ARRIVING → PCB_POSITIONED → BARCODE_SCAN → PRESS_CLOSING →",
    "  CONNECTOR_MATING → TESTING → PRESS_OPENING → RESULT_OUTPUT → LOGGING → IDLE",
    "",
    "  SOFTWARE STACK (already developed – see AutomationScripts/):",
    "  • barcode_utils.py      : reads scanner USB HID",
    "  • orchestrator.py       : runs full test sequence",
    "  • trace32_adapter.py    : Lauterbach T32 control",
    "  • can_service.py        : PCAN-USB CAN communication",
    "  • lin_service.py        : PLIN-USB LIN communication",
    "  • motor_service.py      : motor test",
    "  • nfc_service.py        : NFC antenna test",
    "  • sg_service.py         : strain gauge sensor test",
    "  • eos_service.py        : EOS test",
    "  • report_generator.py   : HTML report",
    "  • MySQL                 : test result database",
    "",
    "  WHAT STILL NEEDS TO BE DEVELOPED:",
    "  1. PLC program (TIA Portal) – state machine + I/O mapping (see Sheet 2)",
    "  2. HMI screens (Weintek / SIMATIC) or Tkinter full-screen mode in gui_main.py",
    "  3. PLC ↔ Test PC handshake (Modbus TCP or simple TCP socket)",
    "  4. Custom fixture PCB design (based on existing SmartBU BOM – mostly defined)",
    "  5. Mechanical drawings for: top press plate, base plate, pogo carrier, connector brackets",
    "  6. Safety validation (EN ISO 13849 PLd assessment for light curtain + safety relay)",
]

for i, line in enumerate(overview_lines):
    ws3.row_dimensions[i + 2].height = 15
    c = ws3.cell(row=i + 2, column=1, value=line)
    c.font = Font(name="Courier New", size=9, color="1F1F1F")
    c.alignment = Alignment(horizontal="left", vertical="center", wrap_text=False)

# ─── Save ─────────────────────────────────────────────────────────────────────
out_path = r"c:\UShin\Testbench_gui_Charan\Continous_Developement\BOM_SmartBU_Automation\Conveyor_AutoLoader_Fixture_BOM_Rev1.0.xlsx"
wb.save(out_path)
print(f"✓  Saved: {out_path}")
print(f"   Sheets: {[s.title for s in wb.worksheets]}")
