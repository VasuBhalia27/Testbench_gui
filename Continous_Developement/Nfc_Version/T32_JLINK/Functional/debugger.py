import os
import shutil
import subprocess
import tempfile
import time
from pathlib import Path
from typing import Any, List, Optional

from Functional import trace32 as trace32_backend
from Functional.trace32 import TestFunctionCmd          # re-exported for GUI imports
from Functional.jlink_backend import JLinkBackend, is_jlink_backend_available


class DebuggerBackendBase:
    def connect(self, repo_path_entry, selected_preset, status_label=None):
        raise NotImplementedError()

    def disconnect(self, status_label=None):
        raise NotImplementedError()

    def run_code(self, exec_label=None):
        raise NotImplementedError()

    def pause_code(self, exec_label=None):
        raise NotImplementedError()

    def reset_target(self, status_label=None):
        raise NotImplementedError()

    def send_cmd(self, command: str):
        raise NotImplementedError()

    def read_variable(self, varname: str) -> Any:
        raise NotImplementedError()

    def write_variable(self, varname: str, value: Any):
        raise NotImplementedError()

    def clear_entries(self, entries: List[Any]):
        raise NotImplementedError()

    def is_connected(self) -> bool:
        return False

    def get_dbg(self):
        raise NotImplementedError()

    def backend_name(self) -> str:
        raise NotImplementedError()


class Trace32Backend(DebuggerBackendBase):
    def __init__(self):
        self.backend = trace32_backend

    def connect(self, repo_path_entry, selected_preset, status_label=None):
        self.backend.Trace32ConnectApp(repo_path_entry, selected_preset, status_label)

    def disconnect(self, status_label=None):
        self.backend.QuitTrace32(status_label=status_label)

    def run_code(self, exec_label=None):
        self.backend.RunCode(exec_label)

    def pause_code(self, exec_label=None):
        self.backend.PauseCode(exec_label)

    def reset_target(self, status_label=None):
        self.backend.ResetTarget(status_label=status_label)

    def send_cmd(self, command: str):
        return self.backend.SendCmdToDbg(command)

    def read_variable(self, varname: str) -> Any:
        return self.backend.dbg.fnc(f"Var.VALUE({varname})")

    def write_variable(self, varname: str, value: Any):
        return self.backend.SendCmdToDbg(f"Var.set {varname} = {value}")

    def clear_entries(self, entries: List[Any]):
        return self.backend.clear_entries(entries)

    def is_connected(self) -> bool:
        return bool(getattr(self.backend, "dbg", None))

    def get_dbg(self):
        return self.backend.dbg

    def backend_name(self) -> str:
        return "trace32"


class DebuggerProxy:
    def __init__(self, manager: "DebuggerManager"):
        self._manager = manager

    def cmd(self, command: str):
        return self._manager.send_cmd(command)

    def fnc(self, expression: str):
        return self._manager.evaluate_function(expression)


class DebuggerManager:
    def __init__(self):
        self.trace32 = Trace32Backend()
        self.jlink = None
        self.jlink_module_available = is_jlink_backend_available()
        self.active: DebuggerBackendBase = self.trace32
        self.current_name = "trace32"
        self.dbg = DebuggerProxy(self)

    def set_backend(self, name: str) -> None:
        normalized = str(name or "").strip().lower()
        if normalized in ("trace32", "t32"):
            self.active = self.trace32
            self.current_name = "trace32"
        elif normalized in ("jlink", "j-link"):
            if not is_jlink_backend_available():
                raise FileNotFoundError(
                    "Segger J-Link executable not found. "
                    "Install J-Link from https://www.segger.com/downloads/jlink/ "
                    "and add JLink.exe to PATH."
                )
            if self.jlink is None:
                self.jlink = JLinkBackend()
            self.active = self.jlink
            self.current_name = "jlink"
        else:
            raise ValueError(f"Unknown debugger backend: {name}")

    def send_cmd(self, command: str) -> Any:
        return self.active.send_cmd(command)

    def evaluate_function(self, expression: str) -> Any:
        prefix = "Var.VALUE("
        if expression.startswith(prefix) and expression.endswith(")"):
            variable = expression[len(prefix):-1]
            return self.active.read_variable(variable)
        raise NotImplementedError(
            f"Expression evaluation is not supported by current backend: {expression}"
        )

    def connect(self, repo_path_entry, selected_preset, status_label=None):
        return self.active.connect(repo_path_entry, selected_preset, status_label)

    def disconnect(self, status_label=None):
        return self.active.disconnect(status_label=status_label)

    def run_code(self, exec_label=None):
        return self.active.run_code(exec_label)

    def pause_code(self, exec_label=None):
        return self.active.pause_code(exec_label)

    def reset_target(self, status_label=None):
        return self.active.reset_target(status_label=status_label)

    def read_variable(self, varname: str) -> Any:
        return self.active.read_variable(varname)

    def write_variable(self, varname: str, value: Any):
        return self.active.write_variable(varname, value)

    def clear_entries(self, entries: List[Any]):
        return self.active.clear_entries(entries)

    def is_connected(self) -> bool:
        try:
            return self.active.is_connected()
        except Exception:
            return False

    def backend_name(self) -> str:
        return self.current_name


_MANAGER = DebuggerManager()


def set_backend(name: str) -> None:
    _MANAGER.set_backend(name)


def get_backend_name() -> str:
    return _MANAGER.backend_name()


def is_connected() -> bool:
    """Return True if the active debugger backend has an open connection."""
    return _MANAGER.is_connected()


def Trace32ConnectApp(repo_path_entry, selected_preset, status_label):
    return _MANAGER.connect(repo_path_entry, selected_preset, status_label)


def RunCode(exec_label):
    return _MANAGER.run_code(exec_label)


def PauseCode(exec_label):
    return _MANAGER.pause_code(exec_label)


def QuitTrace32(status_label=None):
    return _MANAGER.disconnect(status_label=status_label)


def ResetTarget(status_label=None):
    return _MANAGER.reset_target(status_label=status_label)


def SendCmdToDbg(command: str):
    return _MANAGER.send_cmd(command)


def SendDIDGetVal(entry_widget, DID, get_val_var):
    try:
        _MANAGER.send_cmd(f"Var.set TestFw_GuiCmd = {DID}")
        time.sleep(0.5)
        val_master = int(_MANAGER.read_variable(get_val_var))
        formatted_value = format_value_with_unit(get_val_var, val_master)
        entry_widget.delete(0, "end")
        entry_widget.insert(0, formatted_value)
    except Exception as e:
        print(e)
        if "'str' object has no attribute 'cmd'" in str(e):
            from tkinter import messagebox
            messagebox.showerror("Error", "Debugger not connected!!!")


def SendDIDGetVal_multiple_entry(capa_output_variables, entry_list, DID, fetch_run_status=None, running_status_label=None):
    try:
        _MANAGER.send_cmd(f"Var.set TestFw_GuiCmd = {DID}")
        time.sleep(0.5)
        for i in range(len(capa_output_variables)):
            fetched_var_value = int(_MANAGER.read_variable(capa_output_variables[i]))
            formatted_value = format_value_with_unit(capa_output_variables[i], fetched_var_value)
            entry_list[i].delete(0, "end")
            entry_list[i].insert(0, formatted_value)
    except Exception as e:
        print(e)
        if "'str' object has no attribute 'cmd'" in str(e):
            from tkinter import messagebox
            messagebox.showerror("Error", "Debugger not connected!!!")


def clear_entries(entries_list):
    return _MANAGER.clear_entries(entries_list)


format_value_with_unit = trace32_backend.format_value_with_unit

dbg = _MANAGER.dbg

# ---------------------------------------------------------------------------
# These names are imported from trace32 only when Trace32 backend is active.
# The ones below are backend-agnostic wrappers that route through _MANAGER so
# they work with both Trace32 and J-Link.
# ---------------------------------------------------------------------------
from Functional.trace32 import (
    VARIABLE_UNITS_MAP,
    reset_cb,
    UpdateCodeExecLabel_running,
    UpdateCodeExecLabel_notrunning,
    ConnectToTraceUDP,
)


def _send(cmd: str):
    """Send a debugger command through the active backend."""
    _MANAGER.send_cmd(cmd)


def led_on(led_input_condition):
    if led_input_condition.get() == 1:
        led_input_condition.set(1)
    else:
        led_input_condition.set(0)
    _send("Var.set LedTest_LedCanLinRequest = 1")


def led_off(led_input_condition):
    if led_input_condition.get() == 2:
        led_input_condition.set(2)
    else:
        led_input_condition.set(0)
    _send("Var.set LedTest_LedCanLinRequest = 0")


def CANoe_Disable(canoe_input_condition):
    if canoe_input_condition.get() == 1:
        canoe_input_condition.set(1)
    else:
        canoe_input_condition.set(0)
    _send("Var.set TestFw_GuiCanDependencyDisable = 1")


def CANoe_Enable(canoe_input_condition):
    if canoe_input_condition.get() == 2:
        canoe_input_condition.set(2)
    else:
        canoe_input_condition.set(0)
    _send("Var.set TestFw_GuiCanDependencyDisable = 0")


def motor_decouple_couple(selected_motor_state):
    if selected_motor_state.get() == 1:
        selected_motor_state.set(1)
    else:
        selected_motor_state.set(0)
    _send("Var.set MotorTest_SetGuiMotorActuateRequest = 1")


def motor_no_req(selected_motor_state):
    if selected_motor_state.get() == 2:
        selected_motor_state.set(2)
    else:
        selected_motor_state.set(0)
    _send("Var.set MotorTest_SetGuiMotorActuateRequest = 0")


def eos_set(eos_value):
    if eos_value.get() == 1:
        eos_value.set(1)
    else:
        eos_value.set(0)
    _send("Var.set EosTest_EosRequestGui = 1")


def eos_reset(eos_value):
    if eos_value.get() == 2:
        eos_value.set(2)
    else:
        eos_value.set(0)
    _send("Var.set EosTest_EosRequestGui = 0")


def sg_results(SgValue):
    if SgValue.get() == 1:
        SgValue.set(1)
    else:
        SgValue.set(0)
    _send("Var.set TestFw_GetSgResults = 1")


def auto_reset_motor_checkbox(selected_motor_state):
    selected_motor_state.set(0)
    try:
        _send("Var.set MotorTest_SetGuiMotorActuateRequest = 0")
    except Exception as e:
        print(f"Failed to auto-reset motor variable: {e}")


def auto_reset_sg_checkbox(SgValue):
    SgValue.set(0)
    try:
        _send("Var.set TestFw_GetSgResults = 0")
    except Exception as e:
        print(f"Failed to auto-reset SG variable: {e}")


def TransmitLinRawCount(entry_widget):
    try:
        raw_count_value = entry_widget.get()
        _send(f"Var.set TestFw_TxGuiCapaApproachRawCountLinFrame = {raw_count_value}")
    except Exception as e:
        from tkinter import messagebox
        messagebox.showerror("Error", f"Failed to transmit: {e}")


def read_sg_values_with_delay(variables, entries):
    try:
        _send(f"Var.set TestFw_GuiCmd = {TestFunctionCmd.TEST_GUI_CMD_SG_TEST_e}")
        time.sleep(0.2)
        for i in range(len(variables)):
            fetched = int(_MANAGER.read_variable(variables[i]))
            entries[i].delete(0, "end")
            entries[i].insert(0, format_value_with_unit(variables[i], fetched))
    except Exception as e:
        print(f"Error reading SG values: {e}")


def read_capa_values_with_delay(variables, entries):
    try:
        _send(f"Var.set TestFw_GuiCmd = {TestFunctionCmd.TEST_GUI_CMD_CAPA_TEST_e}")
        time.sleep(0.2)
        for i in range(len(variables)):
            fetched = _MANAGER.read_variable(variables[i])
            try:
                fetched = int(fetched)
            except (TypeError, ValueError):
                pass
            entries[i].delete(0, "end")
            entries[i].insert(0, format_value_with_unit(variables[i], fetched))
    except Exception as e:
        print(f"Error reading CAPA values: {e}")

