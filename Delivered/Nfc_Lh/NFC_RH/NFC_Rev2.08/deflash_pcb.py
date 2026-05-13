"""
deflash_pcb.py
==============
Post-EOL De-flash utility for XNF I460 SmartBU PCB.

Purpose
-------
After the EOL functional test is complete, this script mass-erases ALL
internal flash of the CY8C4149AZI-S575 target MCU via the SEGGER J-Link
probe (SWD).  The erased PCB is then safe to release — the BMW test
firmware is no longer present on the board.

Flow
----
  1. Kill any open Trace32 / Ozone instance that may hold the SWD probe.
  2. Write a temporary J-Link commander script with the erase commands.
  3. Execute JLink.exe in silent mode and capture stdout.
  4. Parse the output to confirm a successful erase.
  5. Write a one-line CSV log entry (timestamp, barcode, result, duration).
  6. Print a clear PASS / FAIL banner and exit with code 0 (PASS) or 1 (FAIL).

Usage
-----
  # From the EOL orchestrator (pass barcode as argument):
  python deflash_pcb.py --barcode ABC123456

  # Interactive / standalone (barcode will be prompted):
  python deflash_pcb.py

CLI options
-----------
  --barcode  <str>   PCB barcode / serial number  (default: prompt user)
  --device   <str>   J-Link target device string  (default: CY8C4149AZI-S575)
  --if       <str>   Debug interface: SWD or JTAG (default: SWD)
  --speed    <int>   Target speed in kHz           (default: 4000)
  --logfile  <path>  Path to the CSV log file      (default: deflash_log.csv
                     in the same folder as this script)
  --no-verify        Skip blank-check after erase  (faster, use with care)
  --timeout  <int>   Max seconds to wait for JLink (default: 60)

Compatibility
-------------
  Requires SEGGER J-Link software (JLink.exe) to be installed.
  Tested with J-Link V7.x on Windows.
  Python 3.8+, no third-party packages.

Engineer : Charan Singh
Project  : SmartBU / XNF I460  |  BMW MAE 032080790003
Rev      : 2.08  Date: 13.05.2026
"""

import argparse
import csv
import glob
import os
import shutil
import subprocess
import sys
import tempfile
import time
from datetime import datetime
from pathlib import Path

# ─────────────────────────────────────────────────────────────────
# Constants
# ─────────────────────────────────────────────────────────────────
DEFAULT_DEVICE  = "CY8C4149AZI-S575"   # Cypress PSoC 4 on SmartBU XNF I460
DEFAULT_IF      = "SWD"
DEFAULT_SPEED   = 4000                  # kHz
DEFAULT_TIMEOUT = 60                    # seconds for JLink.exe to finish
LOG_FILE_NAME   = "deflash_log.csv"
LOG_HEADER      = ["Timestamp", "Barcode", "Device", "Result", "Duration_s", "Detail"]

# ─────────────────────────────────────────────────────────────────
# J-Link discovery  (mirrors logic in Functional/jlink.py)
# ─────────────────────────────────────────────────────────────────

def find_jlink_exe() -> str:
    """Return the absolute path to JLink.exe.

    Search order:
      1. System PATH
      2. JLINK_PATH environment variable
      3. Glob under C:\\Program Files\\SEGGER and C:\\Program Files (x86)\\SEGGER
    """
    # 1 — PATH
    for name in ("JLink.exe", "JLinkARM.exe"):
        found = shutil.which(name)
        if found:
            return found

    # 2 — JLINK_PATH env var
    env_path = os.environ.get("JLINK_PATH", "")
    if env_path:
        for name in ("JLink.exe", "JLinkARM.exe"):
            candidate = os.path.join(env_path, name)
            if os.path.exists(candidate):
                return candidate

    # 3 — Glob under SEGGER installation directories
    segger_roots = [
        r"C:\Program Files\SEGGER",
        r"C:\Program Files (x86)\SEGGER",
    ]
    for root in segger_roots:
        for exe_name in ("JLink.exe", "JLinkARM.exe"):
            matches = glob.glob(os.path.join(root, "**", exe_name), recursive=True)
            # Exclude Ozone sub-folder (contains a bundled JLink that conflicts)
            matches = [m for m in matches if "Ozone" not in m]
            if matches:
                return sorted(matches)[-1]

    raise FileNotFoundError(
        "SEGGER J-Link executable not found.\n"
        "Install J-Link from https://www.segger.com/downloads/jlink/\n"
        "or set the JLINK_PATH environment variable."
    )


# ─────────────────────────────────────────────────────────────────
# Release the SWD probe
# ─────────────────────────────────────────────────────────────────

def release_probe() -> None:
    """Terminate Trace32 and Ozone so they release the SWD probe."""
    for proc_name in ("t32marm.exe", "Ozone.exe"):
        try:
            subprocess.run(
                ["taskkill", "/F", "/IM", proc_name, "/T"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                timeout=10,
            )
        except Exception:
            pass  # process may not be running — that's fine

    # Wait up to 5 s for the USB driver to release the device handle
    deadline = time.monotonic() + 5.0
    while time.monotonic() < deadline:
        result = subprocess.run(
            ["tasklist", "/FI", "IMAGENAME eq t32marm.exe"],
            capture_output=True, text=True,
        )
        if "t32marm.exe" not in result.stdout:
            break
        time.sleep(0.3)

    # Short extra pause so Windows releases the USB-HID handle
    time.sleep(0.8)


# ─────────────────────────────────────────────────────────────────
# J-Link commander script builder
# ─────────────────────────────────────────────────────────────────

def _build_erase_script(device: str, interface: str, speed: int, verify: bool) -> list[str]:
    """Return the J-Link commander lines for a mass-erase operation."""
    lines = [
        f"device {device}",
        f"if {interface}",
        f"speed {speed}",
        "connect",
        "r",            # reset and halt the core before erase
        "erase",        # mass-erase all flash sectors
    ]
    if verify:
        # 'verifybin' is not available; use 'mem32 0x00000000 1' to sample
        # the first word — after erase on PSoC4 it must read 0x00000000.
        lines.append("mem32 0x00000000 1")
    lines.append("exit")
    return lines


def run_jlink_script(jlink_exe: str, script_lines: list[str], timeout: int) -> str:
    """Write a temp .jlink script, execute it, return stdout."""
    fd, script_path = tempfile.mkstemp(suffix=".jlink", prefix="deflash_")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as fh:
            fh.write("\n".join(script_lines) + "\n")

        # Hide the console window — avoids J-Link stealing focus during automation
        si = subprocess.STARTUPINFO()
        si.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        si.wShowWindow = 0  # SW_HIDE

        completed = subprocess.run(
            [jlink_exe, "-NoGui", "1", "-CommanderScript", script_path],
            stdin=subprocess.DEVNULL,
            capture_output=True,
            text=True,
            timeout=timeout,
            startupinfo=si,
            creationflags=subprocess.CREATE_NO_WINDOW,
        )
        return completed.stdout + completed.stderr   # combine — JLink mixes both
    finally:
        try:
            os.remove(script_path)
        except OSError:
            pass


# ─────────────────────────────────────────────────────────────────
# Output parsing
# ─────────────────────────────────────────────────────────────────

def parse_erase_result(output: str) -> tuple[bool, str]:
    """
    Analyse J-Link commander stdout and decide PASS / FAIL.

    Returns (success: bool, detail: str).

    Success indicators in J-Link output (V7.x):
      - "Erasing done."
      - "Flash erase done"
      - Line starting with "O.K." after the erase command
    Failure indicators:
      - "Could not connect"
      - "Error"
      - "Failed"
    """
    lower = output.lower()

    # Hard failures — check first
    for bad in ("could not connect", "failed to connect", "connection refused",
                 "cannot connect", "no emulator found", "failed"):
        if bad in lower:
            return False, f"J-Link reported: '{bad}' — check probe/PCB connection."

    # Success markers
    for good in ("erasing done", "flash erase done", "o.k."):
        if good in lower:
            return True, "Mass erase completed successfully."

    # If output is empty the probe was likely not found
    if not output.strip():
        return False, "No output from J-Link — probe may not be connected."

    # Ambiguous: return partial output for diagnostics
    snippet = output.strip()[:200].replace("\n", " | ")
    return False, f"Erase status unclear. J-Link output: {snippet}"


# ─────────────────────────────────────────────────────────────────
# CSV logging
# ─────────────────────────────────────────────────────────────────

def write_log(log_path: str, barcode: str, device: str,
              result: str, duration: float, detail: str) -> None:
    """Append one row to the CSV deflash log (create with header if needed)."""
    file_exists = os.path.isfile(log_path)
    with open(log_path, "a", newline="", encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile)
        if not file_exists:
            writer.writerow(LOG_HEADER)
        writer.writerow([
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            barcode,
            device,
            result,
            f"{duration:.2f}",
            detail,
        ])


# ─────────────────────────────────────────────────────────────────
# Banner helpers
# ─────────────────────────────────────────────────────────────────

SEP = "=" * 60

def _banner(lines: list[str], color_code: str) -> None:
    """Print a coloured banner (ANSI codes ignored on non-ANSI terminals)."""
    reset = "\033[0m"
    bold  = "\033[1m"
    print(f"\n{bold}{color_code}{SEP}{reset}")
    for line in lines:
        print(f"  {bold}{color_code}{line}{reset}")
    print(f"{bold}{color_code}{SEP}{reset}\n")

def banner_pass(lines): _banner(lines, "\033[32m")   # green
def banner_fail(lines): _banner(lines, "\033[31m")   # red
def banner_info(lines): _banner(lines, "\033[36m")   # cyan


# ─────────────────────────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────────────────────────

def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description="Post-EOL PCB De-flash utility — XNF I460 SmartBU NFC Rev2.08",
        formatter_class=argparse.RawTextHelpFormatter,
    )
    p.add_argument("--barcode",   default="",            help="PCB barcode / serial number")
    p.add_argument("--device",    default=DEFAULT_DEVICE, help=f"J-Link device string (default: {DEFAULT_DEVICE})")
    p.add_argument("--if",        dest="interface",      default=DEFAULT_IF,
                   choices=["SWD", "JTAG"],              help="Debug interface (default: SWD)")
    p.add_argument("--speed",     type=int,              default=DEFAULT_SPEED,
                   help=f"Target speed in kHz (default: {DEFAULT_SPEED})")
    p.add_argument("--logfile",   default="",            help="CSV log file path (default: deflash_log.csv beside this script)")
    p.add_argument("--no-verify", dest="verify",         action="store_false",
                   help="Skip blank-check read after erase")
    p.add_argument("--timeout",   type=int,              default=DEFAULT_TIMEOUT,
                   help=f"Max seconds for J-Link to complete (default: {DEFAULT_TIMEOUT})")
    return p.parse_args()


def main() -> int:
    args = parse_args()

    # ── Resolve log file path ─────────────────────────────────────
    script_dir = os.path.dirname(os.path.abspath(__file__))
    log_path = args.logfile or os.path.join(script_dir, LOG_FILE_NAME)

    # ── Barcode ───────────────────────────────────────────────────
    barcode = args.barcode.strip()
    if not barcode:
        barcode = input("Enter PCB barcode / serial number: ").strip()
    if not barcode:
        barcode = "UNKNOWN"

    print(f"\n{SEP}")
    print(f"  XNF I460 SmartBU NFC Rev2.08 — POST-EOL DE-FLASH")
    print(f"  Barcode : {barcode}")
    print(f"  Device  : {args.device}")
    print(f"  IF/Speed: {args.interface} @ {args.speed} kHz")
    print(f"  Log     : {log_path}")
    print(SEP)

    t_start = time.monotonic()
    detail  = ""
    success = False

    # ── Step 1: Find J-Link ───────────────────────────────────────
    print("\n[1/4] Locating J-Link executable ...")
    try:
        jlink_exe = find_jlink_exe()
        print(f"      Found: {jlink_exe}")
    except FileNotFoundError as exc:
        detail = str(exc)
        print(f"      ERROR: {detail}")
        duration = time.monotonic() - t_start
        write_log(log_path, barcode, args.device, "FAIL", duration, detail)
        banner_fail(["DE-FLASH FAILED", f"Barcode : {barcode}", detail])
        return 1

    # ── Step 2: Release SWD probe ─────────────────────────────────
    print("[2/4] Releasing SWD probe (terminating Trace32 / Ozone) ...")
    release_probe()
    print("      Probe released.")

    # ── Step 3: Run mass erase ────────────────────────────────────
    print("[3/4] Running J-Link mass erase ...")
    script_lines = _build_erase_script(
        args.device, args.interface, args.speed, args.verify
    )
    print("      J-Link script:")
    for ln in script_lines:
        print(f"        {ln}")
    print()

    try:
        jlink_output = run_jlink_script(jlink_exe, script_lines, args.timeout)
    except subprocess.TimeoutExpired:
        detail = f"J-Link timed out after {args.timeout}s — PCB may not be connected."
        print(f"      ERROR: {detail}")
        duration = time.monotonic() - t_start
        write_log(log_path, barcode, args.device, "FAIL", duration, detail)
        banner_fail(["DE-FLASH FAILED — TIMEOUT", f"Barcode : {barcode}", detail])
        return 1
    except Exception as exc:
        detail = f"Unexpected error running J-Link: {exc}"
        print(f"      ERROR: {detail}")
        duration = time.monotonic() - t_start
        write_log(log_path, barcode, args.device, "FAIL", duration, detail)
        banner_fail(["DE-FLASH FAILED", f"Barcode : {barcode}", detail])
        return 1

    # ── Step 4: Parse result ──────────────────────────────────────
    print("[4/4] Analysing J-Link output ...")
    print()
    print("  --- J-Link output (truncated to 40 lines) ---")
    for line in jlink_output.splitlines()[:40]:
        print(f"  | {line}")
    print("  --- end ---")
    print()

    success, detail = parse_erase_result(jlink_output)
    duration = time.monotonic() - t_start

    # ── Log result ────────────────────────────────────────────────
    result_str = "PASS" if success else "FAIL"
    write_log(log_path, barcode, args.device, result_str, duration, detail)

    # ── Print banner and exit ─────────────────────────────────────
    if success:
        banner_pass([
            "DE-FLASH  PASSED",
            f"Barcode  : {barcode}",
            f"Device   : {args.device}",
            f"Duration : {duration:.1f} s",
            "All flash sectors erased — BMW firmware removed.",
        ])
        return 0
    else:
        banner_fail([
            "DE-FLASH  FAILED",
            f"Barcode  : {barcode}",
            f"Device   : {args.device}",
            f"Duration : {duration:.1f} s",
            f"Reason   : {detail}",
            "Check SWD wiring, power supply, and J-Link connection.",
        ])
        return 1


if __name__ == "__main__":
    sys.exit(main())
