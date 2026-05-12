"""
Generate: SmartBU_Automation_QA_Rev1.0.xlsx
Sheet 1 : PCB Automation Testing – Q&A
Sheet 2 : Functional Automation Testing with Car Door Handle – Q&A

Engineer : Charan Singh
Project  : BMW SmartBU Automated Test Station
Date     : 11.05.2026
"""

import openpyxl
from openpyxl.styles import PatternFill, Font, Alignment, Border, Side
from openpyxl.utils import get_column_letter

# ─── Helpers ─────────────────────────────────────────────────────────────────
def fill(hex_color):
    return PatternFill("solid", fgColor=hex_color)

def fnt(bold=False, color="1F1F1F", size=10, italic=False):
    return Font(bold=bold, color=color, size=size, name="Calibri", italic=italic)

def thin_border():
    s = Side(style="thin", color="BFBFBF")
    return Border(left=s, right=s, top=s, bottom=s)

def wrap(h="left", v="center"):
    return Alignment(horizontal=h, vertical=v, wrap_text=True)

def col_w(ws, col, w):
    ws.column_dimensions[get_column_letter(col) if isinstance(col, int) else col].width = w

def merge_title(ws, rng, text, bg, fg="FFFFFF", sz=13):
    ws.merge_cells(rng)
    c = ws[rng.split(":")[0]]
    c.value = text
    c.fill = fill(bg)
    c.font = Font(bold=True, color=fg, size=sz, name="Calibri")
    c.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)

# ─── Colours ─────────────────────────────────────────────────────────────────
DKORANGE = "8B3A00"
NAVY   = "1F4E79"
BLUE   = "2E75B6"
LBLUE  = "D6E4F0"
WHITE  = "FFFFFF"
GREEN  = "1E5C2E"
GBKG   = "E2EFDA"
AMBER  = "7F4000"
ABKG   = "FFF2CC"
RED    = "7C0A02"
RBKG   = "FCE4D6"
PURPLE = "4B0082"
PBKG   = "EDE0FF"
TEAL   = "005F6B"
TBKG   = "D6F0F3"
GRAY   = "404040"
ALT1   = "F2F7FB"
ALT2   = "FFFFFF"
OBKG   = "FFF0E0"
OBKG2  = "FFF8F0"

# Section colour map: section_key -> (header_bg, header_fg, q_bg, a_bg)
SEC_STYLE = {
    "CAPA":    (BLUE,   WHITE, ALT1,  "EBF5FB"),
    "SG":      (GREEN,  WHITE, GBKG,  "F0FAF0"),
    "MOTOR":   (RED,    WHITE, RBKG,  "FDF2F2"),
    "EOS":     (AMBER,  WHITE, ABKG,  "FFFAEE"),
    "GENERAL": (GRAY,   WHITE, ALT2,  ALT1),
    "FIXTURE": (NAVY,   WHITE, LBLUE, "EBF3FA"),
    "NFC":     (PURPLE, WHITE, PBKG,  "F5EDFF"),
    "CAN":     (TEAL,   WHITE, TBKG,  "E8F8FA"),
    "LED":     (AMBER,  WHITE, ABKG,  "FFFAEE"),
    "STRATEGY":(GRAY,   WHITE, ALT2,  ALT1),
    "SFUSION":(NAVY,   WHITE, LBLUE, "EBF3FA"),
    "CAPAFW": (BLUE,   WHITE, "E8F4FE", "D8EDFC"),
    "SGFW":   (GREEN,  WHITE, "E8F5E8", "D8EED8"),
    "MOTORFW":(RED,    WHITE, "FDE8E8", "FAD4D4"),
}

# ─── Q&A DATA ─────────────────────────────────────────────────────────────────
# Format: (section_key, section_label, q_number, question, answer)

PCB_QA = [

    # ── CAPA ──────────────────────────────────────────────────────────────────
    ("CAPA", "CAPACITIVE SENSOR (CAPA) TEST", 1,
     "What is the main challenge in automating the CAPA test on a conveyor fixture?",
     "The CAPA test measures very small capacitance values (typically 100 pF range). "
     "In automation, mechanical vibration from the conveyor, pogo-pin bounce, and relay switching "
     "noise inject parasitic capacitance into the measurement path — causing false readings. "
     "A minimum settle delay (200–500 ms) must be inserted after press closure and relay switching "
     "before the measurement window opens."),

    ("CAPA", "CAPACITIVE SENSOR (CAPA) TEST", 2,
     "How do you ensure consistent CAPA readings across every PCB cycle?",
     "The fixture must fully settle before measurement: press fully closed, conveyor stopped, "
     "all relay switching complete, and a minimum settle delay inserted. Any relay switching "
     "near the CAPA signal path must happen before the measurement window opens."),

    ("CAPA", "CAPACITIVE SENSOR (CAPA) TEST", 3,
     "How does stray capacitance from the pogo pin carrier affect the CAPA test?",
     "Every pogo pin, carrier block material, and ribbon cable adds parasitic capacitance. "
     "PEEK carrier material (low dielectric constant ~3.2) is preferred over FR4 to minimise this. "
     "The reference baseline must be calibrated with the fixture closed but no DUT present "
     "to subtract fixture parasitics before production testing begins."),

    ("CAPA", "CAPACITIVE SENSOR (CAPA) TEST", 4,
     "How do you handle the DIP switch signals that CAPA normally requires in the manual fixture?",
     "Manual DIP switches are replaced by software-controlled relays (SPDT) driven by the test PC. "
     "The relay must be confirmed in the correct state before the CAPA measurement starts, "
     "and the CAPA firmware on the DUT must be given sufficient time to re-settle after "
     "relay switching before the ADC read is triggered."),

    # ── SG ────────────────────────────────────────────────────────────────────
    ("SG", "STRAIN GAUGE (SG) TEST", 1,
     "What is the biggest challenge automating SG1 / SG2 testing?",
     "The strain gauge test requires injecting a precise differential voltage across IN+ and IN− "
     "(TP311/TP312 for SG1, TP322/TP324 for SG2) and reading the op-amp output at TP310/TP321. "
     "Pogo pin contact resistance variation (±50–100 mΩ per cycle) adds offset error to the "
     "differential measurement — a critical problem when measuring microvolt-level signals."),

    ("SG", "STRAIN GAUGE (SG) TEST", 2,
     "How can contact resistance variation be mitigated for SG measurements?",
     "Use 4-wire (Kelvin) sensing where possible — separate force and sense pogo pins on critical "
     "SG nodes. Also, the 1.2 kΩ signal conditioning resistors dominate over contact resistance, "
     "reducing its impact. A contact verification step (measure continuity resistance before the "
     "SG test) should be added to the test sequence to confirm good contact before measurement."),

    ("SG", "STRAIN GAUGE (SG) TEST", 3,
     "How does the automatic fixture handle SG reference voltage generation and calibration?",
     "The signal source (DAC or programmable PSU channel) must be calibrated per station. "
     "Tolerance in the 1.2 kΩ resistors on the fixture PCB introduces gain error. "
     "A one-time per-station calibration routine — injecting known voltages and recording the "
     "DUT op-amp output — must be run and the offset/gain stored in the test config JSON file."),

    ("SG", "STRAIN GAUGE (SG) TEST", 4,
     "What is the risk of cross-talk between SG1 and SG2 channels in the auto fixture?",
     "Both SG channels share the IDC34 ribbon cable running in parallel. Capacitive cross-talk "
     "between adjacent wires can corrupt measurements. SG1 and SG2 must not be tested "
     "simultaneously — test one at a time with the other channel's relay open. "
     "Twisted pair or shielded wiring for SG lines in the ribbon cable is recommended."),

    # ── MOTOR ─────────────────────────────────────────────────────────────────
    ("MOTOR", "MOTOR TEST", 1,
     "What is the key challenge in motor testing in an automated fixture vs. manual?",
     "In manual testing the tester monitors the motor by listening and watching. In automation, "
     "the test relies entirely on electrical feedback: DRV_OUT_A/B current signatures via "
     "AI_MOTOR_VISEN (TP412) and diagnostic signal (AI_MOTOR_DIAG, TP414). "
     "PASS/FAIL thresholds must be defined precisely — a stalled, missing, and healthy motor "
     "all produce different current signatures that must be clearly separated."),

    ("MOTOR", "MOTOR TEST", 2,
     "What happens if the motor is not physically loaded in the fixture?",
     "An unloaded motor draws much less current and runs at higher speed than in the real application. "
     "Test thresholds must reflect this unloaded fixture condition and must be agreed with the "
     "customer before commissioning. These thresholds are different from in-application thresholds "
     "and must be clearly documented in the test specification."),

    ("MOTOR", "MOTOR TEST", 3,
     "How do inductive motor transients affect other tests running in the same cycle?",
     "Motor drive switching generates large inductive spikes on the 12V supply rail and GND plane. "
     "These can corrupt CAN/LIN communication and SG/CAPA measurements if the motor test runs "
     "simultaneously. The orchestrator must sequence motor test as an isolated step with a "
     "minimum 300 ms quiet period after motor stop before sensitive measurements resume."),

    ("MOTOR", "MOTOR TEST", 4,
     "How is motor direction verification done automatically?",
     "DRV_OUT_A and DRV_OUT_B H-bridge direction is verified by reading the current direction "
     "via AI_MOTOR_VISEN. The firmware command for CW vs CCW rotation must produce a measurable "
     "difference in this signal. The test script must define separate threshold bands for "
     "forward and reverse current signatures — not a single threshold for both directions."),

    ("MOTOR", "MOTOR TEST", 5,
     "What safety risk exists with motor actuation in an automated fixture?",
     "If the motor drives a mechanical actuator on the DUT and the fixture press is opened while "
     "the motor is still energised, mechanical damage to pogo pins or the DUT can occur. "
     "The test sequence must ensure motor de-energisation is confirmed before the press opening "
     "command is sent to the PLC solenoid valve."),

    # ── EOS ───────────────────────────────────────────────────────────────────
    ("EOS", "EOS (ELECTRONICS ON SETUP) TEST", 1,
     "What does EOS test verify and why is it difficult to automate?",
     "EOS tests verify on-board power distribution: 3.3V rail (TP113), 3.8V rail (TP123), "
     "EOS diagnostic output (TP612/TP613), and IPB GND (TP614). The challenge is that EOS "
     "measurements depend on a stable supply — if the KIKUSUI PSU has not fully settled to "
     "the programmed voltage before EOS is read, all measurements will be out of tolerance."),

    ("EOS", "EOS (ELECTRONICS ON SETUP) TEST", 2,
     "How long must the PSU settle before EOS measurements can begin?",
     "The KIKUSUI PWR401L settles within 50–100 ms of a voltage step. However, with DUT inrush "
     "current from power-up capacitors, the actual rail voltage at test points may take "
     "200–500 ms to stabilise. A minimum settle delay of 500 ms after PSU enable should be "
     "inserted before EOS ADC reads are taken."),

    ("EOS", "EOS (ELECTRONICS ON SETUP) TEST", 3,
     "How does the auto fixture ensure the correct supply voltage is applied per DUT variant?",
     "The orchestrator reads the barcode, looks up the variant configuration from the JSON "
     "config file (automation_gui_settings.json), and sends the correct voltage command to "
     "the PSU before powering the DUT. Hard-coding voltage values in the test script is a "
     "risk — it must always be config-file driven to support all variants (NFC LH/RH, non-NFC LH/RH)."),

    ("EOS", "EOS (ELECTRONICS ON SETUP) TEST", 4,
     "What is the risk of a short-circuit DUT in an automated line?",
     "In manual testing the operator notices immediately. In automation, a DUT with a short "
     "will draw excessive current silently. The PSU must be configured with an over-current "
     "protection (OCP) limit appropriate for the DUT (e.g., 1.5A for 12V supply). "
     "If OCP trips, the test logs FAIL with fault code 'EOS_OCP' and the orchestrator "
     "must power off before opening the press."),

    # ── GENERAL ───────────────────────────────────────────────────────────────
    ("GENERAL", "GENERAL AUTOMATION CHALLENGES", 1,
     "How is test repeatability ensured across 100,000+ press cycles?",
     "Pogo pin wear is the main factor — pins lose spring force after ~500,000 cycles, but "
     "contamination reduces this significantly in production. A preventive maintenance schedule "
     "must be defined: inspect and replace pogo pins every X cycles. A cycle counter in the "
     "MySQL database logs each press event and triggers a maintenance alert at the threshold."),

    ("GENERAL", "GENERAL AUTOMATION CHALLENGES", 2,
     "How do you handle a PCB that is loaded incorrectly (rotated or flipped)?",
     "Alignment tooling pins (Ø4mm, item 11 in BOM) physically prevent wrong orientation "
     "if the PCB has asymmetric tooling holes. Additionally, the barcode scanner must confirm "
     "a valid read before the press is allowed to close — an unreadable barcode (wrong "
     "orientation or missing label) stops the cycle immediately and the PCB is rejected."),

    ("GENERAL", "GENERAL AUTOMATION CHALLENGES", 3,
     "What is the risk of NFC test interference in an automated production line environment?",
     "NFC operates at 13.56 MHz. In a production environment with switching power supplies, "
     "motor drives, and PLC I/O, EMI at this frequency can corrupt NFC measurements. "
     "The NFC test should be performed with the conveyor stopped, all relay switching complete, "
     "and ideally with an RF shield around the NFC zone of the fixture."),

    ("GENERAL", "GENERAL AUTOMATION CHALLENGES", 4,
     "How is test time managed to keep up with conveyor throughput?",
     "Typical functional test time is 60–120 seconds per PCB. The conveyor throughput must "
     "be designed around this cycle time. If faster throughput is needed, parallel stations "
     "are required — not speeding up the test, which risks missed failures. "
     "Never shorten settle delays or timeout values to gain speed."),

    ("GENERAL", "GENERAL AUTOMATION CHALLENGES", 5,
     "What happens if the Lauterbach Trace32 connection fails mid-test?",
     "The orchestrator.py must implement a timeout and retry (max 2 retries) for each T32 "
     "command. If T32 fails after retries, the result is FAIL with fault code 'T32_COMMS'. "
     "The press must open safely and the PCB directed to the reject tray — it must never be "
     "marked as an untested PASS under any condition."),
]

HANDLE_QA = [

    # ── FIXTURE ───────────────────────────────────────────────────────────────
    ("FIXTURE", "GENERAL / FIXTURE CHALLENGES", 1,
     "What is fundamentally different when testing the assembled car handle vs. the bare PCB?",
     "With the bare PCB, all test points are directly accessible by pogo pins. With the assembled "
     "handle, the PCB is sealed inside the plastic housing — there is no direct electrical access "
     "to test points. All electrical connections must go through the handle's OEM connector "
     "(the production harness connector on the handle body). The pogo-pin bed is replaced "
     "by a connector-mate interface."),

    ("FIXTURE", "GENERAL / FIXTURE CHALLENGES", 2,
     "How is the handle physically held in the automated fixture?",
     "The handle has a specific 3D curved shape. It cannot sit flat on a conveyor. "
     "A custom-shaped nest (CNC machined aluminium or 3D printed PETG/ABS) holds the handle "
     "in a repeatable, known orientation. The nest mirrors the handle underside geometry. "
     "Alignment features match handle tooling holes or datum surfaces from the CAD model."),

    ("FIXTURE", "GENERAL / FIXTURE CHALLENGES", 3,
     "How is the production electrical connector mated automatically in the fixture?",
     "The handle's wiring harness connector is mated by a pneumatic actuator-driven connector "
     "block. The connector receptacle on the fixture side is fixed; a cylinder pushes the "
     "handle connector onto it as the fixture closes. Connector insertion force must be within "
     "the connector's rated engagement force to avoid damage to the handle connector."),

    ("FIXTURE", "GENERAL / FIXTURE CHALLENGES", 4,
     "How many test cycles can the OEM connector survive in an automated fixture?",
     "Standard automotive connectors are rated for 20–50 mating cycles for the production harness. "
     "In an automated fixture mating every cycle, this is quickly exceeded. A dedicated test-grade "
     "connector receptacle on the fixture side (gold-plated, high-cycle rated, e.g., 10,000 cycles) "
     "must be used on the fixture side. The handle connector is only mated once per unit."),

    # ── CAPA HANDLE ────────────────────────────────────────────────────────────
    ("CAPA", "CAPACITIVE SENSOR (CAPA) — HANDLE LEVEL", 1,
     "How does CAPA behave differently when the sensor is inside the plastic handle housing?",
     "The plastic handle cover (dielectric) sits between the human hand and the capacitive "
     "sensor electrode. The dielectric constant of the handle plastic (typically ABS or PA66, "
     "εr ≈ 3–4) attenuates the capacitive signal. In the fixture, a conductive probe or "
     "reference plate must simulate the human hand at the correct distance and through "
     "the correct material thickness."),

    ("CAPA", "CAPACITIVE SENSOR (CAPA) — HANDLE LEVEL", 2,
     "How do you simulate a human hand touch in the automated fixture for CAPA verification?",
     "A grounded aluminium or copper probe plate is positioned at the exact touch point on "
     "the handle exterior surface — the same position a driver's hand would rest. "
     "This plate is connected to fixture ground and moved into position by a servo or pneumatic "
     "actuator. The CAPA sensor then sees a capacitive load equivalent to a hand approach."),

    ("CAPA", "CAPACITIVE SENSOR (CAPA) — HANDLE LEVEL", 3,
     "What is the challenge with proximity detection (non-touch CAPA) in the automated fixture?",
     "Proximity CAPA detects a hand approaching — not touching. In the fixture, any nearby "
     "metal structure (press plate, guide columns, frame) acts as a large grounded mass and "
     "shifts the baseline capacitance permanently. The fixture frame near the handle CAPA zone "
     "must use non-conductive material (PEEK, nylon, PETG) to avoid false proximity triggering."),

    ("CAPA", "CAPACITIVE SENSOR (CAPA) — HANDLE LEVEL", 4,
     "How do you verify CAPA unlock vs. CAPA lock thresholds automatically?",
     "The test runs two sub-steps: (1) probe plate NOT present → verify DUT reports 'no hand' "
     "state via CAN message; (2) probe plate IN position → verify DUT reports 'hand detected' "
     "state via CAN. Both thresholds are read from the DUT firmware response over CAN bus, "
     "not from raw ADC values measured externally."),

    # ── SG HANDLE ──────────────────────────────────────────────────────────────
    ("SG", "STRAIN GAUGE (SG) — HANDLE LEVEL", 1,
     "Why is the strain gauge test more meaningful at handle level than at PCB level?",
     "At PCB level, the SG signal path is verified electrically only. At handle level, the "
     "complete mechanical + electrical chain is verified: the SG sensor is bonded to the handle "
     "structure, and when the handle flexes (simulating grip), the sensor must respond correctly. "
     "This catches bonding failures, misplaced sensors, and mechanical deformation issues "
     "invisible at PCB level."),

    ("SG", "STRAIN GAUGE (SG) — HANDLE LEVEL", 2,
     "How do you apply a controlled mechanical load to the handle in the automated fixture?",
     "A calibrated load actuator (servo motor + force sensor, or pneumatic cylinder + pressure "
     "regulator) presses on the defined grip point of the handle with a known force "
     "(e.g., 50N simulating a grip). The fixture nest holds the handle rigidly at its mounting "
     "points, and the actuator applies force perpendicular to the grip surface. "
     "The SG output read via CAN must fall within a defined band for this load."),

    ("SG", "STRAIN GAUGE (SG) — HANDLE LEVEL", 3,
     "What is the risk of over-loading the handle during the SG test?",
     "If the load actuator force is not accurately controlled, the handle can be permanently "
     "deformed or the SG sensor bond can crack. A force sensor (load cell, 0–200N range) "
     "in series with the actuator must provide closed-loop force control, and a hardware force "
     "limit (mechanical stop + over-force cut-off) must be present as a safety backstop."),

    ("SG", "STRAIN GAUGE (SG) — HANDLE LEVEL", 4,
     "How do you achieve test-to-test repeatability for the SG mechanical load?",
     "The handle must seat identically in the nest every cycle (alignment pins to handle datum "
     "holes). The load application point must be fixed relative to the nest, not the handle "
     "surface (which varies with dimensional tolerance). A compliant contact tip (rubber or "
     "UHMW-PE) on the actuator compensates for minor surface variation without altering the "
     "force application point."),

    # ── MOTOR HANDLE ───────────────────────────────────────────────────────────
    ("MOTOR", "MOTOR TEST — HANDLE LEVEL", 1,
     "What does the motor actually do in the car handle and how is this verified?",
     "The motor drives the door latch release mechanism — it retracts the door latch to allow "
     "the door to open (e.g., BMW Comfort Access / keyless entry). In the fixture, the motor "
     "must run through its full travel (extend → retract stroke). A position sensor (hall effect "
     "or optical) in the fixture detects whether the actuator mechanism reached end-of-travel "
     "within the time limit."),

    ("MOTOR", "MOTOR TEST — HANDLE LEVEL", 2,
     "How is motor end-of-travel detected in the automated fixture?",
     "A micro-switch or inductive proximity sensor is positioned at the expected actuator end "
     "position inside the fixture nest. When the motor drives the latch mechanism to full "
     "stroke, the actuator tip triggers the sensor. The test script verifies: "
     "(1) correct current signature via AI_MOTOR_VISEN, "
     "(2) end-of-travel sensor triggered within timeout, "
     "(3) return stroke completes within timeout."),

    ("MOTOR", "MOTOR TEST — HANDLE LEVEL", 3,
     "What happens if the motor mechanism is jammed or stalled in the automated fixture?",
     "A stalled motor draws locked-rotor current (3–5× normal). The test script must detect "
     "this via AI_MOTOR_VISEN exceeding the stall current threshold within the first 200ms "
     "of drive activation. On stall detection: immediately cut motor power, log FAIL with "
     "code 'MOTOR_STALL', open press safely. Do not allow stall to persist — it can burn "
     "the motor driver IC on the DUT."),

    ("MOTOR", "MOTOR TEST — HANDLE LEVEL", 4,
     "How do you verify motor direction (open vs. close latch) automatically?",
     "Two separate commands are sent via CAN to the DUT firmware: "
     "(1) LATCH_RELEASE → motor extends; (2) LATCH_RETURN → motor retracts. "
     "For each direction, the fixture end-stop micro-switches confirm travel completed. "
     "Motor current direction and magnitude are also logged for each command "
     "as a secondary verification."),

    ("MOTOR", "MOTOR TEST — HANDLE LEVEL", 5,
     "What noise does the motor generate and how does it affect other handle-level tests?",
     "The motor generates significant electrical noise on the 12V supply rail and the GND "
     "plane inside the handle. At handle level this noise travels through the actual handle "
     "PCB layout. Motor test must always run as an isolated step — no CAN/LIN messages "
     "expected during motor actuation, and a 300ms quiet period after motor stop is needed "
     "before CAPA or SG readings."),

    # ── EOS HANDLE ─────────────────────────────────────────────────────────────
    ("EOS", "EOS — HANDLE LEVEL", 1,
     "How is the EOS supply routed to the handle in the automated fixture?",
     "The handle receives its 12V supply through the production connector (not pogo pins). "
     "The fixture PSU (KIKUSUI PWR401L) connects to the fixture connector block, which mates "
     "with the handle connector. The supply current path includes the handle's internal wiring "
     "harness — connector contact resistance and wire resistance add to the measurement "
     "and must be accounted for in EOS voltage thresholds."),

    ("EOS", "EOS — HANDLE LEVEL", 2,
     "What is the inrush current challenge at handle level on power-up?",
     "The assembled handle has significantly more bulk capacitance than the bare PCB — "
     "input filter capacitors, motor driver bulk caps, and NFC antenna driver capacitors "
     "all charge on power-up simultaneously. Inrush can reach 2–3A for 5–10ms. "
     "A soft-start (ramp voltage over 50ms) via PSU programming eliminates the inrush "
     "without setting OCP too high."),

    ("EOS", "EOS — HANDLE LEVEL", 3,
     "How do you verify the 3.3V and 3.8V internal rails at handle level without access to test points?",
     "At handle level, these rails are not accessible by pogo pins. Instead, the DUT firmware "
     "reports rail status via a CAN diagnostic message (health status frame). The test reads "
     "this CAN message and checks the reported voltages are within ±5% of nominal. "
     "This is firmware-reported — any ADC calibration error inside the DUT affects the reading."),

    ("EOS", "EOS — HANDLE LEVEL", 4,
     "How do you detect a handle with a damaged internal voltage regulator in automation?",
     "A damaged regulator causes the DUT firmware to either not boot (no CAN response within "
     "2s of power-on = 'NO_COMMS' fault) or boot with an out-of-range voltage in the CAN "
     "health frame. The test sequence first checks for a valid CAN 'alive' message within "
     "2 seconds of power-on before attempting any functional test. "
     "Absence of the alive message = immediate FAIL, press opens, unit rejected."),

    # ── NFC ────────────────────────────────────────────────────────────────────
    ("NFC", "NFC — HANDLE LEVEL", 1,
     "What is different about testing NFC at handle level vs. PCB level?",
     "At PCB level the NFC antenna coil is directly accessible and coupling is direct. "
     "At handle level the antenna is encapsulated inside handle plastic, and the NFC field "
     "must penetrate the cover material. The read range, coupling efficiency, and resonant "
     "frequency change because the plastic affects the antenna's self-capacitance and inductance."),

    ("NFC", "NFC — HANDLE LEVEL", 2,
     "How do you position the NFC reference card consistently in the automated fixture?",
     "The NFC reference card is mounted on a servo-driven arm that moves to a precisely defined "
     "position above the handle NFC window — the same position every cycle. "
     "Distance and angle are set during commissioning by tuning the servo position until "
     "RSSI is maximised. This position is saved as the fixed production test position."),

    ("NFC", "NFC — HANDLE LEVEL", 3,
     "What is the minimum acceptable NFC RSSI threshold at handle level?",
     "This must be defined by the customer test specification for each handle variant. "
     "Typically a minimum RSSI or field strength value returned by the DUT via CAN is specified. "
     "The test script compares the measured value against this minimum. "
     "No threshold should be assumed — it must come from the customer test specification document."),

    ("NFC", "NFC — HANDLE LEVEL", 4,
     "What environmental factors affect NFC testing in a production line?",
     "Metal conveyor rails, steel machine frames, and adjacent handles on the conveyor "
     "reflect and absorb NFC energy, shifting the antenna resonant frequency. "
     "The NFC test must be done with conveyor stopped, no adjacent metal within ~150mm "
     "of the handle NFC zone, and the fixture frame near the NFC window made of "
     "non-metallic material (PEEK, nylon, PETG)."),

    # ── CAN / LIN ──────────────────────────────────────────────────────────────
    ("CAN", "CAN / LIN COMMUNICATION — HANDLE LEVEL", 1,
     "Why is CAN communication the backbone of handle-level functional testing?",
     "At handle level, most test results are not directly measurable electrically — they are "
     "reported by the DUT firmware via CAN diagnostic frames. CAPA state, motor status, "
     "NFC RSSI, EOS rail voltages, SG values, and LED state are all read as CAN messages. "
     "Without a valid CAN link, handle-level functional testing is impossible."),

    ("CAN", "CAN / LIN COMMUNICATION — HANDLE LEVEL", 2,
     "What is the most common CAN communication failure in an automated fixture?",
     "Incorrect termination. A CAN bus requires exactly 120Ω at each end. In the fixture, "
     "the handle connector provides one node and the PCAN-USB provides the other. "
     "If the fixture wiring is long (>0.5m) and unterminated, reflections corrupt frames. "
     "Each fixture must have a 120Ω termination resistor at the fixture PCB CAN connector, "
     "and the PCAN-USB must also be set to terminate."),

    ("CAN", "CAN / LIN COMMUNICATION — HANDLE LEVEL", 3,
     "How do you verify LIN communication at handle level?",
     "The PLIN-USB sends a LIN master request frame and the handle responds as a LIN slave. "
     "The test checks that the response arrives within the LIN slot timeout and contains "
     "the expected data bytes. A missing response = 'LIN_NO_RESPONSE' fault code. "
     "The LIN baud rate must match the DUT firmware configuration (typically 19.2 kbps)."),

    # ── LED ────────────────────────────────────────────────────────────────────
    ("LED", "LED TEST — HANDLE LEVEL", 1,
     "How is the LED verified at handle level in automation?",
     "The LED (ambient/welcome light on handle) is visible through the handle lens. "
     "An optical sensor (photodiode or LDR) or small camera in the fixture detects "
     "LED illumination. The test commands LED ON via CAN, the optical sensor confirms "
     "light above threshold, then OFF is commanded and the sensor confirms light drops. "
     "This is a presence/absence check — colour and luminance require a spectrometer if needed."),

    ("LED", "LED TEST — HANDLE LEVEL", 2,
     "What if the LED is behind a coloured or tinted lens on the handle?",
     "The optical sensor must be calibrated with the specific lens colour and transmission "
     "characteristics. The threshold is set during commissioning using a known-good handle. "
     "A clear lens and an amber lens give very different sensor readings even with identical "
     "LED current — never use a generic threshold across different lens variants."),

    # ── STRATEGY ───────────────────────────────────────────────────────────────
    ("STRATEGY", "OVERALL AUTOMATION STRATEGY", 1,
     "In what order should the handle-level tests run for maximum efficiency?",
     "Recommended sequence:\n"
     "1.  Power ON + EOS alive check (CAN alive message) — gate for all further tests\n"
     "2.  EOS rail verification (CAN health frame)\n"
     "3.  LIN communication check\n"
     "4.  CAN full frame check\n"
     "5.  CAPA proximity (no-touch baseline)\n"
     "6.  CAPA touch simulation (probe plate in)\n"
     "7.  SG mechanical load test\n"
     "8.  Motor extend + return stroke\n"
     "9.  LED ON/OFF optical check\n"
     "10. NFC coupling test (servo positions card)\n"
     "11. Power OFF + EOS off check\n"
     "12. Log result to MySQL, generate HTML report"),

    ("STRATEGY", "OVERALL AUTOMATION STRATEGY", 2,
     "What is the realistic cycle time for full handle-level functional test?",
     "Approximately 90–150 seconds per handle depending on motor stroke time and NFC settle "
     "time. The conveyor and fixture hardware can cycle in under 10 seconds, but the test "
     "time dictates the station output rate. If faster throughput is required, parallel "
     "test stations must be added — never shorten test sequences to gain speed."),

    ("STRATEGY", "OVERALL AUTOMATION STRATEGY", 3,
     "What is the most critical difference between a PCB-level PASS and a handle-level test?",
     "A PCB-level PASS only guarantees the electronics work. A handle-level test additionally "
     "guarantees the complete assembly: correct sensor bonding, correct NFC antenna "
     "encapsulation, correct connector mating, correct motor mechanism travel, and correct "
     "LED lens transmission. A PCB can pass PCB-level test and still fail at handle level "
     "due to assembly defects — both test levels are required."),
]

FIRMWARE_QA = [

    # ── SENSOR FUSION STATE MACHINE ─────────────────────────────────────────────
    ("SFUSION", "SENSOR FUSION STATE MACHINE (SfAppMunich)", 1,
     "What are the 5 states of the SF application state machine and what does each represent?",
     "Defined in sfapp_component_interface.h as SF_ApplicationStateMachine_enum:\n"
     "  SF_IDLE_STATE_e   (0x00) — no sensor input above threshold\n"
     "  SF_LOCK_STATE_e   (0x01) — lock CAPA sensor debounced, no overriding SG pull\n"
     "  SF_UNLOCK_STATE_e (0x02) — unlock CAPA debounced + SG push threshold reached\n"
     "  SF_ADS_STATE_e    (0x03) — approach sensor debounced (XNF variant only)\n"
     "  SF_EOS_STATE_e    (0x04) — SG forced-pull debounced (Emergency-Open-System)\n"
     "All 5 states must be exercised in automation: stimulate the correct CAPA/SG combination,\n"
     "wait for debounce to complete, then read SFAPP_GetArbitratedOutput_s() or CAN diagnostic frame."),

    ("SFUSION", "SENSOR FUSION STATE MACHINE (SfAppMunich)", 2,
     "What is the role of SFMSM (Sensor Fusion Measurement State Machine) and how does it relate to the SF application state machine?",
     "SFMSM (sfmsm.c) is the outer scheduling shell with 3 states:\n"
     "  IDLE → WAIT_FOR_MEASUREMENT (waits for SFMSM_start_sensor_fusion_b flag set by CSA)\n"
     "       → DATA_EVALUATION (executes in one shot):\n"
     "           1. SF_UpdateAllInputsOfSensorFusionStateMachine()\n"
     "           2. SFDEB_UpdateSensorDebouncing()\n"
     "           3. SF_ExecuteApplicationStateMachine()\n"
     "           4. Sets SFMSM_sensor_fusion_finished_b = TRUE\n"
     "In automation: trigger the CSA cycle correctly, wait for SFMSM_sensor_fusion_finished_b = TRUE\n"
     "(read via Trace32) before sampling the SF arbitrated output — reading too early yields stale results."),

    ("SFUSION", "SENSOR FUSION STATE MACHINE (SfAppMunich)", 3,
     "How does sensor debouncing (SFDEB) affect automation test timing and what delays must be respected?",
     "sfdeb.c implements independent debounce timers (each reaches TA_TIMESTAMP_FINAL_e when passed):\n"
     "  • Unlock sensor — SFDEB_CheckUnlockSensorDebounced_b()\n"
     "  • Lock sensor — SFDEB_CheckLockSensorDebounced_b()\n"
     "  • Approach sensor — SFDEB_CheckApproachSensorDebounced_b()\n"
     "  • Direction — SFDEB_CheckDebouncedDirection_e() [CONFIG_SF_DIRECTION_DEBOUNCE_TIME__ms__dU16]\n"
     "  • EOS low-pull / forced-pull / high-pull / ADS-door-closed / ADS-forced-push\n"
     "Key rule: if the stimulus direction changes, the direction debounce RESETS to TA_TIMESTAMP_INITIAL_e.\n"
     "Automation must hold each stimulus for ≥ 2 × debounce time before sampling. Rapid bidirectional\n"
     "stimulation will always read NO_DIRECTION — causing false FAIL results."),

    ("SFUSION", "SENSOR FUSION STATE MACHINE (SfAppMunich)", 4,
     "What happens when both lock and unlock CAPA sensors are simultaneously active and how should automation handle it?",
     "The SF_UnlockOrLockPriority_enum (SF_UNLOCK_HAS_PRIORITY_e or SF_LOCK_HAS_PRIORITY_e) determines\n"
     "which state wins when both sensors are debounced simultaneously.\n"
     "In automation, a conductive probe plate positioned too widely can accidentally stimulate both\n"
     "lock and unlock zones at once — producing an output that depends entirely on the priority setting\n"
     "and may not match the expected state. The test specification must:\n"
     "  1. Verify only one CAPA zone is activated per test sub-step\n"
     "  2. Add a separate test case for simultaneous activation to verify the priority behaviour\n"
     "  3. Document the expected priority configuration in the test spec."),

    ("SFUSION", "SENSOR FUSION STATE MACHINE (SfAppMunich)", 5,
     "How does the SF state machine combine SG1 and SG2 via SFSG_CheckCombinedSGAccessRequest and what test cases cover all paths?",
     "SFSG_CheckCombinedSGAccessRequest() (sfsg.h prototype) combines SG1 and SG2:\n"
     "  • If either sensor's degraded mode is ACTIVATED → that sensor is forced to PULL_DEGRADED_MODE\n"
     "  • SFSG_CheckSGXAccessRequest handles per-sensor implausibility and defect flags\n"
     "  • Combined bitmask is cumulative (lower force levels always included with higher)\n"
     "Automation test cases required:\n"
     "  A. SG1 alone valid PUSH — verify combined = PUSH\n"
     "  B. SG2 alone valid PUSH — verify combined = PUSH\n"
     "  C. Both SG1+SG2 agree on PULL — verify combined = PULL\n"
     "  D. SG1 in degraded mode + SG2 valid PULL — verify combined = PULL_DEGRADED_MODE\n"
     "  E. Both defective — verify combined = NO_ACCESS"),

    # ── CAPA FIRMWARE ─────────────────────────────────────────────────────────
    ("CAPAFW", "CAPACITIVE SENSOR — FIRMWARE DEEP DIVE (CapaAppMunich / sfcapa.c)", 1,
     "What sensors exist in the XNF variant (CAPAAPP_SensorType_enum) and which ones must automation stimulate vs. leave alone?",
     "XNF variant (CAR_VARIANT_XNF) defines 5 sensors in capaapp_component_interface.h:\n"
     "  CAPAAPP_SENSOR_UNLOCK_e      (0x00) — active touch sensor, automation stimulates\n"
     "  CAPAAPP_SENSOR_UNLOCK_REF_e  (0x01) — reference electrode, MUST NOT be stimulated\n"
     "  CAPAAPP_SENSOR_LOCK_e        (0x02) — active touch sensor, automation stimulates\n"
     "  CAPAAPP_SENSOR_APPROACH_e    (0x03) — approach (proximity) sensor, automation stimulates\n"
     "  CAPAAPP_SENSOR_APPROACH_REF_e(0x04) — reference electrode, MUST NOT be stimulated\n"
     "CAPAAPP_AMOUNT_OF_SENSORS_e = 5. The fixture conductive probe must be positioned only over\n"
     "active sensor zones. Any metallic fixture structure near reference electrodes shifts baseline\n"
     "and produces persistent false saturation or wrong touch readings."),

    ("CAPAFW", "CAPACITIVE SENSOR — FIRMWARE DEEP DIVE (CapaAppMunich / sfcapa.c)", 2,
     "What is the difference between HARDWARE_DEFECT and GENERAL_DEFECT (saturation) in CAPA status flags, and how should each be tested?",
     "From sfcapa.c and capaapp_component_interface.h:\n"
     "  HARDWARE_DEFECT  = CAPAAPP_IFACE_SENSOR_STATUS_HARDWARE_DEFECT_dU16\n"
     "    → electrical fault (IC open/short, signal line disconnected)\n"
     "    → triggers CAPAAPP_Request_Complete_Capa_Reinitialization()\n"
     "  GENERAL_DEFECT   = CAPAAPP_IFACE_SENSOR_STATUS_GENERAL_DEFECT_dU16 (saturation)\n"
     "    → measurement exceeded ADC range (probe too close, full-scale reading)\n"
     "Automation test plan:\n"
     "  1. No stimulus → confirm HARDWARE_DEFECT=0, GENERAL_DEFECT=0, TOUCHED=0\n"
     "  2. Normal probe position → confirm TOUCHED=1, no defect flags\n"
     "  3. Probe very close (saturation condition) → confirm GENERAL_DEFECT=1\n"
     "  4. Open-circuit simulate (if supported by fixture) → confirm HARDWARE_DEFECT=1\n"
     "Track via CAN diagnostic message status bits or Trace32 SFCAPA_capa_data_s watch."),

    ("CAPAFW", "CAPACITIVE SENSOR — FIRMWARE DEEP DIVE (CapaAppMunich / sfcapa.c)", 3,
     "What does CAPAAPP_Request_Complete_Capa_Reinitialization() do and why must automation wait before re-testing after a hardware defect?",
     "When SFCAPA_UpdateTouchStatusOnHardwareErrors() detects a hardware defect for the FIRST TIME:\n"
     "  1. Calls CAPAAPP_Request_Complete_Capa_Reinitialization() → full CAPA IC reset\n"
     "  2. Starts timer: CONFIG_SF_CAPA_HARDWARE_DEFECT_BLOCKS_STATUS_TIME__ms__dU16\n"
     "     → during this window ALL sensor touch_status forced to FALSE (no touch reported)\n"
     "  3. Starts timer: CONFIG_SF_CAPA_HARDWARE_DEFECT_RESET_TIME__ms__dU16\n"
     "     → after this time the defect flag resets (re-arming allowed)\n"
     "Automation consequence: after any hardware defect injection test case, the test script MUST\n"
     "wait for both timers to expire before resuming CAPA sensitivity testing — otherwise all CAPA\n"
     "touch readings will be blocked (forced FALSE) and the test produces false failures."),

    ("CAPAFW", "CAPACITIVE SENSOR — FIRMWARE DEEP DIVE (CapaAppMunich / sfcapa.c)", 4,
     "How does CAPA noise suppression work in firmware and what automation action can accidentally trigger it?",
     "In SFCAPA_UpdateCapaSensorData() (sfcapa.c):\n"
     "  IF sensor_noise_status_b == TRUE  → noise_status_b LATCHED to TRUE\n"
     "  ONLY resets when touch_status == FALSE (no touch present)\n"
     "  WHILE noise_status_b == TRUE → sensor_touch_status_b FORCED to FALSE\n"
     "Result: any noise event during a touch = touch silently discarded, returns FALSE.\n"
     "Automation triggers:\n"
     "  • Relay switching near CAPA measurement cycle\n"
     "  • PSU voltage steps during CAPA sensing window\n"
     "  • Motor activation (even on a different DUT) picked up as noise\n"
     "Mitigation: ensure ALL relay switching and supply changes complete ≥300 ms before CAPA\n"
     "measurement window opens. Verify noise_status_b = FALSE (via Trace32) before probe stimulation."),

    # ── SG FIRMWARE ───────────────────────────────────────────────────────────
    ("SGFW", "STRAIN GAUGE — FIRMWARE DEEP DIVE (SgAppMunich / sfsg.c)", 1,
     "Why are SG op-amp diagnostic channels (SG1_OP_PLUS/MINUS, SG2_OP_PLUS/MINUS) disabled in firmware, and what does this mean for PCB-level automation?",
     "From sgm.c (SGAPP_Initialize):\n"
     "  DM_EnableMeasurementChannel(DM_ADC_CHANNEL_SG1_OP_PLUS_e,  FALSE_b)\n"
     "  DM_EnableMeasurementChannel(DM_ADC_CHANNEL_SG1_OP_MINUS_e, FALSE_b)\n"
     "  DM_EnableMeasurementChannel(DM_ADC_CHANNEL_SG2_OP_PLUS_e,  FALSE_b)\n"
     "  DM_EnableMeasurementChannel(DM_ADC_CHANNEL_SG2_OP_MINUS_e, FALSE_b)\n"
     "Comment: 'temporarily disabled until solution found for switching from active to low power mode'\n"
     "Impact on automation:\n"
     "  • Firmware CANNOT detect open/short on the SG element differential input lines\n"
     "  • PCB automation CANNOT rely on firmware-reported SG op-amp input faults\n"
     "  • Instead: automation must inject known input signals and verify op-amp OUTPUT at TP310/TP321\n"
     "  • A missing or out-of-range output response to a stimulated input is the indirect fault indicator"),

    ("SGFW", "STRAIN GAUGE — FIRMWARE DEEP DIVE (SgAppMunich / sfsg.c)", 2,
     "What is the SG temperature compensation timer and how must automation timing account for it?",
     "From sgm.c (SGAPP_Initialize):\n"
     "  Timer: SGM_temperature_compensation_timer_s with period CONFIG_TEMP_COMPENSATION_TIMER__MS__\n"
     "  Callback: SGM_TemperatureCompensationTimerCallback() — recalibrates SG baseline for temp drift\n"
     "Issue for automation:\n"
     "  If an SG measurement window coincides with the compensation callback execution,\n"
     "  the SG baseline is in transition → measurement may be offset from steady-state value.\n"
     "Mitigation:\n"
     "  1. Read CONFIG_TEMP_COMPENSATION_TIMER__MS__ from firmware config header\n"
     "  2. Ensure automation SG measurement window does NOT start within 50 ms of the timer period\n"
     "  3. Alternatively, trigger SG measurement immediately after a known compensation cycle\n"
     "     (read timer status via Trace32) so the next compensation is CONFIG_TEMP_COMPENSATION_TIMER__MS__ away."),

    ("SGFW", "STRAIN GAUGE — FIRMWARE DEEP DIVE (SgAppMunich / sfsg.c)", 3,
     "How does direction debouncing work in SFDEB and what is the minimum hold time the automation must apply to a SG directional signal?",
     "From sfdeb.c — SFDEB_UpdateDirectionDebouncing():\n"
     "  1. If signal direction CHANGES (vs. previous cycle) → debounce state RESET to TA_TIMESTAMP_INITIAL_e\n"
     "  2. SFDEB_UpdateWaitForTimeStamp() runs the timer each cycle\n"
     "  3. Direction is 'debounced' only when state == TA_TIMESTAMP_FINAL_e\n"
     "  Timeout = CONFIG_SF_DIRECTION_DEBOUNCE_TIME__ms__dU16\n"
     "Automation rules:\n"
     "  • Hold each directional stimulus (PUSH or PULL) for ≥ 2 × CONFIG_SF_DIRECTION_DEBOUNCE_TIME ms\n"
     "  • Do NOT reverse direction within the debounce window — this resets the timer\n"
     "  • After reading direction output, allow debounce to lapse before applying opposite direction\n"
     "  • Rapid push-pull-push sequences (typical in some legacy scripts) WILL always read NO_DIRECTION"),

    ("SGFW", "STRAIN GAUGE — FIRMWARE DEEP DIVE (SgAppMunich / sfsg.c)", 4,
     "How does SG degraded mode (SGAPP_IFACE_SGM_DEGRADED_MODE_ACTIVATED_e) alter the SF output bitmask and how should automation test this path?",
     "From sfsg.c — SFSG_CalculateAccessRequestBitMask_U16():\n"
     "  IF degraded mode ACTIVATED → access request FORCED to PULL_DEGRADED_MODE regardless of actual signal\n"
     "  PULL_DEGRADED_MODE bitmask = PULL | HIGH_PULL | FORCED_PULL | DEGRADED_PULL (all 4 bits set)\n"
     "Automation test sequence for degraded mode:\n"
     "  1. Inject SG2 signal with implausibility condition (e.g., out-of-range ADC value)\n"
     "  2. Confirm SGM_State transitions to FailureHandlingMode via Trace32 or CAN\n"
     "  3. Confirm SGAPP_IFACE_SGM_DEGRADED_MODE_ACTIVATED_e is set\n"
     "  4. Inject a normal SG1 PULL signal\n"
     "  5. Verify SF output bitmask = SFAPP_IFACE_PULL_BITMASK | HIGH_PULL | FORCED_PULL | DEGRADED_PULL\n"
     "  6. Restore SG2 to valid range → confirm degraded mode deactivates and bitmask returns to normal"),

    # ── MOTOR FIRMWARE ────────────────────────────────────────────────────────
    ("MOTORFW", "MOTOR APPLICATION — FIRMWARE DEEP DIVE (MotorAppMunich)", 1,
     "How does the motor application select between COLD, NORMAL, and HOT order sheets, and what is the automation implication?",
     "From mam.c — MAM_UpdateMotorOrderSheetForCoupled(MEM_Temp_Zone_enum temperatureZone_e):\n"
     "  COLD  → MotorSheet[COUPLE][MAPP_PARAM_TEMP_LOW_e]\n"
     "  HOT   → MotorSheet[COUPLE][MAPP_PARAM_TEMP_HIGH_e]\n"
     "  NORMAL/UNDEFINED → MotorSheet[COUPLE][MAPP_PARAM_TEMP_NORMAL_e]\n"
     "Same pattern for decouple (MAM_UpdateMotorOrderSheetForDecoupled).\n"
     "Temperature zone comes from MEM (temperature monitoring element) sensor on the PCB.\n"
     "Automation consequence:\n"
     "  • Room-temperature tests only exercise the NORMAL sheet\n"
     "  • Full qualification requires cold-soak (-40°C, MEM_TEMP_ZONE_COLD_e) and hot (+85°C) tests\n"
     "  • Automation station must report the measured temperature zone alongside the motor test result\n"
     "  • Do not apply NORMAL sheet thresholds to a DUT tested cold — the drive parameters differ"),

    ("MOTORFW", "MOTOR APPLICATION — FIRMWARE DEEP DIVE (MotorAppMunich)", 2,
     "What are the two motor drive stages, how are their NVM parameters scaled, and how should automation verify correct NVM loading?",
     "From mac.c — MAC_CopyOrderSheet() and MAPP_SetMotorParameters():\n"
     "  Stage 1 (current-controlled):\n"
     "    current_threshold = sheet1_block_rotor_detection__mA__U16 (direct mA)\n"
     "    duration          = sheet1_movement_duration__2ms_per_LSB__U8 × 2 ms/LSB\n"
     "    target            = sheet1_target_value__mA__U16 (current target in mA)\n"
     "  Stage 2 (voltage-controlled):\n"
     "    current_threshold = sheet2_block_rotor_detection__mA__U16 (direct mA)\n"
     "    duration          = sheet2_movement_duration__5ms_per_LSB__U8 × 5 ms/LSB\n"
     "    target            = sheet2_target_value__mV__U16 (voltage target in mV)\n"
     "  MAPP_SetMotorParameters() returns FALSE if NVM copy fails (restore_ok=0)\n"
     "Automation verification:\n"
     "  1. After firmware boot, read NVM-loaded parameters via Trace32: MAC_Motor_Parameters_s\n"
     "  2. Compare stage 1 duration (converted from raw LSB) against spec limits\n"
     "  3. Verify MAPP_SetMotorParameters return = TRUE — a FALSE means corrupted NVM parameters\n"
     "  4. Observe AI_MOTOR_VISEN current waveform: current-controlled ramp in Stage 1,\n"
     "     then voltage-controlled hold in Stage 2."),

    ("MOTORFW", "MOTOR APPLICATION — FIRMWARE DEEP DIVE (MotorAppMunich)", 3,
     "What are the freewheel (FWS) parameters and how does automation verify correct freewheel behavior?",
     "From mac.c — FWS parameters loaded by MAPP_SetMotorParameters():\n"
     "  fws_voltage_start           [mV] = raw × 20 mV/LSB\n"
     "  fws_voltage_increase_timer  [ms] = raw × 2 ms/LSB\n"
     "  fws_voltage_increase_step   [mV] = raw × 2 mV/LSB\n"
     "  fws_motor_resistance        [mΩ] = raw × 100 mΩ/LSB\n"
     "  fws_motor_forward_timeout   [ms] = raw × 20 ms/LSB\n"
     "  fws_motor_backward_timeout  [ms] = raw × 40 ms/LSB\n"
     "  fws_voltage_max             [mV] = raw × 100 mV/LSB\n"
     "  fws_voltage_offset_couple   [mV] = raw × 20 mV/LSB\n"
     "  fws_motor_wait_time         [ms] = raw × 20 ms/LSB\n"
     "Freewheel purpose: soft-stop the motor after main drive stages to prevent overshoot.\n"
     "Automation test:\n"
     "  1. After motor couple command, sample AI_MOTOR_VISEN at 1 ms resolution\n"
     "  2. Verify current drops smoothly (no oscillation spike) within fws_motor_forward_timeout ms\n"
     "  3. Verify current reaches near-zero within fws_motor_wait_time + fws_motor_forward_timeout ms\n"
     "  4. A freewheel parameter NVM corruption causes abrupt current cut-off or motor bounce —\n"
     "     both are visible as a current spike immediately after Stage 2 ends."),

    ("MOTORFW", "MOTOR APPLICATION — FIRMWARE DEEP DIVE (MotorAppMunich)", 4,
     "How does MAM_Initialize() prepare the motor drive and what happens if it is called when motor is already initialized?",
     "From mam.c — MAM_Initialize():\n"
     "  DCMC_SetRequestedResetOrderSheetQueue(TRUE_b)  → clears any pending order sheets\n"
     "  DCMC_SetExecuteMotorStateMachineRequest(TRUE_b) → enables DCMC state transitions\n"
     "  Note: DCMC will initialize but NOT enable state transitions until the execute flag is TRUE.\n"
     "From sgm.c pattern — if already initialized (SGM_application_data_initialized_b = TRUE),\n"
     "  re-initialization is blocked to prevent duplicate timer/DAC enables.\n"
     "Automation implication:\n"
     "  • After a power-cycle or firmware re-flash, MAM_Initialize() must be called exactly once\n"
     "  • If the test sequence re-boots the DUT mid-test (e.g., after EOS fail), the motor module\n"
     "    reinitializes automatically on next boot — the automation must not assume motor state\n"
     "    persists across a power cycle\n"
     "  • Verify DCMC execute flag is TRUE via Trace32 before commanding motor actions\n"
     "    to avoid commands being silently ignored."),
]

# ─── Sheet Builder ────────────────────────────────────────────────────────────
def build_sheet(wb, title, qa_data, sheet_title_text):
    ws = wb.create_sheet(title)
    ws.sheet_view.showGridLines = False

    # Column widths: A=No, B=Section, C=Question, D=Answer
    col_w(ws, "A", 6)
    col_w(ws, "B", 30)
    col_w(ws, "C", 52)
    col_w(ws, "D", 75)

    # ── Main title ────────────────────────────────────────────────────────────
    ws.row_dimensions[1].height = 40
    merge_title(ws, "A1:D1", sheet_title_text, NAVY, WHITE, sz=13)

    # ── Meta ──────────────────────────────────────────────────────────────────
    ws.row_dimensions[2].height = 15
    ws.row_dimensions[3].height = 15
    for mc, mv in [("A2","Project:"), ("B2","BMW SmartBU Automated Test Station  |  MAE"),
                   ("A3","Date:"),    ("B3","11.05.2026   Rev 1.0")]:
        c = ws[mc]; c.value = mv
        c.font = fnt(bold=(mc[0]=="A"), size=9)

    # ── Column headers ────────────────────────────────────────────────────────
    ws.row_dimensions[4].height = 24
    for ci, h in enumerate(["Q #", "Topic / Section", "Question", "Answer"], 1):
        c = ws.cell(row=4, column=ci, value=h)
        c.fill = fill(NAVY); c.font = fnt(bold=True, color=WHITE, size=10)
        c.alignment = wrap("center"); c.border = thin_border()

    ws.freeze_panes = "A5"

    # ── Rows ──────────────────────────────────────────────────────────────────
    current_section = None
    row = 5
    q_global = 0

    for (sec_key, sec_label, q_num, question, answer) in qa_data:
        style = SEC_STYLE.get(sec_key, (GRAY, WHITE, ALT2, ALT1))
        hdr_bg, hdr_fg, q_bg, a_bg = style

        # Section header row
        if sec_label != current_section:
            current_section = sec_label
            ws.row_dimensions[row].height = 20
            ws.merge_cells(f"A{row}:D{row}")
            c = ws[f"A{row}"]
            c.value = f"  ▶  {sec_label}"
            c.fill = fill(hdr_bg)
            c.font = Font(bold=True, color=hdr_fg, size=10, name="Calibri")
            c.alignment = Alignment(horizontal="left", vertical="center")
            # Apply border to hidden merged cells
            for ci in range(1, 5):
                ws.cell(row=row, column=ci).border = thin_border()
            row += 1

        q_global += 1
        ws.row_dimensions[row].height = 90

        # Q number
        c = ws.cell(row=row, column=1, value=f"Q{q_global}")
        c.fill = fill(hdr_bg); c.font = fnt(bold=True, color=hdr_fg, size=10)
        c.alignment = wrap("center"); c.border = thin_border()

        # Section label
        c = ws.cell(row=row, column=2, value=sec_label)
        c.fill = fill(q_bg); c.font = fnt(bold=False, size=9, color=GRAY)
        c.alignment = wrap("left"); c.border = thin_border()

        # Question
        c = ws.cell(row=row, column=3, value=question)
        c.fill = fill(q_bg); c.font = fnt(bold=True, size=10)
        c.alignment = wrap("left"); c.border = thin_border()

        # Answer
        c = ws.cell(row=row, column=4, value=answer)
        c.fill = fill(a_bg); c.font = fnt(bold=False, size=10)
        c.alignment = wrap("left"); c.border = thin_border()

        row += 1

    # ── Summary footer ────────────────────────────────────────────────────────
    ws.row_dimensions[row].height = 18
    ws.merge_cells(f"A{row}:D{row}")
    c = ws[f"A{row}"]
    c.value = f"  Total questions: {q_global}"
    c.fill = fill(NAVY); c.font = fnt(bold=True, color=WHITE, size=9)
    c.alignment = Alignment(horizontal="right", vertical="center")

# ─── Build workbook ───────────────────────────────────────────────────────────
wb = openpyxl.Workbook()
wb.remove(wb.active)   # remove default blank sheet

build_sheet(wb,
            "PCB Automation Testing",
            PCB_QA,
            "Q&A — PCB Automation Testing Challenges  (SmartBU / XNF I460 / BMW MAE)")

build_sheet(wb,
            "Handle Functional Testing",
            HANDLE_QA,
            "Q&A — Functional Automation Testing with Car Door Handle  (SmartBU / BMW MAE)")

build_sheet(wb,
            "Firmware and Sensor Fusion",
            FIRMWARE_QA,
            "Q&A — Firmware & Sensor Fusion Deep Dive  (SfAppMunich / SgAppMunich / CapaAppMunich / MotorAppMunich)")

# ─── Save ─────────────────────────────────────────────────────────────────────
out_path = (r"c:\UShin\Testbench_gui_Charan\Continous_Developement"
            r"\BOM_SmartBU_Automation\SmartBU_Automation_QA_Rev2.0.xlsx")
wb.save(out_path)
print(f"Saved : {out_path}")
print(f"Sheets: {[s.title for s in wb.worksheets]}")
print(f"Firmware Q&A entries: {len(FIRMWARE_QA)}")
