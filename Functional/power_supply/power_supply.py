import pyvisa
import re
import tkinter as tk

# on connecting two supplies -- Found resources: ('USB0::0x5345::0x1235::23320657::INSTR', 'USB0::0x5345::0x1235::24150828::INSTR', 'ASRL4::INSTR', 'ASRL6::INSTR', 'ASRL7::INSTR', 'ASRL8::INSTR', 'ASRL10::INSTR', 'ASRL11::INSTR', 'ASRL13::INSTR', 'ASRL14::INSTR')
power_sup_inst1 = ''
rm = pyvisa.ResourceManager()

def DoNothing():
    """do nothing function"""
    return


def ConnectToPwrSup(usb_address):
    global power_sup_inst1
    power_sup_inst1 = rm.open_resource(usb_address)
    power_sup_inst1.timeout = 5000
    power_sup_inst1.write_termination = '\n'
    power_sup_inst1.read_termination = '\n'



def SetVoltage(entry_widget):
    requested_volt = entry_widget.get()
    power_sup_inst1.write(f"VOLT {requested_volt}")

def GetVoltage(entry_widget):
    fetched_val = 0
    fetched_val = power_sup_inst1.query("MEAS:VOLT?")
    entry_widget.delete(0, tk.END)
    entry_widget.insert(0,f"{fetched_val}")

def SetCurrent(requested_volt):
       power_sup_inst1.write(f"CURR {requested_volt}")

def PowerSupOn():
    power_sup_inst1.write("OUTP ON")

def PowerSupOff():
    power_sup_inst1.write("OUTP OFF")


def MultiPowerSupHandler(resource_list_raw: str):
    list_supplies = []
    no_of_supplies = 0
    match = False

    pattern =  pattern = r"^USB\d*::(0x[0-9A-Za-z]+)::(0x[0-9A-Za-z]+)::"
    
    if (len(resource_list_raw)) > 0:
        for i in range(len(resource_list_raw)):
            match = re.match(pattern, resource_list_raw[i])
            if match:
                no_of_supplies += 1
                list_supplies.append(resource_list_raw[i])

        return list_supplies

    else:

        print("no supply found(GUI)")

    if no_of_supplies > 1:
        print("Multiple supplies detected, Disconnect other supplies")


def Pwrcontrol_init():

    avalible_devices = rm.list_resources()

    usb_addrs = MultiPowerSupHandler(avalible_devices)
    
    if usb_addrs is not None:
        usb_addr = usb_addrs[0]
        return usb_addr
    
    else:
        return usb_addr


# def PowerSupState():
#     global state
#     if((state%2 == 0 ) or (state == 0)):
#         power_sup_inst1.write("OUTP ON")
#     if(state%2 != 0 ):
#         power_sup_inst1.write("OUTP OFF")
#     state += 1
