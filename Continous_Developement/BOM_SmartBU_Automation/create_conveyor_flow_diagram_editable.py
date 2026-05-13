"""
create_conveyor_flow_diagram_editable.py  v2
Generates a fully editable PowerPoint (.pptx) flow diagram for the
Conveyor-Fed Automatic PCB Test Station using native python-pptx shapes.

All boxes, arrows, and text are native PowerPoint objects — select any
element and edit text, colour, size, or position directly in PowerPoint.

Output: Conveyor_AutoLoader_Flow_Diagram_Rev1.0_Editable.pptx

Slide 1 — Panel A  Station State Machine
Slide 2 — Panel B  System Architecture
Slide 3 — Panel C  Test Sequence Detail + PLC I/O Table

Engineer : Charan Singh
Project  : SmartBU / XNF I460  |  BMW MAE 032080790003
Rev      : 1.0   Date: 11.05.2026
"""

import os
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.enum.shapes import MSO_CONNECTOR_TYPE
from pptx.oxml.ns import qn
from lxml import etree

# ─────────────────────────────────────────────────────────────────
# Colour helpers
# ─────────────────────────────────────────────────────────────────
def rgb(h):
    h = h.lstrip("#")
    return RGBColor(int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16))

C_IDLE    = "#4A90D9"
C_ACTION  = "#27AE60"
C_SAFETY  = "#E74C3C"
C_SPECIAL = "#F39C12"
C_INST    = "#8E44AD"
C_PC      = "#16A085"
C_HW      = "#2C3E50"
C_NFC     = "#D35400"
C_BG      = "#F8F9FA"
C_ARROW   = "#555555"
WHITE     = "#FFFFFF"

# OOXML namespace for DrawingML
A_NS = "http://schemas.openxmlformats.org/drawingml/2006/main"

SLD_W = Inches(22)
SLD_H = Inches(13)

# ─────────────────────────────────────────────────────────────────
# Core shape helpers
# ─────────────────────────────────────────────────────────────────

def add_rounded_box(slide, l, t, w, h, fill_hex, text_lines,
                    font_sizes=None, bold_flags=None,
                    text_color=WHITE, border_hex=WHITE, border_pt=1.5,
                    align=PP_ALIGN.CENTER, v_anchor="middle"):
    """
    Add a rounded-rectangle shape (MSO_AUTO_SHAPE_TYPE 5) with text.
    Uses shape type 5 directly — no XML patching needed for the geometry.
    """
    # 5 = MSO_AUTO_SHAPE_TYPE.ROUNDED_RECTANGLE — native, no XML hacks required
    shape = slide.shapes.add_shape(5, l, t, w, h)

    shape.fill.solid()
    shape.fill.fore_color.rgb = rgb(fill_hex)
    shape.line.color.rgb = rgb(border_hex)
    shape.line.width = Pt(border_pt)

    tf = shape.text_frame
    tf.word_wrap = True

    # Set vertical anchor via XML attribute on bodyPr (avoids enum import issues)
    anchor_val = "ctr" if v_anchor == "middle" else "t"
    body_pr = tf._txBody.find(qn("a:bodyPr"))
    if body_pr is not None:
        body_pr.set("anchor", anchor_val)

    for i, line in enumerate(text_lines):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.alignment = align
        run = p.add_run()
        run.text = line
        run.font.size  = Pt(font_sizes[i]  if font_sizes  and i < len(font_sizes)  else 10)
        run.font.bold  = bold_flags[i]      if bold_flags  and i < len(bold_flags)  else False
        run.font.color.rgb = rgb(text_color) if isinstance(text_color, str) else text_color

    return shape


def add_textbox(slide, l, t, w, h, text, font_size=9, bold=False,
                color=C_HW, align=PP_ALIGN.LEFT, italic=False):
    txBox = slide.shapes.add_textbox(l, t, w, h)
    tf = txBox.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.alignment = align
    run = p.add_run()
    run.text = text
    run.font.size   = Pt(font_size)
    run.font.bold   = bold
    run.font.italic = italic
    run.font.color.rgb = rgb(color)
    return txBox


def add_arrow(slide, x1, y1, x2, y2, color_hex=C_ARROW, width_pt=2.0,
              label="", label_color=C_ARROW, label_size=7, dashed=False):
    """
    Add a straight connector with an arrowhead at (x2, y2).

    Fix notes vs v1:
    - Use MSO_CONNECTOR_TYPE.STRAIGHT enum (not bare int 1)
    - Do NOT set connector.line.* before injecting XML — that creates a
      conflicting a:ln element and produces invalid XML (PowerPoint repair).
    - Build the complete a:ln element as XML string and append once.
    - tailEnd (= destination end) carries the arrow; headEnd is omitted.
    """
    connector = slide.shapes.add_connector(
        MSO_CONNECTOR_TYPE.STRAIGHT, x1, y1, x2, y2
    )

    cxnSp = connector.element
    spPr  = cxnSp.find(qn("p:spPr"))

    # Remove any a:ln that python-pptx may have auto-inserted
    for existing in spPr.findall(qn("a:ln")):
        spPr.remove(existing)

    color_val = color_hex.lstrip("#")
    line_w    = int(Pt(width_pt))          # EMU (1 pt = 12700 EMU)
    dash_part = ('<a:prstDash xmlns:a="{ns}" val="dash"/>'
                 .format(ns=A_NS)) if dashed else ""

    ln_xml = (
        f'<a:ln xmlns:a="{A_NS}" w="{line_w}">'
        f'  <a:solidFill>'
        f'    <a:srgbClr val="{color_val}"/>'
        f'  </a:solidFill>'
        f'  {dash_part}'
        f'  <a:tailEnd type="arrow" w="med" len="med"/>'
        f'</a:ln>'
    )
    spPr.append(etree.fromstring(ln_xml))

    if label:
        mx = (x1 + x2) / 2
        my = (y1 + y2) / 2
        add_textbox(slide, mx, my - Inches(0.12), Inches(1.5), Inches(0.22),
                    label, font_size=label_size, color=label_color,
                    align=PP_ALIGN.LEFT, italic=True)

    return connector


def slide_bg(slide, hex_color):
    """Set slide background colour."""
    background = slide.background
    fill = background.fill
    fill.solid()
    fill.fore_color.rgb = rgb(hex_color)


def section_label(slide, l, t, text, size=13):
    add_textbox(slide, l, t, Inches(14), Inches(0.35), text,
                font_size=size, bold=True, color=C_HW, align=PP_ALIGN.LEFT)


# ═════════════════════════════════════════════════════════════════
#  PRESENTATION
# ═════════════════════════════════════════════════════════════════
prs = Presentation()
prs.slide_width  = SLD_W
prs.slide_height = SLD_H

BLANK = prs.slide_layouts[6]  # blank

def I(v): return Inches(v)


# ═════════════════════════════════════════════════════════════════
#  SLIDE 1 — PANEL A  State Machine
# ═════════════════════════════════════════════════════════════════
sl_a = prs.slides.add_slide(BLANK)
slide_bg(sl_a, C_BG)

# Title
add_textbox(sl_a, I(0.2), I(0.05), I(21.6), I(0.35),
            "Conveyor-Fed Automatic PCB Test Station — System Flow Diagram",
            font_size=20, bold=True, color=C_HW, align=PP_ALIGN.CENTER)
add_textbox(sl_a, I(0.2), I(0.42), I(21.6), I(0.25),
            "SmartBU / XNF I460  |  BMW MAE Project 032080790003  |  "
            "Conveyor_AutoLoader_Fixture_BOM_Rev1.0  |  Charan Singh  |  11.05.2026",
            font_size=8, bold=False, color="#555555", align=PP_ALIGN.CENTER)

section_label(sl_a, I(0.3), I(0.72), "A  —  Station State Machine (Operational Flow)")

# ── State boxes ─────────────────────────────────────────────────
BW, BH = I(1.65), I(1.1)   # box width / height
ROW1_Y = I(1.3)
ROW2_Y = I(4.35)

states_r1 = [
    (I(0.25), ROW1_Y, " 1  IDLE",           "Conveyor runs\nLight: YELLOW",     C_IDLE),
    (I(2.10), ROW1_Y, " 2  PCB ARRIVING",   "Entry sensor\ntriggered",           C_ACTION),
    (I(3.95), ROW1_Y, " 3  PCB POSITIONED", "Centre sensor\nconfirmed",          C_ACTION),
    (I(5.80), ROW1_Y, " 4  BARCODE SCAN",   "Scanner reads\nDataMatrix",         C_SPECIAL),
    (I(7.65), ROW1_Y, " 5  PRESS CLOSING",  "Cylinder extends\nPogopin contact", C_ACTION),
    (I(9.50), ROW1_Y, " 6  CONN. MATING",   "3× connector\ncylinders extend",   C_ACTION),
    (I(11.35),ROW1_Y, " 7  TESTING",        "orchestrator.py\nfull test seq.",   C_INST),
]
states_r2 = [
    (I(11.35),ROW2_Y, " 8  PRESS OPENING",  "Connectors then\npress retract",   C_ACTION),
    (I(9.50), ROW2_Y, " 9  RESULT OUTPUT",  "PASS→main line\nFAIL→reject tray", C_SPECIAL),
    (I(7.65), ROW2_Y, "10  LOGGING",        "MySQL write\nHTML report",          C_PC),
    (I(5.80), ROW2_Y, "11  IDLE (reset)",   "Returns to\nIDLE state",            C_IDLE),
]
fault = (I(13.50), I(2.85), "12  FAULT", "E-stop / curtain\nbreach / timeout",  C_SAFETY)

for lx, ty, lbl, sub, col in states_r1 + states_r2:
    add_rounded_box(sl_a, lx, ty, BW, BH, col,
                    [lbl, sub],
                    font_sizes=[10, 8], bold_flags=[True, False])

add_rounded_box(sl_a, fault[0], fault[1], BW, BH, fault[4],
                [fault[2], fault[3]],
                font_sizes=[10, 8], bold_flags=[True, False])

# Row 1 arrows (left to right)
CX = BW / 2   # centre-x offset
CY = BH / 2
GAP = I(0.15)
for (lx1, ty1, *_), (lx2, ty2, *_) in zip(states_r1, states_r1[1:]):
    add_arrow(sl_a,
              lx1 + BW, ty1 + CY,
              lx2,      ty2 + CY,
              color_hex=C_ARROW)

# Turn: state 7 down to state 8
add_arrow(sl_a,
          states_r1[-1][0] + CX, states_r1[-1][1] + BH,
          states_r2[0][0]  + CX, states_r2[0][1],
          color_hex=C_ARROW)

# Row 2 arrows (right to left)
for (lx1, ty1, *_), (lx2, ty2, *_) in zip(states_r2, states_r2[1:]):
    add_arrow(sl_a,
              lx1,       ty1 + CY,
              lx2 + BW,  ty2 + CY,
              color_hex=C_ARROW)

# IDLE reset loops back to State 1 (up)
add_arrow(sl_a,
          states_r2[-1][0] + CX, states_r2[-1][1],
          states_r1[0][0]  + CX, states_r1[0][1] + BH,
          color_hex=C_IDLE)

# FAULT arrows from State 4 and State 5
add_arrow(sl_a,
          states_r1[3][0] + BW, states_r1[3][1] + CY,
          fault[0],              fault[1] + CY,
          color_hex=C_SAFETY, label="timeout / invalid", label_color=C_SAFETY)
add_arrow(sl_a,
          states_r1[4][0] + BW, states_r1[4][1] + CY,
          fault[0],              fault[1] + BH * 0.75,
          color_hex=C_SAFETY, label="low pressure", label_color=C_SAFETY)

# FAULT → IDLE (operator reset)
add_arrow(sl_a,
          fault[0] + CX, fault[1],
          states_r1[0][0] + CX, states_r1[0][1],
          color_hex=C_SAFETY, dashed=True,
          label="operator reset", label_color=C_SAFETY, label_size=7)

# Legend
LLEG_X = I(0.3)
LLEG_Y = I(6.2)
legend = [
    (C_IDLE,    "Idle / Ready"),
    (C_ACTION,  "Hardware Action"),
    (C_SPECIAL, "Decision / Branch"),
    (C_INST,    "Test Instruments"),
    (C_PC,      "Software / Logging"),
    (C_SAFETY,  "Fault / Safety"),
]
for i, (col, lbl) in enumerate(legend):
    lx = LLEG_X + I(2.6 * i)
    add_rounded_box(sl_a, lx, LLEG_Y, I(2.3), I(0.38), col,
                    [lbl], font_sizes=[9], bold_flags=[False])

# State 6 callout note
add_rounded_box(sl_a, I(0.25), I(5.55), I(5.8), I(0.58),
                "#D6EAF8",
                ["State 6 — CONNECTOR MATING detail",
                 "After press plate lands: 3 pneumatic cylinders (Ø16mm) extend sequentially.\n"
                 "DO0.3 → DO0.4 → DO0.5.  Press FIRST, then connectors.  Settle: 0.5 s."],
                font_sizes=[8, 7], bold_flags=[True, False],
                text_color="#21618C", border_hex="#21618C", border_pt=1.0,
                align=PP_ALIGN.LEFT, v_anchor="top")


# ═════════════════════════════════════════════════════════════════
#  SLIDE 2 — PANEL B  System Architecture
# ═════════════════════════════════════════════════════════════════
sl_b = prs.slides.add_slide(BLANK)
slide_bg(sl_b, C_BG)

add_textbox(sl_b, I(0.2), I(0.05), I(21.6), I(0.35),
            "Conveyor-Fed Automatic PCB Test Station — System Architecture",
            font_size=20, bold=True, color=C_HW, align=PP_ALIGN.CENTER)
add_textbox(sl_b, I(0.2), I(0.42), I(21.6), I(0.25),
            "SmartBU / XNF I460  |  BMW MAE Project 032080790003  |  "
            "Conveyor_AutoLoader_Fixture_BOM_Rev1.0  |  Charan Singh  |  11.05.2026",
            font_size=8, bold=False, color="#555555", align=PP_ALIGN.CENTER)

section_label(sl_b, I(0.3), I(0.72),
              "B  —  System Architecture  (mapped to System Overview sheet)")

# ── Horizontal PCB transport flow ────────────────────────────────
FBW, FBH = I(2.9), I(0.9)
FY = I(1.2)
flow = [
    (I(0.25),  "UPSTREAM CONVEYOR",  "Belt 600mm · 24VDC",       "States 1-2", C_HW),
    (I(3.35),  "PCB STOPPERS",       "Entry + Exit (Ø10mm cyl.)", "State 3",   "#34495E"),
    (I(6.45),  "BARCODE SCANNER",    "2D DataMatrix · USB HID",   "State 4",   C_SPECIAL),
    (I(9.55),  "PRESS STATION",      "Ø80mm cyl. + pogo carrier", "States 5-8","#1A5276"),
    (I(12.65), "EXIT / REJECT GATE", "PASS→main  FAIL→tray",      "States 9-10",C_ACTION),
]

for lx, title, sub, sref, col in flow:
    add_rounded_box(sl_b, lx, FY, FBW, FBH, col,
                    [title, sub, f"[{sref}]"],
                    font_sizes=[10, 8, 7], bold_flags=[True, False, False])

# Arrows between flow boxes
for (lx1, *_), (lx2, *_) in zip(flow, flow[1:]):
    add_arrow(sl_b, lx1 + FBW, FY + FBH/2, lx2, FY + FBH/2, color_hex=C_ARROW)

# Vertical chain below Press Station (centre = lx of press + half width)
PRESS_CX = flow[3][0] + FBW/2
V_BOXES = [
    (I(2.0),  "PNEUMATIC PRESS  (BOM §2-§5)",
     "• Cylinder Ø80mm, ~500N @ 5 bar  (item 6) — 5/2 solenoid valve\n"
     "• Top press plate + pogo-pin carrier (29 pins)  (items 8, 23-24)\n"
     "• 3× Connector plug-in cylinders Ø16mm  (item 26)\n"
     "• FRL unit + pressure sensor + flow control  (items 15-17)",
     "#1A5276"),
    (I(1.5),  "TEST INSTRUMENTS  (BOM §8)",
     "• KIKUSUI PWR401L — 12V / 3.8V DC supply to DUT\n"
     "• Lauterbach Trace32 — SWD/JTAG firmware flash + debug\n"
     "• PEAK PCAN-USB — CAN-H / CAN-L bus\n"
     "• PLIN-USB — LIN bus communication with DUT",
     C_INST),
    (I(1.4),  "TEST PC  (BOM §10)  —  orchestrator.py",
     "• orchestrator.py — sequences PSU→Flash→CAN→LIN→Motor→EOS→NFC\n"
     "• gui_main.py  |  barcode_utils.py  |  trace32_adapter.py\n"
     "• can_service · lin_service · motor_service · nfc_service\n"
     "• MySQL client — logs result, barcode, variant, time  |  HTML report",
     C_PC),
]

VBW = I(7.5)
curr_y = FY + FBH + I(0.25)
v_centres = []
for bh_val, title, body, col in V_BOXES:
    lx = PRESS_CX - VBW/2
    add_rounded_box(sl_b, lx, curr_y, VBW, bh_val, col,
                    [title, body],
                    font_sizes=[10, 8], bold_flags=[True, False],
                    align=PP_ALIGN.LEFT, v_anchor="top")
    v_centres.append((lx, curr_y, VBW, bh_val))
    if curr_y < I(12.5):
        add_arrow(sl_b, PRESS_CX, curr_y + bh_val, PRESS_CX, curr_y + bh_val + I(0.25),
                  color_hex=C_ARROW)
    curr_y += bh_val + I(0.3)

# PASS / FAIL split
SPLIT_Y = curr_y
PASS_X  = PRESS_CX - I(2.8)
FAIL_X  = PRESS_CX + I(2.8)
add_arrow(sl_b, PRESS_CX, SPLIT_Y, PASS_X, SPLIT_Y + I(0.3), color_hex=C_ACTION)
add_arrow(sl_b, PRESS_CX, SPLIT_Y, FAIL_X, SPLIT_Y + I(0.3), color_hex=C_SAFETY)

add_rounded_box(sl_b, PASS_X - I(1.4), SPLIT_Y + I(0.3), I(2.8), I(0.55),
                C_ACTION, ["PASS  →  Exit Conveyor", "Light GREEN  ·  DO1.0 ON"],
                font_sizes=[10, 8], bold_flags=[True, False])
add_rounded_box(sl_b, FAIL_X - I(1.4), SPLIT_Y + I(0.3), I(2.8), I(0.55),
                C_SAFETY, ["FAIL  →  Reject Tray", "Light RED  ·  DO0.6 GATE"],
                font_sizes=[10, 8], bold_flags=[True, False])

# PLC sidebar (left)
add_rounded_box(sl_b, I(0.25), FY + I(0.6), I(3.5), I(6.0),
                "#117A65",
                ["PLC CONTROL UNIT  (BOM §6)",
                 "Siemens S7-1200  1214C DC/DC/DC\n"
                 "14 DI  /  10 DO  /  2 AI  (24VDC)\n\n"
                 "DO → Solenoid valves (press + stoppers\n"
                 "      + connector actuators)\n"
                 "DO → Reject gate  ·  Conveyor run\n"
                 "DO → Tower light (R/Y/G) + Buzzer\n"
                 "DI ← Photoelectric sensors (×2)\n"
                 "DI ← Cylinder reed sensors (×2)\n"
                 "DI ← Light curtain OSSD\n"
                 "DI ← E-stop NC  ·  Air pressure OK\n\n"
                 "Ethernet → HMI  |  Ethernet → Test PC"],
                font_sizes=[10, 8], bold_flags=[True, False],
                align=PP_ALIGN.LEFT, v_anchor="top")

# Safety sidebar (right)
add_rounded_box(sl_b, I(18.0), FY + I(0.6), I(3.7), I(4.0),
                C_SAFETY,
                ["SAFETY LAYER  (BOM §11-§12)",
                 "• Safety Light Curtain (item 51)\n"
                 "  OSSD dual output → Safety relay\n"
                 "• E-stop mushroom (item 53) — NC chain\n"
                 "• Pneumatic pressure switch (item 17)\n"
                 "• Safety relay module (item 52)\n\n"
                 "Press BLOCKED unless:\n"
                 "  ✓ E-stop OK  (NC chain intact)\n"
                 "  ✓ Air pressure ≥ 4 bar\n"
                 "  ✓ Light curtain clear"],
                font_sizes=[10, 8], bold_flags=[True, False],
                align=PP_ALIGN.LEFT, v_anchor="top")

# NFC note
add_rounded_box(sl_b, I(0.25), SPLIT_Y + I(0.3), I(3.5), I(0.55),
                C_NFC,
                ["NFC SUBSYSTEM  (BOM §14)",
                 "Servo ×2 + card holder  |  nfc_service.py  |  NFC LH/RH variants only"],
                font_sizes=[10, 8], bold_flags=[True, False],
                align=PP_ALIGN.LEFT)

# ── Legend for Panel B ────────────────────────────────────────────
LB_Y = I(12.3)
add_textbox(sl_b, I(0.3), LB_Y, I(8.0), I(0.28),
            "Arrow legend:", font_size=8, bold=True, color=C_HW)
add_textbox(sl_b, I(0.3), LB_Y + I(0.28), I(12.0), I(0.22),
            "Solid → PCB / signal flow direction (main process path)", font_size=8, color="#222222")
add_textbox(sl_b, I(0.3), LB_Y + I(0.50), I(12.0), I(0.22),
            "Green dashed → PLC control signal", font_size=8, color="#117A65")
add_textbox(sl_b, I(0.3), LB_Y + I(0.72), I(12.0), I(0.22),
            "Red dashed → Safety enable condition (press BLOCKED until all safety conditions met)",
            font_size=8, color=C_SAFETY)


# ═════════════════════════════════════════════════════════════════
#  SLIDE 3 — PANEL C  Test Sequence Detail
# ═════════════════════════════════════════════════════════════════
sl_c = prs.slides.add_slide(BLANK)
slide_bg(sl_c, C_BG)

add_textbox(sl_c, I(0.2), I(0.05), I(21.6), I(0.35),
            "Conveyor-Fed Automatic PCB Test Station — Test Sequence Detail",
            font_size=20, bold=True, color=C_HW, align=PP_ALIGN.CENTER)
add_textbox(sl_c, I(0.2), I(0.42), I(21.6), I(0.25),
            "SmartBU / XNF I460  |  BMW MAE Project 032080790003  |  "
            "Conveyor_AutoLoader_Fixture_BOM_Rev1.0  |  Charan Singh  |  11.05.2026",
            font_size=8, bold=False, color="#555555", align=PP_ALIGN.CENTER)

section_label(sl_c, I(0.3), I(0.72),
              "C  —  Test Sequence Detail  (TESTING State Expanded)")

# State 6 block
add_rounded_box(sl_c, I(0.25), I(1.1), I(10.0), I(0.85),
                "#21618C",
                ["STATE 6: CONNECTOR MATING  (before testing starts)",
                 "PLC energises DO0.3 → DO0.4 → DO0.5 sequentially  |  3× Ø16mm cylinders extend  |  "
                 "Each cylinder mates one DUT edge connector (motor DB9, LIN terminal, supply header)  |  "
                 "Settle time: 0.5 s  |  Connector CLOSED sensors confirm all 3 mated  |  THEN testing begins"],
                font_sizes=[10, 8], bold_flags=[True, False],
                align=PP_ALIGN.LEFT, v_anchor="top")

# Test steps swimlane
steps = [
    ("T1", "PSU ON — Apply 12V / 3.8V to DUT",         "KIKUSUI PWR401L",    "~2s",  "#1A5276"),
    ("T2", "Trace32 connect — SWD link check",          "Lauterbach Trace32", "~3s",  "#154360"),
    ("T3", "Flash firmware via SWD",                    "Lauterbach Trace32", "~30s", "#154360"),
    ("T4", "CAN communication test",                    "PCAN-USB",           "~10s", "#4A235A"),
    ("T5", "LIN bus communication test",                "PLIN-USB",           "~10s", "#4A235A"),
    ("T6", "Motor drive test (SG1/SG2/Cap relay)",      "Relay board + PSU",  "~15s", "#7D6608"),
    ("T7", "EOS / LED / NFC antenna test",              "EOS board / Servo",  "~10s", "#784212"),
]

STEP_Y0 = I(2.1)
STEP_H  = I(0.82)
STEP_GAP = I(0.1)
STEP_W  = I(7.5)

for i, (sno, lbl, instrument, dur, col) in enumerate(steps):
    ty = STEP_Y0 + i * (STEP_H + STEP_GAP)
    add_rounded_box(sl_c, I(0.25), ty, STEP_W, STEP_H, col,
                    [f"{sno}  {lbl}", f"{instrument}  |  {dur}"],
                    font_sizes=[10, 8], bold_flags=[True, False],
                    align=PP_ALIGN.LEFT)
    # Connector arrow between steps
    if i < len(steps) - 1:
        add_arrow(sl_c,
                  I(0.25) + STEP_W/2, ty + STEP_H,
                  I(0.25) + STEP_W/2, ty + STEP_H + STEP_GAP,
                  color_hex=C_ARROW)

# ── PLC I/O Map Table (right half) ───────────────────────────────
TBL_X  = I(8.2)
TBL_W  = I(13.4)
TBL_Y0 = I(1.1)
ROW_H  = I(0.38)
COLS   = [I(0.6), I(1.1), I(2.6), I(3.8), I(1.4), I(1.8)]  # col widths
COL_LABELS = ["I/O", "Channel", "Signal Name", "Connected Device", "0=", "1="]

# Header
hx = TBL_X
for cw, clbl in zip(COLS, COL_LABELS):
    add_rounded_box(sl_c, hx, TBL_Y0, cw - I(0.04), ROW_H - I(0.02),
                    C_HW, [clbl], font_sizes=[8], bold_flags=[True],
                    border_hex=C_HW, border_pt=0.5)
    hx += cw

io_rows = [
    ("DI", "DI0.0", "PCB_ENTRY_DETECT",    "Entry sensor (item 4)",     "No PCB",   "PCB detected"),
    ("DI", "DI0.1", "PCB_POSITION_DETECT", "Centre sensor (item 4)",    "No PCB",   "PCB at station"),
    ("DI", "DI0.2", "PRESS_OPEN_SENSE",    "Cylinder OPEN reed (12)",   "Not open", "Press open"),
    ("DI", "DI0.3", "PRESS_CLOSED_SENSE",  "Cylinder CLOSED reed (12)", "Not clsd", "Press closed"),
    ("DI", "DI0.4", "LIGHT_CURTAIN_OSSD",  "Safety light curtain (51)", "Breach",   "Clear"),
    ("DI", "DI0.5", "ESTOP_OK",            "E-stop NC chain (53)",      "Pressed",  "OK"),
    ("DI", "DI0.6", "AIR_PRESSURE_OK",     "Pressure switch (17)",      "Low",      "OK"),
    ("DI", "DI0.7", "PCB_EXIT_DETECT",     "Exit sensor",               "No PCB",   "PCB present"),
    ("DO", "DO0.0", "PRESS_SOL_VALVE",     "Press cylinder valve (13)", "Retract",  "Extend"),
    ("DO", "DO0.1", "STOPPER_ENTRY_SOL",   "Entry stopper valve (13)",  "Down",     "Up"),
    ("DO", "DO0.2", "STOPPER_EXIT_SOL",    "Exit stopper valve (13)",   "Down",     "Up"),
    ("DO", "DO0.3", "CONN_SOL_1",          "Connector 1 valve (28)",    "Retract",  "Extend"),
    ("DO", "DO0.4", "CONN_SOL_2",          "Connector 2 valve (28)",    "Retract",  "Extend"),
    ("DO", "DO0.5", "CONN_SOL_3",          "Connector 3 valve (28)",    "Retract",  "Extend"),
    ("DO", "DO0.6", "REJECT_GATE_SOL",     "Reject gate (item 56)",     "Closed",   "Open(FAIL)"),
    ("DO", "DO0.7", "CONVEYOR_RUN",        "Conveyor drive (item 2)",   "Stop",     "Run"),
    ("DO", "DO1.0", "LIGHT_GREEN",         "Tower light (54)",          "Off",      "PASS"),
    ("DO", "DO1.1", "LIGHT_YELLOW",        "Tower light (54)",          "Off",      "BUSY"),
    ("DO", "DO1.2", "LIGHT_RED",           "Tower light (54)",          "Off",      "FAIL/FAULT"),
    ("DO", "DO1.3", "BUZZER",              "Tower light (54)",          "Silent",   "Alert"),
]

for r, row in enumerate(io_rows):
    ty = TBL_Y0 + (r + 1) * ROW_H
    bg_hex = "#D6EAF8" if row[0] == "DI" else "#D5F5E3"
    txt_hex = "#1A5276" if row[0] == "DI" else "#196F3D"
    hx = TBL_X
    for cw, cell in zip(COLS, row):
        add_rounded_box(sl_c, hx, ty, cw - I(0.04), ROW_H - I(0.02),
                        bg_hex, [cell], font_sizes=[7.5], bold_flags=[False],
                        text_color=txt_hex, border_hex="#BDC3C7", border_pt=0.5,
                        align=PP_ALIGN.LEFT)
        hx += cw

# Software stack note
add_rounded_box(sl_c, I(0.25), I(12.1), I(21.5), I(0.55),
                "#EBF5FB",
                ["SOFTWARE STACK (already developed):",
                 "barcode_utils.py  ·  orchestrator.py  ·  trace32_adapter.py  ·  "
                 "can_service.py  ·  lin_service.py  ·  motor_service.py  ·  "
                 "nfc_service.py  ·  sg_service.py  ·  eos_service.py  ·  "
                 "report_generator.py  ·  MySQL integration"],
                font_sizes=[9, 8], bold_flags=[True, False],
                text_color=C_PC, border_hex=C_PC, border_pt=0.8,
                align=PP_ALIGN.LEFT, v_anchor="top")


# ═════════════════════════════════════════════════════════════════
#  SAVE
# ═════════════════════════════════════════════════════════════════
out_dir  = os.path.dirname(os.path.abspath(__file__))
out_pptx = os.path.join(out_dir, "Conveyor_AutoLoader_Flow_Diagram_Rev1.0_Editable.pptx")
prs.save(out_pptx)
print(f"Saved: {out_pptx}")
print("All shapes (boxes, arrows, text) are native PowerPoint objects.")
print("Click any element to select and edit it directly in PowerPoint.")
