import lauterbach.trace32.rcl as t32
import subprocess # module to create an additional process
import time
import tkinter as tk
from tkinter import messagebox
from enum import IntEnum
from Functional.logging import *
import os
import shutil
import tempfile
import re
import io

# logs = LogApp()

class TestFunctionCmd(IntEnum):
    TESTFW_GUI_CMD_VOLTAGE_CHECK_e       = 100  
    TESTFW_GUI_CMD_LED_TEST_e            = 101  
    TESTFW_GUI_CMD_BATT_MONITOR_e        = 102  
    TESTFW_GUI_CMD_MOTOR_TEST_e          = 103 
    TESTFW_GUI_CMD_EOS_TEST_e            = 104  
    TEST_GUI_CMD_SG_TEST_e               = 105  
    TEST_GUI_CMD_CAPA_TEST_e             = 106  
    TEST_GUI_CMD_NFC_TEST_e              = 107  
    TEST_GUI_CMD_CAN_TEST_e              = 108  
    TEST_GUI_CMD_LIN_e                   = 109  
    TEST_GUI_CMD_NFC_SPI_DIAG_e          = 110
    TESTFW_GUI_CMD_INVALID_e             = 111

# Mapping of variable names to their units
VARIABLE_UNITS_MAP = {
    # LED Test
    "TestFw_LedVoltage": "mV",
    
    # Battery Monitor
    "TestFw_AiBatRef": "mV",
    
    # Motor Test
    "TestFw_MotorVoltage": "mV",
    "TestFw_MotorCurrentValue": "mA",
    "TestFw_MotorLoadError": "",
    
    # EOS Test
    "TestFw_EosDiagVoltage": "mV",
    "TestFw_EosErrorsWithLow": "count",
    "TestFw_EosErrorsWithHigh": "count",
    
    # Strain Gauge Test
    "TestFw_DoPwrSg": "(on)",
    "TestFw_Sg1PlusOpamp": "mV",
    "TestFw_Sg1MinusOpamp": "mV",
    "TestFw_Sg1Opamp": "mV",
    "TestFw_Sg1Dac": "mV",
    "TestFw_Sg2PlusOpamp": "mV",
    "TestFw_Sg2MinusOpamp": "mV",
    "TestFw_Sg2Opamp": "mV",
    "TestFw_Sg2Dac": "mV",
    
    # Capa Test
    "TestFw_CapaApproach": "status",
    "TestFw_CapaLock": "status",
    "TestFw_CapaUnlock": "status",
    "TestFw_CapaApproachSensorValue": "counts",
    "TestFw_CapaLockSensorValue": "counts",
    "TestFw_CapaUnlockSensorValue": "counts",
    
    # NFC Test
    "TestFw_IsNfcDetectedCard": "bool",
    "TestFw_NfcRxDataLength": "bytes",
    
    # CAN Test
    "DummyBytes": "bytes",
    "TestFw_CanRxDataValid": "bool",
    "TestFw_CanRxMessageId": "hex",
    "TestFw_CanRxBytes.dummy_byte0_U8": "",
    "TestFw_CanRxBytes.dummy_byte1_U8": "",
    "TestFw_CanRxBytes.dummy_byte2_U8": "",
    "TestFw_CanRxBytes.dummy_byte3_U8": "",
    "TestFw_CanRxBytes.dummy_byte4_U8": "",
    "TestFw_CanRxBytes.dummy_byte5_U8": "",
    "TestFw_CanRxBytes.dummy_byte6_U8": "",
    "TestFw_CanRxBytes.dummy_byte7_U8": "",
    "TestFw_CanFaultLatch": "",

    # NFC Test
    "TestFw_IsNfcDetectedCard": "bool",
    "TestFw_NfcRxDataLength": "",
    "TestFw_NfcSpiError": "bool",
    "TestFw_NfcHwVersion": "hex",
    "TestFw_NfcRomVersion": "hex",
    "TestFw_NfcFwVersion": "hex",
    "TestFw_NfcNtsmState": "",

    # LIN Test
    "TestFw_LinTxPid": "hex",
    "TestFw_LinRxDataValid": "bool",
    "TestFw_LinRxPid": "hex",
    "TestFw_LinRxData_aU8[0]": "",
    "TestFw_LinRxData_aU8[1]": "",
    "TestFw_LinRxData_aU8[2]": "",
    "TestFw_LinRxData_aU8[3]": "",
    "TestFw_LinRxData_aU8[4]": "",
    "TestFw_LinRxData_aU8[5]": "",
    "TestFw_LinRxData_aU8[6]": "",
    "TestFw_LinRxData_aU8[7]": "",
}


dbg = ''
execution_status =''

# ---------------------------------------------------------------------------
# Trace32 executable discovery
# ---------------------------------------------------------------------------
_STANDARD_T32_EXE = Path(r"C:\T32\bin\windows64\t32marm.exe")

def find_trace32():
    """Return (exe_path_str, sys_dir_str) for the installed Trace32 package.

    Search order:
      1. Conan2 package cache  (~/.conan2/p/trace*/p/bin/windows64/t32marm.exe)
      2. Standard Lauterbach installation  (C:\\T32\\bin\\windows64\\t32marm.exe)
      3. System PATH  (shutil.which)

    The SYS directory is derived as three levels up from the executable
    (…/bin/windows64/t32marm.exe  →  SYS=…).
    Returns (None, None) if Trace32 cannot be located.
    """
    # 1 — Conan2 cache
    conan2_hits = sorted(
        (Path.home() / ".conan2" / "p").glob("trace*/p/bin/windows64/t32marm.exe")
    )
    if conan2_hits:
        exe = conan2_hits[-1]
        return str(exe), str(exe.parent.parent.parent)

    # 2 — Standard installation
    if _STANDARD_T32_EXE.is_file():
        exe = _STANDARD_T32_EXE
        return str(exe), str(exe.parent.parent.parent)

    # 3 — System PATH
    on_path = shutil.which("t32marm.exe")
    if on_path:
        exe = Path(on_path)
        return str(exe), str(exe.parent.parent.parent)

    return None, None
# ---------------------------------------------------------------------------

def format_value_with_unit(variable_name, value):
    """
    Format a value with its corresponding unit.
    
    Args:
        variable_name: Name of the variable (key in VARIABLE_UNITS_MAP)
        value: The numeric or string value to format
    
    Returns:
        Formatted string with value and unit, e.g., "12.5 mV"
    """
    if variable_name == "TestFw_CanRxDataValid":
        val = int(value)
        if val == 1:
            return "1 Yes"
        if val == 0:
            return "0 No"
        return str(val)

    unit = VARIABLE_UNITS_MAP.get(variable_name, "")

    if unit == "hex":
        return hex(int(value))
    elif unit:
        return f"{value} {unit}"
    else:
        return str(value)


def LaunchTrace32(repo_path_entry, selected_preset):
    # --- STEP 1: Aggressive Cleanup ---
    # Kill ALL known T32 executable names so that a stale instance from a
    # previous run (or a manually-opened debugger) cannot block the PODBUS
    # USB driver before we launch the new T32 process.
    _T32_PROCS = ['t32marm.exe', 't32mstart.exe', 't32mtc.exe']
    try:
        for _proc in _T32_PROCS:
            subprocess.run(
                ['taskkill', '/F', '/IM', _proc, '/T'],
                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                creationflags=subprocess.CREATE_NO_WINDOW
            )
        # Wait until every T32 process is fully gone (up to 15 seconds)
        # so the USB/PODBUS driver has time to physically release the device
        for _ in range(30):
            result = subprocess.run(
                ['tasklist'],
                capture_output=True, text=True,
                creationflags=subprocess.CREATE_NO_WINDOW
            )
            if not any(p in result.stdout for p in _T32_PROCS):
                break
            time.sleep(0.5)
    except:
        pass
    # --- STEP 2: Path Validation ---
    repo_path_XNF = repo_path_entry.get() 
    if not repo_path_XNF or not os.path.exists(repo_path_XNF):
        messagebox.showerror("Error", "BMW repository not found")
        return 
    # --- STEP 3: Config & Launch ---
    repo_path_XNF = repo_path_entry.get()
    if repo_path_XNF and os.path.exists(repo_path_XNF):
        autoexec_cmm_handler(repo_path_XNF, selected_preset, repo_path_entry)
    else:
        messagebox.showerror("Error", "BMW repository not found")
        return  # Stop execution if path is invalid

    # Locate the Trace32 ARM debugger executable (Conan2, standard install, or PATH).
    trace32_path, _ = find_trace32()
    if not trace32_path:
        messagebox.showerror(
            "Error",
            "Trace32 ARM debugger (t32marm.exe) not found.\n"
            "Checked:\n"
            "  \u2022 Conan2 cache  (~/.conan2/p/trace*/p/)\n"
            "  \u2022 Standard install  (C:\\T32\\bin\\windows64\\)\n"
            "  \u2022 System PATH\n\n"
            "Please install Lauterbach Trace32 and try again."
        )
        return
    
    Automation_repo_path = os.path.dirname(os.path.abspath(__file__)) #to get the path of user being currently used.
    Automation_repo_path = Automation_repo_path.replace('\\Functional', "")
    trace_configfile_path = f"{Automation_repo_path}\\Config\\config.t32"
    if not os.path.exists(trace_configfile_path):
        # Backward compatibility for older folder layout.
        trace_configfile_path = f"{Automation_repo_path}\\config.t32"
    

    repo_path_XNF = str(repo_path_XNF)
    repo_path_XNF_cleaned = repo_path_XNF.replace('/', "\\") 
    autoexec_script_path = f"{repo_path_XNF_cleaned}\\Tests\\DebuggerScripts\\autoexec_automation.cmm"

    edit_trace32_config_file(trace_configfile_path)
    
    command = [trace32_path, '-c', trace_configfile_path, '-s', autoexec_script_path]
    # Kill any stale T32 process before launching to avoid PODBUS "device already used" error
    for _proc in ['t32marm.exe', 't32mstart.exe', 't32mtc.exe']:
        subprocess.run(
            ['taskkill', '/F', '/IM', _proc, '/T'],
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
            creationflags=subprocess.CREATE_NO_WINDOW
        )
    time.sleep(5)  # Give the PODBUS driver time to release before new instance starts
                   # 5 s is required on some benches; 2 s caused "device already used" PODBUS error on retry
    subprocess.Popen(command)
    # Wait for the new GUI to fully initialize before Python tries to talk to it via UDP
    time.sleep(8) 

def autoexec_cmm_handler(repo_path_XNF, selected_preset, repo_path_entry):
    autoexec_cmm = "autoexec.cmm"
    flash_cmm = "flash.cmm"
    autoexec_changed_cmm = "autoexec_automation.cmm"
    flash_changed_cmm = "flash_automation.cmm"

    cmms_path = os.path.join(repo_path_XNF, "Tests", "DebuggerScripts")
    if not os.path.isdir(cmms_path):
        raise KeyError("Repo not found for debugger scripts!!!")

    autoexec_cmm_path = None
    flash_cmm_path = None
    autoexec_changed_cmm_path = None
    flash_changed_cmm_path = None

    # Walk and collect paths
    for root, dirs, files in os.walk(cmms_path):
        if autoexec_cmm in files:
            autoexec_cmm_path = os.path.join(root, autoexec_cmm)
        if flash_cmm in files:
            flash_cmm_path = os.path.join(root, flash_cmm)
        if autoexec_changed_cmm in files:
            autoexec_changed_cmm_path = os.path.join(root, autoexec_changed_cmm)
        if flash_changed_cmm in files:
            flash_changed_cmm_path = os.path.join(root, flash_changed_cmm)

        # You can break early if you found originals and changed ones, if that meets your logic
        # but careful: you may want to find all

    # After walking, check what you found
    if not autoexec_cmm_path:
        raise KeyError("CMM for autoexec not found")
    if not flash_cmm_path:
        raise KeyError("CMM for flash not found")

    # If changed ones are present already
    if autoexec_changed_cmm_path and flash_changed_cmm_path:
        os.remove(autoexec_changed_cmm_path)
        os.remove(flash_changed_cmm_path)

    # Otherwise create & edit copies
    new_flash_path = create_flash_cmm_copy(flash_cmm_path)
    edit_flash_cmm(new_flash_path, selected_preset, repo_path_entry)

    new_autoexec_path = create_autoexec_cmm_copy(autoexec_cmm_path)
    edit_autoexec_cmm(new_autoexec_path)
    # You would similarly have an edit_autoexec_cmm(new_auto) if needed  

def create_flash_cmm_copy(flash_cmm_path):
    flash_changed_cmm_automation = edit_cmm_path_name(flash_cmm_path)
    
    shutil.copy(flash_cmm_path, flash_changed_cmm_automation)
    return flash_changed_cmm_automation
    
def create_autoexec_cmm_copy(autoexec_changed_cmm):
    autoexec_changed_cmm_automation = edit_cmm_path_name(autoexec_changed_cmm)
    
    shutil.copy(autoexec_changed_cmm, autoexec_changed_cmm_automation)
    return autoexec_changed_cmm_automation

def edit_cmm_path_name(changed_cmm):
    dir_name, base_name = os.path.split(changed_cmm)
    name, ext = os.path.splitext(base_name)
    
    # Create the new file name with '_copied' suffix
    new_name = f"{name}_automation{ext}"
    changed_cmm_automation = os.path.join(dir_name, new_name)
    return changed_cmm_automation

def edit_flash_cmm(filepath, selected_preset, repo_path_entry) -> None:
    """
    Replace the line starting with Data.LOAD.Elf in the file at filepath
    with `new_line` (exactly). Other lines stay the _same.
    """
    new_line = get_select_preset(selected_preset, repo_path_entry)
    #messagebox.showinfo(
        #"Repository Path",
        #f"new_line:\n{new_line}"
    #)
    dirn = os.path.dirname(filepath) or "."
    fd, tmpname = tempfile.mkstemp(dir=dirn)
    try:
        with os.fdopen(fd, 'w', encoding='utf-8') as fout, open(filepath, 'r', encoding='utf-8', errors='ignore') as fin:
            for line in fin:
                if re.match(r'^\s*Data\.LOAD\.Elf\b', line):
                    fout.write("Data.LOAD.Elf " + new_line.rstrip('\r\n') + "\n")
                else:
                    fout.write(line)
        os.replace(tmpname, filepath)
    except Exception:
        os.remove(tmpname)
        raise


def edit_autoexec_cmm(filepath: str) -> None:
    """
    Replace any line that calls flash.cmm (with any number of spaces or tildes)
    with one that calls flash_automation.cmm.
    """
    

    new_line = r"DO ~~~~\flash_automation.cmm"

    # Match any line that has DO and ends with \flash.cmm, ignoring case, spaces, tildes, etc.
    pattern = re.compile(r'DO\s*[~\s]*\\flash\.cmm', re.IGNORECASE)

    dirn = os.path.dirname(filepath) or "."
    fd, tmpname = tempfile.mkstemp(dir=dirn)
    try:
        with io.open(filepath, 'r', encoding='utf-8-sig', errors='ignore') as fin, \
             io.open(fd, 'w', encoding='utf-8', newline='\n') as fout:
            replaced = False
            for line in fin:
                if pattern.search(line):  # use search instead of match
                    fout.write(new_line + "\n")
                    replaced = True
                else:
                    fout.write(line)
        os.replace(tmpname, filepath)
        
    except Exception:
        os.remove(tmpname)
        raise

def get_select_preset(selected_preset, repo_path_entry):
    repo_path_XNF = repo_path_entry.get()
    repo_path_XNF_cleaned = repo_path_XNF.replace('/', '\\')
    if selected_preset.get() == 1:#Non_Nfc_Test
        return rf"{repo_path_XNF_cleaned}\Non_Nfc_Test\XNF-Handle_NonDriver_C2_App.elf"
    
    if selected_preset.get() == 2:#Nfc_Test
        return rf"{repo_path_XNF_cleaned}\Nfc_Test\XNF-Handle_Driver_C2_App.elf"

    else:
        print("Select correct preset")
        raise ValueError("Select correct preset: Realwithdebinfo  or Minsizerel")

def edit_trace32_config_file(filename):

    target_prefix = "SYS="

    # Locate the Trace32 SYS directory (Conan2, standard install, or PATH).
    _, sys_dir = find_trace32()
    if not sys_dir:
        return False
    new_path = sys_dir

    replacement_line = "SYS=" + new_path + "\n"
    

    with open(filename, "r", encoding="utf-8", newline=None) as f:
        lines = f.readlines()

    found = False
    for i, line in enumerate(lines):

        stripped = line.strip()
        if stripped.startswith(target_prefix):

            lines[i] = replacement_line
            found = True

    if not found:
        return False

    with open(filename, "w", encoding="utf-8", newline='') as f:
        f.writelines(lines)

    return True



def ConnectToTraceUDP():
    global dbg
    # Close any existing connection before attempting a new one to avoid
    # stale socket state from a previous session.
    if dbg and hasattr(dbg, 'exit'):
        try:
            dbg.exit()
        except Exception:
            pass
    dbg = ''

    # Retry up to 3 times with a short delay between attempts.
    # TRACE32 may still be initialising its UDP port right after launch.
    last_exc = None
    for attempt in range(3):
        try:
            dbg = t32.connect(node='localhost', port=20007, protocol='UDP', packlen=1024, timeout=5.0)
            dbg.print("Hello")
            return
        except Exception as e:
            last_exc = e
            dbg = ''
            if attempt < 2:
                time.sleep(3)

    messagebox.showerror("Error", "Connection to Trace32 Failed!!!")


def SendDIDGetVal(entry_widget, DID, get_val_var):
    try:
        dbg.cmd(f'Var.set TestFw_GuiCmd = {DID}')
        time.sleep(0.5)
        val_master = dbg.fnc(f"Var.VALUE({get_val_var})")
        
        # Format value with unit
        formatted_value = format_value_with_unit(get_val_var, val_master)
        
        entry_widget.delete(0, tk.END)
        entry_widget.insert(0, formatted_value)
        
        # logs.add_log(DID, val_master)

    except Exception as e:
        print(e)
        error_msg = str(e)
        if "'str' object has no attribute 'cmd'" in error_msg:
            messagebox.showerror("Error", "Trace32 not connected!!!")


def SendDIDGetVal_multiple_entry(capa_output_variables, entry_list, DID, fetch_run_status = None, running_status_label = None):
    
    try:
        dbg.cmd(f'Var.set TestFw_GuiCmd = {DID}')
        time.sleep(0.5)

        for i in range(len(capa_output_variables)):
            fetched_var_value = dbg.fnc(f"Var.VALUE({capa_output_variables[i]})")
            fetched_var_value = int(fetched_var_value)
            
            # Format value with unit
            formatted_value = format_value_with_unit(capa_output_variables[i], fetched_var_value)
            
            entry_list[i].delete(0, tk.END)
            entry_list[i].insert(0, formatted_value)

    except Exception as e:
        print(e)
        error_msg = str(e)
        if "'str' object has no attribute 'cmd'" in error_msg:
            messagebox.showerror("Error","Trace32 not connected!!!")


def SendCmdToDbg(command):

    dbg.cmd(command)
    
def UpdateCodeExecLabel_running(exec_label):
    exec_label.config(text = "Code Execution status: Running")

def UpdateCodeExecLabel_notrunning(exec_label):
    exec_label.config(text = "Code Execution status: Not Running")
    

def RunCode(exec_label):
    try:
        dbg.cmd("Go")
        UpdateCodeExecLabel_running(exec_label)
        
    except Exception as err:
        msg, _, cmd_bytes = err.args
        if msg == "target running":
            UpdateCodeExecLabel_running(exec_label)
            
        else:
            UpdateCodeExecLabel_notrunning(exec_label)
        
def PauseCode(exec_label):

    dbg.cmd("Break")
    UpdateCodeExecLabel_notrunning(exec_label)

def QuitTrace32(status_label=None):
    global dbg
    try:
        if dbg and hasattr(dbg, 'exit'):
            dbg.exit()
    except Exception:
        pass
    finally:
        dbg = ''  # always reset so the next run detects no connection

def Trace32ConnectApp(repo_path_entry, selected_preset, status_label):
    LaunchTrace32(repo_path_entry, selected_preset)
    ConnectToTraceUDP()
    time.sleep(2)
    # Update status after successful connection and loading
    if status_label:
        status_label.config(text="Status: stopped at breakpoint", fg="#D35400") # Orange color

def ResetTarget(status_label):
    global dbg
    try:
        if dbg and hasattr(dbg, 'cmd'):
            # On PCB swap the SWD connection is lost. Release probe state with
            # SYStem.Down first, then retry SYStem.Up up to 3 times so a board
            # swap never immediately triggers the error popup.
            last_exc = None
            for attempt in range(3):
                try:
                    dbg.cmd("SYStem.Down")
                except Exception:
                    pass
                time.sleep(0.5)
                try:
                    dbg.cmd("SYStem.Up")
                    last_exc = None
                    break
                except Exception as e:
                    last_exc = e
                    if attempt < 2:
                        time.sleep(1.0)
            if last_exc is not None:
                raise last_exc
            if status_label:
                status_label.config(text="Status: system ready", fg="blue")
        else:
            if status_label is None:
                raise RuntimeError("Trace32 not connected")
            messagebox.showwarning("Warning", "Trace32 not connected!")
    except Exception as e:
        if status_label is None:
            raise
        messagebox.showerror("Error", f"Failed to reset target: {str(e)}")

def RunCode(exec_label):
    global dbg
    try:
        if dbg and hasattr(dbg, 'cmd'):
            dbg.cmd("Go")
            if exec_label:
                exec_label.config(text="Status: running", fg="green")
        else:
            if exec_label is None:
                raise RuntimeError("Trace32 not connected")
            messagebox.showwarning("Warning", "Trace32 not connected!")
    except Exception as err:
        if "target running" in str(err).lower():
            if exec_label:
                exec_label.config(text="Status: running", fg="green")
        else:
            if exec_label is None:
                # Called from automation — re-raise so caller can log and handle it
                # without showing a blocking popup dialog
                raise
            messagebox.showerror(
                "Error",
                f"Failed to start code: {str(err)}\n\n"
                "Troubleshooting:\n"
                "  \u2022 Check PCB power and hardware connections\n"
                "  \u2022 Check debugger cable and USB connection\n"
                "  \u2022 Verify ELF file matches the flashed firmware\n"
                "  \u2022 Try restarting Trace32 and reconnecting",
            )

def QuitTrace32(status_label=None):
    global dbg
    try:
        if dbg and hasattr(dbg, 'cmd'):
            dbg.cmd("SYStem.Down")  # Properly detach probe before quitting to avoid stuck hardware state on reconnect
            dbg.cmd("QUIT") 
            dbg.exit()
    except:
        pass
    finally:
        subprocess.run(
            ['taskkill', '/F', '/IM', 't32marm.exe', '/T'],
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
            creationflags=subprocess.CREATE_NO_WINDOW
        )
        time.sleep(4)  # Wait for PODBUS USB driver to fully release the device
        dbg = ''
        if status_label:
            status_label.config(text="Status: Disconnected", fg="red")

def motor_decouple_couple(selected_motor_state):
    if selected_motor_state.get() == 1:
        selected_motor_state.set(1)
    else:
        selected_motor_state.set(0)

    dbg.cmd(f'Var.set MotorTest_SetGuiMotorActuateRequest = 1')

def motor_no_req(selected_motor_state):
    if selected_motor_state.get() == 2:
        selected_motor_state.set(2)
    else:
        selected_motor_state.set(0)
    dbg.cmd(f'Var.set MotorTest_SetGuiMotorActuateRequest = 0')

def eos_set(eos_value):
    if eos_value.get() == 1:
        eos_value.set(1)
    else:
        eos_value.set(0)

    dbg.cmd(f'Var.set EosTest_EosRequestGui = 1')

def eos_reset(eos_value):
    if eos_value.get() == 2:
        eos_value.set(2)
    else:
        eos_value.set(0)
    dbg.cmd(f'Var.set EosTest_EosRequestGui = 0')

def sg_results(SgValue):
    if SgValue.get() == 1:
        SgValue.set(1)
    else:
        SgValue.set(0)

    dbg.cmd(f'Var.set TestFw_GetSgResults = 1')

def clear_entries(entries_list):
    for i in range(len(entries_list)):
        
        entries_list[i].delete(0, tk.END)

def reset_cb(dac1dac2value):
    
    dac1dac2value.set(0)

def led_on(led_input_condition):
    if led_input_condition.get() == 1:
        led_input_condition.set(1)
    else:
        led_input_condition.set(0)

    dbg.cmd(f'Var.set LedTest_LedCanLinRequest = 1')

def led_off(led_input_condition):
    if led_input_condition.get() == 2:
        led_input_condition.set(2)
    else:
        led_input_condition.set(0)

    dbg.cmd(f'Var.set LedTest_LedCanLinRequest = 0')

def CANoe_Disable(canoe_input_condition):
    if canoe_input_condition.get() == 1:
        canoe_input_condition.set(1)
    else:
        canoe_input_condition.set(0)

    dbg.cmd(f'Var.set TestFw_GuiCanDependencyDisable = 1')

def CANoe_Enable(canoe_input_condition):
    if canoe_input_condition.get() == 2:
        canoe_input_condition.set(2)
    else:
        canoe_input_condition.set(0)

    dbg.cmd(f'Var.set TestFw_GuiCanDependencyDisable = 0')

def poll_target_state(label, window):
    global poll_id, dbg
    
    # Stop polling if the connection object isn't valid
    if not dbg or isinstance(dbg, str):
        label.config(text="SmartBU Status: Disconnected")
        return
    
    try:
        # Check running status from TRACE32
        running_status = dbg.fnc("Var.VALUE(TestFw_IsEcuSleeping)")
        running_status = int(running_status)
        
        if running_status == 1:
            label.config(text="SmartBU Status: running (sleeping)")
        elif running_status == 0:
            label.config(text="SmartBU Status: running")
        else:
            label.config(text="SmartBU Status: Error")
            
        # Schedule the next poll only if successful
        poll_id = window.after(1000, lambda: poll_target_state(label, window))

    except Exception:
        # Stop polling loop on error to prevent ghosting/crashes
        dbg = '' 
        label.config(text="SmartBU Status: Disconnected")

# Add this function to trace32.py
def TransmitLinRawCount(entry_widget):
    global dbg
    try:
        # Get the value from the entry box
        raw_count_value = entry_widget.get()
        
        if dbg and hasattr(dbg, 'cmd'):
            # Set the specific variable requested
            dbg.cmd(f'Var.set TestFw_TxGuiCapaApproachRawCountLinFrame = {raw_count_value}')
            print(f"Transmitted {raw_count_value} to TestFw_TxGuiCapaApproachRawCountLinFrame")
        else:
            messagebox.showerror("Error", "Trace32 not connected!!!")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to transmit: {str(e)}")


def auto_reset_motor_checkbox(selected_motor_state):
    """Resets the checkbox to 0 and updates the debugger variable."""
    # 1. Uncheck the UI checkbox
    selected_motor_state.set(0)
    
    # 2. Update the Trace32 variable back to 0 (No Request)
    try:
        if dbg and hasattr(dbg, 'cmd'):
            dbg.cmd(f'Var.set MotorTest_SetGuiMotorActuateRequest = 0')
    except Exception as e:
        print(f"Failed to auto-reset Trace32 variable: {e}")


def auto_reset_sg_checkbox(SgValue):
    """Resets the checkbox to 0 and updates the debugger variable."""
    # 1. Uncheck the UI checkbox
    SgValue.set(0)
    
    # 2. Update the Trace32 variable back to 0 (No Request)
    try:
        if dbg and hasattr(dbg, 'cmd'):
            dbg.cmd(f'Var.set TestFw_GetSgResults = 0')
    except Exception as e:
        print(f"Failed to auto-reset Trace32 variable: {e}")

def read_sg_values_with_delay(variables, entries):
    """Read SG values with a small delay"""
    try:
        # Trigger measurement
        dbg.cmd(f'Var.set TestFw_GuiCmd = {TestFunctionCmd.TEST_GUI_CMD_SG_TEST_e}')
        time.sleep(0.2)
        
        for i in range(len(variables)):
            fetched_var_value = dbg.fnc(f"Var.VALUE({variables[i]})")
            formatted_value = format_value_with_unit(variables[i], fetched_var_value)
            
            entries[i].delete(0, tk.END)
            entries[i].insert(0, formatted_value)
            
    except Exception as e:
        print(f"Error reading SG values: {e}")

def read_capa_values_with_delay(variables, entries):
    """Read CAPA values with a small delay"""
    try:
        # Trigger measurement
        if dbg and hasattr(dbg, 'cmd'):
            dbg.cmd(f'Var.set TestFw_GuiCmd = {TestFunctionCmd.TEST_GUI_CMD_CAPA_TEST_e}')
            time.sleep(0.2)  # Small delay for measurement
            
            for i in range(len(variables)):
                fetched_var_value = dbg.fnc(f"Var.VALUE({variables[i]})")
                
                # Handle different variable types
                try:
                    # Try to convert to int for numeric values
                    int_val = int(fetched_var_value)
                    formatted_value = format_value_with_unit(variables[i], int_val)
                except:
                    # Keep as string for non-numeric values
                    formatted_value = format_value_with_unit(variables[i], fetched_var_value)
                
                entries[i].delete(0, tk.END)
                entries[i].insert(0, formatted_value)
    except Exception as e:
        print(f"Error reading CAPA values: {e}")
        error_msg = str(e)
        if "'str' object has no attribute 'cmd'" in error_msg:
            messagebox.showerror("Error", "Trace32 not connected!!!")