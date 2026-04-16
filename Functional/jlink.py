import os
import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import Any


class JLinkBackend:
    def __init__(self):
        self.jlink_path = self._find_jlink_exe()
        self.connected = False
        self.elffile = None
        self.device = os.getenv("JLINK_DEVICE", "AUTO")
        self.interface = os.getenv("JLINK_IF", "SWD")
        self.speed = os.getenv("JLINK_SPEED", "4000")

    def _find_jlink_exe(self) -> str:
        candidate = shutil.which("JLink.exe") or shutil.which("JLinkARM.exe")
        if candidate:
            return candidate

        candidates = [
            r"C:\Program Files\SEGGER\JLink\JLink.exe",
            r"C:\Program Files (x86)\SEGGER\JLink\JLink.exe",
            r"C:\Program Files\SEGGER\JLinkARM.exe",
            r"C:\Program Files (x86)\SEGGER\JLinkARM.exe",
        ]
        for path in candidates:
            if os.path.exists(path):
                return path
        raise FileNotFoundError(
            "Segger J-Link executable not found. Install J-Link and add JLink.exe to PATH."
        )

    def _run_script(self, lines):
        fd, script_path = tempfile.mkstemp(suffix=".jlink")
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as handle:
                handle.write("\n".join(lines) + "\n")

            completed = subprocess.run(
                [self.jlink_path, "-CommanderScript", script_path],
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
        repo_path = repo_path_entry.get() if hasattr(repo_path_entry, "get") else str(repo_path_entry)
        self.elffile = self._resolve_elf(repo_path, selected_preset)
        script = self._base_script() + [f"loadfile {self.elffile}", "halt", "exit"]
        self._run_script(script)
        self.connected = True

    def disconnect(self, status_label=None):
        self.connected = False

    def run_code(self, exec_label=None):
        if not self.elffile:
            raise RuntimeError("J-Link is not connected or ELF file is not loaded.")
        script = self._base_script() + [f"loadfile {self.elffile}", "g", "exit"]
        self._run_script(script)

    def pause_code(self, exec_label=None):
        if not self.elffile:
            raise RuntimeError("J-Link is not connected or ELF file is not loaded.")
        script = self._base_script() + [f"loadfile {self.elffile}", "halt", "exit"]
        self._run_script(script)

    def reset_target(self, status_label=None):
        if not self.elffile:
            raise RuntimeError("J-Link is not connected or ELF file is not loaded.")
        script = self._base_script() + [f"loadfile {self.elffile}", "r", "exit"]
        self._run_script(script)

    def send_cmd(self, command: str):
        normalized = command.strip().lower()
        if normalized == "go":
            return self.run_code()
        if normalized == "break":
            return self.pause_code()
        if normalized.startswith("var.set"):
            raise NotImplementedError(
                "J-Link backend currently supports only execution control commands."
            )
        raise NotImplementedError(
            f"J-Link backend cannot execute debugger command: {command}"
        )

    def read_variable(self, varname: str) -> Any:
        raise NotImplementedError(
            "J-Link backend does not support Trace32 variable reads yet."
        )

    def write_variable(self, varname: str, value: Any):
        raise NotImplementedError(
            "J-Link backend does not support Trace32 variable writes yet."
        )

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
