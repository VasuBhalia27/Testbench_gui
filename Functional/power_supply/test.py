import re

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

        print("to do(GUI) -- multiple supplies detected")
    else:

        print("no supply found(GUI)")
        return None

    
    return list_supplies


raw_list = ('USB0::0x5345::0x1235::24150828::INSTR','USB0::0x5345::0x1235::24150828::INSTR', 'ASRL8::INSTR', 'ASRL10::INSTR', 'ASRL11::INSTR', 'ASRL13::INSTR', 'ASRL14::INSTR')

MultiPowerSupHandler(raw_list)