from py_canoe import CANoe, wait
global canoe

canoe = ""


def load_and_start_canoe_config(cfg_path):
    global canoe
    # Initialize the CANoe instance
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
    response = canoe.send_diag_request(diag_ecu_qualifier_name="BMW_XNF_Door_Handle_LIN",request='10 41', request_in_bytes= True)
    print(f"response is --> {response}")
    