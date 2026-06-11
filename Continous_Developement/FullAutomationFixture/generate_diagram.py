"""Generate Full Automation Fixture - High-Level Component Diagram as SVG."""

W, H = 1700, 1160

def esc(s):
    return s.replace('&','&amp;').replace('<','&lt;').replace('>','&gt;')

lines = []
def e(s): lines.append(s)

# ── palette ──────────────────────────────────────────────────────────────────
C = dict(
    bg       = '#F4F6FA',
    title_bg = '#1F3864',
    title_fg = '#FFFFFF',
    # swim-lane backgrounds
    mech_bg  = '#E8F5E9',  mech_border = '#2E7D32',  mech_title = '#2E7D32',
    plc_bg   = '#FFF3E0',  plc_border  = '#E65100',  plc_title  = '#E65100',
    sig_bg   = '#FCE4EC',  sig_border  = '#C62828',  sig_title  = '#C62828',
    fct_bg   = '#E3F2FD',  fct_border  = '#1565C0',  fct_title  = '#1565C0',
    inst_bg  = '#EDE7F6',  inst_border = '#4527A0',  inst_title = '#4527A0',
    data_bg  = '#FFFDE7',  data_border = '#F57F17',  data_title = '#F57F17',
    # component box
    box_bg   = '#FFFFFF',
    new_bg   = '#E8F5E9',   # NEW module highlight
    upd_bg   = '#FFF9C4',   # UPDATED module highlight
    # arrows
    arr_plc2fct = '#C62828',
    arr_fct2plc = '#1565C0',
    arr_data    = '#F57F17',
    arr_inst    = '#4527A0',
    arr_mech    = '#2E7D32',
    # text
    label    = '#212121',
    sublabel = '#555555',
    note     = '#888888',
)

def rect(x,y,w,h,fill,stroke,rx=8,stroke_w=2,opacity=1):
    e(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" '
      f'fill="{fill}" stroke="{stroke}" stroke-width="{stroke_w}" opacity="{opacity}"/>')

def text(x,y,s,size=12,fill='#212121',bold=False,anchor='middle',italic=False):
    fw = 'bold' if bold else 'normal'
    fs = 'italic' if italic else 'normal'
    e(f'<text x="{x}" y="{y}" font-size="{size}" font-weight="{fw}" font-style="{fs}" '
      f'fill="{fill}" text-anchor="{anchor}" font-family="Segoe UI,Arial,sans-serif">'
      f'{esc(s)}</text>')

def line(x1,y1,x2,y2,color,w=2,dash=''):
    da = f'stroke-dasharray="{dash}"' if dash else ''
    e(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" '
      f'stroke="{color}" stroke-width="{w}" {da} marker-end="url(#arr_{color.replace("#","")})"/>')

def arrow_def(color):
    cid = color.replace('#','')
    e(f'<marker id="arr_{cid}" markerWidth="10" markerHeight="7" refX="9" refY="3.5" orient="auto">')
    e(f'<polygon points="0 0, 10 3.5, 0 7" fill="{color}"/>')
    e('</marker>')

def bidir_line(x1,y1,x2,y2,color,w=2,label_txt='',lx=0,ly=0):
    cid = color.replace('#','')
    e(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" '
      f'stroke="{color}" stroke-width="{w}" '
      f'marker-start="url(#arr_start_{cid})" marker-end="url(#arr_{cid})"/>')
    if label_txt:
        text(lx,ly, label_txt, 10, color, italic=True)

def bidir_def(color):
    cid = color.replace('#','')
    e(f'<marker id="arr_start_{cid}" markerWidth="10" markerHeight="7" refX="1" refY="3.5" orient="auto-start-reverse">')
    e(f'<polygon points="0 0, 10 3.5, 0 7" fill="{color}"/>')
    e('</marker>')

def component_box(x,y,w,h,title,lines_txt,fill,border,title_size=12,badge=None):
    rect(x,y,w,h, fill, border, rx=6, stroke_w=1.5)
    rect(x,y,w,22, border, border, rx=6)
    rect(x,y+16,w,8, border, border, rx=0)  # bottom cap for title bar
    text(x+w//2, y+15, title, title_size, '#FFFFFF', bold=True)
    if badge:
        bw=38; bh=15
        rect(x+w-bw-4, y+26, bw, bh, badge[1], badge[1], rx=4)
        text(x+w-4-bw//2, y+37, badge[0], 9, '#FFFFFF', bold=True)
    yy = y+40
    for ln in lines_txt:
        text(x+8, yy, ln, 10, C['label'], anchor='start')
        yy += 14

# ─────────────────────────── SVG HEADER ─────────────────────────────────────
e(f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">')
e('<defs>')

# arrow markers
for col in [C['arr_plc2fct'], C['arr_fct2plc'], C['arr_data'], C['arr_inst'],
            C['arr_mech'], '#555555', '#2E7D32', '#1565C0', '#E65100', '#4527A0',
            '#F57F17', '#C62828', '#888888']:
    arrow_def(col)
    bidir_def(col)

# drop shadow filter
e('''<filter id="shadow" x="-5%" y="-5%" width="110%" height="110%">
  <feDropShadow dx="2" dy="2" stdDeviation="3" flood-color="#00000030"/>
</filter>''')
e('</defs>')

# ── background ────────────────────────────────────────────────────────────────
rect(0,0,W,H, C['bg'], C['bg'], rx=0)

# ── TITLE BAR ─────────────────────────────────────────────────────────────────
rect(0,0,W,52, C['title_bg'], C['title_bg'], rx=0)
text(W//2, 22, 'FULL AUTOMATION FIXTURE — HIGH-LEVEL COMPONENT DIAGRAM', 18,
     C['title_fg'], bold=True)
text(W//2, 42, 'RH_i460 FCT | 4-Slot Parallel | India (FCT SW) + BANWA (PLC / Robot)', 12,
     '#B0C4DE', italic=True)

# ═══════════════════════════════════════════════════════════════════════════════
#  LAYOUT CONSTANTS
# ═══════════════════════════════════════════════════════════════════════════════
TOP       = 65    # y start after title
PAD       = 10

# Column / row positions
# [ MECH ROW : full width at top ]
# [ PLC | SIG | FCT-SW | INSTRUMENTS ]
# [ DATA ROW : full width at bottom ]

MECH_Y    = TOP
MECH_H    = 130

MID_Y     = MECH_Y + MECH_H + PAD
MID_H     = 600

DATA_Y    = MID_Y + MID_H + PAD
DATA_H    = 125

PLC_X     = PAD;         PLC_W  = 260
SIG_X     = PLC_X+PLC_W+PAD;  SIG_W  = 180
FCT_X     = SIG_X+SIG_W+PAD;  FCT_W  = 660
INST_X    = FCT_X+FCT_W+PAD;  INST_W = W - INST_X - PAD

# ═══════════════════════════════════════════════════════════════════════════════
#  SECTION 1 — MECHANICAL FLOW  (full width)
# ═══════════════════════════════════════════════════════════════════════════════
rect(PAD, MECH_Y, W-2*PAD, MECH_H, C['mech_bg'], C['mech_border'], rx=10)
rect(PAD, MECH_Y, W-2*PAD, 24, C['mech_border'], C['mech_border'], rx=10)
rect(PAD, MECH_Y+18, W-2*PAD, 8, C['mech_border'], C['mech_border'], rx=0)
text(W//2, MECH_Y+17, 'MECHANICAL / PHYSICAL FLOW  (BANWA — Robot + Fixture)',
     13, '#FFFFFF', bold=True)

# boxes inside MECH row
mx_start = 40; my = MECH_Y+35; mh=75; mw=150; mgap=18

mboxes = [
    ('PCB Tray Stack\n(Input)', '#E8F5E9', C['mech_border']),
    ('Robot Arm\n(Pick & Place)', '#FFF3E0', C['plc_border']),
    ('Alignment JIG\n(2D Scan here)', '#FFF3E0', C['plc_border']),
    ('4-Slot Fixture\n(Pneumatic Press\n+ Pogo Pins)', '#EDE7F6', C['inst_border']),
    ('Conveyor / Sort\n(Pass → Exit\nFail → Reject)', '#FCE4EC', C['sig_border']),
    ('Production\nFloor', '#E3F2FD', C['fct_border']),
]

bx = mx_start
box_centers = []
for (title, fill, stroke) in mboxes:
    rect(bx, my, mw, mh, fill, stroke, rx=6, stroke_w=1.5)
    lines_t = title.split('\n')
    ty = my + 16
    for i,lt in enumerate(lines_t):
        fw = True if i==0 else False
        text(bx+mw//2, ty, lt, 11 if i==0 else 9, C['label'], bold=fw)
        ty += 14
    box_centers.append((bx+mw//2, my+mh//2))
    bx += mw+mgap

# arrows between mech boxes
arr_pairs = [(0,1),(1,2),(2,3),(3,4),(4,5)]
for (a,b) in arr_pairs:
    ax,ay = box_centers[a]; bx2,by2 = box_centers[b]
    line(ax+mw//2-5, ay, bx2-mw//2+5, by2, C['arr_mech'], w=2)

# label the fixture box connection to mid section
text(box_centers[3][0], my+mh+12, '↕ PLC signals + FCT SW', 9, C['note'], italic=True)

# ═══════════════════════════════════════════════════════════════════════════════
#  SECTION 2 — PLC / BANWA
# ═══════════════════════════════════════════════════════════════════════════════
rect(PLC_X, MID_Y, PLC_W, MID_H, C['plc_bg'], C['plc_border'], rx=10)
rect(PLC_X, MID_Y, PLC_W, 24, C['plc_border'], C['plc_border'], rx=10)
rect(PLC_X, MID_Y+18, PLC_W, 8, C['plc_border'], C['plc_border'], rx=0)
text(PLC_X+PLC_W//2, MID_Y+17, 'PLC / ROBOT  (BANWA)', 13, '#FFFFFF', bold=True)

plc_components = [
    ('PLC Controller',      ['• Siemens/Mitsubishi PLC', '• Robot sequence logic',
                              '• Fixture state machine', '• I/O module (24 V DC)']),
    ('Robot Arm Controller',['• 6-axis articulated arm', '• Pick & place trajectory',
                              '• Slot 1-4 positioning', '• Speed/torque control']),
    ('Fixture Controller',  ['• Pneumatic press (up/down)', '• Pogo pin contact verify',
                              '• Connector plug-in sequence', '• Fixture open/close']),
    ('Conveyor Controller', ['• Entry stopper logic', '• PASS lane routing',
                              '• FAIL/reject routing', '• Belt speed control']),
    ('2D Barcode Scanner',  ['• KEYENCE SR-X100/SR-700', '• Reads 4 PCBs at once',
                              '• Mounted at Alignment JIG', '• USB direct OR PLC register']),
]

py = MID_Y+35
for (title, lns) in plc_components:
    bh = 24 + len(lns)*14
    rect(PLC_X+8, py, PLC_W-16, bh, C['box_bg'], C['plc_border'], rx=5, stroke_w=1)
    rect(PLC_X+8, py, PLC_W-16, 18, C['plc_border'], C['plc_border'], rx=5)
    rect(PLC_X+8, py+12, PLC_W-16, 8, C['plc_border'], C['plc_border'], rx=0)
    text(PLC_X+8+(PLC_W-16)//2, py+13, title, 11, '#FFFFFF', bold=True)
    ly = py+28
    for ln in lns:
        text(PLC_X+14, ly, ln, 9, C['label'], anchor='start')
        ly += 14
    py += bh+8

# ═══════════════════════════════════════════════════════════════════════════════
#  SECTION 3 — I/O SIGNAL INTERFACE
# ═══════════════════════════════════════════════════════════════════════════════
rect(SIG_X, MID_Y, SIG_W, MID_H, C['sig_bg'], C['sig_border'], rx=10)
rect(SIG_X, MID_Y, SIG_W, 24, C['sig_border'], C['sig_border'], rx=10)
rect(SIG_X, MID_Y+18, SIG_W, 8, C['sig_border'], C['sig_border'], rx=0)
text(SIG_X+SIG_W//2, MID_Y+17, 'I/O SIGNAL INTERFACE', 12, '#FFFFFF', bold=True)

sig_items = [
    # (label, direction, from_plc)
    ('FCT_START',         '→  PLC → FCT PC',  True,  'Triggers test start per cycle'),
    ('FIXTURE_CLOSED',    '→  PLC → FCT PC',  True,  'Confirms pneumatic lock'),
    ('PCB_IN_SLOT[1-4]',  '→  PLC → FCT PC',  True,  'Seat confirmation per slot'),
    ('FCT_READY',         '←  FCT PC → PLC',  False, 'SW fully initialised'),
    ('FCT_ACK',           '←  FCT PC → PLC',  False, 'Handshake acknowledge'),
    ('SLOT_PASS[1-4]',    '←  FCT PC → PLC',  False, 'Pass result per slot'),
    ('SLOT_FAIL[1-4]',    '←  FCT PC → PLC',  False, 'Fail result per slot'),
    ('FCT_DONE',          '←  FCT PC → PLC',  False, 'All 4 slots complete'),
    ('FCT_ERROR',         '←  FCT PC → PLC',  False, 'Error — hold robot'),
]

sy = MID_Y + 34
for (sig, direction, from_plc, desc) in sig_items:
    col = C['plc_border'] if from_plc else C['fct_border']
    rect(SIG_X+6, sy, SIG_W-12, 38, '#FFFFFF', col, rx=4, stroke_w=1)
    text(SIG_X+SIG_W//2, sy+13, sig, 10, col, bold=True)
    text(SIG_X+SIG_W//2, sy+25, direction, 9, col, italic=True)
    text(SIG_X+SIG_W//2, sy+36, desc, 8, C['note'], italic=True)
    sy += 44

# physical interface note at bottom
sy += 6
rect(SIG_X+6, sy, SIG_W-12, 70, '#FFF3E0', '#E65100', rx=4, stroke_w=1)
text(SIG_X+SIG_W//2, sy+14, 'Physical Layer', 10, '#E65100', bold=True)
for i, ln in enumerate(['USB-Relay module', 'OR Modbus TCP', 'OR EtherNet/IP',
                         'Voltage: 24V DC / 5V DC']):
    text(SIG_X+SIG_W//2, sy+28+i*12, ln, 9, C['label'])

# ═══════════════════════════════════════════════════════════════════════════════
#  SECTION 4 — FCT SOFTWARE (INDIA)
# ═══════════════════════════════════════════════════════════════════════════════
rect(FCT_X, MID_Y, FCT_W, MID_H, C['fct_bg'], C['fct_border'], rx=10)
rect(FCT_X, MID_Y, FCT_W, 24, C['fct_border'], C['fct_border'], rx=10)
rect(FCT_X, MID_Y+18, FCT_W, 8, C['fct_border'], C['fct_border'], rx=0)
text(FCT_X+FCT_W//2, MID_Y+17, 'FCT TEST PC — SOFTWARE  (INDIA  |  Base: NFC_Rev3.01)', 13, '#FFFFFF', bold=True)

# 4-slot parallel schematic inside FCT area
# Show top-level modules stacked, then 4-slot horizontal strip

FCT_INNER_X = FCT_X + 10
FCT_INNER_W = FCT_W - 20

# ---- Module: GUI ----
gy = MID_Y + 34; gh = 52
rect(FCT_INNER_X, gy, FCT_INNER_W, gh, C['box_bg'], C['fct_border'], rx=5, stroke_w=1)
rect(FCT_INNER_X, gy, FCT_INNER_W, 18, C['fct_border'], C['fct_border'], rx=5)
rect(FCT_INNER_X, gy+12, FCT_INNER_W, 8, C['fct_border'], C['fct_border'], rx=0)
text(FCT_INNER_X+FCT_INNER_W//2, gy+13, '① gui_main.py  —  4-Slot GUI Dashboard', 11, '#FFFFFF', bold=True)
text(FCT_INNER_X+FCT_INNER_W//2, gy+32, '• 4 slot status panels (barcode, progress bar, PASS/FAIL indicator)', 10, C['label'])
text(FCT_INNER_X+FCT_INNER_W//2, gy+46, '• PLC-triggered start mode (replaces manual Play button)  |  Variant selector per slot (NFC / NON-NFC)', 10, C['label'])

# ---- Module: PC I/O Interface (NEW) ----
iy = gy+gh+6; ih=52
rect(FCT_INNER_X, iy, FCT_INNER_W, ih, C['new_bg'], C['fct_border'], rx=5, stroke_w=1)
rect(FCT_INNER_X, iy, FCT_INNER_W, 18, '#2E7D32', '#2E7D32', rx=5)
rect(FCT_INNER_X, iy+12, FCT_INNER_W, 8, '#2E7D32', '#2E7D32', rx=0)
text(FCT_INNER_X+FCT_INNER_W//2, iy+13, '② pc_io_interface.py  —  PLC I/O Driver  [NEW MODULE]', 11, '#FFFFFF', bold=True)
text(FCT_INNER_X+FCT_INNER_W//2, iy+32, '• wait_for_start(slot)  |  send_ready()  |  send_pass/fail(slot)  |  send_error(slot)', 10, C['label'])
text(FCT_INNER_X+FCT_INNER_W//2, iy+46, '• USB-Relay / Modbus TCP driver  |  Pulse timing + handshake FSM  |  Thread-safe per-slot locking', 10, C['label'])

# ---- Module: Barcode Scanner (NEW) ----
by2 = iy+ih+6; bh2=40
rect(FCT_INNER_X, by2, FCT_INNER_W, bh2, C['new_bg'], C['fct_border'], rx=5, stroke_w=1)
rect(FCT_INNER_X, by2, FCT_INNER_W, 18, '#2E7D32', '#2E7D32', rx=5)
rect(FCT_INNER_X, by2+12, FCT_INNER_W, 8, '#2E7D32', '#2E7D32', rx=0)
text(FCT_INNER_X+FCT_INNER_W//2, by2+13, '③ barcode_scanner.py  —  KEYENCE SR-X100/SR-700 USB-COM  [NEW MODULE]', 11, '#FFFFFF', bold=True)
text(FCT_INNER_X+FCT_INNER_W//2, by2+34, '• Reads 4× 2D barcodes  |  Maps scan_code[n] → slot n  |  Passes barcode IDs to orchestrator before test start', 10, C['label'])

# ---- Module: Orchestrator (UPDATED) ----
oy = by2+bh2+6; oh=52
rect(FCT_INNER_X, oy, FCT_INNER_W, oh, C['upd_bg'], C['fct_border'], rx=5, stroke_w=1)
rect(FCT_INNER_X, oy, FCT_INNER_W, 18, '#B8860B', '#B8860B', rx=5)
rect(FCT_INNER_X, oy+12, FCT_INNER_W, 8, '#B8860B', '#B8860B', rx=0)
text(FCT_INNER_X+FCT_INNER_W//2, oy+13, '④ integrated_automation.py  —  4-Slot Orchestrator  [UPDATED]', 11, '#FFFFFF', bold=True)
text(FCT_INNER_X+FCT_INNER_W//2, oy+32, '• Spawns 4 parallel threads/processes (one per slot)  |  Thread-safe resource allocation  |  Per-slot is_first_run flag', 10, C['label'])
text(FCT_INNER_X+FCT_INNER_W//2, oy+46, '• Supervisor monitors all 4 results  |  Reports batch status to PLC via pc_io_interface  |  PSU warm-start optimization', 10, C['label'])

# ---- 4-SLOT PARALLEL STRIP ----
slot_y = oy+oh+8; slot_h=120
slot_label_h = 20
sw = (FCT_INNER_W - 3*8) // 4
slot_colors = ['#1565C0','#1565C0','#1565C0','#1565C0']

for slot in range(4):
    sx = FCT_INNER_X + slot*(sw+8)
    # outer box
    rect(sx, slot_y, sw, slot_h, '#EBF5FF', C['fct_border'], rx=5, stroke_w=1.5)
    rect(sx, slot_y, sw, slot_label_h, C['fct_border'], C['fct_border'], rx=5)
    rect(sx, slot_y+14, sw, 8, C['fct_border'], C['fct_border'], rx=0)
    text(sx+sw//2, slot_y+14, f'SLOT {slot+1}', 11, '#FFFFFF', bold=True)
    items = [
        f'Trace32  Port {4711+slot}',
        f'PSU  VISA addr {slot+1}',
        f'PCAN  CAN ch.{slot+1}',
        f'PLIN  COM{slot+3}',
        f'scan_code[{slot+1}]',
        f'CSV: Slot{slot+1}_*.csv',
    ]
    ity = slot_y + slot_label_h + 10
    for it in items:
        text(sx+sw//2, ity, it, 9, C['label'])
        ity += 16

# ---- Module: TestSequenceRunner ----
ts_y = slot_y + slot_h + 6; ts_h=52
rect(FCT_INNER_X, ts_y, FCT_INNER_W, ts_h, C['box_bg'], C['fct_border'], rx=5, stroke_w=1)
rect(FCT_INNER_X, ts_y, FCT_INNER_W, 18, C['fct_border'], C['fct_border'], rx=5)
rect(FCT_INNER_X, ts_y+12, FCT_INNER_W, 8, C['fct_border'], C['fct_border'], rx=0)
text(FCT_INNER_X+FCT_INNER_W//2, ts_y+13, '⑤ test_sequences.TestSequenceRunner  (×4 instances — per slot)', 11, '#FFFFFF', bold=True)
text(FCT_INNER_X+FCT_INNER_W//2, ts_y+32, 'Sequence per slot:  HW_Setup → LED → BAT → Motor → EOS → SG → CAPA → NFC → CAN → LIN', 10, C['label'])
text(FCT_INNER_X+FCT_INNER_W//2, ts_y+46, '• Per-slot adapters: Trace32Interface(port)  PSU(VISA)  PCAN(ch)  PLIN(COM)  |  CAPA: verify auto-fixture provides actuation', 10, C['label'])

# ---- Module: Result Logger (UPDATED) ----
rl_y = ts_y+ts_h+6; rl_h=52
rect(FCT_INNER_X, rl_y, FCT_INNER_W, rl_h, C['upd_bg'], C['fct_border'], rx=5, stroke_w=1)
rect(FCT_INNER_X, rl_y, FCT_INNER_W, 18, '#B8860B', '#B8860B', rx=5)
rect(FCT_INNER_X, rl_y+12, FCT_INNER_W, 8, '#B8860B', '#B8860B', rx=0)
text(FCT_INNER_X+FCT_INNER_W//2, rl_y+13, '⑥ result_logger.py  —  Data Logging  [UPDATED]', 11, '#FFFFFF', bold=True)
text(FCT_INNER_X+FCT_INNER_W//2, rl_y+32, '• CSV per slot: BarcodeID, SlotNo, Variant, DateTime, all test items, PASS/FAIL', 10, C['label'])
text(FCT_INNER_X+FCT_INNER_W//2, rl_y+46, '• HTML: combined 4-slot batch report  |  MySQL logging: optional (TBD)  |  Output → network share or local path', 10, C['label'])

# ═══════════════════════════════════════════════════════════════════════════════
#  SECTION 5 — TEST INSTRUMENTS
# ═══════════════════════════════════════════════════════════════════════════════
rect(INST_X, MID_Y, INST_W, MID_H, C['inst_bg'], C['inst_border'], rx=10)
rect(INST_X, MID_Y, INST_W, 24, C['inst_border'], C['inst_border'], rx=10)
rect(INST_X, MID_Y+18, INST_W, 8, C['inst_border'], C['inst_border'], rx=0)
text(INST_X+INST_W//2, MID_Y+17, 'TEST INSTRUMENTS', 13, '#FFFFFF', bold=True)

instruments = [
    ('Lauterbach Trace32',    ['PowerDebug E40 + DC20A', 'JTAG/SWD flash & verify',
                                '1 or 4 probes (TBD Q16)', 'Port 4711–4714 per slot']),
    ('KIKUSUI PWR401L',       ['40V / 1A PSU', 'VISA address per unit',
                                '1–4 units (TBD Q18)', 'Power cycle control']),
    ('PCAN-USB Pro FD',       ['2× CAN FD channels/unit', '1–2 units for 4 slots',
                                'python-can driver', 'Per-slot channel isolation']),
    ('PLIN-USB',              ['1× LIN channel/unit', '4 units for 4 slots',
                                'PLIN Python API', 'Per-slot COM port']),
    ('I/O Interface Board',   ['USB-Relay / PCIe card', 'OR Modbus TCP gateway',
                                '24V DC / 5V DC (TBD Q5)', 'Optocoupler isolation']),
]

iy2 = MID_Y + 35
for (title, lns) in instruments:
    bh3 = 22 + len(lns)*14
    rect(INST_X+8, iy2, INST_W-16, bh3, C['box_bg'], C['inst_border'], rx=5, stroke_w=1)
    rect(INST_X+8, iy2, INST_W-16, 18, C['inst_border'], C['inst_border'], rx=5)
    rect(INST_X+8, iy2+12, INST_W-16, 8, C['inst_border'], C['inst_border'], rx=0)
    text(INST_X+8+(INST_W-16)//2, iy2+13, title, 11, '#FFFFFF', bold=True)
    ly2 = iy2+28
    for ln in lns:
        text(INST_X+14, ly2, ln, 9, C['label'], anchor='start')
        ly2 += 14
    iy2 += bh3+8

# ═══════════════════════════════════════════════════════════════════════════════
#  SECTION 6 — DATA / REPORTING ROW
# ═══════════════════════════════════════════════════════════════════════════════
rect(PAD, DATA_Y, W-2*PAD, DATA_H, C['data_bg'], C['data_border'], rx=10)
rect(PAD, DATA_Y, W-2*PAD, 24, C['data_border'], C['data_border'], rx=10)
rect(PAD, DATA_Y+18, W-2*PAD, 8, C['data_border'], C['data_border'], rx=0)
text(W//2, DATA_Y+17, 'DATA & REPORTING LAYER  (INDIA)', 13, '#FFFFFF', bold=True)

data_boxes = [
    ('CSV Result Files\n(×4 per batch)',   ['Per slot: BarcodeID + variant', 'All test items (PASS/FAIL)', 'Datetime + SlotNo', 'Naming: YYYYMMDD_SlotN_PASS.csv']),
    ('HTML Batch Report',                  ['Combined 4-slot view', 'Generated after batch', 'Per-PCB test detail', 'Auto-opened or network hosted']),
    ('MySQL Database\n(Optional)',         ['Per-PCB result row', 'Thread-safe connection pool', 'SQLAlchemy ORM', 'Decision: TBD (Q28)']),
    ('Network Share /\nProduction Server', ['UNC path: \\\\server\\FCT\\', 'Server auto-pickup script', 'Traceability database', 'CSV + HTML stored here']),
]

dw = (W-2*PAD-4*10) // 4
dx = PAD+8
for (title, lns) in data_boxes:
    dh2 = 22+len(lns)*14+4
    rect(dx, DATA_Y+32, dw, dh2, C['box_bg'], C['data_border'], rx=5, stroke_w=1)
    rect(dx, DATA_Y+32, dw, 18, C['data_border'], C['data_border'], rx=5)
    rect(dx, DATA_Y+46, dw, 8, C['data_border'], C['data_border'], rx=0)
    title_lines = title.split('\n')
    text(dx+dw//2, DATA_Y+44, title_lines[0], 10, '#FFFFFF', bold=True)
    if len(title_lines)>1:
        text(dx+dw//2, DATA_Y+54, title_lines[1], 9, '#FFFFAA')
    ly3 = DATA_Y+58
    for ln in lns:
        text(dx+8, ly3, ln, 9, C['label'], anchor='start')
        ly3 += 14
    dx += dw+10

# ── Arrow from result_logger down to data row
rl_cx = FCT_X + FCT_W//2
line(rl_cx, rl_y+rl_h, rl_cx, DATA_Y, C['arr_data'], w=2)

# ── Arrow from instruments to test_sequences
inst_mid_y = MID_Y + MID_H//2
fct_right = FCT_X + FCT_W
line(INST_X, inst_mid_y, fct_right, inst_mid_y, C['arr_inst'], w=2)

# ── Bidirectional arrow between SIG and FCT PC
sig_mid_y = MID_Y + 200
bidir_line(SIG_X+SIG_W, sig_mid_y, FCT_X, sig_mid_y, C['arr_plc2fct'], w=3,
           label_txt='Digital I/O', lx=SIG_X+SIG_W+10, ly=sig_mid_y-6)

# ── Bidirectional arrow between PLC and SIG
bidir_line(PLC_X+PLC_W, sig_mid_y, SIG_X, sig_mid_y, '#555555', w=3,
           label_txt='', lx=0, ly=0)

# ═══════════════════════════════════════════════════════════════════════════════
#  LEGEND
# ═══════════════════════════════════════════════════════════════════════════════
lx = PAD; ly = DATA_Y + DATA_H + 6
legend_items = [
    ('#2E7D32', 'Mechanical / Physical'),
    ('#E65100', 'PLC / Robot  (BANWA)'),
    ('#C62828', 'I/O Signal Interface'),
    ('#1565C0', 'FCT Software  (INDIA)'),
    ('#4527A0', 'Test Instruments'),
    ('#F57F17', 'Data / Reporting'),
    ('#2E7D32', 'NEW module'),
    ('#B8860B', 'UPDATED module'),
]
text(lx, ly+14, 'LEGEND:', 11, C['label'], bold=True, anchor='start')
lx += 70
for col, label in legend_items:
    rect(lx, ly+2, 14, 14, col, col, rx=3)
    text(lx+18, ly+14, label, 10, C['label'], anchor='start')
    lx += len(label)*7 + 30

e('</svg>')

svg_content = '\n'.join(lines)
with open('C:/UShin/Testbench_gui_Charan/Continous_Developement/FullAutomationFixture/Full_Automation_Component_Diagram.svg', 'w', encoding='utf-8') as f:
    f.write(svg_content)

print("SVG written.")
print(f"File size: {len(svg_content):,} bytes")
