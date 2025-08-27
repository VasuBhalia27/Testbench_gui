from py_canoe import CANoe, wait
import time
import lauterbach.trace32.rcl as t32
import subprocess # module to create an additional process
from Functional.logging import *


dbg = ''
execution_status =''
global canoe

# ===================================================================================================================
# ========== Initializations ========================================================================================

canoe = ""
PASS = 1
FAIL = 0


# ===================================================================================================================
# ========== UDS messages for TP coding =============================================================================

coding_session = '10 41'

Caf_id_write = '2e 37 fc 05 FF FF FF FF FF FF FF'

Caf_data = "2E 30 93 03 01 00 00 00 00 DC 05 3C A0 0F 50 58 1B 64 00 00 00 DC 05 3C A0 0F 50 58 1B 64 00 00 00 DC 05 3C A0 0F 50 58 1B 64 00 00 00 DC 05 3C A0 0F 50 58 1B 64 B0 04 00 00 64 00 C8 00 F8 07 B8 0B 88 13 A4 06 00 00 96 00 79 01 4E 07 A0 0F 58 1B 30 75 00 00 A0 0F 10 27 30 75 50 C3 60 EA 00 1E 3C 3C 1E 00 B0 04 00 00 64 00 C8 00 F8 07 B8 0B 88 13 A4 06 00 00 96 00 79 01 4E 07 A0 0F 58 1B 30 75 00 00 A0 0F 10 27 30 75 50 C3 60 EA 00 1E 3C 3C 1E 00 B0 04 00 00 64 00 C8 00 F8 07 B8 0B 88 13 A4 06 00 00 96 00 79 01 4E 07 A0 0F 58 1B 30 75 00 00 A0 0F 10 27 30 75 50 C3 60 EA 00 1E 3C 3C 1E 00 B0 04 00 00 64 00 C8 00 F8 07 B8 0B 88 13 A4 06 00 00 96 00 79 01 4E 07 A0 0F 58 1B 30 75 00 00 A0 0F 10 27 30 75 50 C3 60 EA 00 1E 3C 3C 1E 00 00 21 24 1D 49 18 6D 15 92 13 B6 10 DB 0E FF 0C 00 2D 24 24 49 1C 6D 16 92 13 B6 10 DB 0B FF 08 00 17 24 15 49 15 6D 15 92 14 B6 12 DB 0F FF 0D 00 16 24 15 49 15 6D 15 92 14 B6 12 DB 0F FF 0D 20 03 E8 03 3C 3C FF FF FF FF FF FF FF FF 32 00 28 00 98 3A 06 F4 01 F4 01 19 01 00 1E 01 00 32 01 00 5A 01 00 6E 01 00 9B 01 00 BE 01 00 19 01 00 1E 01 00 32 01 00 5A 01 00 6E 01 00 9B 01 00 BE 01 00 FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF 10 27 1E CA 08 DC 05 64 88 13 10 27 32 CA 08 DC 05 8C 70 17 10 27 32 CA 08 DC 05 8C 58 1B 10 27 28 70 17 08 07 78 88 13 10 27 32 38 18 DC 05 78 88 13 10 27 32 00 19 AC 0D 78 40 1F 19 19 7D 3C 32 0A 19 32 14 1D 1E 23 04 5A 32 FF FF FF FF FF 78 50 50 04 64 28 18 0A FF FF FF FF FF FF FF FF FF 06 05 02 02 19 04 FF FF FF FF FF FF FF FF 41 2C 01 37 FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF C8 00 64 00 03 01 01 FF FF FF FF FF FF FF FF 90 01 C8 00 01 03 01 FF FF FF FF FF FF FF FF 0E 01 87 00 01 01 03 FF FF FF FF FF FF FF FF 3C 00 1E 00 03 01 01 FF FF FF FF FF FF FF FF C8 00 64 00 01 03 01 FF FF FF FF FF FF FF FF 50 00 28 00 01 01 03 FF FF FF FF FF FF FF FF 4C 30"

# ===================================================================================================================
# ========== function/classes definations ===========================================================================


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




def load_and_start_canoe_config(cfg_path):
    
    global canoe
    canoe = CANoe()
    
    # Open the CANoe configuration; customize flags as needed
    canoe.open(
        canoe_cfg=cfg_path,
        visible=True,
        auto_save=False,
        prompt_user=False
    )  # :contentReference[oaicite:0]{index=0}



    canoe.start_measurement()  # :contentReference[oaicite:1]{index=1}

    # Optionally, retrieve version info
    version_info = canoe.get_canoe_version_info()
    print("CANoe Version:", version_info)  # :contentReference[oaicite:2]{index=2}
    
    
    
    
def send_uds_msg(msg): #diag_ecu_qualifier_name: str, request: str, request_in_bytes=True, return_sender_name=False
    response = canoe.send_diag_request(diag_ecu_qualifier_name="BMW_XNF_Door_Handle_LIN",request=msg, request_in_bytes= True)
    print(f"response is --> {response}")

def read_mem_tpcoding():
    dbg.cmd("&major = data.byte(ESD:0x1B00)")
    dbg.cmd("&minor = data.byte(ESD:0x1B01)")
    dbg.cmd("&patch = data.byte(ESD:0x1B02)")
    
    

def TP_coding_process_test():
    
    read_mem_tpcoding()
    
    time.sleep(7)
    
    test_result = FAIL
    
    response1 = canoe.send_diag_request(diag_ecu_qualifier_name="BMW_XNF_Door_Handle_LIN",request=coding_session, request_in_bytes= True)
    if response1 == '50 41':
        resp_step1 = PASS
        
    else:
        resp_step1 = FAIL
    
    time.sleep(1)
    
    response2 = canoe.send_diag_request(diag_ecu_qualifier_name="BMW_XNF_Door_Handle_LIN",request=Caf_id_write, request_in_bytes= True)
    if response2 == '6E 37 FC':
        resp_step2 = PASS
        
    else:
        resp_step1 = FAIL
    
    time.sleep(1)
    
    response3 = canoe.send_diag_request(diag_ecu_qualifier_name="BMW_XNF_Door_Handle_LIN",request=Caf_data, request_in_bytes= True)
    if response3 == '6E 30 93':
        resp_step3 = PASS
        
    else:
        resp_step3 = FAIL
        
    if(resp_step1 and resp_step2 and resp_step3 == PASS):
        test_result = PASS
        
    else:
        test_result = FAIL
        
    print(f"Test result --> {test_result}")