import glob
import os
import shutil
import subprocess
import tempfile
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

void AfterTargetReset(void) {{
    Exec.Reset();
}}

void AfterTargetDownload(void) {{
    Exec.Reset();
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

            completed = subprocess.run(
                [self.jlink_path, "-NoGui", "1", "-CommanderScript", script_path],
                capture_output=True,
                text=True,
                timeout=60,
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
        repo_path = repo_path_entry.get() if hasattr(repo_path_entry, "get") else str(repo_path_entry)
        self.elffile = self._resolve_elf(repo_path, selected_preset)

        # Close any previously opened Ozone instance
        if self._ozone_process and self._ozone_process.poll() is None:
            self._ozone_process.terminate()

        # Clean up previous temp project file
        if self._ozone_project_path and os.path.exists(self._ozone_project_path):
            try:
                os.remove(self._ozone_project_path)
            except OSError:
                pass

        self._ozone_project_path = self._generate_ozone_project(self.elffile)

        # Launch Ozone as a non-blocking process (same pattern as Trace32 launch)
        self._ozone_process = subprocess.Popen(
            [self.ozone_path, self._ozone_project_path],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        self.connected = True
        if status_label:
            status_label.after(0, lambda: status_label.config(text="Status: stopped at breakpoint", fg="#D35400"))

    def disconnect(self, status_label=None):
        """Close the Ozone process and clean up."""
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

    def run_code(self, exec_label=None):
        """Send Go command via JLink.exe in the background (Ozone stays open)."""
        script = self._base_script() + ["g", "exit"]
        self._run_script(script)
        if exec_label:
            exec_label.after(0, lambda: exec_label.config(text="Status: running", fg="green"))

    def pause_code(self, exec_label=None):
        """Send Halt command via JLink.exe in the background."""
        script = self._base_script() + ["halt", "exit"]
        self._run_script(script)
        if exec_label:
            exec_label.after(0, lambda: exec_label.config(text="Status: stopped at breakpoint", fg="#D35400"))

    def reset_target(self, status_label=None):
        """Send Reset command via JLink.exe in the background."""
        script = self._base_script() + ["r", "g", "exit"]
        self._run_script(script)
        if status_label:
            status_label.after(0, lambda: status_label.config(text="Status: system ready", fg="blue"))

    # ------------------------------------------------------------------
    # ELF symbol resolution — maps variable name → target address
    # ------------------------------------------------------------------
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
        script = self._base_script() + [
            f"w4 0x{address:08X} 0x{value & 0xFFFFFFFF:08X}",
            "exit",
        ]
        self._run_script(script)

    def _read_u32(self, address: int) -> int:
        """Read a 32-bit value from target memory via JLink commander."""
        script = self._base_script() + [
            f"mem32 0x{address:08X}, 1",
            "exit",
        ]
        output = self._run_script(script)
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
