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
    TESTFW_GUI_CMD_INVALID_e             = 110  


dbg = ''
execution_status =''


def LaunchTrace32(repo_path_entry, selected_preset):
    repo_path_XNF = repo_path_entry.get() #to get the path of XNF directory.
    if repo_path_XNF:
        if os.path.exists(repo_path_XNF):
            autoexec_cmm_handler(repo_path_XNF, selected_preset, repo_path_entry)
        else:
            messagebox.showerror("Error", "BMW repository not found")
    else:
        messagebox.showerror("Error", "BMW repository not found")



    user_path = Path.home() #to get the path of user being currently used.
    user_path = str(user_path) #to get the path of user being currently used.
    user_path_cleaned = user_path.replace('/', "\\") 
    trace32_path = f"{user_path_cleaned}\\.conan2\\p\\tracee4f08930e322b\\p\\bin\\windows64\\t32marm.exe"    
    
    Automation_repo_path = os.path.dirname(os.path.abspath(__file__)) #to get the path of user being currently used.
    Automation_repo_path = Automation_repo_path.replace('\\Functional', "")
    trace_configfile_path = f"{Automation_repo_path}\\config.t32"    
    

    repo_path_XNF = str(repo_path_XNF)
    repo_path_XNF_cleaned = repo_path_XNF.replace('/', "\\") 
    autoexec_script_path = f"{repo_path_XNF_cleaned}\\Tests\\DebuggerScripts\\autoexec_automation.cmm"

    edit_trace32_config_file(trace_configfile_path)
    
    command = [trace32_path, '-c', trace_configfile_path, '-s', autoexec_script_path]
    subprocess.Popen(command)
    # Wait until the TRACE32 instance is started
    time.sleep(5) 

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
    if selected_preset.get() == 1:#Realwithdeb
        return rf"{repo_path_XNF_cleaned}\build\xnf-handle-driver-c2-gcc-arm-relwithdebinfo\XNF-Handle_Driver_C2_App.elf"
    
    if selected_preset.get() == 2:#Minsizerel
        return rf"{repo_path_XNF_cleaned}\build\xnf-handle-driver-c2-gcc-arm-minsizerel\XNF-Handle_Driver_C2_App.elf"

    else:
        print("Select correct preset")
        raise ValueError("Select correct preset: Realwithdebinfo  or Minsizerel")

def edit_trace32_config_file(filename):

    target_prefix = "SYS="
    
    user_path = Path.home() #to get the path of user being currently used.
    user_path = str(user_path) #to get the path of user being currently used.
    user_path_cleaned = user_path.replace('/', "\\") 
    new_path = f"{user_path_cleaned}\\.conan2\\p\\tracee4f08930e322b\\p"


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
    try:
        dbg = t32.connect(node='localhost', port=20006,protocol='UDP', packlen=1024, timeout=5.0)
        dbg.print("Hello")

    except Exception as e:
        messagebox.showerror("Error", "Connection to Trace32 Failed!!!")


def GetValueVbatt(entry_widget):
    global dbg 
    val_master = dbg.fnc("Var.VALUE(UC_UBatt__mV__U16)")
    val_master = float(f"{val_master/1000:.3f}")
    entry_widget.delete(0, tk.END)
    entry_widget.insert(0, str(val_master))

def SendDIDGetVal(entry_widget, DID, get_val_var):
    try:
        dbg.cmd(f'Var.set TestFw_GuiCmd = {DID}')
        time.sleep(0.5)
        val_master = dbg.fnc(f"Var.VALUE({get_val_var})")
        entry_widget.delete(0, tk.END)
        entry_widget.insert(0, str(val_master))
        
        # logs.add_log(DID, val_master)

    except Exception as e:
        print(e)
        error_msg = str(e)
        if "'str' object has no attribute 'cmd'" in error_msg:
            messagebox.showerror("Error", "Trace32 not connected!!!")




def SendDIDGetVal_multiple_entry(capa_output_variables, entry_list, DID):
    
    try:
        dbg.cmd(f'Var.set TestFw_GuiCmd = {DID}')
        time.sleep(0.5)

        for i in range(len(capa_output_variables)):
            fetched_var_value = dbg.fnc(f"Var.VALUE({capa_output_variables[i]})")
            entry_list[i].delete(0, tk.END)
            entry_list[i].insert(0, str(fetched_var_value))
        
        # logs.add_log(DID, fetched_var_value)

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



def QuitTrace32():
    dbg.exit()

def Trace32ConnectApp(repo_path_entry, selected_preset):

    LaunchTrace32(repo_path_entry, selected_preset)
    ConnectToTraceUDP()
    time.sleep(2)

def motor_couple(selected_motor_state):
    # If cb1 is turned ON, make sure cb2 is OFF by setting the shared var
    if selected_motor_state.get() == 1:
        selected_motor_state.set(1)
    else:
        selected_motor_state.set(0)

    dbg.cmd(f'Var.set Take_input_from_gui = 2')


def motor_decouple(selected_motor_state):
    # If cb2 is turned ON, set shared var to 2; if OFF, reset to 0
    if selected_motor_state.get() == 2:
        selected_motor_state.set(2)
    else:
        selected_motor_state.set(0)

    dbg.cmd(f'Var.set Take_input_from_gui = 1')


def SG_input_1(SG_input_1):
    # If cb1 is turned ON, make sure cb2 is OFF by setting the shared var
    if SG_input_1.get() == 1:
        SG_input_1.set(1)
    else:
        SG_input_1.set(0)

    dbg.cmd(f'Var.set TestFw_Sg1ToggleGui = 1')
    dbg.cmd(f'Var.set TestFw_Sg2ToggleGui = 0')

def SG_input_2(SG_input_2):
    # If cb2 is turned ON, set shared var to 2; if OFF, reset to 0
    if SG_input_2.get() == 2:
        SG_input_2.set(2)
    else:
        SG_input_2.set(0)

    dbg.cmd(f'Var.set TestFw_Sg1ToggleGui = 0')
    dbg.cmd(f'Var.set TestFw_Sg2ToggleGui = 1')

def SG_no_input(SG_input_3):
    # If cb2 is turned ON, set shared var to 3; if OFF, reset to 0
    if SG_input_3.get() == 3:
        SG_input_3.set(3)
    else:
        SG_input_3.set(0)

    dbg.cmd(f'Var.set TestFw_Sg1ToggleGui = 0')
    dbg.cmd(f'Var.set TestFw_Sg2ToggleGui = 0')

def clear_entries(entries_list):
    for i in range(len(entries_list)):
        
        entries_list[i].delete(0, tk.END)

