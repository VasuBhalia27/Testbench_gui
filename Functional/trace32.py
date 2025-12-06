import lauterbach.trace32.rcl as t32
import subprocess # module to create an additional process
import time
import tkinter as tk
from enum import IntEnum
from Functional.logging import *

logs = LogApp()

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


def LaunchTrace32():
    t32_exe = r"C:\Users\genericece\.conan2\p\tracee4f08930e322b\p\bin\windows64\t32marm.exe"
    config_file = r"D:\BMW_Repos\S05HBM690_Munich_testfirmware\build\xnf-handle-driver-c2-gcc-arm-relwithdebinfo\trace32\config.t32"
    start_up = r"D:\BMW_Repos\S05HBM690_Munich_testfirmware\Tests\DebuggerScripts\autoexec_automation.cmm"
    command = [t32_exe, '-c', config_file, '-s', start_up]
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
        
        logs.add_log(DID, val_master)

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
        
        logs.add_log(DID, fetched_var_value)

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

def Trace32ConnectApp():

    LaunchTrace32()
    ConnectToTraceUDP()
    time.sleep(2)

