import os
import tempfile
from pathlib import Path
from typing import Any, List

from Functional import jlink as jlink_module


def is_jlink_backend_available() -> bool:
    return hasattr(jlink_module, "JLinkBackend")


class JLinkBackend:
    def __init__(self):
        if not is_jlink_backend_available():
            raise ImportError("J-Link backend module not installed or unavailable.")
        self.backend = jlink_module.JLinkBackend()

    def connect(self, repo_path_entry, selected_preset, status_label=None):
        return self.backend.connect(repo_path_entry, selected_preset, status_label)

    def disconnect(self, status_label=None):
        return self.backend.disconnect(status_label=status_label)

    def run_code(self, exec_label=None):
        return self.backend.run_code(exec_label)

    def pause_code(self, exec_label=None):
        return self.backend.pause_code(exec_label)

    def reset_target(self, status_label=None):
        return self.backend.reset_target(status_label=status_label)

    def send_cmd(self, command: str):
        return self.backend.send_cmd(command)

    def read_variable(self, varname: str) -> Any:
        return self.backend.read_variable(varname)

    def write_variable(self, varname: str, value: Any):
        return self.backend.write_variable(varname, value)

    def clear_entries(self, entries: List[Any]):
        return self.backend.clear_entries(entries)

    def is_connected(self) -> bool:
        return self.backend.connected

    def get_dbg(self):
        return self.backend.get_dbg()

    def backend_name(self) -> str:
        return "jlink"

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
