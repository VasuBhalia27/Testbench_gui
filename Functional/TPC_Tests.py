from py_canoe import CANoe, wait
import time
import lauterbach.trace32.rcl as t32
import subprocess # module to create an additional process
from Functional.logging import *
import tkinter as tk
from Functional.CAF_handler import *
from enum import Enum

excel_file = r"D:\CAF Datas\XNF\XNF_TP_coding_file_v2.3_P3.2.0.xlsx"

modifications = {
    "PAR_LOCK_SENSOR_DEBOUNCE_TIME": "5B",
    "PAR_UNLOCK_SENSOR_DEBOUNCE_TIME": "05",
    "PAR_ADS_DOOR_CLOSED_DEBOUNCE_TIME_XNF": "19",
    "PAR_ADS_DOOR_OPEN_DEBOUNCE_TIME_XNF": "0B",
}

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
trial_caf_data = "2E 30 93 03 02 01 00 00 00 E8 03 3C DC 05 50 58 1B 64 00 00 00 DC 05 3C A0 0F 50 58 1B 64 00 00 00 E8 03 3C DC 05 50 58 1B 64 00 00 00 DC 05 3C A0 0F 50 58 1B 64 B0 04 00 00 64 00 C8 00 F8 07 B8 0B 88 13 A4 06 00 00 96 00 79 01 4E 07 A0 0F 58 1B 30 75 00 00 A0 0F 10 27 30 75 50 C3 60 EA 00 1E 3C 3C 1E 00 B0 04 00 00 64 00 C8 00 F8 07 B8 0B 88 13 A4 06 00 00 96 00 79 01 4E 07 A0 0F 58 1B 30 75 00 00 A0 0F 10 27 30 75 50 C3 60 EA 00 1E 3C 3C 1E 00 B0 04 00 00 64 00 C8 00 F8 07 B8 0B 88 13 A4 06 00 00 96 00 79 01 4E 07 A0 0F 58 1B 30 75 00 00 A0 0F 10 27 30 75 50 C3 60 EA 00 1E 3C 3C 1E 00 B0 04 00 00 64 00 C8 00 F8 07 B8 0B 88 13 A4 06 00 00 96 00 79 01 4E 07 A0 0F 58 1B 30 75 00 00 A0 0F 10 27 30 75 50 C3 60 EA 00 1E 3C 3C 1E 00 00 14 24 14 49 14 6D 14 92 14 B6 14 DB 14 FF 14 00 14 24 14 49 14 6D 14 92 14 B6 14 DB 14 FF 14 00 14 24 14 49 14 6D 14 92 14 B6 14 DB 14 FF 14 00 14 24 14 49 14 6D 14 92 14 B6 14 DB 14 FF 14 64 00 E8 03 3C 3C FF FF FF FF FF FF FF FF 32 00 28 00 D4 30 C8 F4 01 F4 01 19 01 00 1E 01 00 32 01 00 5A 01 00 6E 01 00 9B 01 00 BE 01 00 19 01 00 1E 01 00 32 01 00 5A 01 00 6E 01 00 9B 01 00 BE 01 00 5C 44 14 98 3A 3C FF FF FF FF FF FF FF FF FF FF FF FF FF FF 10 27 1E CA 08 DC 05 64 88 13 10 27 32 CA 08 DC 05 8C 70 17 10 27 32 CA 08 DC 05 8C 58 1B 10 27 28 70 17 08 07 78 88 13 10 27 32 38 18 DC 05 78 88 13 10 27 32 00 19 AC 0D 78 40 1F 19 19 7D 3C 32 0A 19 32 14 1D 1E 23 04 5A 32 FF FF FF FF FF 5A 50 50 04 64 28 18 0A FF FF FF FF FF FF FF FF FF 0A 05 02 02 4B 04 FF FF FF FF FF FF FF FF 41 2C 01 37 FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF C8 00 9C FF 03 01 01 FF FF FF FF FF FF FF FF 90 01 38 FF 01 03 01 FF FF FF FF FF FF FF FF 0E 01 79 FF 01 01 03 FF FF FF FF FF FF FF FF 3C 00 E2 FF 03 01 01 FF FF FF FF FF FF FF FF C8 00 9C FF 01 03 01 FF FF FF FF FF FF FF FF 50 00 D8 FF 01 01 03 FF FF FF FF FF FF FF FF 12 41"


class UdsCommands(Enum):
    CODING_SESSION = "10 41"
    CAF_ID_READ = "22 37 FC"
    CAF_ID_WRITE = "2E 37 FC"
    WRITE_TPCODING_DATA = "2E 30 93"
    READ_TPCODING_DATA = "22 30 93"

class TpCodingDataStreams(Enum):
    CAF_data_unchanged = "03 02 00 00 00 00 E8 03 3C DC 05 50 58 1B 64 00 00 00 DC 05 3C A0 0F 50 58 1B 64 00 00 00 E8 03 3C DC 05 50 58 1B 64 00 00 00 DC 05 3C A0 0F 50 58 1B 64 B0 04 00 00 64 00 C8 00 F8 07 B8 0B 88 13 A4 06 00 00 96 00 79 01 4E 07 A0 0F 58 1B 30 75 00 00 A0 0F 10 27 30 75 50 C3 60 EA 00 1E 3C 3C 1E 00 B0 04 00 00 64 00 C8 00 F8 07 B8 0B 88 13 A4 06 00 00 96 00 79 01 4E 07 A0 0F 58 1B 30 75 00 00 A0 0F 10 27 30 75 50 C3 60 EA 00 1E 3C 3C 1E 00 B0 04 00 00 64 00 C8 00 F8 07 B8 0B 88 13 A4 06 00 00 96 00 79 01 4E 07 A0 0F 58 1B 30 75 00 00 A0 0F 10 27 30 75 50 C3 60 EA 00 1E 3C 3C 1E 00 B0 04 00 00 64 00 C8 00 F8 07 B8 0B 88 13 A4 06 00 00 96 00 79 01 4E 07 A0 0F 58 1B 30 75 00 00 A0 0F 10 27 30 75 50 C3 60 EA 00 1E 3C 3C 1E 00 00 21 24 1D 49 18 6D 15 92 13 B6 10 DB 0E FF 0C 00 2D 24 24 49 1C 6D 16 92 13 B6 10 DB 0B FF 08 00 17 24 15 49 15 6D 15 92 14 B6 12 DB 0F FF 0D 00 16 24 15 49 15 6D 15 92 14 B6 12 DB 0F FF 0D 20 03 E8 03 3C 3C FF FF FF FF FF FF FF FF 32 00 28 00 D4 30 C8 F4 01 F4 01 19 01 00 1E 01 00 32 01 00 5A 01 00 6E 01 00 9B 01 00 BE 01 00 19 01 00 1E 01 00 32 01 00 5A 01 00 6E 01 00 9B 01 00 BE 01 00 5C 44 14 98 3A 3C FF FF FF FF FF FF FF FF FF FF FF FF FF FF 10 27 1E CA 08 DC 05 64 88 13 10 27 32 CA 08 DC 05 8C 70 17 10 27 32 CA 08 DC 05 8C 58 1B 10 27 28 70 17 08 07 78 88 13 10 27 32 38 18 DC 05 78 88 13 10 27 32 00 19 AC 0D 78 40 1F 19 19 7D 3C 32 0A 19 32 14 1D 1D 23 04 5A 32 FF FF FF FF FF 5A 50 50 04 64 28 18 0A FF FF FF FF FF FF FF FF FF 06 05 02 02 4B 04 FF FF FF FF FF FF FF FF 41 2C 01 37 FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF C8 00 9C FF 03 01 01 FF FF FF FF FF FF FF FF 90 01 38 FF 01 03 01 FF FF FF FF FF FF FF FF 0E 01 79 FF 01 01 03 FF FF FF FF FF FF FF FF 3C 00 E2 FF 03 01 01 FF FF FF FF FF FF FF FF C8 00 9C FF 01 03 01 FF FF FF FF FF FF FF FF 50 00 D8 FF 01 01 03 FF FF FF FF FF FF FF FF"
    CAF_ID_invalid = "05 FF FF FF FF FF FF FF"
    CAF_ID_valid = "05 11 22 33 44 55 66 77"



CAF_DATA_UNCHANGED_PAYLOAD = UdsCommands.WRITE_TPCODING_DATA.value + TpCodingDataStreams.CAF_data_unchanged.value



# ===================================================================================================================
# ========== function/classes definations ===========================================================================


def LaunchTrace32():
    t32_exe = r"C:\Users\genericece\.conan2\p\tracee4f08930e322b\p\bin\windows64\t32marm.exe"
    config_file = r"D:\BMW_Repos\S05HBM690_Munich_7.1.6\build\xnf-handle-nondriver-c2-gcc-arm-relwithdebinfo\trace32\config.t32"
    start_up = r"D:\BMW_Repos\S05HBM690_Munich_7.1.6\Tests\DebuggerScripts\autoexec_automation.cmm"
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
    dbg.cmm("QUIT")

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

def TP_read_mem_majminpat():
    dbg.cmd("&major = data.byte(ESD:0x1B00)")
    dbg.cmd("&minor = data.byte(ESD:0x1B01)")
    dbg.cmd("&patch = data.byte(ESD:0x1B02)")
    
    time.sleep(1)
    
    major = dbg.practice.get_macro("&major")
    major = major.value
    print(f"major -->{major}")
    minor = dbg.practice.get_macro("&minor")
    minor = minor.value
    print(f"minor -->{minor}")
    patch = dbg.practice.get_macro("&patch")
    patch = patch.value
    print(f"minor -->{patch}")
    
    return major, minor, patch

def TP_read_mem_CRC16():
    dbg.cmd("&crc1 = data.byte(ESD:0x1B03)")
    crc1 = dbg.practice.get_macro("&crc1").value
    dbg.cmd("&crc2 = data.byte(ESD:0x1B04)")
    crc2 = dbg.practice.get_macro("&crc2").value
    
    return crc1, crc2

    


def TP_coding_process_test(running_status_widget, result_widget):
    
    time.sleep(7)
    
    test_result = FAIL
    
    
    
    response1 = canoe.send_diag_request(diag_ecu_qualifier_name="BMW_XNF_Door_Handle_LIN",request=UdsCommands.CODING_SESSION, request_in_bytes= True)
    if response1 == '50 41':
        resp_step1 = PASS
        running_status_widget.delete(0, tk.END)
        running_status_widget.insert(0, str("10 41 - positive response"))
        
    else:
        resp_step1 = FAIL
        running_status_widget.delete(0, tk.END)
        running_status_widget.insert(0, str("Fail"))
    
    time.sleep(1)
    
    response2 = canoe.send_diag_request(diag_ecu_qualifier_name="BMW_XNF_Door_Handle_LIN",request=UdsCommands.CAF_ID_WRITE + TpCodingDataStreams.CAF_ID_invalid, request_in_bytes= True)
    if response2 == '6E 37 FC':
        resp_step2 = PASS
        running_status_widget.delete(0, tk.END)
        running_status_widget.insert(0, str("2E 37 FC - positive response"))
    else:
        resp_step1 = FAIL
        running_status_widget.delete(0, tk.END)
        running_status_widget.insert(0, str("Fail"))
    
    time.sleep(1)
    
    response3 = canoe.send_diag_request(diag_ecu_qualifier_name="BMW_XNF_Door_Handle_LIN",request=CAF_DATA_UNCHANGED_PAYLOAD, request_in_bytes= True)
    if response3 == '6E 30 93':
        resp_step3 = PASS
        running_status_widget.delete(0, tk.END)
        running_status_widget.insert(0, str("2E 30 93 - CAF written successfully"))
        
    else:
        resp_step3 = FAIL
        running_status_widget.delete(0, tk.END)
        running_status_widget.insert(0, str("Fail"))
        
    if(resp_step1 and resp_step2 and resp_step3 == PASS):

        major, minor, patch = TP_read_mem_majminpat()
        
        if((major == "0x3") and (minor == "0x1") and (patch == "0x0")):
            test_result = PASS
            running_status_widget.delete(0, tk.END)
            running_status_widget.insert(0, str("major, minor, path found in memory"))
            
            result_widget.delete(0, tk.END)
            result_widget.insert(0, str("Pass"))
            
        else:
            test_result = FAIL
            result_widget.delete(0, tk.END)
            result_widget.insert(0, str("Fail"))
            
            

        
    else:
        test_result = FAIL
        result_widget.delete(0, tk.END)
        result_widget.insert(0, str("Fail"))

        
    print(f"Test result --> {test_result}")
    
def target_soft_reset():
    dbg.cmd("SYStem.RESetTarget")
    dbg.cmd("Go")
    
def TP_coding_CRC16Check_test(running_status_widget, result_widget):  
    test_result = FAIL
    
    
    try:
        breakpoint = dbg.breakpoint.set(address="EST:0x6EE6")
        print(breakpoint)
        
    except Exception as e:
        print(e)
    response1 = canoe.send_diag_request(diag_ecu_qualifier_name="BMW_XNF_Door_Handle_LIN",request= UdsCommands.CODING_SESSION, request_in_bytes= True)
    if response1 == '50 41':
        resp_step1 = PASS
        running_status_widget.delete(0, tk.END)
        running_status_widget.insert(0, str("10 41 - positive response"))
        
    else:
        resp_step1 = FAIL
        running_status_widget.delete(0, tk.END)
        running_status_widget.insert(0, str("Fail"))
    
    time.sleep(1)
    
    response2 = canoe.send_diag_request(diag_ecu_qualifier_name="BMW_XNF_Door_Handle_LIN",request=UdsCommands.CAF_ID_WRITE + TpCodingDataStreams.CAF_ID_invalid, request_in_bytes= True)
    if response2 == '6E 37 FC':
        resp_step2 = PASS
        running_status_widget.delete(0, tk.END)
        running_status_widget.insert(0, str("2E 37 FC - positive response"))
    else:
        resp_step1 = FAIL
        running_status_widget.delete(0, tk.END)
        running_status_widget.insert(0, str("Fail"))
    
    time.sleep(1)
    
    response3 = canoe.send_diag_request(diag_ecu_qualifier_name="BMW_XNF_Door_Handle_LIN",request=CAF_DATA_UNCHANGED_PAYLOAD, request_in_bytes= True)
    if response3 == '6E 30 93':
        resp_step3 = PASS
        running_status_widget.delete(0, tk.END)
        running_status_widget.insert(0, str("2E 30 93 - CAF written successfully"))
        
    else:
        resp_step3 = FAIL
        running_status_widget.delete(0, tk.END)
        running_status_widget.insert(0, str("Fail"))
        
    if(resp_step1 and resp_step2 and resp_step3 == PASS):

        crc1, crc2 = TP_read_mem_CRC16()
        
        if((crc1 == "8E") and (crc2 == "4A")):
            test_result = PASS
            running_status_widget.delete(0, tk.END)
            running_status_widget.insert(0, str("CRC16 matched path found in memory"))
            
            result_widget.delete(0, tk.END)
            result_widget.insert(0, str("Pass"))
            
        else:
            test_result = FAIL 
            result_widget.delete(0, tk.END)
            result_widget.insert(0, str("Fail"))
            
            

        
    else:
        test_result = FAIL
        result_widget.delete(0, tk.END)
        result_widget.insert(0, str("Fail"))

        
    print(f"Test result --> {test_result}")
    
def TP_coding_changeableparameter_test():
    
    print("test running!!!")
    
    dbg.cmd("&PAR_LOCK_SENSOR_DEBOUNCE_TIME = VAR.Value(SF_NonVolatileData_s.lock_input_debounce_time__ms__dU16)") #TODO add correct command to get value of the variable in the code
    dbg.cmd("&PAR_UNLOCK_SENSOR_DEBOUNCE_TIME = VAR.Value(SF_NonVolatileData_s.unlock_debouncing__ms__U16)")
    dbg.cmd("&PAR_ADS_DOOR_CLOSED_DEBOUNCE_TIME_XNF = VAR.Value(SF_NonVolatileData_s.ads_door_closed_debounce_time__ms__U16)")
    dbg.cmd("&PAR_ADS_DOOR_OPEN_DEBOUNCE_TIME_XNF = VAR.Value(SF_NonVolatileData_s.ads_door_open_debounce_time__ms__U16)")
    
    time.sleep(1)
    
    par_lock_sensor_debounce_time_pscript = dbg.practice.get_macro("&PAR_LOCK_SENSOR_DEBOUNCE_TIME")
    par_lock_sensor_debounce_time_pscript = par_lock_sensor_debounce_time_pscript.value
    
    par_unlock_sensor_debounce_time_pscript = dbg.practice.get_macro("&PAR_UNLOCK_SENSOR_DEBOUNCE_TIME")
    par_unlock_sensor_debounce_time_pscript = par_unlock_sensor_debounce_time_pscript.value
    
    par_adsclosed_debounce_time_pscript = dbg.practice.get_macro("&PAR_ADS_DOOR_CLOSED_DEBOUNCE_TIME_XNF")
    par_adsclosed_debounce_time_pscript = par_adsclosed_debounce_time_pscript.value
    
    par_adsopen_debounce_time_pscript = dbg.practice.get_macro("&PAR_ADS_DOOR_OPEN_DEBOUNCE_TIME_XNF")
    par_adsopen_debounce_time_pscript = par_adsopen_debounce_time_pscript.value
    
    Modified_CAF = apply_modifications(TpCodingDataStreams.CAF_data_unchanged.value, excel_file, modifications)
    
    
    CAF_coding_final_payload = UdsCommands.WRITE_TPCODING_DATA.value + " " + Modified_CAF
    
    CAF_ID_INVALID_FINAL_PAYLOAD = UdsCommands.CAF_ID_WRITE.value + " " + TpCodingDataStreams.CAF_ID_invalid.value
    
    CAF_ID_VALID_FINAL_PAYLOAD = UdsCommands.CAF_ID_WRITE.value + " " + TpCodingDataStreams.CAF_ID_valid.value
    
    #SENDING CAF DATA PROCESS STARTS
    
    coding_session_response = canoe.send_diag_request(diag_ecu_qualifier_name="Door_Handle_LIN",request=UdsCommands.CODING_SESSION.value, request_in_bytes= True)
    
    time.sleep(1)
    
    CAF_data_write_response = canoe.send_diag_request(diag_ecu_qualifier_name="Door_Handle_LIN",request=CAF_coding_final_payload, request_in_bytes= True)
    
    time.sleep(1)
    
    CAF_data_write_response = canoe.send_diag_request(diag_ecu_qualifier_name="Door_Handle_LIN",request=CAF_ID_VALID_FINAL_PAYLOAD, request_in_bytes= True)
    

    

    