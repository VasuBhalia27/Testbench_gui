import lauterbach.trace32.rcl as t32
import subprocess # module to create an additional process
import time
import tkinter as tk
from enum import IntEnum
from Functional.logging import *

logs = LogApp()

class TestFunctionCmd(IntEnum):
    TF_VOLTAGE_CHECK_CMD       = 100
    TF_LED_TEST_CMD            = 101
    TF_BAT_MONT_CMD            = 102
    TF_MOTOR_VOLTAGE_TEST_CMD  = 103
    TF_MOTOR_CURRENTTEST_CMD   = 104
    TF_EOS_TEST_CMD            = 105
    TF_SG1PLUS_TEST_CMD        = 106
    TF_SG1MINUS_TEST_CMD       = 107
    TF_SG2PLUS_TEST_CMD        = 108
    TF_SG2MINUS_TEST_CMD       = 109
    TF_SG1_TEST_CMD            = 110
    TF_SG2_TEST_CMD            = 111
    TF_CAPA_TEST_CMD           = 112
    TF_NFC_TEST_CMD            = 113
    TF_CAN_TEST_CMD            = 114
    TF_LIN_TEST_CMD            = 115
    TF_INVALID_CMD             = 255

dbg = ''
execution_status =''


def LaunchTrace32():
    t32_exe = r"C:\Users\genericece\.conan2\p\tracee4f08930e322b\p\bin\windows64\t32marm.exe"
    config_file = r"D:\GITHUB\S05HBM690_Munich_develop\build\xnf-handle-driver-c1-gcc-arm-relwithdebinfo-productive\trace32\config.t32"
    start_up = r"D:\GITHUB\S05HBM690_Munich_develop\Tests\DebuggerScripts\autoexec.cmm"
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
        dbg.cmd(f'Var.set TF_Command = {DID}')
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

