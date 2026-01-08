import lauterbach.trace32.rcl as t32
import subprocess # module to create an additional process
import time
import tkinter as tk
from tkinter import messagebox
from enum import IntEnum
from Functional.logging import *
import os
import tempfile
import re
from tkinter import filedialog

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


def browse_elf_path():
    ELF_path = filedialog.askopenfilename(title="Select ELF")
    if ELF_path:
        return ELF_path

def LaunchTrace32():
    ELF_path = browse_elf_path()

    if ELF_path:
        if os.path.exists(ELF_path):
            autoexec_cmm_handler(ELF_path)
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
    

    ELF_path = str(ELF_path)
    autoexec_script_path = f"{Automation_repo_path}\\Cmms\\autoexec.cmm"

    edit_trace32_config_file(trace_configfile_path)
    
    command = [trace32_path, '-c', trace_configfile_path, '-s', autoexec_script_path]
    subprocess.Popen(command)
    # Wait until the TRACE32 instance is started
    time.sleep(5) 

def autoexec_cmm_handler(ELF_path):
    
    Automation_repo_path = os.path.dirname(os.path.abspath(__file__)) #to get the path of user being currently used.
    Automation_repo_path = Automation_repo_path.replace('\\Functional', "")
    flash_cmm_path = f"{Automation_repo_path}\\Cmms\\flash.cmm"   

    edit_flash_cmm(flash_cmm_path, ELF_path)




def edit_flash_cmm(filepath, ELF_path):
    """
    Replace the line starting with Data.LOAD.Elf in the file at filepath
    with `new_line` (exactly). Other lines stay the _same.
    """
    new_line = ELF_path
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



def ConnectToTraceUDP(trace_connection_status):
    global dbg
    try:
        dbg = t32.connect(node='localhost', port=20006,protocol='UDP', packlen=1024, timeout=5.0)
        dbg.print("Hello")
        trace_connection_status.config(bg="#797979", fg = "Green", text = "Connected")


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




def SendDIDGetVal_multiple_entry(capa_output_variables, entry_list, DID, fetch_run_status = None, running_status_label = None):
    
    try:
        dbg.cmd(f'Var.set TestFw_GuiCmd = {DID}')
        time.sleep(0.5)

        for i in range(len(capa_output_variables)):
            fetched_var_value = dbg.fnc(f"Var.VALUE({capa_output_variables[i]})")
            fetched_var_value = int(fetched_var_value)
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

def Trace32ConnectApp(trace_connection_status):

    LaunchTrace32()
    ConnectToTraceUDP(trace_connection_status)
    time.sleep(2)

def motor_couple(selected_motor_state):
    # If cb1 is turned ON, make sure cb2 is OFF by setting the shared var
    if selected_motor_state.get() == 1:
        selected_motor_state.set(1)
    else:
        selected_motor_state.set(0)

    dbg.cmd(f'Var.set MotorTest_SetGuiMotorActuateRequest = 2')


def motor_decouple(selected_motor_state):
    # If cb2 is turned ON, set shared var to 2; if OFF, reset to 0
    if selected_motor_state.get() == 2:
        selected_motor_state.set(2)
    else:
        selected_motor_state.set(0)

    dbg.cmd(f'Var.set MotorTest_SetGuiMotorActuateRequest = 1')


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

def reset_cb(SG_input_1, SG_input_2, SG_input_3):
    
    SG_input_1.set(0)
    SG_input_2.set(0)
    SG_input_3.set(0)


def poll_target_state(label, window):

    try:

        running_status = dbg.fnc("Var.VALUE(TestFw_IsEcuSleeping)")
        running_status = int(running_status)
        
        if running_status == 1:
            label.config(text= "Running Status: Sleep")

        elif running_status == 0:
            label.config(text= "Running Status: Running")

        else:
            label.config(text= "Running Status: Error")
        window.after(1000, lambda: poll_target_state(label, window))

        
    except Exception as e:
        window.after(1000, lambda: poll_target_state(label, window))

def in_target_reset():

    dbg.cmd("SYStem.RESetTarget")
    
    dbg.cmd("Go")

