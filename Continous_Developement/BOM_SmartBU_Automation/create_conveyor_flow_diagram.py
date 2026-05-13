"""
create_conveyor_flow_diagram.py
Generates a multi-panel flow diagram for the Conveyor-Fed Automatic PCB Test Station.
Output: Conveyor_AutoLoader_Flow_Diagram_Rev1.0.png  (saved next to this script)

Panel A — Station State Machine (main operational flow)
Panel B — System Architecture Overview (hardware subsystems)
Panel C — Test Sequence Detail (TESTING state expanded)
"""

import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
import matplotlib.patheffects as pe

# ──────────────────────────────────────────────────────────────────
# Colour palette
# ──────────────────────────────────────────────────────────────────
C_IDLE    = "#4A90D9"   # blue  – idle / ready
C_ACTION  = "#27AE60"   # green – normal action states
C_SAFETY  = "#E74C3C"   # red   – fault / safety
C_SPECIAL = "#F39C12"   # amber – decision / branch
C_INST    = "#8E44AD"   # purple – instruments
C_PC      = "#16A085"   # teal  – software / PC
C_HW      = "#2C3E50"   # dark  – hardware structure
C_NFC     = "#D35400"   # orange – NFC subsystem
C_BG      = "#F8F9FA"   # light grey background
C_ARROW   = "#555555"   # arrow colour

FONT = "DejaVu Sans"


# ══════════════════════════════════════════════════════════════════
#  HELPER FUNCTIONS
# ══════════════════════════════════════════════════════════════════

def state_box(ax, x, y, w, h, label, sublabel, color, fontsize=9):
    """Draw a rounded state box with a main label and an optional sub-label."""
    box = FancyBboxPatch((x - w/2, y - h/2), w, h,
                         boxstyle="round,pad=0.04",
                         facecolor=color, edgecolor="white",
                         linewidth=1.5, zorder=3)
    ax.add_patch(box)
    ax.text(x, y + (0.06 if sublabel else 0), label,
            ha="center", va="center", fontsize=fontsize,
            fontweight="bold", color="white", zorder=4,
            fontfamily=FONT)
    if sublabel:
        ax.text(x, y - 0.10, sublabel,
                ha="center", va="center", fontsize=fontsize - 2,
                color="white", alpha=0.88, zorder=4,
                fontfamily=FONT, style="italic")


def arrow(ax, x1, y1, x2, y2, label="", color=C_ARROW, lw=1.5,
          arrowstyle="-|>", bend=0.0):
    """Draw an annotated arrow."""
    ax.annotate("",
                xy=(x2, y2), xytext=(x1, y1),
                arrowprops=dict(arrowstyle=arrowstyle,
                                color=color, lw=lw,
                                connectionstyle=f"arc3,rad={bend}"),
                zorder=2)
    if label:
        mx, my = (x1 + x2) / 2, (y1 + y2) / 2
        ax.text(mx + 0.05, my, label, ha="left", va="center",
                fontsize=7, color=color, fontfamily=FONT, zorder=5)


def hw_box(ax, x, y, w, h, title, items, color, fontsize=8):
    """Draw a hardware subsystem box with a title and bullet items."""
    bg = FancyBboxPatch((x, y), w, h,
                        boxstyle="round,pad=0.03",
                        facecolor=color, edgecolor="white",
                        linewidth=1.2, zorder=3, alpha=0.92)
    ax.add_patch(bg)
    ax.text(x + w/2, y + h - 0.08, title,
            ha="center", va="top", fontsize=fontsize,
            fontweight="bold", color="white", zorder=4, fontfamily=FONT)
    for i, item in enumerate(items):
        ax.text(x + 0.07, y + h - 0.20 - i * 0.115,
                f"• {item}", ha="left", va="top",
                fontsize=fontsize - 1.5, color="white", zorder=4,
                fontfamily=FONT)


# ══════════════════════════════════════════════════════════════════
#  FIGURE SETUP  (3 rows: A top, B middle, C bottom)
# ══════════════════════════════════════════════════════════════════

fig = plt.figure(figsize=(22, 30), facecolor=C_BG)
fig.patch.set_facecolor(C_BG)

# Title
fig.text(0.5, 0.985,
         "Conveyor-Fed Automatic PCB Test Station — System Flow Diagram",
         ha="center", va="top", fontsize=17, fontweight="bold",
         color=C_HW, fontfamily=FONT)
fig.text(0.5, 0.977,
         "SmartBU / XNF I460  |  BMW MAE Project 032080790003  |  "
         "Conveyor_AutoLoader_Fixture_BOM_Rev1.0  |  Charan Singh  |  11.05.2026",
         ha="center", va="top", fontsize=9, color="#555555", fontfamily=FONT)

# Divider lines
for yp in [0.675, 0.36]:
    fig.add_artist(plt.Line2D([0.04, 0.96], [yp, yp],
                              transform=fig.transFigure,
                              color="#CCCCCC", lw=1))

# Panel labels
for yp, lbl in [(0.965, "A  —  Station State Machine (Operational Flow)"),
                (0.655, "B  —  System Architecture (mapped to System Overview sheet)"),
                (0.345, "C  —  Test Sequence Detail  (TESTING State Expanded)")]:
    fig.text(0.04, yp, lbl, fontsize=11, fontweight="bold",
             color=C_HW, va="top", fontfamily=FONT)


# ══════════════════════════════════════════════════════════════════
#  PANEL A  —  State Machine
# ══════════════════════════════════════════════════════════════════
ax_a = fig.add_axes([0.03, 0.69, 0.94, 0.275])
ax_a.set_xlim(0, 11.0)
ax_a.set_ylim(-0.65, 1.6)
ax_a.axis("off")
ax_a.set_facecolor(C_BG)

# States layout: two rows, left→right then right→left (snake)
# Row 1 (y=1.1): IDLE  PCB_ARRIVING  PCB_POSITIONED  BARCODE_SCAN  PRESS_CLOSING  CONNECTOR_MATING
# Row 2 (y=0.2): LOGGING  IDLE(loop)  RESULT_OUTPUT  PRESS_OPENING  TESTING

SH, SW = 0.28, 1.45  # box height, width

states_r1 = [
    (0.80,  1.1, " 1  IDLE",           "Conveyor runs\nLight: YELLOW",     C_IDLE),
    (2.40,  1.1, " 2  PCB ARRIVING",   "Entry sensor\ntriggered",           C_ACTION),
    (4.00,  1.1, " 3  PCB POSITIONED", "Centre sensor\nconfirmed",          C_ACTION),
    (5.60,  1.1, " 4  BARCODE SCAN",   "Scanner reads\nDataMatrix",         C_SPECIAL),
    (7.20,  1.1, " 5  PRESS CLOSING",  "Cylinder extends\nPogopin contact", C_ACTION),
    (8.80,  1.1, " 6  CONN. MATING",   "3x connector\ncylinders extend",   C_ACTION),
]

states_r2 = [
    (10.20, 0.25, " 7  TESTING",        "orchestrator.py\nfull test seq.",  C_INST),
    (8.80,  0.25, " 8  PRESS OPENING",  "Connectors then\npress retract",   C_ACTION),
    (7.20,  0.25, " 9  RESULT OUTPUT",  "PASS->main line\nFAIL->reject tray", C_SPECIAL),
    (5.60,  0.25, "10  LOGGING",        "MySQL write\nHTML report",         C_PC),
    (0.80,  0.25, "  IDLE (reset)",   "← returns to\nIDLE state",         C_IDLE),
]

fault_state = (10.20, 1.1, "11  FAULT", "E-stop / curtain\nbreach / timeout", C_SAFETY)

for x, y, lbl, sub, col in states_r1:
    state_box(ax_a, x, y, SW, SH, lbl, sub, col)

for x, y, lbl, sub, col in states_r2:
    state_box(ax_a, x, y, SW, SH, lbl, sub, col)

state_box(ax_a, *fault_state[:2], SW, SH, fault_state[2], fault_state[3], fault_state[4])

# Row 1 forward arrows
for (x1, y1, *_), (x2, y2, *_) in zip(states_r1, states_r1[1:]):
    arrow(ax_a, x1 + SW/2, y1, x2 - SW/2, y2, color=C_ARROW)

# Turn-corner: CONN_MATING → TESTING (down)
arrow(ax_a, 8.80, 1.1 - SH/2, 10.20, 0.25 + SH/2, color=C_ARROW)

# Row 2 backward arrows (right to left)
for (x1, y1, *_), (x2, y2, *_) in zip(states_r2, states_r2[1:]):
    arrow(ax_a, x1 - SW/2, y1, x2 + SW/2, y2, color=C_ARROW)

# LOGGING → IDLE loop arrow (below)
ax_a.annotate("", xy=(0.80 + SW/2, 0.25),
              xytext=(5.60 - SW/2, 0.25),
              arrowprops=dict(arrowstyle="-|>", color=C_IDLE, lw=1.8,
                              connectionstyle="arc3,rad=-0.0"), zorder=2)

# IDLE loop back to row1 start (top loop)
ax_a.annotate("", xy=(0.80, 1.1 + SH/2),
              xytext=(0.80, 0.25 + SH/2),
              arrowprops=dict(arrowstyle="-|>", color=C_IDLE, lw=1.8,
                              connectionstyle="arc3,rad=0.4"), zorder=2)

# FAULT arrows: from BARCODE_SCAN, PRESS_CLOSING
arrow(ax_a, 5.60, 1.1 + SH/2, 10.20, 1.1, "timeout/invalid", C_SAFETY, bend=0.2)
arrow(ax_a, 7.20, 1.1 + SH/2, 10.20, 1.1, "low pressure /\ncurtain breach", C_SAFETY, bend=0.1)

# FAULT → IDLE reset
ax_a.annotate("", xy=(0.80, 1.1 + SH/2),
              xytext=(10.20, 1.1 + SH/2),
              arrowprops=dict(arrowstyle="-|>", color=C_SAFETY, lw=1.5,
                              connectionstyle="arc3,rad=-0.35",
                              linestyle="dashed"), zorder=2)
ax_a.text(5.5, 1.58, "operator reset after fault",
          ha="center", fontsize=7, color=C_SAFETY, fontfamily=FONT)

# State 6 callout annotation — explain what CONNECTOR MATING means
ax_a.annotate(
    "State 6 detail:\n"
    "After press plate lands on PCB (pogo pins contact),\n"
    "3 pneumatic cylinders (Ø16mm) extend sequentially\n"
    "to plug the DUT edge connectors (motor DB9, LIN\n"
    "terminal, supply header) into the PCB.\n"
    "PLC: DO0.3, DO0.4, DO0.5 energised in sequence.\n"
    "Press FIRST — then connectors (prevents damage).",
    xy=(8.80, 1.1 - SH/2),
    xytext=(8.80, -0.38),
    fontsize=6.5, color="#21618C", fontfamily=FONT,
    ha="center", va="top",
    bbox=dict(boxstyle="round,pad=0.3", facecolor="#D6EAF8",
              edgecolor="#21618C", linewidth=1.0, alpha=0.92),
    arrowprops=dict(arrowstyle="->", color="#21618C", lw=1.2),
    zorder=6)

# Legend row A
legend_items = [
    mpatches.Patch(color=C_IDLE,    label="Idle / Ready"),
    mpatches.Patch(color=C_ACTION,  label="Hardware Action"),
    mpatches.Patch(color=C_SPECIAL, label="Decision / Branch"),
    mpatches.Patch(color=C_INST,    label="Test Instruments"),
    mpatches.Patch(color=C_PC,      label="Software / Logging"),
    mpatches.Patch(color=C_SAFETY,  label="Fault / Safety"),
]
ax_a.legend(handles=legend_items, loc="lower center",
            ncol=6, fontsize=7.5, framealpha=0.6,
            bbox_to_anchor=(0.5, -0.25))


# ══════════════════════════════════════════════════════════════════
#  PANEL B  —  System Architecture  (mapped to "System Overview" sheet)
#  Layout mirrors the System Overview ASCII art exactly:
#   Physical PCB flow (horizontal) → Pneumatic Press → Test Instruments
#   → Test PC → PASS/FAIL split
#   Safety layer and PLC shown as cross-cutting control sidebars
# ══════════════════════════════════════════════════════════════════
ax_b = fig.add_axes([0.03, 0.375, 0.94, 0.280])
ax_b.set_xlim(0, 22)
ax_b.set_ylim(-0.55, 6.5)
ax_b.axis("off")
ax_b.set_facecolor(C_BG)

# ── helper: rounded box with title + bullets (centre anchor) ─────
def vbox(ax, xc, yc, w, h, title, items, col, fs=7.8):
    bg = FancyBboxPatch((xc - w/2, yc - h/2), w, h,
                        boxstyle="round,pad=0.04",
                        facecolor=col, edgecolor="white", linewidth=1.5, zorder=3)
    ax.add_patch(bg)
    ax.text(xc, yc + h/2 - 0.11, title,
            ha="center", va="top", fontsize=fs, fontweight="bold",
            color="white", zorder=4, fontfamily=FONT)
    for i, it in enumerate(items):
        ax.text(xc - w/2 + 0.13, yc + h/2 - 0.26 - i * 0.195,
                f"• {it}", ha="left", va="top", fontsize=fs - 1.5,
                color="white", zorder=4, fontfamily=FONT)

# ── helper: state-reference badge ────────────────────────────────
def state_ref(ax, xc, y, text, col):
    ax.text(xc, y, text, ha="center", va="center", fontsize=6.2,
            color=col, fontfamily=FONT, style="italic",
            bbox=dict(boxstyle="round,pad=0.18", facecolor="white",
                      edgecolor=col, linewidth=0.8, alpha=0.85))

# ══ ROW 1 — Physical PCB Transport Flow (horizontal strip) ═══════
FBW, FBH = 2.6, 0.82   # flow-box width, height
FY = 5.85               # y-centre of horizontal flow row

flow_items = [
    # xc,   label,                   sub,                       state_ref,            colour
    (1.50,  "UPSTREAM\nCONVEYOR",   "Belt 600mm · 24VDC",      "States 1-2",        C_HW),
    (4.70,  "PCB STOPPERS",         "Entry + Exit (Ø10mm cyl.)","State 3",           "#34495E"),
    (7.90,  "BARCODE SCANNER",      "2D DataMatrix · USB HID",  "State 4",           C_SPECIAL),
    (11.40, "PRESS STATION",        "Ø80mm cyl. + pogo carrier","States 5-6-7-8",    "#1A5276"),
    (14.80, "EXIT / REJECT GATE",   "PASS→main  FAIL→tray",    "States 9-10",       C_ACTION),
]

for xc, title, sub, sref, col in flow_items:
    box = FancyBboxPatch((xc - FBW/2, FY - FBH/2), FBW, FBH,
                         boxstyle="round,pad=0.04",
                         facecolor=col, edgecolor="white", linewidth=1.5, zorder=3)
    ax_b.add_patch(box)
    ax_b.text(xc, FY + 0.09, title, ha="center", va="center",
              fontsize=8, fontweight="bold", color="white", zorder=4, fontfamily=FONT)
    ax_b.text(xc, FY - 0.12, sub, ha="center", va="center",
              fontsize=6.5, color="white", alpha=0.87, zorder=4, fontfamily=FONT)
    state_ref(ax_b, xc, FY - FBH/2 - 0.18, sref, col)

# Horizontal arrows between flow boxes
flow_xs = [xc for xc, *_ in flow_items]
for x1, x2 in zip(flow_xs, flow_xs[1:]):
    ax_b.annotate("", xy=(x2 - FBW/2, FY), xytext=(x1 + FBW/2, FY),
                  arrowprops=dict(arrowstyle="-|>", color=C_ARROW, lw=2.0), zorder=2)

# Vertical drop connector from PRESS STATION down to hierarchy
VS_X = 11.40
ax_b.plot([VS_X, VS_X], [FY - FBH/2, 4.62],
          "-", color=C_ARROW, lw=2.0, zorder=2)

# ══ VERTICAL HIERARCHY below Press Station ═══════════════════════
VS_W = 5.0   # width of vertical stack boxes

# ── Layer 1: Pneumatic Press ──────────────────────────────────────
PP_YC, PP_H = 4.15, 0.82
vbox(ax_b, VS_X, PP_YC, VS_W, PP_H,
     "PNEUMATIC PRESS  (BOM §2, §3, §4, §5)",
     ["Cylinder Ø80mm, ~500N @ 5 bar  (BOM item 6) — driven by 5/2 solenoid valve",
      "Top press plate + pogo-pin carrier (29 pins)  (BOM items 8, 23-24)",
      "3× Connector plug-in cylinders Ø16mm  (BOM item 26) — mate after press",
      "FRL unit + pressure sensor + flow control  (BOM items 15-17)"],
     "#1A5276")
ax_b.annotate("", xy=(VS_X, PP_YC - PP_H/2), xytext=(VS_X, PP_YC + PP_H/2 + 0.01),
              arrowprops=dict(arrowstyle="-|>", color=C_ARROW, lw=2.0), zorder=2)

# ── Layer 2: Test Instruments ─────────────────────────────────────
TI_YC, TI_H = 2.88, 1.0
vbox(ax_b, VS_X, TI_YC, VS_W, TI_H,
     "TEST INSTRUMENTS  (BOM §8)",
     ["KIKUSUI PWR401L — 12V / 3.8V DC supply to DUT via Fixture PCB",
      "Lauterbach Trace32 — SWD/JTAG firmware flash + debug (USB, PBI=USB)",
      "PEAK PCAN-USB — CAN-H / CAN-L bus communication with DUT",
      "PLIN-USB — LIN bus communication with DUT  (3-pin terminal)"],
     C_INST)
ax_b.annotate("", xy=(VS_X, TI_YC - TI_H/2), xytext=(VS_X, TI_YC + TI_H/2 + 0.01),
              arrowprops=dict(arrowstyle="-|>", color=C_ARROW, lw=2.0), zorder=2)

# ── Layer 3: Test PC / Software ───────────────────────────────────
PC_YC, PC_H = 1.52, 0.92
vbox(ax_b, VS_X, PC_YC, VS_W, PC_H,
     "TEST PC  (BOM §10)  —  orchestrator.py controls full test sequence",
     ["orchestrator.py — sequences PSU→Flash→CAN→LIN→Motor→EOS→NFC",
      "gui_main.py — Tkinter operator HMI  |  barcode_utils.py — scanner",
      "trace32_adapter · can_service · lin_service · motor_service · nfc_service",
      "MySQL client — logs result, barcode, variant, time  |  HTML report"],
     C_PC)

# Vertical line down to PASS/FAIL split
SPLIT_Y = 0.85
ax_b.plot([VS_X, VS_X], [PC_YC - PC_H/2, SPLIT_Y],
          "-", color=C_ARROW, lw=2.0, zorder=2)

# Horizontal split bar
PASS_X, FAIL_X = 7.50, 15.30
ax_b.plot([PASS_X, FAIL_X], [SPLIT_Y, SPLIT_Y],
          "-", color=C_ARROW, lw=2.0, zorder=2)

# PASS branch
ax_b.annotate("", xy=(PASS_X, 0.28), xytext=(PASS_X, SPLIT_Y),
              arrowprops=dict(arrowstyle="-|>", color="#27AE60", lw=2.5), zorder=2)
pass_bg = FancyBboxPatch((5.8, -0.12), 3.4, 0.40,
                         boxstyle="round,pad=0.04",
                         facecolor="#27AE60", edgecolor="white", linewidth=1.5, zorder=3)
ax_b.add_patch(pass_bg)
ax_b.text(PASS_X, 0.08, "PASS  →  Exit Conveyor", ha="center", va="center",
          fontsize=9, fontweight="bold", color="white", zorder=4, fontfamily=FONT)
ax_b.text(PASS_X, -0.20, "Light GREEN  ·  DO1.0 ON", ha="center", va="top",
          fontsize=6.5, color="#27AE60", fontfamily=FONT)
state_ref(ax_b, PASS_X - 1.1, SPLIT_Y + 0.12, "State 9", "#27AE60")

# FAIL branch
ax_b.annotate("", xy=(FAIL_X, 0.28), xytext=(FAIL_X, SPLIT_Y),
              arrowprops=dict(arrowstyle="-|>", color=C_SAFETY, lw=2.5), zorder=2)
fail_bg = FancyBboxPatch((13.6, -0.12), 3.4, 0.40,
                         boxstyle="round,pad=0.04",
                         facecolor=C_SAFETY, edgecolor="white", linewidth=1.5, zorder=3)
ax_b.add_patch(fail_bg)
ax_b.text(FAIL_X, 0.08, "FAIL  →  Reject Tray", ha="center", va="center",
          fontsize=9, fontweight="bold", color="white", zorder=4, fontfamily=FONT)
ax_b.text(FAIL_X, -0.20, "Light RED  ·  DO0.6 GATE", ha="center", va="top",
          fontsize=6.5, color=C_SAFETY, fontfamily=FONT)
state_ref(ax_b, FAIL_X + 1.1, SPLIT_Y + 0.12, "State 9", C_SAFETY)

# "LOGGING → IDLE" label on the right of PC box
ax_b.text(VS_X + VS_W/2 + 0.12, PC_YC,
          "State 10: MySQL write\n→ returns to IDLE",
          ha="left", va="center", fontsize=6.5, color=C_PC, fontfamily=FONT,
          bbox=dict(boxstyle="round,pad=0.2", facecolor="#D0F0EB",
                    edgecolor=C_PC, linewidth=0.8, alpha=0.85))

# ══ SAFETY LAYER sidebar (right) ═════════════════════════════════
SX, SY_BOT, SW2, SH2 = 17.2, 1.5, 4.5, 3.8
safety_box = FancyBboxPatch((SX, SY_BOT), SW2, SH2,
                            boxstyle="round,pad=0.04",
                            facecolor=C_SAFETY, edgecolor="white",
                            linewidth=1.5, zorder=3, alpha=0.93)
ax_b.add_patch(safety_box)
ax_b.text(SX + SW2/2, SY_BOT + SH2 - 0.10, "SAFETY LAYER  (BOM §11)",
          ha="center", va="top", fontsize=8.5, fontweight="bold",
          color="white", zorder=4, fontfamily=FONT)
safety_lines = [
    "Type-4 Light Curtain 300mm  (BOM 51)",
    "OSSD dual output → Safety relay",
    "Safety relay PLd Cat.3  (BOM 52)",
    "E-stop ×2 NC chain  (BOM 53)",
    "Tower light 3-col + buzzer  (BOM 54)",
    "Polycarbonate side guard  (BOM 55)",
    "",
    "Press CLOSES only when ALL true:",
    "  ✓ OSSD = ON  (curtain clear)",
    "  ✓ E-stop OK  (NC chain intact)",
    "  ✓ Air pressure >= 4 bar",
]
for i, ln in enumerate(safety_lines):
    ax_b.text(SX + 0.12, SY_BOT + SH2 - 0.28 - i * 0.30,
              ln, ha="left", va="top", fontsize=7.0,
              color="white", zorder=4, fontfamily=FONT,
              fontweight="bold" if ln.startswith("Press") else "normal")

# Dashed connection from Safety sidebar to Press layer
ax_b.annotate("", xy=(VS_X + VS_W/2, PP_YC),
              xytext=(SX, PP_YC),
              arrowprops=dict(arrowstyle="-|>", color="#FFAAAA", lw=1.2,
                              linestyle="dashed", connectionstyle="arc3,rad=0.0"),
              zorder=2)
ax_b.text((SX + VS_X + VS_W/2) / 2, PP_YC + 0.08,
          "press enable\ncondition",
          ha="center", va="bottom", fontsize=6.0,
          color="#FFAAAA", fontfamily=FONT)

# ══ PLC CONTROL UNIT sidebar (left) ══════════════════════════════
PX, PY_BOT, PW2, PH2 = 0.1, 1.2, 4.0, 4.1
plc_box = FancyBboxPatch((PX, PY_BOT), PW2, PH2,
                         boxstyle="round,pad=0.04",
                         facecolor="#117A65", edgecolor="white",
                         linewidth=1.5, zorder=3, alpha=0.93)
ax_b.add_patch(plc_box)
ax_b.text(PX + PW2/2, PY_BOT + PH2 - 0.10, "PLC CONTROL UNIT  (BOM §6)",
          ha="center", va="top", fontsize=8.5, fontweight="bold",
          color="white", zorder=4, fontfamily=FONT)
plc_lines = [
    "Siemens S7-1200  1214C DC/DC/DC",
    "14 DI  /  10 DO  /  2 AI  (24VDC)",
    "",
    "DO → Solenoid valves (press + stoppers",
    "       + connector actuators)",
    "DO → Reject gate  ·  Conveyor run",
    "DO → Tower light (R/Y/G) + Buzzer",
    "DI ← Photoelectric sensors (×2)",
    "DI ← Cylinder reed sensors (×2)",
    "DI ← Light curtain OSSD",
    "DI ← E-stop NC  ·  Air pressure OK",
    "",
    "Ethernet → HMI (Modbus TCP)",
    "Ethernet → Test PC (result sync)",
]
for i, ln in enumerate(plc_lines):
    ax_b.text(PX + 0.12, PY_BOT + PH2 - 0.28 - i * 0.27,
              ln, ha="left", va="top", fontsize=6.8,
              color="white", zorder=4, fontfamily=FONT)

# Dashed lines from PLC to each vertical layer
for ty in [PP_YC, TI_YC, PC_YC]:
    ax_b.plot([PX + PW2, VS_X - VS_W/2], [ty, ty],
              "--", color="#A9DFBF", lw=0.9, alpha=0.65, zorder=1)

# NFC subsystem note (below PLC box)
nfc_bg = FancyBboxPatch((PX, 0.58), PW2, 0.52,
                        boxstyle="round,pad=0.04",
                        facecolor=C_NFC, edgecolor="white",
                        linewidth=1.2, zorder=3, alpha=0.92)
ax_b.add_patch(nfc_bg)
ax_b.text(PX + PW2/2, 0.84, "NFC SUBSYSTEM  (BOM §14)",
          ha="center", va="center", fontsize=8, fontweight="bold",
          color="white", zorder=4, fontfamily=FONT)
ax_b.text(PX + PW2/2, 0.66, "Servo ×2 + card holder  |  nfc_service.py  |  NFC LH/RH variants only",
          ha="center", va="center", fontsize=6.5,
          color="white", zorder=4, fontfamily=FONT)

# Fixture PCB note (between PLC and Press)
ax_b.text(PX + PW2/2, PY_BOT - 0.05,
          "Fixture PCB (TIB)  BOM §9\n"
          "IDC34 + DB9 + LIN terminal + 10-pin JTAG + 12× relays",
          ha="center", va="top", fontsize=6.5, color="#117A65",
          fontfamily=FONT,
          bbox=dict(boxstyle="round,pad=0.2", facecolor="#D5F5E3",
                    edgecolor="#117A65", linewidth=0.8, alpha=0.85))

# ══ LINE LEGEND (Panel B) ════════════════════════════════════════
leg_x, leg_y = 8.5, -0.10
leg_bg = FancyBboxPatch((leg_x, leg_y), 8.2, 0.90,
                        boxstyle="round,pad=0.04",
                        facecolor="white", edgecolor="#AAAAAA",
                        linewidth=1.0, zorder=5, alpha=0.95)
ax_b.add_patch(leg_bg)
ax_b.text(leg_x + 4.1, leg_y + 0.82, "Line / Arrow Legend",
          ha="center", va="top", fontsize=8, fontweight="bold",
          color=C_HW, zorder=6, fontfamily=FONT)
# Solid arrow — PCB / signal flow
ax_b.annotate("", xy=(leg_x + 1.2, leg_y + 0.57),
              xytext=(leg_x + 0.20, leg_y + 0.57),
              arrowprops=dict(arrowstyle="-|>", color=C_ARROW, lw=2.0), zorder=6)
ax_b.text(leg_x + 1.35, leg_y + 0.57,
          "Solid arrow  =  Physical PCB / signal flow direction (main process path)",
          ha="left", va="center", fontsize=7.2, color="#222222",
          zorder=6, fontfamily=FONT)
# Dashed arrow — PLC control signal
ax_b.plot([leg_x + 0.20, leg_x + 1.15], [leg_y + 0.35, leg_y + 0.35],
          "--", color="#A9DFBF", lw=1.5, zorder=6)
ax_b.annotate("", xy=(leg_x + 1.20, leg_y + 0.35),
              xytext=(leg_x + 1.14, leg_y + 0.35),
              arrowprops=dict(arrowstyle="-|>", color="#117A65", lw=1.2), zorder=6)
ax_b.text(leg_x + 1.35, leg_y + 0.35,
          "Green dashed  =  PLC control signal  (PLC sends DO commands to each layer)",
          ha="left", va="center", fontsize=7.2, color="#117A65",
          zorder=6, fontfamily=FONT)
# Dashed arrow — Safety enable condition
ax_b.plot([leg_x + 0.20, leg_x + 1.15], [leg_y + 0.14, leg_y + 0.14],
          "--", color="#FFAAAA", lw=1.5, zorder=6)
ax_b.annotate("", xy=(leg_x + 1.20, leg_y + 0.14),
              xytext=(leg_x + 1.14, leg_y + 0.14),
              arrowprops=dict(arrowstyle="-|>", color="#FFAAAA", lw=1.2), zorder=6)
ax_b.text(leg_x + 1.35, leg_y + 0.14,
          "Red dashed  =  Safety enable condition  (press is BLOCKED until all safety conditions are met)",
          ha="left", va="center", fontsize=7.2, color=C_SAFETY,
          zorder=6, fontfamily=FONT)


# ══════════════════════════════════════════════════════════════════
#  PANEL C  —  Test Sequence Detail
# ══════════════════════════════════════════════════════════════════
ax_c = fig.add_axes([0.03, 0.04, 0.94, 0.310])
ax_c.set_xlim(0, 22)
ax_c.set_ylim(-0.6, 7.5)
ax_c.axis("off")
ax_c.set_facecolor(C_BG)

# ── Left side: State 6 detail + test step swimlane ──────────────
ax_c.text(3.7, 6.75, "State 6 + TESTING State — Pre-Test Connector Mating & Full Test Sequence",
          ha="center", va="top", fontsize=10.5, fontweight="bold",
          color=C_HW, fontfamily=FONT)

# State 6 block (before T1 — happens while pogo pins are already contacting)
S6_Y = 6.88
s6_box = FancyBboxPatch((0.15, S6_Y - 0.52), 6.95, 0.52,
                        boxstyle="round,pad=0.04",
                        facecolor="#21618C", edgecolor="white",
                        linewidth=1.5, zorder=3)
ax_c.add_patch(s6_box)
circ6 = plt.Circle((0.50, S6_Y - 0.26), 0.22, color="#154360", zorder=4)
ax_c.add_patch(circ6)
ax_c.text(0.50, S6_Y - 0.26, "S6", ha="center", va="center",
          fontsize=8, fontweight="bold", color="white", zorder=5)
ax_c.text(0.85, S6_Y - 0.13,
          "STATE 6: CONNECTOR MATING  (before testing starts)",
          ha="left", va="center", fontsize=8.5, fontweight="bold",
          color="white", zorder=4, fontfamily=FONT)
ax_c.text(0.85, S6_Y - 0.38,
          "PLC energises DO0.3 → DO0.4 → DO0.5 sequentially  |  3× Ø16mm cylinders extend  |  "
          "Each cylinder mates one DUT edge connector (motor DB9, LIN terminal, supply header)  |  "
          "Settle time: 0.5s  |  Connector CLOSED sensors confirm all 3 mated  |  THEN testing begins",
          ha="left", va="center", fontsize=6.5, color="white",
          alpha=0.92, zorder=4, fontfamily=FONT)
# Arrow from S6 block down to T1
ax_c.annotate("", xy=(0.50, 6.22), xytext=(0.50, S6_Y - 0.52),
              arrowprops=dict(arrowstyle="-|>", color="#21618C", lw=1.8), zorder=2)

steps = [
    # (y,  step_no, label,                          instrument,        duration, color)
    (6.0,  "T1",  "PSU ON — Apply 12V / 3.8V to DUT",  "KIKUSUI PWR401L",   "~2s",  "#1A5276"),
    (5.1,  "T2",  "Trace32 connect — SWD link check",   "Lauterbach Trace32","~3s",  "#154360"),
    (4.2,  "T3",  "Flash firmware via SWD",              "Lauterbach Trace32","~30s", "#154360"),
    (3.3,  "T4",  "CAN communication test",              "PCAN-USB",          "~10s", "#4A235A"),
    (2.4,  "T5",  "LIN bus communication test",          "PLIN-USB",          "~10s", "#4A235A"),
    (1.5,  "T6",  "Motor drive test (SG1/SG2/Cap relay)","Relay board + PSU", "~15s", "#7D6608"),
    (0.6,  "T7",  "EOS / LED / NFC antenna test",        "EOS board / Servo", "~10s", "#784212"),
]

for y_pos, step_no, lbl, instrument, dur, col in steps:
    # step bubble
    circ = plt.Circle((0.5, y_pos), 0.22, color=col, zorder=4)
    ax_c.add_patch(circ)
    ax_c.text(0.5, y_pos, step_no, ha="center", va="center",
              fontsize=8, fontweight="bold", color="white", zorder=5)
    # box
    box = FancyBboxPatch((0.85, y_pos - 0.22), 5.4, 0.44,
                         boxstyle="round,pad=0.03",
                         facecolor=col, edgecolor="white",
                         linewidth=1, zorder=3, alpha=0.88)
    ax_c.add_patch(box)
    ax_c.text(1.0, y_pos + 0.08, lbl, ha="left", va="center",
              fontsize=8.5, fontweight="bold", color="white", zorder=4, fontfamily=FONT)
    ax_c.text(1.0, y_pos - 0.08, f"{instrument}  |  {dur}",
              ha="left", va="center", fontsize=7, color="white",
              alpha=0.85, zorder=4, fontfamily=FONT)
    # connector line
    if y_pos > 0.6:
        ax_c.plot([0.5, 0.5], [y_pos - 0.22, y_pos - 0.56],
                  "-", color="#CCCCCC", lw=1.5, zorder=2)

# ── Right side: PLC I/O summary table ─────────────────────────
ax_c.text(13.5, 6.75, "PLC I/O Map Summary  (Siemens S7-1200 1214C)",
          ha="center", va="top", fontsize=11, fontweight="bold",
          color=C_HW, fontfamily=FONT)

# Table header
for txt, xp in [("I/O", 8.0), ("Channel", 9.0), ("Signal Name", 11.0),
                ("Connected Device", 14.8), ("0=", 17.8), ("1=", 19.5)]:
    ax_c.text(xp, 6.4, txt, ha="left", va="top", fontsize=8,
              fontweight="bold", color="white", zorder=4, fontfamily=FONT,
              bbox=dict(boxstyle="round", facecolor=C_HW, edgecolor="none", pad=0.2))

io_rows = [
    ("DI", "DI0.0", "PCB_ENTRY_DETECT",   "Entry sensor (item 4)",     "No PCB",   "PCB detected"),
    ("DI", "DI0.1", "PCB_POSITION_DETECT","Centre sensor (item 4)",    "No PCB",   "PCB at station"),
    ("DI", "DI0.2", "PRESS_OPEN_SENSE",   "Cylinder OPEN reed (12)",   "Not open", "Press open"),
    ("DI", "DI0.3", "PRESS_CLOSED_SENSE", "Cylinder CLOSED reed (12)", "Not clsd", "Press closed"),
    ("DI", "DI0.4", "LIGHT_CURTAIN_OSSD", "Safety light curtain (51)", "Breach",   "Clear"),
    ("DI", "DI0.5", "ESTOP_OK",           "E-stop NC chain (53)",      "Pressed",  "OK"),
    ("DI", "DI0.6", "AIR_PRESSURE_OK",    "Pressure switch (17)",      "Low",      "OK"),
    ("DI", "DI0.7", "PCB_EXIT_DETECT",    "Exit sensor",               "No PCB",   "PCB present"),
    ("DO", "DO0.0", "PRESS_SOL_VALVE",    "Press cylinder valve (13)", "Retract",  "Extend"),
    ("DO", "DO0.1", "STOPPER_ENTRY_SOL",  "Entry stopper valve (13)",  "Down",     "Up"),
    ("DO", "DO0.2", "STOPPER_EXIT_SOL",   "Exit stopper valve (13)",   "Down",     "Up"),
    ("DO", "DO0.3", "CONN_SOL_1",         "Connector 1 valve (28)",    "Retract",  "Extend"),
    ("DO", "DO0.4", "CONN_SOL_2",         "Connector 2 valve (28)",    "Retract",  "Extend"),
    ("DO", "DO0.5", "CONN_SOL_3",         "Connector 3 valve (28)",    "Retract",  "Extend"),
    ("DO", "DO0.6", "REJECT_GATE_SOL",    "Reject gate (item 56)",     "Closed",   "Open(FAIL)"),
    ("DO", "DO0.7", "CONVEYOR_RUN",       "Conveyor drive (item 2)",   "Stop",     "Run"),
    ("DO", "DO1.0", "LIGHT_GREEN",        "Tower light (54)",          "Off",      "PASS"),
    ("DO", "DO1.1", "LIGHT_YELLOW",       "Tower light (54)",          "Off",      "BUSY"),
    ("DO", "DO1.2", "LIGHT_RED",          "Tower light (54)",          "Off",      "FAIL/FAULT"),
    ("DO", "DO1.3", "BUZZER",             "Tower light (54)",          "Silent",   "Alert"),
]

for i, (io, ch, sig, dev, s0, s1) in enumerate(io_rows):
    y_row = 6.05 - i * 0.30
    row_color = "#D6EAF8" if io == "DI" else "#D5F5E3"
    text_color = "#1A5276" if io == "DI" else "#196F3D"
    bg = FancyBboxPatch((7.8, y_row - 0.12), 13.8, 0.26,
                        boxstyle="square,pad=0.0",
                        facecolor=row_color, edgecolor="#BDC3C7",
                        linewidth=0.5, zorder=2, alpha=0.7)
    ax_c.add_patch(bg)
    for txt, xp in [(io, 8.0), (ch, 9.0), (sig, 11.0),
                    (dev, 14.8), (s0, 17.8), (s1, 19.5)]:
        ax_c.text(xp, y_row + 0.01, txt, ha="left", va="center",
                  fontsize=6.8, color=text_color, fontfamily=FONT)

# ── Software stack note (bottom of panel C) ───────────────────
sw_note = (
    "SOFTWARE STACK (already developed):  "
    "barcode_utils.py  ·  orchestrator.py  ·  "
    "trace32_adapter.py  ·  can_service.py  ·  lin_service.py  ·  "
    "motor_service.py  ·  nfc_service.py  ·  "
    "sg_service.py  ·  eos_service.py  ·  "
    "report_generator.py  ·  MySQL integration"
)
ax_c.text(11.0, -0.45, sw_note, ha="center", va="center",
          fontsize=8, color="#555555", fontfamily=FONT,
          bbox=dict(boxstyle="round", facecolor="#EBF5FB",
                    edgecolor=C_PC, pad=0.4))

# ══════════════════════════════════════════════════════════════════
#  SAVE
# ══════════════════════════════════════════════════════════════════
out_dir  = os.path.dirname(os.path.abspath(__file__))

# ── PNG (raster, for quick viewing / insertion into documents) ────
out_png = os.path.join(out_dir, "Conveyor_AutoLoader_Flow_Diagram_Rev1.0.png")
fig.savefig(out_png, dpi=180, bbox_inches="tight",
            facecolor=C_BG, edgecolor="none")
print(f"Saved PNG : {out_png}")

# ── SVG (fully editable vector — open in Inkscape or import into ──
#         PowerPoint 2016+ via Insert > Pictures > SVG, then        ──
#         right-click > "Convert to Shape" to edit individual items) ─
out_svg = os.path.join(out_dir, "Conveyor_AutoLoader_Flow_Diagram_Rev1.0.svg")
fig.savefig(out_svg, format="svg", bbox_inches="tight",
            facecolor=C_BG, edgecolor="none")
print(f"Saved SVG : {out_svg}")

plt.close(fig)

# ── PPTX (PowerPoint slide containing the SVG as an editable ──────
#          vector object; requires python-pptx)                      ─
try:
    from pptx import Presentation
    from pptx.util import Inches, Pt, Emu
    from pptx.dml.color import RGBColor
    from pptx.enum.text import PP_ALIGN
    import math

    SLIDE_W = Inches(22)   # match figure width (22 inches)
    SLIDE_H = Inches(30)   # match figure height (30 inches)

    prs = Presentation()
    prs.slide_width  = SLIDE_W
    prs.slide_height = SLIDE_H

    slide_layout = prs.slide_layouts[6]  # blank layout
    slide = prs.slides.add_slide(slide_layout)

    # Insert the high-res PNG onto the slide.
    # For full vector editing, also import the SVG separately in PowerPoint:
    #   Insert > Pictures > This Device > select the .svg file, then
    #   right-click > Convert to Shape (or Ungroup twice) to edit elements.
    pic = slide.shapes.add_picture(out_png, 0, 0, SLIDE_W, SLIDE_H)

    # Add a small footer text box with revision info
    txBox = slide.shapes.add_textbox(Inches(0.2), SLIDE_H - Inches(0.35),
                                     SLIDE_W - Inches(0.4), Inches(0.30))
    tf = txBox.text_frame
    tf.word_wrap = False
    p = tf.paragraphs[0]
    p.alignment = PP_ALIGN.CENTER
    run = p.add_run()
    run.text = ("Conveyor_AutoLoader_Flow_Diagram_Rev1.0  |  "
                "SmartBU / XNF I460  |  BMW MAE 032080790003  |  "
                "Charan Singh  |  11.05.2026  |  "
                "SVG embedded — use Insert > Pictures > SVG or Convert to Shape for editing")
    run.font.size = Pt(6)
    run.font.color.rgb = RGBColor(0x55, 0x55, 0x55)

    out_pptx = os.path.join(out_dir, "Conveyor_AutoLoader_Flow_Diagram_Rev1.0.pptx")
    prs.save(out_pptx)
    print(f"Saved PPTX: {out_pptx}")
    print("  → In PowerPoint: select the diagram image, right-click,")
    print("    choose 'Convert to Shape' (or Ungroup) to edit individual elements.")

except ImportError:
    print("python-pptx not installed — PPTX not generated.")
    print("  Install with:  pip install python-pptx")
