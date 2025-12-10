import lauterbach.trace32.rcl as t32
import subprocess # module to create an additional process
import time
import tkinter as tk
from enum import IntEnum
from Functional.logging import *
import os

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


def LaunchTrace32(repo_path_entry):
    user_path = Path.home() #to get the path of user being currently used.
    user_path = str(user_path) #to get the path of user being currently used.
    user_path_cleaned = user_path.replace('/', "\\") 
    trace32_path = f"{user_path_cleaned}\\.conan2\\p\\tracee4f08930e322b\\p\\bin\\windows64\\t32marm.exe"    
    
    Automation_repo_path = os.path.dirname(os.path.abspath(__file__)) #to get the path of user being currently used.
    Automation_repo_path = Automation_repo_path.replace('\\Functional', "")
    trace_configfile_path = f"{Automation_repo_path}\\config.t32"    
    
    repo_path_XNF = repo_path_entry.get() #to get the path of XNF directory.
    repo_path_XNF = str(repo_path_XNF)
    repo_path_XNF_cleaned = repo_path_XNF.replace('/', "\\") 
    autoexec_script_path = f"{repo_path_XNF_cleaned}\\Tests\\DebuggerScripts\\autoexec_automation.cmm"
    
    command = [trace32_path, '-c', trace_configfile_path, '-s', autoexec_script_path]
    subprocess.Popen(command)
    # Wait until the TRACE32 instance is started
    time.sleep(5) 



def ConnectToTraceUDP():
    global dbg
    try:
        dbg = t32.connect(node='localhost', port=20006,protocol='UDP', packlen=1024, timeout=5.0)
        dbg.print("Hello")

    except Exception as e:

        print("❌ Unable to connect:", e)

def GetValueVbatt(entry_widget):
    global dbg 
    val_master = dbg.fnc("Var.VALUE(UC_UBatt__mV__U16)")
    val_master = float(f"{val_master/1000:.3f}")
    entry_widget.delete(0, tk.END)
    entry_widget.insert(0, str(val_master))

def SendDIDGetVal(entry_widget, DID, get_val_var, footer_instance):
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
            footer_instance.update_additional_entry("Not connected to Trace32")


def SendDIDGetVal_multiple_entry(capa_output_variables, entry_list, DID, footer_instance):
    
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
            footer_instance.update_additional_entry("Not connected to Trace32")


    except Exception as e:
        print(e)
        error_msg = str(e)
        if "'str' object has no attribute 'cmd'" in error_msg:
            footer_instance.update_additional_entry("Not connected to Trace32")



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

def Trace32ConnectApp(repo_path_entry):

    LaunchTrace32(repo_path_entry)
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

