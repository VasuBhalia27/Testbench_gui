import lauterbach.trace32.rcl as t32
import subprocess # module to create an additional process
from Functional.logging import *



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



def QuitTrace32():
    dbg.exit()

def Trace32ConnectApp():

    LaunchTrace32()
    ConnectToTraceUDP()
    time.sleep(2)

