import lauterbach.trace32.rcl as t32
import subprocess # module to create an additional process
import time
import tkinter as tk

dbg = ''

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



def SendCmdToDbg(command):
    dbg.cmd(command)

def RunCode():
    dbg.cmd("Go")

def PauseCode():
    dbg.cmd("Break")

def QuitTrace32():
    dbg.exit()

def Trace32ConnectApp():

    LaunchTrace32()
    ConnectToTraceUDP()
    time.sleep(2)

