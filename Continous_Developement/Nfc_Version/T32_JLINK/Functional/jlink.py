import ctypes
import glob
import os
import shutil
import subprocess
import tempfile
import threading
from pathlib import Path
from typing import Any


class JLinkBackend:
    def __init__(self):
        self.jlink_path = self._find_jlink_exe()
        self.ozone_path = self._find_ozone_exe()
        self.connected = False
        self.elffile = None
        self._ozone_process = None      # running Ozone GUI process
        self._ozone_project_path = None # temp .jdebug file
        # CY8C4149AZI-S575 is the SmartBU target MCU (Cypress PSoC 4).
        # Override with env var JLINK_DEVICE if a different target is needed.
        self.device = os.getenv("JLINK_DEVICE", "CY8C4149AZI-S575")
        self.interface = os.getenv("JLINK_IF", "SWD")
        self.speed = os.getenv("JLINK_SPEED", "4000")
        self._connect_lock = threading.Lock()  # prevents overlapping connect() calls
        self._ozone_lock = threading.Lock()    # prevents concurrent suspend/resume
        self._dll = None                       # JLinkARM.dll handle (loaded on demand)
        self._dll_connected = False            # whether DLL has an open target session

    def _find_jlink_exe(self) -> str:
        # 1. Check PATH first
        candidate = shutil.which("JLink.exe") or shutil.which("JLinkARM.exe")
        if candidate:
            return candidate

        # 2. Check JLINK_PATH environment variable (set by some installers)
        env_path = os.environ.get("JLINK_PATH", "")
        if env_path:
            for name in ("JLink.exe", "JLinkARM.exe"):
                full = os.path.join(env_path, name)
                if os.path.exists(full):
                    return full

        # 3. Glob search under SEGGER folder — covers versioned installs like JLink_V936
        segger_roots = [
            r"C:\Program Files\SEGGER",
            r"C:\Program Files (x86)\SEGGER",
        ]
        for root in segger_roots:
            for exe_name in ("JLink.exe", "JLinkARM.exe"):
                matches = glob.glob(os.path.join(root, "**", exe_name), recursive=True)
                # Exclude Ozone subfolder to avoid picking the bundled JLink inside Ozone
                matches = [m for m in matches if "Ozone" not in m]
                if matches:
                    return sorted(matches)[-1]

        raise FileNotFoundError(
            "Segger J-Link executable not found.\n"
            "Install J-Link from https://www.segger.com/downloads/jlink/\n"
            "or set the JLINK_PATH environment variable to the folder containing JLink.exe."
        )

    def _find_ozone_exe(self) -> str:
        """Find SEGGER Ozone debugger executable."""
        candidate = shutil.which("Ozone.exe")
        if candidate:
            return candidate

        segger_roots = [
            r"C:\Program Files\SEGGER\Ozone",
            r"C:\Program Files (x86)\SEGGER\Ozone",
            r"C:\Program Files\SEGGER",
            r"C:\Program Files (x86)\SEGGER",
        ]
        for root in segger_roots:
            matches = glob.glob(os.path.join(root, "**", "Ozone.exe"), recursive=True)
            if matches:
                return sorted(matches)[-1]

        raise FileNotFoundError(
            "SEGGER Ozone not found.\n"
            "Install Ozone from https://www.segger.com/products/development-tools/ozone-j-link-debugger/"
        )

    def _generate_ozone_project(self, elf_path: str) -> str:
        """Generate a temporary Ozone .jdebug project file for the SmartBU target."""
        # Ozone project files use forward slashes
        elf_forward = elf_path.replace("\\", "/")
        speed_mhz = int(self.speed) // 1000 or 1

        content = f"""\
/*
 * Auto-generated Ozone project for SmartBU Testbench GUI
 * Target : {self.device}
 * ELF    : {elf_forward}
 */

void OnProjectLoad(void) {{
    Project.SetDevice("{self.device}");
    Project.SetHostIF("USB", "");
    Project.SetTargetIF("{self.interface}");
    Project.SetTIFSpeed("{speed_mhz} MHz");
    Project.AddSvdFile("$(InstallDir)/Config/CPU/Cortex-M0.svd");
    File.Open("{elf_forward}");
}}
"""
        fd, project_path = tempfile.mkstemp(suffix=".jdebug", prefix="smartbu_jlink_")
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write(content)
        return project_path

    def _run_script(self, lines):
        fd, script_path = tempfile.mkstemp(suffix=".jlink")
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as handle:
                handle.write("\n".join(lines) + "\n")

            # On Windows, hide the JLink console window so it never steals focus
            # or sends window messages to the Tkinter main loop (which causes freezes).
            si = subprocess.STARTUPINFO()
            si.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            si.wShowWindow = 0  # SW_HIDE

            completed = subprocess.run(
                [self.jlink_path, "-NoGui", "1", "-CommanderScript", script_path],
                stdin=subprocess.DEVNULL,
                capture_output=True,
                text=True,
                timeout=60,
                startupinfo=si,
                creationflags=subprocess.CREATE_NO_WINDOW,
            )
            if completed.returncode != 0:
                raise RuntimeError(
                    f"J-Link command failed: {completed.stderr.strip() or completed.stdout.strip()}"
                )
            return completed.stdout
        finally:
            try:
                os.remove(script_path)
            except OSError:
                pass

    def _base_script(self):
        return [
            f"device {self.device}",
            f"if {self.interface}",
            f"speed {self.speed}",
            "connect",
        ]

    def _resolve_elf(self, repo_path, selected_preset):
        repo_path = str(repo_path).replace("/", "\\")
        if selected_preset.get() == 1:
            elf_path = Path(repo_path) / "Non_Nfc_Test" / "XNF-Handle_NonDriver_C2_App.elf"
        else:
            elf_path = Path(repo_path) / "Nfc_Test" / "XNF-Handle_Driver_C2_App.elf"

        if not elf_path.is_file():
            raise FileNotFoundError(
                f"Could not locate ELF for selected preset: {elf_path}"
            )
        return str(elf_path)

    def connect(self, repo_path_entry, selected_preset, status_label=None):
        """Launch Ozone with an auto-generated project file for the selected ELF."""
        # Prevent multiple concurrent connect() calls (user clicking the button
        # multiple times while the first call is sleeping / launching Ozone).
        if not self._connect_lock.acquire(blocking=False):
            return   # another thread is already connecting — ignore this click
        try:
            self._connect(repo_path_entry, selected_preset, status_label)
        finally:
            self._connect_lock.release()

    def _connect(self, repo_path_entry, selected_preset, status_label=None):
        """Internal connect implementation (runs inside _connect_lock)."""
        # Show 'Connecting…' immediately so the user doesn't click again
        if status_label:
            status_label.after(0, lambda: status_label.config(text="Status: Connecting…", fg="gray"))

        repo_path = repo_path_entry.get() if hasattr(repo_path_entry, "get") else str(repo_path_entry)
        self.elffile = self._resolve_elf(repo_path, selected_preset)

        # Close any previously opened Ozone instance and WAIT for it to exit
        # before opening a new one — Ozone holds the J-Link probe exclusively,
        # so if the old instance is still shutting down when the new one starts
        # it fails to grab the probe and immediately exits.
        if self._ozone_process and self._ozone_process.poll() is None:
            self._ozone_process.terminate()
            try:
                self._ozone_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self._ozone_process.kill()
                self._ozone_process.wait(timeout=2)
        self._ozone_process = None

        # Brief pause so Windows releases the USB-HID handle the old Ozone held
        import time as _time
        _time.sleep(0.8)

        # Clean up previous temp project file
        if self._ozone_project_path and os.path.exists(self._ozone_project_path):
            try:
                os.remove(self._ozone_project_path)
            except OSError:
                pass

        self._ozone_project_path = self._generate_ozone_project(self.elffile)

        # Launch Ozone as a completely independent GUI process.
        # DETACHED_PROCESS ensures Ozone owns its own session and won't be
        # killed when Python exits.  Do NOT use CREATE_NO_WINDOW here —
        # that flag is for console apps only and prevents Ozone's Win32
        # message loop from initializing, causing an immediate crash.
        self._ozone_process = subprocess.Popen(
            [self.ozone_path, self._ozone_project_path],
            creationflags=subprocess.DETACHED_PROCESS,
        )
        self.connected = True
        if status_label:
            status_label.after(0, lambda: status_label.config(text="Status: stopped at breakpoint", fg="#D35400"))

    def disconnect(self, status_label=None):
        """Close Ozone and the DLL session."""
        self._dll_close()
        if self._ozone_process and self._ozone_process.poll() is None:
            self._ozone_process.terminate()
            try:
                self._ozone_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self._ozone_process.kill()
        self._ozone_process = None

        if self._ozone_project_path and os.path.exists(self._ozone_project_path):
            try:
                os.remove(self._ozone_project_path)
            except OSError:
                pass
        self._ozone_project_path = None
        self.connected = False
        if status_label:
            status_label.after(0, lambda: status_label.config(text="Status: Disconnected", fg="red"))

    # ------------------------------------------------------------------
    # JLinkARM.dll — shared with Ozone, no subprocess, no probe conflicts
    # ------------------------------------------------------------------
    def _find_jlink_dll(self) -> str:
        """Locate JLinkARM.dll next to the JLink.exe we already found."""
        dll_path = os.path.join(os.path.dirname(self.jlink_path), "JLinkARM.dll")
        if os.path.exists(dll_path):
            return dll_path
        # Fallback: search SEGGER folder
        for root in (r"C:\Program Files\SEGGER", r"C:\Program Files (x86)\SEGGER"):
            matches = glob.glob(os.path.join(root, "**", "JLinkARM.dll"), recursive=True)
            if matches:
                return sorted(matches)[-1]
        raise FileNotFoundError("JLinkARM.dll not found next to JLink.exe")

    def _load_dll(self):
        """Load and connect via JLinkARM.dll (shared with Ozone)."""
        if self._dll is not None and self._dll_connected:
            return self._dll

        dll_path = self._find_jlink_dll()
        dll = ctypes.CDLL(dll_path)

        # Set up required function signatures
        dll.JLINKARM_Open.restype = ctypes.c_char_p
        dll.JLINKARM_Open.argtypes = []
        dll.JLINKARM_Close.restype = None
        dll.JLINKARM_Close.argtypes = []
        dll.JLINKARM_TIF_Select.restype = ctypes.c_int
        dll.JLINKARM_TIF_Select.argtypes = [ctypes.c_int]
        dll.JLINKARM_SetSpeed.restype = None
        dll.JLINKARM_SetSpeed.argtypes = [ctypes.c_long]
        dll.JLINKARM_ExecCommand.restype = ctypes.c_int
        dll.JLINKARM_ExecCommand.argtypes = [ctypes.c_char_p, ctypes.c_char_p, ctypes.c_int]
        dll.JLINKARM_Connect.restype = ctypes.c_int
        dll.JLINKARM_Connect.argtypes = []
        dll.JLINKARM_ReadMemU32.restype = ctypes.c_int
        dll.JLINKARM_ReadMemU32.argtypes = [ctypes.c_uint32, ctypes.c_uint32, ctypes.POINTER(ctypes.c_uint32), ctypes.POINTER(ctypes.c_uint8)]
        dll.JLINKARM_WriteU32.restype = ctypes.c_int
        dll.JLINKARM_WriteU32.argtypes = [ctypes.c_uint32, ctypes.c_uint32]
        dll.JLINKARM_Go.restype = None
        dll.JLINKARM_Go.argtypes = []
        dll.JLINKARM_Halt.restype = ctypes.c_int
        dll.JLINKARM_Halt.argtypes = []
        dll.JLINKARM_Reset.restype = None
        dll.JLINKARM_Reset.argtypes = []

        err_buf = ctypes.create_string_buffer(256)
        err = dll.JLINKARM_Open()
        if err:
            raise RuntimeError(f"JLinkARM_Open failed: {err.decode(errors='replace')}")

        # Select interface and speed
        TIF_SWD = 1
        dll.JLINKARM_TIF_Select(TIF_SWD)
        dll.JLINKARM_SetSpeed(int(self.speed))

        # Set device
        cmd = f"Device = {self.device}"
        dll.JLINKARM_ExecCommand(cmd.encode(), err_buf, 256)

        ret = dll.JLINKARM_Connect()
        if ret < 0:
            dll.JLINKARM_Close()
            raise RuntimeError(f"JLinkARM_Connect failed (code {ret})")

        self._dll = dll
        self._dll_connected = True
        return dll

    def _dll_close(self):
        """Disconnect and unload the DLL session."""
        if self._dll is not None:
            try:
                self._dll.JLINKARM_Close()
            except Exception:
                pass
        self._dll = None
        self._dll_connected = False

    def _write_u32(self, address: int, value: int):
        """Write a 32-bit word to target memory via JLinkARM.dll (Ozone stays open)."""
        dll = self._load_dll()
        ret = dll.JLINKARM_WriteU32(ctypes.c_uint32(address), ctypes.c_uint32(value & 0xFFFFFFFF))
        if ret != 0:
            raise RuntimeError(f"JLINKARM_WriteU32 failed at 0x{address:08X} (code {ret})")

    def _read_u32(self, address: int) -> int:
        """Read a 32-bit word from target memory via JLinkARM.dll (Ozone stays open)."""
        dll = self._load_dll()
        buf = (ctypes.c_uint32 * 1)()
        status = (ctypes.c_uint8 * 1)()
        n = dll.JLINKARM_ReadMemU32(ctypes.c_uint32(address), 1, buf, status)
        if n < 1:
            raise RuntimeError(f"JLINKARM_ReadMemU32 failed at 0x{address:08X}")
        return buf[0]

    def run_code(self, exec_label=None):
        """Resume target execution via JLinkARM.dll (Ozone stays open)."""
        dll = self._load_dll()
        dll.JLINKARM_Go()
        if exec_label:
            exec_label.after(0, lambda: exec_label.config(text="Status: running", fg="green"))

    def pause_code(self, exec_label=None):
        """Halt target via JLinkARM.dll (Ozone stays open)."""
        dll = self._load_dll()
        dll.JLINKARM_Halt()
        if exec_label:
            exec_label.after(0, lambda: exec_label.config(text="Status: stopped at breakpoint", fg="#D35400"))

    def reset_target(self, status_label=None):
        """Reset target via JLinkARM.dll (Ozone stays open)."""
        dll = self._load_dll()
        dll.JLINKARM_Reset()
        dll.JLINKARM_Go()
        if status_label:
            status_label.after(0, lambda: status_label.config(text="Status: system ready", fg="blue"))
    def _get_symbol_address(self, varname: str) -> int:
        """Return the absolute address of a global variable from the ELF file."""
        if not self.elffile:
            raise RuntimeError("No ELF file loaded. Connect the debugger first.")

        # Try readelf (part of GNU Binutils / arm-none-eabi toolchain)
        for readelf_cmd in ("arm-none-eabi-readelf", "readelf"):
            found = shutil.which(readelf_cmd)
            if found:
                result = subprocess.run(
                    [found, "-s", "--wide", self.elffile],
                    capture_output=True, text=True, timeout=15
                )
                for line in result.stdout.splitlines():
                    parts = line.split()
                    # readelf symbol table line: Num Value Size Type Bind Vis Ndx Name
                    if len(parts) >= 8 and parts[-1] == varname:
                        return int(parts[1], 16)
                break

        raise RuntimeError(
            f"Symbol '{varname}' not found in ELF. "
            "Ensure arm-none-eabi-readelf is installed and on PATH."
        )

    def _write_u32(self, address: int, value: int):
        """Write a 32-bit value to target memory via JLink commander."""
        had_ozone = self._ozone_suspend()
        script = self._base_script() + [
            f"w4 0x{address:08X} 0x{value & 0xFFFFFFFF:08X}",
            "exit",
        ]
        self._run_script(script)
        if had_ozone:
            self._ozone_resume()

    def _read_u32(self, address: int) -> int:
        """Read a 32-bit value from target memory via JLink commander."""
        had_ozone = self._ozone_suspend()
        script = self._base_script() + [
            f"mem32 0x{address:08X}, 1",
            "exit",
        ]
        output = self._run_script(script)
        if had_ozone:
            self._ozone_resume()
        # JLink output line: "0x20001234 = 0x000003E8"  or  "20001234 = 000003E8"
        for line in output.splitlines():
            if "=" in line:
                parts = line.split("=")
                if len(parts) >= 2:
                    try:
                        return int(parts[-1].strip().split()[0], 16)
                    except ValueError:
                        pass
        raise RuntimeError(f"Could not parse mem32 output for address 0x{address:08X}")

    def send_cmd(self, command: str):
        """Handle debugger commands — routes Var.set to write_variable."""
        stripped = command.strip()
        lower = stripped.lower()

        if lower == "go":
            return self.run_code()
        if lower == "break":
            return self.pause_code()

        # Var.set <VarName> = <Value>
        if lower.startswith("var.set "):
            # Parse:  Var.set SomeVar = 42
            rest = stripped[len("var.set "):].strip()
            if "=" in rest:
                varname, _, val_str = rest.partition("=")
                varname = varname.strip()
                val_str = val_str.strip()
                try:
                    value = int(val_str, 0)
                except ValueError:
                    value = int(float(val_str))
                return self.write_variable(varname, value)

        raise NotImplementedError(
            f"J-Link backend does not support command: {command}"
        )

    def read_variable(self, varname: str) -> Any:
        """Read a firmware global variable by resolving its ELF symbol address."""
        address = self._get_symbol_address(varname)
        return self._read_u32(address)

    def write_variable(self, varname: str, value: Any):
        """Write a firmware global variable by resolving its ELF symbol address."""
        address = self._get_symbol_address(varname)
        self._write_u32(address, int(value))

    def clear_entries(self, entries):
        return None

    def get_dbg(self):
        return self

    def cmd(self, command: str):
        return self.send_cmd(command)

    def fnc(self, expression: str):
        if expression.startswith("Var.VALUE(") and expression.endswith(")"):
            raise NotImplementedError(
                "J-Link backend does not support Var.VALUE() queries yet."
            )
        raise NotImplementedError(
            f"J-Link dbg.fnc() does not support expression: {expression}"
        )
