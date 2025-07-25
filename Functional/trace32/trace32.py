import lauterbach.trace32.rcl as t32
import subprocess # module to create an additional process
import time
import tkinter as tk
from enum import IntEnum, unique

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

def SendDIDGetVal_EOS(entry_widget):
    dbg.cmd('Var.set TF_Command = 105')
    time.sleep(0.5)
    val_master = dbg.fnc("Var.VALUE(TF_AiEosDiag)")
    entry_widget.delete(0, tk.END)
    entry_widget.insert(0, str(val_master))
    
def SendDIDGetVal_Motor(entry_widget):
    dbg.cmd('Var.set TF_Command = 103')
    time.sleep(0.5)
    val_master = dbg.fnc("Var.VALUE(TF_AiMotorDiag)")
    entry_widget.delete(0, tk.END)
    entry_widget.insert(0, str(val_master))
    
def SendDIDGetVal_LED(entry_widget):
    dbg.cmd('Var.set TF_Command = 101')
    time.sleep(0.5)
    val_master = dbg.fnc("Var.VALUE(TF_AiLedDiag)")
    entry_widget.delete(0, tk.END)
    entry_widget.insert(0, str(val_master))
    
def SendDIDGetVal_SG1Plus(entry_widget):
    dbg.cmd('Var.set TF_Command = 106')
    time.sleep(0.5)
    val_master = dbg.fnc("Var.VALUE(TF_Sg1PlusOpamp)")
    entry_widget.delete(0, tk.END)
    entry_widget.insert(0, str(val_master))

def SendDIDGetVal_SG1Minus(entry_widget):
    dbg.cmd('Var.set TF_Command = 107')
    time.sleep(0.5)
    val_master = dbg.fnc("Var.VALUE(TF_Sg1MinusOpamp)")
    entry_widget.delete(0, tk.END)
    entry_widget.insert(0, str(val_master))
    
def SendDIDGetVal_SG2Plus(entry_widget):
    dbg.cmd('Var.set TF_Command = 108')
    time.sleep(0.5)
    val_master = dbg.fnc("Var.VALUE(TF_Sg2PlusOpamp)")
    entry_widget.delete(0, tk.END)
    entry_widget.insert(0, str(val_master))

def SendDIDGetVal_SG2Minus(entry_widget):
    dbg.cmd('Var.set TF_Command = 109')
    time.sleep(0.5)
    val_master = dbg.fnc("Var.VALUE(TF_Sg2MinusOpamp)")
    entry_widget.delete(0, tk.END)
    entry_widget.insert(0, str(val_master))

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

